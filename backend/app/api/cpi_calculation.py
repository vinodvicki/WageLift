# backend/app/api/cpi_calculation.py
"""
CPI Calculation API endpoints for WageLift.

This module provides API endpoints for CPI (Consumer Price Index) calculations,
including inflation gap analysis and purchasing power calculations.
"""

import logging
from datetime import date, datetime
from typing import Dict, Any, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession

# Internal imports
from ..core.auth import get_current_user, Auth0User
from ..core.database import get_db
from ..core.metrics import record_business_metric, metrics_collector
from ..core.logging import get_logger
from ..models.user import User
from ..services.cpi_calculator import CPICalculatorService
from ..services.cpi_data_service import CPIDataService

# Initialize router and logger
router = APIRouter(prefix="/api/v1/cpi", tags=["CPI Calculations"])
logger = get_logger(__name__, component="cpi_api")


# Simplified request/response models
class CPICalculationRequest(BaseModel):
    """Model for CPI calculation request."""
    current_salary: float = Field(..., gt=0, description="Current annual salary")
    last_raise_date: date = Field(..., description="Date of last salary raise")
    location: Optional[str] = Field(None, description="Location for regional CPI data")
    
    @validator('last_raise_date')
    def validate_raise_date(cls, v):
        if v > date.today():
            raise ValueError('Last raise date cannot be in the future')
        return v

class CPICalculationResponse(BaseModel):
    """Model for CPI calculation response."""
    current_salary: float
    last_raise_date: date
    calculation_date: datetime
    inflation_rate: float
    purchasing_power_loss: float
    adjusted_salary_needed: float
    cpi_gap_amount: float
    cpi_gap_percentage: float
    cpi_data_period: str
    
    class Config:
        from_attributes = True

class CPIDataResponse(BaseModel):
    """Model for CPI data response."""
    period: str
    value: float
    series_id: str
    area: str
    item: str
    
    class Config:
        from_attributes = True


class InflationSummaryRequest(BaseModel):
    """Request model for inflation summary statistics."""
    start_date: date = Field(..., description="Start date for inflation analysis")
    end_date: date = Field(..., description="End date for inflation analysis")

    @validator('end_date')
    def validate_date_range(cls, v, values):
        """Ensure end date is after start date."""
        start_date = values.get('start_date')
        if start_date and v <= start_date:
            raise ValueError("End date must be after start date")
        return v


class InflationSummaryResponse(BaseModel):
    """Response model for inflation summary statistics."""
    success: bool = True
    summary: Dict[str, Any]
    timestamp: datetime


# Simplified calculation functions
def calculate_inflation_adjustment(
    original_salary: float,
    current_salary: float,
    historical_date: date,
    current_date: date
) -> Dict[str, Any]:
    """
    Simplified inflation calculation using basic formula.
    In a full implementation, this would use actual CPI data from the database.
    """
    # Simplified calculation - in real implementation, fetch CPI data from database
    # For now, use approximate inflation rate of 3% per year
    years_elapsed = (current_date - historical_date).days / 365.25
    assumed_inflation_rate = 0.03  # 3% per year
    
    # Calculate adjusted salary
    adjusted_salary = original_salary * ((1 + assumed_inflation_rate) ** years_elapsed)
    
    # Calculate gaps
    dollar_gap = adjusted_salary - current_salary
    percentage_gap = (dollar_gap / adjusted_salary) * 100 if adjusted_salary > 0 else 0
    
    return {
        "adjusted_salary": round(adjusted_salary, 2),
        "percentage_gap": round(percentage_gap, 1),
        "dollar_gap": round(dollar_gap, 2),
        "original_salary": original_salary,
        "current_salary": current_salary,
        "inflation_rate": round(assumed_inflation_rate * 100 * years_elapsed, 1),
        "years_elapsed": round(years_elapsed, 1),
        "calculation_method": "simplified_estimation"
    }


