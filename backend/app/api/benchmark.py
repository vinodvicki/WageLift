"""
Salary Benchmark API endpoints for WageLift application.

Provides endpoints for fetching, managing, and analyzing salary benchmark data
from various sources including CareerOneStop API.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.benchmark import Benchmark
from app.models.user import User
from app.services.careeronestop_service import (
    CareerOneStopService,
    get_salary_percentiles,
    compare_salary_to_market
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/benchmark", tags=["benchmark"])


# Pydantic models for request/response
class BenchmarkSearchRequest(BaseModel):
    """Request model for benchmark search."""
    job_title: str = Field(..., min_length=2, max_length=255, description="Job title to search for")
    location: str = Field(..., min_length=2, max_length=255, description="Location (city, state, ZIP)")
    radius: int = Field(25, ge=5, le=100, description="Search radius in miles")
    refresh: bool = Field(False, description="Force refresh of benchmark data")


class SalaryComparisonRequest(BaseModel):
    """Request model for salary comparison."""
    current_salary: Decimal = Field(..., gt=0, description="Current salary to compare")
    job_title: str = Field(..., min_length=2, max_length=255, description="Job title")
    location: str = Field(..., min_length=2, max_length=255, description="Location")
    
    @validator('current_salary')
    def validate_salary(cls, v):
        if v <= 0:
            raise ValueError('Salary must be positive')
        if v > 10000000:  # $10M cap
            raise ValueError('Salary exceeds maximum allowed value')
        return v


class BenchmarkResponse(BaseModel):
    """Response model for benchmark data."""
    id: str
    job_title: str
    location: str
    location_type: str
    base_salary_min: Decimal
    base_salary_max: Decimal
    base_salary_median: Optional[Decimal]
    source: str
    effective_date: date
    confidence_score: Optional[Decimal]
    sample_size: Optional[int]
    
    class Config:
        from_attributes = True


class PercentileData(BaseModel):
    """Percentile data model."""
    p10: Optional[Decimal] = Field(None, description="10th percentile salary")
    p25: Optional[Decimal] = Field(None, description="25th percentile salary")
    p50: Optional[Decimal] = Field(None, description="50th percentile (median) salary")
    p75: Optional[Decimal] = Field(None, description="75th percentile salary")
    p90: Optional[Decimal] = Field(None, description="90th percentile salary")


class SalaryComparisonResponse(BaseModel):
    """Response model for salary comparison."""
    current_salary: Decimal
    job_title: str
    location: str
    percentiles: PercentileData
    percentile_rank: Optional[float] = Field(None, description="Where current salary ranks (0-100)")
    market_position: Optional[str] = Field(None, description="Market position description")
    recommendations: List[str] = Field(default_factory=list, description="Salary recommendations")
    benchmark_count: int = Field(0, description="Number of benchmarks used")


class BenchmarkStatsResponse(BaseModel):
    """Response model for benchmark statistics."""
    total_benchmarks: int
    active_benchmarks: int
    sources: Dict[str, int]
    recent_updates: int
    coverage_by_location: Dict[str, int]
    coverage_by_job_family: Dict[str, int]


@router.post("/search", response_model=List[BenchmarkResponse])
async def search_benchmarks(
    request: BenchmarkSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for salary benchmarks by job title and location.
    
    Searches existing benchmark data and optionally refreshes from external APIs.
    """
    try:
        # Search existing benchmarks first
        query = select(Benchmark).where(
            and_(
                or_(
                    Benchmark.job_title.ilike(f"%{request.job_title}%"),
                    Benchmark.job_title.contains(request.job_title)
                ),
                or_(
                    Benchmark.location.ilike(f"%{request.location}%"),
                    Benchmark.location.contains(request.location)
                ),
                Benchmark.is_active == True,
                Benchmark.effective_date >= date.today() - timedelta(days=90)
            )
        ).order_by(desc(Benchmark.confidence_score), desc(Benchmark.effective_date))
        
        result = await db.execute(query)
        existing_benchmarks = result.scalars().all()
        
        # If no recent data or refresh requested, fetch from API
        if not existing_benchmarks or request.refresh:
            background_tasks.add_task(
                _fetch_benchmark_data_background,
                request.job_title,
                request.location,
                request.radius
            )
            
            if not existing_benchmarks:
                # No existing data, try to fetch synchronously (with timeout)
                try:
                    async with CareerOneStopService() as service:
                        new_benchmarks = await service.fetch_salary_benchmarks(
                            request.job_title,
                            request.location,
                            db,
                            request.radius
                        )
                        if new_benchmarks:
                            existing_benchmarks.extend(new_benchmarks)
                except Exception as e:
                    logger.warning(f"Failed to fetch benchmark data synchronously: {e}")
        
        # Convert to response format
        benchmarks = [
            BenchmarkResponse(
                id=str(benchmark.id),
                job_title=benchmark.job_title,
                location=benchmark.location,
                location_type=benchmark.location_type,
                base_salary_min=benchmark.base_salary_min,
                base_salary_max=benchmark.base_salary_max,
                base_salary_median=benchmark.base_salary_median,
                source=benchmark.source,
                effective_date=benchmark.effective_date,
                confidence_score=benchmark.confidence_score,
                sample_size=benchmark.sample_size
            )
            for benchmark in existing_benchmarks[:20]  # Limit results
        ]
        
        logger.info(f"Returned {len(benchmarks)} benchmarks for '{request.job_title}' in {request.location}")
        return benchmarks
        
    except Exception as e:
        logger.error(f"Error searching benchmarks: {e}")
        raise HTTPException(status_code=500, detail="Failed to search benchmarks")


