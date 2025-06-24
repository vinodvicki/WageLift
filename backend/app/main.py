"""
Main FastAPI application for WageLift.

This module sets up the FastAPI application with all middleware, 
security configurations, and API routes.
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine, async_engine
from app.core.logging import setup_structured_logging, get_logger, RequestContext
from app.core.metrics import metrics_collector

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Logger
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan events.
    Handles startup and shutdown procedures.
    """
    # Startup
    logger.info("Starting WageLift API", version=settings.PROJECT_VERSION)
    
    # Initialize database
    try:
        # Test database connection
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection established")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        raise
    
    # Initialize external services
    # TODO: Add health checks for external APIs (Auth0, BLS, etc.)
    
    yield
    
    # Shutdown
    logger.info("Shutting down WageLift API")
    await async_engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
    openapi_url=settings.OPENAPI_URL if settings.ENABLE_DOCS else None,
    docs_url=settings.DOCS_URL if settings.ENABLE_DOCS else None,
    redoc_url=settings.REDOC_URL if settings.ENABLE_REDOC else None,
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Setup logging
setup_structured_logging()

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add security middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["wagelift.com", "*.wagelift.com", "localhost"]
    )

# Add CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
from app.api.auth import router as auth_router
from app.api.supabase import router as supabase_router
from app.api.salary import router as salary_router
from app.api.cpi_calculation import router as cpi_router
from app.api.benchmark import router as benchmark_router
from app.api.raise_letter import router as raise_letter_router
from app.api.email import router as email_router
from app.api.editor import router as editor_router
from app.api.gusto import router as gusto_router

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(supabase_router, prefix=f"{settings.API_V1_STR}", tags=["User Data"])
app.include_router(salary_router, prefix=f"{settings.API_V1_STR}", tags=["Salary Management"])
app.include_router(cpi_router, prefix=f"{settings.API_V1_STR}", tags=["CPI Calculations"])
app.include_router(benchmark_router, prefix=f"{settings.API_V1_STR}", tags=["Salary Benchmarks"])
app.include_router(raise_letter_router, prefix=f"{settings.API_V1_STR}/raise-letter", tags=["AI Raise Letters"])
app.include_router(email_router, prefix=f"{settings.API_V1_STR}/email", tags=["Email Services"])
app.include_router(editor_router, tags=["Editor"])
app.include_router(gusto_router, prefix=f"{settings.API_V1_STR}/gusto", tags=["Gusto Integration"])


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """Log all requests with metrics."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Update metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    # Log request
    logger.info(
        "HTTP request processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=duration,
        user_agent=request.headers.get("user-agent"),
        remote_addr=get_remote_address(request),
    )
    
    return response


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    # Cache headers for API responses
    if request.url.path.startswith(settings.API_V1_STR):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time(),
    }


# Metrics endpoint (for Prometheus)
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint.
    """
    if not settings.ENABLE_METRICS:
        return {"error": "Metrics disabled"}
    
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with basic API information.
    """
    return {
        "message": "Welcome to WageLift API",
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.PROJECT_VERSION,
        "docs": f"{settings.DOCS_URL}" if settings.ENABLE_DOCS else None,
        "health": "/health",
        "api": settings.API_V1_STR,
    }


# Include API routers
# TODO: Add API routers
# from app.api.v1.api import api_router
# app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
    ) 