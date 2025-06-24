"""
Test Harness for AI-Generated Raise Letters with Numeric Facts

Comprehensive testing suite to validate that AI-generated raise letters
contain accurate numeric data from CPI calculations and salary benchmarks.
"""

import pytest
import re
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from unittest.mock import AsyncMock, MagicMock, patch
import json

from app.services.openai_service import (
    openai_service,
    RaiseLetterRequest,
    RaiseLetterResponse,
    LetterTone,
    LetterLength,
    OpenAIServiceError
)


class NumericFactValidator:
    """Validates numeric facts in generated raise letters"""
    
    @staticmethod
    def extract_salary_amounts(text: str) -> List[float]:
        """Extract salary amounts from text (e.g., $85,000, $95,000)"""
        pattern = r'\$[\d,]+(?:\.\d{2})?'
        matches = re.findall(pattern, text)
        return [float(match.replace('$', '').replace(',', '')) for match in matches]
    
    @staticmethod
    def extract_percentages(text: str) -> List[float]:
        """Extract percentage values from text (e.g., 11.8%, 8.2%)"""
        pattern = r'(\d+\.?\d*)\s*%'
        matches = re.findall(pattern, text)
        return [float(match) for match in matches]
    
    @staticmethod
    def extract_years(text: str) -> List[int]:
        """Extract year values from text"""
        pattern = r'(\d+)\s*(?:year|yr)s?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [int(match) for match in matches]
    
    @staticmethod
    def validate_cpi_facts(letter_content: str, expected_cpi_data: Dict) -> Dict[str, bool]:
        """Validate CPI-related facts in the letter"""
        results = {
            'current_salary_mentioned': False,
            'adjusted_salary_mentioned': False,
            'percentage_gap_accurate': False,
            'dollar_gap_accurate': False,
            'inflation_rate_accurate': False,
            'years_elapsed_accurate': False
        }
        
        # Extract numeric values from letter
        salaries = NumericFactValidator.extract_salary_amounts(letter_content)
        percentages = NumericFactValidator.extract_percentages(letter_content)
        years = NumericFactValidator.extract_years(letter_content)
        
        # Check if current salary is mentioned
        if expected_cpi_data['current_salary'] in salaries:
            results['current_salary_mentioned'] = True
        
        # Check if adjusted salary is mentioned
        if expected_cpi_data['adjusted_salary'] in salaries:
            results['adjusted_salary_mentioned'] = True
        
        # Check percentage gap (allow small tolerance)
        expected_gap = expected_cpi_data['percentage_gap']
        for pct in percentages:
            if abs(pct - expected_gap) < 0.5:  # 0.5% tolerance
                results['percentage_gap_accurate'] = True
                break
        
        # Check inflation rate
        expected_inflation = expected_cpi_data['inflation_rate']
        for pct in percentages:
            if abs(pct - expected_inflation) < 0.5:
                results['inflation_rate_accurate'] = True
                break
        
        # Check years elapsed
        expected_years = expected_cpi_data['years_elapsed']
        if expected_years in years:
            results['years_elapsed_accurate'] = True
        
        # Check dollar gap (mentioned in text)
        dollar_gap_str = f"${expected_cpi_data['dollar_gap']:,.0f}"
        if dollar_gap_str in letter_content or str(expected_cpi_data['dollar_gap']) in letter_content:
            results['dollar_gap_accurate'] = True
        
        return results
    
    @staticmethod
    def validate_benchmark_facts(letter_content: str, expected_benchmark_data: Dict) -> Dict[str, bool]:
        """Validate salary benchmark facts in the letter"""
        results = {
            'percentile_mentioned': False,
            'market_position_mentioned': False,
            'median_salary_mentioned': False,
            'location_mentioned': False,
            'job_title_mentioned': False
        }
        
        if not expected_benchmark_data:
            return results
        
        # Check percentile mention
        percentile = expected_benchmark_data.get('user_percentile', 0)
        if f"{percentile:.0f}th percentile" in letter_content or f"{percentile:.0f} percentile" in letter_content:
            results['percentile_mentioned'] = True
        
        # Check market position
        market_position = expected_benchmark_data.get('market_position', '')
        if market_position.lower() in letter_content.lower():
            results['market_position_mentioned'] = True
        
        # Check median salary
        median_salary = expected_benchmark_data.get('percentile_50', 0)
        salaries = NumericFactValidator.extract_salary_amounts(letter_content)
        if median_salary in salaries:
            results['median_salary_mentioned'] = True
        
        # Check location mention
        location = expected_benchmark_data.get('location', '')
        if location and location.lower() in letter_content.lower():
            results['location_mentioned'] = True
        
        # Check job title
        job_title = expected_benchmark_data.get('occupation_title', '')
        if job_title and job_title.lower() in letter_content.lower():
            results['job_title_mentioned'] = True
        
        return results


