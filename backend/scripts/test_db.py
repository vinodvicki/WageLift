#!/usr/bin/env python3
"""
Database test script for WageLift Backend.

Tests all database models and relationships to verify schema integrity.
"""

import asyncio
import sys
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import AsyncSessionLocal, engine
from app.models import User, SalaryEntry, Benchmark, RaiseRequest, CPIData
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_database_models():
    """Test all database models with CRUD operations."""
    logger.info("Testing database models...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Test User model
            logger.info("Testing User model...")
            test_user = User(
                auth0_user_id="auth0|test123",
                email="test@wagelift.com",
                name="Test User",
                job_title="Software Engineer",
                company="Test Company",
                location="San Francisco, CA"
            )
            session.add(test_user)
            await session.flush()  # Get the ID without committing
            
            logger.info(f"Created user: {test_user}")
            
            # Test SalaryEntry model
            logger.info("Testing SalaryEntry model...")
            test_salary = SalaryEntry(
                user_id=test_user.id,
                annual_salary=Decimal("120000.00"),
                job_title="Software Engineer",
                company="Test Company",
                effective_date=date(2023, 1, 1),
                currency="USD",
                employment_type="full_time"
            )
            session.add(test_salary)
            await session.flush()
            
            logger.info(f"Created salary entry: {test_salary}")
            
            # Test CPIData model
            logger.info("Testing CPIData model...")
            test_cpi = CPIData(
                year=2024,
                month=1,
                cpi_value=Decimal("310.326"),
                reference_date=date(2024, 1, 1),
                region="US",
                data_source="BLS"
            )
            session.add(test_cpi)
            await session.flush()
            
            logger.info(f"Created CPI data: {test_cpi}")
            
            # Test Benchmark model
            logger.info("Testing Benchmark model...")
            test_benchmark = Benchmark(
                job_title="Software Engineer",
                location="San Francisco, CA",
                base_salary_min=Decimal("100000.00"),
                base_salary_max=Decimal("150000.00"),
                base_salary_median=Decimal("125000.00"),
                effective_date=date(2024, 1, 1),
                source="levels.fyi"
            )
            session.add(test_benchmark)
            await session.flush()
            
            logger.info(f"Created benchmark: {test_benchmark}")
            
            # Test RaiseRequest model
            logger.info("Testing RaiseRequest model...")
            test_raise_request = RaiseRequest(
                user_id=test_user.id,
                current_salary_id=test_salary.id,
                requested_salary=Decimal("135000.00"),
                inflation_impact=Decimal("8.5"),
                status="draft"
            )
            session.add(test_raise_request)
            await session.flush()
            
            logger.info(f"Created raise request: {test_raise_request}")
            
            # Test relationships
            logger.info("Testing model relationships...")
            
            # Load user with relationships
            from sqlalchemy.orm import selectinload
            from sqlalchemy import select
            
            stmt = select(User).options(
                selectinload(User.salary_entries),
                selectinload(User.raise_requests)
            ).where(User.id == test_user.id)
            
            result = await session.execute(stmt)
            user_with_relations = result.scalar_one()
            
            logger.info(f"User has {len(user_with_relations.salary_entries)} salary entries")
            logger.info(f"User has {len(user_with_relations.raise_requests)} raise requests")
            
            # Test properties and methods
            logger.info("Testing model properties...")
            
            logger.info(f"User full name: {test_user.full_name}")
            logger.info(f"User is premium: {test_user.is_premium_active}")
            
            logger.info(f"Salary total compensation: ${test_salary.total_compensation}")
            logger.info(f"Salary is current: {test_salary.is_current}")
            
            logger.info(f"CPI period display: {test_cpi.period_display}")
            logger.info(f"CPI is current month: {test_cpi.is_current_month()}")
            
            logger.info(f"Benchmark midpoint: ${test_benchmark.salary_range_midpoint}")
            logger.info(f"Benchmark is current: {test_benchmark.is_current}")
            
            logger.info(f"Raise request is active: {test_raise_request.is_active}")
            logger.info(f"Raise request has outcome: {test_raise_request.has_outcome}")
            
            # Test CPI calculations
            logger.info("Testing CPI calculations...")
            
            inflation_rate = CPIData.calculate_inflation_rate(
                Decimal("310.326"), Decimal("299.170")
            )
            logger.info(f"Calculated inflation rate: {inflation_rate:.4f} ({inflation_rate * 100:.2f}%)")
            
            adjusted_salary = CPIData.calculate_inflation_adjusted_salary(
                Decimal("120000.00"), Decimal("299.170"), Decimal("310.326")
            )
            logger.info(f"Inflation-adjusted salary: ${adjusted_salary:.2f}")
            
            await session.commit()
            logger.info("All tests passed! Database models are working correctly.")
            
            return True
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            await session.rollback()
            return False


async def main():
    """Main test function."""
    logger.info("Starting database model tests...")
    
    try:
        # Test database connection
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        
        # Run model tests
        success = await test_database_models()
        
        if success:
            logger.info("All database tests completed successfully!")
            return 0
        else:
            logger.error("Some tests failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 