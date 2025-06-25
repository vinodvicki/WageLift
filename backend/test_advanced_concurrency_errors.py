#!/usr/bin/env python3
"""
Advanced Concurrency and Threading Error Testing for WageLift
Tests for race conditions, deadlocks, thread safety, and synchronization issues
"""

import asyncio
import json
import requests
import time
import threading
import concurrent.futures
import queue
import multiprocessing
from typing import List, Dict, Any, Optional
import random

class AdvancedConcurrencyTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        self.shared_data = {}
        self.locks = {}
        
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
    
    def test_race_condition_detection(self):
        """Test 7.1: Race condition detection and prevention"""
        try:
            race_errors = []
            
            # Test 1: Shared data modification race conditions
            try:
                shared_counter = {"value": 0}
                lock = threading.Lock()
                race_detected = False
                
                def increment_with_race():
                    """Function that might cause race condition"""
                    for _ in range(1000):
                        # Intentionally create race condition
                        current = shared_counter["value"]
                        time.sleep(0.0001)  # Small delay to increase race chance
                        shared_counter["value"] = current + 1
                
                def increment_with_lock():
                    """Function that prevents race condition"""
                    for _ in range(1000):
                        with lock:
                            current = shared_counter["value"]
                            shared_counter["value"] = current + 1
                
                # Test without lock (expect race condition)
                shared_counter["value"] = 0
                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=increment_with_race)
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
                
                race_result = shared_counter["value"]
                expected_without_race = 5000
                
                if race_result < expected_without_race:
                    # Race condition detected (expected)
                    race_detected = True
                
                # Test with lock (should prevent race condition)
                shared_counter["value"] = 0
                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=increment_with_lock)
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
                
                locked_result = shared_counter["value"]
                
                if locked_result != expected_without_race:
                    race_errors.append(f"Lock failed to prevent race condition: {locked_result} != {expected_without_race}")
                
                if not race_detected:
                    race_errors.append("Race condition not detected in unsafe code")
                    
            except Exception as e:
                race_errors.append(f"Race condition test error: {str(e)}")
            
            # Test 2: File access race conditions
            try:
                import tempfile
                import os
                
                temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
                temp_file.close()
                
                def write_to_file(thread_id):
                    """Write to shared file"""
                    try:
                        for i in range(100):
                            with open(temp_file.name, 'a') as f:
                                f.write(f"Thread{thread_id}-Line{i}\n")
                    except Exception as e:
                        race_errors.append(f"File write error in thread {thread_id}: {str(e)}")
                
                # Multiple threads writing to same file
                threads = []
                for i in range(3):
                    thread = threading.Thread(target=write_to_file, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
                
                # Check file integrity
                try:
                    with open(temp_file.name, 'r') as f:
                        lines = f.readlines()
                    
                    expected_lines = 3 * 100  # 3 threads * 100 lines each
                    if len(lines) != expected_lines:
                        race_errors.append(f"File race condition: expected {expected_lines} lines, got {len(lines)}")
                    
                    # Clean up
                    os.unlink(temp_file.name)
                    
                except Exception as e:
                    race_errors.append(f"File integrity check error: {str(e)}")
                    
            except Exception as e:
                race_errors.append(f"File race condition test error: {str(e)}")
            
            # Evaluate results
            if len(race_errors) == 0:
                self.log_test("Race Condition Detection", "PASS", "Race conditions properly detected and prevented")
            else:
                self.log_test("Race Condition Detection", "FAIL", f"Race condition errors: {len(race_errors)}")
                
        except Exception as e:
            self.log_test("Race Condition Detection", "FAIL", f"Test error: {str(e)}")
    
    def test_deadlock_prevention(self):
        """Test 7.2: Deadlock detection and prevention"""
        try:
            deadlock_errors = []
            
            # Test 1: Classic deadlock scenario
            try:
                lock1 = threading.Lock()
                lock2 = threading.Lock()
                deadlock_detected = False
                
                def acquire_locks_order1():
                    """Acquire locks in order 1-2"""
                    try:
                        if lock1.acquire(timeout=2):
                            time.sleep(0.1)  # Hold lock1 briefly
                            if lock2.acquire(timeout=2):
                                time.sleep(0.1)
                                lock2.release()
                            lock1.release()
                    except Exception as e:
                        deadlock_errors.append(f"Lock order 1 error: {str(e)}")
                
                def acquire_locks_order2():
                    """Acquire locks in order 2-1 (potential deadlock)"""
                    try:
                        if lock2.acquire(timeout=2):
                            time.sleep(0.1)  # Hold lock2 briefly
                            if lock1.acquire(timeout=2):
                                time.sleep(0.1)
                                lock1.release()
                            lock2.release()
                    except Exception as e:
                        deadlock_errors.append(f"Lock order 2 error: {str(e)}")
                
                # Create potential deadlock scenario
                thread1 = threading.Thread(target=acquire_locks_order1)
                thread2 = threading.Thread(target=acquire_locks_order2)
                
                start_time = time.time()
                thread1.start()
                thread2.start()
                
                # Wait for threads with timeout
                thread1.join(timeout=5)
                thread2.join(timeout=5)
                
                end_time = time.time()
                
                # Check if threads completed in reasonable time
                if thread1.is_alive() or thread2.is_alive():
                    deadlock_errors.append("Potential deadlock detected - threads did not complete")
                    deadlock_detected = True
                
                if end_time - start_time > 4:
                    deadlock_errors.append(f"Execution too slow, possible deadlock: {end_time - start_time:.2f}s")
                    
            except Exception as e:
                deadlock_errors.append(f"Deadlock test error: {str(e)}")
            
            # Test 2: Resource ordering to prevent deadlock
            try:
                resources = [threading.Lock() for _ in range(5)]
                
                def acquire_resources_ordered(resource_ids):
                    """Acquire resources in sorted order to prevent deadlock"""
                    sorted_ids = sorted(resource_ids)
                    acquired_locks = []
                    
                    try:
                        for res_id in sorted_ids:
                            if resources[res_id].acquire(timeout=1):
                                acquired_locks.append(res_id)
                            else:
                                deadlock_errors.append(f"Failed to acquire resource {res_id}")
                                break
                        
                        time.sleep(0.1)  # Do some work
                        
                        # Release in reverse order
                        for res_id in reversed(acquired_locks):
                            resources[res_id].release()
                            
                    except Exception as e:
                        deadlock_errors.append(f"Resource ordering error: {str(e)}")
                
                # Multiple threads acquiring different resource combinations
                threads = []
                resource_combinations = [
                    [0, 1, 2],
                    [1, 2, 3],
                    [2, 3, 4],
                    [0, 3, 4],
                    [1, 3, 4]
                ]
                
                for combination in resource_combinations:
                    thread = threading.Thread(target=acquire_resources_ordered, args=(combination,))
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads
                for thread in threads:
                    thread.join(timeout=3)
                
                # Check if any threads are still alive (potential deadlock)
                alive_threads = [t for t in threads if t.is_alive()]
                if alive_threads:
                    deadlock_errors.append(f"Resource ordering deadlock: {len(alive_threads)} threads stuck")
                    
            except Exception as e:
                deadlock_errors.append(f"Resource ordering test error: {str(e)}")
            
            # Evaluate results
            if len(deadlock_errors) == 0:
                self.log_test("Deadlock Prevention", "PASS", "Deadlock scenarios handled correctly")
            else:
                self.log_test("Deadlock Prevention", "FAIL", f"Deadlock errors: {len(deadlock_errors)}")
                
        except Exception as e:
            self.log_test("Deadlock Prevention", "FAIL", f"Test error: {str(e)}")
    
    def test_thread_safety_validation(self):
        """Test 7.3: Thread safety validation for shared resources"""
        try:
            thread_safety_errors = []
            
            # Test 1: Thread-safe data structures
            try:
                # Test thread-safe queue
                safe_queue = queue.Queue()
                results = []
                
                def producer(queue_obj, producer_id):
                    """Produce items for queue"""
                    for i in range(100):
                        queue_obj.put(f"producer{producer_id}_item{i}")
                
                def consumer(queue_obj, consumer_id, results_list):
                    """Consume items from queue"""
                    consumed_count = 0
                    while consumed_count < 100:
                        try:
                            item = queue_obj.get(timeout=1)
                            results_list.append(f"consumer{consumer_id}_got_{item}")
                            consumed_count += 1
                            queue_obj.task_done()
                        except queue.Empty:
                            break
                
                # Start producers and consumers
                threads = []
                
                # 2 producers
                for i in range(2):
                    thread = threading.Thread(target=producer, args=(safe_queue, i))
                    threads.append(thread)
                    thread.start()
                
                # 2 consumers
                for i in range(2):
                    thread = threading.Thread(target=consumer, args=(safe_queue, i, results))
                    threads.append(thread)
                    thread.start()
                
                # Wait for all threads
                for thread in threads:
                    thread.join()
                
                # Verify results
                if len(results) != 200:  # 2 producers * 100 items
                    thread_safety_errors.append(f"Queue thread safety issue: expected 200 results, got {len(results)}")
                    
            except Exception as e:
                thread_safety_errors.append(f"Thread-safe queue test error: {str(e)}")
            
            # Test 2: Thread-local storage
            try:
                thread_local_data = threading.local()
                
                def set_thread_local_data(thread_id):
                    """Set thread-local data"""
                    thread_local_data.value = f"thread_{thread_id}_data"
                    time.sleep(0.1)  # Allow other threads to run
                    
                    # Verify data is still correct for this thread
                    if thread_local_data.value != f"thread_{thread_id}_data":
                        thread_safety_errors.append(f"Thread-local data corruption in thread {thread_id}")
                
                threads = []
                for i in range(10):
                    thread = threading.Thread(target=set_thread_local_data, args=(i,))
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
                    
            except Exception as e:
                thread_safety_errors.append(f"Thread-local storage test error: {str(e)}")
            
            # Test 3: Atomic operations simulation
            try:
                atomic_counter = {"value": 0, "lock": threading.Lock()}
                
                def atomic_increment():
                    """Atomically increment counter"""
                    for _ in range(1000):
                        with atomic_counter["lock"]:
                            atomic_counter["value"] += 1
                
                threads = []
                for _ in range(5):
                    thread = threading.Thread(target=atomic_increment)
                    threads.append(thread)
                    thread.start()
                
                for thread in threads:
                    thread.join()
                
                expected_value = 5 * 1000
                if atomic_counter["value"] != expected_value:
                    thread_safety_errors.append(f"Atomic operation failed: {atomic_counter['value']} != {expected_value}")
                    
            except Exception as e:
                thread_safety_errors.append(f"Atomic operations test error: {str(e)}")
            
            # Evaluate results
            if len(thread_safety_errors) == 0:
                self.log_test("Thread Safety Validation", "PASS", "All thread safety mechanisms working")
            else:
                self.log_test("Thread Safety Validation", "FAIL", f"Thread safety errors: {len(thread_safety_errors)}")
                
        except Exception as e:
            self.log_test("Thread Safety Validation", "FAIL", f"Test error: {str(e)}")
    
    def test_concurrent_api_access(self):
        """Test 7.4: Concurrent API access and synchronization"""
        try:
            api_errors = []
            
            # Test 1: Concurrent API requests
            try:
                def make_api_request(request_id):
                    """Make API request"""
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=5)
                        return {
                            "request_id": request_id,
                            "status_code": response.status_code,
                            "response_time": response.elapsed.total_seconds()
                        }
                    except Exception as e:
                        return {
                            "request_id": request_id,
                            "error": str(e)
                        }
                
                # Make concurrent requests
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(make_api_request, i) for i in range(50)]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                # Analyze results
                successful_requests = [r for r in results if "status_code" in r and r["status_code"] in [200, 429]]
                failed_requests = [r for r in results if "error" in r]
                
                if len(failed_requests) > 10:  # Allow some failures due to rate limiting
                    api_errors.append(f"Too many concurrent API failures: {len(failed_requests)}")
                
                # Check response times
                response_times = [r.get("response_time", 0) for r in successful_requests if "response_time" in r]
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    if avg_response_time > 5.0:  # 5 seconds seems too slow
                        api_errors.append(f"Slow concurrent API responses: {avg_response_time:.2f}s average")
                        
            except Exception as e:
                api_errors.append(f"Concurrent API test error: {str(e)}")
            
            # Test 2: API rate limiting under concurrency
            try:
                def rapid_api_request(request_id):
                    """Make rapid API requests"""
                    try:
                        response = requests.get(f"{self.base_url}/health", timeout=2)
                        return response.status_code
                    except Exception:
                        return 500
                
                # Make rapid concurrent requests to test rate limiting
                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                    futures = [executor.submit(rapid_api_request, i) for i in range(100)]
                    status_codes = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                # Check for proper rate limiting
                rate_limited_responses = [code for code in status_codes if code == 429]
                
                if len(rate_limited_responses) == 0:
                    api_errors.append("Rate limiting not working under concurrent load")
                    
            except Exception as e:
                api_errors.append(f"Rate limiting test error: {str(e)}")
            
            # Evaluate results
            if len(api_errors) == 0:
                self.log_test("Concurrent API Access", "PASS", "API handles concurrent access correctly")
            else:
                self.log_test("Concurrent API Access", "FAIL", f"API concurrency errors: {len(api_errors)}")
                
        except Exception as e:
            self.log_test("Concurrent API Access", "FAIL", f"Test error: {str(e)}")
    
    def run_all_tests(self):
        """Run all advanced concurrency and threading error tests"""
        print("🔄 WAGELIFT ADVANCED CONCURRENCY & THREADING ERROR TESTING")
        print("=" * 60)
        print()
        
        tests = [
            self.test_race_condition_detection,
            self.test_deadlock_prevention,
            self.test_thread_safety_validation,
            self.test_concurrent_api_access
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 ADVANCED CONCURRENCY & THREADING ERROR TESTING SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        if failed == 0:
            print("✅ ALL ADVANCED CONCURRENCY & THREADING TESTS PASSED")
        else:
            print("❌ SOME ADVANCED CONCURRENCY & THREADING TESTS FAILED")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = AdvancedConcurrencyTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)