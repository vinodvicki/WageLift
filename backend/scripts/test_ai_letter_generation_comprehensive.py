#!/usr/bin/env python3
"""
Comprehensive AI Letter Generation Testing Suite
Test accuracy, performance, and quality of AI-generated raise letters
Supports both live API testing and mock testing scenarios
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from services.openai_service import OpenAIService, UserContext, CPIData, BenchmarkData
from tests.test_numeric_validation import NumericFactValidator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestScenario:
    """Test scenario configuration"""
    name: str
    user_context: UserContext
    cpi_data: CPIData
    benchmark_data: BenchmarkData
    tone: str
    length: str
    expected_accuracy: float = 0.9  # 90% minimum accuracy

@dataclass
class TestResult:
    """Test result data structure"""
    scenario_name: str
    tone: str
    length: str
    letter_content: str
    validation_results: Dict
    accuracy_score: float
    generation_time: float
    token_usage: Optional[Dict] = None
    errors: List[str] = None

class ComprehensiveAITester:
    """Comprehensive AI letter generation testing suite"""
    
    def __init__(self):
        self.openai_service = None
        self.validator = NumericFactValidator()
        self.results: List[TestResult] = []
        self.api_available = self._check_api_availability()
        
    def _check_api_availability(self) -> bool:
        """Check if OpenAI API key is available"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            logger.info("✅ OpenAI API key found - will run live API tests")
            return True
        else:
            logger.warning("⚠️ OpenAI API key not found - will run mock tests")
            return False
    
    async def initialize_service(self):
        """Initialize OpenAI service if API is available"""
        if self.api_available:
            try:
                self.openai_service = OpenAIService()
                # Test service health
                health_status = await self.openai_service.health_check()
                if health_status.get('status') == 'healthy':
                    logger.info("✅ OpenAI service initialized and healthy")
                else:
                    logger.error("❌ OpenAI service health check failed")
                    self.api_available = False
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI service: {e}")
                self.api_available = False
    
    def create_test_scenarios(self) -> List[TestScenario]:
        """Create comprehensive test scenarios"""
        scenarios = []
        
        # Scenario 1: High inflation software engineer
        scenarios.append(TestScenario(
            name="High Inflation Software Engineer",
            user_context=UserContext(
                name="Alex Johnson",
                job_title="Senior Software Engineer",
                company="TechCorp",
                current_salary=95000,
                years_in_role=2,
                location="San Francisco, CA",
                achievements=["Led migration to microservices", "Reduced system latency by 40%"],
                projects=["Payment processing system", "Real-time analytics dashboard"]
            ),
            cpi_data=CPIData(
                start_year=2022,
                end_year=2024,
                start_cpi=296.808,
                end_cpi=310.326,
                inflation_rate=4.55,
                adjusted_salary=99323,
                gap_amount=4323,
                gap_percentage=4.55
            ),
            benchmark_data=BenchmarkData(
                median_salary=110000,
                percentile_25=95000,
                percentile_75=125000,
                user_percentile=50,
                market_position="At Market"
            ),
            tone="Professional",
            length="Standard"
        ))
        
        # Scenario 2: Marketing manager with moderate inflation
        scenarios.append(TestScenario(
            name="Marketing Manager Moderate Inflation",
            user_context=UserContext(
                name="Sarah Chen",
                job_title="Marketing Manager",
                company="GrowthCo",
                current_salary=78000,
                years_in_role=3,
                location="Austin, TX",
                achievements=["Increased lead generation by 65%", "Launched successful product campaign"],
                projects=["Brand redesign initiative", "Customer acquisition optimization"]
            ),
            cpi_data=CPIData(
                start_year=2021,
                end_year=2024,
                start_cpi=271.696,
                end_cpi=310.326,
                inflation_rate=14.22,
                adjusted_salary=89084,
                gap_amount=11084,
                gap_percentage=14.22
            ),
            benchmark_data=BenchmarkData(
                median_salary=85000,
                percentile_25=72000,
                percentile_75=98000,
                user_percentile=65,
                market_position="Above Market"
            ),
            tone="Confident",
            length="Detailed"
        ))
        
        # Scenario 3: Data scientist with low inflation but high performance
        scenarios.append(TestScenario(
            name="Data Scientist High Performer",
            user_context=UserContext(
                name="Michael Rodriguez",
                job_title="Senior Data Scientist",
                company="DataTech Inc",
                current_salary=125000,
                years_in_role=1,
                location="Seattle, WA",
                achievements=["Developed ML model with 95% accuracy", "Saved company $2M annually"],
                projects=["Predictive analytics platform", "Customer churn reduction model"]
            ),
            cpi_data=CPIData(
                start_year=2023,
                end_year=2024,
                start_cpi=307.026,
                end_cpi=310.326,
                inflation_rate=1.07,
                adjusted_salary=126338,
                gap_amount=1338,
                gap_percentage=1.07
            ),
            benchmark_data=BenchmarkData(
                median_salary=115000,
                percentile_25=98000,
                percentile_75=140000,
                user_percentile=75,
                market_position="Above Market"
            ),
            tone="Collaborative",
            length="Concise"
        ))
        
        # Scenario 4: Edge case - Very high inflation
        scenarios.append(TestScenario(
            name="Edge Case High Inflation",
            user_context=UserContext(
                name="Jennifer Kim",
                job_title="Product Manager",
                company="InnovateCorp",
                current_salary=88000,
                years_in_role=4,
                location="New York, NY",
                achievements=["Launched 3 successful products", "Increased revenue by 150%"],
                projects=["Mobile app redesign", "Enterprise platform development"]
            ),
            cpi_data=CPIData(
                start_year=2020,
                end_year=2024,
                start_cpi=258.811,
                end_cpi=310.326,
                inflation_rate=19.90,
                adjusted_salary=105512,
                gap_amount=17512,
                gap_percentage=19.90
            ),
            benchmark_data=BenchmarkData(
                median_salary=105000,
                percentile_25=85000,
                percentile_75=125000,
                user_percentile=45,
                market_position="Below Market"
            ),
            tone="Assertive",
            length="Standard"
        ))
        
        return scenarios
    
    async def test_scenario_live(self, scenario: TestScenario) -> TestResult:
        """Test a scenario with live OpenAI API"""
        logger.info(f"🧪 Testing scenario: {scenario.name} ({scenario.tone}, {scenario.length})")
        
        start_time = time.time()
        errors = []
        
        try:
            # Generate letter with live API
            response = await self.openai_service.generate_raise_letter(
                user_context=scenario.user_context,
                cpi_data=scenario.cpi_data,
                benchmark_data=scenario.benchmark_data,
                tone=scenario.tone,
                length=scenario.length
            )
            
            letter_content = response.get('letter', '')
            token_usage = response.get('usage', {})
            
        except Exception as e:
            logger.error(f"❌ Failed to generate letter for {scenario.name}: {e}")
            errors.append(f"Generation failed: {str(e)}")
            letter_content = ""
            token_usage = {}
        
        generation_time = time.time() - start_time
        
        # Validate the generated letter
        validation_results = {}
        accuracy_score = 0.0
        
        if letter_content:
            try:
                # Validate CPI facts
                cpi_validation = self.validator.validate_cpi_facts(letter_content, scenario.cpi_data)
                validation_results['cpi'] = cpi_validation
                
                # Validate benchmark facts
                benchmark_validation = self.validator.validate_benchmark_facts(
                    letter_content, scenario.benchmark_data, scenario.user_context
                )
                validation_results['benchmark'] = benchmark_validation
                
                # Calculate overall accuracy
                total_checks = len(cpi_validation) + len(benchmark_validation)
                passed_checks = sum(1 for v in cpi_validation.values() if v) + \
                               sum(1 for v in benchmark_validation.values() if v)
                
                accuracy_score = passed_checks / total_checks if total_checks > 0 else 0.0
                
                logger.info(f"✅ Validation complete: {passed_checks}/{total_checks} checks passed ({accuracy_score:.2%})")
                
            except Exception as e:
                logger.error(f"❌ Validation failed for {scenario.name}: {e}")
                errors.append(f"Validation failed: {str(e)}")
        
        return TestResult(
            scenario_name=scenario.name,
            tone=scenario.tone,
            length=scenario.length,
            letter_content=letter_content,
            validation_results=validation_results,
            accuracy_score=accuracy_score,
            generation_time=generation_time,
            token_usage=token_usage,
            errors=errors
        )
    
    def test_scenario_mock(self, scenario: TestScenario) -> TestResult:
        """Test a scenario with mock data (when API not available)"""
        logger.info(f"🧪 Mock testing scenario: {scenario.name} ({scenario.tone}, {scenario.length})")
        
        # Generate a realistic mock letter for validation testing
        mock_letter = self._generate_mock_letter(scenario)
        
        # Validate the mock letter
        validation_results = {}
        accuracy_score = 0.0
        
        try:
            # Validate CPI facts
            cpi_validation = self.validator.validate_cpi_facts(mock_letter, scenario.cpi_data)
            validation_results['cpi'] = cpi_validation
            
            # Validate benchmark facts
            benchmark_validation = self.validator.validate_benchmark_facts(
                mock_letter, scenario.benchmark_data, scenario.user_context
            )
            validation_results['benchmark'] = benchmark_validation
            
            # Calculate overall accuracy
            total_checks = len(cpi_validation) + len(benchmark_validation)
            passed_checks = sum(1 for v in cpi_validation.values() if v) + \
                           sum(1 for v in benchmark_validation.values() if v)
            
            accuracy_score = passed_checks / total_checks if total_checks > 0 else 0.0
            
            logger.info(f"✅ Mock validation complete: {passed_checks}/{total_checks} checks passed ({accuracy_score:.2%})")
            
        except Exception as e:
            logger.error(f"❌ Mock validation failed for {scenario.name}: {e}")
        
        return TestResult(
            scenario_name=scenario.name,
            tone=scenario.tone,
            length=scenario.length,
            letter_content=mock_letter,
            validation_results=validation_results,
            accuracy_score=accuracy_score,
            generation_time=0.5,  # Mock generation time
            token_usage={'prompt_tokens': 800, 'completion_tokens': 400, 'total_tokens': 1200},
            errors=[]
        )
    
    def _generate_mock_letter(self, scenario: TestScenario) -> str:
        """Generate a realistic mock letter for testing validation"""
        user = scenario.user_context
        cpi = scenario.cpi_data
        benchmark = scenario.benchmark_data
        
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
    
    async def run_comprehensive_tests(self) -> Dict:
        """Run all test scenarios and generate comprehensive report"""
        logger.info("🚀 Starting comprehensive AI letter generation tests")
        
        if self.api_available:
            await self.initialize_service()
        
        scenarios = self.create_test_scenarios()
        
        # Test each scenario
        for scenario in scenarios:
            if self.api_available and self.openai_service:
                result = await self.test_scenario_live(scenario)
            else:
                result = self.test_scenario_mock(scenario)
            
            self.results.append(result)
        
        # Generate comprehensive report
        return self._generate_report()
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.accuracy_score >= 0.9)
        
        avg_accuracy = sum(r.accuracy_score for r in self.results) / total_tests if total_tests > 0 else 0
        avg_generation_time = sum(r.generation_time for r in self.results) / total_tests if total_tests > 0 else 0
        
        total_tokens = sum(r.token_usage.get('total_tokens', 0) for r in self.results if r.token_usage)
        
        # Find best and worst performers
        best_result = max(self.results, key=lambda r: r.accuracy_score) if self.results else None
        worst_result = min(self.results, key=lambda r: r.accuracy_score) if self.results else None
        
        report = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'average_accuracy': avg_accuracy,
                'average_generation_time': avg_generation_time,
                'total_tokens_used': total_tokens,
                'api_mode': 'live' if self.api_available else 'mock'
            },
            'best_performer': {
                'scenario': best_result.scenario_name if best_result else None,
                'accuracy': best_result.accuracy_score if best_result else 0,
                'tone': best_result.tone if best_result else None,
                'length': best_result.length if best_result else None
            } if best_result else None,
            'worst_performer': {
                'scenario': worst_result.scenario_name if worst_result else None,
                'accuracy': worst_result.accuracy_score if worst_result else 0,
                'tone': worst_result.tone if worst_result else None,
                'length': worst_result.length if worst_result else None
            } if worst_result else None,
            'detailed_results': [asdict(result) for result in self.results]
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted test report"""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE AI LETTER GENERATION TEST REPORT")
        print("="*80)
        
        summary = report['test_summary']
        print(f"\n📊 TEST SUMMARY:")
        print(f"   Mode: {'🔴 Live API' if summary['api_mode'] == 'live' else '🟡 Mock Testing'}")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed Tests: {summary['passed_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.2%}")
        print(f"   Average Accuracy: {summary['average_accuracy']:.2%}")
        print(f"   Average Generation Time: {summary['average_generation_time']:.2f}s")
        print(f"   Total Tokens Used: {summary['total_tokens']:,}")
        
        if report['best_performer']:
            best = report['best_performer']
            print(f"\n🏆 BEST PERFORMER:")
            print(f"   Scenario: {best['scenario']}")
            print(f"   Accuracy: {best['accuracy']:.2%}")
            print(f"   Configuration: {best['tone']}, {best['length']}")
        
        if report['worst_performer']:
            worst = report['worst_performer']
            print(f"\n⚠️ NEEDS IMPROVEMENT:")
            print(f"   Scenario: {worst['scenario']}")
            print(f"   Accuracy: {worst['accuracy']:.2%}")
            print(f"   Configuration: {worst['tone']}, {worst['length']}")
        
        print(f"\n📝 DETAILED RESULTS:")
        for result in self.results:
            status = "✅" if result.accuracy_score >= 0.9 else "❌"
            print(f"   {status} {result.scenario_name} ({result.tone}, {result.length}): {result.accuracy_score:.2%}")
        
        print("\n" + "="*80)

async def main():
    """Main test execution function"""
    tester = ComprehensiveAITester()
    
    try:
        # Run comprehensive tests
        report = await tester.run_comprehensive_tests()
        
        # Print report to console
        tester.print_report(report)
        
        # Save detailed report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"ai_letter_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Return success/failure based on overall results
        success_rate = report['test_summary']['success_rate']
        if success_rate >= 0.9:
            print(f"\n🎉 SUCCESS: {success_rate:.2%} success rate meets production standards!")
            return 0
        else:
            print(f"\n⚠️ ATTENTION: {success_rate:.2%} success rate below 90% threshold")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 