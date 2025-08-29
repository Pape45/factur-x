"""Custom exceptions for Factur-X API."""

from typing import Dict, Any

class FacturXError(Exception):
    """Base exception for Factur-X related errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "FACTURX_ERROR"
        self.details = details or {}

class InvoiceValidationError(FacturXError):
    """Raised when invoice data validation fails."""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        super().__init__(message, "INVOICE_VALIDATION_ERROR")
        self.field = field
        self.value = value
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(value)

class XMLGenerationError(FacturXError):
    """Raised when XML generation fails."""
    
    def __init__(self, message: str, xml_element: str = None):
        super().__init__(message, "XML_GENERATION_ERROR")
        self.xml_element = xml_element
        if xml_element:
            self.details["xml_element"] = xml_element

class PDFGenerationError(FacturXError):
    """Raised when PDF generation fails."""
    
    def __init__(self, message: str, pdf_section: str = None):
        super().__init__(message, "PDF_GENERATION_ERROR")
        self.pdf_section = pdf_section
        if pdf_section:
            self.details["pdf_section"] = pdf_section

class PDFEmbeddingError(FacturXError):
    """Raised when XML embedding in PDF fails."""
    
    def __init__(self, message: str, attachment_name: str = None):
        super().__init__(message, "PDF_EMBEDDING_ERROR")
        self.attachment_name = attachment_name
        if attachment_name:
            self.details["attachment_name"] = attachment_name

class ValidationError(FacturXError):
    """Raised when Factur-X validation fails."""
    
    def __init__(self, message: str, validation_type: str = None, errors: list = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.validation_type = validation_type
        self.errors = errors or []
        if validation_type:
            self.details["validation_type"] = validation_type
        if self.errors:
            self.details["validation_errors"] = self.errors

class BusinessConfigError(FacturXError):
    """Raised when business configuration is invalid or missing."""
    
    def __init__(self, message: str, config_field: str = None):
        super().__init__(message, "BUSINESS_CONFIG_ERROR")
        self.config_field = config_field
        if config_field:
            self.details["config_field"] = config_field

class InvoiceNotFoundError(FacturXError):
    """Raised when requested invoice is not found."""
    
    def __init__(self, invoice_id: str):
        message = f"Invoice with ID '{invoice_id}' not found"
        super().__init__(message, "INVOICE_NOT_FOUND")
        self.invoice_id = invoice_id
        self.details["invoice_id"] = invoice_id

class UnsupportedFormatError(FacturXError):
    """Raised when an unsupported format is requested."""
    
    def __init__(self, format_type: str, supported_formats: list = None):
        message = f"Unsupported format: {format_type}"
        if supported_formats:
            message += f". Supported formats: {', '.join(supported_formats)}"
        super().__init__(message, "UNSUPPORTED_FORMAT")
        self.format_type = format_type
        self.supported_formats = supported_formats or []
        self.details["format_type"] = format_type
        if supported_formats:
            self.details["supported_formats"] = supported_formats

class ExternalServiceError(FacturXError):
    """Raised when external service (like veraPDF) fails."""
    
    def __init__(self, service_name: str, message: str, status_code: int = None):
        full_message = f"{service_name} error: {message}"
        super().__init__(full_message, "EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name
        self.status_code = status_code
        self.details["service_name"] = service_name
        if status_code:
            self.details["status_code"] = status_code

class FileProcessingError(FacturXError):
    """Raised when file processing fails."""
    
    def __init__(self, message: str, filename: str = None, file_type: str = None):
        super().__init__(message, "FILE_PROCESSING_ERROR")
        self.filename = filename
        self.file_type = file_type
        if filename:
            self.details["filename"] = filename
        if file_type:
            self.details["file_type"] = file_type