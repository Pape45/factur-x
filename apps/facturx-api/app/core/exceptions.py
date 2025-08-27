"""Custom exceptions for the Factur-X Express API.

Defines application-specific exceptions with proper error codes and messages.
"""

from typing import Any, Dict, Optional


class FacturXExpressException(Exception):
    """Base exception for Factur-X Express application."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(FacturXExpressException):
    """Raised when data validation fails."""
    
    def __init__(
        self,
        message: str = "Validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(FacturXExpressException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details=details,
        )


class UnauthorizedError(FacturXExpressException):
    """Raised when authentication or authorization fails."""
    
    def __init__(
        self,
        message: str = "Unauthorized access",
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            details=kwargs.get("details", {}),
        )


class ForbiddenError(FacturXExpressException):
    """Raised when access to a resource is forbidden."""
    
    def __init__(
        self,
        message: str = "Access forbidden",
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            details=kwargs.get("details", {}),
        )


class FacturXError(FacturXExpressException):
    """Raised when Factur-X processing fails."""
    
    def __init__(
        self,
        message: str = "Factur-X processing failed",
        operation: Optional[str] = None,
        profile: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        if profile:
            details["profile"] = profile
        
        super().__init__(
            message=message,
            error_code="FACTURX_ERROR",
            details=details,
        )


class PDFProcessingError(FacturXError):
    """Raised when PDF processing fails."""
    
    def __init__(
        self,
        message: str = "PDF processing failed",
        pdf_path: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if pdf_path:
            details["pdf_path"] = pdf_path
        
        super().__init__(
            message=message,
            operation="pdf_processing",
            details=details,
        )


class XMLGenerationError(FacturXError):
    """Raised when XML CII generation fails."""
    
    def __init__(
        self,
        message: str = "XML CII generation failed",
        xml_profile: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if xml_profile:
            details["xml_profile"] = xml_profile
        
        super().__init__(
            message=message,
            operation="xml_generation",
            details=details,
        )


class ValidationToolError(FacturXError):
    """Raised when external validation tools fail."""
    
    def __init__(
        self,
        message: str = "Validation tool failed",
        tool_name: Optional[str] = None,
        tool_path: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if tool_name:
            details["tool_name"] = tool_name
        if tool_path:
            details["tool_path"] = tool_path
        
        super().__init__(
            message=message,
            operation="validation",
            details=details,
        )


class FileUploadError(FacturXExpressException):
    """Raised when file upload fails."""
    
    def __init__(
        self,
        message: str = "File upload failed",
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if filename:
            details["filename"] = filename
        if file_size is not None:
            details["file_size"] = file_size
        
        super().__init__(
            message=message,
            error_code="FILE_UPLOAD_ERROR",
            details=details,
        )


class DatabaseError(FacturXExpressException):
    """Raised when database operations fail."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if operation:
            details["operation"] = operation
        if table:
            details["table"] = table
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ExternalServiceError(FacturXExpressException):
    """Raised when external service calls fail."""
    
    def __init__(
        self,
        message: str = "External service failed",
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if service_name:
            details["service_name"] = service_name
        if status_code is not None:
            details["status_code"] = status_code
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )


class ConfigurationError(FacturXExpressException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
        )
