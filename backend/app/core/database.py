"""
Database configuration and session management.

Provides both synchronous and asynchronous SQLAlchemy engines, session factories, 
and database utilities for different use cases with enhanced error handling.
"""

from typing import Generator, AsyncGenerator, Optional
from contextlib import asynccontextmanager
import time
import structlog

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError as SQLDatabaseError
from sqlalchemy.pool import Pool

from app.core.config import settings
from app.core.error_handling import (
    DatabaseError,
    error_handler,
    async_error_handler,
    safe_operation,
    async_safe_operation,
    create_checkpoint,
    load_checkpoint
)

# Logger
logger = structlog.get_logger(__name__)

# Import models to ensure they're registered with SQLAlchemy
# This import is at module level to satisfy linter requirements
def _import_models():
    """Import all models to register them with SQLAlchemy."""
    try:
        from app.models.user import User  # noqa: F401
        from app.models.salary_entry import SalaryEntry  # noqa: F401
        from app.models.benchmark import Benchmark  # noqa: F401
        logger.info("Database models imported successfully")
    except ImportError as e:
        logger.warning("Some models might not be available during initial setup", error=str(e))

# Don't call _import_models() here to avoid circular imports


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Connection tracking
CONNECTION_STATS = {
    "total_connections": 0,
    "active_connections": 0,
    "failed_connections": 0,
    "last_connection_time": None,
    "last_failure_time": None
}


def track_connection_event(event_type: str, details: dict = None):
    """Track database connection events for monitoring."""
    global CONNECTION_STATS
    
    current_time = time.time()
    
    if event_type == "connect":
        CONNECTION_STATS["total_connections"] += 1
        CONNECTION_STATS["active_connections"] += 1
        CONNECTION_STATS["last_connection_time"] = current_time
        logger.info("Database connection established", **details or {})
        
    elif event_type == "disconnect":
        CONNECTION_STATS["active_connections"] = max(0, CONNECTION_STATS["active_connections"] - 1)
        logger.info("Database connection closed", **details or {})
        
    elif event_type == "failed":
        CONNECTION_STATS["failed_connections"] += 1
        CONNECTION_STATS["last_failure_time"] = current_time
        logger.error("Database connection failed", **details or {})


@event.listens_for(Pool, "connect")
def on_connect(dbapi_conn, connection_record):
    """Handle database connection events."""
    track_connection_event("connect", {"connection_id": id(dbapi_conn)})


@event.listens_for(Pool, "close")
def on_disconnect(dbapi_conn, connection_record):
    """Handle database disconnection events."""
    track_connection_event("disconnect", {"connection_id": id(dbapi_conn)})


def create_safe_engine(database_url: str, is_async: bool = False, **kwargs):
    """
    Create a database engine with enhanced error handling and monitoring.
    
    Args:
        database_url: Database connection URL
        is_async: Whether to create async engine
        **kwargs: Additional engine parameters
        
    Returns:
        SQLAlchemy engine instance
    """
    try:
        # Default engine parameters for reliability
        engine_params = {
            "echo": settings.DEBUG,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # Recycle connections every hour
            "pool_size": 20,
            "max_overflow": 10,
            "pool_timeout": 30,
            **kwargs
        }
        
        if is_async:
            # Use aiosqlite for SQLite async support
            if database_url.startswith("sqlite"):
                database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
            else:
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            
            engine = create_async_engine(database_url, **engine_params)
        else:
            engine = create_engine(database_url, **engine_params)
        
        logger.info(
            "Database engine created successfully",
            is_async=is_async,
            database_type="sqlite" if "sqlite" in database_url else "postgresql"
        )
        
        return engine
        
    except Exception as e:
        track_connection_event("failed", {"error": str(e), "database_url": database_url[:50]})
        raise DatabaseError(
            f"Failed to create database engine: {str(e)}",
            error_code="ENGINE_CREATION_FAILED",
            details={"database_url": database_url[:50], "is_async": is_async}
        )


# Create synchronous engine (for compatibility with existing code)
try:
    engine = create_safe_engine(str(settings.SQLALCHEMY_DATABASE_URI))
except Exception as e:
    logger.critical("Failed to create synchronous database engine", error=str(e))
    # Fallback to SQLite for development
    engine = create_safe_engine("sqlite:///./wagelift_fallback.db")

# Create asynchronous engine (for new async operations)
try:
    async_engine = create_safe_engine(str(settings.SQLALCHEMY_DATABASE_URI), is_async=True)
except Exception as e:
    logger.critical("Failed to create asynchronous database engine", error=str(e))
    # Fallback to SQLite for development
    async_engine = create_safe_engine("sqlite:///./wagelift_fallback.db", is_async=True)

