"""
OpenAI Service for GPT-4 Turbo Integration

Provides AI-powered raise letter generation using OpenAI's GPT-4 Turbo model
with comprehensive prompt engineering and data integration capabilities.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.salary_entry import SalaryEntry
from app.models.benchmark import Benchmark

logger = logging.getLogger(__name__)

class LetterTone(str, Enum):
    """Available tones for raise letter generation"""
    PROFESSIONAL = "professional"
    CONFIDENT = "confident"
    COLLABORATIVE = "collaborative"
    ASSERTIVE = "assertive"

class LetterLength(str, Enum):
    """Available lengths for raise letter generation"""
    CONCISE = "concise"
    STANDARD = "standard"
    DETAILED = "detailed"

@dataclass
class CPIData:
    """CPI calculation data for raise letter context"""
    adjusted_salary: float
    percentage_gap: float
    dollar_gap: float
    original_salary: float
    current_salary: float
    inflation_rate: float
    years_elapsed: int
    calculation_method: str
    calculation_date: str
    historical_date: str

@dataclass
class BenchmarkData:
    """Salary benchmark data for market positioning"""
    percentile_10: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_90: float
    user_percentile: float
    market_position: str
    occupation_title: str
    location: str
    data_source: str
    confidence_score: float

@dataclass
class UserContext:
    """User context for personalized letter generation"""
    name: str
    job_title: str
    company: str
    department: Optional[str] = None
    manager_name: Optional[str] = None
    years_at_company: Optional[int] = None
    key_achievements: Optional[List[str]] = None
    recent_projects: Optional[List[str]] = None

class RaiseLetterRequest(BaseModel):
    """Request model for raise letter generation"""
    user_context: Dict[str, Any]
    cpi_data: Dict[str, Any]
    benchmark_data: Optional[Dict[str, Any]] = None
    tone: LetterTone = LetterTone.PROFESSIONAL
    length: LetterLength = LetterLength.STANDARD
    custom_points: List[str] = Field(default_factory=list)
    requested_increase: Optional[float] = None

class RaiseLetterResponse(BaseModel):
    """Response model for generated raise letter"""
    letter_content: str
    subject_line: str
    key_points: List[str]
    tone_used: LetterTone
    length_used: LetterLength
    generation_metadata: Dict[str, Any]

class OpenAIServiceError(Exception):
    """Custom exception for OpenAI service errors"""
    pass

class OpenAIService:
    """
    OpenAI service for AI-powered raise letter generation
    
    Integrates with GPT-4 Turbo to create personalized, professional
    raise request letters using CPI data and salary benchmarks.
    """
    
    def __init__(self, require_api_key: bool = True):
        """Initialize OpenAI service with configuration"""
        if require_api_key and not settings.OPENAI_API_KEY:
            raise OpenAIServiceError("OpenAI API key not configured")
        
        if settings.OPENAI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=30.0,
                max_retries=3
            )
        else:
            self.client = None
        
        self.model = "gpt-4-turbo-preview"  # Latest GPT-4 Turbo model
        self.max_tokens = 2000
        self.temperature = 0.7
        
    async def generate_raise_letter(
        self, 
        request: RaiseLetterRequest
    ) -> RaiseLetterResponse:
        """
        Generate a professional raise letter using AI
        
        Args:
            request: Raise letter generation request
            
        Returns:
            Generated raise letter with metadata
            
        Raises:
            OpenAIServiceError: If generation fails
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_raise_letter_prompt(request)
            
            # Generate letter using GPT-4 Turbo
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(request.tone, request.length)
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            # Extract and parse response
            content = response.choices[0].message.content
            letter_content = content.strip() if content else ""
            
            # Generate subject line
            subject_line = await self._generate_subject_line(request)
            
            # Extract key points
            key_points = self._extract_key_points(letter_content, request)
            
            # Safely extract usage data
            usage_data = {}
            if response.usage:
                usage_data = {
                    "tokens_used": response.usage.total_tokens,
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }

            return RaiseLetterResponse(
                letter_content=letter_content,
                subject_line=subject_line,
                key_points=key_points,
                tone_used=request.tone,
                length_used=request.length,
                generation_metadata={
                    "model_used": self.model,
                    "generation_time": datetime.utcnow().isoformat(),
                    **usage_data
                }
            )
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIServiceError(f"AI service error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in raise letter generation: {e}")
            raise OpenAIServiceError(f"Letter generation failed: {str(e)}")
    
    async def generate_raise_letter_stream(
        self,
        request: RaiseLetterRequest
    ) -> AsyncGenerator[str, None]:
        """
        Generate raise letter with streaming response
        
        Args:
            request: Raise letter generation request
            
        Yields:
            Chunks of generated letter content
            
        Raises:
            OpenAIServiceError: If generation fails
        """
        try:
            prompt = self._build_raise_letter_prompt(request)
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(request.tone, request.length)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except openai.APIError as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise OpenAIServiceError(f"Streaming generation failed: {str(e)}")
    
    def _build_raise_letter_prompt(self, request: RaiseLetterRequest) -> str:
        """Build comprehensive prompt for raise letter generation"""
        
        user_context = UserContext(**request.user_context)
        cpi_data = CPIData(**request.cpi_data)
        
        # Build base prompt
        prompt_parts = [
            f"Generate a professional raise request letter for {user_context.name}, who works as a {user_context.job_title} at {user_context.company}.",
            "",
            "## INFLATION ANALYSIS DATA:",
            f"- Current salary: ${cpi_data.current_salary:,.2f}",
            f"- Inflation-adjusted salary should be: ${cpi_data.adjusted_salary:,.2f}",
            f"- Purchasing power gap: {cpi_data.percentage_gap:.1f}% (${cpi_data.dollar_gap:,.2f})",
            f"- Inflation rate over {cpi_data.years_elapsed} years: {cpi_data.inflation_rate:.1f}%",
            f"- Analysis period: {cpi_data.historical_date} to {cpi_data.calculation_date}",
            ""
        ]
        
        # Add benchmark data if available
        if request.benchmark_data:
            benchmark = BenchmarkData(**request.benchmark_data)
            prompt_parts.extend([
                "## MARKET BENCHMARK DATA:",
                f"- Job title: {benchmark.occupation_title}",
                f"- Location: {benchmark.location}",
                f"- User's market percentile: {benchmark.user_percentile:.0f}th percentile",
                f"- Market position: {benchmark.market_position}",
                f"- Market median salary: ${benchmark.percentile_50:,.2f}",
                f"- 75th percentile salary: ${benchmark.percentile_75:,.2f}",
                f"- Data source: {benchmark.data_source}",
                f"- Confidence score: {benchmark.confidence_score:.1f}/10",
                ""
            ])
        
        # Add user achievements
        if user_context.key_achievements:
            prompt_parts.extend([
                "## KEY ACHIEVEMENTS:",
                *[f"- {achievement}" for achievement in user_context.key_achievements],
                ""
            ])
        
        # Add recent projects
        if user_context.recent_projects:
            prompt_parts.extend([
                "## RECENT PROJECTS:",
                *[f"- {project}" for project in user_context.recent_projects],
                ""
            ])
        
        # Add custom points
        if request.custom_points:
            prompt_parts.extend([
                "## ADDITIONAL POINTS TO INCLUDE:",
                *[f"- {point}" for point in request.custom_points],
                ""
            ])
        
        # Add specific instructions
        prompt_parts.extend([
            "## LETTER REQUIREMENTS:",
            "- Use the inflation data as primary evidence for the raise request",
            "- Reference market benchmark data to strengthen the position",
            "- Highlight key achievements and recent contributions",
            "- Maintain a professional, respectful tone throughout",
            "- Include specific dollar amounts and percentages from the data",
            "- Structure as a formal business letter",
            "- End with a clear call to action for a meeting",
            ""
        ])
        
        if request.requested_increase:
            prompt_parts.append(f"- Request a salary increase to ${request.requested_increase:,.2f}")
        
        return "\n".join(prompt_parts)
    
    def _get_system_prompt(self, tone: LetterTone, length: LetterLength) -> str:
        """Get system prompt based on tone and length preferences"""
        
        base_prompt = """You are a professional business writing assistant specializing in salary negotiation letters. You help employees craft compelling, evidence-based raise requests that are respectful, professional, and persuasive.

Your letters should:
- Be well-structured with clear introduction, body, and conclusion
- Use specific data and evidence to support the request
- Maintain appropriate business letter formatting
- Be persuasive without being demanding
- Show appreciation for current opportunities
- Demonstrate value and contributions
- Include a clear next step or call to action"""

        tone_instructions = {
            LetterTone.PROFESSIONAL: "Maintain a formal, respectful tone throughout. Use traditional business language and structure.",
            LetterTone.CONFIDENT: "Use confident language that demonstrates self-assurance while remaining respectful. Emphasize achievements and value.",
            LetterTone.COLLABORATIVE: "Focus on partnership and mutual benefit. Emphasize team contributions and shared success.",
            LetterTone.ASSERTIVE: "Be direct and clear about the request while maintaining professionalism. Use strong, decisive language."
        }
        
        length_instructions = {
            LetterLength.CONCISE: "Keep the letter brief and to the point, around 200-300 words. Focus on the most compelling evidence.",
            LetterLength.STANDARD: "Write a standard business letter of 300-500 words with full context and supporting details.",
            LetterLength.DETAILED: "Provide a comprehensive letter of 500-800 words with extensive detail and multiple supporting arguments."
        }
        
        return f"{base_prompt}\n\nTONE: {tone_instructions[tone]}\n\nLENGTH: {length_instructions[length]}"
    
    async def _generate_subject_line(self, request: RaiseLetterRequest) -> str:
        """Generate appropriate subject line for the raise request"""
        
        user_context = UserContext(**request.user_context)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model for simple task
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a professional, concise email subject line for a salary increase request. Keep it under 60 characters and make it clear but not overly direct."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a subject line for a raise request from {user_context.name}, {user_context.job_title} at {user_context.company}."
                    }
                ],
                max_tokens=50,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            return content.strip().strip('"') if content else "Salary Review Request"
            
        except Exception as e:
            logger.warning(f"Failed to generate subject line: {e}")
            return f"Salary Review Request - {user_context.name}"
    
    def _extract_key_points(self, letter_content: str, request: RaiseLetterRequest) -> List[str]:
        """Extract key points from generated letter for summary"""
        
        key_points = []
        
        # Add CPI-based point
        cpi_data = CPIData(**request.cpi_data)
        key_points.append(f"Purchasing power decreased by {cpi_data.percentage_gap:.1f}% due to inflation")
        
        # Add benchmark point if available
        if request.benchmark_data:
            benchmark = BenchmarkData(**request.benchmark_data)
            key_points.append(f"Currently at {benchmark.user_percentile:.0f}th percentile in market")
        
        # Add achievement points
        if request.user_context.get('key_achievements'):
            key_points.append("Highlighted key achievements and contributions")
        
        # Add custom points
        key_points.extend(request.custom_points[:2])  # Limit to 2 custom points
        
        return key_points[:5]  # Limit to 5 key points total
    
    async def validate_api_connection(self) -> bool:
        """Validate OpenAI API connection and model availability"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI API validation failed: {e}")
            return False


# Create service instance for easy importing (optional API key for testing)
try:
    openai_service = OpenAIService(require_api_key=False)
except Exception as e:
    openai_service = None

# Export for easy importing
__all__ = [
    'OpenAIService',
    'openai_service',
    'RaiseLetterRequest', 
    'RaiseLetterResponse',
    'LetterTone',
    'LetterLength',
    'OpenAIServiceError',
    'UserContext',
    'CPIData', 
    'BenchmarkData'
] 