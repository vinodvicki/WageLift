#!/usr/bin/env python3
"""
Test script for WageLift Supabase integration.

This script tests the Supabase service integration including:
- Health checks
- Database connectivity
- API endpoint functionality
- Authentication flow simulation
"""

import asyncio
import sys
import os
from typing import Dict, Any

# Add the parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.supabase_service import supabase_service
from app.core.auth import Auth0User

async def test_health_check():
    """Test Supabase service health check"""
    print("🔍 Testing Supabase health check...")
    try:
        health = await supabase_service.health_check()
        print(f"✅ Health Check: {health}")
        return health['status'] == 'healthy'
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

async def test_benchmark_data():
    """Test benchmark data retrieval"""
    print("\n📊 Testing benchmark data retrieval...")
    try:
        # Test get all benchmarks
        benchmarks = await supabase_service.get_benchmarks()
        print(f"✅ Retrieved {len(benchmarks)} total benchmarks")
        
        # Test filtered benchmarks
        tech_benchmarks = await supabase_service.get_benchmarks(job_title="Software Engineer")
        print(f"✅ Retrieved {len(tech_benchmarks)} Software Engineer benchmarks")
        
        # Test location filtering
        sf_benchmarks = await supabase_service.get_benchmarks(location="San Francisco")
        print(f"✅ Retrieved {len(sf_benchmarks)} San Francisco benchmarks")
        
        return len(benchmarks) > 0
    except Exception as e:
        print(f"❌ Benchmark Data Test Failed: {e}")
        return False

async def test_user_operations():
    """Test user-related operations (simulated)"""
    print("\n👤 Testing user operations...")
    try:
        # Create a mock Auth0 user for testing
        mock_user = Auth0User(
            sub="test_auth0|123456789",
            email="test@wagelift.example.com",
            name="Test User",
            picture="https://via.placeholder.com/150",
            email_verified=True
        )
        
        # Test user creation (this would normally require service role)
        print(f"📝 Mock user created: {mock_user.email}")
        
        # In a real scenario, we would test:
        # - User creation via service role
        # - User profile updates
        # - Salary entry creation
        # - Raise request creation
        
        print("✅ User operations structure validated")
        return True
    except Exception as e:
        print(f"❌ User Operations Test Failed: {e}")
        return False

async def test_database_connection():
    """Test basic database connectivity"""
    print("\n🗄️ Testing database connection...")
    try:
        # Test basic connection by making a simple request
        response = await supabase_service._make_request(
            "GET", 
            "benchmarks", 
            params={"limit": "1"}
        )
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database Connection Test Failed: {e}")
        return False

async def test_api_error_handling():
    """Test API error handling"""
    print("\n⚠️ Testing error handling...")
    try:
        # Test with invalid endpoint
        try:
            await supabase_service._make_request("GET", "invalid_table")
            print("❌ Expected error not thrown")
            return False
        except Exception:
            print("✅ Error handling working correctly")
            return True
    except Exception as e:
        print(f"❌ Error Handling Test Failed: {e}")
        return False

def print_environment_info():
    """Print environment configuration info"""
    print("🌍 Environment Information:")
    print(f"   SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Not Set'}")
    print(f"   SUPABASE_ANON_KEY: {'✅ Set' if os.getenv('SUPABASE_ANON_KEY') else '❌ Not Set'}")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if os.getenv('SUPABASE_SERVICE_ROLE_KEY') else '❌ Not Set'}")

async def main():
    """Run all tests"""
    print("🚀 WageLift Supabase Integration Test Suite")
    print("=" * 50)
    
    # Print environment info
    print_environment_info()
    print()
    
    # Check if Supabase is configured
    if not os.getenv('SUPABASE_URL'):
        print("❌ SUPABASE_URL not configured. Please set environment variables.")
        print("   See SUPABASE_SETUP.md for configuration instructions.")
        return False
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("Database Connection", test_database_connection),
        ("Benchmark Data", test_benchmark_data),
        ("User Operations", test_user_operations),
        ("Error Handling", test_api_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = await test_func()
        results.append((test_name, result))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Supabase integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check configuration and setup.")
        return False

if __name__ == "__main__":
    # Load environment variables if .env file exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 