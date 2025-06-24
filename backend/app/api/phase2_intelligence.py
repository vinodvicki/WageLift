"""
Enhanced Phase 2 Intelligence API - Revolutionary Features for WageLift.

This module provides intelligent manager profiling, readiness scoring,
and advanced AI capabilities with comprehensive error handling.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
import time
import structlog

from app.core.database import get_db
from app.core.error_handling import (
    async_error_handler,
    error_handler,
    WageLiftException,
    ExternalServiceError,
    DataValidationError,
    safe_divide,
    validate_range,
    sanitize_input,
    create_checkpoint,
    safe_operation
)
from app.services.manager_profiler_service import ManagerProfilerService
from app.services.readiness_score_service import ReadinessScoreService
from app.models.manager_profile import ManagerProfile
from app.models.readiness_score import ReadinessScore

# Logger
logger = structlog.get_logger(__name__)

# Router
router = APIRouter()

# Service instances with error handling
try:
    manager_profiler_service = ManagerProfilerService()
    readiness_score_service = ReadinessScoreService()
    logger.info("Phase 2 Intelligence services initialized successfully")
except Exception as e:
    logger.error("Failed to initialize Phase 2 Intelligence services", error=str(e))
    manager_profiler_service = None
    readiness_score_service = None


# === Request/Response Models ===

class CommunicationStyleEnum(str):
    """Communication style options for manager profiling."""
    DATA_DRIVEN = "data_driven"
    RELATIONSHIP_FOCUSED = "relationship_focused"
    DIRECT_ASSERTIVE = "direct_assertive"
    COLLABORATIVE = "collaborative"
    RESULTS_ORIENTED = "results_oriented"


class ManagerProfileRequest(BaseModel):
    """Request model for manager profiling."""
    
    manager_name: str = Field(..., min_length=1, max_length=100, description="Manager's name")
    department: Optional[str] = Field(None, max_length=100, description="Department or team")
    interaction_examples: List[str] = Field(
        ..., 
        min_items=2, 
        max_items=10, 
        description="Examples of manager interactions"
    )
    meeting_frequency: str = Field(..., description="How often you meet with manager")
    feedback_style: Optional[str] = Field(None, description="Manager's feedback style")
    decision_making_approach: Optional[str] = Field(None, description="How manager makes decisions")
    
    @validator('manager_name', 'department', 'feedback_style', 'decision_making_approach', pre=True)
    def sanitize_text_fields(cls, v):
        if v is not None:
            return sanitize_input(str(v), max_length=500)
        return v
    
    @validator('interaction_examples', pre=True)
    def sanitize_examples(cls, v):
        if v is not None:
            return [sanitize_input(str(example), max_length=1000) for example in v]
        return v


class ManagerProfileResponse(BaseModel):
    """Response model for manager profiling."""
    
    profile_id: str = Field(..., description="Unique profile identifier")
    communication_style: CommunicationStyleEnum = Field(..., description="Identified communication style")
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Confidence in profiling (0-100)")
    key_traits: List[str] = Field(..., description="Key personality traits identified")
    communication_preferences: Dict[str, str] = Field(..., description="Preferred communication methods")
    negotiation_strategy: str = Field(..., description="Recommended negotiation approach")
    success_probability: float = Field(..., ge=0.0, le=100.0, description="Success probability for raise request")
    recommended_timing: str = Field(..., description="Best timing for raise discussion")
    conversation_starters: List[str] = Field(..., description="Suggested conversation openings")
    potential_concerns: List[str] = Field(..., description="Potential manager concerns to address")
    created_at: str = Field(..., description="Profile creation timestamp")


class ReadinessScoreRequest(BaseModel):
    """Request model for readiness score calculation."""
    
    current_salary: float = Field(..., gt=0, description="Current annual salary")
    requested_salary: float = Field(..., gt=0, description="Requested annual salary")
    years_in_position: float = Field(..., ge=0, le=50, description="Years in current position")
    years_at_company: float = Field(..., ge=0, le=50, description="Years at current company")
    performance_rating: str = Field(..., description="Recent performance rating")
    market_research_completed: bool = Field(..., description="Whether market research was done")
    achievements_documented: bool = Field(..., description="Whether achievements are documented")
    additional_responsibilities: int = Field(..., ge=0, le=20, description="Number of additional responsibilities")
    team_size_managed: int = Field(..., ge=0, le=1000, description="Size of team managed")
    recent_promotions: int = Field(..., ge=0, le=10, description="Number of recent promotions in team")
    company_financial_health: str = Field(..., description="Company financial health")
    industry_growth: str = Field(..., description="Industry growth status")
    timing_factors: List[str] = Field(default=[], description="Timing considerations")
    
    @validator('current_salary', 'requested_salary')
    def validate_salary_range(cls, v):
        if not validate_range(v, min_val=1000, max_val=10000000):
            raise ValueError("Salary must be between $1,000 and $10,000,000")
        return v
    
    @validator('requested_salary')
    def validate_salary_increase(cls, v, values):
        if 'current_salary' in values and v <= values['current_salary']:
            raise ValueError("Requested salary must be higher than current salary")
        return v


class ReadinessScoreResponse(BaseModel):
    """Response model for readiness score calculation."""
    
    score_id: str = Field(..., description="Unique score identifier")
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall readiness score (0-100)")
    score_breakdown: Dict[str, float] = Field(..., description="Detailed score breakdown by category")
    risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH")
    strengths: List[str] = Field(..., description="Key strengths for negotiation")
    areas_for_improvement: List[str] = Field(..., description="Areas to strengthen before negotiation")
    recommended_actions: List[str] = Field(..., description="Specific actions to take")
    optimal_timing: str = Field(..., description="Optimal timing for raise request")
    success_probability: float = Field(..., ge=0.0, le=100.0, description="Estimated success probability")
    alternative_strategies: List[str] = Field(..., description="Alternative negotiation strategies")
    market_position: str = Field(..., description="Your position relative to market rates")
    preparation_checklist: List[str] = Field(..., description="Pre-negotiation preparation items")
    created_at: str = Field(..., description="Score calculation timestamp")


class IntelligenceHealthResponse(BaseModel):
    """Response model for intelligence system health check."""
    
    status: str = Field(..., description="Overall system status")
    services: Dict[str, bool] = Field(..., description="Individual service health status")
    last_profile_created: Optional[str] = Field(None, description="Last profile creation time")
    last_score_calculated: Optional[str] = Field(None, description="Last score calculation time")
    error_count: int = Field(..., description="Recent error count")
    uptime: float = Field(..., description="System uptime in seconds")


# === API Endpoints ===

@router.post("/manager-profile", response_model=ManagerProfileResponse, status_code=status.HTTP_201_CREATED)
@async_error_handler(
    exceptions=(WageLiftException, ExternalServiceError, DataValidationError),
    raise_on_circuit_open=True
)
async def create_manager_profile(
    request: ManagerProfileRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> ManagerProfileResponse:
    """
    Create an intelligent manager profile using AI analysis.
    
    This endpoint analyzes manager behavior patterns and communication styles
    to provide strategic insights for salary negotiations.
    """
    if not manager_profiler_service:
        raise ExternalServiceError(
            "Manager profiler service not available",
            error_code="SERVICE_UNAVAILABLE"
        )
    
    # Create checkpoint for data recovery
    checkpoint_id = f"manager_profile_{int(time.time() * 1000)}"
    create_checkpoint({
        "operation": "create_manager_profile",
        "request": request.dict(),
        "timestamp": time.time()
    }, checkpoint_id)
    
    try:
        with safe_operation("create_manager_profile"):
            # Validate input data
            if not request.interaction_examples:
                raise DataValidationError(
                    "At least 2 interaction examples are required",
                    error_code="INSUFFICIENT_DATA"
                )
            
            # Calculate profile using AI service
            profile_data = await manager_profiler_service.analyze_manager(
                manager_name=request.manager_name,
                department=request.department,
                interaction_examples=request.interaction_examples,
                meeting_frequency=request.meeting_frequency,
                feedback_style=request.feedback_style,
                decision_making_approach=request.decision_making_approach
            )
            
            # Save to database
            manager_profile = ManagerProfile(
                profile_id=profile_data["profile_id"],
                manager_name=request.manager_name,
                department=request.department,
                communication_style=profile_data["communication_style"],
                confidence_score=profile_data["confidence_score"],
                key_traits=profile_data["key_traits"],
                communication_preferences=profile_data["communication_preferences"],
                negotiation_strategy=profile_data["negotiation_strategy"],
                success_probability=profile_data["success_probability"],
                recommended_timing=profile_data["recommended_timing"],
                conversation_starters=profile_data["conversation_starters"],
                potential_concerns=profile_data["potential_concerns"]
            )
            
            db.add(manager_profile)
            db.commit()
            db.refresh(manager_profile)
            
            # Log successful profile creation
            logger.info(
                "Manager profile created successfully",
                profile_id=profile_data["profile_id"],
                communication_style=profile_data["communication_style"],
                confidence_score=profile_data["confidence_score"]
            )
            
            # Schedule background analytics update
            background_tasks.add_task(
                update_profile_analytics,
                profile_data["profile_id"],
                profile_data["communication_style"]
            )
            
            return ManagerProfileResponse(
                profile_id=profile_data["profile_id"],
                communication_style=profile_data["communication_style"],
                confidence_score=profile_data["confidence_score"],
                key_traits=profile_data["key_traits"],
                communication_preferences=profile_data["communication_preferences"],
                negotiation_strategy=profile_data["negotiation_strategy"],
                success_probability=profile_data["success_probability"],
                recommended_timing=profile_data["recommended_timing"],
                conversation_starters=profile_data["conversation_starters"],
                potential_concerns=profile_data["potential_concerns"],
                created_at=manager_profile.created_at.isoformat()
            )
            
    except Exception as e:
        logger.error(
            "Manager profile creation failed",
            error=str(e),
            checkpoint_id=checkpoint_id,
            manager_name=request.manager_name
        )
        
        if isinstance(e, (WageLiftException, HTTPException)):
            raise
        
        raise ExternalServiceError(
            f"Profile creation failed: {str(e)}",
            error_code="PROFILE_CREATION_FAILED",
            details={"checkpoint_id": checkpoint_id}
        )


@router.post("/readiness-score", response_model=ReadinessScoreResponse, status_code=status.HTTP_201_CREATED)
@async_error_handler(
    exceptions=(WageLiftException, ExternalServiceError, DataValidationError),
    raise_on_circuit_open=True
)
async def calculate_readiness_score(
    request: ReadinessScoreRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> ReadinessScoreResponse:
    """
    Calculate intelligent readiness score for salary negotiation.
    
    This endpoint uses ML algorithms to assess negotiation readiness
    based on multiple factors and provides actionable recommendations.
    """
    if not readiness_score_service:
        raise ExternalServiceError(
            "Readiness score service not available",
            error_code="SERVICE_UNAVAILABLE"
        )
    
    # Create checkpoint for data recovery
    checkpoint_id = f"readiness_score_{int(time.time() * 1000)}"
    create_checkpoint({
        "operation": "calculate_readiness_score",
        "request": request.dict(),
        "timestamp": time.time()
    }, checkpoint_id)
    
    try:
        with safe_operation("calculate_readiness_score"):
            # Calculate salary increase percentage safely
            increase_percentage = safe_divide(
                request.requested_salary - request.current_salary,
                request.current_salary,
                default=0.0
            ) * 100
            
            # Validate reasonable increase range
            if not validate_range(increase_percentage, min_val=1.0, max_val=100.0):
                raise DataValidationError(
                    "Salary increase must be between 1% and 100%",
                    error_code="INVALID_SALARY_INCREASE"
                )
            
            # Calculate score using ML service
            score_data = await readiness_score_service.calculate_score(
                current_salary=request.current_salary,
                requested_salary=request.requested_salary,
                years_in_position=request.years_in_position,
                years_at_company=request.years_at_company,
                performance_rating=request.performance_rating,
                market_research_completed=request.market_research_completed,
                achievements_documented=request.achievements_documented,
                additional_responsibilities=request.additional_responsibilities,
                team_size_managed=request.team_size_managed,
                recent_promotions=request.recent_promotions,
                company_financial_health=request.company_financial_health,
                industry_growth=request.industry_growth,
                timing_factors=request.timing_factors
            )
            
            # Save to database
            readiness_score = ReadinessScore(
                score_id=score_data["score_id"],
                current_salary=request.current_salary,
                requested_salary=request.requested_salary,
                overall_score=score_data["overall_score"],
                score_breakdown=score_data["score_breakdown"],
                risk_level=score_data["risk_level"],
                strengths=score_data["strengths"],
                areas_for_improvement=score_data["areas_for_improvement"],
                recommended_actions=score_data["recommended_actions"],
                optimal_timing=score_data["optimal_timing"],
                success_probability=score_data["success_probability"],
                alternative_strategies=score_data["alternative_strategies"],
                market_position=score_data["market_position"],
                preparation_checklist=score_data["preparation_checklist"]
            )
            
            db.add(readiness_score)
            db.commit()
            db.refresh(readiness_score)
            
            # Log successful score calculation
            logger.info(
                "Readiness score calculated successfully",
                score_id=score_data["score_id"],
                overall_score=score_data["overall_score"],
                risk_level=score_data["risk_level"],
                increase_percentage=increase_percentage
            )
            
            # Schedule background analytics update
            background_tasks.add_task(
                update_score_analytics,
                score_data["score_id"],
                score_data["overall_score"]
            )
            
            return ReadinessScoreResponse(
                score_id=score_data["score_id"],
                overall_score=score_data["overall_score"],
                score_breakdown=score_data["score_breakdown"],
                risk_level=score_data["risk_level"],
                strengths=score_data["strengths"],
                areas_for_improvement=score_data["areas_for_improvement"],
                recommended_actions=score_data["recommended_actions"],
                optimal_timing=score_data["optimal_timing"],
                success_probability=score_data["success_probability"],
                alternative_strategies=score_data["alternative_strategies"],
                market_position=score_data["market_position"],
                preparation_checklist=score_data["preparation_checklist"],
                created_at=readiness_score.created_at.isoformat()
            )
            
    except Exception as e:
        logger.error(
            "Readiness score calculation failed",
            error=str(e),
            checkpoint_id=checkpoint_id,
            current_salary=request.current_salary,
            requested_salary=request.requested_salary
        )
        
        if isinstance(e, (WageLiftException, HTTPException)):
            raise
        
        raise ExternalServiceError(
            f"Score calculation failed: {str(e)}",
            error_code="SCORE_CALCULATION_FAILED",
            details={"checkpoint_id": checkpoint_id}
        )


@router.get("/manager-profile/{profile_id}", response_model=ManagerProfileResponse)
@error_handler(exceptions=(WageLiftException, DataValidationError))
def get_manager_profile(
    profile_id: str,
    db: Session = Depends(get_db)
) -> ManagerProfileResponse:
    """Retrieve a specific manager profile by ID."""
    
    profile_id = sanitize_input(profile_id, max_length=100)
    
    profile = db.query(ManagerProfile).filter(
        ManagerProfile.profile_id == profile_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager profile not found"
        )
    
    return ManagerProfileResponse(
        profile_id=profile.profile_id,
        communication_style=profile.communication_style,
        confidence_score=profile.confidence_score,
        key_traits=profile.key_traits,
        communication_preferences=profile.communication_preferences,
        negotiation_strategy=profile.negotiation_strategy,
        success_probability=profile.success_probability,
        recommended_timing=profile.recommended_timing,
        conversation_starters=profile.conversation_starters,
        potential_concerns=profile.potential_concerns,
        created_at=profile.created_at.isoformat()
    )


@router.get("/readiness-score/{score_id}", response_model=ReadinessScoreResponse)
@error_handler(exceptions=(WageLiftException, DataValidationError))
def get_readiness_score(
    score_id: str,
    db: Session = Depends(get_db)
) -> ReadinessScoreResponse:
    """Retrieve a specific readiness score by ID."""
    
    score_id = sanitize_input(score_id, max_length=100)
    
    score = db.query(ReadinessScore).filter(
        ReadinessScore.score_id == score_id
    ).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Readiness score not found"
        )
    
    return ReadinessScoreResponse(
        score_id=score.score_id,
        overall_score=score.overall_score,
        score_breakdown=score.score_breakdown,
        risk_level=score.risk_level,
        strengths=score.strengths,
        areas_for_improvement=score.areas_for_improvement,
        recommended_actions=score.recommended_actions,
        optimal_timing=score.optimal_timing,
        success_probability=score.success_probability,
        alternative_strategies=score.alternative_strategies,
        market_position=score.market_position,
        preparation_checklist=score.preparation_checklist,
        created_at=score.created_at.isoformat()
    )


@router.get("/health", response_model=IntelligenceHealthResponse)
@error_handler(exceptions=(Exception,))
def get_intelligence_health(db: Session = Depends(get_db)) -> IntelligenceHealthResponse:
    """Check the health status of Phase 2 Intelligence services."""
    
    try:
        # Test service availability
        services_health = {
            "manager_profiler": manager_profiler_service is not None,
            "readiness_scorer": readiness_score_service is not None,
            "database": True  # If we reach here, DB is working
        }
        
        # Get recent activity
        latest_profile = db.query(ManagerProfile).order_by(
            ManagerProfile.created_at.desc()
        ).first()
        
        latest_score = db.query(ReadinessScore).order_by(
            ReadinessScore.created_at.desc()
        ).first()
        
        # Determine overall status
        overall_status = "healthy" if all(services_health.values()) else "degraded"
        
        from app.core.error_handling import get_error_stats
        error_stats = get_error_stats()
        
        return IntelligenceHealthResponse(
            status=overall_status,
            services=services_health,
            last_profile_created=latest_profile.created_at.isoformat() if latest_profile else None,
            last_score_calculated=latest_score.created_at.isoformat() if latest_score else None,
            error_count=error_stats["recent_error_count"],
            uptime=time.time()  # Simplified uptime calculation
        )
        
    except Exception as e:
        logger.error("Intelligence health check failed", error=str(e))
        
        return IntelligenceHealthResponse(
            status="unhealthy",
            services={"error": False},
            last_profile_created=None,
            last_score_calculated=None,
            error_count=999,
            uptime=0.0
        )


# === Background Tasks ===

@error_handler(exceptions=(Exception,))
def update_profile_analytics(profile_id: str, communication_style: str) -> None:
    """Background task to update profile analytics."""
    try:
        logger.info(
            "Updating profile analytics",
            profile_id=profile_id,
            communication_style=communication_style
        )
        # Implementation for analytics update
        # This could include ML model training, pattern analysis, etc.
        
    except Exception as e:
        logger.error("Profile analytics update failed", error=str(e), profile_id=profile_id)


@error_handler(exceptions=(Exception,))
def update_score_analytics(score_id: str, overall_score: float) -> None:
    """Background task to update score analytics."""
    try:
        logger.info(
            "Updating score analytics",
            score_id=score_id,
            overall_score=overall_score
        )
        # Implementation for analytics update
        # This could include success rate tracking, model accuracy, etc.
        
    except Exception as e:
        logger.error("Score analytics update failed", error=str(e), score_id=score_id)