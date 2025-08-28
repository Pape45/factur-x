from decimal import Decimal
from typing import Dict, Optional
from pydantic import BaseModel, Field
from .invoice import Address, TaxRegistration, LegalRegistration, BankAccount, CountryCode, CurrencyCode


class BusinessConfiguration(BaseModel):
    """Business configuration for Factur-X Express demo company"""
    
    # Company Information
    company_name: str = Field("Factur-X Express SAS", description="Legal company name")
    trading_name: str = Field("FX Express", description="Trading name")
    legal_form: str = Field("Société par Actions Simplifiée (SAS)", description="Legal form")
    industry: str = Field("Software & Digital Services", description="Industry sector")
    
    # Legal Registration
    siren: str = Field("123456789", description="SIREN number (fictional)")
    siret: str = Field("12345678900012", description="SIRET number (fictional)")
    ape_code: str = Field("6201Z", description="APE code")
    rcs: str = Field("Paris B 123 456 789", description="RCS registration")
    capital_social: str = Field("50000", description="Share capital in EUR")
    
    # Address Information
    legal_address: Address = Field(
        default=Address(
            street="42 Avenue des Champs-Élysées",
            city="Paris",
            postal_code="75008",
            country=CountryCode.FR
        ),
        description="Legal registered address"
    )
    
    billing_address: Optional[Address] = Field(
        default=None,
        description="Billing address (if different from legal)"
    )
    
    # Tax Registration
    tax_registration: TaxRegistration = Field(
        default=TaxRegistration(
            vat_number="FR12345678901",
            tax_registration_id="FR12345678901",
            tax_scheme="VAT"
        ),
        description="Tax registration information"
    )
    
    # Contact Information
    phone: str = Field("+33 1 42 65 00 00", description="Main phone number")
    email: str = Field("contact@facturx-express.fr", description="Main email address")
    website: str = Field("https://facturx-express.fr", description="Company website")
    
    # Banking Information
    bank_account: BankAccount = Field(
        default=BankAccount(
            iban="FR1420041010050500013M02606",
            bic="PSSTFRPPPAR",
            account_name="Factur-X Express SAS",
            bank_name="La Banque Postale"
        ),
        description="Primary bank account"
    )
    
    # Financial Configuration
    default_currency: CurrencyCode = Field(CurrencyCode.EUR, description="Default currency")
    
    # VAT Rates (French rates)
    vat_rates: Dict[str, Decimal] = Field(
        default={
            "standard": Decimal("20.0"),      # Standard VAT rate
            "reduced": Decimal("10.0"),       # Reduced VAT rate
            "super_reduced": Decimal("5.5"),  # Super reduced VAT rate
            "zero": Decimal("0.0")            # Zero VAT rate
        },
        description="Available VAT rates"
    )
    
    # Invoice Configuration
    invoice_number_format: str = Field("FX-{year}-{seq:06d}", description="Invoice number format")
    quote_number_format: str = Field("QT-{year}-{seq:06d}", description="Quote number format")
    credit_note_format: str = Field("CN-{year}-{seq:06d}", description="Credit note format")
    starting_sequence: int = Field(1, description="Starting sequence number")
    
    # Payment Terms
    default_payment_terms: str = Field("Net 30 days", description="Default payment terms")
    late_payment_interest: str = Field("3x ECB rate", description="Late payment interest rate")
    
    # Branding
    primary_color: str = Field("#2F6DF3", description="Primary brand color (--fx-accent)")
    secondary_color: str = Field("#1E293B", description="Secondary color (--fx-graphite)")
    text_color: str = Field("#0F172A", description="Text color (--fx-ink)")
    muted_color: str = Field("#64748B", description="Muted color (--fx-muted)")
    
    # Legal Representative
    legal_representative_name: str = Field("Jean Dupont", description="Legal representative name")
    legal_representative_title: str = Field("Président", description="Legal representative title")
    
    # Compliance Information
    registration_date: str = Field("2024-01-15", description="Company registration date")
    fiscal_year_start: str = Field("01-01", description="Fiscal year start (MM-DD)")
    fiscal_year_end: str = Field("12-31", description="Fiscal year end (MM-DD)")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "company_name": "Factur-X Express SAS",
                "trading_name": "FX Express",
                "siren": "123456789",
                "siret": "12345678900012",
                "legal_address": {
                    "street": "42 Avenue des Champs-Élysées",
                    "city": "Paris",
                    "postal_code": "75008",
                    "country": "FR"
                },
                "tax_registration": {
                    "vat_number": "FR12345678901"
                },
                "bank_account": {
                    "iban": "FR1420041010050500013M02606",
                    "bic": "PSSTFRPPPAR"
                },
                "primary_color": "#2F6DF3"
            }
        }


# Global business configuration instance
BUSINESS_CONFIG = BusinessConfiguration()


def get_business_config() -> BusinessConfiguration:
    """Get the current business configuration"""
    return BUSINESS_CONFIG


def update_business_config(config: BusinessConfiguration) -> BusinessConfiguration:
    """Update the business configuration"""
    global BUSINESS_CONFIG
    BUSINESS_CONFIG = config
    return BUSINESS_CONFIG