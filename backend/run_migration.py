#!/usr/bin/env python3
"""
Migration runner for WageLift editor tables.
This script creates the necessary database tables for the editor functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.core.database import async_engine

async def run_migration():
    """Run the editor tables migration."""
    try:
        migration_file = Path(__file__).parent / "migrations" / "003_create_editor_tables.sql"
        
        if not migration_file.exists():
            print(f"Migration file not found: {migration_file}")
            return False
            
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("Starting migration: 003_create_editor_tables.sql")
        
        async with async_engine.begin() as conn:
            # Split by statements and execute each one
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement and not statement.startswith('--'):
                    try:
                        await conn.execute(text(statement))
                        print(f"Executed statement {i}/{len(statements)}")
                    except Exception as e:
                        print(f"Error executing statement {i}: {e}")
                        print(f"Statement: {statement[:100]}...")
                        raise
            
        print("✅ Migration 003_create_editor_tables.sql executed successfully!")
        print("📋 Created tables: raise_letters, raise_letter_versions, raise_letter_templates, raise_letter_shares")
        print("📝 Added default templates: Professional Standard, Confident Approach, Collaborative Tone")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

async def check_tables():
    """Check if the tables were created successfully."""
    try:
        async with async_engine.begin() as conn:
            # Check if tables exist
            tables_to_check = [
                'raise_letters',
                'raise_letter_versions', 
                'raise_letter_templates',
                'raise_letter_shares'
            ]
            
            for table in tables_to_check:
                result = await conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """))
                exists = result.scalar()
                status = "✅" if exists else "❌"
                print(f"{status} Table '{table}': {'exists' if exists else 'missing'}")
            
            # Check template count
            result = await conn.execute(text("SELECT COUNT(*) FROM raise_letter_templates WHERE is_public = true;"))
            template_count = result.scalar()
            print(f"📝 Public templates available: {template_count}")
            
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    print("🚀 WageLift Editor Tables Migration")
    print("=" * 50)
    
    # Run migration
    success = asyncio.run(run_migration())
    
    if success:
        print("\n🔍 Verifying migration results...")
        asyncio.run(check_tables())
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1) 