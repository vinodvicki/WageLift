#!/usr/bin/env python3
"""
Comprehensive Supabase Connection Test
Tests all aspects of Supabase integration for WageLift
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.supabase_service import supabase_service

async def test_supabase_connection():
    """Test all Supabase functionality"""
    print("🧪 SUPABASE CONNECTION TEST")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Basic Connection
    print("1. Testing basic connection...")
    try:
        is_connected = await supabase_service.test_connection()
        if is_connected:
            print("   ✅ Supabase connection successful")
            test_results.append(("Connection Test", True, "Connected successfully"))
        else:
            print("   ❌ Supabase connection failed")
            test_results.append(("Connection Test", False, "Connection failed"))
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        test_results.append(("Connection Test", False, str(e)))
    
    # Test 2: User Management
    print("\n2. Testing user management...")
    try:
        # Create test user
        test_user_data = {
            "auth0_id": "test_auth0_123",
            "email": "test@wagelift.com",
            "full_name": "Test User",
            "profile_picture_url": "https://example.com/pic.jpg"
        }
        
        # Try to create user
        created_user = await supabase_service.create_user(test_user_data)
        if created_user:
            print("   ✅ User creation successful")
            user_id = created_user.get('id')
            
            # Test getting user by email
            fetched_user = await supabase_service.get_user_by_email("test@wagelift.com")
            if fetched_user:
                print("   ✅ User retrieval by email successful")
                test_results.append(("User Management", True, "Create and retrieve user successful"))
            else:
                print("   ❌ User retrieval failed")
                test_results.append(("User Management", False, "User retrieval failed"))
        else:
            print("   ❌ User creation failed")
            test_results.append(("User Management", False, "User creation failed"))
            
    except Exception as e:
        print(f"   ⚠️  User management test: {e}")
        test_results.append(("User Management", False, str(e)))
    
    # Test 3: Salary Entry Management
    print("\n3. Testing salary entry management...")
    try:
        # Get or create a test user first
        test_user = await supabase_service.get_user_by_email("test@wagelift.com")
        if test_user:
            salary_data = {
                "user_id": test_user['id'],
                "current_salary": 75000,
                "last_raise_date": "2023-01-01",
                "job_title": "Software Engineer",
                "location": "San Francisco, CA",
                "experience_level": "mid",
                "company_size": "medium",
                "bonus_amount": 5000
            }
            
            created_entry = await supabase_service.create_salary_entry(salary_data)
            if created_entry:
                print("   ✅ Salary entry creation successful")
                
                # Test getting salary entries
                entries = await supabase_service.get_user_salary_entries(test_user['id'])
                if entries:
                    print(f"   ✅ Retrieved {len(entries)} salary entries")
                    test_results.append(("Salary Entries", True, f"Created and retrieved {len(entries)} entries"))
                else:
                    print("   ❌ No salary entries retrieved")
                    test_results.append(("Salary Entries", False, "No entries retrieved"))
            else:
                print("   ❌ Salary entry creation failed")
                test_results.append(("Salary Entries", False, "Entry creation failed"))
        else:
            print("   ⚠️  No test user available for salary entry test")
            test_results.append(("Salary Entries", False, "No test user available"))
            
    except Exception as e:
        print(f"   ⚠️  Salary entry test: {e}")
        test_results.append(("Salary Entries", False, str(e)))
    
    # Test 4: Raise Request Management
    print("\n4. Testing raise request management...")
    try:
        test_user = await supabase_service.get_user_by_email("test@wagelift.com")
        if test_user:
            raise_data = {
                "user_id": test_user['id'],
                "current_salary": 75000,
                "requested_salary": 85000,
                "justification": "CPI adjustment and performance",
                "status": "pending",
                "letter_content": "Sample raise request letter content"
            }
            
            created_request = await supabase_service.create_raise_request(raise_data)
            if created_request:
                print("   ✅ Raise request creation successful")
                
                # Test getting raise requests
                requests = await supabase_service.get_user_raise_requests(test_user['id'])
                if requests:
                    print(f"   ✅ Retrieved {len(requests)} raise requests")
                    test_results.append(("Raise Requests", True, f"Created and retrieved {len(requests)} requests"))
                else:
                    print("   ❌ No raise requests retrieved")
                    test_results.append(("Raise Requests", False, "No requests retrieved"))
            else:
                print("   ❌ Raise request creation failed")
                test_results.append(("Raise Requests", False, "Request creation failed"))
        else:
            print("   ⚠️  No test user available for raise request test")
            test_results.append(("Raise Requests", False, "No test user available"))
            
    except Exception as e:
        print(f"   ⚠️  Raise request test: {e}")
        test_results.append(("Raise Requests", False, str(e)))
    
    # Test 5: CPI Data Management
    print("\n5. Testing CPI data management...")
    try:
        cpi_data = {
            "year": 2024,
            "period": "M01",
            "value": 310.5,
            "series_id": "CUUR0000SA0",
            "area": "U.S. city average"
        }
        
        stored_cpi = await supabase_service.store_cpi_data(cpi_data)
        if stored_cpi:
            print("   ✅ CPI data storage successful")
            
            # Test getting latest CPI data
            latest_cpi = await supabase_service.get_latest_cpi_data(5)
            if latest_cpi:
                print(f"   ✅ Retrieved {len(latest_cpi)} CPI records")
                test_results.append(("CPI Data", True, f"Stored and retrieved {len(latest_cpi)} CPI records"))
            else:
                print("   ❌ No CPI data retrieved")
                test_results.append(("CPI Data", False, "No CPI data retrieved"))
        else:
            print("   ❌ CPI data storage failed")
            test_results.append(("CPI Data", False, "CPI storage failed"))
            
    except Exception as e:
        print(f"   ⚠️  CPI data test: {e}")
        test_results.append(("CPI Data", False, str(e)))
    
    # Test 6: Benchmark Data Management
    print("\n6. Testing benchmark data management...")
    try:
        benchmark_data = {
            "job_title": "Software Engineer",
            "location": "San Francisco, CA",
            "percentile_10": 65000,
            "percentile_25": 75000,
            "percentile_50": 90000,
            "percentile_75": 110000,
            "percentile_90": 130000,
            "source": "CareerOneStop",
            "data_date": datetime.now().isoformat()
        }
        
        stored_benchmark = await supabase_service.store_benchmark_data(benchmark_data)
        if stored_benchmark:
            print("   ✅ Benchmark data storage successful")
            
            # Test getting benchmark data
            retrieved_benchmark = await supabase_service.get_benchmark_data(
                "Software Engineer", "San Francisco, CA"
            )
            if retrieved_benchmark:
                print("   ✅ Benchmark data retrieval successful")
                test_results.append(("Benchmark Data", True, "Stored and retrieved benchmark data"))
            else:
                print("   ❌ Benchmark data retrieval failed")
                test_results.append(("Benchmark Data", False, "Benchmark retrieval failed"))
        else:
            print("   ❌ Benchmark data storage failed")
            test_results.append(("Benchmark Data", False, "Benchmark storage failed"))
            
    except Exception as e:
        print(f"   ⚠️  Benchmark data test: {e}")
        test_results.append(("Benchmark Data", False, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)
    
    for test_name, success, message in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Supabase tests passed! Integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the configuration and database schema.")
        return False

if __name__ == "__main__":
    print("Starting Supabase connection test...")
    success = asyncio.run(test_supabase_connection())
    sys.exit(0 if success else 1) 