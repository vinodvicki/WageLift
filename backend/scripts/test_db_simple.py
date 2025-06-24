#!/usr/bin/env python3
"""
Simple database test script for WageLift Backend.
Tests all database models to verify schema integrity.
"""

import sys
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, engine
from app.models import User, SalaryEntry, Benchmark, RaiseRequest, CPIData
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_models():
    """Test all database models with CRUD operations."""
    logger.info("Testing database models...")
    
    db = SessionLocal()
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
        db.add(test_user)
        db.flush()  # Get the ID without committing
        
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
        db.add(test_salary)
        db.flush()
        
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
        db.add(test_cpi)
        db.flush()
        
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
        db.add(test_benchmark)
        db.flush()
        
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
        db.add(test_raise_request)
        db.flush()
        
        logger.info(f"Created raise request: {test_raise_request}")
        
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
        
        db.commit()
        logger.info("All tests passed! Database models are working correctly.")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Main test function."""
    logger.info("Starting database model tests...")
    
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        
        # Run model tests
        success = test_database_models()
        
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
    exit_code = main()
    sys.exit(exit_code) 