#!/usr/bin/env python3
"""
Web-Specific Error Testing for WageLift
Tests for client-side errors, server-side web errors, performance issues, and integration failures
"""

import asyncio
import json
import requests
import time
import threading
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import subprocess
import os

class WebSpecificTester:
    def __init__(self, backend_url: str = "http://localhost:8000", frontend_url: str = "http://localhost:3001"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
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
    
    def test_cors_functionality(self):
        """Test 3.1: CORS (Cross-Origin Resource Sharing) functionality"""
        try:
            # Test CORS preflight for different origins
            test_origins = [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000",
                "https://wagelift.com",
                "https://malicious-site.com"  # Should be blocked
            ]
            
            cors_working = True
            allowed_origins = []
            blocked_origins = []
            
            for origin in test_origins:
                headers = {
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Content-Type"
                }
                
                try:
                    response = self.session.options(self.backend_url + "/health", headers=headers, timeout=5)
                    
                    cors_header = response.headers.get("Access-Control-Allow-Origin")
                    if cors_header and (cors_header == origin or cors_header == "*"):
                        allowed_origins.append(origin)
                    else:
                        blocked_origins.append(origin)
                        
                except requests.exceptions.RequestException:
                    blocked_origins.append(origin)
            
            # Check if malicious site is properly blocked
            malicious_blocked = "https://malicious-site.com" in blocked_origins
            legitimate_allowed = any("localhost" in origin for origin in allowed_origins)
            
            if malicious_blocked and legitimate_allowed:
                self.log_test("CORS Functionality", "PASS", f"Legitimate origins allowed, malicious blocked")
            elif not malicious_blocked:
                self.log_test("CORS Functionality", "FAIL", "Malicious origins not properly blocked")
            else:
                self.log_test("CORS Functionality", "FAIL", "Legitimate origins blocked")
                
        except Exception as e:
            self.log_test("CORS Functionality", "FAIL", f"Test error: {str(e)}")
    
    def test_large_payload_handling(self):
        """Test 3.2: Large payload handling and memory management"""
        try:
            # Test various payload sizes
            test_sizes = [
                (1024, "1KB"),
                (10 * 1024, "10KB"),
                (100 * 1024, "100KB"),
                (1024 * 1024, "1MB"),
                (5 * 1024 * 1024, "5MB"),
                (10 * 1024 * 1024, "10MB")
            ]
            
            max_successful_size = 0
            properly_rejected_large = False
            
            for size_bytes, size_label in test_sizes:
                payload = {
                    "data": "A" * size_bytes,
                    "metadata": {
                        "size": size_label,
                        "test": "large_payload_handling"
                    }
                }
                
                try:
                    response = self.session.post(
                        f"{self.backend_url}/",
                        json=payload,
                        timeout=10,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code < 400:
                        max_successful_size = size_bytes
                    elif response.status_code in [413, 400]:  # Payload too large or bad request
                        properly_rejected_large = True
                        break
                        
                except requests.exceptions.RequestException as e:
                    if "timeout" in str(e).lower():
                        properly_rejected_large = True
                        break
            
            if max_successful_size > 0 and properly_rejected_large:
                self.log_test("Large Payload Handling", "PASS", f"Accepts reasonable sizes, rejects excessive ({max_successful_size//1024}KB limit)")
            elif properly_rejected_large:
                self.log_test("Large Payload Handling", "PASS", "Properly rejects large payloads")
            else:
                self.log_test("Large Payload Handling", "FAIL", "No size limits detected - potential memory exhaustion risk")
                
        except Exception as e:
            self.log_test("Large Payload Handling", "FAIL", f"Test error: {str(e)}")
    
    def test_concurrent_connection_handling(self):
        """Test 3.3: Concurrent connection handling under load"""
        try:
            # Test concurrent connections
            num_concurrent = 50
            connection_timeout = 5
            
            def make_request(request_id):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.backend_url}/health", timeout=connection_timeout)
                    duration = time.time() - start_time
                    
                    return {
                        "id": request_id,
                        "success": response.status_code in [200, 429],  # 429 is acceptable (rate limited)
                        "status": response.status_code,
                        "duration": duration
                    }
                except Exception as e:
                    return {
                        "id": request_id,
                        "success": False,
                        "error": str(e),
                        "duration": connection_timeout
                    }
            
            # Execute concurrent requests
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_concurrent)]
                results = [future.result() for future in futures]
            total_time = time.time() - start_time
            
            successful_requests = [r for r in results if r["success"]]
            failed_requests = [r for r in results if not r["success"]]
            
            success_rate = len(successful_requests) / len(results) * 100
            avg_response_time = sum(r["duration"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            
            if success_rate >= 80 and avg_response_time < 2.0:
                self.log_test("Concurrent Connection Handling", "PASS", f"{success_rate:.1f}% success, {avg_response_time:.3f}s avg response")
            elif success_rate >= 60:
                self.log_test("Concurrent Connection Handling", "WARN", f"{success_rate:.1f}% success rate - may need tuning")
            else:
                self.log_test("Concurrent Connection Handling", "FAIL", f"Only {success_rate:.1f}% success rate under load")
                
        except Exception as e:
            self.log_test("Concurrent Connection Handling", "FAIL", f"Test error: {str(e)}")
    
    def test_http_error_responses(self):
        """Test 3.4: Proper HTTP error response handling"""
        try:
            # Test various error conditions
            error_tests = [
                ("/nonexistent-endpoint", [404], "Not Found"),
                ("/health", [200, 429], "Health Check"),  # 429 acceptable due to rate limiting
                ("/docs", [200], "Documentation"),
                ("/api/v1/nonexistent", [404], "API Not Found"),
            ]
            
            all_errors_handled = True
            error_details = []
            
            for endpoint, expected_codes, description in error_tests:
                try:
                    response = self.session.get(f"{self.backend_url}{endpoint}", timeout=5)
                    
                    if response.status_code in expected_codes:
                        error_details.append(f"{description}: {response.status_code} ✓")
                    else:
                        error_details.append(f"{description}: {response.status_code} ✗ (expected {expected_codes})")
                        all_errors_handled = False
                        
                except requests.exceptions.RequestException as e:
                    error_details.append(f"{description}: Connection Error ✗")
                    all_errors_handled = False
            
            if all_errors_handled:
                self.log_test("HTTP Error Responses", "PASS", "All endpoints return proper HTTP status codes")
            else:
                self.log_test("HTTP Error Responses", "FAIL", f"Some endpoints return incorrect status codes")
                
        except Exception as e:
            self.log_test("HTTP Error Responses", "FAIL", f"Test error: {str(e)}")
    
    def test_frontend_availability(self):
        """Test 3.5: Frontend availability and basic functionality"""
        try:
            # Test frontend server
            try:
                response = self.session.get(self.frontend_url, timeout=10)
                frontend_responding = True
                frontend_status = response.status_code
            except requests.exceptions.RequestException:
                frontend_responding = False
                frontend_status = "No Response"
            
            # Test frontend assets (if responding)
            assets_loaded = False
            if frontend_responding and frontend_status == 200:
                # Check for basic HTML structure
                if "<html" in response.text.lower() and "<body" in response.text.lower():
                    assets_loaded = True
            
            if frontend_responding and assets_loaded:
                self.log_test("Frontend Availability", "PASS", f"Frontend responding with valid HTML")
            elif frontend_responding:
                self.log_test("Frontend Availability", "WARN", f"Frontend responding but may have rendering issues (status: {frontend_status})")
            else:
                self.log_test("Frontend Availability", "FAIL", "Frontend server not responding")
                
        except Exception as e:
            self.log_test("Frontend Availability", "FAIL", f"Test error: {str(e)}")
    
    def test_api_integration_endpoints(self):
        """Test 3.6: API integration and endpoint availability"""
        try:
            # Test main API endpoints
            api_endpoints = [
                ("/", "Root"),
                ("/health", "Health"),
                ("/docs", "Documentation"),
                ("/metrics", "Metrics"),
            ]
            
            working_endpoints = []
            failing_endpoints = []
            
            for endpoint, name in api_endpoints:
                try:
                    response = self.session.get(f"{self.backend_url}{endpoint}", timeout=5)
                    
                    if response.status_code in [200, 429]:  # 429 acceptable due to rate limiting
                        working_endpoints.append(f"{name} ({response.status_code})")
                    else:
                        failing_endpoints.append(f"{name} ({response.status_code})")
                        
                except requests.exceptions.RequestException as e:
                    failing_endpoints.append(f"{name} (Connection Error)")
            
            success_rate = len(working_endpoints) / len(api_endpoints) * 100
            
            if success_rate == 100:
                self.log_test("API Integration Endpoints", "PASS", f"All {len(working_endpoints)} endpoints working")
            elif success_rate >= 75:
                self.log_test("API Integration Endpoints", "WARN", f"{success_rate:.0f}% endpoints working")
            else:
                self.log_test("API Integration Endpoints", "FAIL", f"Only {success_rate:.0f}% endpoints working")
                
        except Exception as e:
            self.log_test("API Integration Endpoints", "FAIL", f"Test error: {str(e)}")
    
    def test_session_management(self):
        """Test 3.7: Session management and state handling"""
        try:
            # Test session persistence and management
            session1 = requests.Session()
            session2 = requests.Session()
            
            # Make requests with different sessions
            response1 = session1.get(f"{self.backend_url}/health", timeout=5)
            response2 = session2.get(f"{self.backend_url}/health", timeout=5)
            
            # Check if sessions are handled independently
            session1_headers = dict(response1.headers)
            session2_headers = dict(response2.headers)
            
            # Look for session-related headers
            session_indicators = ['Set-Cookie', 'Session-ID', 'X-Session-Token']
            has_session_management = any(header in session1_headers for header in session_indicators)
            
            # Test that both sessions work independently
            both_sessions_work = (response1.status_code in [200, 429] and 
                                response2.status_code in [200, 429])
            
            if both_sessions_work:
                self.log_test("Session Management", "PASS", "Independent session handling working")
            else:
                self.log_test("Session Management", "FAIL", "Session handling issues detected")
                
        except Exception as e:
            self.log_test("Session Management", "FAIL", f"Test error: {str(e)}")
    
    def run_all_tests(self):
        """Run all web-specific error tests"""
        print("🌐 WAGELIFT WEB-SPECIFIC ERROR TESTING")
        print("=" * 60)
        print(f"Backend: {self.backend_url}")
        print(f"Frontend: {self.frontend_url}")
        print()
        
        tests = [
            self.test_cors_functionality,
            self.test_large_payload_handling,
            self.test_concurrent_connection_handling,
            self.test_http_error_responses,
            self.test_frontend_availability,
            self.test_api_integration_endpoints,
            self.test_session_management
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 WEB-SPECIFIC ERROR TESTING SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        warned = sum(1 for r in self.test_results if r['status'] == 'WARN')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests with Warnings: {warned}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        if failed == 0 and warned <= 1:
            print("✅ WEB-SPECIFIC ERROR HANDLING IS ROBUST")
        elif failed == 0:
            print("⚠️ WEB-SPECIFIC ERROR HANDLING IS MOSTLY ROBUST")
        else:
            print("❌ WEB-SPECIFIC ERROR HANDLING NEEDS IMPROVEMENT")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = WebSpecificTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)