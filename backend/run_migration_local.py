#!/usr/bin/env python3
"""
Local migration runner for WageLift editor tables.
This script creates the necessary database tables for the editor functionality using local PostgreSQL.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text

# Local PostgreSQL connection settings
DATABASE_URL = "postgresql://wagelift:wagelift_password_2024@localhost:5432/wagelift"

def run_migration():
    """Run the editor tables migration using local PostgreSQL."""
    try:
        # Create engine with local database URL
        engine = create_engine(DATABASE_URL, echo=False)  # Disable echo for cleaner output
        
        migration_file = Path(__file__).parent / "migrations" / "003_create_editor_tables.sql"
        
        if not migration_file.exists():
            print(f"Migration file not found: {migration_file}")
            return False
            
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        print("Starting migration: 003_create_editor_tables.sql")
        print(f"Connecting to: postgresql://wagelift:***@localhost:5432/wagelift")
        
        with engine.begin() as conn:
            # Execute the entire migration as a single transaction
            # This ensures proper order of table creation before indexes
            try:
                conn.execute(text(migration_sql))
                print("✅ Migration executed successfully!")
            except Exception as e:
                print(f"❌ Error executing migration: {e}")
                raise
            
        print("✅ Migration 003_create_editor_tables.sql executed successfully!")
        print("📋 Created tables: raise_letters, raise_letter_versions, raise_letter_templates, raise_letter_shares")
        print("📝 Added default templates: Professional Standard, Confident Approach, Collaborative Tone")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def check_tables():
    """Check if the tables were created successfully."""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.begin() as conn:
            # Check if tables exist
            tables_to_check = [
                'raise_letters',
                'raise_letter_versions', 
                'raise_letter_templates',
                'raise_letter_shares'
            ]
            
            print("Checking created tables:")
            for table in tables_to_check:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """))
                exists = result.scalar()
                status = "✅" if exists else "❌"
                print(f"  {status} Table '{table}': {'exists' if exists else 'missing'}")
            
            # Check template count
            result = conn.execute(text("SELECT COUNT(*) FROM raise_letter_templates WHERE is_public = true;"))
            template_count = result.scalar()
            print(f"  📝 Public templates available: {template_count}")
            
            # Check indexes
            print("\nChecking indexes:")
            index_check_query = """
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename IN ('raise_letters', 'raise_letter_versions', 'raise_letter_templates', 'raise_letter_shares')
                ORDER BY tablename, indexname;
            """
            result = conn.execute(text(index_check_query))
            indexes = result.fetchall()
            print(f"  📊 Created {len(indexes)} indexes")
            
            # Check triggers
            print("\nChecking triggers:")
            trigger_check_query = """
                SELECT trigger_name, event_object_table 
                FROM information_schema.triggers 
                WHERE event_object_table IN ('raise_letters', 'raise_letter_templates');
            """
            result = conn.execute(text(trigger_check_query))
            triggers = result.fetchall()
            print(f"  ⚡ Created {len(triggers)} triggers")
            
    except Exception as e:
        print(f"Error checking tables: {e}")

if __name__ == "__main__":
    print("🚀 WageLift Editor Tables Migration (Local PostgreSQL)")
    print("=" * 65)
    
    # Run migration
    success = run_migration()
    
    if success:
        print("\n🔍 Verifying migration results...")
        check_tables()
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("1. Update backend/app/main.py to include the editor router")
        print("2. Test the editor API endpoints")
        print("3. Integrate with the frontend editor component")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1) 