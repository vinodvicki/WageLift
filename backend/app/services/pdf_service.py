"""
PDF Generation Service for WageLift
Converts raise request letters to professional PDF documents
"""

import io
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas

from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFServiceError(Exception):
    """Custom exception for PDF service errors"""
    pass


class PDFService:
    """
    PDF generation service for professional raise request letters
    
    Creates formatted PDF documents with proper business letter styling,
    headers, footers, and professional layout.
    """
    
    def __init__(self):
        """Initialize PDF service with styling configuration"""
        self.page_size = letter
        self.margin = 0.75 * inch
        self.styles = self._create_styles()
        
    def _create_styles(self) -> dict:
        """Create custom paragraph styles for PDF generation"""
        base_styles = getSampleStyleSheet()
        
        # Custom styles for raise letter
        styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                textColor=colors.HexColor('#1f2937'),
                alignment=1  # Center alignment
            ),
            'header': ParagraphStyle(
                'CustomHeader',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                textColor=colors.HexColor('#374151')
            ),
            'body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=12,
                leading=14,
                textColor=colors.HexColor('#1f2937'),
                alignment=0  # Left alignment
            ),
            'signature': ParagraphStyle(
                'CustomSignature',
                parent=base_styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                textColor=colors.HexColor('#1f2937'),
                leftIndent=0
            ),
            'footer': ParagraphStyle(
                'CustomFooter',
                parent=base_styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#6b7280'),
                alignment=1  # Center alignment
            ),
            'date': ParagraphStyle(
                'CustomDate',
                parent=base_styles['Normal'],
                fontSize=10,
                spaceAfter=12,
                textColor=colors.HexColor('#374151'),
                alignment=2  # Right alignment
            )
        }
        
        return styles
    
    async def generate_letter_pdf(
        self,
        letter_content: str,
        subject_line: str,
        user_name: str,
        custom_header: Optional[str] = None
    ) -> bytes:
        """
        Generate a professional PDF from letter content
        
        Args:
            letter_content: The main letter text
            subject_line: Email subject line for the document
            user_name: Name of the person sending the letter
            custom_header: Optional custom header text
            
        Returns:
            PDF content as bytes
            
        Raises:
            PDFServiceError: If PDF generation fails
        """
        try:
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=self.page_size,
                rightMargin=self.margin,
                leftMargin=self.margin,
                topMargin=self.margin,
                bottomMargin=self.margin,
                title=f"Salary Adjustment Request - {user_name}",
                author=user_name,
                subject=subject_line,
                creator="WageLift Platform"
            )
            
            # Build document content
            story = []
            
            # Add header
            story.extend(self._create_header(custom_header))
            
            # Add title
            story.append(Paragraph(subject_line, self.styles['title']))
            story.append(Spacer(1, 20))
            
            # Add date
            current_date = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(current_date, self.styles['date']))
            story.append(Spacer(1, 20))
            
            # Add letter content
            story.extend(self._format_letter_content(letter_content))
            
            # Add footer
            story.extend(self._create_footer())
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_page_decorations, onLaterPages=self._add_page_decorations)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"PDF generated successfully for {user_name}, size: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise PDFServiceError(f"Failed to generate PDF: {str(e)}")
    
    def _create_header(self, custom_header: Optional[str] = None) -> list:
        """Create document header"""
        header_elements = []
        
        if custom_header:
            header_elements.append(Paragraph(custom_header, self.styles['header']))
            header_elements.append(Spacer(1, 12))
        
        # Add WageLift branding
        branding = "Generated by WageLift - AI-Powered Salary Analysis Platform"
        header_elements.append(Paragraph(branding, self.styles['footer']))
        header_elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        header_elements.append(Spacer(1, 20))
        
        return header_elements
    
    def _format_letter_content(self, content: str) -> list:
        """Format letter content into PDF paragraphs"""
        elements = []
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Clean up the paragraph
                clean_paragraph = paragraph.strip().replace('\n', ' ')
                
                # Detect if this is a signature block
                if any(word in clean_paragraph.lower() for word in ['sincerely', 'best regards', 'respectfully']):
                    elements.append(Spacer(1, 20))
                    elements.append(Paragraph(clean_paragraph, self.styles['signature']))
                else:
                    elements.append(Paragraph(clean_paragraph, self.styles['body']))
                
                elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_footer(self) -> list:
        """Create document footer"""
        footer_elements = []
        
        footer_elements.append(Spacer(1, 30))
        footer_elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
        footer_elements.append(Spacer(1, 12))
        
        # Footer text
        footer_text = (
            "This document was generated using WageLift's AI-powered salary analysis platform. "
            "Data sourced from the U.S. Bureau of Labor Statistics and CareerOneStop API. "
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}."
        )
        
        footer_elements.append(Paragraph(footer_text, self.styles['footer']))
        
        return footer_elements
    
    def _add_page_decorations(self, canvas, doc):
        """Add page decorations like page numbers"""
        canvas.saveState()
        
        # Add page number
        page_num = canvas.getPageNumber()
        page_text = f"Page {page_num}"
        
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawRightString(
            doc.pagesize[0] - doc.rightMargin,
            doc.bottomMargin / 2,
            page_text
        )
        
        canvas.restoreState()
    
    async def validate_pdf_service(self) -> bool:
        """Validate PDF service functionality"""
        try:
            # Test basic PDF generation
            test_content = "This is a test letter content for PDF generation validation."
            test_pdf = await self.generate_letter_pdf(
                test_content,
                "Test Subject",
                "Test User"
            )
            
            # Verify PDF was generated
            if len(test_pdf) > 1000:  # Basic size check
                logger.info("PDF service validation successful")
                return True
            else:
                logger.error("PDF service validation failed: Generated PDF too small")
                return False
                
        except Exception as e:
            logger.error(f"PDF service validation failed: {e}")
            return False 