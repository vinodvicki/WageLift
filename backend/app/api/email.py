"""
Email API endpoints for WageLift.

This module provides API endpoints for email services,
including sending raise letters and notifications.
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.email_service import EmailService
from app.services.pdf_service import PDFService
from app.services.supabase_service import SupabaseService

router = APIRouter()

# Pydantic models
class EmailSendRequest(BaseModel):
    """Model for sending email request."""
    recipient_email: EmailStr = Field(..., description="Recipient's email address")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    content: str = Field(..., min_length=1, description="Email content/body")
    content_type: str = Field("html", description="Content type (html or plain)")
    attach_pdf: bool = Field(False, description="Whether to attach content as PDF")
    
class RaiseLetterEmailRequest(BaseModel):
    """Model for sending raise letter via email."""
    letter_id: str = Field(..., description="ID of the raise letter to send")
    recipient_email: EmailStr = Field(..., description="Recipient's email address")
    subject: Optional[str] = Field(None, description="Custom subject line")
    include_pdf: bool = Field(True, description="Include letter as PDF attachment")
    personal_message: Optional[str] = Field(None, description="Personal message to include")

class EmailResponse(BaseModel):
    """Model for email response."""
    success: bool
    message: str
    email_id: Optional[str] = None
    sent_at: datetime
    recipient: str
    
class EmailStatusResponse(BaseModel):
    """Model for email status response."""
    email_id: str
    status: str
    sent_at: datetime
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None

# API Endpoints
@router.post("/send", response_model=EmailResponse)
async def send_email(
    email_request: EmailSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a general email with optional PDF attachment.
    """
    try:
        email_service = EmailService()
        
        # Prepare email data
        email_data = {
            "to_email": email_request.recipient_email,
            "subject": email_request.subject,
            "content": email_request.content,
            "content_type": email_request.content_type,
            "from_name": f"{current_user.first_name} {current_user.last_name}",
            "from_email": current_user.email
        }
        
        # Generate PDF if requested
        pdf_attachment = None
        if email_request.attach_pdf:
            pdf_service = PDFService()
            pdf_content = await pdf_service.generate_pdf_from_html(
                email_request.content,
                filename=f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            pdf_attachment = {
                "content": pdf_content,
                "filename": f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "content_type": "application/pdf"
            }
        
        # Send email
        result = await email_service.send_email(
            email_data,
            attachments=[pdf_attachment] if pdf_attachment else None
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send email: {result.get('error', 'Unknown error')}"
            )
        
        return EmailResponse(
            success=True,
            message="Email sent successfully",
            email_id=result.get("email_id"),
            sent_at=datetime.now(),
            recipient=email_request.recipient_email
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )

@router.post("/send-raise-letter", response_model=EmailResponse)
async def send_raise_letter_email(
    email_request: RaiseLetterEmailRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a raise letter via email with PDF attachment.
    """
    try:
        email_service = EmailService()
        supabase_service = SupabaseService()
        
        # Get the raise letter
        letter = await supabase_service.get_raise_letter(
            email_request.letter_id, 
            current_user.id
        )
        
        if not letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Raise letter not found"
            )
        
        # Prepare email content
        subject = email_request.subject or letter.get("subject", "Salary Adjustment Request")
        
        email_content = ""
        if email_request.personal_message:
            email_content += f"<p>{email_request.personal_message}</p><br>"
        
        email_content += f"<div>{letter['content']}</div>"
        
        # Prepare email data
        email_data = {
            "to_email": email_request.recipient_email,
            "subject": subject,
            "content": email_content,
            "content_type": "html",
            "from_name": f"{current_user.first_name} {current_user.last_name}",
            "from_email": current_user.email
        }
        
        # Generate PDF attachment if requested
        attachments = []
        if email_request.include_pdf:
            pdf_service = PDFService()
            pdf_content = await pdf_service.generate_pdf_from_html(
                letter['content'],
                filename=f"raise_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            attachments.append({
                "content": pdf_content,
                "filename": f"raise_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "content_type": "application/pdf"
            })
        
        # Send email
        result = await email_service.send_email(email_data, attachments)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send raise letter: {result.get('error', 'Unknown error')}"
            )
        
        # Log the email send event
        await supabase_service.log_email_event({
            "user_id": current_user.id,
            "letter_id": email_request.letter_id,
            "recipient_email": email_request.recipient_email,
            "subject": subject,
            "sent_at": datetime.now().isoformat(),
            "email_id": result.get("email_id")
        })
        
        return EmailResponse(
            success=True,
            message="Raise letter sent successfully",
            email_id=result.get("email_id"),
            sent_at=datetime.now(),
            recipient=email_request.recipient_email
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending raise letter: {str(e)}"
        )

@router.get("/status/{email_id}", response_model=EmailStatusResponse)
async def get_email_status(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a sent email.
    """
    try:
        email_service = EmailService()
        
        # Get email status
        status_data = await email_service.get_email_status(email_id)
        
        if not status_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        return EmailStatusResponse(
            email_id=email_id,
            status=status_data["status"],
            sent_at=datetime.fromisoformat(status_data["sent_at"]),
            delivered_at=datetime.fromisoformat(status_data["delivered_at"]) if status_data.get("delivered_at") else None,
            opened_at=datetime.fromisoformat(status_data["opened_at"]) if status_data.get("opened_at") else None,
            clicked_at=datetime.fromisoformat(status_data["clicked_at"]) if status_data.get("clicked_at") else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving email status: {str(e)}"
        )

@router.get("/history", response_model=List[EmailStatusResponse])
async def get_email_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get email history for the current user.
    """
    try:
        supabase_service = SupabaseService()
        
        # Get user's email history
        email_history = await supabase_service.get_user_email_history(current_user.id)
        
        return [
            EmailStatusResponse(
                email_id=email["email_id"],
                status=email["status"],
                sent_at=datetime.fromisoformat(email["sent_at"]),
                delivered_at=datetime.fromisoformat(email["delivered_at"]) if email.get("delivered_at") else None,
                opened_at=datetime.fromisoformat(email["opened_at"]) if email.get("opened_at") else None,
                clicked_at=datetime.fromisoformat(email["clicked_at"]) if email.get("clicked_at") else None
            )
            for email in email_history
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving email history: {str(e)}"
        )

@router.post("/test")
async def send_test_email(
    recipient_email: EmailStr,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a test email to verify email service functionality.
    """
    try:
        email_service = EmailService()
        
        # Prepare test email
        email_data = {
            "to_email": recipient_email,
            "subject": "WageLift Email Service Test",
            "content": f"""
            <html>
                <body>
                    <h2>WageLift Email Service Test</h2>
                    <p>Hello {current_user.first_name},</p>
                    <p>This is a test email to verify that the WageLift email service is working correctly.</p>
                    <p>If you receive this email, the service is functioning properly.</p>
                    <br>
                    <p>Best regards,<br>The WageLift Team</p>
                </body>
            </html>
            """,
            "content_type": "html",
            "from_name": "WageLift System",
            "from_email": "noreply@wagelift.com"
        }
        
        # Send test email
        result = await email_service.send_email(email_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send test email: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "message": "Test email sent successfully",
            "recipient": recipient_email,
            "sent_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending test email: {str(e)}"
        ) 