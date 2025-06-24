#!/usr/bin/env python3
"""
WageLift Performance Monitoring Test Suite

Comprehensive testing for:
- Prometheus metrics functionality
- Structured logging system
- Auth0 performance monitoring
- Supabase metrics tracking
- System-level monitoring
- Business metrics validation
"""

import asyncio
import json
import time
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from app.core.metrics import (
        AUTH_SUCCESS_TOTAL,
        AUTH_FAILURE_TOTAL,
        AUTH_LATENCY,
        JWT_VALIDATION_DURATION,
        JWT_CACHE_HITS,
        JWT_CACHE_MISSES,
        SUPABASE_QUERY_DURATION,
        SUPABASE_OPERATIONS_TOTAL,
        SUPABASE_ERRORS_TOTAL,
        HTTP_REQUEST_SIZE,
        HTTP_RESPONSE_SIZE,
        CACHE_OPERATIONS,
        CACHE_HIT_RATIO,
        MEMORY_USAGE,
        USER_ACTIONS,
        SALARY_CALCULATIONS,
        RAISE_REQUESTS,
        track_auth_operation,
        track_supabase_operation,
        track_cache_operation,
        update_cache_hit_ratio,
        record_user_action,
        record_business_metric,
        metrics_collector
    )
    from app.core.logging import (
        setup_structured_logging,
        get_logger,
        RequestContext,
        set_user_context,
        get_correlation_id,
        log_auth_event,
        log_database_event,
        log_api_event,
        log_business_event
    )
    print("✅ Successfully imported metrics and logging modules")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure to install required dependencies: pip install prometheus-client structlog psutil")
    sys.exit(1)

