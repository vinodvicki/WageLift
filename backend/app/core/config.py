"""
Application configuration using Pydantic Settings.
Handles environment variables, validation, and type conversion.
"""

import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    validator,
    Field,
)
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Project Information
    PROJECT_NAME: str = "WageLift API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = (
        "AI-powered platform that helps US employees quantify purchasing-power "
        "loss due to inflation and craft evidence-based raise requests."
    )
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                # Handle JSON-like string format
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    # Fallback to manual parsing
                    v = v.strip("[]")
                    return [i.strip().strip('"\'') for i in v.split(",")]
            else:
                # Handle comma-separated format
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")

    # Database Configuration
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///./wagelift_dev.db"

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        # Use SQLite for local development if PostgreSQL not configured
        if not values.get("POSTGRES_SERVER"):
            return "sqlite:///./wagelift_dev.db"
        # Build PostgreSQL connection string manually
        user = values.get("POSTGRES_USER")
        password = values.get("POSTGRES_PASSWORD")
        server = values.get("POSTGRES_SERVER")
        port = values.get("POSTGRES_PORT", 5432)
        db = values.get("POSTGRES_DB", "")
        return f"postgresql://{user}:{password}@{server}:{port}/{db}"

    # Redis Configuration
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = Field(default=None, description="Supabase project URL")
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None, description="Supabase anonymous key")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None, description="Supabase service role key")
    
    # Database Connection Pool Configuration
    DB_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Database connection pool max overflow")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Database connection pool recycle time")
    
    # Auth0 Configuration
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_AUDIENCE: Optional[str] = None
    AUTH0_CLIENT_ID: Optional[str] = None
    AUTH0_CLIENT_SECRET: Optional[str] = None
    AUTH0_ALGORITHM: str = "RS256"
    
    # External APIs
    BLS_API_KEY: Optional[str] = None
    BLS_BASE_URL: str = "https://api.bls.gov/publicAPI/v2"
    
    CAREERONESTOP_USER_ID: Optional[str] = None
    CAREERONESTOP_AUTHORIZATION_TOKEN: Optional[str] = None
    CAREERONESTOP_BASE_URL: str = "https://api.careeronestop.org/v1"
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Gusto OAuth Configuration
    GUSTO_CLIENT_ID: Optional[str] = None
    GUSTO_CLIENT_SECRET: Optional[str] = None
    GUSTO_REDIRECT_URI: Optional[str] = None
    GUSTO_SCOPES: str = "read write payrolls employees compensations"
    GUSTO_AUTH_URL: str = "https://api.gusto.com/oauth/authorize"
    GUSTO_TOKEN_URL: str = "https://api.gusto.com/oauth/token"
    GUSTO_API_BASE_URL: str = "https://api.gusto.com/v1"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Monitoring & Logging
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    SENTRY_DSN: Optional[HttpUrl] = None
    
    # Email Configuration (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_TYPES: List[str] = ["application/pdf", "text/plain", "image/jpeg", "image/png"]
    
    # Security Configuration
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL_CHARS: bool = True
    SESSION_TIMEOUT_MINUTES: int = 30
    
    # Cache Configuration
    CACHE_TTL_SECONDS: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    
    # Feature Flags
    ENABLE_PAYROLL_SYNC: bool = False
    ENABLE_RESEARCH_MODE: bool = True
    ENABLE_PDF_GENERATION: bool = True
    ENABLE_EMAIL_SENDING: bool = True
    
    # Development Configuration
    ENABLE_DOCS: bool = True
    ENABLE_REDOC: bool = True
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"

    class Config:
        """Pydantic configuration."""
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True
        
        # Environment variable prefixes
        env_prefix = ""
        
        # Field configurations for sensitive data
        fields = {
            "SECRET_KEY": {"description": "Secret key for JWT tokens"},
            "POSTGRES_PASSWORD": {"description": "Database password"},
            "AUTH0_CLIENT_SECRET": {"description": "Auth0 client secret"},
            "OPENAI_API_KEY": {"description": "OpenAI API key"},
            "BLS_API_KEY": {"description": "Bureau of Labor Statistics API key"},
            "GUSTO_CLIENT_SECRET": {"description": "Gusto OAuth client secret"},
        }


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings (dependency injection)."""
    return settings 