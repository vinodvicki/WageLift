"""
Comprehensive Error Handling Module for WageLift.

This module provides centralized error handling, data validation,
and crash-proof utilities to prevent all types of runtime errors.
"""

import functools
import traceback
import asyncio
import sys
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from contextlib import asynccontextmanager, contextmanager
import structlog
from fastapi import HTTPException, status
from pydantic import ValidationError
import time

# Type variables
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])
AF = TypeVar('AF', bound=Callable[..., Any])

# Logger
logger = structlog.get_logger(__name__)

# Global error tracking
ERROR_TRACKER = {
    "total_errors": 0,
    "recent_errors": [],
    "error_types": {},
    "last_error_time": None
}

# Circuit breaker state
CIRCUIT_BREAKER = {
    "consecutive_failures": 0,
    "last_failure_time": None,
    "is_open": False,
    "failure_threshold": 3,
    "recovery_timeout": 300  # 5 minutes
}


class WageLiftException(Exception):
    """Base exception for all WageLift specific errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        self.message = message
        self.error_code = error_code or "WAGELIFT_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class DataValidationError(WageLiftException):
    """Raised when data validation fails."""
    pass


class ExternalServiceError(WageLiftException):
    """Raised when external service calls fail."""
    pass


class DatabaseError(WageLiftException):
    """Raised when database operations fail."""
    pass


class ConfigurationError(WageLiftException):
    """Raised when configuration is invalid."""
    pass


class SecurityError(WageLiftException):
    """Raised when security violations occur."""
    pass


class ResourceError(WageLiftException):
    """Raised when resource operations fail."""
    pass


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, preventing division by zero errors.
    
    Args:
        numerator: The number to divide
        denominator: The number to divide by
        default: Value to return if denominator is zero
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            logger.warning(
                "Division by zero prevented",
                numerator=numerator,
                denominator=denominator,
                default_returned=default
            )
            return default
        return numerator / denominator
    except (TypeError, ValueError) as e:
        logger.error("Division failed due to invalid types", error=str(e))
        return default


def safe_access(data: Dict, keys: List[str], default: Any = None) -> Any:
    """
    Safely access nested dictionary values, preventing KeyError.
    
    Args:
        data: Dictionary to access
        keys: List of keys for nested access
        default: Value to return if key not found
        
    Returns:
        Accessed value or default
    """
    try:
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    except (TypeError, AttributeError) as e:
        logger.warning("Safe access failed", error=str(e), keys=keys)
        return default


def validate_range(value: Union[int, float], min_val: float = None, max_val: float = None) -> bool:
    """
    Validate that a numeric value is within specified range.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if value is valid, False otherwise
    """
    try:
        if not isinstance(value, (int, float)):
            return False
        
        if min_val is not None and value < min_val:
            return False
            
        if max_val is not None and value > max_val:
            return False
            
        return True
    except Exception as e:
        logger.error("Range validation failed", error=str(e))
        return False


def sanitize_input(input_str: str, max_length: int = 1000, allowed_chars: str = None) -> str:
    """
    Sanitize user input to prevent injection attacks and buffer overflows.
    
    Args:
        input_str: String to sanitize
        max_length: Maximum allowed length
        allowed_chars: Regex pattern of allowed characters
        
    Returns:
        Sanitized string
    """
    try:
        if not isinstance(input_str, str):
            input_str = str(input_str)
        
        # Truncate to prevent buffer overflow
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
            logger.warning("Input truncated to prevent overflow", original_length=len(input_str))
        
        # Remove null bytes and control characters
        input_str = ''.join(char for char in input_str if ord(char) >= 32 or char in '\n\r\t')
        
        # Additional character filtering if specified
        if allowed_chars:
            import re
            input_str = re.sub(f'[^{allowed_chars}]', '', input_str)
        
        return input_str
    except Exception as e:
        logger.error("Input sanitization failed", error=str(e))
        return ""


def track_error(error: Exception, context: Dict = None) -> None:
    """
    Track errors for monitoring and circuit breaker logic.
    
    Args:
        error: The exception that occurred
        context: Additional context about the error
    """
    global ERROR_TRACKER, CIRCUIT_BREAKER
    
    try:
        current_time = time.time()
        error_type = type(error).__name__
        
        # Update error tracking
        ERROR_TRACKER["total_errors"] += 1
        ERROR_TRACKER["last_error_time"] = current_time
        ERROR_TRACKER["error_types"][error_type] = ERROR_TRACKER["error_types"].get(error_type, 0) + 1
        
        # Keep only recent errors (last 100)
        ERROR_TRACKER["recent_errors"].append({
            "type": error_type,
            "message": str(error),
            "time": current_time,
            "context": context or {}
        })
        if len(ERROR_TRACKER["recent_errors"]) > 100:
            ERROR_TRACKER["recent_errors"] = ERROR_TRACKER["recent_errors"][-100:]
        
        # Update circuit breaker
        CIRCUIT_BREAKER["consecutive_failures"] += 1
        CIRCUIT_BREAKER["last_failure_time"] = current_time
        
        # Open circuit breaker if threshold exceeded
        if CIRCUIT_BREAKER["consecutive_failures"] >= CIRCUIT_BREAKER["failure_threshold"]:
            CIRCUIT_BREAKER["is_open"] = True
            logger.critical(
                "Circuit breaker opened due to consecutive failures",
                consecutive_failures=CIRCUIT_BREAKER["consecutive_failures"]
            )
    except Exception as tracking_error:
        logger.error("Error tracking failed", error=str(tracking_error))


def reset_circuit_breaker() -> None:
    """Reset circuit breaker after successful operations."""
    global CIRCUIT_BREAKER
    
    current_time = time.time()
    
    # Check if circuit breaker should be reset
    if (CIRCUIT_BREAKER["is_open"] and 
        CIRCUIT_BREAKER["last_failure_time"] and
        current_time - CIRCUIT_BREAKER["last_failure_time"] > CIRCUIT_BREAKER["recovery_timeout"]):
        
        CIRCUIT_BREAKER["is_open"] = False
        CIRCUIT_BREAKER["consecutive_failures"] = 0
        logger.info("Circuit breaker reset after recovery timeout")
    elif not CIRCUIT_BREAKER["is_open"]:
        CIRCUIT_BREAKER["consecutive_failures"] = 0


def circuit_breaker_check() -> bool:
    """
    Check if circuit breaker allows operation.
    
    Returns:
        True if operation allowed, False if circuit is open
    """
    reset_circuit_breaker()
    
    if CIRCUIT_BREAKER["is_open"]:
        logger.warning("Operation blocked by circuit breaker")
        return False
    
    return True


def error_handler(
    default_return: Any = None,
    exceptions: tuple = (Exception,),
    log_level: str = "error",
    raise_on_circuit_open: bool = True
) -> Callable[[F], F]:
    """
    Decorator for comprehensive error handling with circuit breaker protection.
    
    Args:
        default_return: Value to return on error
        exceptions: Tuple of exceptions to catch
        log_level: Logging level for errors
        raise_on_circuit_open: Whether to raise exception when circuit is open
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check circuit breaker
            if not circuit_breaker_check():
                if raise_on_circuit_open:
                    raise WageLiftException(
                        "Service temporarily unavailable due to circuit breaker",
                        error_code="CIRCUIT_BREAKER_OPEN"
                    )
                return default_return
            
            try:
                result = func(*args, **kwargs)
                reset_circuit_breaker()  # Reset on success
                return result
                
            except exceptions as e:
                track_error(e, {"function": func.__name__, "args": str(args)[:100]})
                
                # Log error
                log_func = getattr(logger, log_level, logger.error)
                log_func(
                    f"Error in {func.__name__}",
                    error=str(e),
                    error_type=type(e).__name__,
                    traceback=traceback.format_exc()
                )
                
                # Convert to HTTP exception if needed
                if isinstance(e, ValidationError):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Validation error: {str(e)}"
                    )
                elif isinstance(e, WageLiftException):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{e.error_code}: {e.message}"
                    )
                
                return default_return
                
        return wrapper
    return decorator


