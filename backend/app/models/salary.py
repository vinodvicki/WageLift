"""
Salary form data models for WageLift.
Pydantic models for salary data validation and Supabase integration.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


# Enums for predefined values
class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class CompanySize(str, Enum):
    """Company size enumeration."""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class Benefits(str, Enum):
    """Benefits enumeration."""
    HEALTH_INSURANCE = "health_insurance"
    DENTAL_INSURANCE = "dental_insurance"
    VISION_INSURANCE = "vision_insurance"
    RETIREMENT_401K = "retirement_401k"
    PAID_TIME_OFF = "paid_time_off"
    FLEXIBLE_SCHEDULE = "flexible_schedule"
    REMOTE_WORK = "remote_work"
    PROFESSIONAL_DEVELOPMENT = "professional_development"
    STOCK_OPTIONS = "stock_options"
    BONUS_ELIGIBLE = "bonus_eligible"


# Request models
class SalaryFormRequest(BaseModel):
    """
    Salary form submission request model.
    Validates all user input for salary information.
    """
    # Required fields
    current_salary: int = Field(
        ...,
        gt=0,
        le=5000000,
        description="Current annual salary in USD"
    )
    last_raise_date: datetime = Field(
        ...,
        description="Date of last salary raise"
    )
    job_title: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Current job title"
    )
    location: str = Field(
        ...,
        min_length=5,
        max_length=10,
        description="ZIP code for location"
    )
    experience_level: ExperienceLevel = Field(
        ...,
        description="Professional experience level"
    )
    company_size: CompanySize = Field(
        ...,
        description="Size of current company"
    )
    
    # Optional fields
    bonus_amount: Optional[int] = Field(
        None,
        ge=0,
        le=2000000,
        description="Annual bonus amount in USD"
    )
    benefits: Optional[List[Benefits]] = Field(
        default_factory=list,
        description="Selected employee benefits"
    )
    equity_details: Optional[str] = Field(
        None,
        max_length=500,
        description="Equity compensation details (executive level)"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional notes or context"
    )

    @validator('job_title')
    def validate_job_title(cls, v):
        """Validate job title format."""
        if not v or not v.strip():
            raise ValueError('Job title cannot be empty')
        
        # Check for valid characters
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-\./&()]+$', v.strip()):
            raise ValueError('Job title contains invalid characters')
        
        return v.strip()

    @validator('location')
    def validate_zip_code(cls, v):
        """Validate ZIP code format."""
        import re
        if not re.match(r'^\d{5}(-\d{4})?$', v.strip()):
            raise ValueError('Invalid ZIP code format')
        return v.strip()

    @validator('last_raise_date')
    def validate_raise_date(cls, v):
        """Validate last raise date is not in future and not too old."""
        if v > datetime.now():
            raise ValueError('Last raise date cannot be in the future')
        
        # Check if more than 5 years ago
        five_years_ago = datetime.now().replace(year=datetime.now().year - 5)
        if v < five_years_ago:
            raise ValueError('Last raise date cannot be more than 5 years ago')
        
        return v

    @validator('current_salary')
    def validate_salary_range(cls, v):
        """Validate salary is in reasonable range."""
        if v < 20000:
            # Allow but could trigger warnings in business logic
            pass
        if v > 2000000:
            # Allow but could trigger warnings in business logic
            pass
        return v

    def validate_salary_experience_alignment(self):
        """Cross-validate salary against experience level for business logic."""
        # This can be called in business logic layer for warnings/analytics
        # Not enforced as strict validation to allow flexibility
        
        salary_ranges = {
            ExperienceLevel.ENTRY: (35000, 80000),
            ExperienceLevel.MID: (60000, 120000), 
            ExperienceLevel.SENIOR: (90000, 180000),
            ExperienceLevel.LEAD: (120000, 250000),
            ExperienceLevel.EXECUTIVE: (150000, 500000),
        }
        
        range_min, range_max = salary_ranges.get(self.experience_level, (0, float('inf')))
        
        if self.current_salary < range_min or self.current_salary > range_max:
            return False, f"Salary ${self.current_salary:,} may be outside typical range ${range_min:,}-${range_max:,} for {self.experience_level} level"
        
        return True, "Salary aligns with experience level"

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "current_salary": 85000,
                "last_raise_date": "2023-01-15T00:00:00",
                "job_title": "Software Engineer",
                "location": "94102",
                "experience_level": "mid",
                "company_size": "medium",
                "bonus_amount": 5000,
                "benefits": ["health_insurance", "retirement_401k", "remote_work"],
                "notes": "Looking to understand market rate for my role"
            }
        }


# Database model for Supabase
class SalaryData(BaseModel):
    """
    Salary data model for database storage.
    Includes additional fields for tracking and analysis.
    """
    # Primary fields from form
    current_salary: int
    last_raise_date: datetime
    job_title: str
    location: str
    experience_level: ExperienceLevel
    company_size: CompanySize
    bonus_amount: Optional[int] = None
    benefits: Optional[List[Benefits]] = None
    equity_details: Optional[str] = None
    notes: Optional[str] = None
    
    # Metadata fields
    user_id: str = Field(..., description="Auth0 user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Analysis fields (calculated)
    annual_total_compensation: Optional[int] = None
    benefits_value_estimate: Optional[int] = None
    last_analysis_date: Optional[datetime] = None
    
    # Tracking fields
    submission_ip: Optional[str] = None
    form_version: str = Field(default="1.0")
    data_source: str = Field(default="web_form")

    @validator('annual_total_compensation', pre=True, always=True)
    def calculate_total_compensation(cls, v, values):
        """Calculate total annual compensation."""
        base_salary = values.get('current_salary', 0)
        bonus = values.get('bonus_amount', 0) or 0
        
        # Basic calculation - could be enhanced with benefits valuation
        return base_salary + bonus

    class Config:
        """Pydantic configuration for database model."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Response models
