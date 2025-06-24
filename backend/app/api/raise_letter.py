"""
Raise Letter API endpoints for WageLift.

This module provides API endpoints for AI-generated raise letter creation,
editing, and management using OpenAI services.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.openai_service import OpenAIService
from app.services.supabase_service import SupabaseService

router = APIRouter()

# Pydantic models
class RaiseLetterRequest(BaseModel):
    """Model for raise letter generation request."""
    job_title: str = Field(..., min_length=1, max_length=200, description="Job title")
    current_salary: float = Field(..., gt=0, description="Current annual salary")
    requested_salary: float = Field(..., gt=0, description="Requested annual salary")
    last_raise_date: str = Field(..., description="Date of last salary raise")
    achievements: List[str] = Field(..., min_items=1, description="List of achievements and contributions")
    company_name: Optional[str] = Field(None, max_length=200, description="Company name")
    manager_name: Optional[str] = Field(None, max_length=100, description="Manager's name")
    years_in_role: Optional[int] = Field(None, ge=0, le=50, description="Years in current role")
    market_data: Optional[dict] = Field(None, description="Market salary data for context")
    cpi_data: Optional[dict] = Field(None, description="CPI analysis data for context")
    tone: Optional[str] = Field("professional", description="Tone of the letter (professional, confident, collaborative)")
    
class RaiseLetterResponse(BaseModel):
    """Model for raise letter response."""
    id: str
    content: str
    subject: Optional[str]
    tone: str
    created_at: datetime
    job_title: str
    current_salary: float
    requested_salary: float
    
    class Config:
        from_attributes = True

class RaiseLetterUpdate(BaseModel):
    """Model for updating a raise letter."""
    content: str = Field(..., min_length=10, description="Updated letter content")
    subject: Optional[str] = Field(None, description="Updated subject line")
    
class RaiseLetterTemplate(BaseModel):
    """Model for raise letter template."""
    template_name: str
    description: str
    content_structure: dict
    recommended_tone: str

# API Endpoints
@router.post("/generate", response_model=RaiseLetterResponse, status_code=status.HTTP_201_CREATED)
async def generate_raise_letter(
    letter_request: RaiseLetterRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an AI-powered raise letter based on user input and market data.
    """
    try:
        openai_service = OpenAIService()
        supabase_service = SupabaseService()
        
        # Prepare context for AI generation
        context = {
            "job_title": letter_request.job_title,
            "current_salary": letter_request.current_salary,
            "requested_salary": letter_request.requested_salary,
            "last_raise_date": letter_request.last_raise_date,
            "achievements": letter_request.achievements,
            "company_name": letter_request.company_name,
            "manager_name": letter_request.manager_name,
            "years_in_role": letter_request.years_in_role,
            "market_data": letter_request.market_data,
            "cpi_data": letter_request.cpi_data,
            "tone": letter_request.tone
        }
        
        # Generate raise letter using OpenAI
        letter_content = await openai_service.generate_raise_letter(context)
        
        if not letter_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate raise letter"
            )
        
        # Save generated letter to database
        letter_data = {
            "user_id": current_user.id,
            "content": letter_content["content"],
            "subject": letter_content.get("subject"),
            "tone": letter_request.tone,
            "job_title": letter_request.job_title,
            "current_salary": letter_request.current_salary,
            "requested_salary": letter_request.requested_salary,
            "generation_context": context
        }
        
        saved_letter = await supabase_service.save_raise_letter(letter_data)
        
        if not saved_letter:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save generated letter"
            )
        
        return RaiseLetterResponse(
            id=saved_letter["id"],
            content=saved_letter["content"],
            subject=saved_letter.get("subject"),
            tone=saved_letter["tone"],
            created_at=datetime.fromisoformat(saved_letter["created_at"]),
            job_title=saved_letter["job_title"],
            current_salary=saved_letter["current_salary"],
            requested_salary=saved_letter["requested_salary"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating raise letter: {str(e)}"
        )

@router.get("/", response_model=List[RaiseLetterResponse])
async def get_user_raise_letters(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all raise letters for the current user.
    """
    try:
        supabase_service = SupabaseService()
        
        letters = await supabase_service.get_user_raise_letters(current_user.id)
        
        return [
            RaiseLetterResponse(
                id=letter["id"],
                content=letter["content"],
                subject=letter.get("subject"),
                tone=letter["tone"],
                created_at=datetime.fromisoformat(letter["created_at"]),
                job_title=letter["job_title"],
                current_salary=letter["current_salary"],
                requested_salary=letter["requested_salary"]
            )
            for letter in letters
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving raise letters: {str(e)}"
        )

@router.get("/{letter_id}", response_model=RaiseLetterResponse)
async def get_raise_letter(
    letter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific raise letter by ID.
    """
    try:
        supabase_service = SupabaseService()
        
        letter = await supabase_service.get_raise_letter(letter_id, current_user.id)
        
        if not letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raise letter not found"
            )
        
        return RaiseLetterResponse(
            id=letter["id"],
            content=letter["content"],
            subject=letter.get("subject"),
            tone=letter["tone"],
            created_at=datetime.fromisoformat(letter["created_at"]),
            job_title=letter["job_title"],
            current_salary=letter["current_salary"],
            requested_salary=letter["requested_salary"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving raise letter: {str(e)}"
        )

@router.put("/{letter_id}", response_model=RaiseLetterResponse)
async def update_raise_letter(
    letter_id: str,
    letter_update: RaiseLetterUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific raise letter.
    """
    try:
        supabase_service = SupabaseService()
        
        update_data = {
            "content": letter_update.content,
            "subject": letter_update.subject,
            "updated_at": datetime.now().isoformat()
        }
        
        updated_letter = await supabase_service.update_raise_letter(
            letter_id, current_user.id, update_data
        )
        
        if not updated_letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raise letter not found"
            )
        
        return RaiseLetterResponse(
            id=updated_letter["id"],
            content=updated_letter["content"],
            subject=updated_letter.get("subject"),
            tone=updated_letter["tone"],
            created_at=datetime.fromisoformat(updated_letter["created_at"]),
            job_title=updated_letter["job_title"],
            current_salary=updated_letter["current_salary"],
            requested_salary=updated_letter["requested_salary"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating raise letter: {str(e)}"
        )

@router.delete("/{letter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_raise_letter(
    letter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific raise letter.
    """
    try:
        supabase_service = SupabaseService()
        
        success = await supabase_service.delete_raise_letter(letter_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raise letter not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting raise letter: {str(e)}"
        )

@router.get("/templates/available", response_model=List[RaiseLetterTemplate])
async def get_available_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get available raise letter templates.
    """
    try:
        # Return predefined templates
        templates = [
            RaiseLetterTemplate(
                template_name="Professional Standard",
                description="A formal, professional template suitable for most corporate environments",
                content_structure={
                    "opening": "formal_greeting",
                    "body": ["achievements", "market_data", "cpi_analysis", "request"],
                    "closing": "professional_closing"
                },
                recommended_tone="professional"
            ),
            RaiseLetterTemplate(
                template_name="Data-Driven",
                description="Emphasizes market data and inflation analysis with supporting evidence",
                content_structure={
                    "opening": "direct_approach",
                    "body": ["market_analysis", "cpi_data", "achievements", "justification"],
                    "closing": "confident_closing"
                },
                recommended_tone="confident"
            ),
            RaiseLetterTemplate(
                template_name="Collaborative",
                description="Focuses on team contribution and collaborative growth",
                content_structure={
                    "opening": "appreciation",
                    "body": ["team_contributions", "growth_story", "market_context", "proposal"],
                    "closing": "collaborative_closing"
                },
                recommended_tone="collaborative"
            )
        ]
        
        return templates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving templates: {str(e)}"
        )

@router.post("/{letter_id}/regenerate", response_model=RaiseLetterResponse)
async def regenerate_raise_letter(
    letter_id: str,
    regeneration_request: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate a raise letter with updated context or different tone.
    """
    try:
        supabase_service = SupabaseService()
        openai_service = OpenAIService()
        
        # Get existing letter
        existing_letter = await supabase_service.get_raise_letter(letter_id, current_user.id)
        
        if not existing_letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raise letter not found"
            )
        
        # Use existing context or update with new parameters
        context = existing_letter.get("generation_context", {})
        if regeneration_request:
            context.update(regeneration_request)
        
        # Regenerate letter
        new_content = await openai_service.generate_raise_letter(context)
        
        if not new_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to regenerate raise letter"
            )
        
        # Update the existing letter
        update_data = {
            "content": new_content["content"],
            "subject": new_content.get("subject"),
            "updated_at": datetime.now().isoformat(),
            "generation_context": context
        }
        
        updated_letter = await supabase_service.update_raise_letter(
            letter_id, current_user.id, update_data
        )
        
        return RaiseLetterResponse(
            id=updated_letter["id"],
            content=updated_letter["content"],
            subject=updated_letter.get("subject"),
            tone=updated_letter["tone"],
            created_at=datetime.fromisoformat(updated_letter["created_at"]),
            job_title=updated_letter["job_title"],
            current_salary=updated_letter["current_salary"],
            requested_salary=updated_letter["requested_salary"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating raise letter: {str(e)}"
        ) 