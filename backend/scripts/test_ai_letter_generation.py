#!/usr/bin/env python3
"""
AI Letter Generation Integration Test Script

This script performs comprehensive testing of AI-generated raise letters
with real OpenAI API calls and validates numeric fact accuracy.

Usage:
    python scripts/test_ai_letter_generation.py
    
Environment:
    Requires OPENAI_API_KEY environment variable
"""

import os
import sys
import asyncio
import json
from typing import Dict, List
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.openai_service import (
    OpenAIService,
    RaiseLetterRequest,
    LetterTone,
    LetterLength,
    OpenAIServiceError
)
from tests.test_numeric_validation import NumericFactValidator


class AILetterGenerationTester:
    """Comprehensive tester for AI letter generation with numeric validation"""
    
    def __init__(self):
        self.test_results = []
        self.validator = NumericFactValidator()
        self.openai_service = None
        self.api_available = self._check_api_availability()
    
    def _check_api_availability(self) -> bool:
        """Check if OpenAI API key is available"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✅ OpenAI API key found - will run live API tests")
            return True
        else:
            print("⚠️ OpenAI API key not found - will run mock tests")
            return False
    
    async def initialize_service(self):
        """Initialize OpenAI service if API is available"""
        if self.api_available:
            try:
                self.openai_service = OpenAIService()
                # Test service connection
                is_connected = await self.openai_service.validate_api_connection()
                if is_connected:
                    print("✅ OpenAI service initialized and connected")
                else:
                    print("❌ OpenAI service connection validation failed")
                    self.api_available = False
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI service: {e}")
                self.api_available = False
    
    def get_test_scenarios(self) -> Dict:
        """Get comprehensive test scenarios"""
        return {
            'high_inflation_software_engineer': {
                'name': 'High Inflation - Software Engineer',
                'user_context': {
                    'name': 'Alice Johnson',
                    'job_title': 'Software Engineer',
                    'company': 'TechCorp Inc',
                    'department': 'Engineering',
                    'manager_name': 'Bob Smith',
                    'years_at_company': 3,
                    'key_achievements': [
                        'Led development of microservices architecture reducing deployment time by 60%',
                        'Reduced system latency by 40% through database optimization',
                        'Mentored 2 junior developers, improving team productivity'
                    ],
                    'recent_projects': [
                        'API Gateway Implementation - Unified 15 services under single gateway',
                        'Database Migration Project - Migrated legacy MySQL to PostgreSQL'
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
            'moderate_inflation_marketing_manager': {
                'name': 'Moderate Inflation - Marketing Manager',
                'user_context': {
                    'name': 'David Chen',
                    'job_title': 'Marketing Manager',
                    'company': 'Growth Solutions LLC',
                    'department': 'Marketing',
                    'manager_name': 'Sarah Williams',
                    'years_at_company': 4,
                    'key_achievements': [
                        'Increased lead generation by 60% through strategic campaign optimization',
                        'Launched 3 successful product campaigns generating $2M in revenue',
                        'Managed $500K marketing budget with 15% under-spend and 120% ROI'
                    ],
                    'recent_projects': [
                        'Digital Transformation Initiative - Implemented marketing automation platform',
                        'Customer Segmentation Analysis - Identified 5 high-value customer personas'
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
            'low_inflation_high_performer': {
                'name': 'Low Inflation - High Performer Data Scientist',
                'user_context': {
                    'name': 'Maria Rodriguez',
                    'job_title': 'Data Scientist',
                    'company': 'Analytics Pro',
                    'department': 'Data Science',
                    'manager_name': 'James Park',
                    'years_at_company': 2,
                    'key_achievements': [
                        'Built ML model with 95% accuracy improving fraud detection by 40%',
                        'Automated reporting pipeline saving 20 hours/week across team',
                        'Published 2 research papers in top-tier ML conferences'
                    ],
                    'recent_projects': [
                        'Predictive Analytics Platform - Real-time customer behavior prediction',
                        'Real-time Dashboard Development - Executive KPI monitoring system'
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
    
    async def test_scenario(self, scenario_name: str, scenario_data: Dict, tone: LetterTone, length: LetterLength) -> Dict:
        """Test a specific scenario with given tone and length"""
        print(f"\n🧪 Testing: {scenario_data['name']} - {tone.value.title()} Tone - {length.value.title()} Length")
        
        try:
            # Check if service is available
            if not self.api_available or not self.openai_service:
                raise Exception("OpenAI service not available")
            
            # Create request
            request = RaiseLetterRequest(
                user_context=scenario_data['user_context'],
                cpi_data=scenario_data['cpi_data'],
                benchmark_data=scenario_data['benchmark_data'],
                tone=tone,
                length=length
            )
            
            # Generate letter
            result = await self.openai_service.generate_raise_letter(request)
            
            # Validate CPI facts
            cpi_validation = self.validator.validate_cpi_facts(
                result.letter_content, scenario_data['cpi_data']
            )
            
            # Validate benchmark facts
            benchmark_validation = self.validator.validate_benchmark_facts(
                result.letter_content, scenario_data['benchmark_data']
            )
            
            # Calculate accuracy scores
            cpi_accuracy = sum(cpi_validation.values()) / len(cpi_validation) * 100
            benchmark_accuracy = sum(benchmark_validation.values()) / len(benchmark_validation) * 100
            overall_accuracy = (cpi_accuracy + benchmark_accuracy) / 2
            
            test_result = {
                'scenario': scenario_name,
                'scenario_name': scenario_data['name'],
                'tone': tone.value,
                'length': length.value,
                'success': True,
                'letter_length': len(result.letter_content),
                'word_count': len(result.letter_content.split()),
                'cpi_validation': cpi_validation,
                'benchmark_validation': benchmark_validation,
                'cpi_accuracy': cpi_accuracy,
                'benchmark_accuracy': benchmark_accuracy,
                'overall_accuracy': overall_accuracy,
                'generation_metadata': result.generation_metadata,
                'letter_preview': result.letter_content[:200] + "..." if len(result.letter_content) > 200 else result.letter_content,
                'letter_content': result.letter_content  # Store full content for debugging
            }
            
            # Print results
            print(f"✅ Success - Overall Accuracy: {overall_accuracy:.1f}%")
            print(f"   CPI Facts: {cpi_accuracy:.1f}% | Benchmark Facts: {benchmark_accuracy:.1f}%")
            print(f"   Letter: {len(result.letter_content)} chars, {len(result.letter_content.split())} words")
            print(f"   Tokens: {result.generation_metadata.get('tokens_used', 'N/A')}")
            
            # Show detailed validation if not perfect
            if overall_accuracy < 100:
                print(f"   ⚠️  CPI Issues: {[k for k, v in cpi_validation.items() if not v]}")
                print(f"   ⚠️  Benchmark Issues: {[k for k, v in benchmark_validation.items() if not v]}")
            
            return test_result
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            return {
                'scenario': scenario_name,
                'scenario_name': scenario_data['name'],
                'tone': tone.value,
                'length': length.value,
                'success': False,
                'error': str(e),
                'cpi_accuracy': 0,
                'benchmark_accuracy': 0,
                'overall_accuracy': 0
            }
    
    async def run_comprehensive_tests(self):
        """Run comprehensive tests across all scenarios, tones, and lengths"""
        print("🚀 Starting Comprehensive AI Letter Generation Tests")
        print("=" * 60)
        
        scenarios = self.get_test_scenarios()
        tones = [LetterTone.PROFESSIONAL, LetterTone.CONFIDENT, LetterTone.COLLABORATIVE]
        lengths = [LetterLength.CONCISE, LetterLength.STANDARD, LetterLength.DETAILED]
        
        total_tests = len(scenarios) * len(tones) * len(lengths)
        current_test = 0
        
        for scenario_key, scenario_data in scenarios.items():
            for tone in tones:
                for length in lengths:
                    current_test += 1
                    print(f"\n[{current_test}/{total_tests}]", end="")
                    
                    result = await self.test_scenario(scenario_key, scenario_data, tone, length)
                    self.test_results.append(result)
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate and display comprehensive summary report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        successful_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Successful: {len(successful_tests)} ({len(successful_tests)/len(self.test_results)*100:.1f}%)")
        print(f"Failed: {len(failed_tests)} ({len(failed_tests)/len(self.test_results)*100:.1f}%)")
        
        if successful_tests:
            avg_cpi_accuracy = sum(r['cpi_accuracy'] for r in successful_tests) / len(successful_tests)
            avg_benchmark_accuracy = sum(r['benchmark_accuracy'] for r in successful_tests) / len(successful_tests)
            avg_overall_accuracy = sum(r['overall_accuracy'] for r in successful_tests) / len(successful_tests)
            
            print(f"\n📈 ACCURACY METRICS:")
            print(f"Average CPI Facts Accuracy: {avg_cpi_accuracy:.1f}%")
            print(f"Average Benchmark Facts Accuracy: {avg_benchmark_accuracy:.1f}%")
            print(f"Average Overall Accuracy: {avg_overall_accuracy:.1f}%")
            
            # Accuracy by tone
            print(f"\n🎭 ACCURACY BY TONE:")
            for tone in [LetterTone.PROFESSIONAL, LetterTone.CONFIDENT, LetterTone.COLLABORATIVE]:
                tone_results = [r for r in successful_tests if r['tone'] == tone.value]
                if tone_results:
                    tone_avg = sum(r['overall_accuracy'] for r in tone_results) / len(tone_results)
                    print(f"{tone.value.title()}: {tone_avg:.1f}%")
            
            # Accuracy by length
            print(f"\n📏 ACCURACY BY LENGTH:")
            for length in [LetterLength.CONCISE, LetterLength.STANDARD, LetterLength.DETAILED]:
                length_results = [r for r in successful_tests if r['length'] == length.value]
                if length_results:
                    length_avg = sum(r['overall_accuracy'] for r in length_results) / len(length_results)
                    print(f"{length.value.title()}: {length_avg:.1f}%")
            
            # Token usage stats
            total_tokens = sum(r.get('generation_metadata', {}).get('tokens_used', 0) for r in successful_tests)
            avg_tokens = total_tokens / len(successful_tests) if successful_tests else 0
            print(f"\n🔢 TOKEN USAGE:")
            print(f"Total Tokens Used: {total_tokens:,}")
            print(f"Average Tokens per Letter: {avg_tokens:.0f}")
            
            # Best and worst performers
            best_result = max(successful_tests, key=lambda x: x['overall_accuracy'])
            worst_result = min(successful_tests, key=lambda x: x['overall_accuracy'])
            
            print(f"\n🏆 BEST PERFORMER:")
            print(f"Scenario: {best_result['scenario_name']}")
            print(f"Tone: {best_result['tone'].title()}, Length: {best_result['length'].title()}")
            print(f"Accuracy: {best_result['overall_accuracy']:.1f}%")
            
            print(f"\n⚠️  NEEDS IMPROVEMENT:")
            print(f"Scenario: {worst_result['scenario_name']}")
            print(f"Tone: {worst_result['tone'].title()}, Length: {worst_result['length'].title()}")
            print(f"Accuracy: {worst_result['overall_accuracy']:.1f}%")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"- {test['scenario_name']} ({test['tone']}/{test['length']}): {test['error']}")
        
        # Save detailed results to file
        results_file = Path(__file__).parent.parent / "test_results_ai_generation.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Detailed results saved to: {results_file}")
    
    async def test_specific_scenario(self, scenario_name: str, tone: str = "professional", length: str = "standard"):
        """Test a specific scenario for debugging"""
        scenarios = self.get_test_scenarios()
        if scenario_name not in scenarios:
            print(f"❌ Scenario '{scenario_name}' not found. Available: {list(scenarios.keys())}")
            return
        
        tone_enum = LetterTone(tone.lower())
        length_enum = LetterLength(length.lower())
        
        result = await self.test_scenario(scenario_name, scenarios[scenario_name], tone_enum, length_enum)
        
        if result['success']:
            print(f"\n📄 GENERATED LETTER:")
            print("-" * 40)
            print(result.get('letter_content', 'Letter content not available'))
            print("-" * 40)


async def main():
    """Main test execution"""
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    tester = AILetterGenerationTester()
    await tester.initialize_service()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # Quick test - just one scenario
            print("🏃‍♂️ Running Quick Test (1 scenario)")
            scenarios = tester.get_test_scenarios()
            first_scenario = next(iter(scenarios.items()))
            result = await tester.test_scenario(
                first_scenario[0], 
                first_scenario[1], 
                LetterTone.PROFESSIONAL, 
                LetterLength.STANDARD
            )
            tester.test_results.append(result)
            tester.generate_summary_report()
        elif sys.argv[1] == "--scenario" and len(sys.argv) > 2:
            # Test specific scenario
            scenario_name = sys.argv[2]
            tone = sys.argv[3] if len(sys.argv) > 3 else "professional"
            length = sys.argv[4] if len(sys.argv) > 4 else "standard"
            await tester.test_specific_scenario(scenario_name, tone, length)
        else:
            print("Usage:")
            print("  python scripts/test_ai_letter_generation.py                    # Full test suite")
            print("  python scripts/test_ai_letter_generation.py --quick           # Quick test")
            print("  python scripts/test_ai_letter_generation.py --scenario <name> [tone] [length]")
    else:
        # Full comprehensive test
        await tester.run_comprehensive_tests()


if __name__ == "__main__":
    asyncio.run(main()) 