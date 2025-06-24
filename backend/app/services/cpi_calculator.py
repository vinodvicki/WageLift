"""
CPI Calculation Service for WageLift.
Implements inflation adjustment logic and salary gap calculations.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from pydantic import BaseModel, Field, validator

# Internal imports
from ..core.database import get_db_session
from ..core.metrics import (
    track_supabase_operation,
    record_business_metric,
    SUPABASE_QUERY_DURATION,
    metrics_collector
)
from ..core.logging import log_business_event, log_api_event
from ..models.cpi_data import CPIData  # Assuming this exists from Task 4


# Calculation result models
@dataclass
class InflationAdjustmentResult:
    """Result of inflation adjustment calculation."""
    adjusted_salary: float
    percentage_gap: float
    dollar_gap: float
    original_salary: float
    current_salary: float
    historical_cpi: float
    current_cpi: float
    calculation_date: datetime
    inflation_rate: float


class CalculationMethod(str, Enum):
    """Available CPI calculation methods."""
    EXACT_DATE = "exact_date"
    NEAREST_DATE = "nearest_date"
    INTERPOLATED = "interpolated"
    MONTHLY_AVERAGE = "monthly_average"


class CPICalculationRequest(BaseModel):
    """Request model for CPI calculations."""
    original_salary: float = Field(..., gt=0, le=10_000_000, description="Original salary amount")
    current_salary: float = Field(..., gt=0, le=10_000_000, description="Current salary amount")
    historical_date: date = Field(..., description="Date of original salary")
    current_date: Optional[date] = Field(None, description="Current date (defaults to today)")
    calculation_method: CalculationMethod = Field(default=CalculationMethod.NEAREST_DATE)
    user_id: Optional[str] = Field(None, description="User ID for audit logging")

    @validator('historical_date')
    def validate_historical_date(cls, v):
        """Ensure historical date is not in the future."""
        if v > date.today():
            raise ValueError("Historical date cannot be in the future")
        # Ensure date is not too old (CPI data availability)
        if v < date(1947, 1, 1):  # BLS CPI data starts in 1947
            raise ValueError("Historical date is too old (before 1947)")
        return v

    @validator('current_date')
    def validate_current_date(cls, v, values):
        """Ensure current date is after historical date."""
        if v is None:
            return date.today()
        
        historical_date = values.get('historical_date')
        if historical_date and v <= historical_date:
            raise ValueError("Current date must be after historical date")
        return v


class CPICalculationError(Exception):
    """Custom exception for CPI calculation errors."""
    pass


class CPIDataNotFoundError(CPICalculationError):
    """Exception raised when required CPI data is not available."""
    pass


class CPICalculatorService:
    """
    Service for calculating inflation adjustments and salary gaps using CPI data.
    Provides enterprise-grade calculation capabilities with comprehensive error handling.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cpi_cache: Dict[date, float] = {}
        self._cache_ttl = timedelta(hours=1)  # Cache CPI data for 1 hour
        self._last_cache_update = datetime.min

    @track_supabase_operation("calculate_salary_gap", "cpi_calculations")
    async def calculate_salary_gap(
        self, 
        request: CPICalculationRequest,
        db_session: Optional[AsyncSession] = None
    ) -> InflationAdjustmentResult:
        """
        Calculate inflation-adjusted salary gap.
        
        Args:
            request: Calculation request parameters
            db_session: Optional database session
            
        Returns:
            InflationAdjustmentResult with all calculation details
            
        Raises:
            CPICalculationError: If calculation fails
            CPIDataNotFoundError: If required CPI data is unavailable
        """
        start_time = datetime.now()
        
        try:
            # Log calculation start
            log_business_event(
                "cpi_calculation_started",
                user_id=request.user_id,
                details={
                    "original_salary": request.original_salary,
                    "historical_date": request.historical_date.isoformat(),
                    "calculation_method": request.calculation_method
                }
            )

            # Get database session if not provided
            if db_session is None:
                async with get_db_session() as session:
                    return await self._perform_calculation(request, session)
            else:
                return await self._perform_calculation(request, db_session)

        except Exception as e:
            # Log calculation error
            log_business_event(
                "cpi_calculation_failed",
                user_id=request.user_id,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "request_data": request.dict()
                }
            )
            
            # Record error metric
            record_business_metric("cpi_calculation_errors", 1, {
                "error_type": type(e).__name__,
                "calculation_method": request.calculation_method
            })
            
            raise

        finally:
            # Record calculation duration
            duration = (datetime.now() - start_time).total_seconds()
            record_business_metric("cpi_calculation_duration", duration, {
                "calculation_method": request.calculation_method
            })

    async def _perform_calculation(
        self, 
        request: CPICalculationRequest, 
        db_session: AsyncSession
    ) -> InflationAdjustmentResult:
        """Perform the actual CPI calculation."""
        
        # Get CPI values for both dates
        historical_cpi = await self._get_cpi_for_date(
            request.historical_date, 
            request.calculation_method, 
            db_session
        )
        
        current_cpi = await self._get_cpi_for_date(
            request.current_date, 
            request.calculation_method, 
            db_session
        )

        # Validate CPI data
        if historical_cpi is None:
            raise CPIDataNotFoundError(
                f"CPI data not available for historical date: {request.historical_date}"
            )
        
        if current_cpi is None:
            raise CPIDataNotFoundError(
                f"CPI data not available for current date: {request.current_date}"
            )

        # Perform inflation adjustment calculation
        result = self._calculate_adjustment(
            original_salary=request.original_salary,
            current_salary=request.current_salary,
            historical_cpi=historical_cpi,
            current_cpi=current_cpi,
            historical_date=request.historical_date,
            current_date=request.current_date
        )

        # Log successful calculation
        log_business_event(
            "cpi_calculation_completed",
            user_id=request.user_id,
            details={
                "adjusted_salary": result.adjusted_salary,
                "percentage_gap": result.percentage_gap,
                "dollar_gap": result.dollar_gap,
                "inflation_rate": result.inflation_rate
            }
        )

        # Record success metric
        record_business_metric("cpi_calculations_successful", 1, {
            "calculation_method": request.calculation_method
        })

        return result

    def _calculate_adjustment(
        self,
        original_salary: float,
        current_salary: float,
        historical_cpi: float,
        current_cpi: float,
        historical_date: date,
        current_date: date
    ) -> InflationAdjustmentResult:
        """
        Perform the core inflation adjustment calculation.
        Uses Decimal for precise financial calculations.
        """
        
        # Convert to Decimal for precise financial calculations
        original_decimal = Decimal(str(original_salary))
        current_decimal = Decimal(str(current_salary))
        historical_cpi_decimal = Decimal(str(historical_cpi))
        current_cpi_decimal = Decimal(str(current_cpi))

        # Calculate inflation-adjusted salary
        # Formula: Adjusted = Original × (Current CPI / Historical CPI)
        cpi_ratio = current_cpi_decimal / historical_cpi_decimal
        adjusted_salary_decimal = original_decimal * cpi_ratio

        # Calculate gaps
        dollar_gap_decimal = adjusted_salary_decimal - current_decimal
        percentage_gap_decimal = (dollar_gap_decimal / current_decimal) * Decimal('100')

        # Calculate inflation rate
        inflation_rate_decimal = ((current_cpi_decimal - historical_cpi_decimal) / historical_cpi_decimal) * Decimal('100')

        # Round to appropriate precision (2 decimal places for currency)
        adjusted_salary = float(adjusted_salary_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        dollar_gap = float(dollar_gap_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        percentage_gap = float(percentage_gap_decimal.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        inflation_rate = float(inflation_rate_decimal.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))

        return InflationAdjustmentResult(
            adjusted_salary=adjusted_salary,
            percentage_gap=percentage_gap,
            dollar_gap=dollar_gap,
            original_salary=original_salary,
            current_salary=current_salary,
            historical_cpi=historical_cpi,
            current_cpi=current_cpi,
            calculation_date=datetime.now(),
            inflation_rate=inflation_rate
        )

    @track_supabase_operation("get_cpi_data", "cpi_data")
    async def _get_cpi_for_date(
        self, 
        target_date: date, 
        method: CalculationMethod, 
        db_session: AsyncSession
    ) -> Optional[float]:
        """
        Retrieve CPI value for a specific date using the specified method.
        """
        
        # Check cache first
        if target_date in self._cpi_cache and self._is_cache_valid():
            record_business_metric("cpi_cache_hits", 1)
            return self._cpi_cache[target_date]

        record_business_metric("cpi_cache_misses", 1)

        try:
            if method == CalculationMethod.EXACT_DATE:
                cpi_value = await self._get_exact_date_cpi(target_date, db_session)
            elif method == CalculationMethod.NEAREST_DATE:
                cpi_value = await self._get_nearest_date_cpi(target_date, db_session)
            elif method == CalculationMethod.INTERPOLATED:
                cpi_value = await self._get_interpolated_cpi(target_date, db_session)
            elif method == CalculationMethod.MONTHLY_AVERAGE:
                cpi_value = await self._get_monthly_average_cpi(target_date, db_session)
            else:
                raise CPICalculationError(f"Unknown calculation method: {method}")

            # Cache the result
            if cpi_value is not None:
                self._cpi_cache[target_date] = cpi_value
                self._last_cache_update = datetime.now()

            return cpi_value

        except Exception as e:
            self.logger.error(f"Error retrieving CPI for date {target_date}: {str(e)}")
            raise CPICalculationError(f"Failed to retrieve CPI data: {str(e)}")

    async def _get_exact_date_cpi(self, target_date: date, db_session: AsyncSession) -> Optional[float]:
        """Get CPI for exact date match."""
        query = select(CPIData.value).where(CPIData.date == target_date)
        result = await db_session.execute(query)
        cpi_record = result.scalar_one_or_none()
        return float(cpi_record) if cpi_record is not None else None

    async def _get_nearest_date_cpi(self, target_date: date, db_session: AsyncSession) -> Optional[float]:
        """Get CPI for nearest available date (preferring earlier dates)."""
        # Try to get CPI for date on or before target date
        query = (
            select(CPIData.value)
            .where(CPIData.date <= target_date)
            .order_by(desc(CPIData.date))
            .limit(1)
        )
        result = await db_session.execute(query)
        cpi_record = result.scalar_one_or_none()
        
        if cpi_record is not None:
            return float(cpi_record)

        # If no earlier date, try to get the nearest later date
        query = (
            select(CPIData.value)
            .where(CPIData.date > target_date)
            .order_by(CPIData.date)
            .limit(1)
        )
        result = await db_session.execute(query)
        cpi_record = result.scalar_one_or_none()
        return float(cpi_record) if cpi_record is not None else None

    async def _get_interpolated_cpi(self, target_date: date, db_session: AsyncSession) -> Optional[float]:
        """Get interpolated CPI value between two known dates."""
        # Get the nearest dates before and after target date
        before_query = (
            select(CPIData.date, CPIData.value)
            .where(CPIData.date <= target_date)
            .order_by(desc(CPIData.date))
            .limit(1)
        )
        
        after_query = (
            select(CPIData.date, CPIData.value)
            .where(CPIData.date > target_date)
            .order_by(CPIData.date)
            .limit(1)
        )

        before_result = await db_session.execute(before_query)
        after_result = await db_session.execute(after_query)
        
        before_record = before_result.first()
        after_record = after_result.first()

        if before_record is None and after_record is None:
            return None
        elif before_record is None:
            return float(after_record.value)
        elif after_record is None:
            return float(before_record.value)
        else:
            # Perform linear interpolation
            before_date, before_value = before_record
            after_date, after_value = after_record
            
            if before_date == after_date:
                return float(before_value)
            
            # Calculate interpolated value
            days_total = (after_date - before_date).days
            days_from_before = (target_date - before_date).days
            
            interpolation_factor = days_from_before / days_total
            interpolated_value = before_value + (after_value - before_value) * interpolation_factor
            
            return float(interpolated_value)

    async def _get_monthly_average_cpi(self, target_date: date, db_session: AsyncSession) -> Optional[float]:
        """Get monthly average CPI for the target month."""
        # Get all CPI values for the target month
        month_start = target_date.replace(day=1)
        if target_date.month == 12:
            month_end = date(target_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(target_date.year, target_date.month + 1, 1) - timedelta(days=1)

        query = (
            select(CPIData.value)
            .where(and_(CPIData.date >= month_start, CPIData.date <= month_end))
        )
        
        result = await db_session.execute(query)
        values = [float(row[0]) for row in result.fetchall()]
        
        if not values:
            return None
        
        return sum(values) / len(values)

    def _is_cache_valid(self) -> bool:
        """Check if the CPI cache is still valid."""
        return datetime.now() - self._last_cache_update < self._cache_ttl

    def clear_cache(self):
        """Clear the CPI cache."""
        self._cpi_cache.clear()
        self._last_cache_update = datetime.min

    async def bulk_calculate_gaps(
        self, 
        requests: List[CPICalculationRequest],
        db_session: Optional[AsyncSession] = None
    ) -> List[InflationAdjustmentResult]:
        """
        Perform bulk salary gap calculations for multiple requests.
        Optimized for performance with batch CPI data retrieval.
        """
        start_time = datetime.now()
        
        try:
            if db_session is None:
                async with get_db_session() as session:
                    return await self._perform_bulk_calculation(requests, session)
            else:
                return await self._perform_bulk_calculation(requests, db_session)
        
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            record_business_metric("bulk_cpi_calculation_duration", duration, {
                "request_count": len(requests)
            })

    async def _perform_bulk_calculation(
        self, 
        requests: List[CPICalculationRequest], 
        db_session: AsyncSession
    ) -> List[InflationAdjustmentResult]:
        """Perform bulk calculations with optimized database queries."""
        
        # Collect all unique dates needed
        all_dates = set()
        for request in requests:
            all_dates.add(request.historical_date)
            all_dates.add(request.current_date)

        # Batch fetch all required CPI data
        await self._batch_load_cpi_data(list(all_dates), db_session)

        # Perform individual calculations using cached data
        results = []
        for request in requests:
            try:
                result = await self.calculate_salary_gap(request, db_session)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Bulk calculation failed for request: {request.dict()}, error: {str(e)}")
                # Continue with other calculations
                continue

        record_business_metric("bulk_cpi_calculations_completed", len(results))
        return results

    async def _batch_load_cpi_data(self, dates: List[date], db_session: AsyncSession):
        """Batch load CPI data for multiple dates."""
        query = select(CPIData.date, CPIData.value).where(CPIData.date.in_(dates))
        result = await db_session.execute(query)
        
        for date_val, cpi_val in result.fetchall():
            self._cpi_cache[date_val] = float(cpi_val)
        
        self._last_cache_update = datetime.now()

    async def get_inflation_summary(
        self, 
        start_date: date, 
        end_date: date,
        db_session: Optional[AsyncSession] = None
    ) -> Dict[str, Any]:
        """
        Get inflation summary statistics for a date range.
        Useful for dashboard displays and analysis.
        """
        if db_session is None:
            async with get_db_session() as session:
                return await self._get_inflation_summary(start_date, end_date, session)
        else:
            return await self._get_inflation_summary(start_date, end_date, db_session)

    async def _get_inflation_summary(
        self, 
        start_date: date, 
        end_date: date, 
        db_session: AsyncSession
    ) -> Dict[str, Any]:
        """Calculate inflation summary statistics."""
        
        start_cpi = await self._get_nearest_date_cpi(start_date, db_session)
        end_cpi = await self._get_nearest_date_cpi(end_date, db_session)
        
        if start_cpi is None or end_cpi is None:
            raise CPIDataNotFoundError("Insufficient CPI data for summary calculation")

        total_inflation = ((end_cpi - start_cpi) / start_cpi) * 100
        years = (end_date - start_date).days / 365.25
        annualized_inflation = ((end_cpi / start_cpi) ** (1 / years) - 1) * 100 if years > 0 else 0

        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "start_cpi": start_cpi,
            "end_cpi": end_cpi,
            "total_inflation_percent": round(total_inflation, 2),
            "annualized_inflation_percent": round(annualized_inflation, 2),
            "years": round(years, 2),
            "purchasing_power_loss": round(100 - (100 / (1 + total_inflation / 100)), 2)
        }


# Create singleton instance
cpi_calculator = CPICalculatorService()
