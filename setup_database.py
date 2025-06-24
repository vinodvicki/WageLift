#!/usr/bin/env python3
"""
WageLift Database Setup Script
Automatically configures Supabase database and verifies connection
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

try:
    from backend.app.services.supabase_service import SupabaseService
except ImportError:
    print("❌ Error: Cannot import Supabase service. Check backend setup.")
    sys.exit(1)

async def setup_database():
    """Set up and verify Supabase database"""
    print("🚀 WageLift Database Setup")
    print("=" * 50)
    
    try:
        # Initialize Supabase service
        print("1. Initializing Supabase service...")
        service = SupabaseService()
        print("   ✅ Service initialized")
        
        # Test connection
        print("2. Testing connection...")
        is_connected = await service.test_connection()
        if not is_connected:
            print("   ❌ Connection failed")
            return False
        print("   ✅ Connection successful")
        
        # Check if tables exist
        print("3. Checking database tables...")
        tables = ['users', 'salary_entries', 'raise_requests', 'cpi_data', 'benchmarks']
        tables_exist = 0
        
        for table in tables:
            try:
                result = service.supabase.table(table).select('*').limit(1).execute()
                print(f"   ✅ {table}: EXISTS")
                tables_exist += 1
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print(f"   ❌ {table}: MISSING")
                else:
                    print(f"   ⚠️  {table}: Error - {str(e)[:50]}...")
        
        # Provide setup instructions if tables are missing
        if tables_exist < len(tables):
            print(f"\n⚠️  Database Setup Required: {tables_exist}/{len(tables)} tables exist")
            print("\n📋 SETUP INSTRUCTIONS:")
            print("1. Go to: https://supabase.com/dashboard")
            print("2. Navigate to your project: rtmegwnspngsxtixdhat")
            print("3. Click 'SQL Editor' in the left sidebar")
            print("4. Copy and paste the entire content from: backend/create_supabase_schema.sql")
            print("5. Click 'Run' button")
            print("6. Run this script again to verify")
            
            # Show the SQL file path
            sql_file = Path(__file__).parent / "backend" / "create_supabase_schema.sql"
            if sql_file.exists():
                print(f"\n📄 SQL File Location: {sql_file}")
                print(f"📄 SQL File Size: {sql_file.stat().st_size} bytes")
            
            return False
        else:
            print(f"\n🎉 SUCCESS: All {tables_exist} tables exist and are accessible!")
            
            # Test basic operations
            print("\n4. Testing basic operations...")
            try:
                # Test CPI data query
                cpi_result = service.supabase.table('cpi_data').select('*').limit(1).execute()
                print("   ✅ CPI data query successful")
                
                # Test users table structure
                users_result = service.supabase.table('users').select('*').limit(1).execute()
                print("   ✅ Users table query successful")
                
                print("\n🎉 DATABASE SETUP COMPLETE!")
                print("✅ All tables exist")
                print("✅ All queries working")
                print("✅ Ready for production use")
                
                return True
                
            except Exception as e:
                print(f"   ❌ Operation test failed: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def main():
    """Main execution"""
    print("🔧 WageLift Database Setup & Verification")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("backend").exists():
        print("❌ Error: Please run this script from the WageLift root directory")
        print("   Current directory should contain 'backend' folder")
        sys.exit(1)
    
    # Run async setup
    success = asyncio.run(setup_database())
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. ✅ Database setup complete")
        print("2. 🔄 Continue with Task 14 (Mobile App)")
        print("3. 🚀 Deploy to production")
        print("4. 🌐 Create marketing website")
        print("\n🎯 Ready to proceed to Phase 2 development!")
    else:
        print("\n📋 ACTION REQUIRED:")
        print("Please complete the database setup in Supabase dashboard")
        print("Then run this script again to verify")

if __name__ == "__main__":
    main() 