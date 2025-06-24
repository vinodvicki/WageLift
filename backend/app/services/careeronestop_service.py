"""
CareerOneStop API Service for WageLift application.

Integrates with the U.S. Department of Labor's CareerOneStop API
to fetch salary and wage data for benchmark comparisons.

CareerOneStop provides official government salary data from the
Bureau of Labor Statistics (BLS) and other authoritative sources.
"""

import asyncio
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import aiohttp
import backoff
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.benchmark import Benchmark
from app.core.logging import get_logger

logger = get_logger(__name__)


class CareerOneStopAPIError(Exception):
    """Custom exception for CareerOneStop API errors."""
    pass


class CareerOneStopService:
    """
    Service for interacting with CareerOneStop API.
    
    Provides methods to fetch salary data, wage information,
    and employment statistics from official government sources.
    """
    
    BASE_URL = "https://api.careeronestop.org/v1"
    
    def __init__(self, api_key: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize CareerOneStop service.
        
        Args:
            api_key: CareerOneStop API key (defaults to settings)
            user_id: User ID for API requests (defaults to settings)
        """
        self.api_key = api_key or getattr(settings, 'CAREERONESTOP_AUTHORIZATION_TOKEN', None)
        self.user_id = user_id or getattr(settings, 'CAREERONESTOP_USER_ID', None)
        
        if not self.api_key or not self.user_id:
            logger.warning("CareerOneStop API credentials not configured")
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'User-Agent': 'WageLift/1.0',
                'Accept': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=60
    )
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated request to CareerOneStop API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            CareerOneStopAPIError: If API request fails
        """
        if not self.session:
            raise CareerOneStopAPIError("Service not initialized. Use async context manager.")
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"CareerOneStop API request successful: {endpoint}")
                    return data
                elif response.status == 401:
                    raise CareerOneStopAPIError("Invalid API credentials")
                elif response.status == 429:
                    raise CareerOneStopAPIError("Rate limit exceeded")
                else:
                    error_text = await response.text()
                    raise CareerOneStopAPIError(
                        f"API request failed with status {response.status}: {error_text}"
                    )
        except aiohttp.ClientError as e:
            logger.error(f"CareerOneStop API request failed: {e}")
            raise CareerOneStopAPIError(f"Network error: {e}")
    
    async def search_occupations(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for occupations matching a keyword.
        
        Args:
            keyword: Job title or occupation keyword
            limit: Maximum number of results
            
        Returns:
            List of occupation data
        """
        endpoint = f"occupation/{self.user_id}/{keyword}/{limit}"
        
        try:
            data = await self._make_request(endpoint, {})
            occupations = data.get('OccupationList', [])
            
            logger.info(f"Found {len(occupations)} occupations for keyword: {keyword}")
            return occupations
            
        except CareerOneStopAPIError as e:
            logger.error(f"Failed to search occupations for '{keyword}': {e}")
            return []
    
    async def get_occupation_wages(
        self, 
        onet_code: str, 
        location: str,
        radius: int = 25
    ) -> Dict[str, Any]:
        """
        Get wage data for a specific occupation and location.
        
        Args:
            onet_code: O*NET occupation code
            location: Location (ZIP code, city/state, or state)
            radius: Search radius in miles
            
        Returns:
            Wage data including percentiles and statistics
        """
        endpoint = f"wages/{self.user_id}/{onet_code}/{location}"
        params = {'radius': radius}
        
        try:
            data = await self._make_request(endpoint, params)
            
            # Extract wage information
            wages = data.get('Wages', {})
            if wages:
                logger.info(f"Retrieved wage data for {onet_code} in {location}")
            
            return wages
            
        except CareerOneStopAPIError as e:
            logger.error(f"Failed to get wages for {onet_code} in {location}: {e}")
            return {}
    
    async def get_state_wages(self, onet_code: str, state_code: str) -> Dict[str, Any]:
        """
        Get state-level wage data for an occupation.
        
        Args:
            onet_code: O*NET occupation code
            state_code: Two-letter state code (e.g., 'CA', 'NY')
            
        Returns:
            State wage data
        """
        endpoint = f"wages/{self.user_id}/{onet_code}/{state_code}"
        
        try:
            data = await self._make_request(endpoint, {})
            wages = data.get('Wages', {})
            
            if wages:
                logger.info(f"Retrieved state wage data for {onet_code} in {state_code}")
            
            return wages
            
        except CareerOneStopAPIError as e:
            logger.error(f"Failed to get state wages for {onet_code} in {state_code}: {e}")
            return {}
    
    def _parse_wage_data(self, wage_data: Dict[str, Any], onet_code: str) -> Dict[str, Any]:
        """
        Parse wage data from CareerOneStop API response.
        
        Args:
            wage_data: Raw wage data from API
            onet_code: O*NET occupation code
            
        Returns:
            Parsed and normalized wage data
        """
        if not wage_data:
            return {}
        
        # Extract percentile data
        percentiles = {}
        annual_wages = wage_data.get('AnnualWages', [])
        
        for wage_info in annual_wages:
            pct = wage_info.get('Percentile')
            wage = wage_info.get('Wage')
            
            if pct and wage:
                try:
                    percentiles[f"p{pct}"] = Decimal(str(wage))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid wage value: {wage} for percentile {pct}")
        
        # Extract location information
        location_info = wage_data.get('StateData', {}) or wage_data.get('AreaData', {})
        
        parsed_data = {
            'onet_code': onet_code,
            'occupation_title': wage_data.get('OccupationTitle', ''),
            'location': location_info.get('AreaName', '') or location_info.get('StateName', ''),
            'location_type': 'state' if 'StateData' in wage_data else 'metro',
            'percentiles': percentiles,
            'employment_count': wage_data.get('Employment', {}).get('Employment'),
            'data_year': wage_data.get('DataYear'),
            'last_updated': wage_data.get('LastUpdated')
        }
        
        return parsed_data
    
    async def fetch_salary_benchmarks(
        self,
        job_title: str,
        location: str,
        db_session: AsyncSession,
        radius: int = 25
    ) -> List[Benchmark]:
        """
        Fetch salary benchmarks for a job title and location.
        
        Args:
            job_title: Job title to search for
            location: Location (ZIP, city/state, or state)
            db_session: Database session
            radius: Search radius in miles
            
        Returns:
            List of created benchmark records
        """
        benchmarks = []
        
        try:
            # Search for matching occupations
            occupations = await self.search_occupations(job_title, limit=5)
            
            if not occupations:
                logger.warning(f"No occupations found for job title: {job_title}")
                return benchmarks
            
            # Fetch wage data for each occupation
            for occupation in occupations:
                onet_code = occupation.get('OnetCode')
                if not onet_code:
                    continue
                
                # Get wage data
                wage_data = await self.get_occupation_wages(onet_code, location, radius)
                if not wage_data:
                    continue
                
                # Parse and create benchmark
                parsed_data = self._parse_wage_data(wage_data, onet_code)
                if parsed_data and parsed_data.get('percentiles'):
                    benchmark = await self._create_benchmark_from_data(
                        parsed_data, job_title, db_session
                    )
                    if benchmark:
                        benchmarks.append(benchmark)
            
            logger.info(f"Created {len(benchmarks)} benchmarks for '{job_title}' in {location}")
            
        except Exception as e:
            logger.error(f"Error fetching salary benchmarks: {e}")
        
        return benchmarks
    
    async def _create_benchmark_from_data(
        self,
        parsed_data: Dict[str, Any],
        original_job_title: str,
        db_session: AsyncSession
    ) -> Optional[Benchmark]:
        """
        Create a benchmark record from parsed wage data.
        
        Args:
            parsed_data: Parsed wage data
            original_job_title: Original job title searched
            db_session: Database session
            
        Returns:
            Created benchmark record or None
        """
        try:
            percentiles = parsed_data.get('percentiles', {})
            
            # Check if we have sufficient data
            if not percentiles or len(percentiles) < 3:
                logger.warning("Insufficient percentile data for benchmark creation")
                return None
            
            # Calculate min/max/median from percentiles
            wage_values = list(percentiles.values())
            min_wage = min(wage_values)
            max_wage = max(wage_values)
            median_wage = percentiles.get('p50') or percentiles.get('p10')  # Fallback to available data
            
            # Check if benchmark already exists
            existing = await db_session.execute(
                select(Benchmark).where(
                    and_(
                        Benchmark.job_title == parsed_data['occupation_title'],
                        Benchmark.location == parsed_data['location'],
                        Benchmark.source == 'careeronestop',
                        Benchmark.effective_date >= date.today() - timedelta(days=90)
                    )
                )
            )
            
            if existing.scalar_one_or_none():
                logger.info("Benchmark already exists, skipping creation")
                return None
            
            # Create new benchmark
            benchmark = Benchmark(
                job_title=parsed_data['occupation_title'],
                location=parsed_data['location'],
                location_type=parsed_data['location_type'],
                base_salary_min=min_wage,
                base_salary_max=max_wage,
                base_salary_median=median_wage,
                source='careeronestop',
                source_url=f"https://www.careeronestop.org/Toolkit/Wages/find-wages.aspx",
                data_collection_method='api',
                effective_date=date.today(),
                sample_size=parsed_data.get('employment_count'),
                confidence_score=Decimal('0.9'),  # High confidence for government data
                is_verified=True,
                is_active=True
            )
            
            db_session.add(benchmark)
            await db_session.commit()
            
            logger.info(f"Created benchmark for {parsed_data['occupation_title']} in {parsed_data['location']}")
            return benchmark
            
        except Exception as e:
            logger.error(f"Error creating benchmark: {e}")
            await db_session.rollback()
            return None
    
    async def refresh_benchmark_data(
        self,
        db_session: AsyncSession,
        days_old: int = 30
    ) -> int:
        """
        Refresh benchmark data older than specified days.
        
        Args:
            db_session: Database session
            days_old: Refresh benchmarks older than this many days
            
        Returns:
            Number of benchmarks refreshed
        """
        cutoff_date = date.today() - timedelta(days=days_old)
        
        # Find old benchmarks from CareerOneStop
        old_benchmarks = await db_session.execute(
            select(Benchmark).where(
                and_(
                    Benchmark.source == 'careeronestop',
                    Benchmark.effective_date < cutoff_date,
                    Benchmark.is_active == True
                )
            )
        )
        
        refreshed_count = 0
        
        for benchmark in old_benchmarks.scalars():
            try:
                # Mark old benchmark as inactive
                benchmark.is_active = False
                
                # Fetch new data
                new_benchmarks = await self.fetch_salary_benchmarks(
                    benchmark.job_title,
                    benchmark.location,
                    db_session
                )
                
                if new_benchmarks:
                    refreshed_count += len(new_benchmarks)
                    logger.info(f"Refreshed benchmark for {benchmark.job_title}")
                
            except Exception as e:
                logger.error(f"Error refreshing benchmark {benchmark.id}: {e}")
        
        await db_session.commit()
        logger.info(f"Refreshed {refreshed_count} benchmarks")
        
        return refreshed_count


# Utility functions for working with benchmark data
async def get_salary_percentiles(
    job_title: str,
    location: str,
    db_session: AsyncSession
) -> Dict[str, Decimal]:
    """
    Get salary percentiles for a job title and location.
    
    Args:
        job_title: Job title to search for
        location: Location to search in
        db_session: Database session
        
    Returns:
        Dictionary with percentile data
    """
    # Query recent benchmarks
    benchmarks = await db_session.execute(
        select(Benchmark).where(
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
        ).order_by(Benchmark.confidence_score.desc())
    )
    
    benchmark_list = benchmarks.scalars().all()
    
    if not benchmark_list:
        return {}
    
    # Calculate aggregate percentiles
    all_salaries = []
    for benchmark in benchmark_list:
        if benchmark.base_salary_min and benchmark.base_salary_max:
            # Add min, median, max to salary list
            all_salaries.append(float(benchmark.base_salary_min))
            if benchmark.base_salary_median:
                all_salaries.append(float(benchmark.base_salary_median))
            all_salaries.append(float(benchmark.base_salary_max))
    
    if not all_salaries:
        return {}
    
    all_salaries.sort()
    n = len(all_salaries)
    
    percentiles = {
        'p10': Decimal(str(all_salaries[int(0.1 * n)])),
        'p25': Decimal(str(all_salaries[int(0.25 * n)])),
        'p50': Decimal(str(all_salaries[int(0.5 * n)])),
        'p75': Decimal(str(all_salaries[int(0.75 * n)])),
        'p90': Decimal(str(all_salaries[int(0.9 * n)])),
    }
    
    return percentiles


async def compare_salary_to_market(
    current_salary: Decimal,
    job_title: str,
    location: str,
    db_session: AsyncSession
) -> Dict[str, Any]:
    """
    Compare a salary to market benchmarks.
    
    Args:
        current_salary: Current salary to compare
        job_title: Job title for comparison
        location: Location for comparison
        db_session: Database session
        
    Returns:
        Comparison analysis
    """
    percentiles = await get_salary_percentiles(job_title, location, db_session)
    
    if not percentiles:
        return {
            'error': 'No benchmark data available',
            'percentiles': {},
            'comparison': {}
        }
    
    # Determine where current salary falls
    comparison = {}
    for pct, value in percentiles.items():
        if current_salary >= value:
            comparison[pct] = 'above'
        else:
            comparison[pct] = 'below'
    
    # Calculate percentile rank
    salary_values = list(percentiles.values())
    salary_values.append(current_salary)
    salary_values.sort()
    
    rank = salary_values.index(current_salary) / len(salary_values)
    percentile_rank = round(rank * 100, 1)
    
    return {
        'percentiles': {k: float(v) for k, v in percentiles.items()},
        'comparison': comparison,
        'percentile_rank': percentile_rank,
        'market_position': _get_market_position(percentile_rank)
    }


def _get_market_position(percentile_rank: float) -> str:
    """Get market position description."""
    if percentile_rank >= 90:
        return 'Top 10% - Excellent'
    elif percentile_rank >= 75:
        return 'Top 25% - Above Market'
    elif percentile_rank >= 50:
        return 'Above Median - Good'
    elif percentile_rank >= 25:
        return 'Below Median - Consider Raise'
    else:
        return 'Bottom 25% - Significant Gap' 