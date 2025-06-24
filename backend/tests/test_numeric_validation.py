"""
Test Numeric Validation Utilities for Raise Letter Generation

Standalone tests for validating numeric fact extraction and validation
without requiring OpenAI API integration.
"""

import pytest
import re
from typing import Dict, List, Optional


class NumericFactValidator:
    """Validates numeric facts in generated raise letters"""
    
    @staticmethod
    def extract_salary_amounts(text: str) -> List[float]:
        """Extract salary amounts from text (e.g., $85,000, $95,000)"""
        # Updated pattern to handle various formats including commas and decimals
        pattern = r'\$[\d,]+(?:\.\d{2})?'
        matches = re.findall(pattern, text)
        salaries = []
        for match in matches:
            # Remove $ and commas, then convert to float
            clean_amount = match.replace('$', '').replace(',', '')
            try:
                salaries.append(float(clean_amount))
            except ValueError:
                continue
        return salaries
    
    @staticmethod
    def extract_percentages(text: str) -> List[float]:
        """Extract percentage values from text (e.g., 11.8%, 8.2%)"""
        pattern = r'(\d+\.?\d*)\s*%'
        matches = re.findall(pattern, text)
        percentages = []
        for match in matches:
            try:
                percentages.append(float(match))
            except ValueError:
                continue
        return percentages
    
    @staticmethod
    def extract_years(text: str) -> List[int]:
        """Extract year values from text"""
        pattern = r'(\d+)\s*(?:year|yr)s?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        years = []
        for match in matches:
            try:
                years.append(int(match))
            except ValueError:
                continue
        return years
    
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
        
        # Check if current salary is mentioned (with small tolerance for rounding)
        current_salary = expected_cpi_data['current_salary']
        for salary in salaries:
            if abs(salary - current_salary) < 100:  # $100 tolerance
                results['current_salary_mentioned'] = True
                break
        
        # Check if adjusted salary is mentioned
        adjusted_salary = expected_cpi_data['adjusted_salary']
        for salary in salaries:
            if abs(salary - adjusted_salary) < 100:  # $100 tolerance
                results['adjusted_salary_mentioned'] = True
                break
        
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
        
        # Check dollar gap (mentioned in text) - improved detection
        dollar_gap = expected_cpi_data['dollar_gap']
        dollar_gap_patterns = [
            f"${dollar_gap:,.0f}",  # $5,600
            f"${dollar_gap:.0f}",   # $5600
            f"{dollar_gap:,.0f}",   # 5,600
            f"{dollar_gap:.0f}"     # 5600
        ]
        
        for pattern in dollar_gap_patterns:
            if pattern in letter_content:
                results['dollar_gap_accurate'] = True
                break
        
        return results
    
    @staticmethod
    def validate_benchmark_facts(letter_content: str, expected_benchmark_data: Optional[Dict] = None) -> Dict[str, bool]:
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
        
        # Check percentile mention (various formats)
        percentile = expected_benchmark_data.get('user_percentile', 0)
        percentile_patterns = [
            f"{percentile:.0f}th percentile",
            f"{percentile:.0f} percentile",
            f"{percentile:.0f}th",
            f"at the {percentile:.0f}",
            f"the {percentile:.0f}th"
        ]
        
        for pattern in percentile_patterns:
            if pattern.lower() in letter_content.lower():
                results['percentile_mentioned'] = True
                break
        
        # Check market position
        market_position = expected_benchmark_data.get('market_position', '')
        if market_position.lower() in letter_content.lower():
            results['market_position_mentioned'] = True
        
        # Check median salary (with tolerance)
        median_salary = expected_benchmark_data.get('percentile_50', 0)
        salaries = NumericFactValidator.extract_salary_amounts(letter_content)
        for salary in salaries:
            if abs(salary - median_salary) < 100:  # $100 tolerance
                results['median_salary_mentioned'] = True
                break
        
        # Check location mention
        location = expected_benchmark_data.get('location', '')
        if location and location.lower() in letter_content.lower():
            results['location_mentioned'] = True
        
        # Check job title (flexible matching)
        job_title = expected_benchmark_data.get('occupation_title', '')
        if job_title:
            # Split job title into words for partial matching
            title_words = job_title.lower().split()
            content_lower = letter_content.lower()
            
            # Check if most words from the job title appear in the content
            matches = sum(1 for word in title_words if word in content_lower)
            if matches >= len(title_words) * 0.7:  # 70% of words must match
                results['job_title_mentioned'] = True
        
        return results