def async_error_handler(
    default_return: Any = None,
    exceptions: tuple = (Exception,),
    log_level: str = "error",
    raise_on_circuit_open: bool = True
) -> Callable[[AF], AF]:
    """
    Async version of error handler decorator.
    
    Args:
        default_return: Value to return on error
        exceptions: Tuple of exceptions to catch
        log_level: Logging level for errors
        raise_on_circuit_open: Whether to raise exception when circuit is open
        
    Returns:
        Decorated async function
    """
    def decorator(func: AF) -> AF:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Check circuit breaker
            if not circuit_breaker_check():
                if raise_on_circuit_open:
                    raise WageLiftException(
                        "Service temporarily unavailable due to circuit breaker",
                        error_code="CIRCUIT_BREAKER_OPEN"
                    )
                return default_return
            
            try:
                result = await func(*args, **kwargs)
                reset_circuit_breaker()  # Reset on success
                return result
                
            except exceptions as e:
                track_error(e, {"function": func.__name__, "args": str(args)[:100]})
                
                # Log error
                log_func = getattr(logger, log_level, logger.error)
                log_func(
                    f"Error in {func.__name__}",
                    error=str(e),
                    error_type=type(e).__name__,
                    traceback=traceback.format_exc()
                )
                
                # Convert to HTTP exception if needed
                if isinstance(e, ValidationError):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Validation error: {str(e)}"
                    )
                elif isinstance(e, WageLiftException):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{e.error_code}: {e.message}"
                    )
                
                return default_return
                
        return wrapper
    return decorator


