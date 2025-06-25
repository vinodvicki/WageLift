#!/usr/bin/env python3
"""
FIXED Configuration and Environment Error Testing for WageLift
Tests for missing environment variables, version conflicts, and configuration mismatches
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

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

try:
    import pkg_resources
    from packaging import version as pkg_version
except ImportError:
    print("Warning: pkg_resources not available, skipping version checks")
    pkg_resources = None
    pkg_version = None

class ConfigurationEnvironmentTester:
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
        print(f"{icon} {test_name}: {status} {details}")
    
    def test_environment_variable_handling(self):
        """Test 6.1: Missing and invalid environment variables"""
        try:
            env_errors = []
            
            # Test 1: Required environment variables presence
            try:
                required_env_vars = [
                    "DEBUG",
                    "BACKEND_CORS_ORIGINS",
                    "SQLALCHEMY_DATABASE_URI",
                ]
                
                missing_vars = []
                for var in required_env_vars:
                    if var not in os.environ:
                        missing_vars.append(var)
                
                if missing_vars:
                    env_errors.append(f"Missing required environment variables: {', '.join(missing_vars)}")
                    
            except Exception as e:
                env_errors.append(f"Environment variable check error: {str(e)}")
            
            # Test 2: Environment variable validation
            try:
                # Test DEBUG variable validation
                debug_value = os.environ.get("DEBUG", "").lower()
                if debug_value not in ["true", "false", "1", "0", ""]:
                    env_errors.append(f"Invalid DEBUG value: {debug_value}")
                
                # Test CORS origins format
                cors_origins = os.environ.get("BACKEND_CORS_ORIGINS", "")
                if cors_origins and not (cors_origins.startswith("[") or "http" in cors_origins):
                    env_errors.append(f"Invalid CORS origins format: {cors_origins}")
                    
            except Exception as e:
                env_errors.append(f"Environment validation error: {str(e)}")
            
            # Test 3: Graceful handling of missing optional variables
            try:
                # Test optional variables with defaults
                optional_vars = {
                    "OPENAI_API_KEY": "Optional AI service key",
                    "BLS_API_KEY": "Optional BLS service key",
                    "AUTH0_CLIENT_SECRET": "Optional auth service",
                    "SENTRY_DSN": "Optional monitoring",
                }
                
                for var, description in optional_vars.items():
                    value = os.environ.get(var)
                    if value is None:
                        # This is expected and should be handled gracefully
                        pass
                    elif value == "":
                        # Empty values should also be handled gracefully
                        pass
                        
            except Exception as e:
                env_errors.append(f"Optional environment variable handling error: {str(e)}")
            
            # Test 4: Environment variable type conversion
            try:
                # Test numeric environment variables
                numeric_vars = {
                    "PORT": (8000, int),
                    "RATE_LIMIT_PER_MINUTE": (60, int),
                    "MAX_FILE_SIZE": (5242880, int),  # 5MB
                }
                
                for var, (default_value, expected_type) in numeric_vars.items():
                    env_value = os.environ.get(var, str(default_value))
                    try:
                        converted_value = expected_type(env_value)
                        if converted_value < 0:
                            env_errors.append(f"Negative value for {var}: {converted_value}")
                    except ValueError:
                        env_errors.append(f"Invalid {expected_type.__name__} value for {var}: {env_value}")
                        
            except Exception as e:
                env_errors.append(f"Type conversion error: {str(e)}")
            
            # Test 5: Sensitive data handling
            try:
                sensitive_vars = [
                    "SECRET_KEY",
                    "POSTGRES_PASSWORD",
                    "AUTH0_CLIENT_SECRET",
                    "OPENAI_API_KEY"
                ]
                
                for var in sensitive_vars:
                    value = os.environ.get(var, "")
                    if value and len(value) < 8:
                        env_errors.append(f"Suspiciously short {var}: {len(value)} characters")
                        
            except Exception as e:
                env_errors.append(f"Sensitive data validation error: {str(e)}")
            
            # Evaluate results
            if len(env_errors) == 0:
                self.log_test("Environment Variable Handling", "PASS", "All environment variables handled correctly")
            else:
                self.log_test("Environment Variable Handling", "FAIL", f"Environment errors: {len(env_errors)}")
                
        except Exception as e:
            self.log_test("Environment Variable Handling", "FAIL", f"Test error: {str(e)}")
    
    def test_version_compatibility(self):
        """Test 6.2: Library version compatibility and conflicts"""
        try:
            version_errors = []
            
            # Test 1: Python version compatibility
            try:
                python_version = sys.version_info
                min_python = (3, 8)  # Minimum supported Python version
                
                if python_version < min_python:
                    version_errors.append(f"Python version too old: {python_version} < {min_python}")
                elif python_version >= (3, 14):  # Future versions might have issues
                    version_errors.append(f"Python version too new (untested): {python_version}")
                    
            except Exception as e:
                version_errors.append(f"Python version check error: {str(e)}")
            
            # Test 2: Critical package version compatibility
            if pkg_resources and pkg_version:
                try:
                    critical_packages = {
                        "fastapi": ("0.95.0", "2.0.0"),  # Updated max version
                        "uvicorn": ("0.20.0", "1.0.0"),
                        "pydantic": ("2.0.0", "3.0.0"),
                        "requests": ("2.25.0", "3.0.0"),
                    }
                    
                    for package_name, (min_version, max_version) in critical_packages.items():
                        try:
                            # Get installed version
                            installed_version = pkg_resources.get_distribution(package_name).version
                            
                            # Compare versions
                            if pkg_version.parse(installed_version) < pkg_version.parse(min_version):
                                version_errors.append(f"{package_name} version too old: {installed_version} < {min_version}")
                            elif pkg_version.parse(installed_version) >= pkg_version.parse(max_version):
                                version_errors.append(f"{package_name} version too new: {installed_version} >= {max_version}")
                                
                        except pkg_resources.DistributionNotFound:
                            version_errors.append(f"Required package not found: {package_name}")
                        except Exception as e:
                            version_errors.append(f"Version check error for {package_name}: {str(e)}")
                            
                except Exception as e:
                    version_errors.append(f"Package version check error: {str(e)}")
            
            # Test 3: Import compatibility
            try:
                # Test critical imports
                critical_imports = [
                    "fastapi",
                    "uvicorn", 
                    "pydantic",
                    "requests",
                    "sqlalchemy",
                    "psutil"
                ]
                
                for module_name in critical_imports:
                    try:
                        importlib.import_module(module_name)
                    except ImportError as e:
                        version_errors.append(f"Import error for {module_name}: {str(e)}")
                    except Exception as e:
                        version_errors.append(f"Unexpected import error for {module_name}: {str(e)}")
                        
            except Exception as e:
                version_errors.append(f"Import compatibility test error: {str(e)}")
            
            # Test 4: Dependency conflicts
            if pkg_resources and pkg_version:
                try:
                    # Check for known problematic combinations
                    try:
                        pydantic_version = pkg_resources.get_distribution("pydantic").version
                        fastapi_version = pkg_resources.get_distribution("fastapi").version
                        
                        # Pydantic v2 requires FastAPI 0.100+
                        if (pkg_version.parse(pydantic_version) >= pkg_version.parse("2.0.0") and
                            pkg_version.parse(fastapi_version) < pkg_version.parse("0.100.0")):
                            version_errors.append(f"Incompatible versions: Pydantic {pydantic_version} with FastAPI {fastapi_version}")
                            
                    except pkg_resources.DistributionNotFound:
                        # Skip if packages not found
                        pass
                        
                except Exception as e:
                    version_errors.append(f"Dependency conflict check error: {str(e)}")
            
            # Evaluate results
            if len(version_errors) == 0:
                self.log_test("Version Compatibility", "PASS", "All versions compatible")
            else:
                self.log_test("Version Compatibility", "FAIL", f"Version errors: {len(version_errors)}")
                
        except Exception as e:
            self.log_test("Version Compatibility", "FAIL", f"Test error: {str(e)}")
    
    def test_database_schema_validation(self):
        """Test 6.3: Database schema and configuration validation"""
        try:
            db_errors = []
            
            # Test 1: Database connection string validation
            try:
                db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI", "")
                
                if not db_uri:
                    db_errors.append("Database URI not configured")
                elif db_uri.startswith("sqlite://"):
                    # SQLite validation
                    if "wagelift" not in db_uri.lower():
                        db_errors.append("SQLite database name should contain 'wagelift'")
                elif db_uri.startswith("postgresql://"):
                    # PostgreSQL validation
                    if "@" not in db_uri or ":" not in db_uri:
                        db_errors.append("PostgreSQL URI missing credentials or host")
                else:
                    db_errors.append(f"Unsupported database type in URI: {db_uri}")
                    
            except Exception as e:
                db_errors.append(f"Database URI validation error: {str(e)}")
            
            # Test 2: Database connectivity test
            try:
                # Test actual database connection with retry
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = self.session.get(f"{self.base_url}/health", timeout=10)
                        if response.status_code in [200, 429]:  # 429 acceptable due to rate limiting
                            health_data = response.json()
                            if "status" not in health_data or health_data["status"] != "healthy":
                                db_errors.append("Health check indicates database connectivity issues")
                            break
                        else:
                            if attempt == max_retries - 1:  # Last attempt
                                db_errors.append(f"Health check failed with status {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        if attempt == max_retries - 1:  # Last attempt
                            db_errors.append(f"Health check connection error: {str(e)}")
                        else:
                            time.sleep(2)  # Wait before retry
                    except json.JSONDecodeError:
                        if attempt == max_retries - 1:
                            db_errors.append("Health check returned invalid JSON")
                    except Exception as e:
                        if attempt == max_retries - 1:
                            db_errors.append(f"Health check error: {str(e)}")
                        
            except Exception as e:
                db_errors.append(f"Database connectivity test error: {str(e)}")
            
            # Test 3: Database file permissions (for SQLite)
            try:
                db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI", "")
                if db_uri.startswith("sqlite://"):
                    # Extract database file path
                    db_path = db_uri.replace("sqlite:///", "").replace("sqlite://", "")
                    
                    if os.path.exists(db_path):
                        # Check file permissions
                        if not os.access(db_path, os.R_OK):
                            db_errors.append(f"Database file not readable: {db_path}")
                        if not os.access(db_path, os.W_OK):
                            db_errors.append(f"Database file not writable: {db_path}")
                    else:
                        # File doesn't exist yet - check directory permissions
                        db_dir = os.path.dirname(db_path) or "."
                        if not os.access(db_dir, os.W_OK):
                            db_errors.append(f"Cannot create database file in directory: {db_dir}")
                            
            except Exception as e:
                db_errors.append(f"Database file permission check error: {str(e)}")
            
            # Evaluate results
            if len(db_errors) == 0:
                self.log_test("Database Schema Validation", "PASS", "Database configuration valid")
            else:
                self.log_test("Database Schema Validation", "FAIL", f"Database errors: {len(db_errors)}")
                
        except Exception as e:
            self.log_test("Database Schema Validation", "FAIL", f"Test error: {str(e)}")
    
    def test_configuration_consistency(self):
        """Test 6.4: Configuration consistency and environment mismatch detection"""
        try:
            config_errors = []
            
            # Test 1: Development vs Production configuration consistency
            try:
                debug_mode = os.environ.get("DEBUG", "false").lower() in ["true", "1"]
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                
                # Check for mismatched configurations
                if debug_mode and environment == "production":
                    config_errors.append("DEBUG enabled in production environment")
                
                if not debug_mode and environment == "development":
                    config_errors.append("DEBUG disabled in development environment")
                    
                # Check secret key configuration
                secret_key = os.environ.get("SECRET_KEY", "")
                if environment == "production" and "dev" in secret_key.lower():
                    config_errors.append("Development secret key used in production")
                    
            except Exception as e:
                config_errors.append(f"Environment consistency check error: {str(e)}")
            
            # Test 2: CORS configuration consistency
            try:
                cors_origins = os.environ.get("BACKEND_CORS_ORIGINS", "")
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                
                if environment == "production":
                    if "localhost" in cors_origins:
                        config_errors.append("localhost CORS origins in production")
                elif environment == "development":
                    if cors_origins and "localhost" not in cors_origins:
                        config_errors.append("No localhost CORS origins in development")
                        
            except Exception as e:
                config_errors.append(f"CORS configuration check error: {str(e)}")
            
            # Test 3: Database configuration consistency
            try:
                db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI", "")
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                
                if environment == "production" and "sqlite" in db_uri:
                    config_errors.append("SQLite database used in production (consider PostgreSQL)")
                    
                if environment == "development" and "postgresql" in db_uri:
                    # This is acceptable but worth noting
                    pass
                    
            except Exception as e:
                config_errors.append(f"Database configuration check error: {str(e)}")
            
            # Test 4: Security configuration consistency
            try:
                environment = os.environ.get("ENVIRONMENT", "development").lower()
                
                # Check SSL/HTTPS configuration
                if environment == "production":
                    # In production, should have proper SSL configuration
                    # This would be checked through the actual deployment
                    pass
                    
                # Check rate limiting configuration
                rate_limit = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
                if environment == "production" and rate_limit > 1000:
                    config_errors.append(f"Very high rate limit in production: {rate_limit}")
                    
            except Exception as e:
                config_errors.append(f"Security configuration check error: {str(e)}")
            
            # Test 5: API key configuration validation
            try:
                api_keys = {
                    "OPENAI_API_KEY": "sk-",  # OpenAI keys start with sk-
                    "BLS_API_KEY": "",       # BLS keys have specific format
                    "AUTH0_CLIENT_SECRET": "",  # Auth0 secrets have specific format
                }
                
                for key_name, expected_prefix in api_keys.items():
                    key_value = os.environ.get(key_name, "")
                    if key_value:
                        if expected_prefix and not key_value.startswith(expected_prefix):
                            config_errors.append(f"Invalid format for {key_name}")
                        if len(key_value) < 16:  # Most API keys are longer
                            config_errors.append(f"Suspiciously short {key_name}")
                            
            except Exception as e:
                config_errors.append(f"API key validation error: {str(e)}")
            
            # Evaluate results
            if len(config_errors) == 0:
                self.log_test("Configuration Consistency", "PASS", "All configurations consistent")
            else:
                self.log_test("Configuration Consistency", "FAIL", f"Configuration errors: {len(config_errors)}")
                
        except Exception as e:
            self.log_test("Configuration Consistency", "FAIL", f"Test error: {str(e)}")
    
    def run_all_tests(self):
        """Run all configuration and environment error tests"""
        print("⚙️ WAGELIFT CONFIGURATION & ENVIRONMENT ERROR TESTING (FIXED)")
        print("=" * 60)
        print()
        
        tests = [
            self.test_environment_variable_handling,
            self.test_version_compatibility,
            self.test_database_schema_validation,
            self.test_configuration_consistency
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 CONFIGURATION & ENVIRONMENT ERROR TESTING SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        if failed == 0:
            print("✅ ALL CONFIGURATION & ENVIRONMENT TESTS PASSED")
        else:
            print("❌ SOME CONFIGURATION & ENVIRONMENT TESTS FAILED")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = ConfigurationEnvironmentTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)