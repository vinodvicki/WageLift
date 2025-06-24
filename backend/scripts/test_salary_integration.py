#!/usr/bin/env python3
"""
Comprehensive integration test for WageLift Salary Form FastAPI Integration.
Tests the complete flow from form submission to data storage.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
import httpx
from pydantic import ValidationError

# Test configuration
API_BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"
TEST_USER_ID = "test_user_123"

# Test data generators
def generate_test_salary_data() -> Dict[str, Any]:
    """Generate test salary form data."""
    return {
        "current_salary": 95000,
        "last_raise_date": (datetime.now() - timedelta(days=365)).date().isoformat(),
        "job_title": "Senior Software Engineer",
        "location": "94107",  # San Francisco ZIP
        "experience_level": "senior",
        "company_size": "medium",
        "bonus_amount": 10000,
        "benefits": ["health_insurance", "dental", "vision", "401k"],
        "equity_details": "Stock options with 4-year vesting",
        "notes": "Remote work 3 days per week"
    }

def generate_update_data() -> Dict[str, Any]:
    """Generate update data for testing."""
    return {
        "current_salary": 105000,
        "bonus_amount": 12000,
        "notes": "Updated after performance review"
    }

class SalaryIntegrationTester:
    """Test suite for salary form integration."""
    
    def __init__(self):
        self.base_url = f"{API_BASE_URL}{API_VERSION}"
        self.test_results = []
        self.submission_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test results."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")

    async def test_api_health(self):
        """Test API health endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/salary/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "API Health Check", 
                        True, 
                        f"API is healthy - {data.get('service', 'unknown')}", 
                        data
                    )
                else:
                    self.log_test(
                        "API Health Check", 
                        False, 
                        f"Health check failed with status {response.status_code}"
                    )
        except Exception as e:
            self.log_test("API Health Check", False, f"Exception: {str(e)}")

    async def test_salary_submission(self):
        """Test salary form submission."""
        try:
            test_data = generate_test_salary_data()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/salary/submit",
                    json=test_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    self.submission_id = data.get("data_id")
                    
                    self.log_test(
                        "Salary Form Submission", 
                        True, 
                        f"Submission successful - ID: {self.submission_id}", 
                        {
                            "submission_id": self.submission_id,
                            "message": data.get("message"),
                            "next_steps": data.get("next_steps", [])
                        }
                    )
                else:
                    error_data = response.json() if response.text else {}
                    self.log_test(
                        "Salary Form Submission", 
                        False, 
                        f"Submission failed - {response.status_code}: {error_data.get('message', 'Unknown error')}"
                    )
        except Exception as e:
            self.log_test("Salary Form Submission", False, f"Exception: {str(e)}")

    async def test_user_data_retrieval(self):
        """Test retrieving user salary data."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/salary/user-data",
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "User Data Retrieval", 
                        True, 
                        f"Retrieved {len(data)} salary records", 
                        {"record_count": len(data)}
                    )
                else:
                    self.log_test(
                        "User Data Retrieval", 
                        False, 
                        f"Retrieval failed - {response.status_code}"
                    )
        except Exception as e:
            self.log_test("User Data Retrieval", False, f"Exception: {str(e)}")

    async def test_data_update(self):
        """Test updating salary data."""
        if not self.submission_id:
            self.log_test("Data Update", False, "No submission ID available for update test")
            return
            
        try:
            update_data = generate_update_data()
            
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/salary/update/{self.submission_id}",
                    json=update_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Data Update", 
                        True, 
                        f"Update successful - {data.get('message')}", 
                        data
                    )
                else:
                    error_data = response.json() if response.text else {}
                    self.log_test(
                        "Data Update", 
                        False, 
                        f"Update failed - {response.status_code}: {error_data.get('message', 'Unknown error')}"
                    )
        except Exception as e:
            self.log_test("Data Update", False, f"Exception: {str(e)}")

    async def test_validation_errors(self):
        """Test form validation with invalid data."""
        try:
            # Test with invalid salary (negative)
            invalid_data = generate_test_salary_data()
            invalid_data["current_salary"] = -50000
            invalid_data["experience_level"] = "invalid_level"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/salary/submit",
                    json=invalid_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 422:  # Validation error
                    error_data = response.json()
                    self.log_test(
                        "Validation Error Handling", 
                        True, 
                        f"Validation correctly rejected invalid data - {len(error_data.get('errors', {}).get('validation_errors', []))} errors", 
                        error_data.get("errors", {})
                    )
                else:
                    self.log_test(
                        "Validation Error Handling", 
                        False, 
                        f"Expected validation error but got status {response.status_code}"
                    )
        except Exception as e:
            self.log_test("Validation Error Handling", False, f"Exception: {str(e)}")

    async def test_data_deletion(self):
        """Test deleting salary data."""
        if not self.submission_id:
            self.log_test("Data Deletion", False, "No submission ID available for deletion test")
            return
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/salary/delete/{self.submission_id}",
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        "Data Deletion", 
                        True, 
                        f"Deletion successful - {data.get('message')}", 
                        data
                    )
                else:
                    error_data = response.json() if response.text else {}
                    self.log_test(
                        "Data Deletion", 
                        False, 
                        f"Deletion failed - {response.status_code}: {error_data.get('message', 'Unknown error')}"
                    )
        except Exception as e:
            self.log_test("Data Deletion", False, f"Exception: {str(e)}")

    def generate_report(self):
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("🧪 WAGELIFT SALARY INTEGRATION TEST REPORT")
        print("="*80)
        print(f"📊 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print("\n📋 Detailed Results:")
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}")
            if result["details"]:
                print(f"      💬 {result['details']}")
            if not result["success"] and result.get("data"):
                print(f"      🔍 Error Data: {json.dumps(result['data'], indent=6)}")
        
        print("\n🔧 Integration Status:")
        if failed_tests == 0:
            print("   🎉 ALL SYSTEMS OPERATIONAL - Ready for production!")
        elif failed_tests <= 1:
            print("   ⚠️  MOSTLY FUNCTIONAL - Minor issues detected")
        else:
            print("   🚨 INTEGRATION ISSUES - Multiple components failing")
        
        print("\n📁 Test Report saved to: salary_integration_test_report.json")
        
        # Save detailed report
        report_data = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "api_config": {
                "base_url": self.base_url,
                "test_user_id": TEST_USER_ID
            }
        }
        
        with open("salary_integration_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2, default=str)

    async def run_all_tests(self):
        """Run the complete test suite."""
        print("🚀 Starting WageLift Salary Integration Tests...")
        print(f"📍 Testing API at: {self.base_url}")
        print("-" * 80)
        
        # Test sequence
        await self.test_api_health()
        await self.test_salary_submission()
        await self.test_user_data_retrieval()
        await self.test_data_update()
        await self.test_validation_errors()
        await self.test_data_deletion()
        
        # Generate report
        self.generate_report()

async def main():
    """Main test execution."""
    tester = SalaryIntegrationTester()
    
    print("=" * 80)
    print("🔧 WAGELIFT SALARY FORM FASTAPI INTEGRATION TEST")
    print("=" * 80)
    print("📝 This test suite verifies:")
    print("   • FastAPI salary endpoints are functional")
    print("   • Data validation is working correctly")
    print("   • Database operations are successful")
    print("   • Error handling is appropriate")
    print("   • Full CRUD operations work end-to-end")
    print("=" * 80)
    
    try:
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 