def get_inflation_summary_data(start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Simplified inflation summary calculation.
    In a full implementation, this would query actual CPI data.
    """
    years_elapsed = (end_date - start_date).days / 365.25
    assumed_annual_inflation = 3.0  # 3% per year
    
    total_inflation = ((1.03 ** years_elapsed) - 1) * 100
    annualized_inflation = assumed_annual_inflation
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_inflation_percent": round(total_inflation, 1),
        "annualized_inflation_percent": round(annualized_inflation, 1),
        "years_analyzed": round(years_elapsed, 1),
        "purchasing_power_loss": round(total_inflation, 1),
        "calculation_method": "simplified_estimation",
        "note": "This is a simplified calculation. Full implementation will use actual BLS CPI data."
    }


# API Endpoints

@router.post("/calculate", response_model=CPICalculationResponse)
async def calculate_cpi_gap(
    calculation_request: CPICalculationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate the CPI gap and purchasing power loss for a given salary and raise date.
    """
    try:
        cpi_calculator = CPICalculatorService()
        
        # Perform CPI calculation
        result = await cpi_calculator.calculate_inflation_impact(
            current_salary=Decimal(str(calculation_request.current_salary)),
            last_raise_date=calculation_request.last_raise_date,
            location=calculation_request.location
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to calculate CPI gap"
            )
        
        return CPICalculationResponse(
            current_salary=calculation_request.current_salary,
            last_raise_date=calculation_request.last_raise_date,
            calculation_date=datetime.now(),
            inflation_rate=float(result['inflation_rate']),
            purchasing_power_loss=float(result['purchasing_power_loss']),
            adjusted_salary_needed=float(result['adjusted_salary_needed']),
            cpi_gap_amount=float(result['cpi_gap_amount']),
            cpi_gap_percentage=float(result['cpi_gap_percentage']),
            cpi_data_period=result['cpi_data_period']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating CPI gap: {str(e)}"
        )

@router.get("/current-cpi", response_model=CPIDataResponse)
async def get_current_cpi(
    location: Optional[str] = Query(None, description="Location for regional CPI data"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current CPI data for a location.
    """
    try:
        cpi_data_service = CPIDataService()
        
        # Get current CPI data
        cpi_data = await cpi_data_service.get_latest_cpi_data(location)
        
        if not cpi_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="CPI data not found for the specified location"
            )
        
        return CPIDataResponse(
            period=cpi_data['period'],
            value=cpi_data['value'],
            series_id=cpi_data['series_id'],
            area=cpi_data.get('area', 'US'),
            item=cpi_data.get('item', 'All Items')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving CPI data: {str(e)}"
        )

@router.get("/historical-cpi")
async def get_historical_cpi(
    start_date: date = Query(..., description="Start date for historical data"),
    end_date: Optional[date] = Query(None, description="End date for historical data"),
    location: Optional[str] = Query(None, description="Location for regional CPI data"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical CPI data for a date range and location.
    """
    try:
        if end_date is None:
            end_date = date.today()
            
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )
        
        cpi_data_service = CPIDataService()
        
        # Get historical CPI data
        historical_data = await cpi_data_service.get_historical_cpi_data(
            start_date=start_date,
            end_date=end_date,
            location=location
        )
        
        if not historical_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No historical CPI data found for the specified criteria"
            )
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "location": location or "US",
            "data_points": len(historical_data),
            "cpi_data": historical_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving historical CPI data: {str(e)}"
        )

@router.get("/inflation-rate")
async def get_inflation_rate(
    start_date: date = Query(..., description="Start date for inflation calculation"),
    end_date: Optional[date] = Query(None, description="End date for inflation calculation"),
    location: Optional[str] = Query(None, description="Location for regional CPI data"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate the inflation rate between two dates.
    """
    try:
        if end_date is None:
            end_date = date.today()
            
        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )
        
        cpi_calculator = CPICalculator()
        
        # Calculate inflation rate
        inflation_rate = await cpi_calculator.calculate_inflation_rate(
            start_date=start_date,
            end_date=end_date,
            location=location
        )
        
        if inflation_rate is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unable to calculate inflation rate for the specified period"
            )
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "location": location or "US",
            "inflation_rate": float(inflation_rate),
            "inflation_percentage": float(inflation_rate * 100),
            "calculation_date": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating inflation rate: {str(e)}"
        )

@router.post("/batch-calculate")
async def batch_calculate_cpi(
    calculations: list[CPICalculationRequest],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Perform batch CPI calculations for multiple salary entries.
    """
    try:
        if len(calculations) > 50:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size cannot exceed 50 calculations"
            )
        
        cpi_calculator = CPICalculator()
        results = []
        
        for calc_request in calculations:
            try:
                result = await cpi_calculator.calculate_inflation_impact(
                    current_salary=Decimal(str(calc_request.current_salary)),
                    last_raise_date=calc_request.last_raise_date,
                    location=calc_request.location
                )
                
                if result:
                    results.append(CPICalculationResponse(
                        current_salary=calc_request.current_salary,
                        last_raise_date=calc_request.last_raise_date,
                        calculation_date=datetime.now(),
                        inflation_rate=float(result['inflation_rate']),
                        purchasing_power_loss=float(result['purchasing_power_loss']),
                        adjusted_salary_needed=float(result['adjusted_salary_needed']),
                        cpi_gap_amount=float(result['cpi_gap_amount']),
                        cpi_gap_percentage=float(result['cpi_gap_percentage']),
                        cpi_data_period=result['cpi_data_period']
                    ))
                else:
                    results.append(None)  # Failed calculation
                    
            except Exception as e:
                results.append(None)  # Failed calculation
        
        successful_calculations = sum(1 for r in results if r is not None)
        
        return {
            "total_requests": len(calculations),
            "successful_calculations": successful_calculations,
            "failed_calculations": len(calculations) - successful_calculations,
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing batch CPI calculations: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for CPI calculation service.
    """
    try:
        return {
            "status": "healthy",
            "service": "CPI Calculation Service",
            "timestamp": datetime.now().isoformat(),
            "version": "simplified",
            "note": "This is a simplified implementation. Full CPI integration coming soon."
        }

    except Exception as e:
        logger.error("Health check failed", error=str(e), exc_info=True)
        return {
            "status": "unhealthy",
            "service": "CPI Calculation Service",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }