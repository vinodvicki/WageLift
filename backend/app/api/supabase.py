from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from app.core.auth import get_current_user, Auth0User
from app.services.supabase_service import supabase_service

router = APIRouter(prefix="/supabase", tags=["supabase"])

@router.get("/user/profile", response_model=Dict[str, Any])
async def get_user_profile(current_user: Auth0User = Depends(get_current_user)):
    """Get current user's profile with Supabase data"""
    try:
        # Get or create user in Supabase
        user_data = await supabase_service.get_user_by_email(current_user.email)
        
        if not user_data:
            # Create user record
            user_data = await supabase_service.create_user({
                "auth0_id": current_user.sub,
                "email": current_user.email,
                "full_name": current_user.name,
                "profile_picture_url": current_user.picture,
                "last_login": None
            })
        else:
            # Update last login
            await supabase_service.update_user(user_data["id"], {
                "last_login": None  # Will be set to current timestamp by service
            })
        
        return {
            "user": user_data,
            "auth0_user": {
                "sub": current_user.sub,
                "email": current_user.email,
                "name": current_user.name,
                "picture": current_user.picture
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user profile: {str(e)}"
        )

@router.post("/user/profile", response_model=Dict[str, Any])
async def update_user_profile(
    profile_data: Dict[str, Any],
    current_user: Auth0User = Depends(get_current_user)
):
    """Update user profile"""
    try:
        # Get user record
        user_data = await supabase_service.get_user_by_email(current_user.email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user profile
        updated_user = await supabase_service.update_user(user_data["id"], profile_data)
        
        return {
            "profile": updated_user,
            "message": "Profile updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.get("/salary/entries", response_model=List[Dict[str, Any]])
async def get_salary_entries(current_user: Auth0User = Depends(get_current_user)):
    """Get all salary entries for current user"""
    try:
        # Get user record
        user_data = await supabase_service.get_user_by_email(current_user.email)
        
        if not user_data:
            return []
        
        entries = await supabase_service.get_user_salary_entries(user_data["id"])
        return entries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch salary entries: {str(e)}"
        )

@router.post("/salary/entries", response_model=Dict[str, Any])
async def create_salary_entry(
    salary_data: Dict[str, Any],
    current_user: Auth0User = Depends(get_current_user)
):
    """Create a new salary entry"""
    try:
        # Get user record
        user_data = await supabase_service.get_user_by_email(current_user.email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Add user_id to salary data
        salary_data["user_id"] = user_data["id"]
        
        # Create salary entry
        new_entry = await supabase_service.create_salary_entry(salary_data)
        
        return {
            "entry": new_entry,
            "message": "Salary entry created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create salary entry: {str(e)}"
        )

@router.get("/raise/requests", response_model=List[Dict[str, Any]])
async def get_raise_requests(current_user: Auth0User = Depends(get_current_user)):
    """Get all raise requests for current user"""
    try:
        # Get user record
        user_data = await supabase_service.get_user_by_email(current_user.email)
        
        if not user_data:
            return []
        
        requests = await supabase_service.get_user_raise_requests(user_data["id"])
        return requests
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch raise requests: {str(e)}"
        )

@router.post("/raise/requests", response_model=Dict[str, Any])
async def create_raise_request(
    request_data: Dict[str, Any],
    current_user: Auth0User = Depends(get_current_user)
):
    """Create a new raise request"""
    try:
        # Get user record
        user_data = await supabase_service.get_user_by_email(current_user.email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Add user_id to request data
        request_data["user_id"] = user_data["id"]
        
        # Create raise request
        new_request = await supabase_service.create_raise_request(request_data)
        
        return {
            "request": new_request,
            "message": "Raise request created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create raise request: {str(e)}"
        )

@router.get("/benchmarks", response_model=List[Dict[str, Any]])
async def get_benchmarks(
    job_title: Optional[str] = None,
    location: Optional[str] = None,
    current_user: Auth0User = Depends(get_current_user)
):
    """Get salary benchmarks with optional filtering"""
    try:
        if job_title and location:
            benchmark = await supabase_service.get_benchmark_data(job_title, location)
            return [benchmark] if benchmark else []
        else:
            # Return empty list if no specific search criteria
            return []
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch benchmarks: {str(e)}"
        )

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check for Supabase service"""
    try:
        is_healthy = await supabase_service.test_connection()
        
        if is_healthy:
            return {
                "status": "healthy",
                "service": "supabase",
                "connection": "active"
            }
        else:
            return {
                "status": "unhealthy",
                "service": "supabase",
                "connection": "failed"
            }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "supabase",
            "error": str(e)
        } 