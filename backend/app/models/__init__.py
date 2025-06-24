"""
Model imports for WageLift application.

This module handles all model imports and provides a centralized
access point for database models.
"""

# Import Base from database first to avoid circular imports
from app.core.database import Base

# Import all models
from .user import User
from .salary_entry import SalaryEntry
from .benchmark import Benchmark

# Export all models
__all__ = [
    "Base",
    "User", 
    "SalaryEntry",
    "Benchmark"
] 