class SalaryFormResponse(BaseModel):
    """
    Response model for successful salary form submission.
    """
    success: bool = True
    message: str = "Salary data submitted successfully"
    data_id: Optional[str] = None
    submission_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Analysis preview (if available)
    analysis_preview: Optional[dict] = None
    
    # Next steps for user
    next_steps: List[str] = Field(default_factory=lambda: [
        "View your salary analysis dashboard",
        "Compare with market benchmarks",
        "Generate raise request documentation"
    ])

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SalaryFormErrorResponse(BaseModel):
    """
    Error response model for form submission failures.
    """
    success: bool = False
    message: str
    errors: Optional[dict] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # User-friendly suggestions
    suggestions: Optional[List[str]] = None

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Validation utilities
class SalaryValidationResult(BaseModel):
    """
    Result model for salary data validation and analysis.
    """
    is_valid: bool
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    market_analysis: Optional[dict] = None
    confidence_score: Optional[float] = None


# Update models
class SalaryUpdateRequest(BaseModel):
    """
    Model for updating existing salary data.
    """
    current_salary: Optional[int] = None
    last_raise_date: Optional[datetime] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    company_size: Optional[CompanySize] = None
    bonus_amount: Optional[int] = None
    benefits: Optional[List[Benefits]] = None
    equity_details: Optional[str] = None
    notes: Optional[str] = None
    
    # Only update fields that are provided
    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Prevent extra fields


# Analysis models
class SalaryAnalysisRequest(BaseModel):
    """
    Request model for salary analysis operations.
    """
    include_market_data: bool = True
    include_inflation_analysis: bool = True
    include_raise_recommendations: bool = True
    analysis_period_months: int = Field(default=12, ge=6, le=60)


class SalaryAnalysisResponse(BaseModel):
    """
    Response model for salary analysis results.
    """
    user_salary_data: SalaryData
    market_percentile: Optional[float] = None
    inflation_impact: Optional[dict] = None
    raise_recommendations: Optional[dict] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 

# Alias for backward compatibility
SalaryEntry = SalaryData 