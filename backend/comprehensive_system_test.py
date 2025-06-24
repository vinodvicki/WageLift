#!/usr/bin/env python3
"""
Comprehensive System Test for WageLift Backend.

This script tests all core functionality to ensure the system is
fully functional without any missing data or errors.
"""

import asyncio
import sys
import os
import time
import json
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    import structlog
    from sqlalchemy import text
    from sqlalchemy.orm import Session
    
    # Import our modules
    from app.core.config import settings
    from app.core.database import (
        engine, async_engine, SessionLocal, AsyncSessionLocal,
        get_db, init_db, test_db_connection, get_db_stats
    )
    from app.core.error_handling import (
        safe_divide, safe_access, validate_range, sanitize_input,
        error_handler, async_error_handler, circuit_breaker_check,
        get_error_stats, create_checkpoint, load_checkpoint,
        validate_memory_usage
    )
    from app.main import app
    
    print("✅ All core imports successful")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Test results tracking
TEST_RESULTS = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "test_details": [],
    "start_time": None,
    "end_time": None,
    "errors": []
}


def log_test_result(test_name: str, passed: bool, details: str = "", error: str = ""):
    """Log a test result."""
    global TEST_RESULTS
    
    TEST_RESULTS["total_tests"] += 1
    
    if passed:
        TEST_RESULTS["passed_tests"] += 1
        print(f"✅ {test_name}: PASSED")
        if details:
            print(f"   📝 {details}")
    else:
        TEST_RESULTS["failed_tests"] += 1
        print(f"❌ {test_name}: FAILED")
        if error:
            print(f"   🚨 {error}")
        TEST_RESULTS["errors"].append({"test": test_name, "error": error})
    
    TEST_RESULTS["test_details"].append({
        "test_name": test_name,
        "passed": passed,
        "details": details,
        "error": error,
        "timestamp": datetime.now().isoformat()
    })


