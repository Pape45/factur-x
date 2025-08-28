"""Unit tests for PDF generator service."""

import pytest
from datetime import date
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch, MagicMock

from app.services.pdf_generator import PDFGenerator
from app.models.invoice import (
    Invoice, InvoiceLine, Party, Address, InvoiceTotals, VATBreakdown,
    CurrencyCode, CountryCode, VATCategory, InvoiceType
)
from app.models.business import BusinessConfiguration

class TestPDFGenerator:
    """Test cases for PDFGenerator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = PDFGenerator()
        
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
            description="A test product for PDF generation",
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
    
    def test_setup_styles(self):
        """Test PDF styles setup."""
        styles = self.generator.setup_styles(self.business_config)
        
        assert styles is not None
        assert 'title' in styles
        assert 'heading' in styles
        assert 'normal' in styles
        assert 'bold' in styles
        assert 'small' in styles
        assert 'table_header' in styles
        assert 'table_cell' in styles
        
        # Check that primary color is used
        title_style = styles['title']
        assert hasattr(title_style, 'textColor')
    
    def test_generate_pdf_basic(self):
        """Test basic PDF generation."""
        pdf_bytes = self.generator.generate_pdf(self.invoice, self.business_config)
        
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check PDF header
        assert pdf_bytes.startswith(b'%PDF-')
    
    def test_generate_pdf_with_xml_embedding(self):
        """Test PDF generation with XML embedding."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <CrossIndustryInvoice xmlns="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">
            <ExchangedDocumentContext>
                <TestDocumentContextParameter>
                    <ID>urn:cen.eu:en16931:2017</ID>
                </TestDocumentContextParameter>
            </ExchangedDocumentContext>
        </CrossIndustryInvoice>'''
        
        pdf_bytes = self.generator.generate_pdf_with_xml(
            self.invoice, 
            self.business_config, 
            xml_content
        )
        
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Check PDF header
        assert pdf_bytes.startswith(b'%PDF-')
        
        # The PDF should be larger than without XML (due to embedded content)
        pdf_without_xml = self.generator.generate_pdf(self.invoice, self.business_config)
        assert len(pdf_bytes) > len(pdf_without_xml)
    
    @patch('app.services.pdf_generator.canvas')
    def test_draw_header(self, mock_canvas):
        """Test header drawing."""
        mock_c = MagicMock()
        mock_canvas.Canvas.return_value = mock_c
        
        styles = self.generator.setup_styles(self.business_config)
        
        # This should not raise an exception
        y_position = self.generator.draw_header(
            mock_c, self.invoice, self.business_config, styles, 800
        )
        
        assert isinstance(y_position, (int, float))
        assert y_position < 800  # Should move down from starting position
        
        # Verify some drawing methods were called
        assert mock_c.setFont.called
        assert mock_c.drawString.called or mock_c.drawCentredText.called
    
    @patch('app.services.pdf_generator.canvas')
    def test_draw_parties_info(self, mock_canvas):
        """Test parties information drawing."""
        mock_c = MagicMock()
        mock_canvas.Canvas.return_value = mock_c
        
        styles = self.generator.setup_styles(self.business_config)
        
        y_position = self.generator.draw_parties_info(
            mock_c, self.invoice, styles, 700
        )
        
        assert isinstance(y_position, (int, float))
        assert y_position < 700
        
        # Verify drawing methods were called
        assert mock_c.setFont.called
        assert mock_c.drawString.called
    
    @patch('app.services.pdf_generator.canvas')
    def test_draw_invoice_details(self, mock_canvas):
        """Test invoice details drawing."""
        mock_c = MagicMock()
        mock_canvas.Canvas.return_value = mock_c
        
        styles = self.generator.setup_styles(self.business_config)
        
        y_position = self.generator.draw_invoice_details(
            mock_c, self.invoice, styles, 600
        )
        
        assert isinstance(y_position, (int, float))
        assert y_position < 600
        
        # Verify drawing methods were called
        assert mock_c.setFont.called
        assert mock_c.drawString.called
    
    @patch('app.services.pdf_generator.canvas')
    def test_draw_line_items(self, mock_canvas):
        """Test line items drawing."""
        mock_c = MagicMock()
        mock_canvas.Canvas.return_value = mock_c
        
        styles = self.generator.setup_styles(self.business_config)
        
        y_position = self.generator.draw_line_items(
            mock_c, self.invoice, styles, 500
        )
        
        assert isinstance(y_position, (int, float))
        assert y_position < 500
        
        # Verify drawing methods were called
        assert mock_c.setFont.called
        assert mock_c.drawString.called
    
    @patch('app.services.pdf_generator.canvas')
    def test_draw_totals(self, mock_canvas):
        """Test totals drawing."""
        mock_c = MagicMock()
        mock_canvas.Canvas.return_value = mock_c
        
        styles = self.generator.setup_styles(self.business_config)
        
        y_position = self.generator.draw_totals(
            mock_c, self.invoice, styles, 400
        )
        
        assert isinstance(y_position, (int, float))
        assert y_position < 400
        
        # Verify drawing methods were called
        assert mock_c.setFont.called
        assert mock_c.drawString.called
    
    @patch('app.services.pdf_generator.canvas')
    def test_draw_payment_info(self, mock_canvas):
        """Test payment information drawing."""
        mock_c = MagicMock()
        mock_canvas.Canvas.return_value = mock_c
        
        styles = self.generator.setup_styles(self.business_config)
        
        y_position = self.generator.draw_payment_info(
            mock_c, self.invoice, self.business_config, styles, 300
        )
        
        assert isinstance(y_position, (int, float))
        assert y_position < 300
        
        # Verify drawing methods were called
        assert mock_c.setFont.called
        assert mock_c.drawString.called
    
    @patch('app.services.pdf_generator.canvas')
    def test_draw_footer(self, mock_canvas):
        """Test footer drawing."""
        mock_c = MagicMock()
        mock_canvas.Canvas.return_value = mock_c
        
        styles = self.generator.setup_styles(self.business_config)
        
        # This should not raise an exception
        self.generator.draw_footer(
            mock_c, self.business_config, styles
        )
        
        # Verify drawing methods were called
        assert mock_c.setFont.called
        assert mock_c.drawString.called or mock_c.drawCentredText.called
    
    def test_format_currency(self):
        """Test currency formatting."""
        # Test EUR formatting
        formatted = self.generator.format_currency(Decimal("123.45"), CurrencyCode.EUR)
        assert "123.45" in formatted
        assert "€" in formatted or "EUR" in formatted
        
        # Test USD formatting
        formatted_usd = self.generator.format_currency(Decimal("123.45"), CurrencyCode.USD)
        assert "123.45" in formatted_usd
        assert "$" in formatted_usd or "USD" in formatted_usd
    
    def test_format_date(self):
        """Test date formatting."""
        test_date = date(2024, 1, 15)
        formatted = self.generator.format_date(test_date)
        
        assert isinstance(formatted, str)
        assert "2024" in formatted
        assert "01" in formatted or "1" in formatted
        assert "15" in formatted
    
    def test_pdf_with_multiple_lines(self):
        """Test PDF generation with multiple invoice lines."""
        # Add more lines to the invoice
        additional_lines = [
            InvoiceLine(
                line_id="2",
                name="Second Product",
                description="Another test product",
                quantity=Decimal("1.00"),
                unit_price=Decimal("50.00"),
                vat_category=VATCategory.STANDARD_RATE,
                vat_rate=Decimal("20.00")
            ),
            InvoiceLine(
                line_id="3",
                name="Third Product",
                description="Yet another test product",
                quantity=Decimal("3.00"),
                unit_price=Decimal("25.00"),
                vat_category=VATCategory.STANDARD_RATE,
                vat_rate=Decimal("20.00")
            )
        ]
        
        multi_line_invoice = Invoice(
            invoice_id="multi-line-invoice",
            invoice_number="FX-2024-0002",
            seller=self.seller,
            buyer=self.buyer,
            lines=self.invoice.lines + additional_lines,
            totals=InvoiceTotals(
                net_total=Decimal("325.00"),
                vat_total=Decimal("65.00"),
                gross_total=Decimal("390.00"),
                vat_breakdown=[VATBreakdown(
                    vat_category=VATCategory.STANDARD_RATE,
                    vat_rate=Decimal("20.00"),
                    taxable_amount=Decimal("325.00"),
                    vat_amount=Decimal("65.00")
                )]
            ),
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
        
        pdf_bytes = self.generator.generate_pdf(multi_line_invoice, self.business_config)
        
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_pdf_with_long_descriptions(self):
        """Test PDF generation with long product descriptions."""
        long_description_line = InvoiceLine(
            line_id="1",
            name="Product with Very Long Name That Might Wrap",
            description="This is a very long description that should test the PDF generator's ability to handle text wrapping and formatting when the content exceeds the normal line length limits.",
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            vat_category=VATCategory.STANDARD_RATE,
            vat_rate=Decimal("20.00")
        )
        
        long_desc_invoice = Invoice(
            invoice_id="long-desc-invoice",
            invoice_number="FX-2024-0003",
            seller=self.seller,
            buyer=self.buyer,
            lines=[long_description_line],
            totals=self.totals,
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
        
        pdf_bytes = self.generator.generate_pdf(long_desc_invoice, self.business_config)
        
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_invalid_xml_embedding(self):
        """Test handling of invalid XML during embedding."""
        invalid_xml = "<invalid>xml<content>without</proper>closing</tags>"
        
        # Should handle gracefully and still produce a PDF
        pdf_bytes = self.generator.generate_pdf_with_xml(
            self.invoice,
            self.business_config,
            invalid_xml
        )
        
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_empty_business_config(self):
        """Test PDF generation with minimal business configuration."""
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
        
        pdf_bytes = self.generator.generate_pdf(self.invoice, minimal_config)
        
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0