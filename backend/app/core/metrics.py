"""
WageLift Performance Metrics Module

This module provides comprehensive Prometheus metrics for monitoring:
- Auth0 authentication performance
- Supabase database operations  
- System-level performance indicators
- Business metrics and KPIs
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from functools import wraps
from typing import Callable, Any, Dict, Optional

# ============================================================================
# AUTH0 METRICS
# ============================================================================

# Authentication metrics
AUTH_REQUESTS_TOTAL = Counter(
    'auth_requests_total',
    'Total authentication requests',
    ['method', 'status']
)

AUTH_SUCCESS_TOTAL = Counter(
    'auth_success_total',
    'Successful authentications',
    ['user_type']
)

AUTH_FAILURE_TOTAL = Counter(
    'auth_failure_total', 
    'Failed authentications',
    ['reason', 'method']
)

AUTH_LATENCY = Histogram(
    'auth_latency_seconds',
    'Authentication latency in seconds',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# JWT Token metrics
JWT_VALIDATION_DURATION = Histogram(
    'jwt_validation_duration_seconds',
    'JWT validation duration',
    ['validation_type'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5]
)

JWT_CACHE_HITS = Counter(
    'jwt_cache_hits_total',
    'JWT cache hits',
    ['cache_type']
)

JWT_CACHE_MISSES = Counter(
    'jwt_cache_misses_total',
    'JWT cache misses',
    ['cache_type']
)

# Auth0 API metrics
AUTH0_API_CALLS = Counter(
    'auth0_api_calls_total',
    'Auth0 API calls',
    ['endpoint', 'status']
)

AUTH0_API_LATENCY = Histogram(
    'auth0_api_latency_seconds',
    'Auth0 API call latency',
    ['endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

# ============================================================================
# SUPABASE METRICS
# ============================================================================

# Database operation metrics
SUPABASE_QUERY_DURATION = Histogram(
    'supabase_query_duration_seconds',
    'Supabase query duration',
    ['operation', 'table'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

SUPABASE_OPERATIONS_TOTAL = Counter(
    'supabase_operations_total',
    'Total Supabase operations',
    ['operation', 'table', 'status']
)

SUPABASE_ERRORS_TOTAL = Counter(
    'supabase_errors_total',
    'Supabase operation errors',
    ['operation', 'table', 'error_code']
)

SUPABASE_CONNECTIONS = Gauge(
    'supabase_connections',
    'Supabase connection pool metrics',
    ['state']  # 'active', 'idle', 'total'
)

SUPABASE_RLS_POLICY_TIME = Histogram(
    'supabase_rls_policy_duration_seconds',
    'Row Level Security policy evaluation time',
    ['table', 'policy'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1]
)

# ============================================================================
# SYSTEM METRICS
# ============================================================================

# HTTP request metrics (extending existing)
HTTP_REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000]
)

HTTP_RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=[100, 1000, 10000, 100000, 1000000]
)

# Cache metrics
CACHE_OPERATIONS = Counter(
    'cache_operations_total',
    'Cache operations',
    ['operation', 'cache_type', 'status']
)

CACHE_HIT_RATIO = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio by cache type',
    ['cache_type']
)

# Memory and resource metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['type']  # 'heap', 'rss', 'external'
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections_total',
    'Active connections',
    ['type']  # 'http', 'websocket', 'database'
)

# ============================================================================
# BUSINESS METRICS
# ============================================================================

# User activity metrics
USER_SESSIONS = Counter(
    'user_sessions_total',
    'User sessions',
    ['session_type']  # 'new', 'returning'
)

USER_ACTIONS = Counter(
    'user_actions_total',
    'User actions',
    ['action_type']  # 'salary_entry', 'raise_request', 'benchmark_view'
)

SALARY_CALCULATIONS = Counter(
    'salary_calculations_total',
    'Salary calculations performed',
    ['calculation_type']  # 'inflation', 'benchmark', 'raise_request'
)

RAISE_REQUESTS = Counter(
    'raise_requests_total',
    'Raise requests',
    ['status']  # 'created', 'submitted', 'approved', 'rejected'
)

# ============================================================================
# DECORATORS FOR AUTOMATIC METRICS
# ============================================================================

def track_api_operation(operation: str):
    """Decorator to track general API operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                
                # Track successful operation
                AUTH_REQUESTS_TOTAL.labels(
                    method=operation,
                    status='success'
                ).inc()
                
                # Track operation latency
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                
                return result
                
            except Exception as e:
                # Track failed operation
                AUTH_REQUESTS_TOTAL.labels(
                    method=operation,
                    status='error'
                ).inc()
                
                AUTH_FAILURE_TOTAL.labels(
                    reason=type(e).__name__,
                    method=operation
                ).inc()
                
                # Still track latency for failed operations
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                # Track successful operation
                AUTH_REQUESTS_TOTAL.labels(
                    method=operation,
                    status='success'
                ).inc()
                
                # Track operation latency
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                
                return result
                
            except Exception as e:
                # Track failed operation
                AUTH_REQUESTS_TOTAL.labels(
                    method=operation,
                    status='error'
                ).inc()
                
                AUTH_FAILURE_TOTAL.labels(
                    reason=type(e).__name__,
                    method=operation
                ).inc()
                
                # Still track latency for failed operations
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def track_auth_operation(operation: str):
    """Decorator to track authentication operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                AUTH_SUCCESS_TOTAL.labels(user_type="authenticated").inc()
                return result
            except Exception as e:
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                AUTH_FAILURE_TOTAL.labels(
                    reason=e.__class__.__name__, 
                    method=operation
                ).inc()
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                AUTH_SUCCESS_TOTAL.labels(user_type="authenticated").inc()
                return result
            except Exception as e:
                AUTH_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                AUTH_FAILURE_TOTAL.labels(
                    reason=e.__class__.__name__, 
                    method=operation
                ).inc()
                raise
        
        return async_wrapper if hasattr(func, '__code__') and func.__code__.co_flags & 0x80 else sync_wrapper
    return decorator

def track_supabase_operation(operation: str, table: str):
    """Decorator to track Supabase database operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                SUPABASE_QUERY_DURATION.labels(operation=operation, table=table).observe(duration)
                SUPABASE_OPERATIONS_TOTAL.labels(
                    operation=operation, 
                    table=table, 
                    status="success"
                ).inc()
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                SUPABASE_QUERY_DURATION.labels(operation=operation, table=table).observe(duration)
                SUPABASE_OPERATIONS_TOTAL.labels(
                    operation=operation, 
                    table=table, 
                    status="error"
                ).inc()
                SUPABASE_ERRORS_TOTAL.labels(
                    operation=operation,
                    table=table,
                    error_code=getattr(e, 'code', e.__class__.__name__)
                ).inc()
                
                raise
        return wrapper
    return decorator