class TestNumericValidation:
    """Test cases for numeric fact validation utilities"""
    
    def test_salary_extraction_basic(self):
        """Test basic salary amount extraction"""
        text = "My current salary is $85,000 and I'm requesting $95,000."
        salaries = NumericFactValidator.extract_salary_amounts(text)
        
        assert len(salaries) == 2
        assert 85000.0 in salaries
        assert 95000.0 in salaries
    
    def test_salary_extraction_various_formats(self):
        """Test salary extraction with various formats"""
        text = """
        Current: $85,000
        Target: $95,000.00
        Market median: $110,500
        Range: $75000 to $125,000
        """
        salaries = NumericFactValidator.extract_salary_amounts(text)
        
        assert 85000.0 in salaries
        assert 95000.0 in salaries
        assert 110500.0 in salaries
        assert 125000.0 in salaries
    
    def test_percentage_extraction_basic(self):
        """Test basic percentage extraction"""
        text = "Inflation has been 8.2% over the past 2 years, creating a 11.8% gap."
        percentages = NumericFactValidator.extract_percentages(text)
        
        assert len(percentages) == 2
        assert 8.2 in percentages
        assert 11.8 in percentages
    
    def test_percentage_extraction_various_formats(self):
        """Test percentage extraction with various formats"""
        text = """
        Inflation: 8.2%
        Gap: 11.8 %
        Market position: 35th percentile (35%)
        Growth: 15%
        """
        percentages = NumericFactValidator.extract_percentages(text)
        
        assert 8.2 in percentages
        assert 11.8 in percentages
        assert 35 in percentages
        assert 15 in percentages
    
    def test_years_extraction_basic(self):
        """Test basic year extraction"""
        text = "Over the past 2 years, I have been with the company for 3 years total."
        years = NumericFactValidator.extract_years(text)
        
        assert 2 in years
        assert 3 in years
    
    def test_years_extraction_various_formats(self):
        """Test year extraction with various formats"""
        text = """
        Experience: 5 years
        Tenure: 3 yrs
        Duration: 2 year period
        """
        years = NumericFactValidator.extract_years(text)
        
        assert 5 in years
        assert 3 in years
        assert 2 in years
    
    def test_cpi_facts_validation_complete_match(self):
        """Test CPI facts validation with complete match"""
        letter_content = """
        Dear Manager,
        
        My current salary of $85,000 has lost purchasing power due to inflation.
        Based on CPI data, inflation has been 12.3% over the past 2 years.
        To maintain purchasing power, my salary should be $98,500, representing
        a 15.9% gap or $13,500 in lost value.
        
        Best regards,
        Employee
        """
        
        expected_cpi_data = {
            'current_salary': 85000,
            'adjusted_salary': 98500,
            'percentage_gap': 15.9,
            'dollar_gap': 13500,
            'inflation_rate': 12.3,
            'years_elapsed': 2
        }
        
        validation = NumericFactValidator.validate_cpi_facts(letter_content, expected_cpi_data)
        
        assert validation['current_salary_mentioned']
        assert validation['adjusted_salary_mentioned']
        assert validation['percentage_gap_accurate']
        assert validation['dollar_gap_accurate']
        assert validation['inflation_rate_accurate']
        assert validation['years_elapsed_accurate']
    
    def test_cpi_facts_validation_with_tolerance(self):
        """Test CPI facts validation with small tolerance"""
        letter_content = """
        Inflation has been approximately 12.1% over 2 years, creating a 16.1% gap.
        Current salary: $85,000
        Target: $98,500
        """
        
        expected_cpi_data = {
            'current_salary': 85000,
            'adjusted_salary': 98500,
            'percentage_gap': 15.9,  # Letter shows 16.1%, within 0.5% tolerance
            'dollar_gap': 13500,
            'inflation_rate': 12.3,  # Letter shows 12.1%, within 0.5% tolerance
            'years_elapsed': 2
        }
        
        validation = NumericFactValidator.validate_cpi_facts(letter_content, expected_cpi_data)
        
        assert validation['current_salary_mentioned']
        assert validation['adjusted_salary_mentioned']
        assert validation['percentage_gap_accurate']  # Within tolerance
        assert validation['inflation_rate_accurate']  # Within tolerance
        assert validation['years_elapsed_accurate']
    
    def test_benchmark_facts_validation_complete(self):
        """Test benchmark facts validation with complete data"""
        letter_content = """
        Market analysis shows I am at the 35th percentile for Software Engineers
        in San Francisco, CA, which is Below Market compared to the median
        salary of $95,000.
        """
        
        expected_benchmark_data = {
            'user_percentile': 35,
            'market_position': 'Below Market',
            'percentile_50': 95000,
            'location': 'San Francisco, CA',
            'occupation_title': 'Software Engineer'
        }
        
        validation = NumericFactValidator.validate_benchmark_facts(letter_content, expected_benchmark_data)
        
        assert validation['percentile_mentioned']
        assert validation['market_position_mentioned']
        assert validation['median_salary_mentioned']
        assert validation['location_mentioned']
        assert validation['job_title_mentioned']
    
    def test_benchmark_facts_validation_partial_data(self):
        """Test benchmark facts validation with partial data"""
        letter_content = """
        I am currently at the 65th percentile, which is At Market position.
        """
        
        expected_benchmark_data = {
            'user_percentile': 65,
            'market_position': 'At Market',
            'percentile_50': 75000,  # Not mentioned in letter
            'location': '',  # Not mentioned
            'occupation_title': ''  # Not mentioned
        }
        
        validation = NumericFactValidator.validate_benchmark_facts(letter_content, expected_benchmark_data)
        
        assert validation['percentile_mentioned']
        assert validation['market_position_mentioned']
        assert not validation['median_salary_mentioned']
        assert not validation['location_mentioned']
        assert not validation['job_title_mentioned']
    
    def test_benchmark_facts_validation_empty_data(self):
        """Test benchmark facts validation with no benchmark data"""
        letter_content = "This letter has no benchmark information."
        
        validation = NumericFactValidator.validate_benchmark_facts(letter_content, None)
        
        # All should be False when no benchmark data provided
        assert not any(validation.values())
    
    def test_edge_case_no_numeric_data(self):
        """Test extraction with no numeric data"""
        text = "This is a letter with no numbers or percentages or years mentioned."
        
        salaries = NumericFactValidator.extract_salary_amounts(text)
        percentages = NumericFactValidator.extract_percentages(text)
        years = NumericFactValidator.extract_years(text)
        
        assert len(salaries) == 0
        assert len(percentages) == 0
        assert len(years) == 0
    
    def test_edge_case_malformed_numbers(self):
        """Test extraction with malformed numbers"""
        text = """
        Salary: $85,000.50 (valid)
        Bad format: $85000 (no comma, but valid)
        Percentage: 15.5% (valid)
        Years: 3 years experience (valid)
        """
        
        salaries = NumericFactValidator.extract_salary_amounts(text)
        percentages = NumericFactValidator.extract_percentages(text)
        years = NumericFactValidator.extract_years(text)
        
        # Should still extract valid formats
        assert 85000.5 in salaries
        assert 15.5 in percentages
        assert 3 in years
    
    def test_comprehensive_letter_validation(self):
        """Test comprehensive validation of a realistic letter"""
        letter_content = """
        Dear Sarah Williams,
        
        I am writing to request a salary adjustment based on inflation analysis and market data.
        
        My current salary of $70,000 has experienced purchasing power decline due to inflation.
        Based on Consumer Price Index data, inflation has increased by 6.2% over the past 3 years.
        
        To maintain the same purchasing power, my salary should be adjusted to $75,600, 
        representing an 8.0% gap or $5,600 in lost purchasing power.
        
        Market analysis shows I am at the 65th percentile for Marketing Managers in Austin, TX,
        which is At Market compared to the median salary of $75,000.
        
        My key achievements include increasing lead generation by 60% and managing a $500K budget.
        
        I would appreciate the opportunity to discuss this adjustment.
        
        Best regards,
        David Chen
        """
        
        expected_cpi_data = {
            'current_salary': 70000,
            'adjusted_salary': 75600,
            'percentage_gap': 8.0,
            'dollar_gap': 5600,
            'inflation_rate': 6.2,
            'years_elapsed': 3
        }
        
        expected_benchmark_data = {
            'user_percentile': 65,
            'market_position': 'At Market',
            'percentile_50': 75000,
            'location': 'Austin, TX',
            'occupation_title': 'Marketing Manager'
        }
        
        # Validate CPI facts
        cpi_validation = NumericFactValidator.validate_cpi_facts(letter_content, expected_cpi_data)
        assert all(cpi_validation.values()), f"CPI validation failed: {cpi_validation}"
        
        # Validate benchmark facts
        benchmark_validation = NumericFactValidator.validate_benchmark_facts(letter_content, expected_benchmark_data)
        assert all(benchmark_validation.values()), f"Benchmark validation failed: {benchmark_validation}" 