"""Tests for validation service."""

import pytest
from unittest.mock import Mock, patch, mock_open
import json
import subprocess
from app.services.validation_service import ValidationService


class TestValidationService:
    """Test cases for ValidationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = ValidationService()
    
    def test_init(self):
        """Test ValidationService initialization."""
        assert isinstance(self.service, ValidationService)
        # verapdf_path can be None if not found
        assert self.service.verapdf_path is None or isinstance(self.service.verapdf_path, str)
    
    @patch('subprocess.run')
    def test_find_verapdf_success(self, mock_run):
        """Test successful veraPDF discovery."""
        mock_run.return_value = Mock(returncode=0)
        
        service = ValidationService()
        # Should find verapdf in one of the paths
        assert service.verapdf_path is not None
        mock_run.assert_called()
    
    @patch('subprocess.run')
    def test_find_verapdf_not_found(self, mock_run):
        """Test veraPDF not found."""
        mock_run.side_effect = FileNotFoundError()
        
        service = ValidationService()
        assert service.verapdf_path is None
    
    def test_fallback_validation_valid_pdf(self):
        """Test fallback validation with valid PDF content."""
        # Mock valid PDF content
        pdf_content = b"%PDF-1.4\n" + b"x" * 2000 + b"%%EOF"
        
        result = self.service._fallback_validation(pdf_content)
        
        assert isinstance(result, dict)
        assert "is_valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "validator" in result
        assert result["validator"] == "fallback"
    
    def test_fallback_validation_invalid_header(self):
        """Test fallback validation with invalid PDF header."""
        pdf_content = b"INVALID" + b"x" * 2000 + b"%%EOF"
        
        result = self.service._fallback_validation(pdf_content)
        
        assert result["is_valid"] is False
        assert "Invalid PDF header" in result["errors"]
    
    def test_fallback_validation_too_small(self):
        """Test fallback validation with too small PDF."""
        pdf_content = b"%PDF-1.4\n"
        
        result = self.service._fallback_validation(pdf_content)
        
        assert result["is_valid"] is False
        assert "PDF file too small" in result["errors"]
    
    def test_validate_facturx_structure_valid(self):
        """Test Factur-X structure validation with valid content."""
        pdf_content = b"/EmbeddedFiles" + b"factur-x.xml" + b"/GTS_PDFA3"
        
        result = self.service.validate_facturx_structure(pdf_content)
        
        assert result["is_valid"] is True
        assert result["validator"] == "facturx_structure"
        assert len(result["errors"]) == 0
    
    def test_validate_facturx_structure_no_embedded_files(self):
        """Test Factur-X structure validation without embedded files."""
        pdf_content = b"some pdf content without embedded files"
        
        result = self.service.validate_facturx_structure(pdf_content)
        
        assert result["is_valid"] is False
        assert "No embedded files found" in result["errors"][0]
    
    def test_validate_facturx_structure_no_facturx_file(self):
        """Test Factur-X structure validation without Factur-X XML file."""
        pdf_content = b"/EmbeddedFiles some other file"
        
        result = self.service.validate_facturx_structure(pdf_content)
        
        assert result["is_valid"] is False
        assert "Factur-X XML file not found" in result["errors"][0]
    
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_validate_pdfa3_with_verapdf_success(self, mock_unlink, mock_tempfile, mock_run):
        """Test PDF/A-3 validation with veraPDF success."""
        # Mock veraPDF available
        self.service.verapdf_path = "/usr/local/bin/verapdf"
        
        # Mock temporary file
        mock_file = Mock()
        mock_file.name = "/tmp/test.pdf"
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock successful veraPDF output
        verapdf_output = {
            "jobs": [{
                "validationResult": {
                    "isCompliant": True,
                    "profile": "PDF/A-3a",
                    "statement": "PDF file is compliant",
                    "testAssertions": []
                }
            }]
        }
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(verapdf_output)
        )
        
        pdf_content = b"%PDF-1.4\ntest content"
        result = self.service.validate_pdfa3(pdf_content)
        
        assert result["is_valid"] is True
        assert result["validator"] == "veraPDF"
        assert result["profile"] == "PDF/A-3a"
        mock_file.write.assert_called_once_with(pdf_content)
        mock_unlink.assert_called_once_with("/tmp/test.pdf")
    
    @patch('subprocess.run')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    def test_validate_pdfa3_with_verapdf_failure(self, mock_unlink, mock_tempfile, mock_run):
        """Test PDF/A-3 validation with veraPDF failure."""
        # Mock veraPDF available
        self.service.verapdf_path = "/usr/local/bin/verapdf"
        
        # Mock temporary file
        mock_file = Mock()
        mock_file.name = "/tmp/test.pdf"
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        # Mock veraPDF failure
        mock_run.return_value = Mock(
            returncode=1,
            stderr="Validation failed"
        )
        
        pdf_content = b"%PDF-1.4\ntest content"
        result = self.service.validate_pdfa3(pdf_content)
        
        # Should fall back to basic validation
        assert result["validator"] == "fallback"
        mock_unlink.assert_called_once_with("/tmp/test.pdf")
    
    def test_validate_pdfa3_no_verapdf(self):
        """Test PDF/A-3 validation without veraPDF."""
        # Ensure no veraPDF
        self.service.verapdf_path = None
        
        pdf_content = b"%PDF-1.4\n" + b"x" * 2000 + b"%%EOF"
        result = self.service.validate_pdfa3(pdf_content)
        
        assert result["validator"] == "fallback"
    
    def test_parse_verapdf_result_compliant(self):
        """Test parsing compliant veraPDF result."""
        validation_data = {
            "jobs": [{
                "validationResult": {
                    "isCompliant": True,
                    "profile": "PDF/A-3a",
                    "statement": "PDF file is compliant",
                    "testAssertions": []
                }
            }]
        }
        
        result = self.service._parse_verapdf_result(validation_data)
        
        assert result["is_valid"] is True
        assert result["validator"] == "veraPDF"
        assert result["profile"] == "PDF/A-3a"
        assert len(result["errors"]) == 0
    
    def test_parse_verapdf_result_non_compliant(self):
        """Test parsing non-compliant veraPDF result."""
        validation_data = {
            "jobs": [{
                "validationResult": {
                    "isCompliant": False,
                    "testAssertions": [
                        {"status": "FAILED", "message": "Error 1"},
                        {"status": "WARNING", "message": "Warning 1"}
                    ]
                }
            }]
        }
        
        result = self.service._parse_verapdf_result(validation_data)
        
        assert result["is_valid"] is False
        assert "Error 1" in result["errors"]
        assert "Warning 1" in result["warnings"]
    
    def test_parse_verapdf_result_no_jobs(self):
        """Test parsing veraPDF result with no jobs."""
        validation_data = {"jobs": []}
        
        result = self.service._parse_verapdf_result(validation_data)
        
        assert result["is_valid"] is False
        assert "No validation jobs found" in result["errors"]
    
    def test_validate_comprehensive(self):
        """Test comprehensive validation."""
        # Mock both validations
        with patch.object(self.service, 'validate_pdfa3') as mock_pdfa, \
             patch.object(self.service, 'validate_facturx_structure') as mock_facturx:
            
            mock_pdfa.return_value = {
                "is_valid": True,
                "errors": [],
                "warnings": ["PDF warning"]
            }
            mock_facturx.return_value = {
                "is_valid": True,
                "errors": [],
                "warnings": ["Factur-X warning"]
            }
            
            pdf_content = b"test content"
            result = self.service.validate_comprehensive(pdf_content)
            
            assert result["is_valid"] is True
            assert result["validator"] == "comprehensive"
            assert "PDF warning" in result["warnings"]
            assert "Factur-X warning" in result["warnings"]
            assert "pdfa3_validation" in result
            assert "facturx_validation" in result
    
    def test_validate_comprehensive_mixed_results(self):
        """Test comprehensive validation with mixed results."""
        with patch.object(self.service, 'validate_pdfa3') as mock_pdfa, \
             patch.object(self.service, 'validate_facturx_structure') as mock_facturx:
            
            mock_pdfa.return_value = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            mock_facturx.return_value = {
                "is_valid": False,
                "errors": ["Factur-X error"],
                "warnings": []
            }
            
            pdf_content = b"test content"
            result = self.service.validate_comprehensive(pdf_content)
            
            assert result["is_valid"] is False
            assert "Factur-X error" in result["errors"]
    
    def test_get_validation_info(self):
        """Test getting validation information."""
        result = self.service.get_validation_info()
        
        assert isinstance(result, dict)
        assert "verapdf_available" in result
        assert "verapdf_path" in result
        assert "supported_validations" in result
        assert isinstance(result["supported_validations"], list)
        assert len(result["supported_validations"]) == 3