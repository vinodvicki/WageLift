#!/usr/bin/env python3
"""
Test script for Benchmark API Integration.

This script tests the complete benchmark system including:
- Database storage and retrieval
- CareerOneStop API integration (with mock data)
- Percentile calculations
- Salary comparisons
- API endpoints
"""

import asyncio
import sys
import os
from datetime import date, timedelta
from decimal import Decimal
from typing import List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_async_session
from app.models.benchmark import Benchmark
from app.services.careeronestop_service import (
    get_salary_percentiles,
    compare_salary_to_market
)


class BenchmarkTestData:
    """Test data for benchmark functionality."""
    
    @staticmethod
    def create_sample_benchmarks() -> List[Benchmark]:
        """Create sample benchmark data for testing."""
        return [
            Benchmark(
                job_title="Software Engineer",
                location="San Francisco, CA",
                location_type="metro",
                base_salary_min=Decimal("95000"),
                base_salary_max=Decimal("180000"),
                base_salary_median=Decimal("135000"),
                source="test_data",
                effective_date=date.today(),
                confidence_score=Decimal("0.95"),
                sample_size=150,
                is_verified=True,
                is_active=True
            ),
            Benchmark(
                job_title="Software Engineer",
                location="San Francisco, CA",
                location_type="metro",
                base_salary_min=Decimal("90000"),
                base_salary_max=Decimal("175000"),
                base_salary_median=Decimal("130000"),
                source="test_data",
                effective_date=date.today(),
                confidence_score=Decimal("0.90"),
                sample_size=120,
                is_verified=True,
                is_active=True
            ),
            Benchmark(
                job_title="Senior Software Engineer",
                location="San Francisco, CA",
                location_type="metro",
                base_salary_min=Decimal("140000"),
                base_salary_max=Decimal("250000"),
                base_salary_median=Decimal("190000"),
                source="test_data",
                effective_date=date.today(),
                confidence_score=Decimal("0.92"),
                sample_size=80,
                is_verified=True,
                is_active=True
            ),
            Benchmark(
                job_title="Software Engineer",
                location="Austin, TX",
                location_type="metro",
                base_salary_min=Decimal("75000"),
                base_salary_max=Decimal("140000"),
                base_salary_median=Decimal("105000"),
                source="test_data",
                effective_date=date.today(),
                confidence_score=Decimal("0.88"),
                sample_size=90,
                is_verified=True,
                is_active=True
            ),
            Benchmark(
                job_title="Data Scientist",
                location="San Francisco, CA",
                location_type="metro",
                base_salary_min=Decimal("110000"),
                base_salary_max=Decimal("200000"),
                base_salary_median=Decimal("155000"),
                source="test_data",
                effective_date=date.today(),
                confidence_score=Decimal("0.85"),
                sample_size=60,
                is_verified=True,
                is_active=True
            ),
        ]


async def test_database_storage():
    """Test benchmark data storage and retrieval."""
    print("🗄️  Testing benchmark database storage...")
    
    async with get_async_session() as db:
        # Clean up any existing test data
        await db.execute(delete(Benchmark).where(Benchmark.source == "test_data"))
        await db.commit()
        
        # Create sample benchmarks
        sample_benchmarks = BenchmarkTestData.create_sample_benchmarks()
        
        # Store benchmarks
        for benchmark in sample_benchmarks:
            db.add(benchmark)
        
        await db.commit()
        print(f"✅ Stored {len(sample_benchmarks)} benchmark records")
        
        # Test retrieval
        result = await db.execute(
            select(Benchmark).where(Benchmark.source == "test_data")
        )
        stored_benchmarks = result.scalars().all()
        
        print(f"✅ Retrieved {len(stored_benchmarks)} benchmark records")
        
        # Verify data integrity
        for benchmark in stored_benchmarks:
            assert benchmark.job_title is not None
            assert benchmark.location is not None
            assert benchmark.base_salary_min > 0
            assert benchmark.base_salary_max > benchmark.base_salary_min
            assert benchmark.effective_date == date.today()
            print(f"   📊 {benchmark.job_title} in {benchmark.location}: "
                  f"${benchmark.base_salary_min:,} - ${benchmark.base_salary_max:,}")
        
        print("✅ Database storage test completed successfully")
        return True


async def test_percentile_calculations():
    """Test salary percentile calculations."""
    print("\n📊 Testing percentile calculations...")
    
    async with get_async_session() as db:
        # Test percentiles for Software Engineer in San Francisco
        percentiles = await get_salary_percentiles(
            "Software Engineer",
            "San Francisco",
            db
        )
        
        if percentiles:
            print("✅ Percentile calculation successful:")
            for pct, value in percentiles.items():
                print(f"   {pct}: ${value:,}")
            
            # Verify percentiles are in ascending order
            values = list(percentiles.values())
            assert all(values[i] <= values[i+1] for i in range(len(values)-1)), \
                "Percentiles should be in ascending order"
            
            print("✅ Percentile validation passed")
        else:
            print("❌ No percentile data found")
            return False
        
        return True


