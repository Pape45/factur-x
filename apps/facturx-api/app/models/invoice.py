from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator


class CurrencyCode(str, Enum):
    """ISO 4217 Currency Codes"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"


class CountryCode(str, Enum):
    """ISO 3166-1 Alpha-2 Country Codes"""
    FR = "FR"
    DE = "DE"
    IT = "IT"
    ES = "ES"
    BE = "BE"
    NL = "NL"
    LU = "LU"
    AT = "AT"
    PT = "PT"
    IE = "IE"
    FI = "FI"
    GR = "GR"
    CY = "CY"
    EE = "EE"
    LV = "LV"
    LT = "LT"
    MT = "MT"
    SK = "SK"
    SI = "SI"
    HR = "HR"
    BG = "BG"
    RO = "RO"
    CZ = "CZ"
    HU = "HU"
    PL = "PL"
    DK = "DK"
    SE = "SE"
    US = "US"
    GB = "GB"
    CH = "CH"


class VATCategory(str, Enum):
    """VAT Category Codes (EN 16931)"""
    STANDARD = "S"  # Standard rate
    ZERO = "Z"      # Zero rated
    EXEMPT = "E"    # Exempt from VAT
    REVERSE = "AE"  # Reverse charge
    REDUCED = "AA"  # Reduced rate
    SUPER_REDUCED = "AB"  # Super reduced rate


class InvoiceType(str, Enum):
    """Invoice Type Codes"""
    COMMERCIAL = "380"  # Commercial invoice
    CREDIT_NOTE = "381"  # Credit note
    DEBIT_NOTE = "383"   # Debit note
    CORRECTIVE = "384"  # Corrective invoice


class PaymentMeans(str, Enum):
    """Payment Means Codes (UN/ECE 4461)"""
    BANK_TRANSFER = "30"  # Credit transfer
    DIRECT_DEBIT = "49"   # Direct debit
    CARD = "54"          # Payment card
    CASH = "10"          # In cash
    CHEQUE = "20"        # Cheque


class Address(BaseModel):
    """Address model compliant with EN 16931"""
    street: str = Field(..., max_length=200, description="Street address")
    additional_street: Optional[str] = Field(None, max_length=200, description="Additional street info")
    city: str = Field(..., max_length=100, description="City name")
    postal_code: str = Field(..., max_length=20, description="Postal code")
    country_subdivision: Optional[str] = Field(None, max_length=100, description="State/Province")
    country: CountryCode = Field(..., description="Country code (ISO 3166-1)")


class TaxRegistration(BaseModel):
    """Tax registration information"""
    vat_number: Optional[str] = Field(None, max_length=30, description="VAT identification number")
    tax_registration_id: Optional[str] = Field(None, max_length=30, description="Tax registration identifier")
    tax_scheme: Optional[str] = Field("VAT", description="Tax scheme identifier")


class LegalRegistration(BaseModel):
    """Legal registration information"""
    registration_name: Optional[str] = Field(None, max_length=200, description="Legal registration name")
    company_id: Optional[str] = Field(None, max_length=50, description="Company registration number")
    company_legal_form: Optional[str] = Field(None, max_length=100, description="Legal form")


class Party(BaseModel):
    """Party (Seller/Buyer) model compliant with EN 16931"""
    name: str = Field(..., max_length=200, description="Party name")
    trading_name: Optional[str] = Field(None, max_length=200, description="Trading name")
    address: Address = Field(..., description="Party address")
    tax_registration: Optional[TaxRegistration] = Field(None, description="Tax registration info")
    legal_registration: Optional[LegalRegistration] = Field(None, description="Legal registration info")
    contact_name: Optional[str] = Field(None, max_length=100, description="Contact person name")
    contact_phone: Optional[str] = Field(None, max_length=50, description="Contact phone number")
    contact_email: Optional[str] = Field(None, max_length=100, description="Contact email address")
    electronic_address: Optional[str] = Field(None, max_length=200, description="Electronic address")


class BankAccount(BaseModel):
    """Bank account information"""
    iban: Optional[str] = Field(None, max_length=34, description="IBAN")
    bic: Optional[str] = Field(None, max_length=11, description="BIC/SWIFT code")
    account_name: Optional[str] = Field(None, max_length=200, description="Account holder name")
    bank_name: Optional[str] = Field(None, max_length=200, description="Bank name")


class PaymentTerms(BaseModel):
    """Payment terms information"""
    payment_means_code: PaymentMeans = Field(..., description="Payment means code")
    payment_terms_description: Optional[str] = Field(None, max_length=500, description="Payment terms description")
    due_date: Optional[date] = Field(None, description="Payment due date")
    payment_reference: Optional[str] = Field(None, max_length=100, description="Payment reference")
    bank_account: Optional[BankAccount] = Field(None, description="Bank account for payment")


class VATBreakdown(BaseModel):
    """VAT breakdown per category"""
    vat_category: VATCategory = Field(..., description="VAT category code")
    vat_rate: Decimal = Field(..., ge=0, le=100, description="VAT rate percentage")
    taxable_amount: Decimal = Field(..., ge=0, description="Taxable amount")
    vat_amount: Decimal = Field(..., ge=0, description="VAT amount")
    vat_exemption_reason: Optional[str] = Field(None, max_length=500, description="VAT exemption reason")


class InvoiceLine(BaseModel):
    """Invoice line item compliant with EN 16931"""
    line_id: str = Field(..., max_length=50, description="Line identifier")
    item_name: str = Field(..., max_length=200, description="Item name")
    item_description: Optional[str] = Field(None, max_length=1000, description="Item description")
    quantity: Decimal = Field(..., gt=0, description="Invoiced quantity")
    unit_of_measure: str = Field("C62", max_length=10, description="Unit of measure code (UN/ECE Rec 20)")
    unit_price: Decimal = Field(..., ge=0, description="Item price per unit")
    line_total_amount: Decimal = Field(..., ge=0, description="Line total amount (excluding VAT)")
    vat_category: VATCategory = Field(..., description="VAT category")
    vat_rate: Decimal = Field(..., ge=0, le=100, description="VAT rate percentage")
    item_classification: Optional[str] = Field(None, max_length=100, description="Item classification")
    origin_country: Optional[CountryCode] = Field(None, description="Country of origin")
    
    @validator('line_total_amount')
    def validate_line_total(cls, v, values):
        """Validate that line total equals quantity * unit_price"""
        if 'quantity' in values and 'unit_price' in values:
            expected_total = values['quantity'] * values['unit_price']
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('Line total must equal quantity * unit_price')
        return v


class InvoiceTotals(BaseModel):
    """Invoice totals compliant with EN 16931"""
    line_total_amount: Decimal = Field(..., ge=0, description="Sum of line totals (excluding VAT)")
    allowance_total_amount: Decimal = Field(0, ge=0, description="Total allowances")
    charge_total_amount: Decimal = Field(0, ge=0, description="Total charges")
    tax_exclusive_amount: Decimal = Field(..., ge=0, description="Invoice total (excluding VAT)")
    tax_total_amount: Decimal = Field(..., ge=0, description="Total VAT amount")
    tax_inclusive_amount: Decimal = Field(..., ge=0, description="Invoice total (including VAT)")
    prepaid_amount: Decimal = Field(0, ge=0, description="Prepaid amount")
    payable_amount: Decimal = Field(..., ge=0, description="Amount due for payment")
    
    @validator('tax_exclusive_amount')
    def validate_tax_exclusive(cls, v, values):
        """Validate tax exclusive amount calculation"""
        if all(k in values for k in ['line_total_amount', 'allowance_total_amount', 'charge_total_amount']):
            expected = values['line_total_amount'] - values['allowance_total_amount'] + values['charge_total_amount']
            if abs(v - expected) > Decimal('0.01'):
                raise ValueError('Tax exclusive amount calculation error')
        return v
    
    @validator('tax_inclusive_amount')
    def validate_tax_inclusive(cls, v, values):
        """Validate tax inclusive amount calculation"""
        if all(k in values for k in ['tax_exclusive_amount', 'tax_total_amount']):
            expected = values['tax_exclusive_amount'] + values['tax_total_amount']
            if abs(v - expected) > Decimal('0.01'):
                raise ValueError('Tax inclusive amount calculation error')
        return v
    
    @validator('payable_amount')
    def validate_payable_amount(cls, v, values):
        """Validate payable amount calculation"""
        if all(k in values for k in ['tax_inclusive_amount', 'prepaid_amount']):
            expected = values['tax_inclusive_amount'] - values['prepaid_amount']
            if abs(v - expected) > Decimal('0.01'):
                raise ValueError('Payable amount calculation error')
        return v


class Invoice(BaseModel):
    """Main invoice model compliant with EN 16931 standard"""
    # Basic invoice information
    invoice_number: str = Field(..., max_length=50, description="Invoice number")
    invoice_type: InvoiceType = Field(InvoiceType.COMMERCIAL, description="Invoice type code")
    issue_date: date = Field(..., description="Invoice issue date")
    due_date: Optional[date] = Field(None, description="Payment due date")
    currency_code: CurrencyCode = Field(CurrencyCode.EUR, description="Invoice currency")
    
    # Parties
    seller: Party = Field(..., description="Seller information")
    buyer: Party = Field(..., description="Buyer information")
    
    # Invoice lines
    invoice_lines: List[InvoiceLine] = Field(..., min_items=1, description="Invoice line items")
    
    # VAT breakdown
    vat_breakdown: List[VATBreakdown] = Field(..., min_items=1, description="VAT breakdown by category")
    
    # Totals
    totals: InvoiceTotals = Field(..., description="Invoice totals")
    
    # Payment information
    payment_terms: Optional[PaymentTerms] = Field(None, description="Payment terms")
    
    # Additional information
    order_reference: Optional[str] = Field(None, max_length=100, description="Purchase order reference")
    contract_reference: Optional[str] = Field(None, max_length=100, description="Contract reference")
    project_reference: Optional[str] = Field(None, max_length=100, description="Project reference")
    invoice_note: Optional[str] = Field(None, max_length=1000, description="Invoice note")
    
    # Preceding invoice (for credit notes)
    preceding_invoice_number: Optional[str] = Field(None, max_length=50, description="Preceding invoice number")
    preceding_invoice_date: Optional[date] = Field(None, description="Preceding invoice date")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "invoice_number": "FX-2024-000001",
                "invoice_type": "380",
                "issue_date": "2024-01-15",
                "due_date": "2024-02-14",
                "currency_code": "EUR",
                "seller": {
                    "name": "Factur-X Express SAS",
                    "address": {
                        "street": "42 Avenue des Champs-Élysées",
                        "city": "Paris",
                        "postal_code": "75008",
                        "country": "FR"
                    },
                    "tax_registration": {
                        "vat_number": "FR12345678901"
                    }
                },
                "buyer": {
                    "name": "Example Client SARL",
                    "address": {
                        "street": "123 Rue de la Paix",
                        "city": "Lyon",
                        "postal_code": "69000",
                        "country": "FR"
                    }
                },
                "invoice_lines": [
                    {
                        "line_id": "1",
                        "item_name": "Factur-X Service",
                        "quantity": 1,
                        "unit_price": 100.00,
                        "line_total_amount": 100.00,
                        "vat_category": "S",
                        "vat_rate": 20.0
                    }
                ],
                "vat_breakdown": [
                    {
                        "vat_category": "S",
                        "vat_rate": 20.0,
                        "taxable_amount": 100.00,
                        "vat_amount": 20.00
                    }
                ],
                "totals": {
                    "line_total_amount": 100.00,
                    "tax_exclusive_amount": 100.00,
                    "tax_total_amount": 20.00,
                    "tax_inclusive_amount": 120.00,
                    "payable_amount": 120.00
                }
            }
        }


class InvoiceCreateRequest(BaseModel):
    """Request model for creating a new invoice"""
    
    # Invoice will get auto-generated number and issue date
    due_date: Optional[date] = Field(None, description="Payment due date")
    invoice_type: InvoiceType = Field(InvoiceType.COMMERCIAL, description="Type of invoice")
    currency_code: CurrencyCode = Field(CurrencyCode.EUR, description="Invoice currency")
    
    # Buyer information (required)
    buyer: Party = Field(..., description="Buyer information")
    
    # Invoice lines (required)
    invoice_lines: List[InvoiceLine] = Field(..., min_items=1, description="Invoice line items")
    
    # Optional fields
    order_reference: Optional[str] = Field(None, description="Buyer's purchase order reference")
    contract_reference: Optional[str] = Field(None, description="Contract reference")
    project_reference: Optional[str] = Field(None, description="Project reference")
    
    # Payment information
    payment_terms: Optional[PaymentTerms] = Field(None, description="Payment terms")
    
    # Additional notes
    invoice_note: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        schema_extra = {
            "example": {
                "due_date": "2024-02-14",
                "currency_code": "EUR",
                "buyer": {
                    "name": "ACME Corporation",
                    "address": {
                        "street": "123 Business Street",
                        "city": "Lyon",
                        "postal_code": "69000",
                        "country": "FR"
                    },
                    "tax_registration": {
                        "vat_number": "FR98765432109"
                    }
                },
                "invoice_lines": [
                    {
                        "line_id": "1",
                        "item_name": "Software License",
                        "quantity": 1,
                        "unit_price": 1000.00,
                        "line_total_amount": 1000.00,
                        "vat_rate": 20.0,
                        "vat_category": "S"
                    }
                ],
                "order_reference": "PO-2024-001",
                "invoice_note": "Thank you for your business!"
            }
        }


class InvoiceResponse(BaseModel):
    """Response model for invoice operations"""
    
    invoice: Invoice = Field(..., description="The invoice data")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    
    class Config:
        schema_extra = {
            "example": {
                "invoice": {
                    "invoice_number": "FX-2024-000001",
                    "issue_date": "2024-01-15",
                    "due_date": "2024-02-14",
                    "currency_code": "EUR",
                    "buyer": {
                        "name": "ACME Corporation"
                    },
                    "totals": {
                        "payable_amount": 1200.00
                    }
                },
                "status": "created",
                "message": "Invoice created successfully"
            }
        }