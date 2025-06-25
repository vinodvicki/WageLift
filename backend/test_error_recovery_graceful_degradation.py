#!/usr/bin/env python3
"""
Error Recovery and Graceful Degradation Testing for WageLift
Tests for fallback mechanisms, circuit breakers, graceful degradation, and system resilience
"""

import asyncio
import json
import requests
import time
import os
import threading
import tempfile
from typing import List, Dict, Any, Optional
import random

class ErrorRecoveryGracefulDegradationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status} {details}")
    
    def test_api_fallback_mechanisms(self):
        """Test 8.1: API fallback mechanisms and degraded service"""
        try:
            fallback_errors = []
            
            # Test 1: Health endpoint resilience
            try:
                # Test multiple health check requests
                health_responses = []
                for i in range(10):
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=5)
                        health_responses.append({
                            "status_code": response.status_code,
                            "response_time": response.elapsed.total_seconds(),
                            "success": response.status_code in [200, 429]
                        })
                    except Exception as e:
                        health_responses.append({
                            "error": str(e),
                            "success": False
                        })
                
                successful_health_checks = [r for r in health_responses if r.get("success", False)]
                
                if len(successful_health_checks) < 7:  # At least 70% should succeed
                    fallback_errors.append(f"Health endpoint not resilient: {len(successful_health_checks)}/10 successful")
                    
            except Exception as e:
                fallback_errors.append(f"Health endpoint test error: {str(e)}")
            
            # Test 2: API endpoint graceful failure
            try:
                # Test non-existent endpoints for graceful error handling
                error_endpoints = [
                    "/nonexistent",
                    "/api/invalid",
                    "/health/detailed/nonexistent"
                ]
                
                for endpoint in error_endpoints:
                    try:
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                        
                        # Should return proper HTTP error codes
                        if response.status_code not in [404, 405, 422, 429]:
                            fallback_errors.append(f"Endpoint {endpoint} returned unexpected status: {response.status_code}")
                        
                        # Should return valid JSON error response
                        try:
                            error_data = response.json()
                            if "detail" not in error_data and "message" not in error_data:
                                fallback_errors.append(f"Endpoint {endpoint} returned non-standard error format")
                        except json.JSONDecodeError:
                            fallback_errors.append(f"Endpoint {endpoint} returned non-JSON error response")
                            
                    except requests.exceptions.RequestException as e:
                        # Connection errors are concerning for graceful degradation
                        fallback_errors.append(f"Connection error for {endpoint}: {str(e)}")
                        
            except Exception as e:
                fallback_errors.append(f"API graceful failure test error: {str(e)}")
            
            # Test 3: Service availability under stress
            try:
                # Simulate moderate load to test graceful handling
                concurrent_requests = []
                
                def make_stress_request(request_id):
                    """Make stress test request"""
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=3)
                        return {
                            "request_id": request_id,
                            "status_code": response.status_code,
                            "success": response.status_code in [200, 429]
                        }
                    except Exception as e:
                        return {
                            "request_id": request_id,
                            "error": str(e),
                            "success": False
                        }
                
                # Make 30 requests concurrently (moderate stress)
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                    futures = [executor.submit(make_stress_request, i) for i in range(30)]
                    stress_results = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                successful_stress = [r for r in stress_results if r.get("success", False)]
                
                if len(successful_stress) < 20:  # At least 66% should succeed
                    fallback_errors.append(f"Poor stress test performance: {len(successful_stress)}/30 successful")
                    
            except Exception as e:
                fallback_errors.append(f"Stress test error: {str(e)}")
            
            # Evaluate results
            if len(fallback_errors) == 0:
                self.log_test("API Fallback Mechanisms", "PASS", "API handles failures gracefully")
            else:
                self.log_test("API Fallback Mechanisms", "FAIL", f"Fallback errors: {len(fallback_errors)}")
                
        except Exception as e:
            self.log_test("API Fallback Mechanisms", "FAIL", f"Test error: {str(e)}")
    
    def test_circuit_breaker_patterns(self):
        """Test 8.2: Circuit breaker patterns and failure isolation"""
        try:
            circuit_errors = []
            
            # Test 1: Rate limiting as circuit breaker
            try:
                # Make rapid requests to trigger rate limiting
                rapid_requests = []
                
                for i in range(150):  # Exceed typical rate limits
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=1)
                        rapid_requests.append({
                            "request_id": i,
                            "status_code": response.status_code,
                            "is_rate_limited": response.status_code == 429
                        })
                    except Exception as e:
                        rapid_requests.append({
                            "request_id": i,
                            "error": str(e),
                            "is_rate_limited": False
                        })
                
                # Check if rate limiting kicked in (circuit breaker behavior)
                rate_limited_requests = [r for r in rapid_requests if r.get("is_rate_limited", False)]
                
                if len(rate_limited_requests) == 0:
                    circuit_errors.append("Rate limiting (circuit breaker) not functioning")
                elif len(rate_limited_requests) < 10:
                    circuit_errors.append(f"Rate limiting too lenient: only {len(rate_limited_requests)} requests limited")
                    
                # Test recovery after rate limiting
                time.sleep(2)  # Wait for rate limit to reset
                
                recovery_response = requests.get(f"{self.base_url}/health", timeout=5)
                if recovery_response.status_code not in [200, 429]:
                    circuit_errors.append("Service did not recover from rate limiting")
                    
            except Exception as e:
                circuit_errors.append(f"Circuit breaker test error: {str(e)}")
            
            # Test 2: Error threshold simulation
            try:
                # Simulate service behavior under various error conditions
                error_scenarios = [
                    {"endpoint": "/health", "expected_behavior": "always_available"},
                    {"endpoint": "/nonexistent", "expected_behavior": "consistent_404"},
                    {"endpoint": "/api/invalid", "expected_behavior": "consistent_error"}
                ]
                
                for scenario in error_scenarios:
                    endpoint = scenario["endpoint"]
                    expected = scenario["expected_behavior"]
                    
                    responses = []
                    for _ in range(5):
                        try:
                            response = requests.get(f"{self.base_url}{endpoint}", timeout=3)
                            responses.append(response.status_code)
                        except Exception:
                            responses.append(0)  # Connection error
                    
                    if expected == "always_available":
                        success_codes = [code for code in responses if code in [200, 429]]
                        if len(success_codes) < 4:  # At least 80% availability
                            circuit_errors.append(f"Health endpoint not consistently available: {success_codes}")
                            
                    elif expected == "consistent_404":
                        if not all(code == 404 for code in responses):
                            circuit_errors.append(f"Inconsistent 404 responses for {endpoint}: {responses}")
                            
            except Exception as e:
                circuit_errors.append(f"Error threshold test error: {str(e)}")
            
            # Test 3: Isolation of failures
            try:
                # Test that one endpoint failure doesn't affect others
                # First, confirm health endpoint is working
                health_response = requests.get(f"{self.base_url}/health", timeout=5)
                
                if health_response.status_code in [200, 429]:
                    # Make requests to bad endpoint
                    for _ in range(10):
                        try:
                            requests.get(f"{self.base_url}/nonexistent", timeout=2)
                        except:
                            pass
                    
                    # Check if health endpoint is still working (isolation test)
                    health_after = requests.get(f"{self.base_url}/health", timeout=5)
                    
                    if health_after.status_code not in [200, 429]:
                        circuit_errors.append("Endpoint failure not isolated - health endpoint affected")
                        
            except Exception as e:
                circuit_errors.append(f"Failure isolation test error: {str(e)}")
            
            # Evaluate results
            if len(circuit_errors) == 0:
                self.log_test("Circuit Breaker Patterns", "PASS", "Circuit breaker patterns working correctly")
            else:
                self.log_test("Circuit Breaker Patterns", "FAIL", f"Circuit breaker errors: {len(circuit_errors)}")
                
        except Exception as e:
            self.log_test("Circuit Breaker Patterns", "FAIL", f"Test error: {str(e)}")
    
    def test_graceful_degradation(self):
        """Test 8.3: Graceful degradation under various failure conditions"""
        try:
            degradation_errors = []
            
            # Test 1: Service degradation under load
            try:
                # Create controlled load and monitor response times
                load_test_results = []
                
                def timed_request(request_id):
                    """Make timed request"""
                    start_time = time.time()
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=10)
                        end_time = time.time()
                        return {
                            "request_id": request_id,
                            "response_time": end_time - start_time,
                            "status_code": response.status_code,
                            "success": response.status_code in [200, 429]
                        }
                    except Exception as e:
                        end_time = time.time()
                        return {
                            "request_id": request_id,
                            "response_time": end_time - start_time,
                            "error": str(e),
                            "success": False
                        }
                
                # Sequential requests to establish baseline
                baseline_times = []
                for i in range(5):
                    result = timed_request(i)
                    if result["success"]:
                        baseline_times.append(result["response_time"])
                
                if baseline_times:
                    baseline_avg = sum(baseline_times) / len(baseline_times)
                    
                    # Concurrent load test
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                        futures = [executor.submit(timed_request, i) for i in range(50)]
                        load_results = [future.result() for future in concurrent.futures.as_completed(futures)]
                    
                    successful_load = [r for r in load_results if r["success"]]
                    
                    if successful_load:
                        load_times = [r["response_time"] for r in successful_load]
                        load_avg = sum(load_times) / len(load_times)
                        
                        # Check for graceful degradation (slower but still working)
                        if load_avg > baseline_avg * 10:  # More than 10x slower is concerning
                            degradation_errors.append(f"Poor degradation: {load_avg:.2f}s vs {baseline_avg:.2f}s baseline")
                        
                        # Check availability under load
                        availability = len(successful_load) / len(load_results)
                        if availability < 0.8:  # Less than 80% availability
                            degradation_errors.append(f"Poor availability under load: {availability:.1%}")
                            
            except Exception as e:
                degradation_errors.append(f"Load degradation test error: {str(e)}")
            
            # Test 2: Partial service functionality
            try:
                # Test that core functionality remains available even if some features fail
                core_endpoints = [
                    "/health",
                    "/",  # Root endpoint might exist
                ]
                
                for endpoint in core_endpoints:
                    try:
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                        if response.status_code not in [200, 404, 429]:
                            degradation_errors.append(f"Core endpoint {endpoint} not gracefully handling requests: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        degradation_errors.append(f"Core endpoint {endpoint} connection error: {str(e)}")
                        
            except Exception as e:
                degradation_errors.append(f"Partial service test error: {str(e)}")
            
            # Test 3: Resource exhaustion handling
            try:
                # Test behavior under simulated resource constraints
                # This is done by making many requests quickly
                resource_test_results = []
                
                start_time = time.time()
                for i in range(100):
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=2)
                        resource_test_results.append({
                            "status_code": response.status_code,
                            "success": response.status_code in [200, 429]
                        })
                    except Exception as e:
                        resource_test_results.append({
                            "error": str(e),
                            "success": False
                        })
                
                end_time = time.time()
                total_time = end_time - start_time
                
                successful_resource = [r for r in resource_test_results if r["success"]]
                
                # Check if system maintained some level of service
                if len(successful_resource) < 50:  # At least 50% should succeed
                    degradation_errors.append(f"Poor resource exhaustion handling: {len(successful_resource)}/100 successful")
                
                # Check if system didn't completely freeze
                if total_time > 60:  # Should not take more than 1 minute for 100 requests
                    degradation_errors.append(f"System freeze under load: {total_time:.1f}s for 100 requests")
                    
            except Exception as e:
                degradation_errors.append(f"Resource exhaustion test error: {str(e)}")
            
            # Evaluate results
            if len(degradation_errors) == 0:
                self.log_test("Graceful Degradation", "PASS", "System degrades gracefully under stress")
            else:
                self.log_test("Graceful Degradation", "FAIL", f"Degradation errors: {len(degradation_errors)}")
                
        except Exception as e:
            self.log_test("Graceful Degradation", "FAIL", f"Test error: {str(e)}")
    
    def test_system_resilience_recovery(self):
        """Test 8.4: System resilience and recovery mechanisms"""
        try:
            resilience_errors = []
            
            # Test 1: Recovery after rate limiting
            try:
                # Trigger rate limiting
                for _ in range(100):
                    try:
                        requests.get(f"{self.base_url}/health", timeout=1)
                    except:
                        pass
                
                # Check if rate limited
                rate_limit_response = requests.get(f"{self.base_url}/health", timeout=5)
                
                # Wait for recovery
                time.sleep(3)
                
                # Test recovery
                recovery_attempts = []
                for _ in range(5):
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=5)
                        recovery_attempts.append({
                            "status_code": response.status_code,
                            "recovered": response.status_code == 200
                        })
                    except Exception as e:
                        recovery_attempts.append({
                            "error": str(e),
                            "recovered": False
                        })
                
                recovered_count = sum(1 for r in recovery_attempts if r.get("recovered", False))
                
                if recovered_count == 0:
                    resilience_errors.append("System did not recover from rate limiting")
                    
            except Exception as e:
                resilience_errors.append(f"Rate limit recovery test error: {str(e)}")
            
            # Test 2: Consistent service availability
            try:
                # Test service availability over time
                availability_samples = []
                
                for sample in range(10):
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=5)
                        availability_samples.append({
                            "sample": sample,
                            "available": response.status_code in [200, 429],
                            "status_code": response.status_code
                        })
                    except Exception as e:
                        availability_samples.append({
                            "sample": sample,
                            "available": False,
                            "error": str(e)
                        })
                    
                    time.sleep(0.5)  # Small delay between samples
                
                available_count = sum(1 for s in availability_samples if s["available"])
                availability_percentage = available_count / len(availability_samples)
                
                if availability_percentage < 0.9:  # Less than 90% availability
                    resilience_errors.append(f"Poor system availability: {availability_percentage:.1%}")
                    
            except Exception as e:
                resilience_errors.append(f"Availability test error: {str(e)}")
            
            # Test 3: Error state recovery
            try:
                # Make requests to non-existent endpoints to create error states
                for _ in range(20):
                    try:
                        requests.get(f"{self.base_url}/nonexistent", timeout=2)
                    except:
                        pass
                
                # Test that normal service is still available
                normal_service_test = []
                for _ in range(5):
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=5)
                        normal_service_test.append({
                            "working": response.status_code in [200, 429]
                        })
                    except Exception as e:
                        normal_service_test.append({
                            "working": False,
                            "error": str(e)
                        })
                
                working_count = sum(1 for t in normal_service_test if t["working"])
                
                if working_count < 4:  # At least 80% should work
                    resilience_errors.append(f"Error state affected normal service: {working_count}/5 working")
                    
            except Exception as e:
                resilience_errors.append(f"Error state recovery test error: {str(e)}")
            
            # Test 4: System health monitoring
            try:
                # Test if health endpoint provides meaningful information
                health_response = requests.get(f"{self.base_url}/health", timeout=5)
                
                if health_response.status_code in [200, 429]:
                    try:
                        health_data = health_response.json()
                        
                        # Check for basic health information
                        if "status" not in health_data:
                            resilience_errors.append("Health endpoint lacks status information")
                        
                        # Health endpoint should be responsive
                        if health_response.elapsed.total_seconds() > 2:
                            resilience_errors.append(f"Health endpoint too slow: {health_response.elapsed.total_seconds():.2f}s")
                            
                    except json.JSONDecodeError:
                        resilience_errors.append("Health endpoint returns invalid JSON")
                else:
                    resilience_errors.append(f"Health endpoint not available: {health_response.status_code}")
                    
            except Exception as e:
                resilience_errors.append(f"Health monitoring test error: {str(e)}")
            
            # Evaluate results
            if len(resilience_errors) == 0:
                self.log_test("System Resilience Recovery", "PASS", "System demonstrates good resilience and recovery")
            else:
                self.log_test("System Resilience Recovery", "FAIL", f"Resilience errors: {len(resilience_errors)}")
                
        except Exception as e:
            self.log_test("System Resilience Recovery", "FAIL", f"Test error: {str(e)}")
    
    def run_all_tests(self):
        """Run all error recovery and graceful degradation tests"""
        print("🛡️ WAGELIFT ERROR RECOVERY & GRACEFUL DEGRADATION TESTING")
        print("=" * 60)
        print()
        
        tests = [
            self.test_api_fallback_mechanisms,
            self.test_circuit_breaker_patterns,
            self.test_graceful_degradation,
            self.test_system_resilience_recovery
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 ERROR RECOVERY & GRACEFUL DEGRADATION TESTING SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        if failed == 0:
            print("✅ ALL ERROR RECOVERY & GRACEFUL DEGRADATION TESTS PASSED")
        else:
            print("❌ SOME ERROR RECOVERY & GRACEFUL DEGRADATION TESTS FAILED")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = ErrorRecoveryGracefulDegradationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)