"""Tests for XML generator service."""

import pytest
from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import fromstring
from app.services.xml_generator import XMLGenerator
from app.models.invoice import (
    Invoice, InvoiceLine, Party, Address, TaxRegistration, VATBreakdown,
    InvoiceTotals, PaymentTerms, BankAccount,
    CurrencyCode, CountryCode, VATCategory, InvoiceType, PaymentMeans
)


class TestXMLGenerator:
    """Test cases for XMLGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = XMLGenerator()
        self.sample_invoice = self._create_sample_invoice()
    
    def _create_sample_invoice(self) -> Invoice:
        """Create a sample invoice for testing."""
        seller_address = Address(
            street="42 Avenue des Champs-Élysées",
            city="Paris",
            postal_code="75008",
            country=CountryCode.FR
        )
        
        buyer_address = Address(
            street="123 Rue de la Paix",
            city="Lyon",
            postal_code="69000",
            country=CountryCode.FR
        )
        
        seller = Party(
            name="Factur-X Express SAS",
            address=seller_address,
            tax_registration=TaxRegistration(vat_number="FR12345678901"),
            contact_email="contact@facturx-express.fr",
            contact_phone="+33123456789"
        )
        
        buyer = Party(
            name="Example Client SARL",
            address=buyer_address,
            tax_registration=TaxRegistration(vat_number="FR98765432109")
        )
        
        invoice_line = InvoiceLine(
            line_id="1",
            item_name="Factur-X Service",
            item_description="Professional Factur-X generation service",
            quantity=Decimal("1"),
            unit_price=Decimal("100.00"),
            line_total_amount=Decimal("100.00"),
            vat_category=VATCategory.STANDARD,
            vat_rate=Decimal("20.0")
        )
        
        vat_breakdown = VATBreakdown(
            vat_category=VATCategory.STANDARD,
            vat_rate=Decimal("20.0"),
            taxable_amount=Decimal("100.00"),
            vat_amount=Decimal("20.00")
        )
        
        totals = InvoiceTotals(
            line_total_amount=Decimal("100.00"),
            tax_exclusive_amount=Decimal("100.00"),
            tax_total_amount=Decimal("20.00"),
            tax_inclusive_amount=Decimal("120.00"),
            payable_amount=Decimal("120.00")
        )
        
        bank_account = BankAccount(
            iban="FR1420041010050500013M02606",
            bic="PSSTFRPPPAR",
            account_name="Factur-X Express SAS",
            bank_name="La Banque Postale"
        )
        
        payment_terms = PaymentTerms(
            payment_means_code=PaymentMeans.BANK_TRANSFER,
            payment_terms_description="Payment due within 30 days",
            due_date=date(2024, 2, 14),
            payment_reference="REF-2024-001",
            bank_account=bank_account
        )
        
        return Invoice(
            invoice_number="FX-2024-000001",
            invoice_type=InvoiceType.COMMERCIAL,
            issue_date=date(2024, 1, 15),
            due_date=date(2024, 2, 14),
            currency_code=CurrencyCode.EUR,
            seller=seller,
            buyer=buyer,
            invoice_lines=[invoice_line],
            vat_breakdown=[vat_breakdown],
            totals=totals,
            payment_terms=payment_terms,
            order_reference="PO-2024-001",
            contract_reference="CONTRACT-2024-001",
            invoice_note="Thank you for your business!"
        )
    
    def test_init(self):
        """Test XMLGenerator initialization."""
        assert isinstance(self.generator, XMLGenerator)
        assert isinstance(self.generator.namespaces, dict)
        assert 'rsm' in self.generator.namespaces
        assert 'ram' in self.generator.namespaces
        assert 'udt' in self.generator.namespaces
    
    def test_generate_cii_xml_basic(self):
        """Test basic CII XML generation."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        
        assert isinstance(xml_content, str)
        assert '<?xml version="1.0" ?>' in xml_content
        assert 'rsm:CrossIndustryInvoice' in xml_content
        assert 'FX-2024-000001' in xml_content  # Invoice number
        assert 'Factur-X Express SAS' in xml_content  # Seller name
        assert 'Example Client SARL' in xml_content  # Buyer name
    
    def test_generate_cii_xml_structure(self):
        """Test CII XML structure and required elements."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check namespaces - ElementTree includes full namespace URI in tag
        expected_tag = '{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice'
        assert root.tag == expected_tag
        
        # Check main sections
        context = root.find('.//rsm:ExchangedDocumentContext', self.generator.namespaces)
        assert context is not None
        
        document = root.find('.//rsm:ExchangedDocument', self.generator.namespaces)
        assert document is not None
        
        transaction = root.find('.//rsm:SupplyChainTradeTransaction', self.generator.namespaces)
        assert transaction is not None
    
    def test_add_exchange_context(self):
        """Test ExchangedDocumentContext section."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check business process
        business_process_id = root.find(
            './/ram:BusinessProcessSpecifiedDocumentContextParameter/ram:ID',
            self.generator.namespaces
        )
        assert business_process_id is not None
        assert business_process_id.text == 'A1'
        
        # Check guideline
        guideline_id = root.find(
            './/ram:GuidelineSpecifiedDocumentContextParameter/ram:ID',
            self.generator.namespaces
        )
        assert guideline_id is not None
        assert 'urn:cen.eu:en16931:2017' in guideline_id.text
    
    def test_add_exchanged_document(self):
        """Test ExchangedDocument section."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check invoice number
        invoice_id = root.find('.//rsm:ExchangedDocument/ram:ID', self.generator.namespaces)
        assert invoice_id is not None
        assert invoice_id.text == 'FX-2024-000001'
        
        # Check type code
        type_code = root.find('.//rsm:ExchangedDocument/ram:TypeCode', self.generator.namespaces)
        assert type_code is not None
        assert type_code.text == '380'
        
        # Check issue date
        issue_date = root.find(
            './/rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString',
            self.generator.namespaces
        )
        assert issue_date is not None
        assert issue_date.text == '20240115'
        assert issue_date.get('format') == '102'
    
    def test_add_line_item(self):
        """Test line item generation."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check line item exists
        line_item = root.find('.//ram:IncludedSupplyChainTradeLineItem', self.generator.namespaces)
        assert line_item is not None
        
        # Check line ID
        line_id = root.find(
            './/ram:IncludedSupplyChainTradeLineItem/ram:AssociatedDocumentLineDocument/ram:LineID',
            self.generator.namespaces
        )
        assert line_id is not None
        assert line_id.text == '1'
        
        # Check product name
        product_name = root.find(
            './/ram:IncludedSupplyChainTradeLineItem/ram:SpecifiedTradeProduct/ram:Name',
            self.generator.namespaces
        )
        assert product_name is not None
        assert product_name.text == 'Factur-X Service'
        
        # Check unit price
        unit_price = root.find(
            './/ram:SpecifiedLineTradeAgreement/ram:NetPriceProductTradePrice/ram:ChargeAmount',
            self.generator.namespaces
        )
        assert unit_price is not None
        assert unit_price.text == '100.00'
        assert unit_price.get('currencyID') == 'EUR'
        
        # Check quantity
        quantity = root.find(
            './/ram:SpecifiedLineTradeDelivery/ram:BilledQuantity',
            self.generator.namespaces
        )
        assert quantity is not None
        assert quantity.text == '1'
        
        # Check VAT
        vat_rate = root.find(
            './/ram:SpecifiedLineTradeSettlement/ram:ApplicableTradeTax/ram:RateApplicablePercent',
            self.generator.namespaces
        )
        assert vat_rate is not None
        assert vat_rate.text == '20.0'
    
    def test_add_header_trade_agreement(self):
        """Test header trade agreement section."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check buyer reference
        buyer_ref = root.find(
            './/ram:ApplicableHeaderTradeAgreement/ram:BuyerReference',
            self.generator.namespaces
        )
        assert buyer_ref is not None
        assert buyer_ref.text == 'PO-2024-001'
        
        # Check seller party
        seller_name = root.find(
            './/ram:SellerTradeParty/ram:Name',
            self.generator.namespaces
        )
        assert seller_name is not None
        assert seller_name.text == 'Factur-X Express SAS'
        
        # Check buyer party
        buyer_name = root.find(
            './/ram:BuyerTradeParty/ram:Name',
            self.generator.namespaces
        )
        assert buyer_name is not None
        assert buyer_name.text == 'Example Client SARL'
        
        # Check contract reference
        contract_ref = root.find(
            './/ram:ContractReferencedDocument/ram:IssuerAssignedID',
            self.generator.namespaces
        )
        assert contract_ref is not None
        assert contract_ref.text == 'CONTRACT-2024-001'
    
    def test_add_trade_party_info(self):
        """Test trade party information generation."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check seller address
        seller_street = root.find(
            './/ram:SellerTradeParty/ram:PostalTradeAddress/ram:LineOne',
            self.generator.namespaces
        )
        assert seller_street is not None
        assert seller_street.text == '42 Avenue des Champs-Élysées'
        
        seller_city = root.find(
            './/ram:SellerTradeParty/ram:PostalTradeAddress/ram:CityName',
            self.generator.namespaces
        )
        assert seller_city is not None
        assert seller_city.text == 'Paris'
        
        seller_country = root.find(
            './/ram:SellerTradeParty/ram:PostalTradeAddress/ram:CountryID',
            self.generator.namespaces
        )
        assert seller_country is not None
        assert seller_country.text == 'FR'
        
        # Check VAT number
        seller_vat = root.find(
            './/ram:SellerTradeParty/ram:SpecifiedTaxRegistration/ram:ID',
            self.generator.namespaces
        )
        assert seller_vat is not None
        assert seller_vat.text == 'FR12345678901'
        assert seller_vat.get('schemeID') == 'VA'
        
        # Check contact info
        seller_email = root.find(
            './/ram:SellerTradeParty/ram:DefinedTradeContact/ram:EmailURIUniversalCommunication/ram:URIID',
            self.generator.namespaces
        )
        assert seller_email is not None
        assert seller_email.text == 'contact@facturx-express.fr'
    
    def test_add_header_trade_settlement(self):
        """Test header trade settlement section."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check currency
        currency = root.find(
            './/ram:ApplicableHeaderTradeSettlement/ram:InvoiceCurrencyCode',
            self.generator.namespaces
        )
        assert currency is not None
        assert currency.text == 'EUR'
        
        # Check VAT breakdown
        vat_amount = root.find(
            './/ram:ApplicableHeaderTradeSettlement/ram:ApplicableTradeTax/ram:CalculatedAmount',
            self.generator.namespaces
        )
        assert vat_amount is not None
        assert vat_amount.text == '20.00'
        assert vat_amount.get('currencyID') == 'EUR'
        
        # Check totals
        line_total = root.find(
            './/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:LineTotalAmount',
            self.generator.namespaces
        )
        assert line_total is not None
        assert line_total.text == '100.00'
        
        tax_total = root.find(
            './/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:TaxTotalAmount',
            self.generator.namespaces
        )
        assert tax_total is not None
        assert tax_total.text == '20.00'
        
        grand_total = root.find(
            './/ram:SpecifiedTradeSettlementHeaderMonetarySummation/ram:GrandTotalAmount',
            self.generator.namespaces
        )
        assert grand_total is not None
        assert grand_total.text == '120.00'
    
    def test_validate_xml_structure_valid(self):
        """Test XML structure validation with valid XML."""
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        result = self.generator.validate_xml_structure(xml_content)
        
        assert result['is_valid'] is True
        assert len(result['errors']) == 0
        assert isinstance(result['warnings'], list)
    
    def test_validate_xml_structure_invalid(self):
        """Test XML structure validation with invalid XML."""
        invalid_xml = "<invalid>not a valid factur-x xml</invalid>"
        result = self.generator.validate_xml_structure(invalid_xml)
        
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
        assert any('Missing required element' in error for error in result['errors'])
    
    def test_validate_xml_structure_malformed(self):
        """Test XML structure validation with malformed XML."""
        malformed_xml = "<invalid>not closed"
        result = self.generator.validate_xml_structure(malformed_xml)
        
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
        assert any('XML parsing error' in error for error in result['errors'])
    
    def test_multiple_invoice_lines(self):
        """Test XML generation with multiple invoice lines."""
        # Add another line to the invoice
        second_line = InvoiceLine(
            line_id="2",
            item_name="Additional Service",
            quantity=Decimal("2"),
            unit_price=Decimal("50.00"),
            line_total_amount=Decimal("100.00"),
            vat_category=VATCategory.STANDARD,
            vat_rate=Decimal("20.0")
        )
        
        self.sample_invoice.invoice_lines.append(second_line)
        
        # Update totals
        self.sample_invoice.totals.line_total_amount = Decimal("200.00")
        self.sample_invoice.totals.tax_exclusive_amount = Decimal("200.00")
        self.sample_invoice.totals.tax_total_amount = Decimal("40.00")
        self.sample_invoice.totals.tax_inclusive_amount = Decimal("240.00")
        self.sample_invoice.totals.payable_amount = Decimal("240.00")
        
        # Update VAT breakdown
        self.sample_invoice.vat_breakdown[0].taxable_amount = Decimal("200.00")
        self.sample_invoice.vat_breakdown[0].vat_amount = Decimal("40.00")
        
        xml_content = self.generator.generate_cii_xml(self.sample_invoice)
        root = fromstring(xml_content)
        
        # Check that both lines are present
        line_items = root.findall('.//ram:IncludedSupplyChainTradeLineItem', self.generator.namespaces)
        assert len(line_items) == 2
        
        # Check line IDs
        line_ids = []
        for item in line_items:
            line_id = item.find('.//ram:LineID', self.generator.namespaces)
            if line_id is not None:
                line_ids.append(line_id.text)
        
        assert '1' in line_ids
        assert '2' in line_ids
    
    def test_invoice_without_optional_fields(self):
        """Test XML generation with minimal invoice data."""
        # Create minimal invoice
        minimal_invoice = Invoice(
            invoice_number="MIN-001",
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
            invoice_lines=[InvoiceLine(
                line_id="1",
                item_name="Service",
                quantity=Decimal("1"),
                unit_price=Decimal("100.00"),
                line_total_amount=Decimal("100.00"),
                vat_category=VATCategory.STANDARD,
                vat_rate=Decimal("20.0")
            )],
            vat_breakdown=[VATBreakdown(
                vat_category=VATCategory.STANDARD,
                vat_rate=Decimal("20.0"),
                taxable_amount=Decimal("100.00"),
                vat_amount=Decimal("20.00")
            )],
            totals=InvoiceTotals(
                line_total_amount=Decimal("100.00"),
                tax_exclusive_amount=Decimal("100.00"),
                tax_total_amount=Decimal("20.00"),
                tax_inclusive_amount=Decimal("120.00"),
                payable_amount=Decimal("120.00")
            )
        )
        
        xml_content = self.generator.generate_cii_xml(minimal_invoice)
        
        assert isinstance(xml_content, str)
        assert 'MIN-001' in xml_content
        assert 'Minimal Seller' in xml_content
        assert 'Minimal Buyer' in xml_content
        
        # Validate structure
        result = self.generator.validate_xml_structure(xml_content)
        assert result['is_valid'] is True