@router.post("/compare", response_model=SalaryComparisonResponse)
async def compare_salary(
    request: SalaryComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare a salary against market benchmarks.
    
    Provides percentile analysis and recommendations based on market data.
    """
    try:
        # Get comparison data
        comparison_data = await compare_salary_to_market(
            request.current_salary,
            request.job_title,
            request.location,
            db
        )
        
        if comparison_data.get('error'):
            raise HTTPException(
                status_code=404,
                detail=f"No benchmark data available for {request.job_title} in {request.location}"
            )
        
        # Generate recommendations
        recommendations = _generate_salary_recommendations(
            request.current_salary,
            comparison_data
        )
        
        # Count benchmarks used
        benchmark_count = await _count_benchmarks_for_comparison(
            request.job_title,
            request.location,
            db
        )
        
        response = SalaryComparisonResponse(
            current_salary=request.current_salary,
            job_title=request.job_title,
            location=request.location,
            percentiles=PercentileData(**comparison_data['percentiles']),
            percentile_rank=comparison_data.get('percentile_rank'),
            market_position=comparison_data.get('market_position'),
            recommendations=recommendations,
            benchmark_count=benchmark_count
        )
        
        logger.info(f"Salary comparison completed for {request.job_title}: {comparison_data.get('percentile_rank', 0):.1f} percentile")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing salary: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare salary")


@router.get("/percentiles", response_model=PercentileData)
async def get_percentiles(
    job_title: str = Query(..., min_length=2, description="Job title"),
    location: str = Query(..., min_length=2, description="Location"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get salary percentiles for a job title and location.
    """
    try:
        percentiles = await get_salary_percentiles(job_title, location, db)
        
        if not percentiles:
            raise HTTPException(
                status_code=404,
                detail=f"No percentile data available for {job_title} in {location}"
            )
        
        return PercentileData(**percentiles)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting percentiles: {e}")
        raise HTTPException(status_code=500, detail="Failed to get percentiles")


@router.get("/stats", response_model=BenchmarkStatsResponse)
async def get_benchmark_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics about available benchmark data.
    """
    try:
        # Total benchmarks
        total_count = await db.scalar(select(func.count(Benchmark.id)))
        
        # Active benchmarks
        active_count = await db.scalar(
            select(func.count(Benchmark.id)).where(Benchmark.is_active == True)
        )
        
        # Recent updates (last 30 days)
        recent_cutoff = date.today() - timedelta(days=30)
        recent_count = await db.scalar(
            select(func.count(Benchmark.id)).where(
                Benchmark.effective_date >= recent_cutoff
            )
        )
        
        # Sources breakdown
        source_result = await db.execute(
            select(Benchmark.source, func.count(Benchmark.id))
            .where(Benchmark.is_active == True)
            .group_by(Benchmark.source)
        )
        sources = dict(source_result.all())
        
        # Location coverage (top 10)
        location_result = await db.execute(
            select(Benchmark.location, func.count(Benchmark.id))
            .where(Benchmark.is_active == True)
            .group_by(Benchmark.location)
            .order_by(desc(func.count(Benchmark.id)))
            .limit(10)
        )
        coverage_by_location = dict(location_result.all())
        
        # Job family coverage (extract from job titles)
        job_family_result = await db.execute(
            select(Benchmark.job_family, func.count(Benchmark.id))
            .where(and_(Benchmark.is_active == True, Benchmark.job_family.isnot(None)))
            .group_by(Benchmark.job_family)
            .order_by(desc(func.count(Benchmark.id)))
            .limit(10)
        )
        coverage_by_job_family = dict(job_family_result.all())
        
        return BenchmarkStatsResponse(
            total_benchmarks=total_count or 0,
            active_benchmarks=active_count or 0,
            sources=sources,
            recent_updates=recent_count or 0,
            coverage_by_location=coverage_by_location,
            coverage_by_job_family=coverage_by_job_family
        )
        
    except Exception as e:
        logger.error(f"Error getting benchmark stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get benchmark statistics")


@router.post("/refresh")
async def refresh_benchmark_data(
    background_tasks: BackgroundTasks,
    days_old: int = Query(30, ge=1, le=365, description="Refresh benchmarks older than N days"),
    current_user: User = Depends(get_current_user)
):
    """
    Refresh old benchmark data from external APIs.
    
    Runs as a background task to avoid blocking the request.
    """
    background_tasks.add_task(_refresh_benchmark_data_background, days_old)
    
    return {
        "message": "Benchmark data refresh started",
        "status": "background_task_queued",
        "days_old_threshold": days_old
    }


# Background task functions
async def _fetch_benchmark_data_background(
    job_title: str,
    location: str,
    radius: int = 25
):
    """Background task to fetch benchmark data."""
    try:
        from app.core.database import get_async_session
        
        async with get_async_session() as db:
            async with CareerOneStopService() as service:
                benchmarks = await service.fetch_salary_benchmarks(
                    job_title,
                    location,
                    db,
                    radius
                )
                logger.info(f"Background task created {len(benchmarks)} benchmarks for '{job_title}' in {location}")
    except Exception as e:
        logger.error(f"Background benchmark fetch failed: {e}")


async def _refresh_benchmark_data_background(days_old: int):
    """Background task to refresh old benchmark data."""
    try:
        from app.core.database import get_async_session
        
        async with get_async_session() as db:
            async with CareerOneStopService() as service:
                refreshed_count = await service.refresh_benchmark_data(db, days_old)
                logger.info(f"Background refresh completed: {refreshed_count} benchmarks updated")
    except Exception as e:
        logger.error(f"Background benchmark refresh failed: {e}")


# Helper functions
def _generate_salary_recommendations(
    current_salary: Decimal,
    comparison_data: Dict[str, Any]
) -> List[str]:
    """Generate salary recommendations based on market comparison."""
    recommendations = []
    
    percentile_rank = comparison_data.get('percentile_rank', 0)
    percentiles = comparison_data.get('percentiles', {})
    
    if percentile_rank < 25:
        # Bottom quartile - significant gap
        target_salary = percentiles.get('p50', current_salary * Decimal('1.2'))
        increase_pct = ((target_salary - current_salary) / current_salary * 100)
        recommendations.extend([
            f"Your salary is in the bottom 25% for your role and location",
            f"Consider requesting a {increase_pct:.1f}% increase to reach market median",
            "Document your achievements and market research when negotiating",
            "Consider seeking opportunities at companies with better compensation"
        ])
    elif percentile_rank < 50:
        # Below median
        target_salary = percentiles.get('p50', current_salary * Decimal('1.1'))
        increase_pct = ((target_salary - current_salary) / current_salary * 100)
        recommendations.extend([
            f"Your salary is below the market median",
            f"A {increase_pct:.1f}% increase would bring you to market median",
            "Use CPI data and performance metrics to justify your request"
        ])
    elif percentile_rank < 75:
        # Above median but below 75th percentile
        recommendations.extend([
            "Your salary is above market median - good position",
            "Focus on performance-based increases and career advancement",
            "Consider total compensation including benefits and equity"
        ])
    else:
        # Top quartile
        recommendations.extend([
            "Excellent! Your salary is in the top 25% for your role",
            "Focus on career advancement and leadership opportunities",
            "Consider negotiating for additional benefits or equity"
        ])
    
    return recommendations


async def _count_benchmarks_for_comparison(
    job_title: str,
    location: str,
    db: AsyncSession
) -> int:
    """Count benchmarks used for salary comparison."""
    count = await db.scalar(
        select(func.count(Benchmark.id)).where(
            and_(
                or_(
                    Benchmark.job_title.ilike(f"%{job_title}%"),
                    Benchmark.job_title.contains(job_title)
                ),
                or_(
                    Benchmark.location.ilike(f"%{location}%"),
                    Benchmark.location.contains(location)
                ),
                Benchmark.is_active == True,
                Benchmark.effective_date >= date.today() - timedelta(days=90)
            )
        )
    )
    return count or 0 