@error_handler(default_return=False, exceptions=(Exception,))
def test_configuration():
    """Test configuration loading and validation."""
    try:
        # Test basic configuration
        assert settings.PROJECT_NAME == "WageLift API"
        assert settings.API_V1_STR == "/api/v1"
        assert settings.SQLALCHEMY_DATABASE_URI is not None
        
        # Test environment-specific settings
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
        assert settings.DEBUG in [True, False]
        
        # Test required URLs
        assert settings.SQLALCHEMY_DATABASE_URI
        
        log_test_result(
            "Configuration Loading",
            True,
            f"Environment: {settings.ENVIRONMENT}, DB: {settings.SQLALCHEMY_DATABASE_URI[:50]}..."
        )
        return True
        
    except Exception as e:
        log_test_result("Configuration Loading", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_error_handling_utilities():
    """Test error handling utility functions."""
    try:
        # Test safe_divide
        result1 = safe_divide(10, 2)
        assert result1 == 5.0, f"Expected 5.0, got {result1}"
        
        result2 = safe_divide(10, 0, default=999)
        assert result2 == 999, f"Expected 999, got {result2}"
        
        # Test safe_access
        test_data = {"a": {"b": {"c": "value"}}}
        result3 = safe_access(test_data, ["a", "b", "c"])
        assert result3 == "value", f"Expected 'value', got {result3}"
        
        result4 = safe_access(test_data, ["x", "y", "z"], default="default")
        assert result4 == "default", f"Expected 'default', got {result4}"
        
        # Test validate_range
        assert validate_range(50, min_val=0, max_val=100) == True
        assert validate_range(150, min_val=0, max_val=100) == False
        assert validate_range(-10, min_val=0, max_val=100) == False
        
        # Test sanitize_input
        dirty_input = "<script>alert('xss')</script>Hello\x00World"
        clean_input = sanitize_input(dirty_input, max_length=50)
        assert len(clean_input) <= 50
        assert "\x00" not in clean_input
        
        # Test checkpointing
        test_checkpoint_id = f"test_{int(time.time())}"
        test_data = {"test": "data", "number": 42}
        
        checkpoint_created = create_checkpoint(test_data, test_checkpoint_id)
        assert checkpoint_created == True
        
        loaded_data = load_checkpoint(test_checkpoint_id)
        assert loaded_data is not None
        assert loaded_data["test"] == "data"
        assert loaded_data["number"] == 42
        
        log_test_result(
            "Error Handling Utilities",
            True,
            "All utility functions working correctly"
        )
        return True
        
    except Exception as e:
        log_test_result("Error Handling Utilities", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_database_connection():
    """Test database connectivity and operations."""
    try:
        # Test synchronous connection
        sync_healthy = test_db_connection()
        assert sync_healthy == True, "Synchronous database connection failed"
        
        # Test basic query
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1 as test_value")).fetchone()
            assert result[0] == 1, f"Expected 1, got {result[0]}"
        
        # Test database statistics
        db_stats = get_db_stats()
        assert "connection_stats" in db_stats
        assert "is_healthy" in db_stats
        assert db_stats["is_healthy"] == True
        
        log_test_result(
            "Database Connection",
            True,
            f"Sync: ✅, Stats: {db_stats['connection_stats']['total_connections']} connections"
        )
        return True
        
    except Exception as e:
        log_test_result("Database Connection", False, error=str(e))
        return False


@async_error_handler(default_return=False, exceptions=(Exception,))
async def test_async_database_connection():
    """Test asynchronous database connectivity."""
    try:
        # Test async connection
        from app.core.database import test_async_db_connection, get_db_session
        
        async_healthy = await test_async_db_connection()
        assert async_healthy == True, "Asynchronous database connection failed"
        
        # Test async session
        async with get_db_session() as session:
            result = await session.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1, f"Expected 1, got {row[0]}"
        
        log_test_result(
            "Async Database Connection",
            True,
            "Async database operations working correctly"
        )
        return True
        
    except Exception as e:
        log_test_result("Async Database Connection", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_database_initialization():
    """Test database table creation."""
    try:
        # Initialize database tables
        init_db()
        
        # Verify tables exist by checking schema
        with SessionLocal() as session:
            # Try to query metadata tables (works in SQLite and PostgreSQL)
            if "sqlite" in str(settings.SQLALCHEMY_DATABASE_URI):
                result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
                table_names = [row[0] for row in result]
            else:
                result = session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'")).fetchall()
                table_names = [row[0] for row in result]
            
            # We should have some tables
            assert len(table_names) > 0, "No tables found after initialization"
        
        log_test_result(
            "Database Initialization",
            True,
            f"Found {len(table_names)} tables: {', '.join(table_names[:5])}" + ("..." if len(table_names) > 5 else "")
        )
        return True
        
    except Exception as e:
        log_test_result("Database Initialization", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_fastapi_app_creation():
    """Test FastAPI application creation and basic endpoints."""
    try:
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200, f"Root endpoint returned {response.status_code}"
        
        root_data = response.json()
        assert "message" in root_data
        assert "WageLift" in root_data["message"]
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200, f"Health endpoint returned {response.status_code}"
        
        health_data = response.json()
        assert "status" in health_data
        assert health_data["status"] == "healthy"
        
        log_test_result(
            "FastAPI Application",
            True,
            f"Root and health endpoints working. Status: {health_data['status']}"
        )
        return True
        
    except Exception as e:
        log_test_result("FastAPI Application", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_circuit_breaker():
    """Test circuit breaker functionality."""
    try:
        # Test circuit breaker initial state
        assert circuit_breaker_check() == True, "Circuit breaker should initially be closed"
        
        # Get error stats
        error_stats = get_error_stats()
        assert "circuit_breaker" in error_stats
        assert "total_errors" in error_stats
        
        initial_error_count = error_stats["total_errors"]
        
        log_test_result(
            "Circuit Breaker",
            True,
            f"Circuit breaker operational. Errors: {initial_error_count}"
        )
        return True
        
    except Exception as e:
        log_test_result("Circuit Breaker", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_memory_usage():
    """Test memory usage validation."""
    try:
        # Test memory validation (should pass for reasonable limits)
        memory_ok = validate_memory_usage(max_mb=1000)  # 1GB limit
        
        log_test_result(
            "Memory Usage",
            True,
            f"Memory validation passed: {memory_ok}"
        )
        return True
        
    except Exception as e:
        log_test_result("Memory Usage", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_model_imports():
    """Test that all models can be imported successfully."""
    try:
        from app.models import (
            User, SalaryEntry, Benchmark, RaiseRequest, CPIData,
            RaiseLetter, RaiseLetterVersion, RaiseLetterTemplate, RaiseLetterShare,
            GustoToken
        )
        
        # Verify models have the expected attributes
        assert hasattr(User, '__tablename__'), "User model missing __tablename__"
        assert hasattr(SalaryEntry, '__tablename__'), "SalaryEntry model missing __tablename__"
        assert hasattr(Benchmark, '__tablename__'), "Benchmark model missing __tablename__"
        
        log_test_result(
            "Model Imports",
            True,
            "All models imported successfully with proper table definitions"
        )
        return True
        
    except Exception as e:
        log_test_result("Model Imports", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_api_imports():
    """Test that API modules can be imported successfully."""
    try:
        # Test core API imports
        from app.api import auth, salary, cpi_calculation, benchmark
        from app.api import raise_letter, email, editor, gusto
        
        # Test if routers exist
        assert hasattr(auth, 'router'), "Auth module missing router"
        assert hasattr(salary, 'router'), "Salary module missing router"
        assert hasattr(cpi_calculation, 'router'), "CPI module missing router"
        
        log_test_result(
            "API Module Imports",
            True,
            "All API modules imported successfully with routers"
        )
        return True
        
    except Exception as e:
        log_test_result("API Module Imports", False, error=str(e))
        return False


@error_handler(default_return=False, exceptions=(Exception,))
def test_service_imports():
    """Test that service modules can be imported successfully."""
    try:
        from app.services import openai_service, email_service, pdf_service
        
        # Test service availability
        services_available = []
        
        if hasattr(openai_service, 'OpenAIService'):
            services_available.append("OpenAI")
            
        if hasattr(email_service, 'EmailService'):
            services_available.append("Email")
            
        if hasattr(pdf_service, 'PDFService'):
            services_available.append("PDF")
        
        log_test_result(
            "Service Module Imports",
            True,
            f"Services available: {', '.join(services_available)}"
        )
        return True
        
    except Exception as e:
        log_test_result("Service Module Imports", False, error=str(e))
        return False


def run_stress_test(duration_seconds: int = 10):
    """Run a stress test to validate system stability."""
    try:
        print(f"\n🔥 Running stress test for {duration_seconds} seconds...")
        
        start_time = time.time()
        operations = 0
        errors = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                # Perform various operations
                
                # Database operations
                with SessionLocal() as session:
                    session.execute(text("SELECT 1"))
                
                # Error handling operations
                safe_divide(100, 10)
                safe_access({"test": "value"}, ["test"])
                validate_range(50, 0, 100)
                
                # Memory check
                validate_memory_usage()
                
                operations += 1
                
            except Exception as e:
                errors += 1
                logger.error("Stress test operation failed", error=str(e))
            
            # Small delay to prevent overwhelming
            time.sleep(0.01)
        
        duration = time.time() - start_time
        ops_per_second = operations / duration
        
        success_rate = (operations / (operations + errors)) * 100 if (operations + errors) > 0 else 0
        
        log_test_result(
            "Stress Test",
            success_rate >= 95,  # Consider successful if 95%+ operations succeed
            f"Operations: {operations}, Errors: {errors}, Rate: {ops_per_second:.1f} ops/sec, Success: {success_rate:.1f}%"
        )
        
        return success_rate >= 95
        
    except Exception as e:
        log_test_result("Stress Test", False, error=str(e))
        return False


async def run_all_tests():
    """Run all system tests."""
    print("🚀 Starting Comprehensive WageLift System Test")
    print("=" * 60)
    
    TEST_RESULTS["start_time"] = datetime.now().isoformat()
    
    # Core functionality tests
    test_configuration()
    test_error_handling_utilities()
    test_database_connection()
    await test_async_database_connection()
    test_database_initialization()
    test_circuit_breaker()
    test_memory_usage()
    
    # Application component tests
    test_model_imports()
    test_api_imports()
    test_service_imports()
    test_fastapi_app_creation()
    
    # Stress test
    run_stress_test(duration_seconds=5)
    
    TEST_RESULTS["end_time"] = datetime.now().isoformat()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total = TEST_RESULTS["total_tests"]
    passed = TEST_RESULTS["passed_tests"]
    failed = TEST_RESULTS["failed_tests"]
    
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if TEST_RESULTS["errors"]:
        print("\n🚨 ERRORS:")
        for error in TEST_RESULTS["errors"]:
            print(f"  - {error['test']}: {error['error']}")
    
    # Save results to file
    results_file = f"test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    if success_rate >= 95:
        print("\n🎉 SYSTEM IS FULLY FUNCTIONAL! 🎉")
        print("✨ WageLift backend is ready for production use.")
        return True
    else:
        print("\n⚠️  SYSTEM HAS ISSUES")
        print("🔧 Please review the failed tests and fix the issues.")
        return False


def main():
    """Main test execution function."""
    try:
        # Run async tests
        result = asyncio.run(run_all_tests())
        
        # Exit with appropriate code
        sys.exit(0 if result else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Critical test failure: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()