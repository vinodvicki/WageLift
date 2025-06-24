"""
User model for WageLift application.

Handles user authentication, profile information, and relationships.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """
    User model representing application users.
    
    Integrates with Auth0 for authentication while maintaining
    local user profiles and application-specific data.
    """
    
    __tablename__ = "users"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Primary key for the user"
    )
    
    # Auth0 Integration
    auth0_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="Auth0 user identifier"
    )
    
    # Profile Information
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address (from Auth0)"
    )
    
    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="User's full name"
    )
    
    given_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's first name"
    )
    
    family_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's last name"
    )
    
    picture_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="URL to user's profile picture"
    )
    
    # Application-specific fields
    job_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="User's job title"
    )
    
    company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="User's company name"
    )
    
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="User's work location (city, state)"
    )
    
    # Account Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active"
    )
    
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user's email is verified"
    )
    
    # Subscription/Premium features
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether user has premium subscription"
    )
    
    premium_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When premium subscription expires"
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the user was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="When the user was last updated"
    )
    
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user last logged in"
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When the user was soft deleted"
    )
    
    # Relationships
    salary_entries: Mapped[List["SalaryEntry"]] = relationship(
        "SalaryEntry",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="SalaryEntry.effective_date.desc()"
    )
    
    raise_requests: Mapped[List["RaiseRequest"]] = relationship(
        "RaiseRequest",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="RaiseRequest.created_at.desc()"
    )

    gusto_tokens: Mapped[List["GustoToken"]] = relationship(
        "GustoToken",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="GustoToken.created_at.desc()"
    )

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
    
    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        if self.name:
            return self.name
        if self.given_name and self.family_name:
            return f"{self.given_name} {self.family_name}"
        return self.given_name or self.family_name or "Unknown User"
    
    @property
    def is_deleted(self) -> bool:
        """Check if the user is soft deleted."""
        return self.deleted_at is not None
    
    @property
    def is_premium_active(self) -> bool:
        """Check if user has active premium subscription."""
        if not self.is_premium:
            return False
        if self.premium_expires_at is None:
            return True  # Permanent premium
        return self.premium_expires_at > datetime.utcnow()
    
    def soft_delete(self) -> None:
        """Soft delete the user."""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
    
    def restore(self) -> None:
        """Restore a soft deleted user."""
        self.deleted_at = None
        self.is_active = True


class GustoToken(Base):
    """
    Gusto OAuth token storage with encryption.
    
    Stores encrypted access and refresh tokens for Gusto API integration.
    """
    
    __tablename__ = "gusto_tokens"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Primary key for the token"
    )
    
    # Foreign key to user
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to the user who owns this token"
    )
    
    # Encrypted token data
    encrypted_access_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Encrypted Gusto access token"
    )
    
    encrypted_refresh_token: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Encrypted Gusto refresh token"
    )
    
    # Token metadata
    token_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Bearer",
        doc="Token type (usually Bearer)"
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="When the access token expires"
    )
    
    # Encryption key (unique per token for additional security)
    encryption_key: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        doc="Encryption key for this token"
    )
    
    # Gusto-specific metadata
    gusto_company_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Gusto company ID associated with this token"
    )
    
    gusto_employee_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Gusto employee ID for the user"
    )
    
    # OAuth scopes granted
    scopes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="OAuth scopes granted for this token"
    )
    
    # Status tracking
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this token is currently active"
    )
    
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When this token was last used"
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the token was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="When the token was last updated"
    )
    
    # Relationship back to user
    user: Mapped["User"] = relationship(
        "User",
        back_populates="gusto_tokens"
    )

    def __repr__(self) -> str:
        """String representation of the token."""
        return f"<GustoToken(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the access token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def expires_in_seconds(self) -> int:
        """Get seconds until token expires."""
        if self.is_expired:
            return 0
        return int((self.expires_at - datetime.utcnow()).total_seconds())
    
    def mark_used(self) -> None:
        """Mark the token as recently used."""
        self.last_used_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the token."""
        self.is_active = False 