"""
Enhanced Structured Logging for WageLift
Provides comprehensive logging with correlation IDs, user context, and metrics integration
"""

import sys
import uuid
import time
import logging
import structlog
from typing import Dict, Any, Optional
from contextvars import ContextVar
from datetime import datetime

# Context variables for request correlation
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_id: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
request_start_time: ContextVar[Optional[float]] = ContextVar('request_start_time', default=None)

class CorrelationIDProcessor:
    """Add correlation IDs to log entries"""
    
    def __call__(self, logger, method_name, event_dict):
        correlation = correlation_id.get()
        if correlation:
            event_dict['correlation_id'] = correlation
        return event_dict

class UserContextProcessor:
    """Add user context to log entries"""
    
    def __call__(self, logger, method_name, event_dict):
        user = user_id.get()
        if user:
            event_dict['user_id'] = user
        return event_dict

class RequestTimingProcessor:
    """Add request timing information to log entries"""
    
    def __call__(self, logger, method_name, event_dict):
        start_time = request_start_time.get()
        if start_time:
            event_dict['request_duration'] = time.time() - start_time
        return event_dict

class PerformanceProcessor:
    """Add performance metrics to log entries"""
    
    def __call__(self, logger, method_name, event_dict):
        # Add timestamp in ISO format
        event_dict['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add log level for easier filtering
        if 'level' not in event_dict:
            event_dict['level'] = method_name.upper()
        
        # Add service information
        event_dict['service'] = 'wagelift-backend'
        event_dict['component'] = event_dict.get('component', 'unknown')
        
        return event_dict

def setup_structured_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging with enhanced processors
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Configure structlog processors
    processors = [
        # Context processors
        CorrelationIDProcessor(),
        UserContextProcessor(),
        RequestTimingProcessor(),
        PerformanceProcessor(),
        
        # Built-in processors
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        
        # Final JSON rendering
        structlog.processors.JSONRenderer()
    ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str, component: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a structured logger with optional component context
    
    Args:
        name: Logger name (usually __name__)
        component: Component name for better log organization
        
    Returns:
        Configured structlog logger
    """
    logger = structlog.get_logger(name)
    
    if component:
        logger = logger.bind(component=component)
    
    return logger

# Context managers for request correlation
class RequestContext:
    """Context manager for request-scoped logging context"""
    
    def __init__(self, correlation: Optional[str] = None, user: Optional[str] = None):
        self.correlation = correlation or str(uuid.uuid4())
        self.user = user
        self.start_time = time.time()
        
        # Store previous values
        self.prev_correlation = None
        self.prev_user = None
        self.prev_start_time = None
    
    def __enter__(self):
        # Store previous values
        self.prev_correlation = correlation_id.get()
        self.prev_user = user_id.get()
        self.prev_start_time = request_start_time.get()
        
        # Set new values
        correlation_id.set(self.correlation)
        if self.user:
            user_id.set(self.user)
        request_start_time.set(self.start_time)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous values
        correlation_id.set(self.prev_correlation)
        user_id.set(self.prev_user)
        request_start_time.set(self.prev_start_time)

# Utility functions
def set_user_context(user: str) -> None:
    """Set user context for current request"""
    user_id.set(user)

def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id.get()

def log_auth_event(
    logger: structlog.BoundLogger,
    event: str,
    success: bool,
    user: Optional[str] = None,
    duration: Optional[float] = None,
    **kwargs
) -> None:
    """
    Log authentication events with standardized format
    
    Args:
        logger: Structured logger instance
        event: Event type (e.g., 'login', 'token_validation')
        success: Whether the event was successful
        user: User ID
        duration: Event duration in seconds
        **kwargs: Additional context
    """
    log_data = {
        'event_type': 'auth',
        'auth_event': event,
        'success': success,
        **kwargs
    }
    
    if user:
        log_data['user_id'] = user
    
    if duration:
        log_data['duration'] = duration
    
    if success:
        logger.info("Authentication event", **log_data)
    else:
        logger.warning("Authentication failed", **log_data)

def log_database_event(
    logger: structlog.BoundLogger,
    operation: str,
    table: str,
    success: bool,
    duration: Optional[float] = None,
    rows_affected: Optional[int] = None,
    **kwargs
) -> None:
    """
    Log database events with standardized format
    
    Args:
        logger: Structured logger instance
        operation: Database operation (SELECT, INSERT, UPDATE, DELETE)
        table: Table name
        success: Whether the operation was successful
        duration: Operation duration in seconds
        rows_affected: Number of rows affected
        **kwargs: Additional context
    """
    log_data = {
        'event_type': 'database',
        'db_operation': operation.upper(),
        'db_table': table,
        'success': success,
        **kwargs
    }
    
    if duration:
        log_data['duration'] = duration
    
    if rows_affected is not None:
        log_data['rows_affected'] = rows_affected
    
    if success:
        logger.info("Database operation", **log_data)
    else:
        logger.error("Database operation failed", **log_data)

def log_api_event(
    logger: structlog.BoundLogger,
    method: str,
    endpoint: str,
    status_code: int,
    duration: Optional[float] = None,
    user: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log API events with standardized format
    
    Args:
        logger: Structured logger instance
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration: Request duration in seconds
        user: User ID
        **kwargs: Additional context
    """
    log_data = {
        'event_type': 'api',
        'http_method': method.upper(),
        'endpoint': endpoint,
        'status_code': status_code,
        'success': 200 <= status_code < 400,
        **kwargs
    }
    
    if duration:
        log_data['duration'] = duration
    
    if user:
        log_data['user_id'] = user
    
    if 200 <= status_code < 400:
        logger.info("API request", **log_data)
    elif 400 <= status_code < 500:
        logger.warning("Client error", **log_data)
    else:
        logger.error("Server error", **log_data)

# Business event logging
def log_business_event(
    logger: structlog.BoundLogger,
    event: str,
    user: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log business events with standardized format
    
    Args:
        logger: Structured logger instance
        event: Business event name
        user: User ID
        **kwargs: Additional context
    """
    log_data = {
        'event_type': 'business',
        'business_event': event,
        **kwargs
    }
    
    if user:
        log_data['user_id'] = user
    
    logger.info("Business event", **log_data)

# Initialize logging on module import
setup_structured_logging()

# Export the main logger function
__all__ = [
    'setup_structured_logging',
    'get_logger',
    'RequestContext',
    'set_user_context',
    'get_correlation_id',
    'log_auth_event',
    'log_database_event',
    'log_api_event',
    'log_business_event'
] 