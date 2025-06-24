"""
Database models for the editor functionality.
Handles raise letter documents and version history.
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..core.database import Base

class RaiseLetter(Base):
    """
    Main table for storing raise letter documents.
    """
    __tablename__ = "raise_letters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, nullable=False, index=True)  # Auth0 user ID
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # HTML content
    document_metadata = Column(JSON, nullable=False)  # Employee info, company details, etc.
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship to versions
    versions = relationship("RaiseLetterVersion", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RaiseLetter(id={self.id}, title='{self.title}', user_id='{self.user_id}')>"

class RaiseLetterVersion(Base):
    """
    Version history for raise letter documents.
    Stores previous versions when documents are updated.
    """
    __tablename__ = "raise_letter_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("raise_letters.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    document_metadata = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    change_summary = Column(Text, nullable=True)  # Optional summary of changes

    # Relationship to main document
    document = relationship("RaiseLetter", back_populates="versions")

    def __repr__(self):
        return f"<RaiseLetterVersion(id={self.id}, document_id={self.document_id}, version={self.version_number})>"

class RaiseLetterTemplate(Base):
    """
    Template storage for commonly used raise letter formats.
    """
    __tablename__ = "raise_letter_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)  # HTML template
    category = Column(String(100), nullable=True)  # e.g., "professional", "confident", "collaborative"
    is_public = Column(Boolean, default=False, nullable=False)  # Whether template is available to all users
    created_by = Column(String, nullable=True)  # User ID who created the template
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_modified = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)  # Track template popularity

    def __repr__(self):
        return f"<RaiseLetterTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"

class RaiseLetterShare(Base):
    """
    Sharing functionality for raise letters.
    Allows users to share documents with specific people or generate public links.
    """
    __tablename__ = "raise_letter_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("raise_letters.id"), nullable=False, index=True)
    share_token = Column(String(255), unique=True, nullable=False, index=True)  # Unique share token
    shared_by = Column(String, nullable=False)  # User ID who shared
    shared_with = Column(String, nullable=True)  # Specific user ID (null for public links)
    permissions = Column(String(50), default="read", nullable=False)  # "read", "comment", "edit"
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship to document
    document = relationship("RaiseLetter")

    def __repr__(self):
        return f"<RaiseLetterShare(id={self.id}, document_id={self.document_id}, permissions='{self.permissions}')>" 