from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
import traceback

from .routers import invoices
from .models.business import get_business_config

app = FastAPI(
    title="Factur-X API",
    description="API for generating and validating Factur-X invoices compliant with EN 16931 standard",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(invoices.router, prefix="/api/v1")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc),
            "traceback": traceback.format_exc() if app.debug else None
        }
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    business_config = get_business_config()
    return {
        "message": "Factur-X API is running",
        "version": "1.0.0",
        "description": "API for generating and validating Factur-X invoices",
        "company": business_config.company_name,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "invoices": "/api/v1/invoices"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "factur-x-api",
        "version": "1.0.0"
    }

@app.get("/api/v1/business-config")
async def get_business_configuration():
    """Get business configuration for invoice generation"""
    business_config = get_business_config()
    return {
        "company_name": business_config.company_name,
        "legal_form": business_config.legal_form,
        "country": business_config.legal_address.country.value,
        "currency": business_config.default_currency.value,
        "vat_rates": business_config.vat_rates,
        "invoice_number_format": business_config.invoice_number_format,
        "branding": {
            "primary_color": business_config.primary_color,
            "secondary_color": business_config.secondary_color
        }
    }