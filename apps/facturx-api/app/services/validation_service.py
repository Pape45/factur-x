"""Validation service for Factur-X PDF/A-3 compliance using veraPDF."""

import subprocess
import tempfile
import os
import json
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ValidationService:
    """Service for validating PDF/A-3 and Factur-X compliance."""
    
    def __init__(self):
        self.verapdf_path = self._find_verapdf()
        
    def _find_verapdf(self) -> Optional[str]:
        """Find veraPDF installation path."""
        # Common veraPDF installation paths
        possible_paths = [
            "/usr/local/bin/verapdf",
            "/opt/verapdf/verapdf",
            "verapdf",  # If in PATH
            "/Applications/veraPDF/verapdf",  # macOS
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    logger.info(f"Found veraPDF at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
                
        logger.warning("veraPDF not found. PDF/A-3 validation will be limited.")
        return None
    
    def validate_pdfa3(self, pdf_content: bytes) -> Dict[str, Any]:
        """Validate PDF/A-3 compliance using veraPDF."""
        if not self.verapdf_path:
            return self._fallback_validation(pdf_content)
            
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Run veraPDF validation
                result = subprocess.run([
                    self.verapdf_path,
                    "--format", "json",
                    "--flavour", "3a",  # PDF/A-3a
                    tmp_file_path
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    validation_data = json.loads(result.stdout)
                    return self._parse_verapdf_result(validation_data)
                else:
                    logger.error(f"veraPDF validation failed: {result.stderr}")
                    return self._fallback_validation(pdf_content)
                    
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            logger.error(f"Error during PDF/A-3 validation: {e}")
            return self._fallback_validation(pdf_content)
    
    def _parse_verapdf_result(self, validation_data: Dict) -> Dict[str, Any]:
        """Parse veraPDF JSON output."""
        try:
            jobs = validation_data.get("jobs", [])
            if not jobs:
                return {
                    "is_valid": False,
                    "errors": ["No validation jobs found"],
                    "warnings": [],
                    "validator": "veraPDF"
                }
            
            job = jobs[0]
            validation_result = job.get("validationResult", {})
            
            is_compliant = validation_result.get("isCompliant", False)
            
            # Extract errors and warnings
            errors = []
            warnings = []
            
            test_assertions = validation_result.get("testAssertions", [])
            for assertion in test_assertions:
                status = assertion.get("status")
                message = assertion.get("message", "Unknown error")
                
                if status == "FAILED":
                    errors.append(message)
                elif status == "WARNING":
                    warnings.append(message)
            
            return {
                "is_valid": is_compliant,
                "errors": errors,
                "warnings": warnings,
                "validator": "veraPDF",
                "profile": validation_result.get("profile", "PDF/A-3a"),
                "statement": validation_result.get("statement", "")
            }
            
        except Exception as e:
            logger.error(f"Error parsing veraPDF result: {e}")
            return {
                "is_valid": False,
                "errors": [f"Failed to parse validation result: {e}"],
                "warnings": [],
                "validator": "veraPDF"
            }
    
    def _fallback_validation(self, pdf_content: bytes) -> Dict[str, Any]:
        """Fallback validation when veraPDF is not available."""
        # Basic PDF structure validation
        errors = []
        warnings = []
        
        # Check PDF header
        if not pdf_content.startswith(b"%PDF-"):
            errors.append("Invalid PDF header")
        
        # Check minimum file size
        if len(pdf_content) < 1024:
            errors.append("PDF file too small")
        
        # Check for PDF trailer
        if b"%%EOF" not in pdf_content[-1024:]:
            warnings.append("PDF trailer not found in expected location")
        
        # Check for XMP metadata (required for PDF/A)
        if b"<x:xmpmeta" not in pdf_content:
            warnings.append("XMP metadata not found (required for PDF/A)")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings + ["veraPDF not available - using basic validation"],
            "validator": "fallback"
        }
    
    def validate_facturx_structure(self, pdf_content: bytes) -> Dict[str, Any]:
        """Validate Factur-X specific structure requirements."""
        errors = []
        warnings = []
        
        # Check for embedded files (XML should be embedded)
        if b"/EmbeddedFiles" not in pdf_content:
            errors.append("No embedded files found - Factur-X requires embedded XML")
        
        # Check for specific Factur-X file names
        facturx_files = [b"factur-x.xml", b"ZUGFeRD-invoice.xml"]
        has_facturx_file = any(filename in pdf_content for filename in facturx_files)
        
        if not has_facturx_file:
            errors.append("Factur-X XML file not found in embedded files")
        
        # Check for PDF/A conformance declaration
        if b"/GTS_PDFA1" not in pdf_content and b"/GTS_PDFA3" not in pdf_content:
            warnings.append("PDF/A conformance declaration not found")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validator": "facturx_structure"
        }
    
    def validate_comprehensive(self, pdf_content: bytes) -> Dict[str, Any]:
        """Comprehensive validation combining PDF/A-3 and Factur-X checks."""
        # Run both validations
        pdfa_result = self.validate_pdfa3(pdf_content)
        facturx_result = self.validate_facturx_structure(pdf_content)
        
        # Combine results
        all_errors = pdfa_result["errors"] + facturx_result["errors"]
        all_warnings = pdfa_result["warnings"] + facturx_result["warnings"]
        
        return {
            "is_valid": pdfa_result["is_valid"] and facturx_result["is_valid"],
            "errors": all_errors,
            "warnings": all_warnings,
            "pdfa3_validation": pdfa_result,
            "facturx_validation": facturx_result,
            "validator": "comprehensive"
        }
    
    def get_validation_info(self) -> Dict[str, Any]:
        """Get information about available validation tools."""
        return {
            "verapdf_available": self.verapdf_path is not None,
            "verapdf_path": self.verapdf_path,
            "supported_validations": [
                "PDF/A-3 compliance",
                "Factur-X structure",
                "Comprehensive validation"
            ]
        }