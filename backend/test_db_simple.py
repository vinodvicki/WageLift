#!/usr/bin/env python3
"""
Simple Database Connection Test
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

print('🗄️  Testing Database Connection...')

# Get connection details
host = os.getenv('POSTGRES_SERVER')
user = os.getenv('POSTGRES_USER') 
password = os.getenv('POSTGRES_PASSWORD')
database = os.getenv('POSTGRES_DB')
port = os.getenv('POSTGRES_PORT', '5432')

print(f'Host: {host}')
print(f'Database: {database}')
print(f'User: {user}')
print(f'Port: {port}')

try:
    # Try connection
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        connect_timeout=10
    )
    
    cursor = conn.cursor()
    cursor.execute('SELECT version()')
    version = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    print(f'✅ Database Connection: SUCCESS')
    print(f'PostgreSQL Version: {version[0][:60]}...')
    
except Exception as e:
    print(f'❌ Database Connection Error: {e}')
    print(f'Error Type: {type(e).__name__}') 