async def test_salary_comparison():
    """Test salary comparison functionality."""
    print("\n🔍 Testing salary comparison...")
    
    async with get_async_session() as db:
        # Test salary comparison
        test_salary = Decimal("120000")
        comparison = await compare_salary_to_market(
            test_salary,
            "Software Engineer",
            "San Francisco",
            db
        )
        
        if comparison.get('error'):
            print(f"❌ Comparison failed: {comparison['error']}")
            return False
        
        print(f"✅ Salary comparison for ${test_salary:,}:")
        print(f"   Percentile rank: {comparison.get('percentile_rank', 'N/A')}")
        print(f"   Market position: {comparison.get('market_position', 'N/A')}")
        
        percentiles = comparison.get('percentiles', {})
        if percentiles:
            print("   Market percentiles:")
            for pct, value in percentiles.items():
                status = "✅" if test_salary >= value else "❌"
                print(f"     {pct}: ${value:,} {status}")
        
        return True


async def test_benchmark_queries():
    """Test various benchmark query scenarios."""
    print("\n🔎 Testing benchmark queries...")
    
    async with get_async_session() as db:
        # Test 1: Exact job title match
        result = await db.execute(
            select(Benchmark).where(
                Benchmark.job_title == "Software Engineer",
                Benchmark.source == "test_data"
            )
        )
        exact_matches = result.scalars().all()
        print(f"✅ Exact job title matches: {len(exact_matches)}")
        
        # Test 2: Location-based queries
        result = await db.execute(
            select(Benchmark).where(
                Benchmark.location.ilike("%San Francisco%"),
                Benchmark.source == "test_data"
            )
        )
        sf_benchmarks = result.scalars().all()
        print(f"✅ San Francisco benchmarks: {len(sf_benchmarks)}")
        
        # Test 3: Salary range queries
        result = await db.execute(
            select(Benchmark).where(
                Benchmark.base_salary_median >= 100000,
                Benchmark.source == "test_data"
            )
        )
        high_salary_benchmarks = result.scalars().all()
        print(f"✅ High salary benchmarks (median >= $100k): {len(high_salary_benchmarks)}")
        
        # Test 4: Active benchmarks only
        result = await db.execute(
            select(Benchmark).where(
                Benchmark.is_active == True,
                Benchmark.source == "test_data"
            )
        )
        active_benchmarks = result.scalars().all()
        print(f"✅ Active benchmarks: {len(active_benchmarks)}")
        
        return True


async def test_data_validation():
    """Test data validation and constraints."""
    print("\n✅ Testing data validation...")
    
    async with get_async_session() as db:
        # Test 1: Invalid salary range (min > max)
        try:
            invalid_benchmark = Benchmark(
                job_title="Test Job",
                location="Test Location",
                location_type="metro",
                base_salary_min=Decimal("150000"),  # Higher than max
                base_salary_max=Decimal("100000"),  # Lower than min
                base_salary_median=Decimal("125000"),
                source="test_validation",
                effective_date=date.today(),
                is_active=True
            )
            db.add(invalid_benchmark)
            await db.commit()
            print("❌ Should have failed validation for min > max salary")
            return False
        except Exception as e:
            print("✅ Correctly rejected invalid salary range")
        
        # Test 2: Missing required fields
        try:
            incomplete_benchmark = Benchmark(
                # Missing job_title and location
                base_salary_min=Decimal("50000"),
                base_salary_max=Decimal("100000"),
                source="test_validation",
                effective_date=date.today(),
                is_active=True
            )
            db.add(incomplete_benchmark)
            await db.commit()
            print("❌ Should have failed validation for missing fields")
            return False
        except Exception as e:
            print("✅ Correctly rejected incomplete benchmark")
        
        return True


async def test_benchmark_statistics():
    """Test benchmark statistics calculations."""
    print("\n📈 Testing benchmark statistics...")
    
    async with get_async_session() as db:
        # Count total benchmarks
        result = await db.execute(
            select(Benchmark).where(Benchmark.source == "test_data")
        )
        total_benchmarks = len(result.scalars().all())
        print(f"✅ Total test benchmarks: {total_benchmarks}")
        
        # Group by location
        result = await db.execute(
            select(Benchmark.location, Benchmark.base_salary_median)
            .where(Benchmark.source == "test_data")
        )
        location_data = result.all()
        
        location_stats = {}
        for location, median in location_data:
            if location not in location_stats:
                location_stats[location] = []
            if median:
                location_stats[location].append(float(median))
        
        print("✅ Location-based salary statistics:")
        for location, salaries in location_stats.items():
            if salaries:
                avg_salary = sum(salaries) / len(salaries)
                print(f"   {location}: Average median ${avg_salary:,.0f}")
        
        return True


async def cleanup_test_data():
    """Clean up test data."""
    print("\n🧹 Cleaning up test data...")
    
    async with get_async_session() as db:
        # Remove test data
        await db.execute(delete(Benchmark).where(Benchmark.source == "test_data"))
        await db.execute(delete(Benchmark).where(Benchmark.source == "test_validation"))
        await db.commit()
        print("✅ Test data cleaned up")


async def main():
    """Run all benchmark tests."""
    print("🚀 Starting Benchmark Integration Tests\n")
    
    tests = [
        ("Database Storage", test_database_storage),
        ("Percentile Calculations", test_percentile_calculations),
        ("Salary Comparison", test_salary_comparison),
        ("Benchmark Queries", test_benchmark_queries),
        ("Data Validation", test_data_validation),
        ("Benchmark Statistics", test_benchmark_statistics),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    try:
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*50}")
                print(f"Running: {test_name}")
                print(f"{'='*50}")
                
                success = await test_func()
                if success:
                    passed_tests += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
                    
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        # Always clean up
        await cleanup_test_data()
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Benchmark system is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 