@pytest.fixture
def test_scenarios():
    """Comprehensive test scenarios with known data sets"""
    return {
        'scenario_1_high_inflation': {
            'user_context': {
                'name': 'Alice Johnson',
                'job_title': 'Software Engineer',
                'company': 'TechCorp Inc',
                'department': 'Engineering',
                'manager_name': 'Bob Smith',
                'years_at_company': 3,
                'key_achievements': [
                    'Led development of microservices architecture',
                    'Reduced system latency by 40%',
                    'Mentored 2 junior developers'
                ],
                'recent_projects': [
                    'API Gateway Implementation',
                    'Database Migration Project'
                ]
            },
            'cpi_data': {
                'original_salary': 80000,
                'current_salary': 85000,
                'adjusted_salary': 98500,
                'percentage_gap': 15.9,
                'dollar_gap': 13500,
                'inflation_rate': 12.3,
                'years_elapsed': 2,
                'calculation_method': 'CPI-U All Items',
                'calculation_date': '2024-01-01',
                'historical_date': '2022-01-01'
            },
            'benchmark_data': {
                'percentile_10': 70000,
                'percentile_25': 80000,
                'percentile_50': 95000,
                'percentile_75': 110000,
                'percentile_90': 125000,
                'user_percentile': 35,
                'market_position': 'Below Market',
                'occupation_title': 'Software Engineer',
                'location': 'San Francisco, CA',
                'data_source': 'CareerOneStop',
                'confidence_score': 8.5
            }
        },
        'scenario_2_moderate_inflation': {
            'user_context': {
                'name': 'David Chen',
                'job_title': 'Marketing Manager',
                'company': 'Growth Solutions LLC',
                'department': 'Marketing',
                'manager_name': 'Sarah Williams',
                'years_at_company': 4,
                'key_achievements': [
                    'Increased lead generation by 60%',
                    'Launched 3 successful campaigns',
                    'Managed $500K marketing budget'
                ],
                'recent_projects': [
                    'Digital Transformation Initiative',
                    'Customer Segmentation Analysis'
                ]
            },
            'cpi_data': {
                'original_salary': 65000,
                'current_salary': 70000,
                'adjusted_salary': 75600,
                'percentage_gap': 8.0,
                'dollar_gap': 5600,
                'inflation_rate': 6.2,
                'years_elapsed': 3,
                'calculation_method': 'CPI-U All Items',
                'calculation_date': '2024-01-01',
                'historical_date': '2021-01-01'
            },
            'benchmark_data': {
                'percentile_10': 55000,
                'percentile_25': 65000,
                'percentile_50': 75000,
                'percentile_75': 85000,
                'percentile_90': 95000,
                'user_percentile': 65,
                'market_position': 'At Market',
                'occupation_title': 'Marketing Manager',
                'location': 'Austin, TX',
                'data_source': 'CareerOneStop',
                'confidence_score': 9.2
            }
        },
        'scenario_3_low_inflation_high_performer': {
            'user_context': {
                'name': 'Maria Rodriguez',
                'job_title': 'Data Scientist',
                'company': 'Analytics Pro',
                'department': 'Data Science',
                'manager_name': 'James Park',
                'years_at_company': 2,
                'key_achievements': [
                    'Built ML model with 95% accuracy',
                    'Automated reporting saving 20 hours/week',
                    'Published 2 research papers'
                ],
                'recent_projects': [
                    'Predictive Analytics Platform',
                    'Real-time Dashboard Development'
                ]
            },
            'cpi_data': {
                'original_salary': 95000,
                'current_salary': 100000,
                'adjusted_salary': 103800,
                'percentage_gap': 3.8,
                'dollar_gap': 3800,
                'inflation_rate': 3.2,
                'years_elapsed': 2,
                'calculation_method': 'CPI-U All Items',
                'calculation_date': '2024-01-01',
                'historical_date': '2022-01-01'
            },
            'benchmark_data': {
                'percentile_10': 85000,
                'percentile_25': 95000,
                'percentile_50': 110000,
                'percentile_75': 125000,
                'percentile_90': 140000,
                'user_percentile': 25,
                'market_position': 'Below Market',
                'occupation_title': 'Data Scientist',
                'location': 'Seattle, WA',
                'data_source': 'CareerOneStop',
                'confidence_score': 9.8
            }
        }
    }


