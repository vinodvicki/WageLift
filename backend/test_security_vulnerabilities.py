#!/usr/bin/env python3
"""
Security Vulnerability Assessment for WageLift Backend
Tests for SQL injection, XSS, input validation, authentication bypasses, and other security issues
"""

import asyncio
import json
import os
import re
import requests
import time
import urllib.parse
from typing import List, Dict, Any, Optional
import warnings

class SecurityTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
        # Common attack payloads
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "' UNION SELECT * FROM users--",
            "'; DROP TABLE users; --",
            "' OR 1=1 --",
            "admin'--",
            "' OR 'x'='x",
            "1' AND '1'='1",
            "' OR EXISTS(SELECT * FROM users WHERE username='admin')--"
        ]
        
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<%2Fscript%3E%3Cscript%3Ealert('XSS')%3C%2Fscript%3E"
        ]
        
        self.path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        self.command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`",
            "$(whoami)",
            "; ping -c 1 127.0.0.1",
            "| echo vulnerable"
        ]
    
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
    
    def test_server_availability(self):
        """Test 2.1: Basic server security headers and availability"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code != 200:
                self.log_test("Server Availability", "FAIL", f"Health endpoint returned {response.status_code}")
                return False
            
            # Check security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin'
            }
            
            missing_headers = []
            for header, expected_value in security_headers.items():
                if header not in response.headers:
                    missing_headers.append(header)
                elif response.headers[header] != expected_value:
                    missing_headers.append(f"{header} (wrong value)")
            
            if missing_headers:
                self.log_test("Security Headers", "FAIL", f"Missing/incorrect: {', '.join(missing_headers)}")
            else:
                self.log_test("Security Headers", "PASS", "All security headers present and correct")
            
            self.log_test("Server Availability", "PASS", "Server responding correctly")
            return True
            
        except Exception as e:
            self.log_test("Server Availability", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_sql_injection_protection(self):
        """Test 2.2: SQL injection protection"""
        try:
            # Test various endpoints with SQL injection payloads
            test_endpoints = [
                "/",
                "/health",
                "/docs"
            ]
            
            vulnerable_found = False
            
            for endpoint in test_endpoints:
                for payload in self.sql_injection_payloads:
                    # Test in URL parameters
                    test_url = f"{self.base_url}{endpoint}?query={urllib.parse.quote(payload)}"
                    
                    try:
                        response = self.session.get(test_url, timeout=5)
                        
                        # Check for SQL error patterns in response
                        sql_error_patterns = [
                            "sql",
                            "mysql",
                            "postgresql",
                            "sqlite",
                            "syntax error",
                            "database error",
                            "unexpected token",
                            "column",
                            "table"
                        ]
                        
                        response_text = response.text.lower()
                        for pattern in sql_error_patterns:
                            if pattern in response_text and "error" in response_text:
                                vulnerable_found = True
                                break
                        
                        # Check for successful injection patterns
                        if "union" in response_text.lower() and "select" in response_text.lower():
                            vulnerable_found = True
                        
                    except requests.exceptions.RequestException:
                        continue  # Timeout/connection error is acceptable
            
            if vulnerable_found:
                self.log_test("SQL Injection Protection", "FAIL", "Potential SQL injection vulnerability detected")
            else:
                self.log_test("SQL Injection Protection", "PASS", "No SQL injection vulnerabilities detected")
                
        except Exception as e:
            self.log_test("SQL Injection Protection", "FAIL", f"Test error: {str(e)}")
    
    def test_xss_protection(self):
        """Test 2.3: Cross-Site Scripting (XSS) protection"""
        try:
            vulnerable_found = False
            
            # Test XSS in URL parameters
            for payload in self.xss_payloads:
                test_url = f"{self.base_url}/?input={urllib.parse.quote(payload)}"
                
                try:
                    response = self.session.get(test_url, timeout=5)
                    
                    # Check if payload is reflected without encoding
                    if payload in response.text or payload.replace("'", '"') in response.text:
                        vulnerable_found = True
                    
                    # Check for script execution indicators
                    dangerous_patterns = [
                        "<script>",
                        "javascript:",
                        "onload=",
                        "onerror=",
                        "onclick="
                    ]
                    
                    response_lower = response.text.lower()
                    for pattern in dangerous_patterns:
                        if pattern in response_lower:
                            vulnerable_found = True
                            break
                            
                except requests.exceptions.RequestException:
                    continue
            
            if vulnerable_found:
                self.log_test("XSS Protection", "FAIL", "Potential XSS vulnerability detected")
            else:
                self.log_test("XSS Protection", "PASS", "No XSS vulnerabilities detected")
                
        except Exception as e:
            self.log_test("XSS Protection", "FAIL", f"Test error: {str(e)}")
    
    def test_path_traversal_protection(self):
        """Test 2.4: Path traversal protection"""
        try:
            vulnerable_found = False
            
            for payload in self.path_traversal_payloads:
                test_url = f"{self.base_url}/static/{payload}"
                
                try:
                    response = self.session.get(test_url, timeout=5)
                    
                    # Check for system file content patterns
                    dangerous_patterns = [
                        "root:x:",  # /etc/passwd
                        "localhost",  # hosts file
                        "# This file",  # common file headers
                        "[users]"  # Windows-style config
                    ]
                    
                    for pattern in dangerous_patterns:
                        if pattern in response.text:
                            vulnerable_found = True
                            break
                            
                except requests.exceptions.RequestException:
                    continue
            
            if vulnerable_found:
                self.log_test("Path Traversal Protection", "FAIL", "Potential path traversal vulnerability detected")
            else:
                self.log_test("Path Traversal Protection", "PASS", "No path traversal vulnerabilities detected")
                
        except Exception as e:
            self.log_test("Path Traversal Protection", "FAIL", f"Test error: {str(e)}")
    
    def test_command_injection_protection(self):
        """Test 2.5: Command injection protection"""
        try:
            vulnerable_found = False
            
            for payload in self.command_injection_payloads:
                # Test in various parameters
                test_params = {
                    'cmd': payload,
                    'exec': payload,
                    'system': payload,
                    'command': payload
                }
                
                try:
                    response = self.session.get(f"{self.base_url}/", params=test_params, timeout=5)
                    
                    # Check for command execution indicators
                    execution_patterns = [
                        "uid=",  # id command output
                        "gid=",  # id command output
                        "root",  # whoami output
                        "bin/",  # ls output
                        "PING",  # ping command output
                        "64 bytes from"  # ping response
                    ]
                    
                    for pattern in execution_patterns:
                        if pattern in response.text:
                            vulnerable_found = True
                            break
                            
                except requests.exceptions.RequestException:
                    continue
            
            if vulnerable_found:
                self.log_test("Command Injection Protection", "FAIL", "Potential command injection vulnerability detected")
            else:
                self.log_test("Command Injection Protection", "PASS", "No command injection vulnerabilities detected")
                
        except Exception as e:
            self.log_test("Command Injection Protection", "FAIL", f"Test error: {str(e)}")
    
    def test_input_validation(self):
        """Test 2.6: Input validation and sanitization"""
        try:
            # Test malformed JSON
            malformed_payloads = [
                '{"key": value}',  # Missing quotes
                '{"key": "value",}',  # Trailing comma
                '{"key":: "value"}',  # Double colon
                '{"key" "value"}',  # Missing colon
                '{key: "value"}',  # Unquoted key
                '{"key": "value" "key2": "value2"}',  # Missing comma
            ]
            
            validation_works = True
            
            for payload in malformed_payloads:
                try:
                    response = self.session.post(
                        f"{self.base_url}/",
                        data=payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                    # Server should reject malformed JSON with 400-level error
                    if response.status_code < 400:
                        validation_works = False
                        break
                        
                except requests.exceptions.RequestException:
                    continue  # Connection errors are acceptable
            
            # Test extremely large payloads
            try:
                large_payload = '{"data": "' + 'A' * (10 * 1024 * 1024) + '"}'  # 10MB payload
                response = self.session.post(
                    f"{self.base_url}/",
                    data=large_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                # Server should reject oversized payloads
                if response.status_code == 200:
                    validation_works = False
                    
            except requests.exceptions.RequestException:
                pass  # Timeout is acceptable/expected for large payloads
            
            if validation_works:
                self.log_test("Input Validation", "PASS", "Input validation working correctly")
            else:
                self.log_test("Input Validation", "FAIL", "Input validation insufficient")
                
        except Exception as e:
            self.log_test("Input Validation", "FAIL", f"Test error: {str(e)}")
    
    def test_rate_limiting(self):
        """Test 2.7: Rate limiting protection"""
        try:
            # Make rapid requests to test rate limiting
            responses = []
            start_time = time.time()
            
            for i in range(100):  # 100 requests
                try:
                    response = self.session.get(f"{self.base_url}/health", timeout=1)
                    responses.append(response.status_code)
                    
                    # If we get rate limited, that's good
                    if response.status_code == 429:  # Too Many Requests
                        self.log_test("Rate Limiting", "PASS", f"Rate limiting active (request {i+1})")
                        return
                        
                except requests.exceptions.RequestException:
                    break  # Connection timeout might indicate protection
            
            end_time = time.time()
            requests_per_second = 100 / (end_time - start_time)
            
            # If we can make more than 200 requests per second without being limited, that's concerning
            if requests_per_second > 200:
                self.log_test("Rate Limiting", "FAIL", f"No rate limiting detected ({requests_per_second:.1f} req/s)")
            else:
                self.log_test("Rate Limiting", "PASS", f"Reasonable request rate ({requests_per_second:.1f} req/s)")
                
        except Exception as e:
            self.log_test("Rate Limiting", "FAIL", f"Test error: {str(e)}")
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🔐 WAGELIFT SECURITY VULNERABILITY ASSESSMENT")
        print("=" * 60)
        print(f"Target: {self.base_url}")
        print()
        
        # First check if server is available
        if not self.test_server_availability():
            print("❌ Server not available - cannot proceed with security tests")
            return False
        
        tests = [
            self.test_sql_injection_protection,
            self.test_xss_protection,
            self.test_path_traversal_protection,
            self.test_command_injection_protection,
            self.test_input_validation,
            self.test_rate_limiting
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 SECURITY ASSESSMENT SUMMARY")
        print("=" * 40)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        if failed == 0:
            print("✅ ALL SECURITY TESTS PASSED")
        else:
            print("❌ SOME SECURITY TESTS FAILED")
            print("🚨 SECURITY VULNERABILITIES DETECTED - IMMEDIATE ATTENTION REQUIRED")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = SecurityTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)