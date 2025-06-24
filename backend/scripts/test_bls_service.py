#!/usr/bin/env python3
"""
Test script for BLS API service functionality.

This script tests the BLS service by fetching real CPI data from the API,
processing it, and performing inflation calculations.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from services.bls_service import BLSService, BLSAPIError, CPIDataPoint, bls_service


def setup_logging():
    """Configure logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_bls_service_initialization():
    """Test BLS service initialization."""
    print("=== Testing BLS Service Initialization ===")
    
    # Test basic initialization
    service = BLSService()
    assert service.BASE_URL == "https://api.bls.gov/publicAPI/v2/timeseries/data"
    assert service.CPI_SERIES_ID == "CUSR0000SA0"
    assert service.registration_key is None
    print("✓ Basic initialization successful")
    
    # Test initialization with registration key
    service_with_key = BLSService(registration_key="test_key")
    assert service_with_key.registration_key == "test_key"
    print("✓ Initialization with registration key successful")
    
    print("✓ BLS Service initialization tests passed\n")


def test_fetch_cpi_data():
    """Test fetching CPI data from BLS API."""
    print("=== Testing CPI Data Fetching ===")
    
    try:
        # Test fetching recent data (last 2 years)
        current_year = datetime.now().year
        start_year = current_year - 2
        
        print(f"Fetching CPI data from {start_year} to {current_year}...")
        raw_data = bls_service.fetch_cpi_data(start_year=start_year, end_year=current_year)
        
        # Validate response structure
        assert 'status' in raw_data
        assert raw_data['status'] == 'REQUEST_SUCCEEDED'
        assert 'Results' in raw_data
        assert 'series' in raw_data['Results']
        assert len(raw_data['Results']['series']) > 0
        assert 'data' in raw_data['Results']['series'][0]
        
        data_points = raw_data['Results']['series'][0]['data']
        assert len(data_points) > 0
        
        print(f"✓ Successfully fetched {len(data_points)} data points")
        
        # Test individual data point structure
        sample_point = data_points[0]
        required_fields = ['year', 'period', 'periodName', 'value']
        for field in required_fields:
            assert field in sample_point, f"Missing field: {field}"
        
        print("✓ Data point structure validation passed")
        
        # Test fetching without year range (should get latest available)
        print("Fetching latest available data...")
        latest_data = bls_service.fetch_cpi_data()
        assert latest_data['status'] == 'REQUEST_SUCCEEDED'
        print("✓ Latest data fetch successful")
        
    except BLSAPIError as e:
        print(f"✗ BLS API Error: {e}")
        raise
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise
    
    print("✓ CPI Data fetching tests passed\n")


def test_process_cpi_data():
    """Test processing raw CPI data."""
    print("=== Testing CPI Data Processing ===")
    
    try:
        # Fetch raw data
        current_year = datetime.now().year
        raw_data = bls_service.fetch_cpi_data(start_year=current_year - 1, end_year=current_year)
        
        # Process the data
        processed_data = bls_service.process_cpi_data(raw_data)
        
        # Validate processed data
        assert isinstance(processed_data, list)
        assert len(processed_data) > 0
        print(f"✓ Processed {len(processed_data)} data points")
        
        # Validate individual data points
        for i, data_point in enumerate(processed_data[:3]):  # Check first 3
            assert isinstance(data_point, CPIDataPoint)
            assert isinstance(data_point.date, datetime)
            assert isinstance(data_point.value, float)
            assert data_point.value > 0  # CPI should be positive
            assert isinstance(data_point.year, int)
            assert isinstance(data_point.period, str)
            assert isinstance(data_point.period_name, str)
            
            print(f"  Point {i+1}: {data_point.date.strftime('%Y-%m')} = {data_point.value}")
        
        # Verify data is sorted by date
        for i in range(1, len(processed_data)):
            assert processed_data[i].date >= processed_data[i-1].date, "Data not sorted by date"
        
        print("✓ Data sorting validation passed")
        
    except Exception as e:
        print(f"✗ Data processing error: {e}")
        raise
    
    print("✓ CPI Data processing tests passed\n")


def test_get_latest_cpi():
    """Test getting the latest CPI data."""
    print("=== Testing Latest CPI Retrieval ===")
    
    try:
        latest_cpi = bls_service.get_latest_cpi()
        
        assert latest_cpi is not None, "Latest CPI should not be None"
        assert isinstance(latest_cpi, CPIDataPoint)
        assert latest_cpi.value > 0
        
        # Check that it's reasonably recent (within last 2 years)
        two_years_ago = datetime.now() - timedelta(days=730)
        assert latest_cpi.date >= two_years_ago, "Latest CPI data seems too old"
        
        print(f"✓ Latest CPI: {latest_cpi.date.strftime('%Y-%m')} = {latest_cpi.value}")
        print(f"  Period: {latest_cpi.period_name}")
        
    except Exception as e:
        print(f"✗ Latest CPI retrieval error: {e}")
        raise
    
    print("✓ Latest CPI retrieval tests passed\n")


