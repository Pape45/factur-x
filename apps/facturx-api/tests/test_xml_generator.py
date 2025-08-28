"""Unit tests for XML generator service."""

import pytest
from datetime import date
from decimal import Decimal
from xml.etree import ElementTree as ET

from app.services.xml_generator import XMLGenerator
from app.models.invoice import (
    Invoice, InvoiceLine, Party, Address, InvoiceTotals, VATBreakdown,
    CurrencyCode, CountryCode, VATCategory, InvoiceType
)

class TestXMLGenerator:
    """Test cases for XMLGenerator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.generator = XMLGenerator()
        
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
            description="A test product for XML generation",
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
    
    def test_generate_xml_basic_structure(self):
        """Test basic XML structure generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        
        assert xml_content is not None
        assert isinstance(xml_content, str)
        assert len(xml_content) > 0
        
        # Parse XML to verify structure
        root = ET.fromstring(xml_content)
        
        # Check root element
        assert root.tag.endswith('CrossIndustryInvoice')
        
        # Check main sections
        exchange_context = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ExchangedDocumentContext')
        assert exchange_context is not None
        
        document_header = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ExchangedDocument')
        assert document_header is not None
        
        supply_chain = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SupplyChainTradeTransaction')
        assert supply_chain is not None
    
    def test_exchange_context_generation(self):
        """Test exchange context generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find exchange context
        context = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ExchangedDocumentContext')
        assert context is not None
        
        # Check business process specified document context parameter
        business_process = context.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}BusinessProcessSpecifiedDocumentContextParameter')
        assert business_process is not None
        
        # Check guideline specified document context parameter
        guideline = context.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}GuidelineSpecifiedDocumentContextParameter')
        assert guideline is not None
        
        guideline_id = guideline.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}ID')
        assert guideline_id is not None
        assert 'urn:cen.eu:en16931:2017' in guideline_id.text
    
    def test_document_header_generation(self):
        """Test document header generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find document header
        document = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ExchangedDocument')
        assert document is not None
        
        # Check invoice number
        invoice_id = document.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}ID')
        assert invoice_id is not None
        assert invoice_id.text == self.invoice.invoice_number
        
        # Check type code
        type_code = document.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}TypeCode')
        assert type_code is not None
        assert type_code.text == "380"  # Commercial invoice
        
        # Check issue date
        issue_date = document.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}IssueDateTime')
        assert issue_date is not None
    
    def test_seller_party_generation(self):
        """Test seller party information generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find seller party
        seller_party = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SellerTradeParty')
        assert seller_party is not None
        
        # Check seller name
        seller_name = seller_party.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}Name')
        assert seller_name is not None
        assert seller_name.text == self.seller.name
        
        # Check seller address
        postal_address = seller_party.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}PostalTradeAddress')
        assert postal_address is not None
        
        # Check VAT registration
        vat_registration = seller_party.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTaxRegistration')
        assert vat_registration is not None
        
        vat_id = vat_registration.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}ID')
        assert vat_id is not None
        assert vat_id.text == self.seller.vat_id
    
    def test_buyer_party_generation(self):
        """Test buyer party information generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find buyer party
        buyer_party = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}BuyerTradeParty')
        assert buyer_party is not None
        
        # Check buyer name
        buyer_name = buyer_party.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}Name')
        assert buyer_name is not None
        assert buyer_name.text == self.buyer.name
        
        # Check buyer address
        postal_address = buyer_party.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}PostalTradeAddress')
        assert postal_address is not None
    
    def test_line_items_generation(self):
        """Test line items generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find line items
        line_items = root.findall('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}IncludedSupplyChainTradeLineItem')
        assert len(line_items) == len(self.invoice.lines)
        
        line_item = line_items[0]
        
        # Check line ID
        line_id = line_item.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}AssociatedDocumentLineDocument/{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}LineID')
        assert line_id is not None
        assert line_id.text == self.invoice_line.line_id
        
        # Check product name
        product_name = line_item.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTradeProduct/{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}Name')
        assert product_name is not None
        assert product_name.text == self.invoice_line.name
        
        # Check quantity
        quantity = line_item.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}BilledQuantity')
        assert quantity is not None
        assert Decimal(quantity.text) == self.invoice_line.quantity
    
    def test_monetary_totals_generation(self):
        """Test monetary totals generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find monetary summation
        monetary_summation = root.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}SpecifiedTradeSettlementHeaderMonetarySummation')
        assert monetary_summation is not None
        
        # Check net total
        net_total = monetary_summation.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}LineTotalAmount')
        assert net_total is not None
        assert Decimal(net_total.text) == self.totals.net_total
        
        # Check VAT total
        vat_total = monetary_summation.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}TaxTotalAmount')
        assert vat_total is not None
        assert Decimal(vat_total.text) == self.totals.vat_total
        
        # Check gross total
        gross_total = monetary_summation.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}GrandTotalAmount')
        assert gross_total is not None
        assert Decimal(gross_total.text) == self.totals.gross_total
    
    def test_vat_breakdown_generation(self):
        """Test VAT breakdown generation."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find VAT breakdown
        vat_breakdowns = root.findall('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}ApplicableTradeTax')
        assert len(vat_breakdowns) >= 1
        
        vat_breakdown = vat_breakdowns[0]
        
        # Check VAT rate
        vat_rate = vat_breakdown.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}RateApplicablePercent')
        assert vat_rate is not None
        assert Decimal(vat_rate.text) == self.vat_breakdown.vat_rate
        
        # Check taxable amount
        taxable_amount = vat_breakdown.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}BasisAmount')
        assert taxable_amount is not None
        assert Decimal(taxable_amount.text) == self.vat_breakdown.taxable_amount
        
        # Check VAT amount
        vat_amount = vat_breakdown.find('.//{urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100}CalculatedAmount')
        assert vat_amount is not None
        assert Decimal(vat_amount.text) == self.vat_breakdown.vat_amount
    
    def test_xml_validation(self):
        """Test XML validation."""
        xml_content = self.generator.generate_xml(self.invoice)
        
        # Basic validation - should parse without errors
        root = ET.fromstring(xml_content)
        assert root is not None
        
        # Validate using the generator's validation method
        is_valid, errors = self.generator.validate_xml_structure(xml_content)
        assert is_valid, f"XML validation failed: {errors}"
    
    def test_xml_namespaces(self):
        """Test XML namespaces are correctly defined."""
        xml_content = self.generator.generate_xml(self.invoice)
        
        # Check that required namespaces are present
        assert 'xmlns:rsm=' in xml_content
        assert 'xmlns:qdt=' in xml_content
        assert 'xmlns:ram=' in xml_content
        assert 'xmlns:xs=' in xml_content
        assert 'xmlns:udt=' in xml_content
    
    def test_currency_codes(self):
        """Test currency codes in XML."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find currency codes
        currency_elements = root.findall('.//*[@currencyID]')
        assert len(currency_elements) > 0
        
        # All currency codes should match invoice currency
        for element in currency_elements:
            assert element.get('currencyID') == self.invoice.currency.value
    
    def test_date_formatting(self):
        """Test date formatting in XML."""
        xml_content = self.generator.generate_xml(self.invoice)
        root = ET.fromstring(xml_content)
        
        # Find issue date
        issue_date = root.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}IssueDateTime')
        assert issue_date is not None
        
        # Check date format (should be YYYYMMDD)
        date_value = issue_date.find('.//{urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100}DateTimeString')
        assert date_value is not None
        assert len(date_value.text) == 8  # YYYYMMDD format
        assert date_value.text.isdigit()
    
    def test_empty_invoice_lines(self):
        """Test handling of invoice with no lines."""
        empty_invoice = Invoice(
            invoice_id="empty-invoice",
            invoice_number="FX-2024-0002",
            seller=self.seller,
            buyer=self.buyer,
            lines=[],  # Empty lines
            totals=InvoiceTotals(
                net_total=Decimal("0.00"),
                vat_total=Decimal("0.00"),
                gross_total=Decimal("0.00"),
                vat_breakdown=[]
            ),
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
        
        xml_content = self.generator.generate_xml(empty_invoice)
        assert xml_content is not None
        
        # Should still be valid XML
        root = ET.fromstring(xml_content)
        assert root is not None