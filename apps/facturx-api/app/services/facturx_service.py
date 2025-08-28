import io
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from facturx import generate_from_file, get_level, check_facturx_xsd, get_facturx_xml_from_pdf
from facturx.facturx import generate_facturx_from_binary
from lxml import etree

from ..models.invoice import Invoice
from .xml_generator import XMLGenerator
from .pdf_generator import PDFGenerator


class FacturXService:
    """Service for generating Factur-X compliant invoices"""
    
    def __init__(self):
        self.xml_generator = XMLGenerator()
        self.pdf_generator = PDFGenerator()
    
    def generate_facturx_invoice(
        self, 
        invoice: Invoice,
        facturx_level: str = "basic"
    ) -> Tuple[bytes, str, Dict[str, Any]]:
        """
        Generate complete Factur-X invoice with PDF and embedded XML
        
        Args:
            invoice: Invoice data model
            facturx_level: Factur-X conformance level (minimum, basic, comfort, extended)
            
        Returns:
            Tuple of (pdf_bytes, xml_content, validation_result)
        """
        try:
            # Generate XML content
            xml_content = self.xml_generator.generate_cii_xml(invoice)
            
            # Validate XML structure
            xml_validation = self.xml_generator.validate_xml_structure(xml_content)
            
            if not xml_validation['is_valid']:
                raise ValueError(f"Invalid XML structure: {xml_validation['errors']}")
            
            # Generate PDF with embedded XML
            pdf_bytes = self.pdf_generator.generate_facturx_pdf(invoice, xml_content)
            
            # Validate the complete Factur-X file
            validation_result = self.validate_facturx_file(pdf_bytes)
            
            return pdf_bytes, xml_content, validation_result
            
        except Exception as e:
            raise Exception(f"Failed to generate Factur-X invoice: {str(e)}")
    
    def generate_xml_only(self, invoice: Invoice) -> str:
        """
        Generate only the XML content for an invoice
        
        Args:
            invoice: Invoice data model
            
        Returns:
            XML content as string
        """
        return self.xml_generator.generate_cii_xml(invoice)
    
    def generate_pdf_only(self, invoice: Invoice) -> bytes:
        """
        Generate only the PDF content for an invoice (without XML embedding)
        
        Args:
            invoice: Invoice data model
            
        Returns:
            PDF content as bytes
        """
        return self.pdf_generator.generate_standard_pdf(invoice)
    
    def validate_facturx_file(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Validate a Factur-X PDF file
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Validation result dictionary
        """
        try:
            # Create temporary file-like object
            pdf_file = io.BytesIO(pdf_bytes)
            
            validation_result = {
                'is_valid': True,
                'facturx_level': None,
                'has_xml': False,
                'xml_valid': False,
                'errors': [],
                'warnings': []
            }
            
            try:
                # Extract XML from PDF first - get_facturx_xml_from_pdf returns (filename, xml_bytes)
                xml_result = get_facturx_xml_from_pdf(pdf_file)
                if xml_result and xml_result[1]:  # Check if we have xml_bytes
                    xml_content = xml_result[1]  # Extract the XML bytes
                    validation_result['has_xml'] = True
                    
                    # Parse XML content to etree using lxml
                    try:
                        xml_etree = etree.fromstring(xml_content)
                        facturx_level = get_level(xml_etree)
                        if facturx_level:
                            validation_result['facturx_level'] = facturx_level
                            validation_result['xml_valid'] = True
                        else:
                            validation_result['warnings'].append("Could not determine Factur-X level")
                            validation_result['xml_valid'] = True  # XML exists but level unknown
                    except Exception as xml_error:
                        validation_result['xml_valid'] = False
                        validation_result['errors'].append(f"XML parsing failed: {str(xml_error)}")
                        validation_result['is_valid'] = False
                else:
                    validation_result['warnings'].append("No Factur-X XML found in PDF")
                    
            except Exception as level_error:
                validation_result['errors'].append(f"Failed to determine Factur-X level: {str(level_error)}")
                validation_result['is_valid'] = False
            
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'facturx_level': None,
                'has_xml': False,
                'xml_valid': False,
                'errors': [f"Validation failed: {str(e)}"],
                'warnings': []
            }
    
    def extract_xml_from_facturx(self, pdf_bytes: bytes) -> Optional[str]:
        """
        Extract XML content from a Factur-X PDF file
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            XML content as string, or None if not found
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            
            # Extract XML using factur-x library - returns (filename, xml_bytes)
            xml_result = get_facturx_xml_from_pdf(pdf_file)
            if xml_result and xml_result[1]:
                return xml_result[1].decode('utf-8') if isinstance(xml_result[1], bytes) else xml_result[1]
            return None
            
        except Exception as e:
            print(f"Failed to extract XML from Factur-X file: {e}")
            return None
    
    def convert_pdf_to_facturx(
        self, 
        pdf_bytes: bytes, 
        invoice: Invoice,
        facturx_level: str = "basic"
    ) -> bytes:
        """
        Convert a standard PDF to Factur-X by adding XML
        
        Args:
            pdf_bytes: Original PDF content
            invoice: Invoice data for XML generation
            facturx_level: Factur-X conformance level
            
        Returns:
            Factur-X compliant PDF with embedded XML
        """
        try:
            # Generate XML content
            xml_content = self.xml_generator.generate_cii_xml(invoice)
            
            # Embed XML in the existing PDF
            facturx_pdf = self.pdf_generator._embed_xml_in_pdf(pdf_bytes, xml_content)
            
            return facturx_pdf
            
        except Exception as e:
            raise Exception(f"Failed to convert PDF to Factur-X: {str(e)}")
    
    def get_supported_levels(self) -> list[str]:
        """
        Get list of supported Factur-X conformance levels
        
        Returns:
            List of supported levels
        """
        return ["minimum", "basic", "comfort", "extended"]
    
    def get_facturx_info(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Get comprehensive information about a Factur-X file
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Dictionary with file information
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            
            info = {
                'is_facturx': False,
                'level': None,
                'has_xml': False,
                'file_size': len(pdf_bytes),
                'created_at': datetime.now().isoformat(),
                'validation': None
            }
            
            # Check Factur-X level
            try:
                xml_result = get_facturx_xml_from_pdf(pdf_file)
                if xml_result and xml_result[1]:
                    xml_content = xml_result[1]  # Extract the XML bytes
                    info['has_xml'] = True
                    try:
                        xml_etree = etree.fromstring(xml_content)
                        level = get_level(xml_etree)
                        if level:
                            info['is_facturx'] = True
                            info['level'] = level
                    except Exception:
                        pass
            except Exception:
                pass
            
            # Add validation results
            info['validation'] = self.validate_facturx_file(pdf_bytes)
            
            return info
            
        except Exception as e:
            return {
                'is_facturx': False,
                'level': None,
                'has_xml': False,
                'file_size': len(pdf_bytes) if pdf_bytes else 0,
                'created_at': datetime.now().isoformat(),
                'validation': {
                    'is_valid': False,
                    'errors': [f"Failed to analyze file: {str(e)}"]
                }
            }
    
    def create_sample_invoice(self) -> Invoice:
        """
        Create a sample invoice for testing purposes
        
        Returns:
            Sample Invoice object
        """
        from ..services.invoice_service import InvoiceService
        
        invoice_service = InvoiceService()
        return invoice_service.create_sample_invoice()
    
    def batch_generate_facturx(
        self, 
        invoices: list[Invoice],
        facturx_level: str = "basic"
    ) -> list[Dict[str, Any]]:
        """
        Generate multiple Factur-X invoices in batch
        
        Args:
            invoices: List of invoice data models
            facturx_level: Factur-X conformance level
            
        Returns:
            List of results with PDF bytes, XML content, and validation
        """
        results = []
        
        for i, invoice in enumerate(invoices):
            try:
                pdf_bytes, xml_content, validation = self.generate_facturx_invoice(
                    invoice, facturx_level
                )
                
                results.append({
                    'index': i,
                    'invoice_number': invoice.invoice_number,
                    'success': True,
                    'pdf_bytes': pdf_bytes,
                    'xml_content': xml_content,
                    'validation': validation,
                    'error': None
                })
                
            except Exception as e:
                results.append({
                    'index': i,
                    'invoice_number': getattr(invoice, 'invoice_number', f'Invoice_{i}'),
                    'success': False,
                    'pdf_bytes': None,
                    'xml_content': None,
                    'validation': None,
                    'error': str(e)
                })
        
        return results