"""
Benchmark model for WageLift application.

Stores salary benchmark data for different roles, locations, and companies.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class Benchmark(Base):
    """
    Benchmark model representing salary benchmark data.
    
    Used to provide market salary comparisons for raise requests
    and salary analysis.
    """
    
    __tablename__ = "benchmarks"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Primary key for the benchmark"
    )
    
    # Job Information
    job_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Job title for this benchmark"
    )
    
    job_level: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Job level (junior, mid, senior, staff, principal, etc.)"
    )
    
    job_family: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Job family/category (engineering, marketing, sales, etc.)"
    )
    
    # Location Information
    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Geographic location (city, state/region, country)"
    )
    
    location_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="metro",
        doc="Location type (metro, state, country, remote)"
    )
    
    # Company Information
    company_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Company name (if company-specific benchmark)"
    )
    
    company_size: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Company size category (startup, small, medium, large, enterprise)"
    )
    
    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Industry category"
    )
    
    # Salary Data
    base_salary_min: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        doc="Minimum base salary for this benchmark"
    )
    
    base_salary_max: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        doc="Maximum base salary for this benchmark"
    )
    
    base_salary_median: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Median base salary for this benchmark"
    )
    
    base_salary_mean: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Mean base salary for this benchmark"
    )
    
    # Total Compensation
    total_comp_min: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Minimum total compensation (including bonus, equity)"
    )
    
    total_comp_max: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Maximum total compensation (including bonus, equity)"
    )
    
    total_comp_median: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Median total compensation"
    )
    
    total_comp_mean: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Mean total compensation"
    )
    
    # Metadata
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        doc="Currency code (ISO 4217)"
    )
    
    experience_years_min: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        doc="Minimum years of experience"
    )
    
    experience_years_max: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        doc="Maximum years of experience"
    )
    
    sample_size: Mapped[Optional[int]] = mapped_column(
        nullable=True,
        doc="Number of data points used for this benchmark"
    )
    
    # Data Source
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Source of benchmark data (glassdoor, levels.fyi, payscale, etc.)"
    )
    
    source_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="URL to the source data"
    )
    
    data_collection_method: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="How the data was collected (survey, scraping, api, etc.)"
    )
    
    # Date Information
    effective_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Date when this benchmark data became effective"
    )
    
    expiration_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Date when this benchmark data expires"
    )
    
    # Quality Indicators
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=3, scale=2),
        nullable=True,
        doc="Confidence score (0.0 to 1.0) for this benchmark"
    )
    
    is_verified: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        doc="Whether this benchmark has been verified"
    )
    
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        doc="Whether this benchmark is currently active"
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the benchmark was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="When the benchmark was last updated"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "base_salary_min > 0",
            name="check_positive_base_salary_min"
        ),
        CheckConstraint(
            "base_salary_max > 0",
            name="check_positive_base_salary_max"
        ),
        CheckConstraint(
            "base_salary_max >= base_salary_min",
            name="check_base_salary_range"
        ),
        CheckConstraint(
            "base_salary_median IS NULL OR (base_salary_median >= base_salary_min AND base_salary_median <= base_salary_max)",
            name="check_base_salary_median_range"
        ),
        CheckConstraint(
            "total_comp_min IS NULL OR total_comp_min >= 0",
            name="check_non_negative_total_comp_min"
        ),
        CheckConstraint(
            "total_comp_max IS NULL OR total_comp_max >= 0",
            name="check_non_negative_total_comp_max"
        ),
        CheckConstraint(
            "total_comp_max IS NULL OR total_comp_min IS NULL OR total_comp_max >= total_comp_min",
            name="check_total_comp_range"
        ),
        CheckConstraint(
            "experience_years_min IS NULL OR experience_years_min >= 0",
            name="check_non_negative_exp_min"
        ),
        CheckConstraint(
            "experience_years_max IS NULL OR experience_years_max >= 0",
            name="check_non_negative_exp_max"
        ),
        CheckConstraint(
            "experience_years_max IS NULL OR experience_years_min IS NULL OR experience_years_max >= experience_years_min",
            name="check_experience_range"
        ),
        CheckConstraint(
            "sample_size IS NULL OR sample_size > 0",
            name="check_positive_sample_size"
        ),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)",
            name="check_confidence_score_range"
        ),
        CheckConstraint(
            "expiration_date IS NULL OR expiration_date >= effective_date",
            name="check_valid_date_range"
        ),
        CheckConstraint(
            "location_type IN ('metro', 'state', 'country', 'remote')",
            name="check_valid_location_type"
        ),
        CheckConstraint(
            "company_size IS NULL OR company_size IN ('startup', 'small', 'medium', 'large', 'enterprise')",
            name="check_valid_company_size"
        ),
    )

    def __repr__(self) -> str:
        """String representation of the benchmark."""
        return (
            f"<Benchmark(id={self.id}, job_title={self.job_title}, "
            f"location={self.location}, salary_range=${self.base_salary_min}-${self.base_salary_max})>"
        )
    
    @property
    def is_current(self) -> bool:
        """Check if this benchmark is currently valid."""
        if not self.is_active:
            return False
        if self.expiration_date is None:
            return True
        return self.expiration_date > date.today()
    
    @property
    def salary_range_midpoint(self) -> Decimal:
        """Calculate the midpoint of the salary range."""
        return (self.base_salary_min + self.base_salary_max) / 2
    
    @property
    def total_comp_range_midpoint(self) -> Optional[Decimal]:
        """Calculate the midpoint of the total compensation range."""
        if self.total_comp_min is None or self.total_comp_max is None:
            return None
        return (self.total_comp_min + self.total_comp_max) / 2
    
    def matches_criteria(
        self,
        job_title: Optional[str] = None,
        location: Optional[str] = None,
        experience_years: Optional[int] = None,
        company_size: Optional[str] = None,
        industry: Optional[str] = None
    ) -> bool:
        """Check if this benchmark matches the given criteria."""
        if job_title and job_title.lower() not in self.job_title.lower():
            return False
        
        if location and location.lower() not in self.location.lower():
            return False
        
        if experience_years is not None:
            if self.experience_years_min is not None and experience_years < self.experience_years_min:
                return False
            if self.experience_years_max is not None and experience_years > self.experience_years_max:
                return False
        
        if company_size and self.company_size and company_size != self.company_size:
            return False
        
        if industry and self.industry and industry.lower() not in self.industry.lower():
            return False
        
        return True 