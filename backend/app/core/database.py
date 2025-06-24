"""
Database configuration and session management.

Provides both synchronous and asynchronous SQLAlchemy engines, session factories, 
and database utilities for different use cases.
"""

from typing import Generator, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings

# Import models to ensure they're registered with SQLAlchemy
# This import is at module level to satisfy linter requirements
def _import_models():
    """Import all models to register them with SQLAlchemy."""
    try:
        from app.models import User, SalaryEntry, Benchmark, RaiseRequest, CPIData  # noqa: F401
    except ImportError:
        # Models might not be available during initial setup
        pass

_import_models()


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


# Create synchronous engine (for compatibility with existing code)
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Create asynchronous engine (for new async operations)
# Use aiosqlite for SQLite async support
database_url = str(settings.SQLALCHEMY_DATABASE_URI)
if database_url.startswith("sqlite"):
    async_database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

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


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get synchronous database session.
    
    Usage:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager to get asynchronous database session.
    
    Usage:
        async with get_db_session() as session:
            # Use async session here
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get asynchronous database session for FastAPI.
    
    Usage:
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            # Use async db session here
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def init_db() -> None:
    """
    Initialize database tables using synchronous engine.
    
    This creates all tables defined in models.
    In production, use Alembic migrations instead.
    """
    # Import models to ensure they're registered with SQLAlchemy
    from app.models import User, SalaryEntry, Benchmark, RaiseRequest, CPIData  # noqa: F401
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


async def init_async_db() -> None:
    """
    Initialize database tables using asynchronous engine.
    
    This creates all tables defined in models.
    In production, use Alembic migrations instead.
    """
    # Import models to ensure they're registered with SQLAlchemy
    from app.models import User, SalaryEntry, Benchmark, RaiseRequest, CPIData  # noqa: F401
    
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def close_db() -> None:
    """Close database connections."""
    engine.dispose()


async def close_async_db() -> None:
    """Close async database connections."""
    await async_engine.dispose() 