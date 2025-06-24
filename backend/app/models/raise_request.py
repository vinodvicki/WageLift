"""
RaiseRequest model for WageLift application.

Handles salary raise requests with justification, status tracking, and outcomes.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class RaiseRequest(Base):
    """
    RaiseRequest model representing salary increase requests.
    
    Tracks the entire lifecycle of raise requests from creation
    to resolution with comprehensive justification data.
    """
    
    __tablename__ = "raise_requests"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Primary key for the raise request"
    )
    
    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the user making the request"
    )
    
    current_salary_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("salary_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the current salary entry"
    )
    
    # Request Details
    requested_salary: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=False,
        doc="Requested annual salary amount"
    )
    
    requested_increase_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Calculated increase amount (can be auto-calculated)"
    )
    
    requested_increase_percentage: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
        doc="Calculated increase percentage (can be auto-calculated)"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        doc="Currency code (ISO 4217)"
    )
    
    # Justification Data
    inflation_impact: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=5, scale=2),
        nullable=True,
        doc="Calculated inflation impact percentage"
    )
    
    purchasing_power_loss: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Calculated purchasing power loss in currency"
    )
    
    market_benchmark_data: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="JSON string containing market benchmark analysis"
    )
    
    performance_justification: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User-provided performance justification"
    )
    
    additional_justification: Mapped[Optional[str]] = mapped_column(
        Text,  
        nullable=True,
        doc="Additional justification provided by user"
    )
    
    # Generated Content
    ai_generated_letter: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="AI-generated raise request letter"
    )
    
    ai_talking_points: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="AI-generated talking points for conversation"
    )
    
    # Request Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
        index=True,
        doc="Current status of the raise request"
    )
    
    submission_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="How the request was submitted (email, meeting, formal_review, etc.)"
    )
    
    # Outcome Tracking
    manager_response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Manager's response to the request"
    )
    
    outcome_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Final outcome (approved, denied, counter_offer, pending)"
    )
    
    approved_salary: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Approved salary amount (if different from requested)"
    )
    
    effective_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the approved raise becomes effective"
    )
    
    counter_offer_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=12, scale=2),
        nullable=True,
        doc="Counter offer amount if applicable"
    )
    
    denial_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Reason provided for denial"
    )
    
    # Timeline
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the request was submitted to manager"
    )
    
    responded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the manager responded"
    )
    
    # Follow-up
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Scheduled follow-up date"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Additional notes and updates"
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the raise request was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="When the raise request was last updated"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="raise_requests"
    )
    
    current_salary: Mapped["SalaryEntry"] = relationship(
        "SalaryEntry",
        back_populates="raise_requests"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "requested_salary > 0",
            name="check_positive_requested_salary"
        ),
        CheckConstraint(
            "requested_increase_amount IS NULL OR requested_increase_amount >= 0",
            name="check_non_negative_increase_amount"
        ),
        CheckConstraint(
            "requested_increase_percentage IS NULL OR requested_increase_percentage >= 0",
            name="check_non_negative_increase_percentage"
        ),
        CheckConstraint(
            "approved_salary IS NULL OR approved_salary > 0",
            name="check_positive_approved_salary"
        ),
        CheckConstraint(
            "counter_offer_amount IS NULL OR counter_offer_amount > 0",
            name="check_positive_counter_offer"
        ),
        CheckConstraint(
            "status IN ('draft', 'in_progress', 'submitted', 'under_review', 'completed', 'cancelled')",
            name="check_valid_status"
        ),
        CheckConstraint(
            "outcome_status IS NULL OR outcome_status IN ('approved', 'denied', 'counter_offer', 'pending', 'withdrawn')",
            name="check_valid_outcome_status"
        ),
        CheckConstraint(
            "submission_method IS NULL OR submission_method IN ('email', 'meeting', 'formal_review', 'phone', 'slack', 'other')",
            name="check_valid_submission_method"
        ),
        CheckConstraint(
            "responded_at IS NULL OR submitted_at IS NULL OR responded_at >= submitted_at",
            name="check_valid_response_timeline"
        ),
    )

    def __repr__(self) -> str:
        """String representation of the raise request."""
        return (
            f"<RaiseRequest(id={self.id}, user_id={self.user_id}, "
            f"requested_salary=${self.requested_salary}, status={self.status})>"
        )
    
    @property
    def is_active(self) -> bool:
        """Check if this raise request is currently active."""
        return self.status not in ['completed', 'cancelled']
    
    @property
    def has_outcome(self) -> bool:
        """Check if this raise request has a final outcome."""
        return self.outcome_status is not None
    
    @property
    def is_successful(self) -> bool:
        """Check if this raise request was successful."""
        return self.outcome_status in ['approved', 'counter_offer']
    
    @property
    def days_since_submission(self) -> Optional[int]:
        """Calculate days since submission."""
        if self.submitted_at is None:
            return None
        return (datetime.utcnow() - self.submitted_at).days
    
    @property
    def days_to_follow_up(self) -> Optional[int]:
        """Calculate days until follow-up."""
        if self.follow_up_date is None:
            return None
        return (self.follow_up_date - datetime.utcnow()).days
    
    def calculate_increase_metrics(self, current_salary: Decimal) -> None:
        """Calculate increase amount and percentage based on current salary."""
        if current_salary > 0:
            self.requested_increase_amount = self.requested_salary - current_salary
            self.requested_increase_percentage = (
                (self.requested_salary - current_salary) / current_salary
            ) * 100
    
    def set_outcome(
        self,
        outcome_status: str,
        approved_salary: Optional[Decimal] = None,
        counter_offer_amount: Optional[Decimal] = None,
        denial_reason: Optional[str] = None,
        effective_date: Optional[datetime] = None
    ) -> None:
        """Set the outcome of the raise request."""
        self.outcome_status = outcome_status
        self.responded_at = datetime.utcnow()
        
        if outcome_status == "approved":
            self.approved_salary = approved_salary or self.requested_salary
            self.effective_date = effective_date
            self.status = "completed"
        elif outcome_status == "counter_offer":
            self.counter_offer_amount = counter_offer_amount
        elif outcome_status == "denied":
            self.denial_reason = denial_reason
            self.status = "completed" 