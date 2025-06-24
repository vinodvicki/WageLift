"""
Salary API endpoints for WageLift.

This module provides API endpoints for salary data management,
including salary entry creation, retrieval, and market analysis.
"""

from typing import List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.salary import SalaryEntry
from app.services.supabase_service import SupabaseService

router = APIRouter()

# Pydantic models
class SalaryEntryCreate(BaseModel):
    """Model for creating a new salary entry."""
    current_salary: float = Field(..., gt=0, description="Current annual salary")
    last_raise_date: date = Field(..., description="Date of last salary raise")
    job_title: str = Field(..., min_length=1, max_length=200, description="Job title")
    company_name: Optional[str] = Field(None, max_length=200, description="Company name")
    location: Optional[str] = Field(None, max_length=200, description="Work location")
    years_experience: Optional[int] = Field(None, ge=0, le=50, description="Years of experience")
    education_level: Optional[str] = Field(None, description="Education level")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    
    @validator('last_raise_date')
    def validate_raise_date(cls, v):
        if v > date.today():
            raise ValueError('Last raise date cannot be in the future')
        return v

class SalaryEntryResponse(BaseModel):
    """Model for salary entry response."""
    id: int
    current_salary: float
    last_raise_date: date
    job_title: str
    company_name: Optional[str]
    location: Optional[str]
    years_experience: Optional[int]
    education_level: Optional[str]
    industry: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SalaryEntryUpdate(BaseModel):
    """Model for updating salary entry."""
    current_salary: Optional[float] = Field(None, gt=0)
    last_raise_date: Optional[date] = None
    job_title: Optional[str] = Field(None, min_length=1, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    education_level: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=100)
    
    @validator('last_raise_date')
    def validate_raise_date(cls, v):
        if v and v > date.today():
            raise ValueError('Last raise date cannot be in the future')
        return v

# API Endpoints
@router.post("/salary-entries", response_model=SalaryEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_entry(
    salary_data: SalaryEntryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new salary entry for the current user.
    """
    try:
        supabase_service = SupabaseService()
        
        # Create salary entry data
        entry_data = {
            "user_id": current_user.id,
            "current_salary": salary_data.current_salary,
            "last_raise_date": salary_data.last_raise_date.isoformat(),
            "job_title": salary_data.job_title,
            "company_name": salary_data.company_name,
            "location": salary_data.location,
            "years_experience": salary_data.years_experience,
            "education_level": salary_data.education_level,
            "industry": salary_data.industry,
        }
        
        # Create entry in Supabase
        result = await supabase_service.create_salary_entry(entry_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create salary entry"
            )
        
        return SalaryEntryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating salary entry: {str(e)}"
        )

@router.get("/salary-entries", response_model=List[SalaryEntryResponse])
async def get_salary_entries(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all salary entries for the current user.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get user's salary entries
        entries = await supabase_service.get_user_salary_entries(
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        return [SalaryEntryResponse(**entry) for entry in entries]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving salary entries: {str(e)}"
        )

@router.get("/salary-entries/{entry_id}", response_model=SalaryEntryResponse)
async def get_salary_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific salary entry by ID.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get salary entry
        entry = await supabase_service.get_salary_entry(entry_id, current_user.id)
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salary entry not found"
            )
        
        return SalaryEntryResponse(**entry)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving salary entry: {str(e)}"
        )

@router.put("/salary-entries/{entry_id}", response_model=SalaryEntryResponse)
async def update_salary_entry(
    entry_id: int,
    salary_data: SalaryEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific salary entry.
    """
    try:
        supabase_service = SupabaseService()
        
        # Prepare update data (only include non-None values)
        update_data = {}
        for field, value in salary_data.dict(exclude_unset=True).items():
            if value is not None:
                if field == 'last_raise_date' and isinstance(value, date):
                    update_data[field] = value.isoformat()
                else:
                    update_data[field] = value
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        # Update salary entry
        updated_entry = await supabase_service.update_salary_entry(
            entry_id, current_user.id, update_data
        )
        
        if not updated_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salary entry not found"
            )
        
        return SalaryEntryResponse(**updated_entry)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating salary entry: {str(e)}"
        )

@router.delete("/salary-entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salary_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific salary entry.
    """
    try:
        supabase_service = SupabaseService()
        
        # Delete salary entry
        success = await supabase_service.delete_salary_entry(entry_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salary entry not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting salary entry: {str(e)}"
        )

@router.get("/salary-entries/{entry_id}/analysis")
async def get_salary_analysis(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get salary analysis for a specific entry including CPI gap and market comparison.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get salary entry
        entry = await supabase_service.get_salary_entry(entry_id, current_user.id)
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salary entry not found"
            )
        
        # TODO: Integrate with CPI calculation and benchmark services
        # This would typically call the CPI and benchmark services
        analysis = {
            "entry_id": entry_id,
            "current_salary": entry["current_salary"],
            "last_raise_date": entry["last_raise_date"],
            "analysis_date": datetime.now().isoformat(),
            "cpi_gap": None,  # To be calculated by CPI service
            "market_percentile": None,  # To be calculated by benchmark service
            "recommended_salary": None,  # To be calculated based on analysis
        }
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating salary analysis: {str(e)}"
        ) 