"""Factur-X Express FastAPI Application.

Main entry point for the Factur-X Express API server.
Provides endpoints for generating, validating, and managing Factur-X invoices.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import get_settings
from app.core.database import create_db_and_tables, get_database
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.core.exceptions import (
    ValidationError,
    NotFoundError,
    UnauthorizedError,
    FacturXError,
)

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting Factur-X Express API", version="0.1.0")
    
    # Initialize database
    await create_db_and_tables()
    logger.info("Database initialized")
    
    # Yield control to the application
    yield
    
    # Shutdown
    logger.info("Shutting down Factur-X Express API")
    
    # Close database connections
    database = get_database()
    if database:
        await database.disconnect()
        logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="Factur-X Express API",
    description="Professional micro-SaaS for generating, validating, and exporting Factur-X invoices",
    version="0.1.0",
    docs_url="/docs" if settings.API_DEBUG else None,
    redoc_url="/redoc" if settings.API_DEBUG else None,
    lifespan=lifespan,
)

# Add middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )


# Exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors."""
    logger.warning(
        "Validation error",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": str(exc),
            "type": "validation_error",
        },
    )


@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    """Handle not found errors."""
    logger.warning(
        "Resource not found",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": str(exc),
            "type": "not_found_error",
        },
    )


@app.exception_handler(UnauthorizedError)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedError):
    """Handle unauthorized errors."""
    logger.warning(
        "Unauthorized access attempt",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=401,
        content={
            "error": "Unauthorized",
            "message": str(exc),
            "type": "unauthorized_error",
        },
    )


@app.exception_handler(FacturXError)
async def facturx_exception_handler(request: Request, exc: FacturXError):
    """Handle Factur-X specific errors."""
    logger.error(
        "Factur-X processing error",
        path=request.url.path,
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Factur-X Error",
            "message": str(exc),
            "type": "facturx_error",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "type": "internal_error",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "facturx-api",
        "version": "0.1.0",
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_config=None,  # Use our custom logging
    )
