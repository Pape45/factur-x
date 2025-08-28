# Why Business Information is Required for Factur-X

## EN 16931 Compliance Requirements

Factur-X invoices must comply with the **EN 16931 European Standard** for electronic invoicing. This standard mandates specific business information to be embedded in both the PDF and XML components:

### 1. Legal Company Identification
- **Company Name**: Legal entity name for official recognition
- **SIREN/SIRET**: French business registry numbers (mandatory for French companies)
- **VAT Number**: European VAT identification for cross-border transactions
- **Legal Address**: Official registered business address

### 2. Financial Information
- **IBAN**: Bank account details for payment processing
- **Currency**: Default currency for invoice amounts
- **VAT Rates**: Tax calculations and compliance

### 3. Invoice Formatting
- **Numbering Format**: Sequential invoice numbering for audit trails
- **Date Formats**: Standardized date representation

### 4. XML CII Generation
The Cross Industry Invoice (CII) XML format requires:
- Seller party identification with legal identifiers
- Tax registration details
- Payment terms and bank information
- Structured address data

### 5. PDF/A-3 Embedding
The PDF component must contain:
- Human-readable invoice with company branding
- Embedded XML metadata with structured data
- Digital signature capabilities

### 6. Validation Requirements
- **veraPDF**: Validates PDF/A-3 compliance
- **Mustangproject**: Validates Factur-X structure
- **EN 16931 Schema**: Validates XML content

## Demo Data Purpose

Using fictional but realistic business data allows us to:
1. Test all compliance scenarios
2. Demonstrate proper data structure
3. Validate invoice generation workflows
4. Ensure regulatory compliance patterns

This information is embedded in every generated invoice and is essential for legal and technical compliance.