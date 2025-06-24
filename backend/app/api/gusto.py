"""
Gusto Integration API endpoints for WageLift.

This module provides API endpoints for Gusto OAuth integration,
payroll data synchronization, and token management.
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.gusto_service import GustoService
from app.services.salary_sync_service import SalarySyncService

router = APIRouter()

# Pydantic models
class GustoConnectionStatus(BaseModel):
    """Model for Gusto connection status."""
    connected: bool
    company_name: Optional[str] = None
    last_sync: Optional[datetime] = None
    token_expires_at: Optional[datetime] = None
    
class SyncResponse(BaseModel):
    """Model for sync operation response."""
    success: bool
    message: str
    synced_entries: int
    skipped_entries: int
    errors: list = []

# API Endpoints
@router.get("/authorize")
async def authorize_gusto(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate Gusto OAuth authorization flow.
    """
    try:
        gusto_service = GustoService()
        
        # Generate authorization URL
        auth_url = await gusto_service.get_authorization_url(current_user.id)
        
        if not auth_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate authorization URL"
            )
        
        return {"authorization_url": auth_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating Gusto authorization: {str(e)}"
        )

@router.get("/callback")
async def gusto_callback(
    request: Request,
    code: str = Query(..., description="Authorization code from Gusto"),
    state: str = Query(..., description="State parameter for security"),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Gusto OAuth callback and exchange code for tokens.
    """
    try:
        gusto_service = GustoService()
        
        # Exchange authorization code for tokens
        result = await gusto_service.handle_callback(code, state)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth callback failed: {result.get('error', 'Unknown error')}"
            )
        
        # Redirect to success page or dashboard
        return RedirectResponse(
            url="/dashboard?gusto_connected=true",
            status_code=status.HTTP_302_FOUND
        )
        
    except Exception as e:
        # Redirect to error page
        return RedirectResponse(
            url=f"/dashboard?gusto_error={str(e)}",
            status_code=status.HTTP_302_FOUND
        )

@router.post("/sync", response_model=SyncResponse)
async def sync_salary_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync salary data from Gusto to WageLift.
    """
    try:
        gusto_service = GustoService()
        salary_sync_service = SalarySyncService()
        
        # Check if user has valid Gusto connection
        connection_status = await gusto_service.check_connection_status(current_user.id)
        
        if not connection_status["connected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gusto account not connected. Please authorize first."
            )
        
        # Fetch compensation data from Gusto
        compensation_data = await gusto_service.get_user_compensation_data(current_user.id)
        
        if not compensation_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No compensation data found in Gusto"
            )
        
        # Sync data using salary sync service
        sync_result = await salary_sync_service.sync_gusto_data(
            user_id=current_user.id,
            compensation_data=compensation_data
        )
        
        return SyncResponse(
            success=True,
            message=f"Successfully synced {sync_result['synced_entries']} salary entries",
            synced_entries=sync_result["synced_entries"],
            skipped_entries=sync_result["skipped_entries"],
            errors=sync_result.get("errors", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing salary data: {str(e)}"
        )

@router.get("/status", response_model=GustoConnectionStatus)
async def get_connection_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current Gusto connection status for the user.
    """
    try:
        gusto_service = GustoService()
        
        # Check connection status
        status_data = await gusto_service.check_connection_status(current_user.id)
        
        return GustoConnectionStatus(
            connected=status_data["connected"],
            company_name=status_data.get("company_name"),
            last_sync=datetime.fromisoformat(status_data["last_sync"]) if status_data.get("last_sync") else None,
            token_expires_at=datetime.fromisoformat(status_data["token_expires_at"]) if status_data.get("token_expires_at") else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking connection status: {str(e)}"
        )

@router.delete("/disconnect")
async def disconnect_gusto(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disconnect Gusto integration for the current user.
    """
    try:
        gusto_service = GustoService()
        
        # Disconnect Gusto account
        result = await gusto_service.disconnect_account(current_user.id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to disconnect Gusto: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": "Gusto account disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disconnecting Gusto: {str(e)}"
        )

@router.get("/companies")
async def get_user_companies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get companies associated with the user's Gusto account.
    """
    try:
        gusto_service = GustoService()
        
        # Check if user has valid connection
        connection_status = await gusto_service.check_connection_status(current_user.id)
        
        if not connection_status["connected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gusto account not connected"
            )
        
        # Get companies
        companies = await gusto_service.get_user_companies(current_user.id)
        
        return {
            "companies": companies,
            "count": len(companies)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving companies: {str(e)}"
        )

@router.get("/payrolls")
async def get_recent_payrolls(
    company_id: Optional[str] = Query(None, description="Specific company ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of payrolls to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent payroll data from Gusto.
    """
    try:
        gusto_service = GustoService()
        
        # Check connection
        connection_status = await gusto_service.check_connection_status(current_user.id)
        
        if not connection_status["connected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gusto account not connected"
            )
        
        # Get payroll data
        payrolls = await gusto_service.get_recent_payrolls(
            user_id=current_user.id,
            company_id=company_id,
            limit=limit
        )
        
        return {
            "payrolls": payrolls,
            "count": len(payrolls),
            "company_id": company_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving payrolls: {str(e)}"
        )

@router.post("/refresh-token")
async def refresh_access_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh the Gusto access token.
    """
    try:
        gusto_service = GustoService()
        
        # Refresh token
        result = await gusto_service.refresh_access_token(current_user.id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to refresh token: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": "Access token refreshed successfully",
            "expires_at": result.get("expires_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing token: {str(e)}"
        )
