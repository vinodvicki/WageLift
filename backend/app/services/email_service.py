"""
Email Service for WageLift
Handles sending raise request letters via email with PDF attachments
"""

import asyncio
import smtplib
import ssl
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

import aiofiles
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel, EmailStr, Field

from app.core.config import settings
from app.core.logging import get_logger
from app.services.pdf_service import PDFService
from app.services.openai_service import RaiseLetterResponse

logger = get_logger(__name__)


class EmailProvider(str, Enum):
    """Available email providers"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "aws_ses"


class EmailPriority(str, Enum):
    """Email priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass
class EmailAttachment:
    """Email attachment data"""
    filename: str
    content: bytes
    content_type: str = "application/pdf"


@dataclass
class EmailRecipient:
    """Email recipient information"""
    email: str
    name: Optional[str] = None
    type: str = "to"  # to, cc, bcc


class EmailRequest(BaseModel):
    """Email sending request model"""
    recipients: List[EmailRecipient]
    subject: str
    body_text: str
    body_html: Optional[str] = None
    attachments: List[EmailAttachment] = Field(default_factory=list)
    priority: EmailPriority = EmailPriority.NORMAL
    reply_to: Optional[str] = None
    sender_name: Optional[str] = None
    tracking_enabled: bool = True


class EmailResponse(BaseModel):
    """Email sending response model"""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: datetime
    provider_used: EmailProvider
    recipients_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RaiseLetterEmailRequest(BaseModel):
    """Specific request for sending raise letters"""
    user_email: str
    user_name: str
    manager_email: str
    manager_name: Optional[str] = None
    letter_content: str
    subject_line: str
    include_pdf: bool = True
    cc_user: bool = True
    custom_message: Optional[str] = None


class EmailServiceError(Exception):
    """Custom exception for email service errors"""
    pass


