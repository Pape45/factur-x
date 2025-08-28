"""Unit tests for Factur-X service."""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
from xml.etree import ElementTree as ET

from app.services.facturx_service import FacturXService
from app.models.invoice import (
    Invoice, InvoiceLine, Party, Address, InvoiceTotals, VATBreakdown,
    CurrencyCode, CountryCode, VATCategory, InvoiceType
)
from app.models.business import BusinessConfiguration
from app.utils.exceptions import (
    XMLGenerationError, PDFGenerationError, PDFEmbeddingError,
    ValidationError, FileProcessingError
)

class TestFacturXService:
    """Test cases for FacturXService."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.service = FacturXService()
        
        # Sample business configuration
        self.business_config = BusinessConfiguration(
            company_name="Factur-X Express SAS",
            legal_form="SAS",
            siren="123456789",
            siret="12345678900012",
            vat_number="FR12345678901",
            address=Address(
                street="42 Avenue des Champs-Élysées",
                city="Paris",
                postal_code="75008",
                country_code=CountryCode.FR
            ),
            phone="+33 1 23 45 67 89",
            email="contact@facturx-express.fr",
            website="https://facturx-express.fr",
            iban="FR1420041010050500013M02606",
            bic="PSSTFRPPPAR",
            default_currency=CurrencyCode.EUR,
            default_vat_rate=Decimal("20.00"),
            invoice_number_format="FX-{YYYY}-{seq:04d}",
            primary_color="#2F6DF3",
            secondary_color="#1E40AF",
            accent_color="#3B82F6"
        )
        
        # Sample invoice data
        self.seller_address = Address(
            street="42 Avenue des Champs-Élysées",
            city="Paris",
            postal_code="75008",
            country_code=CountryCode.FR
        )
        
        self.seller = Party(
            name="Factur-X Express SAS",
            address=self.seller_address,
            vat_id="FR12345678901",
            legal_registration="123456789"
        )
        
        self.buyer_address = Address(
            street="123 Test Street",
            city="Test City",
            postal_code="12345",
            country_code=CountryCode.FR
        )
        
        self.buyer = Party(
            name="Test Buyer Company",
            address=self.buyer_address,
            vat_id="FR98765432109"
        )
        
        self.invoice_line = InvoiceLine(
            line_id="1",
            name="Test Product",
            description="A test product for Factur-X generation",
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            vat_category=VATCategory.STANDARD_RATE,
            vat_rate=Decimal("20.00")
        )
        
        self.vat_breakdown = VATBreakdown(
            vat_category=VATCategory.STANDARD_RATE,
            vat_rate=Decimal("20.00"),
            taxable_amount=Decimal("200.00"),
            vat_amount=Decimal("40.00")
        )
        
        self.totals = InvoiceTotals(
            net_total=Decimal("200.00"),
            vat_total=Decimal("40.00"),
            gross_total=Decimal("240.00"),
            vat_breakdown=[self.vat_breakdown]
        )
        
        self.invoice = Invoice(
            invoice_id="test-invoice-1",
            invoice_number="FX-2024-0001",
            seller=self.seller,
            buyer=self.buyer,
            lines=[self.invoice_line],
            totals=self.totals,
            issue_date=date(2024, 1, 15),
            due_date=date(2024, 2, 15),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
    
    def test_generate_facturx_invoice(self):
        """Test complete Factur-X invoice generation."""
        result = self.service.generate_facturx_invoice(self.invoice, self.business_config)
        
        assert result is not None
        assert "pdf_bytes" in result
        assert "xml_content" in result
        assert "metadata" in result
        
        # Check PDF bytes
        pdf_bytes = result["pdf_bytes"]
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF-')
        
        # Check XML content
        xml_content = result["xml_content"]
        assert isinstance(xml_content, str)
        assert len(xml_content) > 0
        assert '<?xml' in xml_content
        assert 'CrossIndustryInvoice' in xml_content
        
        # Check metadata
        metadata = result["metadata"]
        assert "invoice_number" in metadata
        assert "generation_date" in metadata
        assert "file_size" in metadata
        assert "xml_size" in metadata
        assert metadata["invoice_number"] == self.invoice.invoice_number
    
    def test_generate_xml_only(self):
        """Test XML-only generation."""
        xml_content = self.service.generate_xml_only(self.invoice)
        
        assert xml_content is not None
        assert isinstance(xml_content, str)
        assert len(xml_content) > 0
        assert '<?xml' in xml_content
        assert 'CrossIndustryInvoice' in xml_content
        
        # Verify XML is valid
        root = ET.fromstring(xml_content)
        assert root is not None
    
    def test_generate_pdf_only(self):
        """Test PDF-only generation."""
        pdf_bytes = self.service.generate_pdf_only(self.invoice, self.business_config)
        
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF-')
    
    @patch('app.services.facturx_service.facturx')
    def test_validate_facturx_file(self, mock_facturx):
        """Test Factur-X file validation."""
        # Mock facturx validation
        mock_facturx.check_facturx_xsd.return_value = True
        mock_facturx.get_level.return_value = 'EN 16931'
        
        # Create sample PDF bytes
        sample_pdf = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'
        
        result = self.service.validate_facturx_file(sample_pdf)
        
        assert result is not None
        assert "is_valid" in result
        assert "level" in result
        assert "errors" in result
        assert "warnings" in result
    
    @patch('app.services.facturx_service.facturx')
    def test_extract_xml_from_pdf(self, mock_facturx):
        """Test XML extraction from PDF."""
        # Mock XML content
        mock_xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <CrossIndustryInvoice xmlns="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">
            <ExchangedDocumentContext>
                <TestDocumentContextParameter>
                    <ID>urn:cen.eu:en16931:2017</ID>
                </TestDocumentContextParameter>
            </ExchangedDocumentContext>
        </CrossIndustryInvoice>'''
        
        mock_facturx.get_facturx_xml_from_pdf.return_value = mock_xml
        
        # Create sample PDF bytes
        sample_pdf = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'
        
        extracted_xml = self.service.extract_xml_from_pdf(sample_pdf)
        
        assert extracted_xml is not None
        assert isinstance(extracted_xml, str)
        assert 'CrossIndustryInvoice' in extracted_xml
    
    def test_convert_pdf_to_facturx(self):
        """Test converting regular PDF to Factur-X."""
        # Create sample PDF bytes
        sample_pdf = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'
        
        result = self.service.convert_pdf_to_facturx(
            sample_pdf, 
            self.invoice, 
            self.business_config
        )
        
        assert result is not None
        assert "pdf_bytes" in result
        assert "xml_content" in result
        assert "metadata" in result
        
        # Check that result contains valid data
        pdf_bytes = result["pdf_bytes"]
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_batch_generate_invoices(self):
        """Test batch invoice generation."""
        # Create multiple invoices
        invoices = []
        for i in range(3):
            invoice = Invoice(
                invoice_id=f"batch-invoice-{i+1}",
                invoice_number=f"FX-2024-{i+1:04d}",
                seller=self.seller,
                buyer=self.buyer,
                lines=[self.invoice_line],
                totals=self.totals,
                issue_date=date.today(),
                due_date=date.today(),
                currency=CurrencyCode.EUR,
                invoice_type=InvoiceType.COMMERCIAL_INVOICE
            )
            invoices.append(invoice)
        
        results = self.service.batch_generate_invoices(invoices, self.business_config)
        
        assert results is not None
        assert "results" in results
        assert "summary" in results
        
        # Check results
        batch_results = results["results"]
        assert len(batch_results) == 3
        
        for result in batch_results:
            assert "invoice_id" in result
            assert "success" in result
            if result["success"]:
                assert "pdf_bytes" in result
                assert "xml_content" in result
        
        # Check summary
        summary = results["summary"]
        assert "total_processed" in summary
        assert "successful" in summary
        assert "failed" in summary
        assert summary["total_processed"] == 3
    
    @patch('app.services.facturx_service.XMLGenerator')
    def test_xml_generation_error_handling(self, mock_xml_generator):
        """Test XML generation error handling."""
        # Mock XML generator to raise an exception
        mock_instance = MagicMock()
        mock_instance.generate_xml.side_effect = Exception("XML generation failed")
        mock_xml_generator.return_value = mock_instance
        
        with pytest.raises(XMLGenerationError):
            self.service.generate_xml_only(self.invoice)
    
    @patch('app.services.facturx_service.PDFGenerator')
    def test_pdf_generation_error_handling(self, mock_pdf_generator):
        """Test PDF generation error handling."""
        # Mock PDF generator to raise an exception
        mock_instance = MagicMock()
        mock_instance.generate_pdf.side_effect = Exception("PDF generation failed")
        mock_pdf_generator.return_value = mock_instance
        
        with pytest.raises(PDFGenerationError):
            self.service.generate_pdf_only(self.invoice, self.business_config)
    
    @patch('app.services.facturx_service.PDFGenerator')
    def test_pdf_embedding_error_handling(self, mock_pdf_generator):
        """Test PDF embedding error handling."""
        # Mock PDF generator to raise an exception during XML embedding
        mock_instance = MagicMock()
        mock_instance.generate_pdf.return_value = b'valid pdf'
        mock_instance.generate_pdf_with_xml.side_effect = Exception("Embedding failed")
        mock_pdf_generator.return_value = mock_instance
        
        with pytest.raises(PDFEmbeddingError):
            self.service.generate_facturx_invoice(self.invoice, self.business_config)
    
    def test_invalid_invoice_data(self):
        """Test handling of invalid invoice data."""
        # Create invoice with invalid data
        invalid_invoice = Invoice(
            invoice_id="",  # Empty ID
            invoice_number="",  # Empty number
            seller=self.seller,
            buyer=self.buyer,
            lines=[],  # No lines
            totals=self.totals,
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
        
        # Should handle gracefully or raise appropriate error
        try:
            result = self.service.generate_facturx_invoice(invalid_invoice, self.business_config)
            # If it succeeds, check that result is still valid
            assert result is not None
        except (XMLGenerationError, PDFGenerationError, ValidationError):
            # These are acceptable exceptions for invalid data
            pass
    
    def test_missing_business_config(self):
        """Test handling of missing business configuration."""
        minimal_config = BusinessConfiguration(
            company_name="Test Company",
            address=Address(
                street="Test Street",
                city="Test City",
                postal_code="12345",
                country_code=CountryCode.FR
            ),
            default_currency=CurrencyCode.EUR,
            default_vat_rate=Decimal("20.00"),
            invoice_number_format="INV-{seq}"
        )
        
        # Should still work with minimal configuration
        result = self.service.generate_facturx_invoice(self.invoice, minimal_config)
        
        assert result is not None
        assert "pdf_bytes" in result
        assert "xml_content" in result
    
    def test_large_invoice_handling(self):
        """Test handling of invoices with many line items."""
        # Create invoice with many lines
        many_lines = []
        for i in range(50):
            line = InvoiceLine(
                line_id=str(i+1),
                name=f"Product {i+1}",
                description=f"Description for product {i+1}",
                quantity=Decimal("1.00"),
                unit_price=Decimal("10.00"),
                vat_category=VATCategory.STANDARD_RATE,
                vat_rate=Decimal("20.00")
            )
            many_lines.append(line)
        
        large_invoice = Invoice(
            invoice_id="large-invoice",
            invoice_number="FX-2024-LARGE",
            seller=self.seller,
            buyer=self.buyer,
            lines=many_lines,
            totals=InvoiceTotals(
                net_total=Decimal("500.00"),
                vat_total=Decimal("100.00"),
                gross_total=Decimal("600.00"),
                vat_breakdown=[VATBreakdown(
                    vat_category=VATCategory.STANDARD_RATE,
                    vat_rate=Decimal("20.00"),
                    taxable_amount=Decimal("500.00"),
                    vat_amount=Decimal("100.00")
                )]
            ),
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
        
        result = self.service.generate_facturx_invoice(large_invoice, self.business_config)
        
        assert result is not None
        assert "pdf_bytes" in result
        assert "xml_content" in result
        
        # Check that the result is larger due to more content
        pdf_bytes = result["pdf_bytes"]
        assert len(pdf_bytes) > 1000  # Should be substantial
    
    def test_different_currencies(self):
        """Test handling of different currencies."""
        # Test with USD
        usd_invoice = Invoice(
            invoice_id="usd-invoice",
            invoice_number="FX-2024-USD",
            seller=self.seller,
            buyer=self.buyer,
            lines=[self.invoice_line],
            totals=self.totals,
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.USD,  # Different currency
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
        
        result = self.service.generate_facturx_invoice(usd_invoice, self.business_config)
        
        assert result is not None
        assert "pdf_bytes" in result
        assert "xml_content" in result
        
        # Check that USD is mentioned in the XML
        xml_content = result["xml_content"]
        assert "USD" in xml_content
    
    def test_metadata_generation(self):
        """Test metadata generation."""
        result = self.service.generate_facturx_invoice(self.invoice, self.business_config)
        metadata = result["metadata"]
        
        # Check required metadata fields
        required_fields = [
            "invoice_number", "generation_date", "file_size", 
            "xml_size", "facturx_level", "generator_info"
        ]
        
        for field in required_fields:
            assert field in metadata, f"Missing metadata field: {field}"
        
        # Check data types
        assert isinstance(metadata["invoice_number"], str)
        assert isinstance(metadata["file_size"], int)
        assert isinstance(metadata["xml_size"], int)
        assert metadata["file_size"] > 0
        assert metadata["xml_size"] > 0