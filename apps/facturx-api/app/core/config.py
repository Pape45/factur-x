"""Application configuration settings.

Centralized configuration management using Pydantic Settings.
Supports environment variables and .env files.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.
    
    All settings can be overridden via environment variables.
    """
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    API_DEBUG: bool = Field(default=False, description="Enable debug mode")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://facturx:password@localhost:5432/facturx_db",
        description="Database connection URL"
    )
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # Security Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts"
    )
    
    # JWT Configuration
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiration in minutes"
    )
    
    # File Upload Configuration
    UPLOAD_DIR: str = Field(default="./uploads", description="Upload directory")
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size in bytes"
    )
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".pdf", ".xml", ".json"],
        description="Allowed file extensions"
    )
    
    # Factur-X Configuration
    FACTURX_PROFILE: str = Field(
        default="BASIC",
        description="Default Factur-X profile"
    )
    FACTURX_VALIDATION_ENABLED: bool = Field(
        default=True,
        description="Enable Factur-X validation"
    )
    
    # External Tools Configuration
    VERAPDF_PATH: Optional[str] = Field(
        default=None,
        description="Path to veraPDF executable"
    )
    MUSTANG_PATH: Optional[str] = Field(
        default=None,
        description="Path to Mustang executable"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format (json or text)"
    )
    
    # Monitoring Configuration
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )
    
    # Celery Configuration (for background tasks)
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL"
    )
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    @validator("FACTURX_PROFILE")
    def validate_facturx_profile(cls, v):
        """Validate Factur-X profile."""
        allowed_profiles = ["MINIMUM", "BASIC", "COMFORT", "EXTENDED"]
        if v.upper() not in allowed_profiles:
            raise ValueError(f"Profile must be one of: {allowed_profiles}")
        return v.upper()
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()
