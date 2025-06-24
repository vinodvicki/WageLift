"""
BLS (Bureau of Labor Statistics) API Service for fetching CPI data.

This service handles fetching Consumer Price Index data from the BLS Public Data API,
specifically the CUSR0000SA0 series (All Urban Consumers - All Items).
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


@dataclass
class CPIDataPoint:
    """Represents a single CPI data point."""
    date: datetime
    value: float
    period_name: str
    year: int
    period: str
    footnotes: Optional[List[Dict[str, Any]]] = None


class BLSAPIError(Exception):
    """Custom exception for BLS API errors."""
    pass


class RateLimitError(BLSAPIError):
    """Exception raised when rate limit is exceeded."""
    pass


def rate_limit_retry(max_retries: int = 3, base_delay: int = 1):
    """Decorator to handle rate limiting with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    if attempt == max_retries:
                        raise e
                    
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(delay)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"API error: {str(e)}, retrying in {delay}s (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(delay)
            
            return None
        return wrapper
    return decorator


class BLSService:
    """Service for interacting with the BLS Public Data API."""
    
    BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data"
    CPI_SERIES_ID = "CUSR0000SA0"  # All Urban Consumers - All Items
    RATE_LIMIT_DELAY = 2.5  # Seconds between requests (25 requests per 10 seconds)
    
    def __init__(self, registration_key: Optional[str] = None):
        """
        Initialize BLS service.
        
        Args:
            registration_key: Optional BLS API registration key for higher rate limits
        """
        self.registration_key = registration_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WageLift/1.0 (contact@wagelift.com)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.last_request_time = 0
    
    def _respect_rate_limit(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    @rate_limit_retry(max_retries=3, base_delay=2)
    def fetch_cpi_data(
        self, 
        start_year: Optional[int] = None, 
        end_year: Optional[int] = None,
        series_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch CPI data from BLS API.
        
        Args:
            start_year: Starting year for data (YYYY format)
            end_year: Ending year for data (YYYY format)
            series_id: BLS series ID (defaults to CUSR0000SA0)
            
        Returns:
            Raw JSON response from BLS API
            
        Raises:
            BLSAPIError: If API request fails or returns error
            RateLimitError: If rate limit is exceeded
        """
        self._respect_rate_limit()
        
        # Use default CPI series if not specified
        if series_id is None:
            series_id = self.CPI_SERIES_ID
        
        url = f"{self.BASE_URL}/{series_id}"
        params = {}
        
        # Add year range if specified
        if start_year and end_year:
            params['startyear'] = str(start_year)
            params['endyear'] = str(end_year)
        
        # Add registration key if available
        if self.registration_key:
            params['registrationkey'] = self.registration_key
        
        try:
            logger.info(f"Fetching CPI data for series {series_id} from {start_year or 'beginning'} to {end_year or 'latest'}")
            response = self.session.get(url, params=params, timeout=30)
            
            # Check for rate limiting
            if response.status_code == 429:
                raise RateLimitError("BLS API rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()
            
            # Check API-level errors
            if data.get('status') != 'REQUEST_SUCCEEDED':
                error_messages = data.get('message', ['Unknown error'])
                raise BLSAPIError(f"BLS API error: {'; '.join(error_messages)}")
            
            logger.info(f"Successfully fetched CPI data: {len(data.get('Results', {}).get('series', [{}])[0].get('data', []))} data points")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch CPI data: {str(e)}")
            raise BLSAPIError(f"Network error fetching CPI data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching CPI data: {str(e)}")
            raise BLSAPIError(f"Unexpected error: {str(e)}")
    
    def process_cpi_data(self, raw_data: Dict[str, Any]) -> List[CPIDataPoint]:
        """
        Process raw BLS API response into structured data points.
        
        Args:
            raw_data: Raw JSON response from BLS API
            
        Returns:
            List of CPIDataPoint objects sorted by date
            
        Raises:
            BLSAPIError: If data processing fails
        """
        try:
            series_data = raw_data['Results']['series'][0]['data']
            processed_data = []
            
            for item in series_data:
                # Parse period (M01-M12 for months, Q01-Q04 for quarters, A01 for annual)
                period = item['period']
                year = int(item['year'])
                
                # Handle different period types
                if period.startswith('M'):
                    month = int(period[1:])
                    date = datetime(year, month, 1)
                elif period.startswith('Q'):
                    quarter = int(period[1:])
                    month = (quarter - 1) * 3 + 1
                    date = datetime(year, month, 1)
                elif period == 'A01':
                    date = datetime(year, 1, 1)
                else:
                    logger.warning(f"Unknown period format: {period}")
                    continue
                
                # Convert value to float
                try:
                    value = float(item['value'])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid CPI value: {item['value']}")
                    continue
                
                data_point = CPIDataPoint(
                    date=date,
                    value=value,
                    period_name=item.get('periodName', ''),
                    year=year,
                    period=period,
                    footnotes=item.get('footnotes', [])
                )
                
                processed_data.append(data_point)
            
            # Sort by date
            processed_data.sort(key=lambda x: x.date)
            
            logger.info(f"Processed {len(processed_data)} CPI data points")
            return processed_data
            
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Failed to process CPI data: {str(e)}")
            raise BLSAPIError(f"Data processing error: {str(e)}")
    
    def get_latest_cpi(self) -> Optional[CPIDataPoint]:
        """
        Get the most recent CPI data point.
        
        Returns:
            Latest CPIDataPoint or None if no data available
        """
        current_year = datetime.now().year
        start_year = current_year - 1  # Get last 2 years to ensure we have recent data
        
        try:
            raw_data = self.fetch_cpi_data(start_year=start_year, end_year=current_year)
            processed_data = self.process_cpi_data(raw_data)
            
            if processed_data:
                return processed_data[-1]  # Return most recent
            return None
            
        except BLSAPIError as e:
            logger.error(f"Failed to get latest CPI: {str(e)}")
            return None
    
    def get_cpi_range(self, start_year: int, end_year: int) -> List[CPIDataPoint]:
        """
        Get CPI data for a specific year range.
        
        Args:
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            List of CPIDataPoint objects in date order
        """
        raw_data = self.fetch_cpi_data(start_year=start_year, end_year=end_year)
        return self.process_cpi_data(raw_data)
    
    def calculate_inflation_rate(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[float]:
        """
        Calculate inflation rate between two dates.
        
        Args:
            start_date: Starting date
            end_date: Ending date
            
        Returns:
            Inflation rate as decimal (e.g., 0.05 for 5%) or None if data unavailable
        """
        try:
            # Get data covering the range
            start_year = start_date.year
            end_year = end_date.year
            
            cpi_data = self.get_cpi_range(start_year, end_year)
            
            if not cpi_data:
                return None
            
            # Find closest data points
            start_cpi = None
            end_cpi = None
            
            for data_point in cpi_data:
                if data_point.date <= start_date:
                    start_cpi = data_point
                if data_point.date <= end_date:
                    end_cpi = data_point
            
            if not start_cpi or not end_cpi or start_cpi.value == 0:
                return None
            
            # Calculate inflation rate
            inflation_rate = (end_cpi.value - start_cpi.value) / start_cpi.value
            
            logger.info(f"Calculated inflation rate: {inflation_rate:.4f} ({inflation_rate * 100:.2f}%)")
            return inflation_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate inflation rate: {str(e)}")
            return None
    
    def get_annual_inflation_rate(self, year: int) -> Optional[float]:
        """
        Get year-over-year inflation rate for a specific year.
        
        Args:
            year: Year to calculate inflation for
            
        Returns:
            Annual inflation rate as decimal or None if data unavailable
        """
        try:
            # Get data for current year and previous year
            cpi_data = self.get_cpi_range(year - 1, year)
            
            if len(cpi_data) < 2:
                return None
            
            # Find December values for both years (or latest available)
            prev_year_cpi = None
            current_year_cpi = None
            
            for data_point in cpi_data:
                if data_point.year == year - 1:
                    if prev_year_cpi is None or data_point.date > prev_year_cpi.date:
                        prev_year_cpi = data_point
                elif data_point.year == year:
                    if current_year_cpi is None or data_point.date > current_year_cpi.date:
                        current_year_cpi = data_point
            
            if not prev_year_cpi or not current_year_cpi:
                return None
            
            # Calculate annual inflation
            inflation_rate = (current_year_cpi.value - prev_year_cpi.value) / prev_year_cpi.value
            
            logger.info(f"Annual inflation rate for {year}: {inflation_rate:.4f} ({inflation_rate * 100:.2f}%)")
            return inflation_rate
            
        except Exception as e:
            logger.error(f"Failed to calculate annual inflation rate: {str(e)}")
            return None


# Singleton instance for application use
bls_service = BLSService() 