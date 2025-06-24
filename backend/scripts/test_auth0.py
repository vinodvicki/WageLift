#!/usr/bin/env python3
"""
Test script for Auth0 JWT validation and Redis caching
Run this after configuring Auth0 environment variables
"""
import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

# Add app directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

async def test_auth0_integration():
    """Test Auth0 JWT validation system"""
    print("🔐 Testing Auth0 JWT Integration")
    print("=" * 50)
    
    try:
        # Test imports
        print("✅ Testing imports...")
        from core.auth import Auth0User, verify_token, get_redis_client, cache_user, get_cached_user
        from core.config import settings
        print("   All imports successful")
        
        # Test configuration
        print("\n🔧 Testing configuration...")
        required_settings = ['AUTH0_DOMAIN', 'AUTH0_AUDIENCE', 'AUTH0_ALGORITHM']
        for setting in required_settings:
            value = getattr(settings, setting, None)
            if value:
                print(f"   ✅ {setting}: configured")
            else:
                print(f"   ❌ {setting}: not configured")
        
        # Test Redis connection
        print("\n📦 Testing Redis connection...")
        try:
            redis_client = get_redis_client()
            redis_client.ping()
            print("   ✅ Redis connection successful")
            
            # Test caching functionality
            test_data = {"test": "data", "timestamp": str(datetime.utcnow())}
            redis_client.setex("test_key", 60, json.dumps(test_data))
            retrieved = redis_client.get("test_key")
            
            if retrieved and json.loads(retrieved) == test_data:
                print("   ✅ Redis caching functional")
            else:
                print("   ❌ Redis caching failed")
                
            # Cleanup
            redis_client.delete("test_key")
            
        except Exception as e:
            print(f"   ❌ Redis connection failed: {e}")
        
        # Test Auth0User model
        print("\n👤 Testing Auth0User model...")
        try:
            test_user_data = {
                "sub": "auth0|test123456789",
                "email": "test@wagelift.com",
                "email_verified": True,
                "name": "Test User",
                "picture": "https://example.com/avatar.png",
                "aud": "your-api-audience",
                "iss": f"https://{settings.AUTH0_DOMAIN}/",
                "iat": int(datetime.utcnow().timestamp()),
                "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp())
            }
            
            user = Auth0User(**test_user_data)
            print(f"   ✅ Auth0User model validation successful")
            print(f"   📋 User ID: {user.sub}")
            print(f"   📧 Email: {user.email}")
            print(f"   ✅ Verified: {user.email_verified}")
            
        except Exception as e:
            print(f"   ❌ Auth0User model validation failed: {e}")
        
        # Test caching with Auth0User
        print("\n🔄 Testing user caching...")
        try:
            test_token = "test_token_123456789"
            await cache_user(test_token, user, ttl=60)
            
            cached_user = await get_cached_user(test_token)
            if cached_user and cached_user.sub == user.sub:
                print("   ✅ User caching functional")
            else:
                print("   ❌ User caching failed")
                
        except Exception as e:
            print(f"   ❌ User caching test failed: {e}")
        
        print("\n🎉 Auth0 integration test completed!")
        print("\nNext steps:")
        print("1. Configure Auth0 application in dashboard")
        print("2. Set environment variables (AUTH0_DOMAIN, AUTH0_AUDIENCE, etc.)")
        print("3. Test with real JWT tokens from Auth0")
        print("4. Run: uvicorn app.main:app --reload")
        print("5. Test endpoints: /api/v1/auth/auth-status")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install fastapi python-jose[cryptography] redis")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

async def test_jwt_structure():
    """Test JWT token structure understanding"""
    print("\n🔍 JWT Token Structure Reference")
    print("=" * 50)
    
    print("A valid Auth0 JWT should have these claims:")
    print("Required:")
    print("  - sub: Auth0 user ID (e.g., 'auth0|123456789')")
    print("  - email: User email address")
    print("  - email_verified: Boolean verification status")
    print("  - aud: API audience (configured in Auth0)")
    print("  - iss: Issuer (https://your-domain.auth0.com/)")
    print("  - exp: Expiration timestamp")
    print("  - iat: Issued at timestamp")
    
    print("\nOptional:")
    print("  - name: Full name")
    print("  - picture: Profile picture URL")
    print("  - nickname: Display name")
    print("  - updated_at: Last profile update")

if __name__ == "__main__":
    print("WageLift Auth0 Integration Test")
    print("=" * 50)
    
    asyncio.run(test_auth0_integration())
    asyncio.run(test_jwt_structure()) 