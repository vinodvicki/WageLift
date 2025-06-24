#!/usr/bin/env python3
"""
CPI Frontend Integration Test Script
Tests the CPI calculation endpoints for frontend integration
"""

import sys
import os
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CPIFrontendIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.test_results = []
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def log_test_result(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log and store test results"""
        result = {
            'test_name': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌"
        logger.info(f"{status_emoji} {test_name}: {status}")
        
        if details.get('error'):
            logger.error(f"   Error: {details['error']}")
        if details.get('response_time'):
            logger.info(f"   Response time: {details['response_time']:.3f}s")

    def test_health_check(self) -> bool:
        """Test CPI service health endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(f"{self.api_base}/cpi/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(
                    "CPI Health Check",
                    "PASS",
                    {
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'service_status': data.get('status'),
                        'service_name': data.get('service')
                    }
                )
                return True
            else:
                self.log_test_result(
                    "CPI Health Check",
                    "FAIL",
                    {
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'error': f"Unexpected status code: {response.status_code}"
                    }
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "CPI Health Check",
                "FAIL",
                {'error': str(e)}
            )
            return False

    def test_salary_gap_calculation(self) -> bool:
        """Test salary gap calculation endpoint"""
        test_data = {
            'original_salary': 75000,
            'current_salary': 80000,
            'historical_date': '2020-01-01',
            'current_date': '2024-01-01'
        }
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.api_base}/cpi/calculate-gap",
                json=test_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                calculation_data = data.get('data', {})
                
                # Check for required fields
                required_fields = ['adjusted_salary', 'percentage_gap', 'dollar_gap', 'inflation_rate']
                missing_fields = [field for field in required_fields if field not in calculation_data]
                
                if missing_fields:
                    self.log_test_result(
                        "Salary Gap Calculation",
                        "FAIL",
                        {
                            'status_code': response.status_code,
                            'response_time': response_time,
                            'error': f"Missing fields: {missing_fields}"
                        }
                    )
                    return False
                else:
                    self.log_test_result(
                        "Salary Gap Calculation",
                        "PASS",
                        {
                            'status_code': response.status_code,
                            'response_time': response_time,
                            'adjusted_salary': calculation_data['adjusted_salary'],
                            'percentage_gap': calculation_data['percentage_gap'],
                            'dollar_gap': calculation_data['dollar_gap'],
                            'inflation_rate': calculation_data['inflation_rate']
                        }
                    )
                    return True
            else:
                error_data = response.json() if response.content else {}
                self.log_test_result(
                    "Salary Gap Calculation",
                    "FAIL",
                    {
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'error': error_data.get('message', 'Unknown error')
                    }
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "Salary Gap Calculation",
                "FAIL",
                {'error': str(e)}
            )
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("🚀 Starting CPI Frontend Integration Tests")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        test_results = {
            'health_check': self.test_health_check(),
            'salary_gap_calculation': self.test_salary_gap_calculation()
        }
        
        total_time = time.time() - start_time
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate final report
        logger.info("=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Total Time: {total_time:.2f}s")
        
        # Overall status
        overall_status = "PASS" if all(test_results.values()) else "FAIL"
        status_emoji = "✅" if overall_status == "PASS" else "❌"
        logger.info(f"{status_emoji} Overall Status: {overall_status}")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'total_time': total_time
            },
            'test_categories': test_results,
            'detailed_results': self.test_results
        }

def main():
    """Main function to run the CPI frontend integration tests"""
    tester = CPIFrontendIntegrationTester()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if report['overall_status'] == 'PASS' else 1
    return exit_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code) 