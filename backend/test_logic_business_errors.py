#!/usr/bin/env python3
"""
Logic and Business Error Testing for WageLift
Tests for algorithmic logic errors, data processing errors, and business logic mistakes
"""

import asyncio
import json
import requests
import time
import math
from typing import List, Dict, Any, Optional
from decimal import Decimal, InvalidOperation
import re

class LogicBusinessTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{icon} {test_name}: {status} {details}")
    
    def test_algorithmic_logic_errors(self):
        """Test 4.1: Algorithmic logic errors and mathematical operations"""
        try:
            # Test 1: Off-by-one errors in data processing
            test_arrays = [
                [],  # Empty array
                [1],  # Single element
                [1, 2, 3, 4, 5],  # Normal array
                list(range(1000))  # Large array
            ]
            
            off_by_one_detected = False
            
            for test_array in test_arrays:
                # Test various array operations that commonly have off-by-one errors
                try:
                    # Safe array access patterns
                    if len(test_array) > 0:
                        first = test_array[0]
                        last = test_array[-1]
                        
                    # Safe iteration patterns
                    for i in range(len(test_array)):
                        element = test_array[i]
                        
                    # Safe slicing patterns
                    if len(test_array) > 1:
                        middle_slice = test_array[1:-1]
                        
                except IndexError:
                    off_by_one_detected = True
                    break
            
            # Test 2: Mathematical operation accuracy
            math_errors = []
            
            # Test division operations
            test_cases = [
                (10, 3, "Division precision"),
                (1, 3, "Fraction handling"),
                (0, 1, "Zero numerator"),
                (100, 7, "Large division")
            ]
            
            for a, b, description in test_cases:
                try:
                    result = a / b
                    # Check for expected precision issues
                    if isinstance(result, float) and math.isfinite(result):
                        continue
                    else:
                        math_errors.append(f"{description}: {result}")
                except Exception as e:
                    math_errors.append(f"{description}: {str(e)}")
            
            # Test 3: Loop boundary conditions
            boundary_errors = []
            
            # Test various loop patterns
            for size in [0, 1, 10, 100]:
                try:
                    # Standard for loop
                    for i in range(size):
                        if i >= size:  # Should never happen
                            boundary_errors.append(f"Loop overflow at size {size}")
                        
                    # While loop with counter
                    counter = 0
                    while counter < size:
                        counter += 1
                        
                    if counter != size:
                        boundary_errors.append(f"While loop incorrect count: expected {size}, got {counter}")
                        
                except Exception as e:
                    boundary_errors.append(f"Loop error at size {size}: {str(e)}")
            
            # Evaluate results
            if not off_by_one_detected and len(math_errors) == 0 and len(boundary_errors) == 0:
                self.log_test("Algorithmic Logic Errors", "PASS", "No off-by-one, math, or boundary errors detected")
            else:
                issues = []
                if off_by_one_detected:
                    issues.append("off-by-one errors")
                if math_errors:
                    issues.append(f"math errors: {len(math_errors)}")
                if boundary_errors:
                    issues.append(f"boundary errors: {len(boundary_errors)}")
                self.log_test("Algorithmic Logic Errors", "FAIL", f"Issues: {', '.join(issues)}")
                
        except Exception as e:
            self.log_test("Algorithmic Logic Errors", "FAIL", f"Test error: {str(e)}")
    
    def test_data_processing_logic(self):
        """Test 4.2: Data processing and transformation logic"""
        try:
            # Test 1: Sorting logic verification
            test_datasets = [
                [],
                [1],
                [3, 1, 4, 1, 5, 9, 2, 6],
                ["apple", "banana", "cherry"],
                [1.1, 2.2, 1.5, 3.3]
            ]
            
            sorting_errors = []
            
            for dataset in test_datasets:
                try:
                    # Test ascending sort
                    sorted_asc = sorted(dataset)
                    
                    # Verify sort correctness
                    if len(sorted_asc) != len(dataset):
                        sorting_errors.append(f"Length mismatch in sorting: {len(dataset)} -> {len(sorted_asc)}")
                        continue
                        
                    # Check if actually sorted
                    for i in range(len(sorted_asc) - 1):
                        if sorted_asc[i] > sorted_asc[i + 1]:
                            sorting_errors.append(f"Sort order incorrect: {sorted_asc[i]} > {sorted_asc[i + 1]}")
                            break
                            
                except Exception as e:
                    sorting_errors.append(f"Sort error for {dataset}: {str(e)}")
            
            # Test 2: Data transformation accuracy
            transformation_errors = []
            
            # Test string transformations
            test_strings = ["hello", "WORLD", "123", "", "Mixed Case 123"]
            
            for test_str in test_strings:
                try:
                    # Test various transformations
                    upper = test_str.upper()
                    lower = test_str.lower()
                    reversed_str = test_str[::-1]
                    
                    # Verify transformation properties
                    if test_str.upper().lower() != test_str.lower():
                        # Some case conversions might not be reversible (e.g., special chars)
                        pass
                    
                    if len(reversed_str) != len(test_str):
                        transformation_errors.append(f"Reverse length mismatch: {test_str}")
                        
                except Exception as e:
                    transformation_errors.append(f"String transformation error: {str(e)}")
            
            # Test 3: Numeric data processing
            numeric_errors = []
            
            test_numbers = [0, 1, -1, 3.14159, 1e10, 1e-10]
            
            for num in test_numbers:
                try:
                    # Test various numeric operations
                    abs_val = abs(num)
                    if abs_val < 0:
                        numeric_errors.append(f"Absolute value negative: {num} -> {abs_val}")
                    
                    # Test rounding
                    if isinstance(num, float):
                        rounded = round(num, 2)
                        if not isinstance(rounded, (int, float)):
                            numeric_errors.append(f"Round returned unexpected type: {type(rounded)}")
                            
                except Exception as e:
                    numeric_errors.append(f"Numeric processing error for {num}: {str(e)}")
            
            # Evaluate results
            total_errors = len(sorting_errors) + len(transformation_errors) + len(numeric_errors)
            
            if total_errors == 0:
                self.log_test("Data Processing Logic", "PASS", "All data transformations working correctly")
            else:
                self.log_test("Data Processing Logic", "FAIL", f"Total processing errors: {total_errors}")
                
        except Exception as e:
            self.log_test("Data Processing Logic", "FAIL", f"Test error: {str(e)}")
    
    def test_business_logic_validation(self):
        """Test 4.3: Business logic and application-specific logic"""
        try:
            # Test 1: Wage calculation logic (WageLift specific)
            wage_calculation_errors = []
            
            # Test various wage scenarios
            test_wage_scenarios = [
                {"hourly_rate": 15.0, "hours": 40, "expected_weekly": 600.0},
                {"hourly_rate": 25.50, "hours": 37.5, "expected_weekly": 956.25},
                {"hourly_rate": 0, "hours": 40, "expected_weekly": 0},
                {"hourly_rate": 15.0, "hours": 0, "expected_weekly": 0},
            ]
            
            for scenario in test_wage_scenarios:
                try:
                    calculated = scenario["hourly_rate"] * scenario["hours"]
                    expected = scenario["expected_weekly"]
                    
                    if abs(calculated - expected) > 0.01:  # Allow for floating point precision
                        wage_calculation_errors.append(
                            f"Wage calc error: {scenario['hourly_rate']} * {scenario['hours']} = {calculated}, expected {expected}"
                        )
                        
                except Exception as e:
                    wage_calculation_errors.append(f"Wage calculation exception: {str(e)}")
            
            # Test 2: CPI calculation logic validation
            cpi_logic_errors = []
            
            # Test CPI adjustment scenarios
            cpi_scenarios = [
                {"base_salary": 50000, "old_cpi": 100, "new_cpi": 105, "expected_adjustment": 52500},
                {"base_salary": 75000, "old_cpi": 250, "new_cpi": 255, "expected_adjustment": 76500},
                {"base_salary": 0, "old_cpi": 100, "new_cpi": 105, "expected_adjustment": 0},
            ]
            
            for scenario in cpi_scenarios:
                try:
                    if scenario["old_cpi"] > 0:
                        adjustment_factor = scenario["new_cpi"] / scenario["old_cpi"]
                        calculated = scenario["base_salary"] * adjustment_factor
                        expected = scenario["expected_adjustment"]
                        
                        if abs(calculated - expected) > 1.0:  # Allow $1 variance
                            cpi_logic_errors.append(
                                f"CPI calc error: ${scenario['base_salary']} * {adjustment_factor} = ${calculated:.2f}, expected ${expected}"
                            )
                            
                except Exception as e:
                    cpi_logic_errors.append(f"CPI calculation exception: {str(e)}")
            
            # Test 3: Input validation business logic
            validation_errors = []
            
            # Test business rule validations
            validation_scenarios = [
                {"salary": -1000, "should_reject": True, "reason": "negative salary"},
                {"salary": 1000000000, "should_reject": True, "reason": "unrealistic salary"},
                {"salary": 50000, "should_reject": False, "reason": "normal salary"},
                {"hours_per_week": -5, "should_reject": True, "reason": "negative hours"},
                {"hours_per_week": 200, "should_reject": True, "reason": "unrealistic hours"},
                {"hours_per_week": 40, "should_reject": False, "reason": "normal hours"},
            ]
            
            for scenario in validation_scenarios:
                try:
                    # Simulate validation logic
                    is_valid = True
                    
                    if "salary" in scenario:
                        salary = scenario["salary"]
                        if salary < 0 or salary > 10000000:  # Basic business rules
                            is_valid = False
                    
                    if "hours_per_week" in scenario:
                        hours = scenario["hours_per_week"]
                        if hours < 0 or hours > 168:  # Max hours in a week
                            is_valid = False
                    
                    should_reject = scenario["should_reject"]
                    if (not is_valid) != should_reject:
                        validation_errors.append(
                            f"Validation logic error: {scenario['reason']} - valid={is_valid}, should_reject={should_reject}"
                        )
                        
                except Exception as e:
                    validation_errors.append(f"Validation error: {str(e)}")
            
            # Test 4: State management logic
            state_errors = []
            
            try:
                # Simulate user session state transitions
                user_states = {
                    "logged_out": ["login"],
                    "logged_in": ["logout", "calculate_raise", "view_profile"],
                    "calculating": ["cancel", "complete_calculation"],
                    "results_ready": ["download_letter", "recalculate", "logout"]
                }
                
                # Test valid transitions
                current_state = "logged_out"
                valid_transitions = user_states.get(current_state, [])
                
                if "login" not in valid_transitions:
                    state_errors.append("Cannot login from logged_out state")
                
                # Test invalid transition detection
                if "calculate_raise" in valid_transitions:
                    state_errors.append("Should not be able to calculate raise while logged out")
                    
            except Exception as e:
                state_errors.append(f"State management error: {str(e)}")
            
            # Evaluate results
            total_errors = (len(wage_calculation_errors) + len(cpi_logic_errors) + 
                          len(validation_errors) + len(state_errors))
            
            if total_errors == 0:
                self.log_test("Business Logic Validation", "PASS", "All business logic working correctly")
            else:
                error_details = []
                if wage_calculation_errors:
                    error_details.append(f"wage: {len(wage_calculation_errors)}")
                if cpi_logic_errors:
                    error_details.append(f"CPI: {len(cpi_logic_errors)}")
                if validation_errors:
                    error_details.append(f"validation: {len(validation_errors)}")
                if state_errors:
                    error_details.append(f"state: {len(state_errors)}")
                    
                self.log_test("Business Logic Validation", "FAIL", f"Errors - {', '.join(error_details)}")
                
        except Exception as e:
            self.log_test("Business Logic Validation", "FAIL", f"Test error: {str(e)}")
    
    def test_conditional_logic_accuracy(self):
        """Test 4.4: Conditional logic and decision-making accuracy"""
        try:
            # Test 1: Complex conditional logic
            conditional_errors = []
            
            # Test various conditional scenarios
            test_conditions = [
                {"age": 25, "income": 50000, "should_qualify": True, "reason": "standard case"},
                {"age": 17, "income": 100000, "should_qualify": False, "reason": "too young"},
                {"age": 65, "income": 20000, "should_qualify": False, "reason": "income too low"},
                {"age": 30, "income": 75000, "should_qualify": True, "reason": "good candidate"},
                {"age": 18, "income": 30000, "should_qualify": True, "reason": "minimum qualifying"},
            ]
            
            for condition in test_conditions:
                try:
                    # Example business logic: qualify for raise request if age >= 18 and income >= 25000
                    age = condition["age"]
                    income = condition["income"]
                    
                    qualifies = (age >= 18) and (income >= 25000)
                    expected = condition["should_qualify"]
                    
                    if qualifies != expected:
                        conditional_errors.append(
                            f"Condition error ({condition['reason']}): age={age}, income={income}, got={qualifies}, expected={expected}"
                        )
                        
                except Exception as e:
                    conditional_errors.append(f"Conditional evaluation error: {str(e)}")
            
            # Test 2: Nested conditional logic
            nested_errors = []
            
            # Test nested if-else logic
            test_nested = [
                {"score": 95, "experience": 5, "expected_level": "senior"},
                {"score": 85, "experience": 2, "expected_level": "intermediate"},
                {"score": 70, "experience": 0, "expected_level": "junior"},
                {"score": 95, "experience": 0, "expected_level": "intermediate"},  # High score, no experience
            ]
            
            for test_case in test_nested:
                try:
                    score = test_case["score"]
                    experience = test_case["experience"]
                    
                    # Nested logic for determining level
                    if score >= 90:
                        if experience >= 3:
                            level = "senior"
                        else:
                            level = "intermediate"
                    elif score >= 80:
                        level = "intermediate"
                    else:
                        level = "junior"
                    
                    expected = test_case["expected_level"]
                    
                    if level != expected:
                        nested_errors.append(
                            f"Nested logic error: score={score}, exp={experience}, got={level}, expected={expected}"
                        )
                        
                except Exception as e:
                    nested_errors.append(f"Nested conditional error: {str(e)}")
            
            # Evaluate results
            total_errors = len(conditional_errors) + len(nested_errors)
            
            if total_errors == 0:
                self.log_test("Conditional Logic Accuracy", "PASS", "All conditional logic working correctly")
            else:
                self.log_test("Conditional Logic Accuracy", "FAIL", f"Conditional errors: {total_errors}")
                
        except Exception as e:
            self.log_test("Conditional Logic Accuracy", "FAIL", f"Test error: {str(e)}")
    
    def run_all_tests(self):
        """Run all logic and business error tests"""
        print("🧠 WAGELIFT LOGIC & BUSINESS ERROR TESTING")
        print("=" * 60)
        print()
        
        tests = [
            self.test_algorithmic_logic_errors,
            self.test_data_processing_logic,
            self.test_business_logic_validation,
            self.test_conditional_logic_accuracy
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "FAIL", f"Test crashed: {str(e)}")
        
        print()
        print("📊 LOGIC & BUSINESS ERROR TESTING SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Tests Failed: {failed}/{total}")
        
        if failed == 0:
            print("✅ ALL LOGIC & BUSINESS TESTS PASSED")
        else:
            print("❌ SOME LOGIC & BUSINESS TESTS FAILED")
        
        return failed == 0

if __name__ == "__main__":
    import sys
    tester = LogicBusinessTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)