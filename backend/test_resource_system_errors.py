#!/usr/bin/env python3
"""
Resource and System Error Testing for WageLift
Tests for file system errors, network resource errors, and system resource management
"""

import asyncio
import json
import requests
import time
import os
import tempfile
import shutil
import socket
import threading
import subprocess
import psutil
from typing import List, Dict, Any, Optional
from pathlib import Path
import stat

class ResourceSystemTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        self.temp_dir = None
        
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
    
    def setup_test_environment(self):
        """Set up test environment with temporary files and directories"""
        try:
            self.temp_dir = tempfile.mkdtemp(prefix="wagelift_test_")
            return True
        except Exception as e:
            self.log_test("Test Environment Setup", "FAIL", f"Cannot create temp directory: {str(e)}")
            return False
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")
    
    def test_file_system_errors(self):
        """Test 5.1: File system error handling"""
        try:
            if not self.setup_test_environment():
                return
            
            file_errors = []
            
            # Test 1: File not found scenarios
            try:
                nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
                
                # Test reading non-existent file
                try:
                    with open(nonexistent_file, 'r') as f:
                        content = f.read()
                    file_errors.append("Should have raised FileNotFoundError for reading")
                except FileNotFoundError:
                    pass  # Expected behavior
                except Exception as e:
                    file_errors.append(f"Unexpected error reading non-existent file: {str(e)}")
                
                # Test safe file existence check
                if os.path.exists(nonexistent_file):
                    file_errors.append("os.path.exists incorrectly returned True for non-existent file")
                    
            except Exception as e:
                file_errors.append(f"File not found test error: {str(e)}")
            
            # Test 2: Permission denied scenarios
            try:
                # Create a file and make it read-only
                readonly_file = os.path.join(self.temp_dir, "readonly.txt")
                with open(readonly_file, 'w') as f:
                    f.write("test content")
                
                # Make file read-only
                os.chmod(readonly_file, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                
                # Test writing to read-only file
                try:
                    with open(readonly_file, 'w') as f:
                        f.write("should fail")
                    file_errors.append("Should have raised PermissionError for read-only file")
                except PermissionError:
                    pass  # Expected behavior
                except Exception as e:
                    file_errors.append(f"Unexpected error writing to read-only file: {str(e)}")
                    
            except Exception as e:
                file_errors.append(f"Permission test error: {str(e)}")
            
            # Test 3: Disk space simulation (mock)
            try:
                # Test large file creation (to simulate disk space issues)
                large_file = os.path.join(self.temp_dir, "large_test.txt")
                
                # Try to create a reasonably large file for testing
                try:
                    with open(large_file, 'w') as f:
                        # Write 10MB of data
                        chunk = "A" * 1024  # 1KB chunk
                        for i in range(10 * 1024):  # 10MB total
                            f.write(chunk)
                    
                    # Verify file was created
                    if not os.path.exists(large_file):
                        file_errors.append("Large file creation failed unexpectedly")
                    else:
                        file_size = os.path.getsize(large_file)
                        if file_size < 10 * 1024 * 1024 * 0.9:  # Allow 10% variance
                            file_errors.append(f"Large file size incorrect: {file_size}")
                            
                except Exception as e:
                    # This might be expected if disk space is actually low
                    if "No space left" in str(e) or "Disk quota exceeded" in str(e):
                        pass  # Expected behavior for actual disk space issues
                    else:
                        file_errors.append(f"Large file creation error: {str(e)}")
                        
            except Exception as e:
                file_errors.append(f"Disk space test error: {str(e)}")
            
            # Test 4: File lock conflicts
            try:
                lock_file = os.path.join(self.temp_dir, "locktest.txt")
                
                # Create a file and keep it open
                with open(lock_file, 'w') as f1:
                    f1.write("locked content")
                    
                    # Try to open the same file for writing (should work on most systems)
                    try:
                        with open(lock_file, 'r') as f2:
                            content = f2.read()
                        
                        if content != "locked content":
                            file_errors.append("File lock test: content mismatch")
                            
                    except Exception as e:
                        # Some systems may actually lock files
                        pass
                        
            except Exception as e:
                file_errors.append(f"File lock test error: {str(e)}")
            
            # Test 5: Path traversal protection
            try:
                # Test various dangerous path patterns
                dangerous_paths = [
                    "../../../etc/passwd",
                    "..\\..\\..\\windows\\system32\\config\\sam",
                    "/etc/shadow",
                    "C:\\Windows\\System32\\config\\SAM"
                ]
                
                for dangerous_path in dangerous_paths:
                    try:
                        # Should not be able to access system files
                        safe_path = os.path.join(self.temp_dir, os.path.basename(dangerous_path))
                        
                        # This should be safe - just creating a file with the basename
                        with open(safe_path, 'w') as f:
                            f.write("safe test content")
                            
                        # Verify it's actually in our temp directory
                        if not safe_path.startswith(self.temp_dir):
                            file_errors.append(f"Path traversal security issue: {safe_path}")
                            
                    except Exception as e:
                        # Errors are acceptable for dangerous paths
                        pass
                        
            except Exception as e:
                file_errors.append(f"Path traversal test error: {str(e)}")
            
            # Evaluate results
            if len(file_errors) == 0:
                self.log_test("File System Error Handling", "PASS", "All file system operations handled correctly")
            else:
                self.log_test("File System Error Handling", "FAIL", f"File system errors: {len(file_errors)}")
                
        except Exception as e:
            self.log_test("File System Error Handling", "FAIL", f"Test error: {str(e)}")
        finally:
            self.cleanup_test_environment()
    
    def test_network_resource_errors(self):
        """Test 5.2: Network resource error handling"""
        try:
            network_errors = []
            
            # Test 1: Connection timeouts
            try:
                # Test connection to a non-responsive endpoint
                timeout_urls = [
                    "http://10.255.255.1:12345",  # Non-routable IP
                    "http://httpbin.org:12345",   # Invalid port
                ]
                
                for url in timeout_urls:
                    try:
                        response = requests.get(url, timeout=2)
                        network_errors.append(f"Should have timed out for {url}")
                    except requests.exceptions.Timeout:
                        pass  # Expected behavior
                    except requests.exceptions.ConnectionError:
                        pass  # Also acceptable (connection refused/unreachable)
                    except Exception as e:
                        # Other exceptions might be acceptable depending on the system
                        pass
                        
            except Exception as e:
                network_errors.append(f"Timeout test error: {str(e)}")
            
            # Test 2: Connection refused scenarios
            try:
                # Test connection to localhost on an unused port
                unused_port = self._find_unused_port()
                if unused_port:
                    try:
                        response = requests.get(f"http://localhost:{unused_port}", timeout=5)
                        network_errors.append(f"Should have been refused on port {unused_port}")
                    except requests.exceptions.ConnectionError:
                        pass  # Expected behavior
                    except Exception as e:
                        # Other exceptions might be acceptable
                        pass
                        
            except Exception as e:
                network_errors.append(f"Connection refused test error: {str(e)}")
            
            # Test 3: DNS resolution failures
            try:
                invalid_domains = [
                    "http://this-domain-should-not-exist-12345.com",
                    "http://invalid.local.domain.test",
                ]
                
                for domain in invalid_domains:
                    try:
                        response = requests.get(domain, timeout=5)
                        network_errors.append(f"Should have failed DNS resolution for {domain}")
                    except requests.exceptions.ConnectionError:
                        pass  # Expected for DNS failures
                    except Exception as e:
                        # Other exceptions might be acceptable
                        pass
                        
            except Exception as e:
                network_errors.append(f"DNS resolution test error: {str(e)}")
            
            # Test 4: Network unreachable scenarios
            try:
                # Test connection to our backend with various error conditions
                backend_tests = [
                    (self.base_url + "/nonexistent", 404),
                    (self.base_url + "/health", [200, 429]),  # 429 acceptable due to rate limiting
                ]
                
                for url, expected_codes in backend_tests:
                    try:
                        response = requests.get(url, timeout=10)
                        if isinstance(expected_codes, list):
                            if response.status_code not in expected_codes:
                                network_errors.append(f"Unexpected status for {url}: {response.status_code}")
                        else:
                            if response.status_code != expected_codes:
                                network_errors.append(f"Unexpected status for {url}: {response.status_code}")
                                
                    except requests.exceptions.RequestException as e:
                        # Connection errors to our own backend are concerning
                        network_errors.append(f"Backend connection error for {url}: {str(e)}")
                        
            except Exception as e:
                network_errors.append(f"Backend network test error: {str(e)}")
            
            # Test 5: HTTP error handling
            try:
                # Test various HTTP error responses
                if network_errors == []:  # Only test if backend is working
                    try:
                        # Test 404 handling
                        response = requests.get(self.base_url + "/definitely-nonexistent-endpoint", timeout=5)
                        if response.status_code != 404:
                            network_errors.append(f"Expected 404, got {response.status_code}")
                            
                    except requests.exceptions.RequestException as e:
                        network_errors.append(f"HTTP error test failed: {str(e)}")
                        
            except Exception as e:
                network_errors.append(f"HTTP error test error: {str(e)}")
            
            # Evaluate results
            if len(network_errors) == 0:
                self.log_test("Network Resource Error Handling", "PASS", "All network error scenarios handled correctly")
            else:
                self.log_test("Network Resource Error Handling", "FAIL", f"Network errors: {len(network_errors)}")
                
        except Exception as e:
            self.log_test("Network Resource Error Handling", "FAIL", f"Test error: {str(e)}")
    
    def test_system_resource_errors(self):
        """Test 5.3: System resource error handling"""
        try:
            system_errors = []
            
            # Test 1: Memory usage monitoring
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                
                initial_memory = memory_info.rss
                
                # Allocate some memory and verify tracking
                large_list = []
                for i in range(100000):
                    large_list.append(f"memory_test_string_{i}" * 10)
                
                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory
                
                # Clean up
                del large_list
                
                if memory_increase < 0:
                    system_errors.append("Memory usage tracking showing negative increase")
                elif memory_increase > 1024 * 1024 * 1024:  # More than 1GB increase is suspicious
                    system_errors.append(f"Excessive memory usage increase: {memory_increase / 1024 / 1024:.1f} MB")
                    
            except Exception as e:
                system_errors.append(f"Memory monitoring error: {str(e)}")
            
            # Test 2: File descriptor usage
            try:
                # Check current file descriptor usage
                process = psutil.Process()
                initial_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
                
                # Open some files temporarily
                temp_files = []
                try:
                    for i in range(10):
                        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                        temp_files.append(temp_file)
                        temp_file.write(f"test data {i}")
                    
                    current_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
                    
                    # Clean up files
                    for temp_file in temp_files:
                        temp_file.close()
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                    
                    final_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
                    
                    # Check for file descriptor leaks
                    if current_fds > 0 and final_fds > current_fds:
                        system_errors.append(f"Potential file descriptor leak: {initial_fds} -> {final_fds}")
                        
                except Exception as cleanup_error:
                    system_errors.append(f"File descriptor cleanup error: {str(cleanup_error)}")
                    
            except Exception as e:
                # File descriptor monitoring might not be available on all systems
                pass
            
            # Test 3: Thread/process limits
            try:
                # Check current thread count
                process = psutil.Process()
                initial_threads = process.num_threads()
                
                # Create a few test threads
                test_threads = []
                
                def test_thread_function():
                    time.sleep(0.1)
                
                for i in range(5):
                    thread = threading.Thread(target=test_thread_function)
                    test_threads.append(thread)
                    thread.start()
                
                # Wait for threads to complete
                for thread in test_threads:
                    thread.join()
                
                final_threads = process.num_threads()
                
                # Check for thread leaks
                if final_threads > initial_threads + 2:  # Allow some variance
                    system_errors.append(f"Potential thread leak: {initial_threads} -> {final_threads}")
                    
            except Exception as e:
                system_errors.append(f"Thread monitoring error: {str(e)}")
            
            # Test 4: System resource availability
            try:
                # Check available system resources
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Check for critically low resources
                if memory.percent > 95:
                    system_errors.append(f"Critical memory usage: {memory.percent:.1f}%")
                
                if disk.percent > 95:
                    system_errors.append(f"Critical disk usage: {disk.percent:.1f}%")
                
                # Check CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                if cpu_percent > 95:
                    system_errors.append(f"Critical CPU usage: {cpu_percent:.1f}%")
                    
            except Exception as e:
                system_errors.append(f"Resource monitoring error: {str(e)}")
            
            # Evaluate results
            if len(system_errors) == 0:
                self.log_test("System Resource Error Handling", "PASS", "System resource management working correctly")
            else:
                self.log_test("System Resource Error Handling", "FAIL", f"System resource errors: {len(system_errors)}")
                
        except Exception as e:
            self.log_test("System Resource Error Handling", "FAIL", f"Test error: {str(e)}")
    
    def test_hardware_resource_availability(self):
        """Test 5.4: Hardware resource availability and access"""
        try:
            hardware_errors = []
            
            # Test 1: CPU availability and access
            try:
                cpu_count = psutil.cpu_count()
                if cpu_count is None or cpu_count < 1:
                    hardware_errors.append("CPU count detection failed")
                
                # Test CPU usage measurement
                cpu_times = psutil.cpu_times()
                if not hasattr(cpu_times, 'user') or not hasattr(cpu_times, 'system'):
                    hardware_errors.append("CPU time measurement unavailable")
                    
            except Exception as e:
                hardware_errors.append(f"CPU access error: {str(e)}")
            
            # Test 2: Memory hardware access
            try:
                memory = psutil.virtual_memory()
                if memory.total < 1024 * 1024:  # Less than 1MB seems wrong
                    hardware_errors.append(f"Suspicious total memory: {memory.total}")
                
                swap = psutil.swap_memory()
                # Swap might be 0 on some systems, so just check if accessible
                
            except Exception as e:
                hardware_errors.append(f"Memory hardware access error: {str(e)}")
            
            # Test 3: Disk hardware access
            try:
                disk_partitions = psutil.disk_partitions()
                if not disk_partitions:
                    hardware_errors.append("No disk partitions detected")
                
                # Test disk I/O stats
                try:
                    disk_io = psutil.disk_io_counters()
                    if disk_io is None:
                        # This might be normal on some virtualized systems
                        pass
                except:
                    # Disk I/O counters might not be available on all systems
                    pass
                    
            except Exception as e:
                hardware_errors.append(f"Disk hardware access error: {str(e)}")
            
            # Test 4: Network hardware access
            try:
                network_interfaces = psutil.net_if_addrs()
                if not network_interfaces:
                    hardware_errors.append("No network interfaces detected")
                
                # Test network I/O stats
                try:
                    net_io = psutil.net_io_counters()
                    if net_io is None:
                        hardware_errors.append("Network I/O counters unavailable")
                except:
                    # Network I/O might not be available on all systems
                    pass
                    
            except Exception as e:
                hardware_errors.append(f"Network hardware access error: {str(e)}")
            
            # Evaluate results
            if len(hardware_errors) == 0:
                self.log_test("Hardware Resource Availability", "PASS", "All hardware resources accessible")
            else:
                self.log_test("Hardware Resource Availability", "FAIL", f"Hardware access errors: {len(hardware_errors)}")
                
        except Exception as e:
            self.log_test("Hardware Resource Availability", "FAIL", f"Test error: {str(e)}")
    
    def _find_unused_port(self):
        """Find an unused port for testing"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', 0))
                return s.getsockname()[1]
        except:
            return 12345  # Fallback port
    
    def run_all_tests(self):
        """Run all resource and system error tests"""
        print("📁 WAGELIFT RESOURCE & SYSTEM ERROR TESTING")
        print("=" * 60)
        print()
        
        tests = [
            self.test_file_system_errors,
            self.test_network_resource_errors,
            self.test_system_resource_errors,
            self.test_hardware_resource_availability
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 RESOURCE & SYSTEM ERROR TESTING SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        if failed == 0:
            print("✅ ALL RESOURCE & SYSTEM TESTS PASSED")
        else:
            print("❌ SOME RESOURCE & SYSTEM TESTS FAILED")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = ResourceSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)