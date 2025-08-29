import pytest
import io
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from pypdf import PdfReader

from app.services.pdf_generator import PDFGenerator
from app.models.invoice import (
    Invoice, InvoiceLine, Party, Address, TaxRegistration, LegalRegistration,
    VATBreakdown, InvoiceTotals, PaymentTerms, CountryCode, CurrencyCode,
    InvoiceType, VATCategory, PaymentMeans
)
from app.models.business import BusinessConfiguration


class TestPDFGenerator:
    """Test suite for PDFGenerator service"""
    
    @pytest.fixture
    def pdf_generator(self):
        """Create PDFGenerator instance"""
        return PDFGenerator()
    
    @pytest.fixture
    def sample_invoice(self):
        """Create a sample invoice for testing"""
        seller = Party(
            name="Test Company SAS",
            address=Address(
                street="123 Test Street",
                city="Paris",
                postal_code="75001",
                country=CountryCode.FR
            ),
            tax_registration=TaxRegistration(
                vat_number="FR12345678901",
                tax_registration_id="FR12345678901",
                tax_scheme="VAT"
            ),
            legal_registration=LegalRegistration(
                company_id="12345678901234",
                company_legal_form="SAS"
            ),
            contact_name="John Doe",
            contact_email="john@test.com",
            contact_phone="+33123456789"
        )
        
        buyer = Party(
            name="Client Company Ltd",
            address=Address(
                street="456 Client Avenue",
                city="London",
                postal_code="SW1A 1AA",
                country=CountryCode.GB
            ),
            tax_registration=TaxRegistration(
                vat_number="GB123456789",
                tax_registration_id="GB123456789",
                tax_scheme="VAT"
            ),
            contact_name="Jane Smith",
            contact_email="jane@client.com",
            contact_phone="+44123456789"
        )
        
        invoice_lines = [
            InvoiceLine(
                line_id="1",
                item_name="Software License",
                item_description="Annual software license",
                quantity=Decimal("1"),
                unit_price=Decimal("1000.00"),
                vat_rate=Decimal("20.0"),
                vat_category=VATCategory.STANDARD,
                line_total_amount=Decimal("1000.00")
            ),
            InvoiceLine(
                line_id="2",
                item_name="Support Services",
                item_description="Technical support",
                quantity=Decimal("12"),
                unit_price=Decimal("100.00"),
                vat_rate=Decimal("20.0"),
                vat_category=VATCategory.STANDARD,
                line_total_amount=Decimal("1200.00")
            )
        ]
        
        vat_breakdown = [
            VATBreakdown(
                vat_category=VATCategory.STANDARD,
                vat_rate=Decimal("20.0"),
                taxable_amount=Decimal("2200.00"),
                vat_amount=Decimal("440.00")
            )
        ]
        
        totals = InvoiceTotals(
            line_total_amount=Decimal("2200.00"),
            tax_exclusive_amount=Decimal("2200.00"),
            tax_total_amount=Decimal("440.00"),
            tax_inclusive_amount=Decimal("2640.00"),
            payable_amount=Decimal("2640.00")
        )
        
        payment_terms = PaymentTerms(
            payment_means_code=PaymentMeans.BANK_TRANSFER,
            payment_terms_description="Payment due within 30 days"
        )
        
        return Invoice(
            invoice_number="TEST-2024-000001",
            invoice_type=InvoiceType.COMMERCIAL,
            issue_date=date(2024, 1, 15),
            due_date=date(2024, 2, 14),
            currency_code=CurrencyCode.EUR,
            seller=seller,
            buyer=buyer,
            invoice_lines=invoice_lines,
            vat_breakdown=vat_breakdown,
            totals=totals,
            payment_terms=payment_terms,
            order_reference="PO-2024-001"
        )
    
    def test_pdf_generator_initialization(self, pdf_generator):
        """Test PDFGenerator initialization"""
        assert pdf_generator is not None
        assert pdf_generator.business_config is not None
        assert pdf_generator.styles is not None
        assert pdf_generator.brand_colors is not None
        
        # Check brand colors
        assert 'accent' in pdf_generator.brand_colors
        assert 'graphite' in pdf_generator.brand_colors
        assert 'slate' in pdf_generator.brand_colors
        assert 'ink' in pdf_generator.brand_colors
        assert 'muted' in pdf_generator.brand_colors
    
    def test_custom_styles_setup(self, pdf_generator):
        """Test custom paragraph styles setup"""
        # Check that custom styles are added
        assert 'CustomHeader' in pdf_generator.styles
        assert 'CompanyInfo' in pdf_generator.styles
        assert 'InvoiceDetails' in pdf_generator.styles
        assert 'TableHeader' in pdf_generator.styles
        assert 'Total' in pdf_generator.styles
        
        # Check style properties
        header_style = pdf_generator.styles['CustomHeader']
        assert header_style.fontSize == 24
        assert header_style.textColor == pdf_generator.brand_colors['accent']
    
    def test_generate_standard_pdf(self, pdf_generator, sample_invoice):
        """Test standard PDF generation without XML"""
        pdf_bytes = pdf_generator.generate_standard_pdf(sample_invoice)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) >= 1
    
    def test_generate_pdf_with_xml_embedding(self, pdf_generator, sample_invoice):
        """Test PDF generation with XML embedding"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><Invoice></Invoice>'
        
        pdf_bytes = pdf_generator.generate_pdf(sample_invoice, xml_content)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) >= 1
    
    def test_format_party_info_complete(self, pdf_generator, sample_invoice):
        """Test party information formatting with complete data"""
        party_info = pdf_generator._format_party_info(sample_invoice.seller, "TEST PARTY")
        
        assert "TEST PARTY" in party_info
        assert sample_invoice.seller.name in party_info
        assert sample_invoice.seller.address.street in party_info
        assert sample_invoice.seller.address.city in party_info
        assert sample_invoice.seller.tax_registration.vat_number in party_info
    
    def test_format_party_info_minimal(self, pdf_generator):
        """Test party information formatting with minimal data"""
        minimal_address = Address(
            street="123 Main St",
            city="Test City",
            postal_code="12345",
            country=CountryCode.FR
        )
        minimal_party = Party(
            name="Minimal Party",
            address=minimal_address,
            tax_registration=None
        )
        
        party_info = pdf_generator._format_party_info(minimal_party, "MINIMAL")
        
        assert "MINIMAL" in party_info
        assert "Minimal Party" in party_info
    
    def test_add_header(self, pdf_generator, sample_invoice):
        """Test header addition to PDF story"""
        story = []
        pdf_generator._add_header(story, sample_invoice)
        
        assert len(story) > 0
        # Should have company name and invoice title
        assert len(story) >= 3  # Company name, invoice title, spacer
    
    def test_add_parties_info(self, pdf_generator, sample_invoice):
        """Test parties information addition"""
        story = []
        pdf_generator._add_parties_info(story, sample_invoice)
        
        assert len(story) > 0
        # Should have table and spacer
        assert len(story) >= 2
    
    def test_add_invoice_details(self, pdf_generator, sample_invoice):
        """Test invoice details addition"""
        story = []
        pdf_generator._add_invoice_details(story, sample_invoice)
        
        assert len(story) > 0
        # Should have table and spacer
        assert len(story) >= 2
    
    def test_add_line_items_table(self, pdf_generator, sample_invoice):
        """Test line items table addition"""
        story = []
        pdf_generator._add_line_items_table(story, sample_invoice)
        
        assert len(story) > 0
        # Should have table and spacer
        assert len(story) >= 2
    
    def test_add_totals(self, pdf_generator, sample_invoice):
        """Test totals section addition"""
        story = []
        pdf_generator._add_totals(story, sample_invoice)
        
        assert len(story) > 0
        # Should have table and spacer
        assert len(story) >= 2
    
    def test_add_payment_info_with_terms(self, pdf_generator, sample_invoice):
        """Test payment information addition with payment terms"""
        story = []
        pdf_generator._add_payment_info(story, sample_invoice)
        
        assert len(story) > 0
    
    def test_add_payment_info_without_terms(self, pdf_generator, sample_invoice):
        """Test payment information addition without payment terms"""
        sample_invoice.payment_terms = None
        story = []
        pdf_generator._add_payment_info(story, sample_invoice)
        
        # Should not add anything if no payment terms
        assert len(story) == 0
    
    def test_add_footer(self, pdf_generator, sample_invoice):
        """Test footer addition"""
        story = []
        pdf_generator._add_footer(story, sample_invoice)
        
        assert len(story) > 0
        # Should have separator, legal info, and factur-x notice
        assert len(story) >= 4
    
    def test_embed_xml_in_pdf_success(self, pdf_generator, sample_invoice):
        """Test successful XML embedding in PDF"""
        # First generate a standard PDF
        pdf_bytes = pdf_generator.generate_standard_pdf(sample_invoice)
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><Invoice></Invoice>'
        
        # Embed XML
        embedded_pdf = pdf_generator._embed_xml_in_pdf(pdf_bytes, xml_content)
        
        assert isinstance(embedded_pdf, bytes)
        assert len(embedded_pdf) > 0
        
        # Verify it's still a valid PDF
        pdf_reader = PdfReader(io.BytesIO(embedded_pdf))
        assert len(pdf_reader.pages) >= 1
    
    def test_embed_xml_in_pdf_failure(self, pdf_generator):
        """Test XML embedding failure handling"""
        invalid_pdf = b"not a pdf"
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><Invoice></Invoice>'
        
        # Should return original bytes on failure
        result = pdf_generator._embed_xml_in_pdf(invalid_pdf, xml_content)
        assert result == invalid_pdf
    
    @patch('facturx.facturx.generate_facturx_from_binary')
    def test_generate_facturx_pdf_with_library(self, mock_generate_facturx, pdf_generator, sample_invoice):
        """Test Factur-X PDF generation using factur-x library"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><Invoice></Invoice>'
        expected_pdf = b"facturx pdf content"
        mock_generate_facturx.return_value = expected_pdf
        
        result = pdf_generator.generate_facturx_pdf(sample_invoice, xml_content)
        
        assert result == expected_pdf
        mock_generate_facturx.assert_called_once()
    
    @patch('facturx.facturx.generate_facturx_from_binary')
    def test_generate_facturx_pdf_library_fallback(self, mock_generate_facturx, pdf_generator, sample_invoice):
        """Test Factur-X PDF generation fallback when library fails"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?><Invoice></Invoice>'
        mock_generate_facturx.side_effect = Exception("Library error")
        
        result = pdf_generator.generate_facturx_pdf(sample_invoice, xml_content)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
        mock_generate_facturx.assert_called_once()
    
    def test_generate_pdf_with_multiple_vat_rates(self, pdf_generator, sample_invoice):
        """Test PDF generation with multiple VAT rates"""
        # Add another VAT breakdown
        sample_invoice.vat_breakdown.append(
            VATBreakdown(
                vat_category=VATCategory.REDUCED,
                vat_rate=Decimal("10.0"),
                taxable_amount=Decimal("500.00"),
                vat_amount=Decimal("50.00")
            )
        )
        
        pdf_bytes = pdf_generator.generate_standard_pdf(sample_invoice)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) >= 1
    
    def test_generate_pdf_without_optional_fields(self, pdf_generator):
        """Test PDF generation with minimal invoice data"""
        minimal_invoice = Invoice(
            invoice_number="MIN-001",
            invoice_type=InvoiceType.COMMERCIAL,
            issue_date=date(2024, 1, 15),
            currency_code=CurrencyCode.EUR,
            seller=Party(
                name="Minimal Seller",
                address=Address(
                    street="123 Street",
                    city="City",
                    postal_code="12345",
                    country=CountryCode.FR
                )
            ),
            buyer=Party(
                name="Minimal Buyer",
                address=Address(
                    street="456 Avenue",
                    city="Town",
                    postal_code="67890",
                    country=CountryCode.FR
                )
            ),
            invoice_lines=[
                InvoiceLine(
                    line_id="1",
                    item_name="Basic Item",
                    quantity=Decimal("1"),
                    unit_price=Decimal("100.00"),
                    vat_rate=Decimal("20.0"),
                    vat_category=VATCategory.STANDARD,
                    line_total_amount=Decimal("100.00")
                )
            ],
            vat_breakdown=[
                VATBreakdown(
                    vat_category=VATCategory.STANDARD,
                    vat_rate=Decimal("20.0"),
                    taxable_amount=Decimal("100.00"),
                    vat_amount=Decimal("20.00")
                )
            ],
            totals=InvoiceTotals(
                line_total_amount=Decimal("100.00"),
                tax_exclusive_amount=Decimal("100.00"),
                tax_total_amount=Decimal("20.00"),
                tax_inclusive_amount=Decimal("120.00"),
                payable_amount=Decimal("120.00")
            )
        )
        
        pdf_bytes = pdf_generator.generate_standard_pdf(minimal_invoice)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # Verify it's a valid PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
        assert len(pdf_reader.pages) >= 1
    
    @patch('app.services.pdf_generator.get_business_config')
    def test_pdf_generator_with_custom_business_config(self, mock_get_config, sample_invoice):
        """Test PDF generator with custom business configuration"""
        custom_config = BusinessConfiguration(
            company_name="Custom Company",
            trading_name="Custom Trading",
            siren="987654321"
        )
        # Setup mock to return custom config BEFORE creating PDFGenerator
        mock_get_config.return_value = custom_config
        
        pdf_generator = PDFGenerator()
        pdf_bytes = pdf_generator.generate_standard_pdf(sample_invoice)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        mock_get_config.assert_called_once()