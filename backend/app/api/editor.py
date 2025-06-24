"""
Editor API endpoints for WageLift.

This module provides API endpoints for document editing and management,
including raise letter editing, version control, and collaboration features.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.supabase_service import SupabaseService

router = APIRouter()

# Pydantic models
class DocumentCreate(BaseModel):
    """Model for creating a new document."""
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    content: str = Field(..., description="Document content")
    document_type: str = Field("raise_letter", description="Type of document")
    tags: Optional[List[str]] = Field(None, description="Document tags")
    
class DocumentResponse(BaseModel):
    """Model for document response."""
    id: str
    title: str
    content: str
    document_type: str
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: datetime
    version: int
    
    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    """Model for updating a document."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None)
    tags: Optional[List[str]] = Field(None)

class DocumentVersion(BaseModel):
    """Model for document version."""
    version: int
    content: str
    created_at: datetime
    change_summary: Optional[str]
    
class CollaborationRequest(BaseModel):
    """Model for collaboration request."""
    collaborator_email: str = Field(..., description="Email of collaborator to invite")
    permission_level: str = Field("view", description="Permission level (view, edit, admin)")
    message: Optional[str] = Field(None, description="Optional message to collaborator")

class CommentCreate(BaseModel):
    """Model for creating a comment."""
    content: str = Field(..., min_length=1, description="Comment content")
    selection_start: Optional[int] = Field(None, description="Start position of text selection")
    selection_end: Optional[int] = Field(None, description="End position of text selection")
    
class CommentResponse(BaseModel):
    """Model for comment response."""
    id: str
    content: str
    selection_start: Optional[int]
    selection_end: Optional[int]
    created_at: datetime
    author_name: str
    
    class Config:
        from_attributes = True

# API Endpoints
@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new document.
    """
    try:
        supabase_service = SupabaseService()
        
        # Create document data
        document_data = {
            "user_id": current_user.id,
            "title": document.title,
            "content": document.content,
            "document_type": document.document_type,
            "tags": document.tags,
            "version": 1
        }
        
        # Save document
        saved_document = await supabase_service.create_document(document_data)
        
        if not saved_document:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create document"
            )
        
        return DocumentResponse(
            id=saved_document["id"],
            title=saved_document["title"],
            content=saved_document["content"],
            document_type=saved_document["document_type"],
            tags=saved_document.get("tags"),
            created_at=datetime.fromisoformat(saved_document["created_at"]),
            updated_at=datetime.fromisoformat(saved_document["updated_at"]),
            version=saved_document["version"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document: {str(e)}"
        )

@router.get("/documents", response_model=List[DocumentResponse])
async def get_user_documents(
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all documents for the current user.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get user's documents
        documents = await supabase_service.get_user_documents(
            current_user.id, 
            document_type=document_type
        )
        
        return [
            DocumentResponse(
                id=doc["id"],
                title=doc["title"],
                content=doc["content"],
                document_type=doc["document_type"],
                tags=doc.get("tags"),
                created_at=datetime.fromisoformat(doc["created_at"]),
                updated_at=datetime.fromisoformat(doc["updated_at"]),
                version=doc["version"]
            )
            for doc in documents
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific document by ID.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get document
        document = await supabase_service.get_document(document_id, current_user.id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return DocumentResponse(
            id=document["id"],
            title=document["title"],
            content=document["content"],
            document_type=document["document_type"],
            tags=document.get("tags"),
            created_at=datetime.fromisoformat(document["created_at"]),
            updated_at=datetime.fromisoformat(document["updated_at"]),
            version=document["version"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )

@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a specific document.
    """
    try:
        supabase_service = SupabaseService()
        
        # Prepare update data
        update_data = {}
        for field, value in document_update.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        # Update document and increment version
        updated_document = await supabase_service.update_document(
            document_id, current_user.id, update_data
        )
        
        if not updated_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return DocumentResponse(
            id=updated_document["id"],
            title=updated_document["title"],
            content=updated_document["content"],
            document_type=updated_document["document_type"],
            tags=updated_document.get("tags"),
            created_at=datetime.fromisoformat(updated_document["created_at"]),
            updated_at=datetime.fromisoformat(updated_document["updated_at"]),
            version=updated_document["version"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating document: {str(e)}"
        )

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific document.
    """
    try:
        supabase_service = SupabaseService()
        
        # Delete document
        success = await supabase_service.delete_document(document_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )

@router.get("/documents/{document_id}/versions", response_model=List[DocumentVersion])
async def get_document_versions(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all versions of a document.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get document versions
        versions = await supabase_service.get_document_versions(document_id, current_user.id)
        
        return [
            DocumentVersion(
                version=version["version"],
                content=version["content"],
                created_at=datetime.fromisoformat(version["created_at"]),
                change_summary=version.get("change_summary")
            )
            for version in versions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document versions: {str(e)}"
        )

@router.post("/documents/{document_id}/collaborate")
async def invite_collaborator(
    document_id: str,
    collaboration_request: CollaborationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Invite a collaborator to work on a document.
    """
    try:
        supabase_service = SupabaseService()
        
        # Check if document exists and user owns it
        document = await supabase_service.get_document(document_id, current_user.id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Create collaboration invitation
        invitation_data = {
            "document_id": document_id,
            "inviter_id": current_user.id,
            "collaborator_email": collaboration_request.collaborator_email,
            "permission_level": collaboration_request.permission_level,
            "message": collaboration_request.message,
            "status": "pending"
        }
        
        invitation = await supabase_service.create_collaboration_invitation(invitation_data)
        
        if not invitation:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create collaboration invitation"
            )
        
        return {
            "success": True,
            "message": "Collaboration invitation sent",
            "invitation_id": invitation["id"],
            "collaborator_email": collaboration_request.collaborator_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inviting collaborator: {str(e)}"
        )

@router.post("/documents/{document_id}/comments", response_model=CommentResponse)
async def add_comment(
    document_id: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a comment to a document.
    """
    try:
        supabase_service = SupabaseService()
        
        # Check if document exists and user has access
        document = await supabase_service.get_document(document_id, current_user.id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Create comment
        comment_data = {
            "document_id": document_id,
            "user_id": current_user.id,
            "content": comment.content,
            "selection_start": comment.selection_start,
            "selection_end": comment.selection_end
        }
        
        saved_comment = await supabase_service.create_comment(comment_data)
        
        if not saved_comment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
        
        return CommentResponse(
            id=saved_comment["id"],
            content=saved_comment["content"],
            selection_start=saved_comment.get("selection_start"),
            selection_end=saved_comment.get("selection_end"),
            created_at=datetime.fromisoformat(saved_comment["created_at"]),
            author_name=f"{current_user.first_name} {current_user.last_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding comment: {str(e)}"
        )

@router.get("/documents/{document_id}/comments", response_model=List[CommentResponse])
async def get_document_comments(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all comments for a document.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get document comments
        comments = await supabase_service.get_document_comments(document_id, current_user.id)
        
        return [
            CommentResponse(
                id=comment["id"],
                content=comment["content"],
                selection_start=comment.get("selection_start"),
                selection_end=comment.get("selection_end"),
                created_at=datetime.fromisoformat(comment["created_at"]),
                author_name=comment["author_name"]
            )
            for comment in comments
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving comments: {str(e)}"
        )