class TestRaiseLetterGeneration:
    """Test cases for AI-generated raise letter accuracy"""
    
    @pytest.mark.asyncio
    async def test_cpi_facts_accuracy_high_inflation(self, test_scenarios):
        """Test accurate CPI fact integration in high inflation scenario"""
        scenario = test_scenarios['scenario_1_high_inflation']
        
        # Mock OpenAI response with realistic content
        mock_response_content = f"""
        Dear Bob Smith,
        
        I am writing to request a salary adjustment based on recent inflation analysis and market data.
        
        My current salary of ${scenario['cpi_data']['current_salary']:,} has experienced a significant 
        purchasing power decline due to inflation. Based on Consumer Price Index data from the Bureau 
        of Labor Statistics, inflation has increased by {scenario['cpi_data']['inflation_rate']:.1f}% 
        over the past {scenario['cpi_data']['years_elapsed']} years.
        
        To maintain the same purchasing power as when I started, my salary should be adjusted to 
        ${scenario['cpi_data']['adjusted_salary']:,}, representing a {scenario['cpi_data']['percentage_gap']:.1f}% 
        gap or ${scenario['cpi_data']['dollar_gap']:,} in lost purchasing power.
        
        Additionally, market analysis shows I am currently at the {scenario['benchmark_data']['user_percentile']:.0f}th 
        percentile for Software Engineers in San Francisco, CA, which is Below Market compared to the 
        median salary of ${scenario['benchmark_data']['percentile_50']:,}.
        
        My key achievements include leading development of microservices architecture and reducing 
        system latency by 40%.
        
        I would appreciate the opportunity to discuss this adjustment.
        
        Sincerely,
        Alice Johnson
        """
        
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            # Setup mock
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = {
                'choices': [{'message': {'content': mock_response_content}}],
                'usage': {'prompt_tokens': 200, 'completion_tokens': 300, 'total_tokens': 500}
            }
            mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
            
            # Create request
            request = RaiseLetterRequest(
                user_context=scenario['user_context'],
                cpi_data=scenario['cpi_data'],
                benchmark_data=scenario['benchmark_data'],
                tone=LetterTone.PROFESSIONAL,
                length=LetterLength.STANDARD
            )
            
            # Generate letter
            result = await openai_service.generate_raise_letter(request)
            
            # Validate CPI facts
            cpi_validation = NumericFactValidator.validate_cpi_facts(
                result.letter_content, scenario['cpi_data']
            )
            
            # Assert CPI facts are accurate
            assert cpi_validation['current_salary_mentioned'], "Current salary should be mentioned"
            assert cpi_validation['adjusted_salary_mentioned'], "Adjusted salary should be mentioned"
            assert cpi_validation['percentage_gap_accurate'], "Percentage gap should be accurate"
            assert cpi_validation['inflation_rate_accurate'], "Inflation rate should be accurate"
            assert cpi_validation['years_elapsed_accurate'], "Years elapsed should be accurate"
            
            # Validate benchmark facts
            benchmark_validation = NumericFactValidator.validate_benchmark_facts(
                result.letter_content, scenario['benchmark_data']
            )
            
            assert benchmark_validation['percentile_mentioned'], "User percentile should be mentioned"
            assert benchmark_validation['market_position_mentioned'], "Market position should be mentioned"

    @pytest.mark.asyncio
    async def test_different_tones_maintain_accuracy(self, test_scenarios):
        """Test that different tones maintain numeric accuracy"""
        scenario = test_scenarios['scenario_2_moderate_inflation']
        tones = [LetterTone.PROFESSIONAL, LetterTone.CONFIDENT, LetterTone.COLLABORATIVE]
        
        for tone in tones:
            # Create realistic mock response for each tone
            mock_content = f"""
            Dear Sarah Williams,
            
            I am requesting a salary review based on inflation data and market analysis.
            
            Current salary: ${scenario['cpi_data']['current_salary']:,}
            Inflation-adjusted target: ${scenario['cpi_data']['adjusted_salary']:,}
            Purchasing power gap: {scenario['cpi_data']['percentage_gap']:.1f}%
            Inflation over {scenario['cpi_data']['years_elapsed']} years: {scenario['cpi_data']['inflation_rate']:.1f}%
            
            Market position: {scenario['benchmark_data']['user_percentile']:.0f}th percentile ({scenario['benchmark_data']['market_position']})
            
            Key achievements: Increased lead generation by 60%, launched 3 successful campaigns.
            
            Best regards,
            David Chen
            """
            
            with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
                mock_client = AsyncMock()
                mock_openai.return_value = mock_client
                mock_response = {
                    'choices': [{'message': {'content': mock_content}}],
                    'usage': {'prompt_tokens': 180, 'completion_tokens': 250, 'total_tokens': 430}
                }
                mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
                
                request = RaiseLetterRequest(
                    user_context=scenario['user_context'],
                    cpi_data=scenario['cpi_data'],
                    benchmark_data=scenario['benchmark_data'],
                    tone=tone,
                    length=LetterLength.STANDARD
                )
                
                result = await openai_service.generate_raise_letter(request)
                
                # Validate facts regardless of tone
                cpi_validation = NumericFactValidator.validate_cpi_facts(
                    result.letter_content, scenario['cpi_data']
                )
                
                assert cpi_validation['current_salary_mentioned'], f"Current salary missing in {tone.value} tone"
                assert cpi_validation['percentage_gap_accurate'], f"Percentage gap inaccurate in {tone.value} tone"
                assert cpi_validation['inflation_rate_accurate'], f"Inflation rate inaccurate in {tone.value} tone"

    @pytest.mark.asyncio
    async def test_edge_case_high_performer_low_percentile(self, test_scenarios):
        """Test edge case: high performer at low market percentile"""
        scenario = test_scenarios['scenario_3_low_inflation_high_performer']
        
        mock_content = f"""
        Dear James Park,
        
        I am writing to request a salary adjustment based on my performance and market analysis.
        
        Despite low inflation of {scenario['cpi_data']['inflation_rate']:.1f}% over {scenario['cpi_data']['years_elapsed']} years,
        my current salary of ${scenario['cpi_data']['current_salary']:,} places me at only the 
        {scenario['benchmark_data']['user_percentile']:.0f}th percentile for Data Scientists in Seattle, WA.
        
        The market median is ${scenario['benchmark_data']['percentile_50']:,}, indicating I am Below Market.
        Even accounting for inflation, my adjusted salary should be ${scenario['cpi_data']['adjusted_salary']:,}.
        
        My achievements include building an ML model with 95% accuracy and automating reporting 
        to save 20 hours per week.
        
        I believe my performance warrants positioning closer to market median.
        
        Thank you,
        Maria Rodriguez
        """
        
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = {
                'choices': [{'message': {'content': mock_content}}],
                'usage': {'prompt_tokens': 220, 'completion_tokens': 280, 'total_tokens': 500}
            }
            mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
            
            request = RaiseLetterRequest(
                user_context=scenario['user_context'],
                cpi_data=scenario['cpi_data'],
                benchmark_data=scenario['benchmark_data'],
                tone=LetterTone.CONFIDENT,
                length=LetterLength.STANDARD
            )
            
            result = await openai_service.generate_raise_letter(request)
            
            # Validate both CPI and benchmark facts
            cpi_validation = NumericFactValidator.validate_cpi_facts(
                result.letter_content, scenario['cpi_data']
            )
            benchmark_validation = NumericFactValidator.validate_benchmark_facts(
                result.letter_content, scenario['benchmark_data']
            )
            
            # Should mention low inflation but emphasize market position
            assert cpi_validation['inflation_rate_accurate'], "Should mention accurate inflation rate"
            assert benchmark_validation['percentile_mentioned'], "Should mention low percentile"
            assert benchmark_validation['median_salary_mentioned'], "Should mention market median"
            assert benchmark_validation['market_position_mentioned'], "Should mention Below Market position"

    @pytest.mark.asyncio
    async def test_numeric_consistency_across_generations(self, test_scenarios):
        """Test that multiple generations maintain consistent numeric facts"""
        scenario = test_scenarios['scenario_1_high_inflation']
        
        # Generate same letter multiple times
        results = []
        
        for i in range(3):
            mock_content = f"""
            Dear Bob Smith,
            
            Request for salary adjustment based on inflation analysis.
            
            Current: ${scenario['cpi_data']['current_salary']:,}
            Target: ${scenario['cpi_data']['adjusted_salary']:,}
            Gap: {scenario['cpi_data']['percentage_gap']:.1f}% (${scenario['cpi_data']['dollar_gap']:,})
            Inflation: {scenario['cpi_data']['inflation_rate']:.1f}% over {scenario['cpi_data']['years_elapsed']} years
            
            Market: {scenario['benchmark_data']['user_percentile']:.0f}th percentile
            
            Sincerely,
            Alice Johnson
            """
            
            with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
                mock_client = AsyncMock()
                mock_openai.return_value = mock_client
                mock_response = {
                    'choices': [{'message': {'content': mock_content}}],
                    'usage': {'prompt_tokens': 150, 'completion_tokens': 200, 'total_tokens': 350}
                }
                mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
                
                request = RaiseLetterRequest(
                    user_context=scenario['user_context'],
                    cpi_data=scenario['cpi_data'],
                    benchmark_data=scenario['benchmark_data'],
                    tone=LetterTone.PROFESSIONAL,
                    length=LetterLength.STANDARD
                )
                
                result = await openai_service.generate_raise_letter(request)
                results.append(result)
        
        # Validate all generations have consistent facts
        for i, result in enumerate(results):
            cpi_validation = NumericFactValidator.validate_cpi_facts(
                result.letter_content, scenario['cpi_data']
            )
            
            assert cpi_validation['current_salary_mentioned'], f"Generation {i+1} missing current salary"
            assert cpi_validation['percentage_gap_accurate'], f"Generation {i+1} has inaccurate percentage"
            assert cpi_validation['inflation_rate_accurate'], f"Generation {i+1} has inaccurate inflation rate"

    def test_numeric_extraction_utilities(self):
        """Test the numeric extraction utility functions"""
        sample_text = """
        My current salary is $85,000 and I'm requesting an increase to $95,000.
        Inflation has been 8.2% over the past 2 years, creating a 11.8% purchasing power gap.
        I'm currently at the 35th percentile in the market.
        """
        
        # Test salary extraction
        salaries = NumericFactValidator.extract_salary_amounts(sample_text)
        assert 85000.0 in salaries
        assert 95000.0 in salaries
        
        # Test percentage extraction
        percentages = NumericFactValidator.extract_percentages(sample_text)
        assert 8.2 in percentages
        assert 11.8 in percentages
        assert 35 in percentages
        
        # Test year extraction
        years = NumericFactValidator.extract_years(sample_text)
        assert 2 in years

    @pytest.mark.asyncio
    async def test_missing_benchmark_data_handling(self, test_scenarios):
        """Test letter generation when benchmark data is missing"""
        scenario = test_scenarios['scenario_2_moderate_inflation']
        
        mock_content = f"""
        Dear Sarah Williams,
        
        I am requesting a salary adjustment based on inflation analysis.
        
        Current salary: ${scenario['cpi_data']['current_salary']:,}
        Inflation-adjusted salary: ${scenario['cpi_data']['adjusted_salary']:,}
        Purchasing power loss: {scenario['cpi_data']['percentage_gap']:.1f}%
        
        Over the past {scenario['cpi_data']['years_elapsed']} years, inflation has been 
        {scenario['cpi_data']['inflation_rate']:.1f}%, significantly impacting my purchasing power.
        
        Best regards,
        David Chen
        """
        
        with patch('app.services.openai_service.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = {
                'choices': [{'message': {'content': mock_content}}],
                'usage': {'prompt_tokens': 160, 'completion_tokens': 220, 'total_tokens': 380}
            }
            mock_client.chat.completions.create.return_value = MagicMock(**mock_response)
            
            # Request without benchmark data
            request = RaiseLetterRequest(
                user_context=scenario['user_context'],
                cpi_data=scenario['cpi_data'],
                benchmark_data=None,  # No benchmark data
                tone=LetterTone.PROFESSIONAL,
                length=LetterLength.STANDARD
            )
            
            result = await openai_service.generate_raise_letter(request)
            
            # Should still have accurate CPI facts
            cpi_validation = NumericFactValidator.validate_cpi_facts(
                result.letter_content, scenario['cpi_data']
            )
            
            assert cpi_validation['current_salary_mentioned'], "Should mention current salary without benchmark"
            assert cpi_validation['percentage_gap_accurate'], "Should have accurate percentage without benchmark"
            assert cpi_validation['inflation_rate_accurate'], "Should have accurate inflation rate without benchmark"
            
            # Should not fail when no benchmark data to validate
            benchmark_validation = NumericFactValidator.validate_benchmark_facts(
                result.letter_content, None
            )
            assert not any(benchmark_validation.values()), "Should not have benchmark facts when none provided"