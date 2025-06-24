"""
CPIData model for WageLift application.

Stores Consumer Price Index data for inflation calculations.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class CPIData(Base):
    """
    CPIData model representing Consumer Price Index data.
    
    Stores monthly CPI values for calculating inflation impact
    on purchasing power and salary adjustments.
    """
    
    __tablename__ = "cpi_data"

    # Primary key
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Primary key for the CPI data entry"
    )
    
    # Date Information
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        doc="Year of the CPI data"
    )
    
    month: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        doc="Month of the CPI data (1-12)"
    )
    
    # CPI Values
    cpi_value: Mapped[Decimal] = mapped_column(
        Numeric(precision=8, scale=3),
        nullable=False,
        doc="Consumer Price Index value for this period"
    )
    
    # Additional CPI Series (optional)
    cpi_u_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=8, scale=3),
        nullable=True,
        doc="CPI-U (Urban consumers) value"
    )
    
    cpi_w_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=8, scale=3),
        nullable=True,
        doc="CPI-W (Urban wage earners) value"
    )
    
    core_cpi_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=8, scale=3),
        nullable=True,
        doc="Core CPI value (excluding food and energy)"
    )
    
    # Regional Data (optional)
    region: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="US",
        doc="Geographic region (US, Northeast, South, Midwest, West, etc.)"
    )
    
    metro_area: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Specific metropolitan area if applicable"
    )
    
    # Calculated Values
    monthly_inflation_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=6, scale=4),
        nullable=True,
        doc="Month-over-month inflation rate as decimal (0.02 = 2%)"
    )
    
    annual_inflation_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=6, scale=4),
        nullable=True,
        doc="Year-over-year inflation rate as decimal"
    )
    
    # Data Source and Quality
    data_source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="BLS",
        doc="Source of the CPI data (BLS, FRED, etc.)"
    )
    
    series_id: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="BLS or other official series identifier"
    )
    
    is_preliminary: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        doc="Whether this is preliminary data"
    )
    
    is_revised: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        doc="Whether this data has been revised"
    )
    
    is_seasonal_adjusted: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
        doc="Whether the data is seasonally adjusted"
    )
    
    # Reference Period
    reference_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Reference date for this CPI data point"
    )
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the CPI data was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="When the CPI data was last updated"
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint(
            "year", "month", "region", "series_id",
            name="unique_cpi_period_region_series"
        ),
        CheckConstraint(
            "month >= 1 AND month <= 12",
            name="check_valid_month"
        ),
        CheckConstraint(
            "year >= 1900 AND year <= 2100",
            name="check_valid_year"
        ),
        CheckConstraint(
            "cpi_value > 0",
            name="check_positive_cpi_value"
        ),
        CheckConstraint(
            "cpi_u_value IS NULL OR cpi_u_value > 0",
            name="check_positive_cpi_u_value"
        ),
        CheckConstraint(
            "cpi_w_value IS NULL OR cpi_w_value > 0",
            name="check_positive_cpi_w_value"
        ),
        CheckConstraint(
            "core_cpi_value IS NULL OR core_cpi_value > 0",
            name="check_positive_core_cpi_value"
        ),
        CheckConstraint(
            "monthly_inflation_rate IS NULL OR monthly_inflation_rate >= -1.0",
            name="check_reasonable_monthly_inflation"
        ),
        CheckConstraint(
            "annual_inflation_rate IS NULL OR annual_inflation_rate >= -1.0",
            name="check_reasonable_annual_inflation"
        ),
    )

    def __repr__(self) -> str:
        """String representation of the CPI data."""
        return (
            f"<CPIData(id={self.id}, year={self.year}, month={self.month}, "
            f"cpi_value={self.cpi_value}, region={self.region})>"
        )
    
    @property
    def period_display(self) -> str:
        """Get a human-readable period display."""
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return f"{month_names[self.month - 1]} {self.year}"
    
    @property
    def period_short(self) -> str:
        """Get a short period display (YYYY-MM)."""
        return f"{self.year}-{self.month:02d}"
    
    @classmethod
    def calculate_inflation_rate(
        cls,
        current_cpi: Decimal,
        previous_cpi: Decimal
    ) -> Decimal:
        """Calculate inflation rate between two CPI values."""
        if previous_cpi <= 0:
            raise ValueError("Previous CPI must be positive")
        return ((current_cpi - previous_cpi) / previous_cpi)
    
    @classmethod
    def calculate_purchasing_power_loss(
        cls,
        salary: Decimal,
        start_cpi: Decimal,
        end_cpi: Decimal
    ) -> Decimal:
        """Calculate purchasing power loss due to inflation."""
        if start_cpi <= 0 or end_cpi <= 0:
            raise ValueError("CPI values must be positive")
        
        inflation_rate = cls.calculate_inflation_rate(end_cpi, start_cpi)
        return salary * inflation_rate
    
    @classmethod
    def calculate_inflation_adjusted_salary(
        cls,
        original_salary: Decimal,
        start_cpi: Decimal,
        end_cpi: Decimal
    ) -> Decimal:
        """Calculate what salary should be to maintain purchasing power."""
        if start_cpi <= 0:
            raise ValueError("Start CPI must be positive")
        return original_salary * (end_cpi / start_cpi)
    
    def is_current_month(self) -> bool:
        """Check if this CPI data is for the current month."""
        today = date.today()
        return self.year == today.year and self.month == today.month
    
    def is_recent(self, months: int = 3) -> bool:
        """Check if this CPI data is within the last N months."""
        from datetime import timedelta
        cutoff_date = date.today() - timedelta(days=months * 30)  # Approximate
        return self.reference_date >= cutoff_date 