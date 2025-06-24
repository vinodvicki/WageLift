"""
Tests for OpenAI Service

Comprehensive test suite for AI-powered raise letter generation functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import json

from app.services.openai_service import (
    openai_service,
    RaiseLetterRequest,
    RaiseLetterResponse,
    LetterTone,
    LetterLength,
    OpenAIServiceError
)


@pytest.fixture
def sample_request():
    """Sample raise letter request for testing."""
    return RaiseLetterRequest(
        user_context={
            "name": "John Smith",
            "job_title": "Senior Software Engineer", 
            "company": "TechCorp Solutions",
            "department": "Engineering",
            "manager_name": "Sarah Johnson",
            "years_at_company": 3,
            "key_achievements": ["Led customer portal development", "Mentored junior developers"],
            "recent_projects": ["Portal Redesign", "Testing Framework"]
        },
        cpi_data={
            "original_salary": 75000,
            "current_salary": 85000,
            "adjusted_salary": 95000,
            "percentage_gap": 11.8,
            "dollar_gap": 10000,
            "inflation_rate": 8.2,
            "years_elapsed": 2,
            "calculation_method": "CPI-U All Items",
            "calculation_date": "2024-01-01",
            "historical_date": "2022-01-01"
        },
        tone=LetterTone.PROFESSIONAL,
        length=LetterLength.STANDARD,
        custom_points=["Architecture responsibilities"],
        requested_increase=95000
    )


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1640995200,
        "model": "gpt-4-turbo-preview",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Dear Sarah Johnson,\n\nI am writing to request a salary adjustment..."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 300,
            "total_tokens": 450
        }
    }


class TestOpenAIService:
    """Test cases for OpenAI service functionality."""

    @pytest.mark.asyncio
    async def test_generate_raise_letter_success(self, sample_request, mock_openai_response):
        """Test successful letter generation."""
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.return_value = MagicMock(**mock_openai_response)
            
            # Execute
            result = await openai_service.generate_raise_letter(sample_request)
            
            # Verify
            assert isinstance(result, RaiseLetterResponse)
            assert result.success is True
            assert result.letter_content == "Dear Sarah Johnson,\n\nI am writing to request a salary adjustment..."
            assert "salary adjustment" in result.subject_line.lower()
            assert len(result.key_points) > 0
            assert result.tone_used == LetterTone.PROFESSIONAL
            assert result.length_used == LetterLength.STANDARD
            assert result.generation_metadata.model_used == "gpt-4-turbo-preview"
            assert result.generation_metadata.tokens_used == 450
            assert result.generation_metadata.prompt_tokens == 150
            assert result.generation_metadata.completion_tokens == 300

    @pytest.mark.asyncio
    async def test_generate_raise_letter_different_tones(self, sample_request):
        """Test letter generation with different tones."""
        mock_responses = {
            LetterTone.CONFIDENT: "I am confident that my contributions warrant...",
            LetterTone.COLLABORATIVE: "I would like to discuss the possibility of...",
            LetterTone.ASSERTIVE: "Based on my performance and market data, I request..."
        }
        
        for tone, expected_content in mock_responses.items():
            with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
                # Setup mock
                mock_client = AsyncMock()
                mock_openai.return_value = mock_client
                mock_response = {
                    "choices": [{"message": {"content": expected_content}}],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
                }
                mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
                
                # Update request tone
                sample_request.tone = tone
                
                # Execute
                result = await openai_service.generate_raise_letter(sample_request)
                
                # Verify
                assert result.tone_used == tone
                assert expected_content in result.letter_content

    @pytest.mark.asyncio
    async def test_generate_raise_letter_different_lengths(self, sample_request):
        """Test letter generation with different lengths."""
        lengths = [LetterLength.CONCISE, LetterLength.STANDARD, LetterLength.DETAILED]
        
        for length in lengths:
            with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
                # Setup mock
                mock_client = AsyncMock()
                mock_openai.return_value = mock_client
                mock_response = {
                    "choices": [{"message": {"content": f"Letter content for {length.value} length"}}],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
                }
                mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
                
                # Update request length
                sample_request.length = length
                
                # Execute
                result = await openai_service.generate_raise_letter(sample_request)
                
                # Verify
                assert result.length_used == length

    @pytest.mark.asyncio
    async def test_generate_raise_letter_with_benchmark_data(self, sample_request):
        """Test letter generation with salary benchmark data."""
        # Add benchmark data to request
        sample_request.benchmark_data = {
            "percentile_50": 90000,
            "percentile_75": 105000,
            "user_percentile": 45,
            "market_position": "Below Market",
            "occupation_title": "Software Engineer",
            "location": "San Francisco, CA"
        }
        
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = {
                "choices": [{"message": {"content": "Letter with market data analysis"}}],
                "usage": {"prompt_tokens": 150, "completion_tokens": 250, "total_tokens": 400}
            }
            mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
            
            # Execute
            result = await openai_service.generate_raise_letter(sample_request)
            
            # Verify that the call was made (benchmark data should be included in prompt)
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            
            # Check that benchmark data is referenced in the prompt
            messages = call_args[1]['messages']
            user_message = next(msg for msg in messages if msg['role'] == 'user')
            assert 'market data' in user_message['content'].lower() or 'benchmark' in user_message['content'].lower()

    @pytest.mark.asyncio
    async def test_generate_raise_letter_openai_error(self, sample_request):
        """Test handling of OpenAI API errors."""
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock to raise exception
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("OpenAI API Error")
            
            # Execute and verify exception
            with pytest.raises(OpenAIServiceError) as exc_info:
                await openai_service.generate_raise_letter(sample_request)
            
            assert "Failed to generate raise letter" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_raise_letter_no_api_key(self, sample_request):
        """Test handling when OpenAI API key is not configured."""
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = None
            
            # Execute and verify exception
            with pytest.raises(OpenAIServiceError) as exc_info:
                await openai_service.generate_raise_letter(sample_request)
            
            assert "OpenAI API key not configured" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_raise_letter_streaming_success(self, sample_request):
        """Test successful streaming letter generation."""
        chunks = [
            "Dear Sarah Johnson,",
            " I am writing to request",
            " a salary adjustment based on",
            " my performance and market data."
        ]
        
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock for streaming
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            # Create async generator for streaming response
            async def mock_stream():
                for chunk in chunks:
                    yield MagicMock(
                        choices=[MagicMock(
                            delta=MagicMock(content=chunk),
                            finish_reason=None
                        )]
                    )
                # Final chunk with finish reason
                yield MagicMock(
                    choices=[MagicMock(
                        delta=MagicMock(content=""),
                        finish_reason="stop"
                    )]
                )
            
            mock_client.chat.completions.create.return_value = mock_stream()
            
            # Execute streaming
            collected_chunks = []
            async for chunk in openai_service.generate_raise_letter_stream(sample_request):
                collected_chunks.append(chunk)
            
            # Verify
            assert collected_chunks == chunks
            assert "".join(collected_chunks) == "Dear Sarah Johnson, I am writing to request a salary adjustment based on my performance and market data."

    @pytest.mark.asyncio
    async def test_check_service_health_success(self):
        """Test successful health check."""
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = {
                "choices": [{"message": {"content": "Test response"}}],
                "usage": {"total_tokens": 10}
            }
            mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
            
            # Execute
            health = await openai_service.check_service_health()
            
            # Verify
            assert health.status == "healthy"
            assert health.openai_connected is True
            assert health.service == "OpenAI Raise Letter Service"
            assert health.model == "gpt-4-turbo-preview"

    @pytest.mark.asyncio
    async def test_check_service_health_failure(self):
        """Test health check failure."""
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock to fail
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("Connection failed")
            
            # Execute
            health = await openai_service.check_service_health()
            
            # Verify
            assert health.status == "unhealthy"
            assert health.openai_connected is False
            assert "Connection failed" in health.error

    def test_prompt_construction(self, sample_request):
        """Test that prompts are constructed correctly."""
        # Test system prompt construction
        system_prompt = openai_service._build_system_prompt(sample_request)
        
        assert "professional raise letter" in system_prompt.lower()
        assert sample_request.tone.value in system_prompt.lower()
        assert sample_request.length.value in system_prompt.lower()
        
        # Test user prompt construction
        user_prompt = openai_service._build_user_prompt(sample_request)
        
        assert sample_request.user_name in user_prompt
        assert sample_request.job_title in user_prompt
        assert sample_request.company in user_prompt
        assert str(sample_request.current_salary) in user_prompt
        assert str(sample_request.percentage_gap) in user_prompt
        
        # Check achievements are included
        for achievement in sample_request.key_achievements:
            assert achievement in user_prompt

    def test_response_parsing(self):
        """Test parsing of OpenAI response into structured format."""
        raw_content = """
        Subject: Request for Salary Adjustment

        Dear Manager,

        I am writing to request a salary adjustment...

        Key Points:
        - Performance exceeds expectations
        - Market data supports increase
        - Inflation impact on purchasing power

        Thank you for your consideration.
        """
        
        parsed = openai_service._parse_letter_response(raw_content, LetterTone.PROFESSIONAL, LetterLength.STANDARD)
        
        assert "Request for Salary Adjustment" in parsed["subject_line"]
        assert "Dear Manager" in parsed["letter_content"]
        assert len(parsed["key_points"]) >= 3
        assert "Performance exceeds expectations" in parsed["key_points"]

    @pytest.mark.asyncio
    async def test_rate_limiting_handling(self, sample_request):
        """Test handling of rate limiting from OpenAI API."""
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock to simulate rate limiting
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            
            from openai import RateLimitError
            mock_client.chat.completions.create.side_effect = RateLimitError(
                message="Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None
            )
            
            # Execute and verify exception handling
            with pytest.raises(OpenAIServiceError) as exc_info:
                await openai_service.generate_raise_letter(sample_request)
            
            assert "rate limit" in str(exc_info.value).lower()

    def test_validation_errors(self):
        """Test validation of request data."""
        # Test missing required fields
        with pytest.raises(ValueError):
            RaiseLetterRequest(
                user_name="",  # Empty name should fail validation
                job_title="Engineer",
                company="TechCorp",
                current_salary=85000,
                adjusted_salary=95000,
                percentage_gap=11.8,
                dollar_gap=10000,
                inflation_rate=8.2,
                years_elapsed=2,
                calculation_method="CPI-U",
                calculation_date="2024-01-01",
                historical_date="2022-01-01",
                tone=LetterTone.PROFESSIONAL,
                length=LetterLength.STANDARD
            )

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, sample_request):
        """Test handling of concurrent letter generation requests."""
        import asyncio
        
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = {
                "choices": [{"message": {"content": "Generated letter content"}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
            }
            mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
            
            # Execute concurrent requests
            tasks = [
                openai_service.generate_raise_letter(sample_request)
                for _ in range(3)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verify all requests succeeded
            assert len(results) == 3
            for result in results:
                assert result.success is True
                assert result.letter_content == "Generated letter content" 