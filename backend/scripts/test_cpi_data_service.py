#!/usr/bin/env python3
"""
Test script for CPI Data Service functionality.

This script tests the CPI data service integration with PostgreSQL,
including data fetching, storage, and management capabilities.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
import logging

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services.bls_service import bls_service, CPIDataPoint
from core.database import SessionLocal
from models.cpi_data import CPIData
from decimal import Decimal


def setup_logging():
    """Configure logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


class SimpleCPIDataService:
    """Simplified CPI data service for testing."""
    
    def __init__(self):
        self.bls_service = bls_service
    
    def get_db_session(self):
        return SessionLocal()
    
    def store_cpi_data_point(self, db, data_point: CPIDataPoint):
        """Store a single CPI data point in the database."""
        try:
            # Check if record already exists
            existing_record = db.query(CPIData).filter(
                CPIData.year == data_point.year,
                CPIData.month == data_point.date.month,
                CPIData.series_id == self.bls_service.CPI_SERIES_ID,
                CPIData.region == "US"
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.cpi_value = Decimal(str(data_point.value))
                existing_record.reference_date = data_point.date.date()
                existing_record.updated_at = datetime.now()
                
                print(f"  ✓ Updated existing CPI record for {data_point.date.strftime('%Y-%m')}: {data_point.value}")
                return existing_record, False
            else:
                # Create new record
                new_record = CPIData(
                    year=data_point.year,
                    month=data_point.date.month,
                    cpi_value=Decimal(str(data_point.value)),
                    cpi_u_value=Decimal(str(data_point.value)),  # CUSR0000SA0 is CPI-U
                    reference_date=data_point.date.date(),
                    data_source="BLS",
                    series_id=self.bls_service.CPI_SERIES_ID,
                    region="US",
                    is_seasonal_adjusted=True,
                    is_preliminary=False,
                    is_revised=False
                )
                
                db.add(new_record)
                
                print(f"  ✓ Created new CPI record for {data_point.date.strftime('%Y-%m')}: {data_point.value}")
                return new_record, True
                
        except Exception as e:
            print(f"  ✗ Error storing CPI data point: {str(e)}")
            raise
    
    def fetch_and_store_data(self):
        """Fetch data from BLS API and store in database."""
        print("=== Testing CPI Data Storage Integration ===")
        
        db = self.get_db_session()
        try:
            # Get recent CPI data from BLS
            current_year = datetime.now().year
            start_year = current_year - 1  # Get last year's data
            
            print(f"Fetching CPI data from BLS API for {start_year}-{current_year}...")
            cpi_data_points = self.bls_service.get_cpi_range(start_year, current_year)
            
            if not cpi_data_points:
                print("✗ No data received from BLS API")
                return False
            
            print(f"Retrieved {len(cpi_data_points)} data points from BLS API")
            
            # Store data points
            new_count = 0
            updated_count = 0
            
            for data_point in cpi_data_points[:5]:  # Test with first 5 records
                try:
                    stored_record, is_new = self.store_cpi_data_point(db, data_point)
                    if stored_record:
                        if is_new:
                            new_count += 1
                        else:
                            updated_count += 1
                except Exception as e:
                    print(f"  ✗ Error processing {data_point.date}: {str(e)}")
                    continue
            
            db.commit()
            
            print(f"✓ Database storage completed: {new_count} new, {updated_count} updated records")
            return True
            
        except Exception as e:
            db.rollback()
            print(f"✗ Database error: {str(e)}")
            return False
        finally:
            db.close()
    
    def test_data_retrieval(self):
        """Test retrieving CPI data from database."""
        print("\n=== Testing Data Retrieval ===")
        
        db = self.get_db_session()
        try:
            # Get latest record
            latest_record = db.query(CPIData).filter(
                CPIData.series_id == self.bls_service.CPI_SERIES_ID
            ).order_by(CPIData.year.desc(), CPIData.month.desc()).first()
            
            if latest_record:
                print(f"✓ Latest CPI record: {latest_record.year}-{latest_record.month:02d} = {latest_record.cpi_value}")
                print(f"  Reference Date: {latest_record.reference_date}")
                print(f"  Data Source: {latest_record.data_source}")
                print(f"  Series ID: {latest_record.series_id}")
            else:
                print("✗ No CPI records found in database")
                return False
            
            # Get total count
            total_count = db.query(CPIData).filter(
                CPIData.series_id == self.bls_service.CPI_SERIES_ID
            ).count()
            print(f"✓ Total CPI records in database: {total_count}")
            
            # Get recent records
            recent_records = db.query(CPIData).filter(
                CPIData.series_id == self.bls_service.CPI_SERIES_ID
            ).order_by(CPIData.year.desc(), CPIData.month.desc()).limit(5).all()
            
            print("✓ Recent CPI records:")
            for record in recent_records:
                print(f"  {record.year}-{record.month:02d}: {record.cpi_value}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error retrieving data: {str(e)}")
            return False
        finally:
            db.close()
    
    def test_inflation_calculations(self):
        """Test inflation rate calculations using database data."""
        print("\n=== Testing Inflation Calculations ===")
        
        db = self.get_db_session()
        try:
            # Get records for calculation
            records = db.query(CPIData).filter(
                CPIData.series_id == self.bls_service.CPI_SERIES_ID
            ).order_by(CPIData.year, CPIData.month).all()
            
            if len(records) < 2:
                print("✗ Insufficient data for inflation calculations")
                return False
            
            # Calculate month-over-month inflation for latest record
            latest_record = records[-1]
            previous_record = records[-2]
            
            if latest_record.cpi_value and previous_record.cpi_value:
                monthly_inflation = CPIData.calculate_inflation_rate(
                    latest_record.cpi_value,
                    previous_record.cpi_value
                )
                print(f"✓ Monthly inflation ({previous_record.year}-{previous_record.month:02d} to {latest_record.year}-{latest_record.month:02d}): {monthly_inflation:.4f} ({float(monthly_inflation) * 100:.2f}%)")
            
            # Calculate year-over-year inflation if possible
            latest_year = latest_record.year
            latest_month = latest_record.month
            
            # Find record from same month previous year
            previous_year_record = next(
                (r for r in records 
                 if r.year == latest_year - 1 and r.month == latest_month),
                None
            )
            
            if previous_year_record and previous_year_record.cpi_value:
                annual_inflation = CPIData.calculate_inflation_rate(
                    latest_record.cpi_value,
                    previous_year_record.cpi_value
                )
                print(f"✓ Annual inflation ({previous_year_record.year}-{previous_year_record.month:02d} to {latest_record.year}-{latest_record.month:02d}): {annual_inflation:.4f} ({float(annual_inflation) * 100:.2f}%)")
            else:
                print("⚠️  Year-over-year calculation not possible (insufficient historical data)")
            
            # Test salary adjustment calculation
            test_salary = Decimal('75000.00')
            if len(records) >= 12:
                old_record = records[-12]  # 12 months ago
                adjusted_salary = CPIData.calculate_inflation_adjusted_salary(
                    test_salary,
                    old_record.cpi_value,
                    latest_record.cpi_value
                )
                purchasing_power_loss = CPIData.calculate_purchasing_power_loss(
                    test_salary,
                    old_record.cpi_value,
                    latest_record.cpi_value
                )
                
                print(f"✓ Salary adjustment example for ${test_salary}:")
                print(f"  Inflation-adjusted salary: ${adjusted_salary}")
                print(f"  Purchasing power loss: ${purchasing_power_loss}")
                print(f"  Recommended raise: ${adjusted_salary - test_salary}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error in inflation calculations: {str(e)}")
            return False
        finally:
            db.close()


def test_database_connection():
    """Test database connection."""
    print("=== Testing Database Connection ===")
    
    try:
        db = SessionLocal()
        
        # Test query
        result = db.execute("SELECT 1 as test").fetchone()
        if result and result[0] == 1:
            print("✓ Database connection successful")
            
            # Check if CPI table exists
            table_check = db.execute(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'cpi_data')"
            ).fetchone()
            
            if table_check and table_check[0]:
                print("✓ CPI data table exists")
            else:
                print("✗ CPI data table not found")
                return False
                
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        return False


def main():
    """Run all tests."""
    setup_logging()
    
    print("🚀 Starting CPI Data Service Integration Tests")
    print("=" * 60)
    
    try:
        # Test database connection
        if not test_database_connection():
            print("❌ Database connection failed. Exiting.")
            sys.exit(1)
        
        # Initialize service
        cpi_service = SimpleCPIDataService()
        
        # Run tests
        tests = [
            cpi_service.fetch_and_store_data,
            cpi_service.test_data_retrieval,
            cpi_service.test_inflation_calculations
        ]
        
        all_passed = True
        for test in tests:
            if not test():
                all_passed = False
        
        if all_passed:
            print("\n🎉 All CPI Data Service Integration Tests Passed!")
        else:
            print("\n❌ Some tests failed.")
            
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 