def test_inflation_calculations():
    """Test inflation rate calculations."""
    print("=== Testing Inflation Rate Calculations ===")
    
    try:
        # Test inflation rate calculation between two dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # 1 year ago
        
        print(f"Calculating inflation from {start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}...")
        inflation_rate = bls_service.calculate_inflation_rate(start_date, end_date)
        
        if inflation_rate is not None:
            assert isinstance(inflation_rate, float)
            # Reasonable inflation rate bounds (-10% to +20%)
            assert -0.10 <= inflation_rate <= 0.20, f"Inflation rate {inflation_rate:.4f} seems unrealistic"
            
            print(f"✓ Calculated inflation rate: {inflation_rate:.4f} ({inflation_rate * 100:.2f}%)")
        else:
            print("⚠️  Inflation rate calculation returned None (insufficient data)")
        
        # Test annual inflation rate
        current_year = datetime.now().year
        print(f"Calculating annual inflation rate for {current_year}...")
        annual_inflation = bls_service.get_annual_inflation_rate(current_year)
        
        if annual_inflation is not None:
            assert isinstance(annual_inflation, float)
            assert -0.10 <= annual_inflation <= 0.20, f"Annual inflation {annual_inflation:.4f} seems unrealistic"
            
            print(f"✓ Annual inflation rate for {current_year}: {annual_inflation:.4f} ({annual_inflation * 100:.2f}%)")
        else:
            print(f"⚠️  Annual inflation rate for {current_year} returned None (insufficient data)")
        
    except Exception as e:
        print(f"✗ Inflation calculation error: {e}")
        raise
    
    print("✓ Inflation calculation tests passed\n")


def test_error_handling():
    """Test error handling for various scenarios."""
    print("=== Testing Error Handling ===")
    
    try:
        # Test with invalid year range
        try:
            bls_service.fetch_cpi_data(start_year=2050, end_year=2051)
            print("⚠️  Expected error for future years, but none occurred")
        except BLSAPIError:
            print("✓ Properly handled invalid year range")
        
        # Test with invalid series ID
        try:
            bls_service.fetch_cpi_data(series_id="INVALID_SERIES")
            print("⚠️  Expected error for invalid series, but none occurred")
        except BLSAPIError:
            print("✓ Properly handled invalid series ID")
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        raise
    
    print("✓ Error handling tests passed\n")


def run_integration_test():
    """Run a complete integration test scenario."""
    print("=== Running Integration Test ===")
    
    try:
        # Simulate a real-world scenario
        print("Scenario: Calculate raise recommendation for employee")
        
        # 1. Get latest CPI data
        latest_cpi = bls_service.get_latest_cpi()
        assert latest_cpi is not None
        print(f"✓ Current CPI: {latest_cpi.value} ({latest_cpi.date.strftime('%Y-%m')})")
        
        # 2. Calculate inflation since last raise (1 year ago)
        last_raise_date = datetime.now() - timedelta(days=365)
        inflation_rate = bls_service.calculate_inflation_rate(last_raise_date, datetime.now())
        
        if inflation_rate is not None:
            print(f"✓ Inflation since last raise: {inflation_rate * 100:.2f}%")
            
            # 3. Calculate recommended raise
            current_salary = 75000
            inflation_adjustment = current_salary * inflation_rate
            recommended_raise = max(inflation_adjustment, current_salary * 0.03)  # At least 3%
            
            print(f"✓ Scenario Results:")
            print(f"  Current salary: ${current_salary:,.2f}")
            print(f"  Inflation adjustment: ${inflation_adjustment:,.2f}")
            print(f"  Recommended raise: ${recommended_raise:,.2f}")
            print(f"  New salary: ${current_salary + recommended_raise:,.2f}")
        else:
            print("⚠️  Could not calculate inflation rate for integration test")
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        raise
    
    print("✓ Integration test passed\n")


def main():
    """Run all tests."""
    setup_logging()
    
    print("🚀 Starting BLS Service Tests")
    print("=" * 50)
    
    try:
        test_bls_service_initialization()
        test_fetch_cpi_data()
        test_process_cpi_data()
        test_get_latest_cpi()
        test_inflation_calculations()
        test_error_handling()
        run_integration_test()
        
        print("🎉 All BLS Service Tests Passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main() 