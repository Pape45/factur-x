"""Unit tests for invoice service."""

import pytest
from datetime import datetime, date
from decimal import Decimal

from app.services.invoice_service import InvoiceService
from app.models.invoice import (
    InvoiceCreateRequest, Invoice, InvoiceLine, Party, Address,
    CurrencyCode, CountryCode, VATCategory, InvoiceType
)

class TestInvoiceService:
    """Test cases for InvoiceService."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.service = InvoiceService()
        
        # Sample buyer data
        self.buyer_address = Address(
            street="123 Test Street",
            city="Test City",
            postal_code="12345",
            country_code=CountryCode.FR
        )
        
        self.buyer = Party(
            name="Test Buyer Company",
            address=self.buyer_address,
            vat_id="FR12345678901"
        )
        
        # Sample invoice line
        self.invoice_line = InvoiceLine(
            line_id="1",
            name="Test Product",
            description="A test product for unit testing",
            quantity=Decimal("2.00"),
            unit_price=Decimal("100.00"),
            vat_category=VATCategory.STANDARD_RATE,
            vat_rate=Decimal("20.00")
        )
        
        # Sample invoice request
        self.invoice_request = InvoiceCreateRequest(
            buyer=self.buyer,
            lines=[self.invoice_line],
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
    
    def test_generate_invoice_number(self):
        """Test invoice number generation."""
        invoice_number = self.service.generate_invoice_number()
        
        assert invoice_number is not None
        assert isinstance(invoice_number, str)
        assert len(invoice_number) > 0
        
        # Should follow format FX-YYYY-NNNN
        parts = invoice_number.split('-')
        assert len(parts) == 3
        assert parts[0] == "FX"
        assert len(parts[1]) == 4  # Year
        assert parts[2].isdigit()  # Sequence number
    
    def test_generate_unique_invoice_numbers(self):
        """Test that generated invoice numbers are unique."""
        numbers = set()
        for _ in range(10):
            number = self.service.generate_invoice_number()
            assert number not in numbers
            numbers.add(number)
    
    def test_calculate_line_totals(self):
        """Test line total calculations."""
        line = InvoiceLine(
            line_id="1",
            name="Test Product",
            quantity=Decimal("3.00"),
            unit_price=Decimal("50.00"),
            vat_category=VATCategory.STANDARD_RATE,
            vat_rate=Decimal("20.00")
        )
        
        totals = self.service.calculate_line_totals(line)
        
        assert totals["net_amount"] == Decimal("150.00")
        assert totals["vat_amount"] == Decimal("30.00")
        assert totals["gross_amount"] == Decimal("180.00")
    
    def test_calculate_invoice_totals(self):
        """Test invoice total calculations."""
        lines = [
            InvoiceLine(
                line_id="1",
                name="Product 1",
                quantity=Decimal("2.00"),
                unit_price=Decimal("100.00"),
                vat_category=VATCategory.STANDARD_RATE,
                vat_rate=Decimal("20.00")
            ),
            InvoiceLine(
                line_id="2",
                name="Product 2",
                quantity=Decimal("1.00"),
                unit_price=Decimal("50.00"),
                vat_category=VATCategory.STANDARD_RATE,
                vat_rate=Decimal("20.00")
            )
        ]
        
        totals = self.service.calculate_invoice_totals(lines)
        
        assert totals.net_total == Decimal("250.00")
        assert totals.vat_total == Decimal("50.00")
        assert totals.gross_total == Decimal("300.00")
        
        # Check VAT breakdown
        assert len(totals.vat_breakdown) == 1
        vat_item = totals.vat_breakdown[0]
        assert vat_item.vat_rate == Decimal("20.00")
        assert vat_item.taxable_amount == Decimal("250.00")
        assert vat_item.vat_amount == Decimal("50.00")
    
    def test_create_invoice_from_request(self):
        """Test creating invoice from request."""
        invoice = self.service.create_invoice_from_request(self.invoice_request)
        
        assert isinstance(invoice, Invoice)
        assert invoice.invoice_number is not None
        assert invoice.buyer == self.buyer
        assert len(invoice.lines) == 1
        assert invoice.lines[0] == self.invoice_line
        assert invoice.issue_date == self.invoice_request.issue_date
        assert invoice.due_date == self.invoice_request.due_date
        assert invoice.currency == self.invoice_request.currency
        assert invoice.invoice_type == self.invoice_request.invoice_type
        
        # Check calculated totals
        assert invoice.totals.net_total == Decimal("200.00")
        assert invoice.totals.vat_total == Decimal("40.00")
        assert invoice.totals.gross_total == Decimal("240.00")
    
    def test_store_and_retrieve_invoice(self):
        """Test storing and retrieving invoices."""
        invoice = self.service.create_invoice_from_request(self.invoice_request)
        
        # Store invoice
        stored_invoice = self.service.store_invoice(invoice)
        assert stored_invoice.invoice_id is not None
        
        # Retrieve invoice
        retrieved_invoice = self.service.get_invoice(stored_invoice.invoice_id)
        assert retrieved_invoice is not None
        assert retrieved_invoice.invoice_id == stored_invoice.invoice_id
        assert retrieved_invoice.invoice_number == stored_invoice.invoice_number
    
    def test_get_nonexistent_invoice(self):
        """Test retrieving non-existent invoice."""
        invoice = self.service.get_invoice("nonexistent-id")
        assert invoice is None
    
    def test_list_invoices(self):
        """Test listing invoices."""
        # Create and store multiple invoices
        invoices = []
        for i in range(3):
            request = InvoiceCreateRequest(
                buyer=self.buyer,
                lines=[self.invoice_line],
                issue_date=date.today(),
                due_date=date.today(),
                currency=CurrencyCode.EUR,
                invoice_type=InvoiceType.COMMERCIAL_INVOICE
            )
            invoice = self.service.create_invoice_from_request(request)
            stored_invoice = self.service.store_invoice(invoice)
            invoices.append(stored_invoice)
        
        # List all invoices
        all_invoices = self.service.list_invoices()
        assert len(all_invoices) >= 3
        
        # Check that our invoices are in the list
        stored_ids = {inv.invoice_id for inv in invoices}
        retrieved_ids = {inv.invoice_id for inv in all_invoices}
        assert stored_ids.issubset(retrieved_ids)
    
    def test_list_invoices_with_limit(self):
        """Test listing invoices with limit."""
        # Create and store multiple invoices
        for i in range(5):
            request = InvoiceCreateRequest(
                buyer=self.buyer,
                lines=[self.invoice_line],
                issue_date=date.today(),
                due_date=date.today(),
                currency=CurrencyCode.EUR,
                invoice_type=InvoiceType.COMMERCIAL_INVOICE
            )
            invoice = self.service.create_invoice_from_request(request)
            self.service.store_invoice(invoice)
        
        # List with limit
        limited_invoices = self.service.list_invoices(limit=3)
        assert len(limited_invoices) == 3
    
    def test_get_invoice_statistics(self):
        """Test getting invoice statistics."""
        # Create and store invoices
        for i in range(3):
            request = InvoiceCreateRequest(
                buyer=self.buyer,
                lines=[self.invoice_line],
                issue_date=date.today(),
                due_date=date.today(),
                currency=CurrencyCode.EUR,
                invoice_type=InvoiceType.COMMERCIAL_INVOICE
            )
            invoice = self.service.create_invoice_from_request(request)
            self.service.store_invoice(invoice)
        
        stats = self.service.get_invoice_statistics()
        
        assert "total_count" in stats
        assert "total_amount" in stats
        assert "currency_breakdown" in stats
        assert stats["total_count"] >= 3
        assert stats["total_amount"] >= Decimal("720.00")  # 3 * 240.00
    
    def test_create_sample_invoice(self):
        """Test creating sample invoice."""
        sample_invoice = self.service.create_sample_invoice()
        
        assert isinstance(sample_invoice, Invoice)
        assert sample_invoice.invoice_number is not None
        assert sample_invoice.buyer is not None
        assert len(sample_invoice.lines) > 0
        assert sample_invoice.totals.gross_total > Decimal("0")
        
        # Verify it can be stored
        stored_sample = self.service.store_invoice(sample_invoice)
        assert stored_sample.invoice_id is not None
    
    def test_invoice_validation(self):
        """Test invoice validation."""
        # Test with invalid line (negative quantity)
        invalid_line = InvoiceLine(
            line_id="1",
            name="Invalid Product",
            quantity=Decimal("-1.00"),  # Invalid
            unit_price=Decimal("100.00"),
            vat_category=VATCategory.STANDARD_RATE,
            vat_rate=Decimal("20.00")
        )
        
        invalid_request = InvoiceCreateRequest(
            buyer=self.buyer,
            lines=[invalid_line],
            issue_date=date.today(),
            due_date=date.today(),
            currency=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL_INVOICE
        )
        
        # This should raise a validation error
        with pytest.raises(ValueError):
            self.service.create_invoice_from_request(invalid_request)