class PerformanceMonitoringTests:
    """Comprehensive test suite for performance monitoring"""
    
    def __init__(self):
        self.test_results = []
        self.logger = get_logger(__name__, component="testing")
        
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
    
    def test_prometheus_metrics_basic(self):
        """Test basic Prometheus metrics functionality"""
        try:
            # Test counter metrics
            initial_auth_success = AUTH_SUCCESS_TOTAL.labels(user_type="test")._value._value
            AUTH_SUCCESS_TOTAL.labels(user_type="test").inc()
            new_auth_success = AUTH_SUCCESS_TOTAL.labels(user_type="test")._value._value
            
            assert new_auth_success > initial_auth_success, "Counter should increment"
            
            # Test histogram metrics
            AUTH_LATENCY.labels(operation="test_operation").observe(0.5)
            JWT_VALIDATION_DURATION.labels(validation_type="test").observe(0.1)
            
            # Test gauge metrics
            MEMORY_USAGE.labels(type="test").set(1000)
            
            self.log_test_result("prometheus_metrics_basic", True, "All basic metrics working")
            
        except Exception as e:
            self.log_test_result("prometheus_metrics_basic", False, f"Error: {e}")
    
    def test_auth_metrics_tracking(self):
        """Test Auth0 metrics tracking"""
        try:
            # Test auth success tracking
            initial_success = AUTH_SUCCESS_TOTAL.labels(user_type="authenticated")._value._value
            
            @track_auth_operation("test_login")
            async def test_auth_function():
                await asyncio.sleep(0.1)  # Simulate auth time
                return True
            
            # Run the tracked function
            asyncio.run(test_auth_function())
            
            new_success = AUTH_SUCCESS_TOTAL.labels(user_type="authenticated")._value._value
            assert new_success > initial_success, "Auth success should be tracked"
            
            # Test auth failure tracking
            initial_failure = AUTH_FAILURE_TOTAL.labels(reason="test_error", method="test_login")._value._value
            
            @track_auth_operation("test_failed_login")
            async def test_failed_auth():
                raise ValueError("Test auth error")
            
            try:
                asyncio.run(test_failed_auth())
            except ValueError:
                pass  # Expected
            
            new_failure = AUTH_FAILURE_TOTAL.labels(reason="ValueError", method="test_failed_login")._value._value
            assert new_failure > initial_failure, "Auth failure should be tracked"
            
            self.log_test_result("auth_metrics_tracking", True, "Auth metrics tracking working")
            
        except Exception as e:
            self.log_test_result("auth_metrics_tracking", False, f"Error: {e}")
    
    def test_supabase_metrics_tracking(self):
        """Test Supabase metrics tracking"""
        try:
            initial_ops = SUPABASE_OPERATIONS_TOTAL.labels(
                operation="select", 
                table="test_table", 
                status="success"
            )._value._value
            
            @track_supabase_operation("select", "test_table")
            async def test_db_operation():
                await asyncio.sleep(0.05)  # Simulate DB time
                return {"id": 1, "name": "test"}
            
            # Run the tracked function
            result = asyncio.run(test_db_operation())
            
            new_ops = SUPABASE_OPERATIONS_TOTAL.labels(
                operation="select", 
                table="test_table", 
                status="success"
            )._value._value
            
            assert new_ops > initial_ops, "Database operation should be tracked"
            assert result["id"] == 1, "Function should return correct result"
            
            # Test error tracking
            initial_errors = SUPABASE_ERRORS_TOTAL.labels(
                operation="insert",
                table="test_table",
                error_code="ValueError"
            )._value._value
            
            @track_supabase_operation("insert", "test_table")
            async def test_db_error():
                raise ValueError("Test database error")
            
            try:
                asyncio.run(test_db_error())
            except ValueError:
                pass  # Expected
            
            new_errors = SUPABASE_ERRORS_TOTAL.labels(
                operation="insert",
                table="test_table",
                error_code="ValueError"
            )._value._value
            
            assert new_errors > initial_errors, "Database error should be tracked"
            
            self.log_test_result("supabase_metrics_tracking", True, "Supabase metrics tracking working")
            
        except Exception as e:
            self.log_test_result("supabase_metrics_tracking", False, f"Error: {e}")
    
    def test_cache_metrics(self):
        """Test cache metrics tracking"""
        try:
            # Test cache hit
            initial_hits = JWT_CACHE_HITS.labels(cache_type="test_cache")._value._value
            
            @track_cache_operation("test_cache")
            async def test_cache_hit():
                return "cached_value"
            
            result = asyncio.run(test_cache_hit())
            new_hits = JWT_CACHE_HITS.labels(cache_type="test_cache")._value._value
            
            assert new_hits > initial_hits, "Cache hit should be tracked"
            assert result == "cached_value", "Function should return value"
            
            # Test cache miss
            initial_misses = JWT_CACHE_MISSES.labels(cache_type="test_cache")._value._value
            
            @track_cache_operation("test_cache")
            async def test_cache_miss():
                return None
            
            asyncio.run(test_cache_miss())
            new_misses = JWT_CACHE_MISSES.labels(cache_type="test_cache")._value._value
            
            assert new_misses > initial_misses, "Cache miss should be tracked"
            
            # Test cache hit ratio calculation
            update_cache_hit_ratio("test_cache", 80, 100)
            
            self.log_test_result("cache_metrics", True, "Cache metrics tracking working")
            
        except Exception as e:
            self.log_test_result("cache_metrics", False, f"Error: {e}")
    
    def test_business_metrics(self):
        """Test business metrics tracking"""
        try:
            # Test user action tracking
            initial_actions = USER_ACTIONS.labels(action_type="test_action")._value._value
            record_user_action("test_action", "test_user_123")
            new_actions = USER_ACTIONS.labels(action_type="test_action")._value._value
            
            assert new_actions > initial_actions, "User action should be tracked"
            
            # Test salary calculation tracking
            initial_salary_calc = SALARY_CALCULATIONS.labels(calculation_type="inflation")._value._value
            record_business_metric("salary_calculation", labels={"calculation_type": "inflation"})
            new_salary_calc = SALARY_CALCULATIONS.labels(calculation_type="inflation")._value._value
            
            assert new_salary_calc > initial_salary_calc, "Salary calculation should be tracked"
            
            # Test raise request tracking
            initial_raise_req = RAISE_REQUESTS.labels(status="created")._value._value
            record_business_metric("raise_request", labels={"status": "created"})
            new_raise_req = RAISE_REQUESTS.labels(status="created")._value._value
            
            assert new_raise_req > initial_raise_req, "Raise request should be tracked"
            
            self.log_test_result("business_metrics", True, "Business metrics tracking working")
            
        except Exception as e:
            self.log_test_result("business_metrics", False, f"Error: {e}")
    
    def test_structured_logging(self):
        """Test structured logging functionality"""
        try:
            # Test basic logging
            logger = get_logger("test_logger", component="testing")
            logger.info("Test log message", test_field="test_value")
            
            # Test request context
            with RequestContext(correlation="test-123", user="user-456") as ctx:
                correlation = get_correlation_id()
                assert correlation == "test-123", "Correlation ID should be set"
                
                logger.info("Test message with context")
                
                # Test user context setting
                set_user_context("new_user_789")
                logger.info("Test message with updated user context")
            
            # Test specialized logging functions
            log_auth_event(logger, "login", True, "test_user", 0.5, extra_field="test")
            log_database_event(logger, "SELECT", "users", True, 0.1, 5)
            log_api_event(logger, "GET", "/api/test", 200, 0.2, "test_user")
            log_business_event(logger, "salary_updated", "test_user", amount=50000)
            
            self.log_test_result("structured_logging", True, "Structured logging working")
            
        except Exception as e:
            self.log_test_result("structured_logging", False, f"Error: {e}")
    
    def test_metrics_collector(self):
        """Test metrics collector functionality"""
        try:
            # Test uptime calculation
            uptime = metrics_collector.get_uptime()
            assert uptime > 0, "Uptime should be positive"
            
            # Test system metrics collection
            metrics_collector.collect_system_metrics()
            
            # Test metrics summary
            summary = metrics_collector.get_metrics_summary()
            assert "uptime_seconds" in summary, "Summary should include uptime"
            assert "auth_metrics" in summary, "Summary should include auth metrics"
            assert "supabase_metrics" in summary, "Summary should include supabase metrics"
            
            self.log_test_result("metrics_collector", True, "Metrics collector working")
            
        except Exception as e:
            self.log_test_result("metrics_collector", False, f"Error: {e}")
    
    def test_performance_scenarios(self):
        """Test real-world performance scenarios"""
        try:
            # Scenario 1: User authentication flow
            start_time = time.time()
            
            with RequestContext(user="test_user_123") as ctx:
                # Simulate auth operation
                AUTH_LATENCY.labels(operation="user_login").observe(0.2)
                AUTH_SUCCESS_TOTAL.labels(user_type="authenticated").inc()
                
                # Simulate database operations
                SUPABASE_QUERY_DURATION.labels(operation="select", table="users").observe(0.05)
                SUPABASE_OPERATIONS_TOTAL.labels(operation="select", table="users", status="success").inc()
                
                # Simulate cache operations
                JWT_CACHE_HITS.labels(cache_type="user_cache").inc()
                
                # Business metrics
                record_user_action("login", "test_user_123")
            
            total_time = time.time() - start_time
            
            # Scenario 2: Salary calculation workflow
            with RequestContext(user="test_user_456") as ctx:
                # Multiple database operations
                for table in ["salary_entries", "benchmarks", "cpi_data"]:
                    SUPABASE_QUERY_DURATION.labels(operation="select", table=table).observe(0.03)
                    SUPABASE_OPERATIONS_TOTAL.labels(operation="select", table=table, status="success").inc()
                
                # Business metrics
                record_business_metric("salary_calculation", labels={"calculation_type": "inflation"})
                record_user_action("salary_calculation", "test_user_456")
            
            # Scenario 3: Error handling
            try:
                with RequestContext(user="test_user_789"):
                    raise ValueError("Simulated error")
            except ValueError:
                AUTH_FAILURE_TOTAL.labels(reason="ValueError", method="test_scenario").inc()
                SUPABASE_ERRORS_TOTAL.labels(operation="test", table="test", error_code="ValueError").inc()
            
            self.log_test_result("performance_scenarios", True, f"Performance scenarios completed in {total_time:.3f}s")
            
        except Exception as e:
            self.log_test_result("performance_scenarios", False, f"Error: {e}")
    
    def run_all_tests(self):
        """Run all performance monitoring tests"""
        print("🚀 Starting WageLift Performance Monitoring Tests\n")
        
        # Initialize logging
        setup_structured_logging("INFO")
        
        tests = [
            self.test_prometheus_metrics_basic,
            self.test_auth_metrics_tracking,
            self.test_supabase_metrics_tracking,
            self.test_cache_metrics,
            self.test_business_metrics,
            self.test_structured_logging,
            self.test_metrics_collector,
            self.test_performance_scenarios
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test_result(test.__name__, False, f"Unexpected error: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! Performance monitoring system is ready for production.")
        else:
            print("\n⚠️  Some tests failed. Please review the issues above.")
            
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
            if result["message"]:
                print(f"    {result['message']}")
        
        return passed == total

def main():
    """Main test runner"""
    tests = PerformanceMonitoringTests()
    success = tests.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 