from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse, Response
import tempfile
import os
from pathlib import Path
import io

from ..models.invoice import Invoice, InvoiceCreateRequest, InvoiceResponse
from ..models.business import get_business_config
from ..services.invoice_service import InvoiceService
from ..services.facturx_service import FacturXService
from ..services.xml_generator import XMLGenerator
from ..services.pdf_generator import PDFGenerator
from ..services.validation_service import ValidationService

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
    responses={404: {"description": "Not found"}},
)

invoice_service = InvoiceService()
facturx_service = FacturXService()
xml_generator = XMLGenerator()
pdf_generator = PDFGenerator()
validation_service = ValidationService()


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_request: InvoiceCreateRequest) -> InvoiceResponse:
    """
    Create a new invoice with automatic number generation.
    
    This endpoint:
    - Generates a unique invoice number
    - Validates the invoice data
    - Creates the invoice record
    - Returns the complete invoice data
    """
    try:
        # Generate invoice number
        invoice_number = invoice_service.generate_invoice_number()
        
        # Create invoice with generated number
        invoice_data = invoice_request.dict()
        invoice_data["invoice_number"] = invoice_number
        invoice_data["issue_date"] = datetime.now().date()
        
        # Add seller information from business config
        business_config = get_business_config()
        invoice_data["seller"] = {
            "name": business_config.company_name,
            "address": business_config.legal_address.dict(),
            "tax_registration": business_config.tax_registration.dict(),
            "legal_registration": {
                "registration_id": business_config.siret,
                "registration_scheme": "SIRET",
                "registration_name": business_config.company_name
            },
            "contact": {
                "telephone": business_config.phone,
                "email": business_config.email
            }
        }
        
        # Create and validate invoice
        invoice = Invoice(**invoice_data)
        
        # Store invoice (in a real app, this would save to database)
        stored_invoice = invoice_service.store_invoice(invoice)
        
        return InvoiceResponse(
            invoice=stored_invoice,
            status="created",
            message="Invoice created successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid invoice data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create invoice: {str(e)}"
        )


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str) -> InvoiceResponse:
    """
    Retrieve an invoice by ID.
    """
    try:
        invoice = invoice_service.get_invoice(invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        return InvoiceResponse(
            invoice=invoice,
            status="found",
            message="Invoice retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve invoice: {str(e)}"
        )


@router.get("/", response_model=List[InvoiceResponse])
async def list_invoices(
    limit: int = 10,
    offset: int = 0,
    buyer_name: Optional[str] = None
) -> List[InvoiceResponse]:
    """
    List invoices with optional filtering and pagination.
    """
    try:
        invoices = invoice_service.list_invoices(
            limit=limit,
            offset=offset,
            buyer_name=buyer_name
        )
        
        return [
            InvoiceResponse(
                invoice=invoice,
                status="found",
                message="Invoice listed"
            )
            for invoice in invoices
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list invoices: {str(e)}"
        )


@router.get("/{invoice_id}/xml")
async def get_invoice_xml(invoice_id: str):
    """Generate Factur-X XML for an invoice"""
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        xml_content = facturx_service.generate_xml_only(invoice)
        
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={invoice_id}.xml"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate XML: {str(e)}")


@router.get("/{invoice_id}/pdf")
async def get_invoice_pdf(invoice_id: str):
    """Generate standard PDF for an invoice"""
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        pdf_content = facturx_service.generate_pdf_only(invoice)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={invoice_id}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@router.get("/{invoice_id}/facturx")
async def get_invoice_facturx(
    invoice_id: str,
    level: str = Query("basic", description="Factur-X conformance level")
):
    """Generate Factur-X compliant PDF with embedded XML"""
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Validate level
    supported_levels = facturx_service.get_supported_levels()
    if level not in supported_levels:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported level '{level}'. Supported levels: {supported_levels}"
        )
    
    try:
        pdf_bytes, xml_content, validation = facturx_service.generate_facturx_invoice(invoice, level)
        
        if not validation['is_valid']:
            raise HTTPException(
                status_code=500, 
                detail=f"Generated Factur-X file is invalid: {validation['errors']}"
            )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={invoice_id}_facturx.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Factur-X: {str(e)}")


@router.post("/{invoice_id}/validate")
async def validate_invoice_facturx(invoice_id: str):
    """Validate Factur-X compliance for a specific invoice"""
    invoice = invoice_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    try:
        # Generate Factur-X and validate
        pdf_bytes, xml_content, validation = facturx_service.generate_facturx_invoice(invoice)
        
        # Validate XML structure
        xml_validation = xml_generator.validate_xml_structure(xml_content)
        
        return {
            "invoice_id": invoice_id,
            "invoice_number": invoice.invoice_number,
            "facturx_validation": validation,
            "xml_validation": xml_validation,
            "overall_valid": validation['is_valid'] and xml_validation['is_valid'],
            "validated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate invoice: {str(e)}")


@router.post("/sample", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_sample_invoice() -> InvoiceResponse:
    """
    Create a sample invoice for testing purposes.
    
    This endpoint creates a demo invoice with fictional data
    to test the Factur-X functionality.
    """
    try:
        import traceback
        print("Starting sample invoice creation...")
        
        # Create sample invoice using the service
        sample_invoice = invoice_service.create_sample_invoice()
        print(f"Sample invoice created: {sample_invoice.invoice_number}")
        
        # Store the sample invoice
        stored_invoice = invoice_service.store_invoice(sample_invoice)
        print(f"Sample invoice stored successfully")
        
        return InvoiceResponse(
            invoice=stored_invoice,
            status="created",
            message="Sample invoice created successfully"
        )
        
    except Exception as e:
        import traceback
        print(f"Error creating sample invoice: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create sample invoice: {str(e)}"
        )


@router.post("/validate")
async def validate_facturx_file(file: UploadFile = File(...)):
    """Validate a Factur-X file"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        content = await file.read()
        
        # Get comprehensive file information
        file_info = facturx_service.get_facturx_info(content)
        
        return {
            "filename": file.filename,
            "file_size": len(content),
            "is_facturx": file_info['is_facturx'],
            "facturx_level": file_info['level'],
            "has_xml": file_info['has_xml'],
            "validation": file_info['validation'],
            "analyzed_at": file_info['created_at']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate file: {str(e)}")