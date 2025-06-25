#!/usr/bin/env python3
"""
DEBUG Configuration and Environment Error Testing for WageLift
Shows detailed error messages for troubleshooting
"""

import asyncio
import json
import requests
import time
import os
import sys
import subprocess
import tempfile
from typing import List, Dict, Any, Optional
import importlib

class ConfigurationDebugTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        self.original_env = {}
        
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
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_environment_variable_handling(self):
        """Test 6.1: Missing and invalid environment variables"""
        try:
            env_errors = []
            
            print("\n🔍 DEBUGGING ENVIRONMENT VARIABLE HANDLING:")
            
            # Test 1: Required environment variables presence
            try:
                required_env_vars = [
                    "DEBUG",
                    "BACKEND_CORS_ORIGINS",
                    "SQLALCHEMY_DATABASE_URI",
                ]
                
                missing_vars = []
                for var in required_env_vars:
                    value = os.environ.get(var)
                    print(f"   {var}: {'✅ Present' if value else '❌ Missing'} = '{value}'")
                    if var not in os.environ:
                        missing_vars.append(var)
                
                if missing_vars:
                    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
                    env_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Environment variable check error: {str(e)}"
                env_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 2: Environment variable validation
            try:
                # Test DEBUG variable validation
                debug_value = os.environ.get("DEBUG", "").lower()
                valid_debug = debug_value in ["true", "false", "1", "0", ""]
                print(f"   DEBUG validation: {'✅ Valid' if valid_debug else '❌ Invalid'} = '{debug_value}'")
                if not valid_debug:
                    error_msg = f"Invalid DEBUG value: {debug_value}"
                    env_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                
                # Test CORS origins format
                cors_origins = os.environ.get("BACKEND_CORS_ORIGINS", "")
                valid_cors = cors_origins and (cors_origins.startswith("[") or "http" in cors_origins)
                print(f"   CORS validation: {'✅ Valid' if valid_cors else '❌ Invalid'} = '{cors_origins}'")
                if cors_origins and not valid_cors:
                    error_msg = f"Invalid CORS origins format: {cors_origins}"
                    env_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Environment validation error: {str(e)}"
                env_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 3: Graceful handling of missing optional variables
            try:
                # Test optional variables with defaults
                optional_vars = {
                    "OPENAI_API_KEY": "Optional AI service key",
                    "BLS_API_KEY": "Optional BLS service key",
                    "AUTH0_CLIENT_SECRET": "Optional auth service",
                    "SENTRY_DSN": "Optional monitoring",
                }
                
                print(f"   Optional variables check:")
                for var, description in optional_vars.items():
                    value = os.environ.get(var)
                    print(f"     {var}: {'✅ Set' if value else '⚪ Empty'} = '{value}'")
                        
            except Exception as e:
                error_msg = f"Optional environment variable handling error: {str(e)}"
                env_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 4: Environment variable type conversion
            try:
                # Test numeric environment variables
                numeric_vars = {
                    "PORT": (8000, int),
                    "RATE_LIMIT_PER_MINUTE": (60, int),
                    "MAX_FILE_SIZE": (5242880, int),  # 5MB
                }
                
                print(f"   Numeric variables check:")
                for var, (default_value, expected_type) in numeric_vars.items():
                    env_value = os.environ.get(var, str(default_value))
                    try:
                        converted_value = expected_type(env_value)
                        valid_value = converted_value >= 0
                        print(f"     {var}: {'✅ Valid' if valid_value else '❌ Invalid'} = {converted_value}")
                        if converted_value < 0:
                            error_msg = f"Negative value for {var}: {converted_value}"
                            env_errors.append(error_msg)
                            print(f"     ❌ ERROR: {error_msg}")
                    except ValueError as ve:
                        error_msg = f"Invalid {expected_type.__name__} value for {var}: {env_value}"
                        env_errors.append(error_msg)
                        print(f"     ❌ ERROR: {error_msg}")
                        
            except Exception as e:
                error_msg = f"Type conversion error: {str(e)}"
                env_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 5: Sensitive data handling
            try:
                sensitive_vars = [
                    "SECRET_KEY",
                    "POSTGRES_PASSWORD",
                    "AUTH0_CLIENT_SECRET",
                    "OPENAI_API_KEY"
                ]
                
                print(f"   Sensitive variables check:")
                for var in sensitive_vars:
                    value = os.environ.get(var, "")
                    length_ok = not value or len(value) >= 8
                    print(f"     {var}: {'✅ Valid length' if length_ok else '❌ Too short'} = {len(value)} chars")
                    if value and len(value) < 8:
                        error_msg = f"Suspiciously short {var}: {len(value)} characters"
                        env_errors.append(error_msg)
                        print(f"     ❌ ERROR: {error_msg}")
                        
            except Exception as e:
                error_msg = f"Sensitive data validation error: {str(e)}"
                env_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Evaluate results
            if len(env_errors) == 0:
                self.log_test("Environment Variable Handling", "PASS", "All environment variables handled correctly")
            else:
                self.log_test("Environment Variable Handling", "FAIL", f"Environment errors: {len(env_errors)}")
                for error in env_errors:
                    print(f"     🔴 {error}")
                
        except Exception as e:
            self.log_test("Environment Variable Handling", "FAIL", f"Test error: {str(e)}")
    
    def test_database_schema_validation(self):
        """Test 6.3: Database schema and configuration validation"""
        try:
            db_errors = []
            
            print("\n🔍 DEBUGGING DATABASE SCHEMA VALIDATION:")
            
            # Test 1: Database connection string validation
            try:
                db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI", "")
                print(f"   Database URI: '{db_uri}'")
                
                if not db_uri:
                    error_msg = "Database URI not configured"
                    db_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                elif db_uri.startswith("sqlite://"):
                    # SQLite validation
                    has_wagelift = "wagelift" in db_uri.lower()
                    print(f"   SQLite validation: {'✅ Contains wagelift' if has_wagelift else '❌ Missing wagelift'}")
                    if not has_wagelift:
                        error_msg = "SQLite database name should contain 'wagelift'"
                        db_errors.append(error_msg)
                        print(f"   ❌ ERROR: {error_msg}")
                elif db_uri.startswith("postgresql://"):
                    # PostgreSQL validation
                    has_credentials = "@" in db_uri and ":" in db_uri
                    print(f"   PostgreSQL validation: {'✅ Has credentials' if has_credentials else '❌ Missing credentials'}")
                    if not has_credentials:
                        error_msg = "PostgreSQL URI missing credentials or host"
                        db_errors.append(error_msg)
                        print(f"   ❌ ERROR: {error_msg}")
                else:
                    error_msg = f"Unsupported database type in URI: {db_uri}"
                    db_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Database URI validation error: {str(e)}"
                db_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 2: Database connectivity test
            try:
                print(f"   Testing health endpoint: {self.base_url}/health")
                response = self.session.get(f"{self.base_url}/health", timeout=10)
                print(f"   Health response status: {response.status_code}")
                
                if response.status_code in [200, 429]:  # 429 acceptable due to rate limiting
                    try:
                        health_data = response.json()
                        print(f"   Health data: {health_data}")
                        if "status" not in health_data or health_data["status"] != "healthy":
                            error_msg = "Health check indicates database connectivity issues"
                            db_errors.append(error_msg)
                            print(f"   ❌ ERROR: {error_msg}")
                        else:
                            print(f"   ✅ Health check passed")
                    except json.JSONDecodeError as jde:
                        error_msg = "Health check returned invalid JSON"
                        db_errors.append(error_msg)
                        print(f"   ❌ ERROR: {error_msg}")
                        print(f"   Response text: {response.text}")
                else:
                    error_msg = f"Health check failed with status {response.status_code}"
                    db_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    print(f"   Response text: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Health check connection error: {str(e)}"
                db_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            except Exception as e:
                error_msg = f"Health check error: {str(e)}"
                db_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 3: Database file permissions (for SQLite)
            try:
                db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI", "")
                if db_uri.startswith("sqlite://"):
                    # Extract database file path
                    db_path = db_uri.replace("sqlite:///", "").replace("sqlite://", "")
                    print(f"   Database file path: {db_path}")
                    
                    if os.path.exists(db_path):
                        readable = os.access(db_path, os.R_OK)
                        writable = os.access(db_path, os.W_OK)
                        print(f"   File permissions: readable={'✅' if readable else '❌'}, writable={'✅' if writable else '❌'}")
                        
                        if not readable:
                            error_msg = f"Database file not readable: {db_path}"
                            db_errors.append(error_msg)
                            print(f"   ❌ ERROR: {error_msg}")
                        if not writable:
                            error_msg = f"Database file not writable: {db_path}"
                            db_errors.append(error_msg)
                            print(f"   ❌ ERROR: {error_msg}")
                    else:
                        # File doesn't exist yet - check directory permissions
                        db_dir = os.path.dirname(db_path) or "."
                        dir_writable = os.access(db_dir, os.W_OK)
                        print(f"   Directory permissions: {db_dir} writable={'✅' if dir_writable else '❌'}")
                        if not dir_writable:
                            error_msg = f"Cannot create database file in directory: {db_dir}"
                            db_errors.append(error_msg)
                            print(f"   ❌ ERROR: {error_msg}")
                            
            except Exception as e:
                error_msg = f"Database file permission check error: {str(e)}"
                db_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Evaluate results
            if len(db_errors) == 0:
                self.log_test("Database Schema Validation", "PASS", "Database configuration valid")
            else:
                self.log_test("Database Schema Validation", "FAIL", f"Database errors: {len(db_errors)}")
                for error in db_errors:
                    print(f"     🔴 {error}")
                
        except Exception as e:
            self.log_test("Database Schema Validation", "FAIL", f"Test error: {str(e)}")
    
    def test_configuration_consistency(self):
        """Test 6.4: Configuration consistency and environment mismatch detection"""
        try:
            config_errors = []
            
            print("\n🔍 DEBUGGING CONFIGURATION CONSISTENCY:")
            
            # Test 1: Development vs Production configuration consistency
            try:
                debug_mode = os.environ.get("DEBUG", "false").lower() in ["true", "1"]
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                print(f"   DEBUG mode: {debug_mode}, ENVIRONMENT: {environment}")
                
                # Check for mismatched configurations
                if debug_mode and environment == "production":
                    error_msg = "DEBUG enabled in production environment"
                    config_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                
                if not debug_mode and environment == "development":
                    error_msg = "DEBUG disabled in development environment"
                    config_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    
                # Check secret key configuration
                secret_key = os.environ.get("SECRET_KEY", "")
                has_dev_in_key = "dev" in secret_key.lower()
                print(f"   SECRET_KEY has 'dev': {has_dev_in_key}, environment: {environment}")
                if environment == "production" and has_dev_in_key:
                    error_msg = "Development secret key used in production"
                    config_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Environment consistency check error: {str(e)}"
                config_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 2: CORS configuration consistency
            try:
                cors_origins = os.environ.get("BACKEND_CORS_ORIGINS", "")
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                has_localhost = "localhost" in cors_origins
                print(f"   CORS has localhost: {has_localhost}, environment: {environment}")
                
                if environment == "production":
                    if has_localhost:
                        error_msg = "localhost CORS origins in production"
                        config_errors.append(error_msg)
                        print(f"   ❌ ERROR: {error_msg}")
                elif environment == "development":
                    if cors_origins and not has_localhost:
                        error_msg = "No localhost CORS origins in development"
                        config_errors.append(error_msg)
                        print(f"   ❌ ERROR: {error_msg}")
                        
            except Exception as e:
                error_msg = f"CORS configuration check error: {str(e)}"
                config_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 3: Database configuration consistency
            try:
                db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI", "")
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                is_sqlite = "sqlite" in db_uri
                print(f"   Database is SQLite: {is_sqlite}, environment: {environment}")
                
                if environment == "production" and is_sqlite:
                    error_msg = "SQLite database used in production (consider PostgreSQL)"
                    config_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Database configuration check error: {str(e)}"
                config_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 4: Security configuration consistency
            try:
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                rate_limit = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
                print(f"   Rate limit: {rate_limit}, environment: {environment}")
                
                if environment == "production" and rate_limit > 1000:
                    error_msg = f"Very high rate limit in production: {rate_limit}"
                    config_errors.append(error_msg)
                    print(f"   ❌ ERROR: {error_msg}")
                    
            except Exception as e:
                error_msg = f"Security configuration check error: {str(e)}"
                config_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Test 5: API key configuration validation
            try:
                api_keys = {
                    "OPENAI_API_KEY": "sk-",  # OpenAI keys start with sk-
                    "BLS_API_KEY": "",       # BLS keys have specific format
                    "AUTH0_CLIENT_SECRET": "",  # Auth0 secrets have specific format
                }
                
                print(f"   API key validation:")
                for key_name, expected_prefix in api_keys.items():
                    key_value = os.environ.get(key_name, "")
                    if key_value:
                        prefix_ok = not expected_prefix or key_value.startswith(expected_prefix)
                        length_ok = len(key_value) >= 16
                        print(f"     {key_name}: prefix={'✅' if prefix_ok else '❌'}, length={'✅' if length_ok else '❌'} ({len(key_value)} chars)")
                        
                        if expected_prefix and not prefix_ok:
                            error_msg = f"Invalid format for {key_name}"
                            config_errors.append(error_msg)
                            print(f"     ❌ ERROR: {error_msg}")
                        if not length_ok:
                            error_msg = f"Suspiciously short {key_name}"
                            config_errors.append(error_msg)
                            print(f"     ❌ ERROR: {error_msg}")
                    else:
                        print(f"     {key_name}: ⚪ Empty")
                            
            except Exception as e:
                error_msg = f"API key validation error: {str(e)}"
                config_errors.append(error_msg)
                print(f"   ❌ ERROR: {error_msg}")
            
            # Evaluate results
            if len(config_errors) == 0:
                self.log_test("Configuration Consistency", "PASS", "All configurations consistent")
            else:
                self.log_test("Configuration Consistency", "FAIL", f"Configuration errors: {len(config_errors)}")
                for error in config_errors:
                    print(f"     🔴 {error}")
                
        except Exception as e:
            self.log_test("Configuration Consistency", "FAIL", f"Test error: {str(e)}")
    
    def run_debug_tests(self):
        """Run debug configuration tests"""
        print("🔍 WAGELIFT CONFIGURATION DEBUG TESTING")
        print("=" * 60)
        
        tests = [
            self.test_environment_variable_handling,
            self.test_database_schema_validation,
            self.test_configuration_consistency
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 DEBUG CONFIGURATION TESTING SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = ConfigurationDebugTester()
    success = tester.run_debug_tests()
    sys.exit(0 if success else 1)