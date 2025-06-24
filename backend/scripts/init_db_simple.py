#!/usr/bin/env python3
"""
Simple database initialization script for WageLift Backend.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import logging
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main initialization function."""
    logger.info("Starting database initialization...")
    
    try:
        # Import database components
        from app.core.database import engine, init_db
        
        # Test database connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        
        # Create all tables
        logger.info("Creating database tables...")
        init_db()
        logger.info("Database tables created successfully")
        
        logger.info("Database initialization completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 