def track_cache_operation(cache_type: str):
    """Decorator to track cache operations"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                if result is not None:
                    CACHE_OPERATIONS.labels(
                        operation="get", 
                        cache_type=cache_type, 
                        status="hit"
                    ).inc()
                    JWT_CACHE_HITS.labels(cache_type=cache_type).inc()
                else:
                    CACHE_OPERATIONS.labels(
                        operation="get", 
                        cache_type=cache_type, 
                        status="miss"
                    ).inc()
                    JWT_CACHE_MISSES.labels(cache_type=cache_type).inc()
                return result
            except Exception as e:
                CACHE_OPERATIONS.labels(
                    operation="get", 
                    cache_type=cache_type, 
                    status="error"
                ).inc()
                raise
        return wrapper
    return decorator

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def update_cache_hit_ratio(cache_type: str, hits: int, total: int):
    """Update cache hit ratio gauge"""
    if total > 0:
        ratio = hits / total
        CACHE_HIT_RATIO.labels(cache_type=cache_type).set(ratio)

def record_user_action(action_type: str, user_id: Optional[str] = None):
    """Record user action with optional user context"""
    USER_ACTIONS.labels(action_type=action_type).inc()

def record_business_metric(metric_type: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
    """Record business metrics with flexible labels"""
    if labels is None:
        labels = {}
        
    if metric_type == "salary_calculation":
        SALARY_CALCULATIONS.labels(
            calculation_type=labels.get("calculation_type", "unknown")
        ).inc()
    elif metric_type == "raise_request":
        RAISE_REQUESTS.labels(
            status=labels.get("status", "unknown")
        ).inc()

# ============================================================================
# METRICS COLLECTION
# ============================================================================

class MetricsCollector:
    """Centralized metrics collection and reporting"""
    
    def __init__(self):
        self._start_time = time.time()
    
    def get_uptime(self) -> float:
        """Get application uptime in seconds"""
        return time.time() - self._start_time
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        import psutil
        import os
        
        # Memory metrics
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        MEMORY_USAGE.labels(type="rss").set(memory_info.rss)
        MEMORY_USAGE.labels(type="vms").set(memory_info.vms)
        
        # Connection metrics (placeholder - would integrate with actual connection pools)
        # ACTIVE_CONNECTIONS.labels(type="http").set(current_http_connections)
        # ACTIVE_CONNECTIONS.labels(type="database").set(current_db_connections)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics"""
        return {
            "uptime_seconds": self.get_uptime(),
            "auth_metrics": {
                "total_requests": AUTH_REQUESTS_TOTAL._value.sum(),
                "success_count": AUTH_SUCCESS_TOTAL._value.sum(),
                "failure_count": AUTH_FAILURE_TOTAL._value.sum()
            },
            "supabase_metrics": {
                "total_operations": SUPABASE_OPERATIONS_TOTAL._value.sum(),
                "error_count": SUPABASE_ERRORS_TOTAL._value.sum()
            }
        }

# Global metrics collector instance
metrics_collector = MetricsCollector() 