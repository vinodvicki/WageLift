"""
CPI Data Service for WageLift application.

This service manages Consumer Price Index data by integrating the BLS API
with PostgreSQL storage. It provides data access, caching, and automated
data management capabilities.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any, Tuple
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func, desc

from app.core.database import SessionLocal
from app.models.cpi_data import CPIData
from app.services.bls_service import bls_service, CPIDataPoint, BLSAPIError

logger = logging.getLogger(__name__)


class CPIDataService:
    """Service for managing CPI data with database storage and BLS API integration."""
    
    def __init__(self):
        """Initialize the CPI data service."""
        self.bls_service = bls_service
    
    def get_db_session(self) -> Session:
        """Get a database session."""
        return SessionLocal()
    
    def fetch_and_store_latest_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetch the latest CPI data from BLS API and store in database.
        
        Args:
            force_refresh: If True, fetch data regardless of last update
            
        Returns:
            Dictionary with operation results
        """
        results = {
            "success": False,
            "message": "",
            "new_records": 0,
            "updated_records": 0,
            "total_records": 0,
            "latest_date": None,
            "errors": []
        }
        
        db = self.get_db_session()
        try:
            # Check if we need to fetch new data
            if not force_refresh:
                latest_record = self.get_latest_cpi_record(db)
                if latest_record:
                    # Don't fetch if we have data from current month
                    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                    latest_record_date = datetime.combine(latest_record.reference_date, datetime.min.time())
                    
                    if latest_record_date >= current_month_start:
                        results["message"] = "Current month data already exists"
                        results["success"] = True
                        results["total_records"] = self.get_total_records_count(db)
                        return results
            
            # Fetch data from BLS API
            current_year = datetime.now().year
            start_year = current_year - 2  # Get last 2 years of data
            
            logger.info(f"Fetching CPI data from BLS API for {start_year}-{current_year}")
            
            try:
                cpi_data_points = self.bls_service.get_cpi_range(start_year, current_year)
            except BLSAPIError as e:
                results["errors"].append(f"BLS API Error: {str(e)}")
                results["message"] = "Failed to fetch data from BLS API"
                return results
            
            if not cpi_data_points:
                results["message"] = "No data received from BLS API"
                return results
            
            # Store data in database
            new_count = 0
            updated_count = 0
            
            for data_point in cpi_data_points:
                try:
                    stored_record, is_new = self.store_cpi_data_point(db, data_point)
                    if stored_record:
                        if is_new:
                            new_count += 1
                        else:
                            updated_count += 1
                except Exception as e:
                    error_msg = f"Error storing data point {data_point.date}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
            
            # Calculate inflation rates for new records
            self.calculate_and_update_inflation_rates(db)
            
            db.commit()
            
            results.update({
                "success": True,
                "message": f"Successfully processed {len(cpi_data_points)} data points",
                "new_records": new_count,
                "updated_records": updated_count,
                "total_records": self.get_total_records_count(db),
                "latest_date": max([dp.date for dp in cpi_data_points]).strftime('%Y-%m-%d') if cpi_data_points else None
            })
            
            logger.info(f"CPI data update completed: {new_count} new, {updated_count} updated records")
            
        except Exception as e:
            db.rollback()
            error_msg = f"Database error during CPI data update: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["message"] = "Database operation failed"
        
        finally:
            db.close()
        
        return results
    
    def store_cpi_data_point(self, db: Session, data_point: CPIDataPoint) -> Tuple[Optional[CPIData], bool]:
        """
        Store a single CPI data point in the database.
        
        Args:
            db: Database session
            data_point: CPI data point from BLS API
            
        Returns:
            CPIData record (new or updated)
        """
        try:
            # Check if record already exists
            existing_record = db.query(CPIData).filter(
                and_(
                    CPIData.year == data_point.year,
                    CPIData.month == data_point.date.month,
                    CPIData.series_id == self.bls_service.CPI_SERIES_ID,
                    CPIData.region == "US"
                )
            ).first()
            
            if existing_record:
                # Update existing record
                existing_record.cpi_value = Decimal(str(data_point.value))
                existing_record.reference_date = data_point.date.date()
                existing_record.updated_at = datetime.now()
                
                logger.debug(f"Updated existing CPI record for {data_point.date.strftime('%Y-%m')}")
                return existing_record, False
            else:
                # Create new record
                new_record = CPIData(
                    year=data_point.year,
                    month=data_point.date.month,
                    cpi_value=Decimal(str(data_point.value)),
                    cpi_u_value=Decimal(str(data_point.value)),  # CUSR0000SA0 is CPI-U
                    reference_date=data_point.date.date(),
                    data_source="BLS",
                    series_id=self.bls_service.CPI_SERIES_ID,
                    region="US",
                    is_seasonal_adjusted=True,
                    is_preliminary=False,
                    is_revised=False
                )
                
                db.add(new_record)
                
                logger.debug(f"Created new CPI record for {data_point.date.strftime('%Y-%m')}")
                return new_record, True
               
        except IntegrityError as e:
            db.rollback()
            logger.warning(f"Integrity error storing CPI data for {data_point.date}: {str(e)}")
            return None, False
        except Exception as e:
            logger.error(f"Error storing CPI data point: {str(e)}")
            raise
    
    def calculate_and_update_inflation_rates(self, db: Session):
        """Calculate and update inflation rates for CPI records."""
        try:
            # Get all records ordered by date
            records = db.query(CPIData).filter(
                CPIData.series_id == self.bls_service.CPI_SERIES_ID
            ).order_by(CPIData.year, CPIData.month).all()
            
            if len(records) < 2:
                return
            
            # Calculate month-over-month rates
            for i in range(1, len(records)):
                current_record = records[i]
                previous_record = records[i - 1]
                
                if current_record.cpi_value and previous_record.cpi_value:
                    monthly_rate = CPIData.calculate_inflation_rate(
                        current_record.cpi_value,
                        previous_record.cpi_value
                    )
                    current_record.monthly_inflation_rate = monthly_rate
            
            # Calculate year-over-year rates
            for i, record in enumerate(records):
                # Find record from 12 months ago
                target_year = record.year - 1
                target_month = record.month
                
                previous_year_record = next(
                    (r for r in records 
                     if r.year == target_year and r.month == target_month),
                    None
                )
                
                if previous_year_record and previous_year_record.cpi_value:
                    annual_rate = CPIData.calculate_inflation_rate(
                        record.cpi_value,
                        previous_year_record.cpi_value
                    )
                    record.annual_inflation_rate = annual_rate
            
            logger.info("Updated inflation rates for CPI records")
            
        except Exception as e:
            logger.error(f"Error calculating inflation rates: {str(e)}")
            raise
    
    def get_latest_cpi_record(self, db: Session) -> Optional[CPIData]:
        """Get the most recent CPI record from database."""
        return db.query(CPIData).filter(
            CPIData.series_id == self.bls_service.CPI_SERIES_ID
        ).order_by(desc(CPIData.year), desc(CPIData.month)).first()
    
    def get_total_records_count(self, db: Session) -> int:
        """Get total count of CPI records in database."""
        return db.query(CPIData).filter(
            CPIData.series_id == self.bls_service.CPI_SERIES_ID
        ).count()
    
    def get_cpi_data_range(
        self, 
        start_date: date, 
        end_date: date, 
        db: Optional[Session] = None
    ) -> List[CPIData]:
        """
        Get CPI data for a specific date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            db: Database session (optional)
            
        Returns:
            List of CPIData records
        """
        should_close_db = False
        if db is None:
            db = self.get_db_session()
            should_close_db = True
        
        try:
            records = db.query(CPIData).filter(
                and_(
                    CPIData.series_id == self.bls_service.CPI_SERIES_ID,
                    CPIData.reference_date >= start_date,
                    CPIData.reference_date <= end_date
                )
            ).order_by(CPIData.reference_date).all()
            
            return records
            
        finally:
            if should_close_db:
                db.close()
    
    def get_inflation_rate_between_dates(
        self, 
        start_date: date, 
        end_date: date
    ) -> Optional[Decimal]:
        """
        Calculate inflation rate between two dates using database records.
        
        Args:
            start_date: Starting date
            end_date: Ending date
            
        Returns:
            Inflation rate as decimal or None if insufficient data
        """
        db = self.get_db_session()
        try:
            # Get CPI data closest to the requested dates
            start_record = db.query(CPIData).filter(
                and_(
                    CPIData.series_id == self.bls_service.CPI_SERIES_ID,
                    CPIData.reference_date <= start_date
                )
            ).order_by(desc(CPIData.reference_date)).first()
            
            end_record = db.query(CPIData).filter(
                and_(
                    CPIData.series_id == self.bls_service.CPI_SERIES_ID,
                    CPIData.reference_date <= end_date
                )
            ).order_by(desc(CPIData.reference_date)).first()
            
            if not start_record or not end_record:
                return None
            
            if start_record.cpi_value and end_record.cpi_value:
                return CPIData.calculate_inflation_rate(
                    end_record.cpi_value,
                    start_record.cpi_value
                )
            
            return None
            
        finally:
            db.close()
    
    def get_current_vs_previous_year_inflation(self) -> Optional[Decimal]:
        """
        Get current year-over-year inflation rate.
        
        Returns:
            Annual inflation rate as decimal or None if unavailable
        """
        db = self.get_db_session()
        try:
            latest_record = self.get_latest_cpi_record(db)
            if latest_record and latest_record.annual_inflation_rate:
                return latest_record.annual_inflation_rate
            
            return None
            
        finally:
            db.close()
    
    def get_data_freshness_status(self) -> Dict[str, Any]:
        """
        Get information about data freshness and coverage.
        
        Returns:
            Dictionary with data freshness information
        """
        db = self.get_db_session()
        try:
            latest_record = self.get_latest_cpi_record(db)
            total_records = self.get_total_records_count(db)
            
            if not latest_record:
                return {
                    "has_data": False,
                    "latest_date": None,
                    "days_since_latest": None,
                    "total_records": 0,
                    "is_current": False,
                    "needs_update": True
                }
            
            latest_date = latest_record.reference_date
            days_since_latest = (date.today() - latest_date).days
            
            # Consider data current if it's from this month or last month
            current_month_start = date.today().replace(day=1)
            last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            
            is_current = latest_date >= last_month_start
            needs_update = latest_date < last_month_start
            
            return {
                "has_data": True,
                "latest_date": latest_date.strftime('%Y-%m-%d'),
                "days_since_latest": days_since_latest,
                "total_records": total_records,
                "is_current": is_current,
                "needs_update": needs_update,
                "latest_cpi_value": float(latest_record.cpi_value) if latest_record.cpi_value else None,
                "annual_inflation_rate": float(latest_record.annual_inflation_rate) if latest_record.annual_inflation_rate else None
            }
            
        finally:
            db.close()
    
    def cleanup_old_data(self, keep_years: int = 10) -> Dict[str, int]:
        """
        Clean up old CPI data beyond specified years.
        
        Args:
            keep_years: Number of years to keep
            
        Returns:
            Dictionary with cleanup results
        """
        cutoff_year = datetime.now().year - keep_years
        
        db = self.get_db_session()
        try:
            deleted_count = db.query(CPIData).filter(
                and_(
                    CPIData.series_id == self.bls_service.CPI_SERIES_ID,
                    CPIData.year < cutoff_year
                )
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old CPI records (before {cutoff_year})")
            
            return {
                "deleted_count": deleted_count,
                "cutoff_year": cutoff_year
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error during cleanup: {str(e)}")
            raise
        finally:
            db.close()


# Singleton instance for application use
cpi_data_service = CPIDataService() 