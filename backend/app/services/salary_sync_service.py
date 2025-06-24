"""
Salary synchronization service.

Handles syncing salary data between Gusto and WageLift's SalaryEntry model.
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.salary_entry import SalaryEntry
from app.services.gusto_service import GustoService, GustoAPIError, get_gusto_service


class SalarySyncService:
    """
    Service for synchronizing salary data between Gusto and WageLift.
    
    Converts Gusto compensation data into SalaryEntry records.
    """
    
    def __init__(self, gusto_service: GustoService = None):
        self.gusto_service = gusto_service or get_gusto_service()
    
    def _parse_gusto_date(self, date_str: Optional[str]) -> Optional[date]:
        """
        Parse Gusto date string into Python date object.
        
        Args:
            date_str: Date string from Gusto API
            
        Returns:
            Parsed date or None
        """
        if not date_str:
            return None
        
        try:
            # Gusto typically uses ISO format: YYYY-MM-DD
            return datetime.fromisoformat(date_str.replace('Z', '')).date()
        except (ValueError, AttributeError):
            return None
    
    def _convert_compensation_to_salary_entry(
        self, 
        user: User, 
        compensation: Dict,
        company_name: Optional[str] = None
    ) -> Optional[SalaryEntry]:
        """
        Convert a Gusto compensation record to a SalaryEntry.
        
        Args:
            user: User object
            compensation: Compensation data from Gusto
            company_name: Company name from Gusto
            
        Returns:
            SalaryEntry object or None if conversion fails
        """
        try:
            # Extract compensation details
            amount = compensation.get("amount")
            if not amount:
                return None
            
            # Convert amount to Decimal
            try:
                salary_amount = Decimal(str(amount))
            except (ValueError, TypeError):
                return None
            
            # Determine pay frequency
            pay_frequency = compensation.get("payment_unit", "yearly").lower()
            if pay_frequency in ["per_year", "annually", "annual"]:
                pay_frequency = "yearly"
            elif pay_frequency in ["per_month", "monthly"]:
                pay_frequency = "monthly"
            elif pay_frequency in ["per_week", "weekly"]:
                pay_frequency = "weekly"
            elif pay_frequency in ["per_hour", "hourly"]:
                pay_frequency = "hourly"
            else:
                pay_frequency = "yearly"  # Default
            
            # Get effective date
            effective_date = self._parse_gusto_date(
                compensation.get("effective_date")
            ) or date.today()
            
            # Create SalaryEntry
            salary_entry = SalaryEntry(
                user_id=user.id,
                amount=salary_amount,
                frequency=pay_frequency,
                effective_date=effective_date,
                company=company_name or user.company or "Unknown Company",
                job_title=compensation.get("job_title") or user.job_title or "Unknown Title",
                location=user.location or "Unknown Location",
                source="gusto",
                is_verified=True,  # Data from Gusto is considered verified
                notes=f"Synced from Gusto on {datetime.utcnow().isoformat()}"
            )
            
            return salary_entry
            
        except Exception as e:
            # Log error but don't fail the entire sync
            print(f"Error converting compensation to salary entry: {e}")
            return None
    
    async def sync_user_salary_data(
        self, 
        db: Session, 
        user: User,
        overwrite_existing: bool = False
    ) -> Dict:
        """
        Sync salary data from Gusto for a specific user.
        
        Args:
            db: Database session
            user: User object
            overwrite_existing: Whether to overwrite existing salary entries
            
        Returns:
            Sync result summary
        """
        try:
            # Get salary data from Gusto
            sync_result = await self.gusto_service.sync_salary_data(db, user)
            
            if not sync_result.get("success"):
                return {
                    "success": False,
                    "message": sync_result.get("message", "Failed to sync from Gusto"),
                    "error": sync_result.get("error"),
                    "entries_created": 0,
                    "entries_updated": 0
                }
            
            # Extract data from sync result
            company = sync_result.get("company", {})
            employee = sync_result.get("employee", {})
            compensations = sync_result.get("compensations", [])
            
            company_name = company.get("name")
            
            # Track sync statistics
            entries_created = 0
            entries_updated = 0
            entries_skipped = 0
            
            # Process each compensation record
            for compensation in compensations:
                salary_entry = self._convert_compensation_to_salary_entry(
                    user, compensation, company_name
                )
                
                if not salary_entry:
                    entries_skipped += 1
                    continue
                
                # Check if similar entry exists
                existing_entry = db.query(SalaryEntry).filter(
                    SalaryEntry.user_id == user.id,
                    SalaryEntry.effective_date == salary_entry.effective_date,
                    SalaryEntry.source == "gusto"
                ).first()
                
                if existing_entry:
                    if overwrite_existing:
                        # Update existing entry
                        existing_entry.amount = salary_entry.amount
                        existing_entry.frequency = salary_entry.frequency
                        existing_entry.company = salary_entry.company
                        existing_entry.job_title = salary_entry.job_title
                        existing_entry.location = salary_entry.location
                        existing_entry.notes = salary_entry.notes
                        existing_entry.updated_at = datetime.utcnow()
                        entries_updated += 1
                    else:
                        entries_skipped += 1
                else:
                    # Create new entry
                    db.add(salary_entry)
                    entries_created += 1
            
            # Commit changes
            db.commit()
            
            return {
                "success": True,
                "message": f"Successfully synced salary data from Gusto",
                "company_name": company_name,
                "employee_name": f"{employee.get('first_name', '')} {employee.get('last_name', '')}".strip(),
                "total_compensations": len(compensations),
                "entries_created": entries_created,
                "entries_updated": entries_updated,
                "entries_skipped": entries_skipped,
                "sync_timestamp": datetime.utcnow().isoformat()
            }
            
        except GustoAPIError as e:
            return {
                "success": False,
                "message": f"Gusto API error: {e.message}",
                "error": e.message,
                "entries_created": 0,
                "entries_updated": 0
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Sync failed: {str(e)}",
                "error": str(e),
                "entries_created": 0,
                "entries_updated": 0
            }
    
    async def get_sync_status(self, db: Session, user: User) -> Dict:
        """
        Get the current sync status for a user.
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Sync status information
        """
        try:
            # Check if user has Gusto connection
            token_record = self.gusto_service.get_active_token(db, user)
            if not token_record:
                return {
                    "connected": False,
                    "message": "No Gusto connection found"
                }
            
            # Get salary entries from Gusto
            gusto_entries = db.query(SalaryEntry).filter(
                SalaryEntry.user_id == user.id,
                SalaryEntry.source == "gusto"
            ).order_by(SalaryEntry.effective_date.desc()).all()
            
            # Get latest sync time
            latest_sync = None
            if gusto_entries:
                latest_sync = max(entry.created_at for entry in gusto_entries)
            
            return {
                "connected": True,
                "company_id": token_record.gusto_company_id,
                "employee_id": token_record.gusto_employee_id,
                "total_entries": len(gusto_entries),
                "latest_sync": latest_sync.isoformat() if latest_sync else None,
                "last_token_use": token_record.last_used_at.isoformat() if token_record.last_used_at else None,
                "token_expires": token_record.expires_at.isoformat()
            }
            
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "message": f"Failed to get sync status: {str(e)}"
            }


# Create global service instance
salary_sync_service = SalarySyncService()


def get_salary_sync_service() -> SalarySyncService:
    """Get salary sync service instance (dependency injection)."""
    return salary_sync_service
