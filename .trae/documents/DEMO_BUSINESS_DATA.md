# Demo Business Data Configuration

## Company Information

### Legal Entity
- **Company Name**: Factur-X Express SAS
- **Legal Form**: Société par Actions Simplifiée (SAS)
- **Trade Name**: FX Express
- **Industry**: Software & Digital Services

### Registration & Identification
- **SIREN**: 123456789 (fictional)
- **SIRET**: 12345678900012 (fictional)
- **VAT Number**: FR12345678901 (fictional)
- **APE Code**: 6201Z (Computer programming activities)
- **RCS**: Paris B 123 456 789

### Address Information
```json
{
  "legal_address": {
    "street": "42 Avenue des Champs-Élysées",
    "city": "Paris",
    "postal_code": "75008",
    "country": "France",
    "country_code": "FR"
  },
  "billing_address": {
    "street": "42 Avenue des Champs-Élysées",
    "city": "Paris",
    "postal_code": "75008",
    "country": "France",
    "country_code": "FR"
  }
}
```

### Contact Information
- **Phone**: +33 1 42 65 00 00
- **Email**: contact@facturx-express.fr
- **Website**: https://facturx-express.fr

### Banking Information
- **IBAN**: FR1420041010050500013M02606 (fictional)
- **BIC**: PSSTFRPPPAR
- **Bank**: La Banque Postale
- **Account Holder**: Factur-X Express SAS

## Financial Configuration

### Currency & Tax
- **Default Currency**: EUR (€)
- **Standard VAT Rate**: 20.0%
- **Reduced VAT Rate**: 10.0%
- **Super Reduced VAT Rate**: 5.5%
- **Zero VAT Rate**: 0.0%

### Invoice Configuration
- **Invoice Number Format**: FX-{YYYY}-{seq:06d}
- **Quote Number Format**: QT-{YYYY}-{seq:06d}
- **Credit Note Format**: CN-{YYYY}-{seq:06d}
- **Starting Sequence**: 000001
- **Payment Terms**: Net 30 days
- **Late Payment Interest**: 3x ECB rate

## Branding Configuration

### Primary Colors (from fx-brand)
- **Primary Brand Color**: #2F6DF3 (--fx-accent)
- **Secondary Color**: #1E293B (--fx-graphite)
- **Text Color**: #0F172A (--fx-ink)
- **Muted Color**: #64748B (--fx-muted)
- **Slate Color**: #475569 (--fx-slate)

### Brand Assets
- **Logo Path**: `/brand/fx-logo.svg`
- **Logo Dark Path**: `/brand/fx-logo-dark.svg`
- **Favicon**: `/brand/favicon.ico`
- **Brand Kit**: Available in `/brand/` directory

### Typography
- **Primary Font**: Inter
- **Monospace Font**: JetBrains Mono
- **Font Weights**: 400, 500, 600, 700

## Legal & Compliance

### Regulatory Information
- **Capital Social**: €50,000
- **Legal Representative**: Jean Dupont (Président)
- **Registration Date**: 2024-01-15
- **Fiscal Year**: Calendar Year (Jan-Dec)

### Compliance Standards
- **EN 16931**: European Standard for Electronic Invoicing
- **PDF/A-3**: ISO 19005-3 for long-term archiving
- **GDPR**: EU General Data Protection Regulation
- **French Tax Code**: Articles 289 and following

## Usage in Development

This fictional data is designed to:
1. Test all Factur-X compliance scenarios
2. Demonstrate proper EN 16931 implementation
3. Validate XML CII generation
4. Test PDF/A-3 embedding
5. Ensure proper VAT calculations
6. Validate invoice numbering sequences

**Note**: All identifiers (SIREN, SIRET, VAT, IBAN) are fictional and should not be used in production.