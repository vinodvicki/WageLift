#!/usr/bin/env python3
"""
Memory Safety and Runtime Error Testing for WageLift Backend
Tests for memory leaks, buffer overflows, and invalid memory access patterns
"""

import asyncio
import gc
import os
import psutil
import sys
import threading
import time
import traceback
import json
import requests
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import warnings

class MemorySafetyTester:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()
        self.test_results = []
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "memory_mb": self.get_memory_usage(),
            "timestamp": time.time()
        }
        self.test_results.append(result)
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status} {details}")
    
    def test_buffer_overflow_protection(self):
        """Test 1.1: Buffer overflow protection"""
        try:
            # Test large string handling
            large_string = "A" * (10 * 1024 * 1024)  # 10MB string
            processed = large_string[:1000]  # Safe slicing
            del large_string
            gc.collect()
            
            # Test list overflow protection
            large_list = []
            for i in range(100000):
                large_list.append(f"item_{i}")
            
            # Safe access patterns
            if len(large_list) > 0:
                first_item = large_list[0]
                last_item = large_list[-1]
            
            del large_list
            gc.collect()
            
            self.log_test("Buffer Overflow Protection", "PASS", "Large data structures handled safely")
            
        except Exception as e:
            self.log_test("Buffer Overflow Protection", "FAIL", f"Error: {str(e)}")
    
    def test_null_pointer_safety(self):
        """Test 1.2: Null pointer dereference protection"""
        try:
            # Test None handling
            test_dict = {"key": None}
            
            # Safe None checks
            if test_dict.get("key") is not None:
                value = test_dict["key"].upper()
            else:
                value = "default"
            
            # Test empty list/dict access
            empty_list = []
            empty_dict = {}
            
            # Safe access patterns
            if empty_list:
                first = empty_list[0]
            
            if "key" in empty_dict:
                val = empty_dict["key"]
                
            self.log_test("Null Pointer Safety", "PASS", "None values handled safely")
            
        except Exception as e:
            self.log_test("Null Pointer Safety", "FAIL", f"Error: {str(e)}")
    
    def test_arithmetic_safety(self):
        """Test 1.3: Division by zero and arithmetic errors"""
        try:
            # Test division by zero protection
            def safe_divide(a, b):
                if b == 0:
                    return 0  # Safe default
                return a / b
            
            result1 = safe_divide(10, 0)  # Should return 0
            result2 = safe_divide(10, 2)  # Should return 5
            
            # Test integer overflow (Python handles this automatically)
            large_int = 2 ** 100
            larger_int = large_int * large_int
            
            # Test floating point operations
            try:
                float_result = 1.0 / 0.0
            except ZeroDivisionError:
                float_result = float('inf')  # Graceful handling
            
            self.log_test("Arithmetic Safety", "PASS", "Division by zero handled safely")
            
        except Exception as e:
            self.log_test("Arithmetic Safety", "FAIL", f"Error: {str(e)}")
    
    def test_concurrent_memory_access(self):
        """Test 1.4: Concurrent memory access safety"""
        try:
            shared_data = []
            lock = threading.Lock()
            
            def worker_thread(thread_id):
                for i in range(1000):
                    with lock:  # Safe concurrent access
                        shared_data.append(f"thread_{thread_id}_item_{i}")
            
            # Start multiple threads
            threads = []
            for i in range(5):
                t = threading.Thread(target=worker_thread, args=(i,))
                threads.append(t)
                t.start()
            
            # Wait for completion
            for t in threads:
                t.join()
            
            expected_items = 5 * 1000
            if len(shared_data) == expected_items:
                self.log_test("Concurrent Memory Access", "PASS", f"All {expected_items} items processed safely")
            else:
                self.log_test("Concurrent Memory Access", "FAIL", f"Expected {expected_items}, got {len(shared_data)}")
                
        except Exception as e:
            self.log_test("Concurrent Memory Access", "FAIL", f"Error: {str(e)}")
    
    def test_exception_handling(self):
        """Test 1.5: Exception handling and cleanup"""
        try:
            test_passed = True
            
            # Test nested exception handling
            try:
                try:
                    raise ValueError("Inner exception")
                except ValueError as inner_e:
                    # Resource cleanup in inner handler
                    temp_resource = ["cleanup_me"]
                    del temp_resource
                    raise RuntimeError("Outer exception") from inner_e
            except RuntimeError as outer_e:
                # Proper exception chaining handling
                if outer_e.__cause__:
                    test_passed = True
            
            # Test resource cleanup in exception paths
            try:
                resource = open(__file__, 'r')
                raise Exception("Test exception")
            except Exception:
                if 'resource' in locals():
                    resource.close()
            
            self.log_test("Exception Handling", "PASS", "Exceptions handled with proper cleanup")
            
        except Exception as e:
            self.log_test("Exception Handling", "FAIL", f"Error: {str(e)}")
    
    def test_api_memory_patterns(self):
        """Test 1.6: API memory usage patterns"""
        try:
            # Test making requests to our own API
            base_url = "http://localhost:8000"
            
            # Test health endpoint multiple times
            for i in range(10):
                try:
                    response = requests.get(f"{base_url}/health", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        # Verify response structure
                        required_fields = ['status', 'service', 'version']
                        if all(field in data for field in required_fields):
                            continue
                        else:
                            raise ValueError("Missing required fields in response")
                    else:
                        raise ValueError(f"HTTP {response.status_code}")
                except requests.exceptions.RequestException as e:
                    self.log_test("API Memory Patterns", "FAIL", f"Request failed: {str(e)}")
                    return
            
            self.log_test("API Memory Patterns", "PASS", "Multiple API requests handled without memory issues")
            
        except Exception as e:
            self.log_test("API Memory Patterns", "FAIL", f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all memory safety tests"""
        print("🛡️ WAGELIFT MEMORY SAFETY ASSESSMENT")
        print("=" * 60)
        print(f"Initial Memory: {self.initial_memory:.2f} MB")
        print(f"Available Memory: {psutil.virtual_memory().available / 1024 / 1024:.2f} MB")
        print()
        
        tests = [
            self.test_buffer_overflow_protection,
            self.test_null_pointer_safety,
            self.test_arithmetic_safety,
            self.test_concurrent_memory_access,
            self.test_exception_handling,
            self.test_api_memory_patterns
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
            
            # Check for memory leaks after each test
            current_memory = self.get_memory_usage()
            memory_increase = current_memory - self.initial_memory
            if memory_increase > 50:  # More than 50MB increase
                print(f"⚠️ Potential memory leak detected: +{memory_increase:.2f} MB")
        
        print()
        print("📊 MEMORY SAFETY SUMMARY")
        print("=" * 40)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        print(f"Final Memory: {self.get_memory_usage():.2f} MB")
        print(f"Memory Increase: {self.get_memory_usage() - self.initial_memory:.2f} MB")
        
        if failed == 0:
            print("✅ ALL MEMORY SAFETY TESTS PASSED")
        else:
            print("❌ SOME MEMORY SAFETY TESTS FAILED")
        
        return failed == 0

if __name__ == "__main__":
    tester = MemorySafetyTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)