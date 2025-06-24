"""
Gusto OAuth and API service.

Handles OAuth 2.0 flow, token management, and API interactions with Gusto.
"""

import base64
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, GustoToken


class GustoOAuthError(Exception):
    """Base exception for Gusto OAuth errors."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GustoAPIError(Exception):
    """Base exception for Gusto API errors."""
    
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GustoService:
    """
    Service for handling Gusto OAuth and API operations.
    
    Provides secure token management, OAuth flow handling,
    and salary data synchronization.
    """
    
    def __init__(self):
        self.client_id = settings.GUSTO_CLIENT_ID
        self.client_secret = settings.GUSTO_CLIENT_SECRET
        self.redirect_uri = settings.GUSTO_REDIRECT_URI
        self.auth_url = settings.GUSTO_AUTH_URL
        self.token_url = settings.GUSTO_TOKEN_URL
        self.api_base_url = settings.GUSTO_API_BASE_URL
        self.scopes = settings.GUSTO_SCOPES
    
    def generate_authorization_url(self, state: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Generate the authorization URL for Gusto OAuth flow.
        
        Returns:
            Tuple of (authorization_url, state, code_verifier)
        """
        if not state:
            state = secrets.token_urlsafe(16)
        
        # Generate PKCE parameters
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().replace("=", "")
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        authorization_url = f"{self.auth_url}?{urlencode(params)}"
        return authorization_url, state, code_verifier
    
    async def exchange_code_for_token(
        self, 
        code: str, 
        code_verifier: str
    ) -> Dict:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from Gusto
            code_verifier: PKCE code verifier
            
        Returns:
            Token response from Gusto
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                raise GustoOAuthError(
                    f"Failed to exchange code for token: {error_detail}",
                    e.response.status_code if e.response else 500
                )
    
    async def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: Gusto refresh token
            
        Returns:
            New token response from Gusto
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                raise GustoOAuthError(
                    f"Failed to refresh token: {error_detail}",
                    e.response.status_code if e.response else 500
                )
    
    def _generate_encryption_key(self) -> bytes:
        """Generate a new encryption key for token storage."""
        return Fernet.generate_key()
    
    def _encrypt_token(self, token: str, key: bytes) -> str:
        """Encrypt a token using the provided key."""
        fernet = Fernet(key)
        return fernet.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str, key: bytes) -> str:
        """Decrypt a token using the provided key."""
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_token.encode()).decode()
    
    def store_token(
        self,
        db: Session,
        user: User,
        token_data: Dict,
        company_id: Optional[str] = None,
        employee_id: Optional[str] = None
    ) -> GustoToken:
        """
        Store encrypted Gusto tokens in the database.
        
        Args:
            db: Database session
            user: User object
            token_data: Token response from Gusto
            company_id: Optional Gusto company ID
            employee_id: Optional Gusto employee ID
            
        Returns:
            Created GustoToken object
        """
        # Deactivate existing tokens for the user
        existing_tokens = db.query(GustoToken).filter(
            GustoToken.user_id == user.id,
            GustoToken.is_active == True
        ).all()
        
        for token in existing_tokens:
            token.deactivate()
        
        # Generate encryption key
        encryption_key = self._generate_encryption_key()
        
        # Encrypt tokens
        encrypted_access_token = self._encrypt_token(
            token_data["access_token"], 
            encryption_key
        )
        encrypted_refresh_token = self._encrypt_token(
            token_data["refresh_token"], 
            encryption_key
        )
        
        # Calculate expiration
        expires_in = token_data.get("expires_in", 7200)  # Default 2 hours
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Create new token record
        gusto_token = GustoToken(
            user_id=user.id,
            encrypted_access_token=encrypted_access_token,
            encrypted_refresh_token=encrypted_refresh_token,
            token_type=token_data.get("token_type", "Bearer"),
            expires_at=expires_at,
            encryption_key=encryption_key,
            gusto_company_id=company_id,
            gusto_employee_id=employee_id,
            scopes=self.scopes
        )
        
        db.add(gusto_token)
        db.commit()
        db.refresh(gusto_token)
        
        return gusto_token
    
    def get_active_token(self, db: Session, user: User) -> Optional[GustoToken]:
        """
        Get the active Gusto token for a user.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Active GustoToken or None
        """
        return db.query(GustoToken).filter(
            GustoToken.user_id == user.id,
            GustoToken.is_active == True
        ).first()
    
    async def get_valid_access_token(self, db: Session, user: User) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Valid access token or None if no token available
        """
        token_record = self.get_active_token(db, user)
        if not token_record:
            return None
        
        # Decrypt access token
        access_token = self._decrypt_token(
            token_record.encrypted_access_token,
            token_record.encryption_key
        )
        
        # Check if token is expired
        if not token_record.is_expired:
            token_record.mark_used()
            db.commit()
            return access_token
        
        # Token is expired, try to refresh
        try:
            refresh_token = self._decrypt_token(
                token_record.encrypted_refresh_token,
                token_record.encryption_key
            )
            
            new_token_data = await self.refresh_token(refresh_token)
            
            # Update the existing token record
            new_encryption_key = self._generate_encryption_key()
            token_record.encrypted_access_token = self._encrypt_token(
                new_token_data["access_token"],
                new_encryption_key
            )
            token_record.encrypted_refresh_token = self._encrypt_token(
                new_token_data["refresh_token"],
                new_encryption_key
            )
            token_record.encryption_key = new_encryption_key
            
            expires_in = new_token_data.get("expires_in", 7200)
            token_record.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            token_record.mark_used()
            
            db.commit()
            
            return new_token_data["access_token"]
            
        except GustoOAuthError:
            # Refresh failed, deactivate token
            token_record.deactivate()
            db.commit()
            return None
    
    async def make_api_request(
        self,
        db: Session,
        user: User,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict:
        """
        Make an authenticated API request to Gusto.
        
        Args:
            db: Database session
            user: User object
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for httpx request
            
        Returns:
            API response data
        """
        access_token = await self.get_valid_access_token(db, user)
        if not access_token:
            raise GustoAPIError("No valid Gusto token available", 401)
        
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {access_token}"
        headers["X-Gusto-API-Version"] = "2024-04-01"
        
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                error_detail = e.response.text if e.response else str(e)
                raise GustoAPIError(
                    f"Gusto API error: {error_detail}",
                    e.response.status_code if e.response else 500
                )
    
    async def get_companies(self, db: Session, user: User) -> List[Dict]:
        """
        Get companies associated with the user's Gusto account.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            List of company data
        """
        response = await self.make_api_request(db, user, "GET", "/companies")
        return response.get("data", [])
    
    async def get_employees(self, db: Session, user: User, company_id: str) -> List[Dict]:
        """
        Get employees for a specific company.
        
        Args:
            db: Database session
            user: User object
            company_id: Gusto company ID
            
        Returns:
            List of employee data
        """
        response = await self.make_api_request(
            db, user, "GET", f"/companies/{company_id}/employees"
        )
        return response.get("data", [])
    
    async def get_employee_compensations(
        self, 
        db: Session, 
        user: User, 
        employee_id: str
    ) -> List[Dict]:
        """
        Get compensation data for a specific employee.
        
        Args:
            db: Database session
            user: User object
            employee_id: Gusto employee ID
            
        Returns:
            List of compensation data
        """
        response = await self.make_api_request(
            db, user, "GET", f"/employees/{employee_id}/compensations"
        )
        return response.get("data", [])
    
    async def sync_salary_data(self, db: Session, user: User) -> Dict:
        """
        Synchronize salary data from Gusto for the user.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Summary of synchronized data
        """
        try:
            # Get companies
            companies = await self.get_companies(db, user)
            if not companies:
                raise GustoAPIError("No companies found in Gusto account", 404)
            
            # For now, use the first company
            company = companies[0]
            company_id = company["id"]
            
            # Get employees
            employees = await self.get_employees(db, user, company_id)
            
            # Find the user's employee record by email
            user_employee = None
            for employee in employees:
                if employee.get("email") == user.email:
                    user_employee = employee
                    break
            
            if not user_employee:
                raise GustoAPIError("User not found as employee in Gusto", 404)
            
            employee_id = user_employee["id"]
            
            # Update token with company and employee IDs
            token_record = self.get_active_token(db, user)
            if token_record:
                token_record.gusto_company_id = company_id
                token_record.gusto_employee_id = employee_id
                db.commit()
            
            # Get compensation data
            compensations = await self.get_employee_compensations(
                db, user, employee_id
            )
            
            return {
                "success": True,
                "company": company,
                "employee": user_employee,
                "compensations": compensations,
                "message": f"Successfully synchronized data for {len(compensations)} compensation records"
            }
            
        except (GustoAPIError, GustoOAuthError) as e:
            return {
                "success": False,
                "error": e.message,
                "message": f"Failed to sync salary data: {e.message}"
            }


# Create global service instance
gusto_service = GustoService()


def get_gusto_service() -> GustoService:
    """Get Gusto service instance (dependency injection)."""
    return gusto_service 