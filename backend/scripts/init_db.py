#!/usr/bin/env python3
"""
Database initialization script for WageLift Backend.

This script handles:
- Creating initial Alembic migration
- Setting up database tables
- Loading initial data (if needed)
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_initial_migration():
    """Create the initial Alembic migration."""
    try:
        logger.info("Creating initial Alembic migration...")
        
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Initialize Alembic (if not already done)
        try:
            result = subprocess.run(
                ["alembic", "init", "alembic"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("Alembic initialized")
            else:
                logger.info("Alembic already initialized")
        except FileNotFoundError:
            logger.error("Alembic not found. Install with: pip install alembic")
            return False
        
        # Create initial migration
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            logger.info("Initial migration created successfully")
            logger.info(f"Migration output: {result.stdout}")
            return True
        else:
            logger.error(f"Failed to create migration: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating migration: {e}")
        return False


async def run_migrations():
    """Run Alembic migrations to latest."""
    try:
        logger.info("Running database migrations...")
        
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            logger.info("Migrations completed successfully")
            logger.info(f"Migration output: {result.stdout}")
            return True
        else:
            logger.error(f"Failed to run migrations: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False


async def create_initial_data():
    """Create initial data if needed."""
    try:
        logger.info("Creating initial data...")
        
        # Import models to access database
        from app.models import CPIData
        from app.core.database import AsyncSessionLocal
        from datetime import date
        from decimal import Decimal
        
        async with AsyncSessionLocal() as session:
            # Check if we already have CPI data
            from sqlalchemy import text
            result = await session.execute(
                text("SELECT COUNT(*) FROM cpi_data")
            )
            count = result.scalar()
            
            if count == 0:
                logger.info("Creating sample CPI data...")
                
                # Add some recent CPI data for testing
                sample_cpi_data = [
                    CPIData(
                        year=2024,
                        month=1,
                        cpi_value=Decimal("310.326"),
                        reference_date=date(2024, 1, 1),
                        region="US",
                        data_source="BLS",
                        series_id="CUUR0000SA0"
                    ),
                    CPIData(
                        year=2023,
                        month=12,
                        cpi_value=Decimal("307.671"),
                        reference_date=date(2023, 12, 1),
                        region="US", 
                        data_source="BLS",
                        series_id="CUUR0000SA0"
                    ),
                    CPIData(
                        year=2023,
                        month=1,
                        cpi_value=Decimal("299.170"),
                        reference_date=date(2023, 1, 1),
                        region="US",
                        data_source="BLS",
                        series_id="CUUR0000SA0"
                    ),
                ]
                
                session.add_all(sample_cpi_data)
                await session.commit()
                logger.info("Sample CPI data created")
            else:
                logger.info(f"CPI data already exists ({count} records)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        return False


async def main():
    """Main initialization function."""
    logger.info("Starting database initialization...")
    
    # Test database connection
    try:
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return 1
    
    # Create and run initial migration
    if not await create_initial_migration():
        logger.error("Failed to create initial migration")
        return 1
    
    if not await run_migrations():
        logger.error("Failed to run migrations")
        return 1
    
    # Create initial data
    if not await create_initial_data():
        logger.error("Failed to create initial data")
        return 1
    
    logger.info("Database initialization completed successfully!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 