class EmailService:
    """
    Comprehensive email service for WageLift
    
    Supports multiple providers and handles raise letter delivery
    with PDF attachments and professional templates.
    """
    
    def __init__(self):
        """Initialize email service with configuration"""
        self.provider = self._determine_provider()
        self.pdf_service = PDFService()
        self.template_env = self._setup_templates()
        
        # Email configuration
        self.smtp_config = {
            'hostname': settings.SMTP_HOST,
            'port': settings.SMTP_PORT or 587,
            'username': settings.SMTP_USER,
            'password': settings.SMTP_PASSWORD,
            'use_tls': settings.SMTP_TLS,
        }
        
        self.sender_email = settings.EMAILS_FROM_EMAIL
        self.sender_name = settings.EMAILS_FROM_NAME or "WageLift Platform"
        
    def _determine_provider(self) -> EmailProvider:
        """Determine which email provider to use based on configuration"""
        if settings.SMTP_HOST and settings.SMTP_USER:
            return EmailProvider.SMTP
        else:
            logger.warning("No email provider configured, using SMTP as default")
            return EmailProvider.SMTP
    
    def _setup_templates(self) -> Environment:
        """Setup Jinja2 template environment"""
        template_dir = Path(__file__).parent.parent / "templates" / "email"
        template_dir.mkdir(parents=True, exist_ok=True)
        
        return Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    async def send_raise_letter_email(
        self, 
        request: RaiseLetterEmailRequest,
        letter_response: RaiseLetterResponse
    ) -> EmailResponse:
        """
        Send a raise request letter via email
        
        Args:
            request: Raise letter email request
            letter_response: Generated letter response from OpenAI
            
        Returns:
            Email response with delivery status
            
        Raises:
            EmailServiceError: If email sending fails
        """
        try:
            # Prepare recipients
            recipients = [
                EmailRecipient(
                    email=request.manager_email,
                    name=request.manager_name,
                    type="to"
                )
            ]
            
            # Add user as CC if requested
            if request.cc_user:
                recipients.append(
                    EmailRecipient(
                        email=request.user_email,
                        name=request.user_name,
                        type="cc"
                    )
                )
            
            # Generate email content
            html_body = await self._generate_email_html(request, letter_response)
            text_body = await self._generate_email_text(request, letter_response)
            
            # Generate PDF attachment if requested
            attachments = []
            if request.include_pdf:
                pdf_content = await self.pdf_service.generate_letter_pdf(
                    letter_response.letter_content,
                    request.subject_line,
                    request.user_name
                )
                
                attachments.append(
                    EmailAttachment(
                        filename=f"raise_request_{request.user_name.replace(' ', '_')}.pdf",
                        content=pdf_content,
                        content_type="application/pdf"
                    )
                )
            
            # Create email request
            email_request = EmailRequest(
                recipients=recipients,
                subject=request.subject_line,
                body_text=text_body,
                body_html=html_body,
                attachments=attachments,
                priority=EmailPriority.HIGH,
                sender_name=request.user_name,
                reply_to=request.user_email
            )
            
            # Send email
            response = await self._send_email(email_request)
            
            # Log success
            logger.info(
                f"Raise letter email sent successfully",
                extra={
                    "user_email": request.user_email,
                    "manager_email": request.manager_email,
                    "message_id": response.message_id,
                    "provider": response.provider_used
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to send raise letter email: {e}")
            raise EmailServiceError(f"Email sending failed: {str(e)}")
    
    async def _send_email(self, request: EmailRequest) -> EmailResponse:
        """Send email using configured provider"""
        
        if self.provider == EmailProvider.SMTP:
            return await self._send_smtp_email(request)
        else:
            raise EmailServiceError(f"Provider {self.provider} not implemented")
    
    async def _send_smtp_email(self, request: EmailRequest) -> EmailResponse:
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = request.subject
            msg['From'] = f"{request.sender_name or self.sender_name} <{self.sender_email}>"
            
            # Add recipients
            to_recipients = [r.email for r in request.recipients if r.type == "to"]
            cc_recipients = [r.email for r in request.recipients if r.type == "cc"]
            bcc_recipients = [r.email for r in request.recipients if r.type == "bcc"]
            
            msg['To'] = ', '.join(to_recipients)
            if cc_recipients:
                msg['Cc'] = ', '.join(cc_recipients)
            
            if request.reply_to:
                msg['Reply-To'] = request.reply_to
            
            # Add text body
            text_part = MIMEText(request.body_text, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if request.body_html:
                html_part = MIMEText(request.body_html, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments
            for attachment in request.attachments:
                part = MIMEApplication(
                    attachment.content,
                    _subtype=attachment.content_type.split('/')[-1]
                )
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{attachment.filename}"'
                )
                msg.attach(part)
            
            # Send email
            all_recipients = to_recipients + cc_recipients + bcc_recipients
            
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_config['hostname'],
                port=self.smtp_config['port'],
                username=self.smtp_config['username'],
                password=self.smtp_config['password'],
                use_tls=self.smtp_config['use_tls'],
                recipients=all_recipients
            )
            
            return EmailResponse(
                success=True,
                message_id=msg.get('Message-ID'),
                sent_at=datetime.utcnow(),
                provider_used=EmailProvider.SMTP,
                recipients_count=len(all_recipients),
                metadata={
                    "smtp_host": self.smtp_config['hostname'],
                    "attachments_count": len(request.attachments)
                }
            )
            
        except Exception as e:
            logger.error(f"SMTP email sending failed: {e}")
            return EmailResponse(
                success=False,
                error_message=str(e),
                sent_at=datetime.utcnow(),
                provider_used=EmailProvider.SMTP,
                recipients_count=0
            )
    
    async def _generate_email_html(
        self, 
        request: RaiseLetterEmailRequest,
        letter_response: RaiseLetterResponse
    ) -> str:
        """Generate HTML email body"""
        try:
            template = self.template_env.get_template('raise_letter_email.html')
            return template.render(
                user_name=request.user_name,
                manager_name=request.manager_name or "Manager",
                letter_content=letter_response.letter_content,
                custom_message=request.custom_message,
                include_pdf=request.include_pdf,
                platform_name="WageLift",
                sent_date=datetime.utcnow().strftime("%B %d, %Y")
            )
        except Exception as e:
            logger.warning(f"Failed to generate HTML template: {e}")
            return self._generate_fallback_html(request, letter_response)
    
    async def _generate_email_text(
        self, 
        request: RaiseLetterEmailRequest,
        letter_response: RaiseLetterResponse
    ) -> str:
        """Generate plain text email body"""
        try:
            template = self.template_env.get_template('raise_letter_email.txt')
            return template.render(
                user_name=request.user_name,
                manager_name=request.manager_name or "Manager",
                letter_content=letter_response.letter_content,
                custom_message=request.custom_message,
                include_pdf=request.include_pdf,
                platform_name="WageLift",
                sent_date=datetime.utcnow().strftime("%B %d, %Y")
            )
        except Exception as e:
            logger.warning(f"Failed to generate text template: {e}")
            return self._generate_fallback_text(request, letter_response)
    
    def _generate_fallback_html(
        self, 
        request: RaiseLetterEmailRequest,
        letter_response: RaiseLetterResponse
    ) -> str:
        """Generate fallback HTML email"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Salary Adjustment Request</h2>
                
                <p>Dear {request.manager_name or 'Manager'},</p>
                
                {f'<p><em>{request.custom_message}</em></p>' if request.custom_message else ''}
                
                <div style="background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <pre style="white-space: pre-wrap; font-family: Georgia, serif;">{letter_response.letter_content}</pre>
                </div>
                
                {f'<p><strong>Note:</strong> This email includes a PDF attachment with the formal letter.</p>' if request.include_pdf else ''}
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                
                <p style="font-size: 12px; color: #6b7280;">
                    This letter was generated using WageLift, an AI-powered salary analysis platform.<br>
                    Sent on {datetime.utcnow().strftime("%B %d, %Y")}
                </p>
            </div>
        </body>
        </html>
        """
    
    def _generate_fallback_text(
        self, 
        request: RaiseLetterEmailRequest,
        letter_response: RaiseLetterResponse
    ) -> str:
        """Generate fallback plain text email"""
        text_parts = [
            f"Dear {request.manager_name or 'Manager'},",
            ""
        ]
        
        if request.custom_message:
            text_parts.extend([request.custom_message, ""])
        
        text_parts.extend([
            letter_response.letter_content,
            ""
        ])
        
        if request.include_pdf:
            text_parts.append("Note: This email includes a PDF attachment with the formal letter.")
            text_parts.append("")
        
        text_parts.extend([
            "---",
            f"This letter was generated using WageLift, an AI-powered salary analysis platform.",
            f"Sent on {datetime.utcnow().strftime('%B %d, %Y')}"
        ])
        
        return "\n".join(text_parts)
    
    async def validate_email_configuration(self) -> bool:
        """Validate email service configuration"""
        try:
            if not self.sender_email:
                logger.error("Sender email not configured")
                return False
            
            if self.provider == EmailProvider.SMTP:
                if not all([
                    self.smtp_config['hostname'],
                    self.smtp_config['username'],
                    self.smtp_config['password']
                ]):
                    logger.error("SMTP configuration incomplete")
                    return False
            
            logger.info(f"Email service configuration valid for provider: {self.provider}")
            return True
            
        except Exception as e:
            logger.error(f"Email configuration validation failed: {e}")
            return False
    
    async def send_test_email(self, recipient_email: str) -> EmailResponse:
        """Send a test email to verify configuration"""
        test_request = EmailRequest(
            recipients=[EmailRecipient(email=recipient_email, name="Test User")],
            subject="WageLift Email Service Test",
            body_text="This is a test email from WageLift email service. If you received this, the configuration is working correctly!",
            body_html="<p>This is a test email from <strong>WageLift</strong> email service.</p><p>If you received this, the configuration is working correctly!</p>",
            priority=EmailPriority.LOW
        )
        
        return await self._send_email(test_request) 