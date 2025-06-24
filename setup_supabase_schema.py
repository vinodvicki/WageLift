# -*- coding: utf-8 -*-
"""
Setup Supabase Database Schema
Applies the complete WageLift schema to Supabase
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
sys.path.insert(0, 'app')

async def setup_schema():
    try:
        from services.supabase_service import supabase_service
        print("🔧 SUPABASE SCHEMA SETUP")
        print("=" * 50)
        
        # Read the schema file
        print("1. Reading schema file...")
        with open('supabase-schema.sql', 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"   Found {len(statements)} SQL statements")
        
        # Apply each statement
        print("2. Applying schema...")
        success_count = 0
        
        for i, statement in enumerate(statements, 1):
            if not statement or statement.startswith('--'):
                continue
                
            try:
                # Use the Supabase client to execute raw SQL
                result = supabase_service.client.rpc('exec_sql', {'sql': statement}).execute()
                print(f"   ✅ Statement {i}/{len(statements)}: Success")
                success_count += 1
            except Exception as e:
                # Some statements might fail if tables already exist
                if "already exists" in str(e) or "duplicate" in str(e):
                    print(f"   ⚠️  Statement {i}/{len(statements)}: Already exists (skipped)")
                    success_count += 1
                else:
                    print(f"   ❌ Statement {i}/{len(statements)}: {e}")
        
        print(f"\n3. Schema setup complete: {success_count}/{len(statements)} statements applied")
        
        # Test the connection again
        print("4. Testing connection...")
        is_connected = await supabase_service.test_connection()
        if is_connected:
            print("   ✅ Supabase connection successful")
        else:
            print("   ❌ Supabase connection failed")
            
        print("\n🎉 Supabase schema setup completed!")
        
    except Exception as e:
        print(f"❌ Error during schema setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(setup_schema()) 