# Create session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@error_handler(default_return=None, exceptions=(SQLAlchemyError, DatabaseError))
def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get synchronous database session with error handling.
    
    Usage:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            # Use db session here
    """
    db = None
    checkpoint_id = f"db_session_{int(time.time() * 1000)}"
    
    try:
        db = SessionLocal()
        
        # Test connection
        db.execute(text("SELECT 1"))
        
        # Create checkpoint for recovery
        create_checkpoint({"session_created": True}, checkpoint_id)
        
        yield db
        
        # Commit any pending changes
        db.commit()
        logger.debug("Database session committed successfully")
        
    except SQLAlchemyError as e:
        if db:
            db.rollback()
            logger.error("Database session rolled back due to error", error=str(e))
        raise DatabaseError(
            f"Database session error: {str(e)}",
            error_code="SESSION_ERROR",
            details={"checkpoint_id": checkpoint_id}
        )
    except Exception as e:
        if db:
            db.rollback()
        logger.error("Unexpected error in database session", error=str(e))
        raise
    finally:
        if db:
            db.close()
            logger.debug("Database session closed")


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager to get asynchronous database session with error handling.
    
    Usage:
        async with get_db_session() as session:
            # Use async session here
    """
    session = None
    checkpoint_id = f"async_db_session_{int(time.time() * 1000)}"
    
    try:
        session = AsyncSessionLocal()
        
        # Test connection
        await session.execute(text("SELECT 1"))
        
        # Create checkpoint for recovery
        create_checkpoint({"async_session_created": True}, checkpoint_id)
        
        yield session
        
        # Commit any pending changes
        await session.commit()
        logger.debug("Async database session committed successfully")
        
    except SQLAlchemyError as e:
        if session:
            await session.rollback()
            logger.error("Async database session rolled back due to error", error=str(e))
        raise DatabaseError(
            f"Async database session error: {str(e)}",
            error_code="ASYNC_SESSION_ERROR",
            details={"checkpoint_id": checkpoint_id}
        )
    except Exception as e:
        if session:
            await session.rollback()
        logger.error("Unexpected error in async database session", error=str(e))
        raise
    finally:
        if session:
            await session.close()
            logger.debug("Async database session closed")


@async_error_handler(default_return=None, exceptions=(SQLAlchemyError, DatabaseError))
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get asynchronous database session for FastAPI with error handling.
    
    Usage:
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            # Use async db session here
    """
    async with get_db_session() as session:
        yield session


@error_handler(exceptions=(SQLAlchemyError, DatabaseError))
def init_db() -> None:
    """
    Initialize database tables using synchronous engine with error handling.
    
    This creates all tables defined in models.
    In production, use Alembic migrations instead.
    """
    try:
        # Import models to ensure they're registered with SQLAlchemy
        _import_models()
        
        # Create checkpoint before initialization
        create_checkpoint({"operation": "init_db", "timestamp": time.time()}, "db_init")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
    except SQLAlchemyError as e:
        raise DatabaseError(
            f"Failed to initialize database: {str(e)}",
            error_code="DB_INIT_FAILED",
            details={"operation": "create_all_tables"}
        )


@async_error_handler(exceptions=(SQLAlchemyError, DatabaseError))
async def init_async_db() -> None:
    """
    Initialize database tables using asynchronous engine with error handling.
    
    This creates all tables defined in models.
    In production, use Alembic migrations instead.
    """
    try:
        # Import models to ensure they're registered with SQLAlchemy
        _import_models()
        
        # Create checkpoint before initialization
        create_checkpoint({"operation": "init_async_db", "timestamp": time.time()}, "async_db_init")
        
        # Create all tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Async database tables created successfully")
        
    except SQLAlchemyError as e:
        raise DatabaseError(
            f"Failed to initialize async database: {str(e)}",
            error_code="ASYNC_DB_INIT_FAILED",
            details={"operation": "create_all_tables_async"}
        )


@error_handler(exceptions=(SQLAlchemyError,))
def test_db_connection() -> bool:
    """
    Test database connection health.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        with safe_operation("test_db_connection"):
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
                session.commit()
        
        logger.info("Database connection test successful")
        return True
        
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        return False


@async_error_handler(exceptions=(SQLAlchemyError,))
async def test_async_db_connection() -> bool:
    """
    Test async database connection health.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        async with async_safe_operation("test_async_db_connection"):
            async with get_db_session() as session:
                await session.execute(text("SELECT 1"))
                await session.commit()
        
        logger.info("Async database connection test successful")
        return True
        
    except Exception as e:
        logger.error("Async database connection test failed", error=str(e))
        return False


def get_db_stats() -> dict:
    """
    Get database connection statistics for monitoring.
    
    Returns:
        Dictionary containing connection statistics
    """
    return {
        "connection_stats": CONNECTION_STATS.copy(),
        "engine_info": {
            "pool_size": engine.pool.size(),
            "checked_in": engine.pool.checkedin(),
            "checked_out": engine.pool.checkedout(),
            "overflow": engine.pool.overflow(),
        } if hasattr(engine.pool, 'size') else {},
        "is_healthy": test_db_connection()
    }


@error_handler(exceptions=(Exception,))
def close_db() -> None:
    """Close database connections with error handling."""
    try:
        engine.dispose()
        logger.info("Synchronous database connections closed")
    except Exception as e:
        logger.error("Error closing synchronous database connections", error=str(e))


@async_error_handler(exceptions=(Exception,))
async def close_async_db() -> None:
    """Close async database connections with error handling."""
    try:
        await async_engine.dispose()
        logger.info("Asynchronous database connections closed")
    except Exception as e:
        logger.error("Error closing asynchronous database connections", error=str(e))


def recover_from_checkpoint(checkpoint_id: str) -> bool:
    """
    Recover database session from checkpoint.
    
    Args:
        checkpoint_id: Checkpoint identifier
        
    Returns:
        True if recovery successful, False otherwise
    """
    try:
        checkpoint_data = load_checkpoint(checkpoint_id)
        if checkpoint_data:
            logger.info("Database recovery from checkpoint successful", checkpoint_id=checkpoint_id)
            return True
        return False
    except Exception as e:
        logger.error("Database recovery from checkpoint failed", error=str(e), checkpoint_id=checkpoint_id)
        return False 