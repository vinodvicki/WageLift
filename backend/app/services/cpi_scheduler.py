"""
CPI Data Scheduler for WageLift application.

This module handles scheduled fetching and updating of CPI data from the BLS API.
It provides both APScheduler-based background scheduling and manual execution capabilities.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

from app.core.config import settings
from app.services.bls_service import bls_service, BLSAPIError
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class CPIScheduler:
    """Scheduler for automated CPI data collection and management."""
    
    def __init__(self):
        """Initialize the CPI scheduler."""
        self.scheduler: Optional[BackgroundScheduler] = None
        self.is_running = False
        
        # Job store configuration (stores jobs in database)
        jobstores = {
            'default': SQLAlchemyJobStore(url=str(settings.SQLALCHEMY_DATABASE_URI))
        }
        
        # Executor configuration
        executors = {
            'default': ThreadPoolExecutor(10),
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_executed_listener, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error_listener, EVENT_JOB_ERROR)
    
    def start(self) -> bool:
        """
        Start the scheduler.
        
        Returns:
            True if scheduler started successfully, False otherwise
        """
        try:
            if self.scheduler and not self.is_running:
                self.scheduler.start()
                self.is_running = True
                logger.info("CPI scheduler started successfully")
                
                # Schedule default jobs
                self._schedule_default_jobs()
                
                return True
            else:
                logger.warning("Scheduler already running or not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start CPI scheduler: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        Stop the scheduler.
        
        Returns:
            True if scheduler stopped successfully, False otherwise
        """
        try:
            if self.scheduler and self.is_running:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                logger.info("CPI scheduler stopped successfully")
                return True
            else:
                logger.warning("Scheduler not running or not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Failed to stop CPI scheduler: {str(e)}")
            return False
    
    def _schedule_default_jobs(self):
        """Schedule default CPI data collection jobs."""
        try:
            # Monthly CPI data update - 15th of each month at 10:00 AM UTC
            # BLS typically releases CPI data mid-month
            self.scheduler.add_job(
                func=self._fetch_cpi_data_job,
                trigger=CronTrigger(day=15, hour=10, minute=0),
                id='monthly_cpi_update',
                name='Monthly CPI Data Update',
                replace_existing=True,
                kwargs={'force_refresh': True}
            )
            
            # Weekly data check - every Sunday at 2:00 AM UTC
            # Check for any missed updates or late releases
            self.scheduler.add_job(
                func=self._fetch_cpi_data_job,
                trigger=CronTrigger(day_of_week=6, hour=2, minute=0),
                id='weekly_cpi_check',
                name='Weekly CPI Data Check',
                replace_existing=True,
                kwargs={'force_refresh': False}
            )
            
            # Daily health check - every day at 1:00 AM UTC
            # Check data freshness and system health
            self.scheduler.add_job(
                func=self._health_check_job,
                trigger=CronTrigger(hour=1, minute=0),
                id='daily_health_check',
                name='Daily CPI Data Health Check',
                replace_existing=True
            )
            
            # Monthly cleanup - first day of month at 3:00 AM UTC
            # Clean up old data beyond retention period
            self.scheduler.add_job(
                func=self._cleanup_job,
                trigger=CronTrigger(day=1, hour=3, minute=0),
                id='monthly_cleanup',
                name='Monthly Data Cleanup',
                replace_existing=True
            )
            
            logger.info("Default CPI scheduler jobs configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to schedule default jobs: {str(e)}")
    
    def _fetch_cpi_data_job(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Scheduled job to fetch CPI data.
        
        Args:
            force_refresh: Whether to force data refresh regardless of freshness
            
        Returns:
            Dictionary with job execution results
        """
        job_id = f"cpi_fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting CPI data fetch job: {job_id}")
        
        try:
            # Import here to avoid circular imports
            from app.services.cpi_data_service import cpi_data_service
            
            # Execute the data fetch and store operation
            results = cpi_data_service.fetch_and_store_latest_data(force_refresh=force_refresh)
            
            # Log results
            if results.get('success'):
                logger.info(f"CPI data fetch completed successfully: {results['message']}")
                logger.info(f"New records: {results['new_records']}, Updated: {results['updated_records']}")
            else:
                logger.warning(f"CPI data fetch completed with issues: {results['message']}")
                if results.get('errors'):
                    for error in results['errors']:
                        logger.error(f"  Error: {error}")
            
            return {
                'job_id': job_id,
                'success': results.get('success', False),
                'message': results.get('message', 'Unknown status'),
                'new_records': results.get('new_records', 0),
                'updated_records': results.get('updated_records', 0),
                'total_records': results.get('total_records', 0),
                'latest_date': results.get('latest_date'),
                'errors': results.get('errors', [])
            }
            
        except Exception as e:
            error_msg = f"CPI data fetch job failed: {str(e)}"
            logger.error(error_msg)
            return {
                'job_id': job_id,
                'success': False,
                'message': error_msg,
                'errors': [str(e)]
            }
    
    def _health_check_job(self) -> Dict[str, Any]:
        """
        Scheduled job to check CPI data health and freshness.
        
        Returns:
            Dictionary with health check results
        """
        job_id = f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting CPI data health check: {job_id}")
        
        try:
            # Import here to avoid circular imports
            from app.services.cpi_data_service import cpi_data_service
            
            # Get data freshness status
            freshness_status = cpi_data_service.get_data_freshness_status()
            
            # Check if data needs updating
            if freshness_status.get('needs_update', True):
                logger.warning(f"CPI data is stale - last update: {freshness_status.get('latest_date', 'unknown')}")
                
                # Attempt automatic update if data is very stale
                if freshness_status.get('days_since_latest', 0) > 45:  # More than 45 days old
                    logger.info("Attempting automatic CPI data update due to stale data")
                    update_results = self._fetch_cpi_data_job(force_refresh=True)
                    
                    return {
                        'job_id': job_id,
                        'success': True,
                        'message': 'Health check triggered automatic update',
                        'freshness_status': freshness_status,
                        'update_results': update_results
                    }
            else:
                logger.info(f"CPI data is current - last update: {freshness_status.get('latest_date', 'unknown')}")
            
            return {
                'job_id': job_id,
                'success': True,
                'message': 'Health check completed successfully',
                'freshness_status': freshness_status
            }
            
        except Exception as e:
            error_msg = f"CPI health check job failed: {str(e)}"
            logger.error(error_msg)
            return {
                'job_id': job_id,
                'success': False,
                'message': error_msg,
                'errors': [str(e)]
            }
    
    def _cleanup_job(self) -> Dict[str, Any]:
        """
        Scheduled job to clean up old CPI data.
        
        Returns:
            Dictionary with cleanup results
        """
        job_id = f"cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting CPI data cleanup: {job_id}")
        
        try:
            # Import here to avoid circular imports
            from app.services.cpi_data_service import cpi_data_service
            
            # Clean up data older than 10 years
            cleanup_results = cpi_data_service.cleanup_old_data(keep_years=10)
            
            deleted_count = cleanup_results.get('deleted_count', 0)
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old CPI records")
            else:
                logger.info("No old CPI records found for cleanup")
            
            return {
                'job_id': job_id,
                'success': True,
                'message': f'Cleanup completed - deleted {deleted_count} records',
                'deleted_count': deleted_count,
                'cutoff_year': cleanup_results.get('cutoff_year')
            }
            
        except Exception as e:
            error_msg = f"CPI cleanup job failed: {str(e)}"
            logger.error(error_msg)
            return {
                'job_id': job_id,
                'success': False,
                'message': error_msg,
                'errors': [str(e)]
            }
    
    def _job_executed_listener(self, event):
        """Event listener for successful job execution."""
        logger.info(f"Job {event.job_id} executed successfully")
    
    def _job_error_listener(self, event):
        """Event listener for job execution errors."""
        logger.error(f"Job {event.job_id} failed: {event.exception}")
    
    def execute_manual_fetch(self, force_refresh: bool = True) -> Dict[str, Any]:
        """
        Manually execute CPI data fetch (outside of scheduled jobs).
        
        Args:
            force_refresh: Whether to force data refresh
            
        Returns:
            Dictionary with execution results
        """
        logger.info("Executing manual CPI data fetch")
        return self._fetch_cpi_data_job(force_refresh=force_refresh)
    
    def execute_manual_health_check(self) -> Dict[str, Any]:
        """
        Manually execute health check (outside of scheduled jobs).
        
        Returns:
            Dictionary with health check results
        """
        logger.info("Executing manual CPI health check")
        return self._health_check_job()
    
    def execute_manual_cleanup(self) -> Dict[str, Any]:
        """
        Manually execute cleanup (outside of scheduled jobs).
        
        Returns:
            Dictionary with cleanup results
        """
        logger.info("Executing manual CPI cleanup")
        return self._cleanup_job()
    
    def get_job_status(self) -> Dict[str, Any]:
        """
        Get current status of scheduled jobs.
        
        Returns:
            Dictionary with scheduler and job status information
        """
        if not self.scheduler:
            return {
                'scheduler_running': False,
                'jobs': [],
                'message': 'Scheduler not initialized'
            }
        
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
                'func_name': job.func.__name__ if hasattr(job.func, '__name__') else str(job.func)
            })
        
        return {
            'scheduler_running': self.is_running,
            'jobs': jobs_info,
            'total_jobs': len(jobs_info)
        }
    
    def add_custom_job(
        self, 
        job_id: str, 
        schedule_type: str = 'cron',
        **schedule_kwargs
    ) -> bool:
        """
        Add a custom CPI data fetch job.
        
        Args:
            job_id: Unique identifier for the job
            schedule_type: Type of schedule ('cron' or 'interval')
            **schedule_kwargs: Schedule configuration parameters
            
        Returns:
            True if job added successfully, False otherwise
        """
        try:
            if not self.scheduler or not self.is_running:
                logger.error("Scheduler not running")
                return False
            
            if schedule_type == 'cron':
                trigger = CronTrigger(**schedule_kwargs)
            elif schedule_type == 'interval':
                trigger = IntervalTrigger(**schedule_kwargs)
            else:
                logger.error(f"Unsupported schedule type: {schedule_type}")
                return False
            
            self.scheduler.add_job(
                func=self._fetch_cpi_data_job,
                trigger=trigger,
                id=job_id,
                name=f'Custom CPI Job: {job_id}',
                replace_existing=True,
                kwargs={'force_refresh': False}
            )
            
            logger.info(f"Custom job '{job_id}' added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add custom job '{job_id}': {str(e)}")
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.
        
        Args:
            job_id: Identifier of the job to remove
            
        Returns:
            True if job removed successfully, False otherwise
        """
        try:
            if not self.scheduler or not self.is_running:
                logger.error("Scheduler not running")
                return False
            
            self.scheduler.remove_job(job_id)
            logger.info(f"Job '{job_id}' removed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove job '{job_id}': {str(e)}")
            return False


# Global scheduler instance
cpi_scheduler = CPIScheduler()


@asynccontextmanager
async def scheduler_lifespan():
    """
    Context manager for scheduler lifecycle management.
    Use this in FastAPI lifespan events.
    """
    try:
        # Start scheduler
        success = cpi_scheduler.start()
        if success:
            logger.info("CPI scheduler started during application startup")
        else:
            logger.error("Failed to start CPI scheduler during application startup")
        
        yield
        
    finally:
        # Stop scheduler
        success = cpi_scheduler.stop()
        if success:
            logger.info("CPI scheduler stopped during application shutdown")
        else:
            logger.error("Failed to stop CPI scheduler during application shutdown")


def get_scheduler() -> CPIScheduler:
    """Get the global CPI scheduler instance."""
    return cpi_scheduler 