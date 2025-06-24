"""
SalaryEntry model for WageLift application.

Tracks user salary information over time with proper validation and constraints.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SalaryEntry(Base):
    """
    SalaryEntry model representing user salary information.
    
    Tracks salary history to calculate inflation impact and
    support raise request calculations.
    """
    
    __tablename__ = "salary_entries"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Primary key for the salary entry"
    )
    
    # Foreign key to User
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the user who owns this salary entry"
    )
    
    # Salary Information
    annual_salary: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        doc="Annual salary amount in USD"
    )
    
    hourly_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=8, scale=2),
        nullable=True,
        doc="Hourly rate if applicable"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        doc="Currency code (ISO 4217)"
    )
    
    # Employment Details
    employment_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="full_time",
        doc="Employment type (full_time, part_time, contract, etc.)"
    )
    
    job_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Job title at the time of this salary"
    )
    
    company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Company name at the time of this salary"
    )
    
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Work location (city, state)"
    )
    
    # Date Information
    effective_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Date when this salary became effective"
    )
    
    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Date when this salary ended (if applicable)"
    )
    
    # Additional Information
    bonus_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Annual bonus amount"
    )
    
    equity_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Annual equity compensation value"
    )
    
    benefits_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Estimated annual value of benefits"
    )
    
    # Data Source
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="manual",
        doc="Source of salary data (manual, payroll_sync, etc.)"
    )
    
    is_verified: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        doc="Whether this salary has been verified"
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the salary entry was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="When the salary entry was last updated"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="salary_entries"
    )
    
    # raise_requests: Mapped[List["RaiseRequest"]] = relationship(
    #     "RaiseRequest",
    #     back_populates="current_salary",
    #     cascade="all, delete-orphan"
    # )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "annual_salary > 0",
            name="check_positive_annual_salary"
        ),
        CheckConstraint(
            "hourly_rate IS NULL OR hourly_rate > 0",
            name="check_positive_hourly_rate"
        ),
        CheckConstraint(
            "bonus_amount IS NULL OR bonus_amount >= 0",
            name="check_non_negative_bonus"
        ),
        CheckConstraint(
            "equity_value IS NULL OR equity_value >= 0",
            name="check_non_negative_equity"
        ),
        CheckConstraint(
            "benefits_value IS NULL OR benefits_value >= 0",
            name="check_non_negative_benefits"
        ),
        CheckConstraint(
            "end_date IS NULL OR end_date >= effective_date",
            name="check_valid_date_range"
        ),
        CheckConstraint(
            "employment_type IN ('full_time', 'part_time', 'contract', 'temporary', 'intern')",
            name="check_valid_employment_type"
        ),
        CheckConstraint(
            "source IN ('manual', 'payroll_sync', 'api_import', 'csv_upload')",
            name="check_valid_source"
        ),
    )

    def __repr__(self) -> str:
        """String representation of the salary entry."""
        return (
            f"<SalaryEntry(id={self.id}, user_id={self.user_id}, "
            f"salary=${self.annual_salary}, effective_date={self.effective_date})>"
        )
    
    @property
    def total_compensation(self) -> Decimal:
        """Calculate total annual compensation including bonuses and equity."""
        total = self.annual_salary
        if self.bonus_amount:
            total += self.bonus_amount
        if self.equity_value:
            total += self.equity_value
        if self.benefits_value:
            total += self.benefits_value
        return total
    
    @property
    def is_current(self) -> bool:
        """Check if this is the current salary (no end date or end date in future)."""
        if self.end_date is None:
            return True
        return self.end_date > date.today()
    
    @property
    def duration_days(self) -> Optional[int]:
        """Calculate the duration of this salary in days."""
        if self.end_date is None:
            return (date.today() - self.effective_date).days
        return (self.end_date - self.effective_date).days
    
    def calculate_monthly_salary(self) -> Decimal:
        """Calculate monthly salary amount."""
        return self.annual_salary / 12
    
    def calculate_biweekly_salary(self) -> Decimal:
        """Calculate biweekly salary amount."""
        return self.annual_salary / 26
    
    def calculate_weekly_salary(self) -> Decimal:
        """Calculate weekly salary amount."""
        return self.annual_salary / 52 