"""
Auth-related API endpoints for testing JWT validation
"""
from datetime import datetime
from typing import Dict, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.auth import Auth0User, get_current_user, get_cached_user
from app.core.config import settings

router = APIRouter()

@router.get("/protected")
async def protected_endpoint(
    current_user: Auth0User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Protected endpoint that requires valid Auth0 JWT token
    Returns current user information
    """
    return {
        "message": f"Hello {current_user.name or current_user.email}!",
        "user": {
            "id": current_user.sub,
            "email": current_user.email,
            "email_verified": current_user.email_verified,
            "name": current_user.name,
            "picture": current_user.picture,
            "last_updated": current_user.updated_at
        },
        "token_info": {
            "audience": current_user.aud,
            "issuer": current_user.iss,
            "issued_at": current_user.iat,
            "expires_at": current_user.exp
        }
    }

@router.get("/user-profile")
async def get_user_profile(
    current_user: Auth0User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed user profile information"""
    return {
        "profile": {
            "user_id": current_user.sub,
            "email": current_user.email,
            "email_verified": current_user.email_verified,
            "name": current_user.name,
            "nickname": current_user.nickname,
            "picture": current_user.picture,
            "updated_at": current_user.updated_at,
        },
        "account_status": {
            "verified": current_user.email_verified,
            "active": True,  # Could be extended with more checks
        }
    }

@router.post("/validate-token")
async def validate_token(
    current_user: Auth0User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate token and return validation status
    Useful for frontend to check token validity
    """
    return {
        "valid": True,
        "user_id": current_user.sub,
        "email": current_user.email,
        "expires_at": current_user.exp,
        "message": "Token is valid"
    }

@router.get("/auth-status")
async def auth_status() -> Dict[str, Any]:
    """
    Public endpoint to check Auth0 configuration status
    Does not require authentication
    """
    return {
        "auth_configured": bool(settings.AUTH0_DOMAIN and settings.AUTH0_AUDIENCE),
        "auth0_domain": settings.AUTH0_DOMAIN if settings.AUTH0_DOMAIN else None,
        "audience": settings.AUTH0_AUDIENCE if settings.AUTH0_AUDIENCE else None,
        "algorithm": settings.AUTH0_ALGORITHM,
        "message": "Auth0 configuration status"
    }

@router.get("/health", response_model=None)
async def auth_health_check():
    """
    Health check endpoint for authentication service
    Tests Redis connectivity and Auth0 configuration
    """
    health_status = {
        "auth_service": "healthy",
        "timestamp": str(datetime.utcnow()),
        "checks": {}
    }
    
    # Check Auth0 configuration
    try:
        if not all([settings.AUTH0_DOMAIN, settings.AUTH0_AUDIENCE, settings.AUTH0_ALGORITHM]):
            health_status["checks"]["auth0_config"] = "missing_configuration"
        else:
            health_status["checks"]["auth0_config"] = "configured"
    except Exception as e:
        health_status["checks"]["auth0_config"] = f"error: {str(e)}"
    
    # Check Redis connectivity
    try:
        from app.core.auth import get_redis_client
        redis_client = get_redis_client()
        redis_client.ping()
        health_status["checks"]["redis"] = "connected"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["auth_service"] = "degraded"
    
    # Determine overall status
    if any("error" in check for check in health_status["checks"].values()):
        health_status["auth_service"] = "unhealthy"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status 