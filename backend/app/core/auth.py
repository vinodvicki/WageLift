"""
Auth0 JWT validation with Redis caching and performance monitoring for FastAPI
"""
import json
import httpx
import redis
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import lru_cache

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr
from structlog import get_logger

from .config import settings
from .metrics import (
    track_auth_operation, 
    track_cache_operation,
    AUTH0_API_CALLS, 
    AUTH0_API_LATENCY,
    JWT_VALIDATION_DURATION,
    JWT_CACHE_HITS,
    JWT_CACHE_MISSES,
    AUTH_REQUESTS_TOTAL,
    AUTH_SUCCESS_TOTAL,
    AUTH_FAILURE_TOTAL,
    record_user_action
)

logger = get_logger(__name__)
security = HTTPBearer()

class Auth0User(BaseModel):
    """Auth0 user model with required fields"""
    sub: str  # Auth0 user ID
    email: EmailStr
    email_verified: bool
    name: Optional[str] = None
    picture: Optional[str] = None
    nickname: Optional[str] = None
    updated_at: Optional[str] = None
    aud: Optional[str] = None
    iss: Optional[str] = None
    iat: Optional[int] = None
    exp: Optional[int] = None

@lru_cache()
def get_redis_client() -> redis.Redis:
    """Get Redis client with connection pooling"""
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=getattr(settings, 'REDIS_PASSWORD', None),
        db=0,
        decode_responses=True,
        socket_connect_timeout=5
    )

async def verify_token(token: str) -> Auth0User:
    """Verify JWT token with Auth0 JWKS validation and performance monitoring"""
    start_time = time.time()
    
    try:
        # Track JWT validation start
        AUTH_REQUESTS_TOTAL.labels(method="jwt_validation", status="started").inc()
        
        # Get JWKS from Auth0 with monitoring
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        
        jwks_start = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url, timeout=10.0)
            response.raise_for_status()
            jwks = response.json()
        
        # Record Auth0 API metrics
        jwks_duration = time.time() - jwks_start
        AUTH0_API_LATENCY.labels(endpoint="jwks").observe(jwks_duration)
        AUTH0_API_CALLS.labels(endpoint="jwks", status="success").inc()
        
        # Get token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            AUTH_FAILURE_TOTAL.labels(reason="missing_kid", method="jwt_validation").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID"
            )
        
        # Find the correct key
        key = None
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid:
                key = jwk
                break
                
        if not key:
            AUTH_FAILURE_TOTAL.labels(reason="key_not_found", method="jwt_validation").inc()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key"
            )
        
        # Verify token with timing
        jwt_start = time.time()
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.AUTH0_ALGORITHM],
            audience=settings.AUTH0_AUDIENCE,
            issuer=f"https://{settings.AUTH0_DOMAIN}/"
        )
        
        # Record JWT validation metrics
        jwt_duration = time.time() - jwt_start
        total_duration = time.time() - start_time
        
        JWT_VALIDATION_DURATION.labels(validation_type="full").observe(jwt_duration)
        JWT_VALIDATION_DURATION.labels(validation_type="total").observe(total_duration)
        
        AUTH_SUCCESS_TOTAL.labels(user_type="authenticated").inc()
        AUTH_REQUESTS_TOTAL.labels(method="jwt_validation", status="success").inc()
        
        # Record user action
        record_user_action("token_validation", payload.get("sub"))
        
        logger.info("Token verified", user_id=payload.get("sub"), duration=total_duration)
        return Auth0User(**payload)
        
    except JWTError as e:
        total_duration = time.time() - start_time
        JWT_VALIDATION_DURATION.labels(validation_type="total").observe(total_duration)
        AUTH_FAILURE_TOTAL.labels(reason="jwt_error", method="jwt_validation").inc()
        AUTH_REQUESTS_TOTAL.labels(method="jwt_validation", status="error").inc()
        
        logger.warning("JWT validation failed", error=str(e), duration=total_duration)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        total_duration = time.time() - start_time
        JWT_VALIDATION_DURATION.labels(validation_type="total").observe(total_duration)
        AUTH_FAILURE_TOTAL.labels(reason=e.__class__.__name__, method="jwt_validation").inc()
        AUTH_REQUESTS_TOTAL.labels(method="jwt_validation", status="error").inc()
        
        logger.error("Unexpected error in token verification", error=str(e), duration=total_duration)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

async def get_cached_user(token: str) -> Optional[Auth0User]:
    """Get user from Redis cache with metrics tracking"""
    try:
        redis_client = get_redis_client()
        cache_key = f"auth:user:{token[-20:]}"
        
        cached_data = redis_client.get(cache_key)
        if cached_data:
            user_data = json.loads(cached_data)
            
            # Record cache hit
            JWT_CACHE_HITS.labels(cache_type="user_cache").inc()
            record_user_action("cache_hit")
            
            logger.debug("Cache hit", cache_key=cache_key[-8:])
            return Auth0User(**user_data)
        else:
            # Record cache miss
            JWT_CACHE_MISSES.labels(cache_type="user_cache").inc()
            logger.debug("Cache miss", cache_key=cache_key[-8:])
            
    except Exception as e:
        JWT_CACHE_MISSES.labels(cache_type="user_cache").inc()
        logger.warning("Cache read failed", error=str(e))
    
    return None

async def cache_user(token: str, user: Auth0User, ttl: int = 300) -> None:
    """Cache user in Redis with TTL and metrics tracking"""
    try:
        redis_client = get_redis_client()
        cache_key = f"auth:user:{token[-20:]}"
        
        redis_client.setex(
            cache_key, 
            ttl, 
            json.dumps(user.model_dump())
        )
        
        record_user_action("cache_write", user.sub)
        logger.debug("User cached", user_id=user.sub, ttl=ttl)
        
    except Exception as e:
        logger.warning("Cache write failed", error=str(e), user_id=user.sub)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Auth0User:
    """FastAPI dependency to get current authenticated user with caching"""
    token = credentials.credentials
    
    # Try cache first
    cached_user = await get_cached_user(token)
    if cached_user:
        # Verify token hasn't expired
        if cached_user.exp and datetime.utcnow().timestamp() < cached_user.exp:
            return cached_user
    
    # Validate with Auth0
    user = await verify_token(token)
    
    # Cache successful validation
    await cache_user(token, user)
    
    return user 