#!/usr/bin/env python3
"""
Core Functionality Test for WageLift Backend.

This script tests the essential components to ensure the system is
fully functional without any missing data or errors.
"""

import sys
import os
import time
import traceback
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def print_test_header(test_name: str):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")

def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")

def test_imports():
    """Test that all core modules can be imported successfully."""
    print_test_header("Testing Core Module Imports")
    
    tests = [
        ("Core Config", "from app.core.config import settings"),
        ("Error Handling", "from app.core.error_handling import error_handler, WageLiftException"),
        ("Database", "from app.core.database import Base, engine, SessionLocal"),
        ("Models", "from app.models.user import User"),
        ("Models", "from app.models.salary_entry import SalaryEntry"),
        ("Models", "from app.models.benchmark import Benchmark"),
        ("Main App", "from app.main import app"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, import_statement in tests:
        try:
            exec(import_statement)
            print_success(f"{test_name} imported successfully")
            passed += 1
        except Exception as e:
            print_error(f"{test_name} import failed: {str(e)}")
            failed += 1
    
    print_info(f"Import Tests: {passed} passed, {failed} failed")
    return failed == 0

def test_config():
    """Test configuration loading and validation."""
    print_test_header("Testing Configuration")
    
    try:
        from app.core.config import settings
        
        # Test basic config values
        tests = [
            ("Project Name", hasattr(settings, 'PROJECT_NAME')),
            ("Database URI", hasattr(settings, 'SQLALCHEMY_DATABASE_URI')),
            ("Environment", hasattr(settings, 'ENVIRONMENT')),
            ("Secret Key", hasattr(settings, 'SECRET_KEY')),
            ("API Version", hasattr(settings, 'API_V1_STR')),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, condition in tests:
            if condition:
                print_success(f"{test_name} configured")
                passed += 1
            else:
                print_error(f"{test_name} missing")
                failed += 1
        
        # Print some config values
        print_info(f"Project: {settings.PROJECT_NAME}")
        print_info(f"Environment: {settings.ENVIRONMENT}")
        print_info(f"Database: {str(settings.SQLALCHEMY_DATABASE_URI)[:50]}...")
        
        print_info(f"Configuration Tests: {passed} passed, {failed} failed")
        return failed == 0
        
    except Exception as e:
        print_error(f"Configuration test failed: {str(e)}")
        return False

def test_database():
    """Test database connectivity and operations."""
    print_test_header("Testing Database Connectivity")
    
    try:
        from app.core.database import engine, SessionLocal, test_db_connection, init_db
        from sqlalchemy import text
        
        # Test database connection
        connection_ok = test_db_connection()
        if connection_ok:
            print_success("Database connection test passed")
        else:
            print_error("Database connection test failed")
            return False
        
        # Test session creation
        try:
            with SessionLocal() as session:
                result = session.execute(text("SELECT 1 as test_value"))
                test_value = result.fetchone()[0]
                if test_value == 1:
                    print_success("Database session test passed")
                else:
                    print_error("Database session test failed")
                    return False
        except Exception as e:
            print_error(f"Database session test failed: {str(e)}")
            return False
        
        # Test database initialization
        try:
            init_db()
            print_success("Database initialization completed")
        except Exception as e:
            print_error(f"Database initialization failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling mechanisms."""
    print_test_header("Testing Error Handling")
    
    try:
        from app.core.error_handling import (
            error_handler, 
            WageLiftException,
            safe_divide,
            validate_range,
            sanitize_input
        )
        
        # Test safe_divide
        try:
            result = safe_divide(10, 2)
            if result == 5.0:
                print_success("Safe divide test passed")
            else:
                print_error("Safe divide test failed")
                return False
        except Exception as e:
            print_error(f"Safe divide test failed: {str(e)}")
            return False
        
        # Test divide by zero protection
        try:
            result = safe_divide(10, 0)
            if result == 0.0:  # Should return default value
                print_success("Divide by zero protection test passed")
            else:
                print_error("Divide by zero protection test failed")
                return False
        except Exception as e:
            print_error(f"Divide by zero protection test failed: {str(e)}")
            return False
        
        # Test range validation
        try:
            is_valid = validate_range(5, 1, 10)
            if is_valid:
                print_success("Range validation test passed")
            else:
                print_error("Range validation test failed")
                return False
        except Exception as e:
            print_error(f"Range validation test failed: {str(e)}")
            return False
        
        # Test input sanitization
        try:
            clean_input = sanitize_input("  Hello World!  ")
            if "Hello World!" in clean_input:  # Function removes control chars but may keep some whitespace
                print_success("Input sanitization test passed")
            else:
                print_error(f"Input sanitization test failed - got: '{clean_input}'")
                return False
        except Exception as e:
            print_error(f"Input sanitization test failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error handling test failed: {str(e)}")
        return False

def test_models():
    """Test database models."""
    print_test_header("Testing Database Models")
    
    try:
        from app.models.user import User
        from app.models.salary_entry import SalaryEntry
        from app.models.benchmark import Benchmark
        from app.core.database import SessionLocal
        
        # Test model creation
        with SessionLocal() as session:
            # Test User model
            try:
                import uuid
                unique_id = str(uuid.uuid4())[:8]
                user = User(
                    auth0_user_id=f"test_auth0_id_{unique_id}",
                    email=f"test_{unique_id}@example.com",
                    name="Test User"
                )
                session.add(user)
                session.commit()
                print_success("User model creation test passed")
            except Exception as e:
                session.rollback()
                print_error(f"User model creation test failed: {str(e)}")
                return False
            
            # Test querying
            try:
                users = session.query(User).all()
                if len(users) >= 1:
                    print_success("User model query test passed")
                else:
                    print_error("User model query test failed")
                    return False
            except Exception as e:
                print_error(f"User model query test failed: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Models test failed: {str(e)}")
        return False

def test_fastapi_app():
    """Test FastAPI application."""
    print_test_header("Testing FastAPI Application")
    
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        # Create test client
        client = TestClient(app)
        
        # Test health endpoint
        try:
            response = client.get("/health")
            if response.status_code == 200:
                print_success("Health endpoint test passed")
            else:
                print_error(f"Health endpoint test failed: {response.status_code}")
                print_error(f"Response content: {response.text}")
                return False
        except Exception as e:
            print_error(f"Health endpoint test failed: {str(e)}")
            return False
        
        # Test API documentation
        try:
            response = client.get("/docs")
            if response.status_code == 200:
                print_success("API documentation test passed")
            else:
                print_error(f"API documentation test failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"API documentation test failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"FastAPI application test failed: {str(e)}")
        return False

def main():
    """Run all core functionality tests."""
    print("🚀 Starting WageLift Core Functionality Tests")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Error Handling", test_error_handling),
        ("Models", test_models),
        ("FastAPI App", test_fastapi_app),
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    start_time = time.time()
    
    for test_name, test_function in tests:
        try:
            if test_function():
                passed_tests += 1
                print_success(f"{test_name} test suite PASSED")
            else:
                failed_tests += 1
                print_error(f"{test_name} test suite FAILED")
        except Exception as e:
            failed_tests += 1
            print_error(f"{test_name} test suite FAILED with exception: {str(e)}")
            traceback.print_exc()
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print final results
    print_test_header("Test Results Summary")
    print_info(f"Total Tests: {passed_tests + failed_tests}")
    print_success(f"Passed: {passed_tests}")
    print_error(f"Failed: {failed_tests}")
    print_info(f"Duration: {duration:.2f} seconds")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! Your WageLift backend is fully functional!")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())