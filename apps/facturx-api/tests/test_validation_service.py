"""Unit tests for validation service."""

import pytest
from unittest.mock import patch, MagicMock
import json
import tempfile
import os

from app.services.validation_service import ValidationService
from app.utils.exceptions import ValidationError, ExternalServiceError

class TestValidationService:
    """Test cases for ValidationService."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.service = ValidationService()
        
        # Sample PDF bytes
        self.sample_pdf = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'
        
        # Sample XML content
        self.sample_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <CrossIndustryInvoice xmlns="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">
            <ExchangedDocumentContext>
                <TestDocumentContextParameter>
                    <ID>urn:cen.eu:en16931:2017</ID>
                </TestDocumentContextParameter>
            </ExchangedDocumentContext>
        </CrossIndustryInvoice>'''
    
    @patch('shutil.which')
    def test_find_verapdf_executable_found(self, mock_which):
        """Test finding veraPDF executable when it exists."""
        mock_which.return_value = '/usr/local/bin/verapdf'
        
        result = self.service._find_verapdf_executable()
        
        assert result == '/usr/local/bin/verapdf'
        mock_which.assert_called_once_with('verapdf')
    
    @patch('shutil.which')
    def test_find_verapdf_executable_not_found(self, mock_which):
        """Test finding veraPDF executable when it doesn't exist."""
        mock_which.return_value = None
        
        result = self.service._find_verapdf_executable()
        
        assert result is None
        mock_which.assert_called_once_with('verapdf')
    
    @patch('app.services.validation_service.ValidationService._find_verapdf_executable')
    @patch('subprocess.run')
    def test_validate_pdfa3_compliance_success(self, mock_run, mock_find_verapdf):
        """Test successful PDF/A-3 compliance validation."""
        # Mock veraPDF found
        mock_find_verapdf.return_value = '/usr/local/bin/verapdf'
        
        # Mock successful veraPDF output
        mock_output = {
            "compliant": True,
            "pdfFlavour": "PDF/A-3b",
            "totalAssertions": 100,
            "failedAssertions": 0,
            "passedChecks": 100,
            "failedChecks": 0
        }
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_output),
            stderr=""
        )
        
        result = self.service.validate_pdfa3_compliance(self.sample_pdf)
        
        assert result["is_compliant"] is True
        assert result["pdf_flavour"] == "PDF/A-3b"
        assert result["total_assertions"] == 100
        assert result["failed_assertions"] == 0
        assert len(result["errors"]) == 0
    
    @patch('app.services.validation_service.ValidationService._find_verapdf_executable')
    @patch('subprocess.run')
    def test_validate_pdfa3_compliance_failure(self, mock_run, mock_find_verapdf):
        """Test PDF/A-3 compliance validation with failures."""
        # Mock veraPDF found
        mock_find_verapdf.return_value = '/usr/local/bin/verapdf'
        
        # Mock failed veraPDF output
        mock_output = {
            "compliant": False,
            "pdfFlavour": "PDF/A-3b",
            "totalAssertions": 100,
            "failedAssertions": 5,
            "passedChecks": 95,
            "failedChecks": 5,
            "validationReports": [{
                "details": {
                    "failedRules": [
                        {
                            "clause": "6.1.7-1",
                            "description": "Font not embedded",
                            "object": "Font1"
                        }
                    ]
                }
            }]
        }
        
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps(mock_output),
            stderr=""
        )
        
        result = self.service.validate_pdfa3_compliance(self.sample_pdf)
        
        assert result["is_compliant"] is False
        assert result["failed_assertions"] == 5
        assert len(result["errors"]) > 0
        assert "Font not embedded" in str(result["errors"])
    
    @patch('app.services.validation_service.ValidationService._find_verapdf_executable')
    def test_validate_pdfa3_compliance_no_verapdf(self, mock_find_verapdf):
        """Test PDF/A-3 validation when veraPDF is not available."""
        # Mock veraPDF not found
        mock_find_verapdf.return_value = None
        
        result = self.service.validate_pdfa3_compliance(self.sample_pdf)
        
        assert result["is_compliant"] is False
        assert "veraPDF not found" in result["errors"][0]
        assert result["pdf_flavour"] == "Unknown"
    
    @patch('app.services.validation_service.ValidationService._find_verapdf_executable')
    @patch('subprocess.run')
    def test_validate_pdfa3_compliance_subprocess_error(self, mock_run, mock_find_verapdf):
        """Test PDF/A-3 validation with subprocess error."""
        # Mock veraPDF found
        mock_find_verapdf.return_value = '/usr/local/bin/verapdf'
        
        # Mock subprocess error
        mock_run.side_effect = Exception("Subprocess failed")
        
        with pytest.raises(ExternalServiceError):
            self.service.validate_pdfa3_compliance(self.sample_pdf)
    
    def test_parse_verapdf_output_valid_json(self):
        """Test parsing valid veraPDF JSON output."""
        mock_output = {
            "compliant": True,
            "pdfFlavour": "PDF/A-3b",
            "totalAssertions": 50,
            "failedAssertions": 0
        }
        
        result = self.service._parse_verapdf_output(json.dumps(mock_output))
        
        assert result["is_compliant"] is True
        assert result["pdf_flavour"] == "PDF/A-3b"
        assert result["total_assertions"] == 50
        assert result["failed_assertions"] == 0
    
    def test_parse_verapdf_output_invalid_json(self):
        """Test parsing invalid veraPDF JSON output."""
        invalid_json = "This is not valid JSON"
        
        result = self.service._parse_verapdf_output(invalid_json)
        
        assert result["is_compliant"] is False
        assert "Failed to parse veraPDF output" in result["errors"][0]
    
    def test_parse_verapdf_output_missing_fields(self):
        """Test parsing veraPDF output with missing fields."""
        incomplete_output = {
            "compliant": True
            # Missing other required fields
        }
        
        result = self.service._parse_verapdf_output(json.dumps(incomplete_output))
        
        assert result["is_compliant"] is True
        assert result["pdf_flavour"] == "Unknown"
        assert result["total_assertions"] == 0
    
    @patch('app.services.validation_service.facturx')
    def test_validate_facturx_structure_valid(self, mock_facturx):
        """Test Factur-X structure validation with valid file."""
        # Mock facturx validation
        mock_facturx.check_facturx_xsd.return_value = True
        mock_facturx.get_level.return_value = 'EN 16931'
        mock_facturx.get_facturx_xml_from_pdf.return_value = self.sample_xml
        
        result = self.service.validate_facturx_structure(self.sample_pdf)
        
        assert result["is_valid"] is True
        assert result["level"] == 'EN 16931'
        assert result["has_embedded_xml"] is True
        assert len(result["errors"]) == 0
    
    @patch('app.services.validation_service.facturx')
    def test_validate_facturx_structure_invalid(self, mock_facturx):
        """Test Factur-X structure validation with invalid file."""
        # Mock facturx validation failure
        mock_facturx.check_facturx_xsd.return_value = False
        mock_facturx.get_level.return_value = None
        mock_facturx.get_facturx_xml_from_pdf.return_value = None
        
        result = self.service.validate_facturx_structure(self.sample_pdf)
        
        assert result["is_valid"] is False
        assert result["level"] is None
        assert result["has_embedded_xml"] is False
        assert len(result["errors"]) > 0
    
    @patch('app.services.validation_service.facturx')
    def test_validate_facturx_structure_exception(self, mock_facturx):
        """Test Factur-X structure validation with exception."""
        # Mock facturx exception
        mock_facturx.check_facturx_xsd.side_effect = Exception("Validation failed")
        
        result = self.service.validate_facturx_structure(self.sample_pdf)
        
        assert result["is_valid"] is False
        assert "Validation failed" in result["errors"][0]
    
    @patch('app.services.validation_service.ValidationService.validate_pdfa3_compliance')
    @patch('app.services.validation_service.ValidationService.validate_facturx_structure')
    def test_validate_facturx_file_complete_success(self, mock_facturx_validation, mock_pdfa_validation):
        """Test complete Factur-X file validation with success."""
        # Mock successful PDF/A-3 validation
        mock_pdfa_validation.return_value = {
            "is_compliant": True,
            "pdf_flavour": "PDF/A-3b",
            "total_assertions": 100,
            "failed_assertions": 0,
            "errors": [],
            "warnings": []
        }
        
        # Mock successful Factur-X validation
        mock_facturx_validation.return_value = {
            "is_valid": True,
            "level": "EN 16931",
            "has_embedded_xml": True,
            "errors": [],
            "warnings": []
        }
        
        result = self.service.validate_facturx_file(self.sample_pdf)
        
        assert result["is_valid"] is True
        assert result["is_pdfa3_compliant"] is True
        assert result["facturx_level"] == "EN 16931"
        assert result["has_embedded_xml"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
    
    @patch('app.services.validation_service.ValidationService.validate_pdfa3_compliance')
    @patch('app.services.validation_service.ValidationService.validate_facturx_structure')
    def test_validate_facturx_file_complete_failure(self, mock_facturx_validation, mock_pdfa_validation):
        """Test complete Factur-X file validation with failures."""
        # Mock failed PDF/A-3 validation
        mock_pdfa_validation.return_value = {
            "is_compliant": False,
            "pdf_flavour": "PDF/A-3b",
            "total_assertions": 100,
            "failed_assertions": 5,
            "errors": ["Font not embedded"],
            "warnings": []
        }
        
        # Mock failed Factur-X validation
        mock_facturx_validation.return_value = {
            "is_valid": False,
            "level": None,
            "has_embedded_xml": False,
            "errors": ["No embedded XML found"],
            "warnings": []
        }
        
        result = self.service.validate_facturx_file(self.sample_pdf)
        
        assert result["is_valid"] is False
        assert result["is_pdfa3_compliant"] is False
        assert result["facturx_level"] is None
        assert result["has_embedded_xml"] is False
        assert len(result["errors"]) == 2
        assert "Font not embedded" in result["errors"]
        assert "No embedded XML found" in result["errors"]
    
    def test_validate_facturx_file_empty_pdf(self):
        """Test validation with empty PDF data."""
        empty_pdf = b''
        
        with pytest.raises(ValidationError):
            self.service.validate_facturx_file(empty_pdf)
    
    def test_validate_facturx_file_invalid_pdf(self):
        """Test validation with invalid PDF data."""
        invalid_pdf = b'This is not a PDF file'
        
        result = self.service.validate_facturx_file(invalid_pdf)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_facturx_file_large_pdf(self):
        """Test validation with large PDF file."""
        # Create a larger PDF-like content
        large_pdf = self.sample_pdf + b'\n' + b'0' * 10000  # Add 10KB of data
        
        # Should handle large files gracefully
        result = self.service.validate_facturx_file(large_pdf)
        
        assert result is not None
        assert "is_valid" in result
    
    @patch('tempfile.NamedTemporaryFile')
    def test_temporary_file_handling(self, mock_tempfile):
        """Test proper handling of temporary files."""
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = '/tmp/test_file.pdf'
        mock_file.__enter__.return_value = mock_file
        mock_tempfile.return_value = mock_file
        
        # Test that temporary files are properly managed
        with patch('app.services.validation_service.ValidationService._find_verapdf_executable') as mock_find:
            mock_find.return_value = None  # No veraPDF to avoid subprocess calls
            
            result = self.service.validate_pdfa3_compliance(self.sample_pdf)
            
            # Verify temporary file was created and used
            mock_tempfile.assert_called_once()
            mock_file.write.assert_called_once_with(self.sample_pdf)
            mock_file.flush.assert_called_once()
    
    def test_error_aggregation(self):
        """Test that errors from different validation steps are properly aggregated."""
        with patch('app.services.validation_service.ValidationService.validate_pdfa3_compliance') as mock_pdfa:
            with patch('app.services.validation_service.ValidationService.validate_facturx_structure') as mock_facturx:
                # Mock multiple errors from different sources
                mock_pdfa.return_value = {
                    "is_compliant": False,
                    "errors": ["PDF/A-3 error 1", "PDF/A-3 error 2"],
                    "warnings": ["PDF/A-3 warning 1"]
                }
                
                mock_facturx.return_value = {
                    "is_valid": False,
                    "errors": ["Factur-X error 1"],
                    "warnings": ["Factur-X warning 1", "Factur-X warning 2"]
                }
                
                result = self.service.validate_facturx_file(self.sample_pdf)
                
                # Check that all errors and warnings are aggregated
                assert len(result["errors"]) == 3
                assert len(result["warnings"]) == 3
                assert "PDF/A-3 error 1" in result["errors"]
                assert "PDF/A-3 error 2" in result["errors"]
                assert "Factur-X error 1" in result["errors"]
                assert "PDF/A-3 warning 1" in result["warnings"]
                assert "Factur-X warning 1" in result["warnings"]
                assert "Factur-X warning 2" in result["warnings"]
    
    def test_validation_metadata(self):
        """Test that validation results include proper metadata."""
        result = self.service.validate_facturx_file(self.sample_pdf)
        
        # Check that metadata fields are present
        required_fields = [
            "is_valid", "is_pdfa3_compliant", "facturx_level", 
            "has_embedded_xml", "errors", "warnings", "validation_date"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing metadata field: {field}"
        
        # Check data types
        assert isinstance(result["is_valid"], bool)
        assert isinstance(result["is_pdfa3_compliant"], bool)
        assert isinstance(result["has_embedded_xml"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["validation_date"], str)