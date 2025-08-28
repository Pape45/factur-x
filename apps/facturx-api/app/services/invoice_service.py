from datetime import datetime, date
from typing import List, Optional, Dict, Any
from decimal import Decimal
import uuid

from ..models.invoice import Invoice, InvoiceCreateRequest, InvoiceTotals, VATBreakdown
from ..models.business import get_business_config


class InvoiceService:
    """Service for managing invoice operations"""
    
    def __init__(self):
        # In-memory storage for demo purposes
        # In production, this would be a database
        self._invoices: Dict[str, Invoice] = {}
        self._sequence_counter = 1
    
    def generate_invoice_number(self) -> str:
        """Generate a unique invoice number based on business configuration"""
        business_config = get_business_config()
        current_year = datetime.now().year
        
        # Parse format template
        invoice_number = business_config.invoice_number_format.format(
            year=current_year,
            seq=self._sequence_counter
        )
        
        self._sequence_counter += 1
        return invoice_number
    
    def calculate_totals(self, invoice_request: InvoiceCreateRequest) -> InvoiceTotals:
        """Calculate invoice totals from line items"""
        line_extension_amount = Decimal('0')
        total_vat_amount = Decimal('0')
        
        # Calculate line totals and VAT
        for line in invoice_request.invoice_lines:
            line_total = line.quantity * line.unit_price
            line_extension_amount += line_total
            
            # Calculate VAT for this line
            vat_amount = line_total * (line.vat_rate / Decimal('100'))
            total_vat_amount += vat_amount
        
        # Calculate final totals
        tax_exclusive_amount = line_extension_amount
        tax_inclusive_amount = line_extension_amount + total_vat_amount
        payable_amount = tax_inclusive_amount  # Assuming no additional charges
        
        return InvoiceTotals(
            line_total_amount=line_extension_amount,
            tax_exclusive_amount=tax_exclusive_amount,
            tax_total_amount=total_vat_amount,
            tax_inclusive_amount=tax_inclusive_amount,
            payable_amount=payable_amount
        )
    
    def _calculate_vat_breakdown(self, invoice_request: InvoiceCreateRequest) -> List[VATBreakdown]:
        """Calculate VAT breakdown from line items"""
        from ..models.invoice import VATBreakdown
        
        vat_breakdowns = {}
        
        # Calculate VAT breakdown
        for line in invoice_request.invoice_lines:
            line_total = line.quantity * line.unit_price
            vat_amount = line_total * (line.vat_rate / Decimal('100'))
            
            # Group by VAT rate for breakdown
            vat_key = (line.vat_rate, line.vat_category)
            if vat_key not in vat_breakdowns:
                vat_breakdowns[vat_key] = {
                    'taxable_amount': Decimal('0'),
                    'tax_amount': Decimal('0'),
                    'rate': line.vat_rate,
                    'category': line.vat_category
                }
            
            vat_breakdowns[vat_key]['taxable_amount'] += line_total
            vat_breakdowns[vat_key]['tax_amount'] += vat_amount
        
        # Create VAT breakdown list
        return [
            VATBreakdown(
                taxable_amount=breakdown['taxable_amount'],
                vat_amount=breakdown['tax_amount'],
                vat_category=breakdown['category'],
                vat_rate=breakdown['rate']
            )
            for breakdown in vat_breakdowns.values()
        ]
    
    def create_invoice_from_request(self, invoice_request: InvoiceCreateRequest) -> Invoice:
        """Create a complete invoice from a request"""
        business_config = get_business_config()
        
        # Generate invoice number and dates
        invoice_number = self.generate_invoice_number()
        issue_date = date.today()
        
        # Set due date if not provided
        due_date = invoice_request.due_date
        if not due_date:
            # Default to 30 days from issue date
            from datetime import timedelta
            due_date = issue_date + timedelta(days=30)
        
        # Calculate totals and VAT breakdown
        totals = self.calculate_totals(invoice_request)
        vat_breakdown = self._calculate_vat_breakdown(invoice_request)
        
        # Create seller information from business config
        from ..models.invoice import Party, Address, TaxRegistration, LegalRegistration
        
        seller = Party(
            name=business_config.company_name,
            address=business_config.legal_address,
            tax_registration=business_config.tax_registration,
            legal_registration=LegalRegistration(
                registration_id=business_config.siret,
                registration_scheme="SIRET",
                registration_name=business_config.company_name
            ),
            contact={
                "telephone": business_config.phone,
                "email": business_config.email
            }
        )
        
        # Create the complete invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            issue_date=issue_date,
            due_date=due_date,
            invoice_type=invoice_request.invoice_type,
            currency_code=invoice_request.currency_code,
            seller=seller,
            buyer=invoice_request.buyer,
            invoice_lines=invoice_request.invoice_lines,
            totals=totals,
            vat_breakdown=vat_breakdown,
            order_reference=invoice_request.order_reference,
            contract_reference=invoice_request.contract_reference,
            project_reference=invoice_request.project_reference,
            payment_terms=invoice_request.payment_terms,
            invoice_note=invoice_request.invoice_note
        )
        
        return invoice
    
    def store_invoice(self, invoice: Invoice) -> Invoice:
        """Store an invoice (in-memory for demo)"""
        # Generate a unique ID for storage
        invoice_id = str(uuid.uuid4())
        
        # In a real application, you would save to database here
        # For demo, we'll store in memory with the invoice number as key
        self._invoices[invoice.invoice_number] = invoice
        self._invoices[invoice_id] = invoice  # Also store by ID for retrieval
        
        return invoice
    
    def get_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """Retrieve an invoice by ID or invoice number"""
        return self._invoices.get(invoice_id)
    
    def list_invoices(
        self,
        limit: int = 10,
        offset: int = 0,
        buyer_name: Optional[str] = None
    ) -> List[Invoice]:
        """List invoices with optional filtering"""
        invoices = list(self._invoices.values())
        
        # Remove duplicates (since we store by both ID and number)
        unique_invoices = []
        seen_numbers = set()
        for invoice in invoices:
            if invoice.invoice_number not in seen_numbers:
                unique_invoices.append(invoice)
                seen_numbers.add(invoice.invoice_number)
        
        # Filter by buyer name if provided
        if buyer_name:
            unique_invoices = [
                inv for inv in unique_invoices
                if buyer_name.lower() in inv.buyer.name.lower()
            ]
        
        # Apply pagination
        start = offset
        end = offset + limit
        return unique_invoices[start:end]
    
    def get_invoice_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about invoices"""
        invoices = list(self._invoices.values())
        
        # Remove duplicates
        unique_invoices = []
        seen_numbers = set()
        for invoice in invoices:
            if invoice.invoice_number not in seen_numbers:
                unique_invoices.append(invoice)
                seen_numbers.add(invoice.invoice_number)
        
        total_count = len(unique_invoices)
        total_amount = sum(
            invoice.totals.payable_amount for invoice in unique_invoices
        )
        
        # Group by currency
        currency_totals = {}
        for invoice in unique_invoices:
            currency = invoice.currency_code.value
            if currency not in currency_totals:
                currency_totals[currency] = Decimal('0')
            currency_totals[currency] += invoice.totals.payable_amount
        
        return {
            "total_invoices": total_count,
            "total_amount": float(total_amount),
            "currency_breakdown": {
                currency: float(amount)
                for currency, amount in currency_totals.items()
            },
            "next_invoice_number": self.generate_invoice_number()
        }
    
    def create_sample_invoice(self) -> Invoice:
        """Create a sample invoice for testing"""
        from ..models.invoice import (
            InvoiceCreateRequest, Party, Address, TaxRegistration,
            InvoiceLine, CountryCode, CurrencyCode, InvoiceType
        )
        
        # Create sample buyer
        buyer = Party(
            name="ACME Corporation",
            address=Address(
                street="123 Business Avenue",
                city="Lyon",
                postal_code="69000",
                country=CountryCode.FR
            ),
            tax_registration=TaxRegistration(
                vat_number="FR98765432109",
                tax_registration_id="FR98765432109",
                tax_scheme="VAT"
            )
        )
        
        # Create sample invoice lines
        lines = [
            InvoiceLine(
                line_id="1",
                item_name="Software Development Services",
                item_description="Custom software development - Q1 2024",
                quantity=Decimal('40'),
                unit_code="HUR",  # Hours
                unit_price=Decimal('125.00'),
                line_total_amount=Decimal('5000.00'),
                vat_rate=Decimal('20.0'),
                vat_category="S"
            ),
            InvoiceLine(
                line_id="2",
                item_name="Technical Consultation",
                item_description="Architecture review and recommendations",
                quantity=Decimal('8'),
                unit_code="HUR",
                unit_price=Decimal('150.00'),
                line_total_amount=Decimal('1200.00'),
                vat_rate=Decimal('20.0'),
                vat_category="S"
            )
        ]
        
        # Create request
        request = InvoiceCreateRequest(
            currency_code=CurrencyCode.EUR,
            invoice_type=InvoiceType.COMMERCIAL,
            buyer=buyer,
            invoice_lines=lines,
            order_reference="PO-ACME-2024-001",
            invoice_note="Thank you for choosing Factur-X Express for your software development needs."
        )
        
        # Create and store invoice
        invoice = self.create_invoice_from_request(request)
        return self.store_invoice(invoice)