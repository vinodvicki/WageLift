#!/usr/bin/env python3
"""
Simple AI Letter Generation Accuracy Test
Tests the accuracy of AI-generated raise letters with or without OpenAI API
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test if we can import our validation system
try:
    from tests.test_numeric_validation import NumericFactValidator
    print("✅ Validation system imported successfully")
except ImportError as e:
    print(f"❌ Failed to import validation system: {e}")
    sys.exit(1)

# Test if we can import OpenAI service components
try:
    from app.services.openai_service import (
        OpenAIService,
        RaiseLetterRequest,
        LetterTone,
        LetterLength,
        OpenAIServiceError,
        UserContext,
        CPIData,
        BenchmarkData
    )
    print("✅ OpenAI service components imported successfully")
except ImportError as e:
    print(f"❌ Failed to import OpenAI service: {e}")
    sys.exit(1)

class SimpleAITester:
    """Simple AI letter generation tester"""
    
    def __init__(self):
        self.validator = NumericFactValidator()
        self.api_available = self._check_api_availability()
        self.openai_service = None
    
    def _check_api_availability(self) -> bool:
        """Check if OpenAI API key is available"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✅ OpenAI API key found - will run live API tests")
            return True
        else:
            print("⚠️ OpenAI API key not found - will run validation tests with mock data")
            return False
    
    async def initialize_service(self):
        """Initialize OpenAI service if API is available"""
        if self.api_available:
            try:
                self.openai_service = OpenAIService()
                print("✅ OpenAI service initialized")
                return True
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI service: {e}")
                self.api_available = False
                return False
        return False
    
    def create_test_scenario(self):
        """Create a test scenario for validation"""
        return {
            'user_context': UserContext(
                name="Alex Johnson",
                job_title="Software Engineer",
                company="TechCorp",
                current_salary=95000,
                years_in_role=2,
                location="San Francisco, CA",
                achievements=["Led microservices migration", "Reduced system latency by 40%"],
                projects=["Payment processing system", "Analytics dashboard"]
            ),
            'cpi_data': CPIData(
                start_year=2022,
                end_year=2024,
                start_cpi=296.808,
                end_cpi=310.326,
                inflation_rate=4.55,
                adjusted_salary=99323,
                gap_amount=4323,
                gap_percentage=4.55
            ),
            'benchmark_data': BenchmarkData(
                median_salary=110000,
                percentile_25=95000,
                percentile_75=125000,
                user_percentile=50,
                market_position="At Market"
            )
        }
    
    def generate_mock_letter(self, scenario):
        """Generate a mock letter for testing validation"""
        user = scenario['user_context']
        cpi = scenario['cpi_data']
        benchmark = scenario['benchmark_data']
        
        return f"""Subject: Request for Salary Adjustment - {user.name}

Dear Hiring Manager,

I am writing to request a salary adjustment based on inflation data and market analysis.

Over the past {cpi.end_year - cpi.start_year} years in my role as {user.job_title}, inflation has increased by {cpi.inflation_rate:.1f}%. My current salary of ${user.current_salary:,} would need to be ${cpi.adjusted_salary:,} to maintain the same purchasing power, representing a gap of ${cpi.gap_amount:,}.

According to market data for {user.job_title} positions in {user.location}, the median salary is ${benchmark.median_salary:,}. My current compensation places me at the {benchmark.user_percentile}th percentile, which is {benchmark.market_position}.

During my {user.years_in_role} years with the company, I have achieved significant results including:
- {user.achievements[0] if user.achievements else 'Key achievement'}
- {user.achievements[1] if len(user.achievements) > 1 else 'Additional achievement'}

I have successfully delivered projects such as:
- {user.projects[0] if user.projects else 'Major project'}
- {user.projects[1] if len(user.projects) > 1 else 'Additional project'}

Based on this analysis, I respectfully request a salary adjustment to ${cpi.adjusted_salary:,} to account for inflation impact.

Thank you for your consideration.

Sincerely,
{user.name}"""
    
    async def test_with_live_api(self, scenario):
        """Test with live OpenAI API"""
        print("🔴 Testing with live OpenAI API...")
        
        try:
            # Create request (need to convert dataclasses to dicts for the API)
            request_data = {
                'user_context': {
                    'name': scenario['user_context'].name,
                    'job_title': scenario['user_context'].job_title,
                    'company': scenario['user_context'].company,
                    'current_salary': scenario['user_context'].current_salary,
                    'years_in_role': scenario['user_context'].years_in_role,
                    'location': scenario['user_context'].location,
                    'achievements': scenario['user_context'].achievements,
                    'projects': scenario['user_context'].projects
                },
                'cpi_data': {
                    'start_year': scenario['cpi_data'].start_year,
                    'end_year': scenario['cpi_data'].end_year,
                    'start_cpi': scenario['cpi_data'].start_cpi,
                    'end_cpi': scenario['cpi_data'].end_cpi,
                    'inflation_rate': scenario['cpi_data'].inflation_rate,
                    'adjusted_salary': scenario['cpi_data'].adjusted_salary,
                    'gap_amount': scenario['cpi_data'].gap_amount,
                    'gap_percentage': scenario['cpi_data'].gap_percentage
                },
                'benchmark_data': {
                    'median_salary': scenario['benchmark_data'].median_salary,
                    'percentile_25': scenario['benchmark_data'].percentile_25,
                    'percentile_75': scenario['benchmark_data'].percentile_75,
                    'user_percentile': scenario['benchmark_data'].user_percentile,
                    'market_position': scenario['benchmark_data'].market_position
                }
            }
            
            request = RaiseLetterRequest(**request_data)
            
            # Generate letter
            start_time = time.time()
            response = await self.openai_service.generate_raise_letter(request)
            generation_time = time.time() - start_time
            
            print(f"✅ Letter generated in {generation_time:.2f} seconds")
            print(f"📊 Token usage: {response.generation_metadata.get('tokens_used', 'N/A')}")
            
            return response.letter_content
            
        except Exception as e:
            print(f"❌ Live API test failed: {e}")
            return None
    
    def test_with_mock_data(self, scenario):
        """Test with mock data"""
        print("🟡 Testing with mock data...")
        
        mock_letter = self.generate_mock_letter(scenario)
        print("✅ Mock letter generated")
        
        return mock_letter
    
    def validate_letter_accuracy(self, letter_content, scenario):
        """Validate the accuracy of generated letter"""
        print("\n🔍 Validating letter accuracy...")
        
        # Convert dataclasses to dicts for validation
        cpi_data_dict = {
            'current_salary': scenario['cpi_data'].adjusted_salary,  # Use adjusted as "current" for validation
            'adjusted_salary': scenario['cpi_data'].adjusted_salary,
            'percentage_gap': scenario['cpi_data'].gap_percentage,
            'dollar_gap': scenario['cpi_data'].gap_amount,
            'inflation_rate': scenario['cpi_data'].inflation_rate,
            'years_elapsed': scenario['cpi_data'].end_year - scenario['cpi_data'].start_year
        }
        
        benchmark_data_dict = {
            'median_salary': scenario['benchmark_data'].median_salary,
            'user_percentile': scenario['benchmark_data'].user_percentile,
            'market_position': scenario['benchmark_data'].market_position
        }
        
        user_context_dict = {
            'job_title': scenario['user_context'].job_title,
            'location': scenario['user_context'].location
        }
        
        # Validate CPI facts
        cpi_validation = self.validator.validate_cpi_facts(letter_content, cpi_data_dict)
        print("\n📈 CPI Facts Validation:")
        for check, passed in cpi_validation.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check.replace('_', ' ').title()}")
        
        # Validate benchmark facts  
        benchmark_validation = self.validator.validate_benchmark_facts(
            letter_content, benchmark_data_dict, user_context_dict
        )
        print("\n📊 Benchmark Facts Validation:")
        for check, passed in benchmark_validation.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check.replace('_', ' ').title()}")
        
        # Calculate overall accuracy
        total_checks = len(cpi_validation) + len(benchmark_validation)
        passed_checks = sum(cpi_validation.values()) + sum(benchmark_validation.values())
        accuracy = passed_checks / total_checks if total_checks > 0 else 0
        
        print(f"\n🎯 Overall Accuracy: {passed_checks}/{total_checks} ({accuracy:.2%})")
        
        return {
            'cpi_validation': cpi_validation,
            'benchmark_validation': benchmark_validation,
            'accuracy_score': accuracy,
            'total_checks': total_checks,
            'passed_checks': passed_checks
        }
    
    async def run_test(self):
        """Run the complete test"""
        print("🚀 Starting AI Letter Generation Accuracy Test")
        print("="*60)
        
        # Initialize service if API available
        if self.api_available:
            await self.initialize_service()
        
        # Create test scenario
        scenario = self.create_test_scenario()
        print(f"📝 Test Scenario: {scenario['user_context'].name} - {scenario['user_context'].job_title}")
        
        # Generate letter
        if self.api_available and self.openai_service:
            letter_content = await self.test_with_live_api(scenario)
        else:
            letter_content = self.test_with_mock_data(scenario)
        
        if not letter_content:
            print("❌ Failed to generate letter content")
            return False
        
        # Validate accuracy
        validation_results = self.validate_letter_accuracy(letter_content, scenario)
        
        # Print summary
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        print(f"Mode: {'🔴 Live API' if self.api_available and self.openai_service else '🟡 Mock Testing'}")
        print(f"Accuracy: {validation_results['accuracy_score']:.2%}")
        print(f"Status: {'✅ PASS' if validation_results['accuracy_score'] >= 0.9 else '⚠️ NEEDS IMPROVEMENT'}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"ai_accuracy_test_{timestamp}.json"
        
        results = {
            'timestamp': timestamp,
            'mode': 'live_api' if self.api_available and self.openai_service else 'mock',
            'scenario': {
                'name': scenario['user_context'].name,
                'job_title': scenario['user_context'].job_title,
                'company': scenario['user_context'].company
            },
            'validation_results': validation_results,
            'letter_content': letter_content
        }
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {results_file}")
        
        return validation_results['accuracy_score'] >= 0.9

async def main():
    """Main test execution"""
    tester = SimpleAITester()
    
    try:
        success = await tester.run_test()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 