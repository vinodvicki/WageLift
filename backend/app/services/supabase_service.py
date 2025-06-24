"""
Supabase Service for WageLift Backend
Handles database operations using Supabase Python client
"""

import os
import logging
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        """Initialize Supabase client using JavaScript pattern"""
        self.supabase_url = "https://rtmegwnspngsxtixdhat.supabase.co"
        self.supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0bWVnd25zcG5nc3h0aXhkaGF0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1NTczOTksImV4cCI6MjA2NjEzMzM5OX0.DdZ48QWj-lwyaWmUVW-CbIO-qKVrb6b6MRTdfBYDO3g")
        
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully with JavaScript pattern")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    async def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            # Test with a simple query to verify service is accessible
            # This will work even if tables don't exist yet
            result = self.supabase.auth.get_session()
            logger.info("Supabase connection test successful - Service accessible")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False

    # User operations
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            response = self.supabase.table("users").select("*").eq("email", email).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user data"""
        try:
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("users").update(user_data).eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching user by ID: {e}")
            return None

    # Salary entry operations
    async def create_salary_entry(self, salary_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create salary entry"""
        try:
            salary_data['created_at'] = datetime.utcnow().isoformat()
            salary_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("salary_entries").insert(salary_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating salary entry: {e}")
            return None

    async def get_salary_entries_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all salary entries for a user"""
        try:
            response = self.supabase.table("salary_entries").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting salary entries: {e}")
            return []

    # Raise request operations
    async def create_raise_request(self, raise_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create raise request"""
        try:
            raise_data['created_at'] = datetime.utcnow().isoformat()
            raise_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("raise_requests").insert(raise_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating raise request: {e}")
            return None

    async def get_raise_requests_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all raise requests for a user"""
        try:
            response = self.supabase.table("raise_requests").select("*").eq("user_id", user_id).execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting raise requests: {e}")
            return []

    # CPI data operations
    async def store_cpi_data(self, cpi_data: List[Dict[str, Any]]) -> bool:
        """Store CPI data"""
        try:
            for entry in cpi_data:
                entry['created_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("cpi_data").upsert(cpi_data).execute()
            return True
        except Exception as e:
            logger.error(f"Error storing CPI data: {e}")
            return False

    async def get_cpi_data(self, start_year: int, end_year: int) -> List[Dict[str, Any]]:
        """Get CPI data for date range"""
        try:
            response = (self.supabase.table("cpi_data")
                       .select("*")
                       .gte("year", start_year)
                       .lte("year", end_year)
                       .order("year", desc=False)
                       .order("month", desc=False)
                       .execute())
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting CPI data: {e}")
            return []

    # Benchmark operations
    async def store_benchmark_data(self, benchmark_data: List[Dict[str, Any]]) -> bool:
        """Store benchmark data"""
        try:
            for entry in benchmark_data:
                entry['created_at'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table("benchmarks").upsert(benchmark_data).execute()
            return True
        except Exception as e:
            logger.error(f"Error storing benchmark data: {e}")
            return False

    async def get_benchmark_data(self, job_title: str, location: str) -> List[Dict[str, Any]]:
        """Get benchmark data for job and location"""
        try:
            response = (self.supabase.table("benchmarks")
                       .select("*")
                       .ilike("job_title", f"%{job_title}%")
                       .ilike("location", f"%{location}%")
                       .order("created_at", desc=True)
                       .execute())
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting benchmark data: {e}")
            return []

    # Legacy methods for compatibility
    async def get_user_salary_entries(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all salary entries for a user (legacy method)"""
        return await self.get_salary_entries_by_user(user_id)

    async def get_user_raise_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all raise requests for a user (legacy method)"""
        return await self.get_raise_requests_by_user(user_id)

    async def get_latest_cpi_data(self, limit: int = 12) -> List[Dict[str, Any]]:
        """Get latest CPI data"""
        try:
            result = self.supabase.table('cpi_data').select('*').order('year', desc=True).order('month', desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching CPI data: {e}")
            return []

    async def store_benchmark_data_single(self, benchmark_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store single benchmark data entry (legacy method)"""
        try:
            benchmark_data['created_at'] = datetime.utcnow().isoformat()
            benchmark_data['updated_at'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table('benchmarks').insert(benchmark_data).execute()
            logger.info(f"Benchmark data stored for: {benchmark_data.get('job_title')}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error storing benchmark data: {e}")
            return None

    async def get_benchmark_data_single(self, job_title: str, location: str) -> Optional[Dict[str, Any]]:
        """Get single benchmark data entry (legacy method)"""
        try:
            result = self.supabase.table('benchmarks').select('*').eq('job_title', job_title).eq('location', location).order('created_at', desc=True).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching benchmark data: {e}")
            return None

    async def store_cpi_data_single(self, cpi_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store single CPI data entry (legacy method)"""
        try:
            cpi_data['created_at'] = datetime.utcnow().isoformat()
            
            result = self.supabase.table('cpi_data').insert(cpi_data).execute()
            logger.info(f"CPI data stored for period: {cpi_data.get('period')}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error storing CPI data: {e}")
            return None

# Global instance
supabase_service = SupabaseService() 