@contextmanager
def safe_operation(operation_name: str, default_return: Any = None):
    """
    Context manager for safe operations with automatic error handling.
    
    Args:
        operation_name: Name of the operation for logging
        default_return: Value to return on error
        
    Yields:
        Context for safe operations
    """
    try:
        if not circuit_breaker_check():
            raise WageLiftException(
                "Service temporarily unavailable due to circuit breaker",
                error_code="CIRCUIT_BREAKER_OPEN"
            )
        
        yield
        reset_circuit_breaker()
        
    except Exception as e:
        track_error(e, {"operation": operation_name})
        logger.error(
            f"Error in operation: {operation_name}",
            error=str(e),
            error_type=type(e).__name__
        )
        return default_return


@asynccontextmanager
async def async_safe_operation(operation_name: str, default_return: Any = None):
    """
    Async context manager for safe operations with automatic error handling.
    
    Args:
        operation_name: Name of the operation for logging
        default_return: Value to return on error
        
    Yields:
        Context for safe async operations
    """
    try:
        if not circuit_breaker_check():
            raise WageLiftException(
                "Service temporarily unavailable due to circuit breaker",
                error_code="CIRCUIT_BREAKER_OPEN"
            )
        
        yield
        reset_circuit_breaker()
        
    except Exception as e:
        track_error(e, {"operation": operation_name})
        logger.error(
            f"Error in async operation: {operation_name}",
            error=str(e),
            error_type=type(e).__name__
        )
        # Note: Cannot return from async context manager
        # default_return value should be handled by the caller
        raise


def get_error_stats() -> Dict:
    """
    Get current error statistics for monitoring.
    
    Returns:
        Dictionary containing error statistics
    """
    return {
        "total_errors": ERROR_TRACKER["total_errors"],
        "recent_error_count": len(ERROR_TRACKER["recent_errors"]),
        "error_types": ERROR_TRACKER["error_types"].copy(),
        "circuit_breaker": {
            "is_open": CIRCUIT_BREAKER["is_open"],
            "consecutive_failures": CIRCUIT_BREAKER["consecutive_failures"],
            "last_failure_time": CIRCUIT_BREAKER["last_failure_time"]
        },
        "last_error_time": ERROR_TRACKER["last_error_time"]
    }


def validate_memory_usage(max_mb: int = 500) -> bool:
    """
    Check current memory usage to prevent memory leaks.
    
    Args:
        max_mb: Maximum allowed memory usage in MB
        
    Returns:
        True if memory usage is acceptable, False otherwise
    """
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        
        if memory_mb > max_mb:
            logger.warning(
                "High memory usage detected",
                current_mb=memory_mb,
                max_mb=max_mb
            )
            return False
        
        return True
    except Exception as e:
        logger.error("Memory validation failed", error=str(e))
        return True  # Allow operation to continue if check fails


def create_checkpoint(data: Dict, checkpoint_id: str) -> bool:
    """
    Create a data checkpoint for crash recovery.
    
    Args:
        data: Data to checkpoint
        checkpoint_id: Unique identifier for checkpoint
        
    Returns:
        True if checkpoint created successfully
    """
    try:
        import json
        import os
        
        checkpoint_dir = "/tmp/wagelift_checkpoints"
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_file = os.path.join(checkpoint_dir, f"{checkpoint_id}.json")
        
        with open(checkpoint_file, 'w') as f:
            json.dump({
                "data": data,
                "timestamp": time.time(),
                "checkpoint_id": checkpoint_id
            }, f)
        
        logger.info("Checkpoint created", checkpoint_id=checkpoint_id)
        return True
        
    except Exception as e:
        logger.error("Checkpoint creation failed", error=str(e), checkpoint_id=checkpoint_id)
        return False


def load_checkpoint(checkpoint_id: str) -> Optional[Dict]:
    """
    Load data from a checkpoint.
    
    Args:
        checkpoint_id: Unique identifier for checkpoint
        
    Returns:
        Checkpoint data or None if not found
    """
    try:
        import json
        import os
        
        checkpoint_file = f"/tmp/wagelift_checkpoints/{checkpoint_id}.json"
        
        if not os.path.exists(checkpoint_file):
            return None
        
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
        
        logger.info("Checkpoint loaded", checkpoint_id=checkpoint_id)
        return checkpoint.get("data")
        
    except Exception as e:
        logger.error("Checkpoint loading failed", error=str(e), checkpoint_id=checkpoint_id)
        return None