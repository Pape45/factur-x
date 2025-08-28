# Compliance Framework

## Overview
This document outlines the comprehensive compliance framework for Factur-X Express, covering European e-invoicing standards, data protection regulations, and French fiscal requirements.

---

## Table of Contents
1. [EN 16931 Compliance](#en-16931-compliance)
2. [PDF/A-3 Compliance](#pdfa-3-compliance)
3. [GDPR Compliance](#gdpr-compliance)
4. [French E-invoicing Regulations](#french-e-invoicing-regulations)
5. [Compliance Monitoring](#compliance-monitoring)
6. [Audit Procedures](#audit-procedures)

---

## EN 16931 Compliance

### 1.1 Standard Overview
**EN 16931** is the European standard for electronic invoicing that defines:
- Semantic data model for core invoice elements
- Syntax bindings (UBL 2.1, UN/CEFACT CII D16B)
- Business rules and validation requirements
- Code lists for standardized values

### 1.2 Mandatory Data Elements

#### Invoice Header Information
| Element | Cardinality | Description | Validation |
|---------|-------------|-------------|------------|
| Invoice number | 1..1 | Unique invoice identifier | Required, unique per seller |
| Invoice issue date | 1..1 | Date when invoice was issued | Required, valid date format |
| Invoice type code | 1..1 | Type of invoice (380=Commercial invoice) | Required, from code list |
| Invoice currency code | 1..1 | Currency of invoice amounts | Required, ISO 4217 code |
| VAT accounting currency | 0..1 | VAT currency if different | Optional, ISO 4217 code |
| Value added tax point date | 0..1 | Date when VAT becomes due | Optional, valid date |
| Invoice period | 0..1 | Period covered by invoice | Optional, start/end dates |
| Payment due date | 0..1 | Date when payment is due | Optional, valid date |
| Buyer reference | 0..1 | Reference provided by buyer | Optional, string |
| Project reference | 0..1 | Project identifier | Optional, string |
| Contract reference | 0..1 | Contract identifier | Optional, string |

#### Seller Information
| Element | Cardinality | Description | Validation |
|---------|-------------|-------------|------------|
| Seller name | 1..1 | Legal name of seller | Required, non-empty |
| Seller identifier | 0..1 | Unique seller identifier | Optional, valid format |
| Seller VAT identifier | 0..1 | VAT registration number | Conditional, required if VAT |
| Seller address | 1..1 | Postal address | Required, complete address |
| Seller electronic address | 1..1 | Electronic address for delivery | Required, valid format |
| Seller contact point | 0..1 | Contact information | Optional |

#### Buyer Information
| Element | Cardinality | Description | Validation |
|---------|-------------|-------------|------------|
| Buyer name | 1..1 | Legal name of buyer | Required, non-empty |
| Buyer identifier | 0..1 | Unique buyer identifier | Optional, valid format |
| Buyer VAT identifier | 0..1 | VAT registration number | Conditional |
| Buyer address | 1..1 | Postal address | Required, complete address |
| Buyer electronic address | 0..1 | Electronic address | Optional |

#### Invoice Line Information
| Element | Cardinality | Description | Validation |
|---------|-------------|-------------|------------|
| Invoice line identifier | 1..1 | Unique line identifier | Required, unique per invoice |
| Invoiced quantity | 1..1 | Quantity of items | Required, numeric |
| Invoiced quantity unit | 1..1 | Unit of measure | Required, from code list |
| Invoice line net amount | 1..1 | Net amount for line | Required, calculated |
| Item name | 1..1 | Name/description of item | Required, non-empty |
| Item price | 1..1 | Unit price of item | Required, numeric |
| VAT category code | 1..1 | VAT category | Required, from code list |
| VAT rate | 1..1 | VAT percentage | Required, numeric |

### 1.3 Business Rules Implementation

#### BR-01: Invoice Total Validation
```python
def validate_invoice_totals(invoice):
    """
    BR-01: An Invoice shall have a Sum of Invoice line net amount
    """
    calculated_sum = sum(line.net_amount for line in invoice.lines)
    if abs(invoice.sum_of_line_net_amounts - calculated_sum) > 0.01:
        raise ValidationError("BR-01: Sum of line net amounts mismatch")
    
    # BR-02: Invoice total VAT amount validation
    calculated_vat = sum(line.vat_amount for line in invoice.lines)
    if abs(invoice.total_vat_amount - calculated_vat) > 0.01:
        raise ValidationError("BR-02: Total VAT amount mismatch")
    
    # BR-03: Invoice total amount validation
    expected_total = invoice.sum_of_line_net_amounts + invoice.total_vat_amount
    if abs(invoice.total_amount - expected_total) > 0.01:
        raise ValidationError("BR-03: Invoice total amount mismatch")
```

#### BR-05: VAT Category Validation
```python
def validate_vat_categories(invoice):
    """
    BR-05: VAT category code validation
    """
    valid_vat_categories = {
        'S': 'Standard rate',
        'Z': 'Zero rated goods',
        'E': 'Exempt from VAT',
        'AE': 'VAT Reverse Charge',
        'K': 'VAT exempt for EEA intra-community supply',
        'G': 'Free export item, VAT not charged',
        'O': 'Services outside scope of VAT',
        'L': 'Canary Islands general indirect tax',
        'M': 'Tax for production, services and importation in Ceuta and Melilla'
    }
    
    for line in invoice.lines:
        if line.vat_category_code not in valid_vat_categories:
            raise ValidationError(f"BR-05: Invalid VAT category code: {line.vat_category_code}")
```

### 1.4 XML Generation

```python
from facturx import generate_from_file
from lxml import etree

def generate_en16931_xml(invoice_data):
    """
    Generate EN 16931 compliant XML using factur-x library
    """
    # Create XML structure according to EN 16931
    xml_template = """
    <?xml version="1.0" encoding="UTF-8"?>
    <rsm:CrossIndustryInvoice 
        xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
        xmlns:qdt="urn:un:unece:uncefact:data:standard:QualifiedDataType:100"
        xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
        xmlns:xs="http://www.w3.org/2001/XMLSchema"
        xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
        
        <!-- Exchange Document Context -->
        <rsm:ExchangedDocumentContext>
            <ram:GuidelineSpecifiedDocumentContextParameter>
                <ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:extended</ram:ID>
            </ram:GuidelineSpecifiedDocumentContextParameter>
        </rsm:ExchangedDocumentContext>
        
        <!-- Exchange Document -->
        <rsm:ExchangedDocument>
            <ram:ID>{invoice_number}</ram:ID>
            <ram:TypeCode>380</ram:TypeCode>
            <ram:IssueDateTime>
                <udt:DateTimeString format="102">{issue_date}</udt:DateTimeString>
            </ram:IssueDateTime>
        </rsm:ExchangedDocument>
        
        <!-- Supply Chain Trade Transaction -->
        <rsm:SupplyChainTradeTransaction>
            <!-- Line Items -->
            <!-- Seller Information -->
            <!-- Buyer Information -->
            <!-- Settlement -->
        </rsm:SupplyChainTradeTransaction>
    </rsm:CrossIndustryInvoice>
    """
    
    # Populate XML with invoice data
    xml_content = xml_template.format(
        invoice_number=invoice_data['invoice_number'],
        issue_date=invoice_data['issue_date'].strftime('%Y%m%d')
    )
    
    # Validate XML against EN 16931 schema
    validate_en16931_xml(xml_content)
    
    return xml_content

def validate_en16931_xml(xml_content):
    """
    Validate XML against EN 16931 schema using Mustangproject
    """
    try:
        # Use Mustangproject for validation
        validation_result = mustangproject_validate(xml_content)
        if not validation_result.is_valid:
            raise ValidationError(f"EN 16931 validation failed: {validation_result.errors}")
    except Exception as e:
        raise ValidationError(f"XML validation error: {str(e)}")
```

---

## PDF/A-3 Compliance

### 2.1 PDF/A-3 Requirements

**PDF/A-3** is an ISO standard (ISO 19005-3) that ensures long-term preservation of electronic documents with embedded files.

#### Key Requirements:
1. **File Structure**: Valid PDF structure according to PDF 1.7
2. **Fonts**: All fonts must be embedded
3. **Color Spaces**: Device-independent color spaces only
4. **Transparency**: No transparency effects
5. **Encryption**: No encryption allowed
6. **Metadata**: XMP metadata required
7. **Attachments**: Embedded files must be PDF/A compliant or have proper MIME types

### 2.2 PDF Generation Implementation

```python
import weasyprint
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

def generate_pdfa3_invoice(invoice_data, xml_content):
    """
    Generate PDF/A-3 compliant invoice with embedded XML
    """
    # Configure fonts for PDF/A compliance
    font_config = FontConfiguration()
    
    # HTML template for invoice
    html_content = generate_invoice_html(invoice_data)
    
    # CSS for styling (PDF/A-3 compliant)
    css_content = """
    @page {
        size: A4;
        margin: 2cm;
    }
    
    body {
        font-family: 'Inter', sans-serif;
        color: #000000;
        background-color: #ffffff;
    }
    
    /* No transparency or advanced effects */
    .header {
        border-bottom: 2px solid #2563eb;
        margin-bottom: 20px;
    }
    
    .invoice-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .invoice-table th,
    .invoice-table td {
        border: 1px solid #000000;
        padding: 8px;
        text-align: left;
    }
    """
    
    # Generate PDF with WeasyPrint
    html_doc = HTML(string=html_content)
    css_doc = CSS(string=css_content)
    
    # PDF/A-3 specific options
    pdf_options = {
        'pdf_version': '1.7',
        'pdf_identifier': True,
        'pdf_variant': 'pdf/a-3b',
        'attachments': [{
            'filename': f'factur-x-{invoice_data["invoice_number"]}.xml',
            'content': xml_content.encode('utf-8'),
            'mime_type': 'text/xml',
            'description': 'Factur-X XML data'
        }]
    }
    
    pdf_bytes = html_doc.write_pdf(
        stylesheets=[css_doc],
        font_config=font_config,
        **pdf_options
    )
    
    # Validate PDF/A-3 compliance
    validate_pdfa3_compliance(pdf_bytes)
    
    return pdf_bytes

def validate_pdfa3_compliance(pdf_bytes):
    """
    Validate PDF/A-3 compliance using veraPDF
    """
    import subprocess
    import tempfile
    import json
    
    # Write PDF to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_file.write(pdf_bytes)
        temp_file_path = temp_file.name
    
    try:
        # Run veraPDF validation
        result = subprocess.run([
            'verapdf',
            '--format', 'json',
            '--flavour', 'pdfa-3b',
            temp_file_path
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            raise ValidationError(f"veraPDF execution failed: {result.stderr}")
        
        # Parse validation results
        validation_data = json.loads(result.stdout)
        
        if not validation_data['jobs'][0]['validationResult']['isCompliant']:
            errors = validation_data['jobs'][0]['validationResult']['details']
            raise ValidationError(f"PDF/A-3 validation failed: {errors}")
            
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)
```

### 2.3 Metadata Requirements

```python
def add_pdfa3_metadata(pdf_bytes, invoice_data):
    """
    Add required XMP metadata for PDF/A-3 compliance
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    import xml.etree.ElementTree as ET
    
    # XMP metadata template
    xmp_template = """
    <?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
    <x:xmpmeta xmlns:x="adobe:ns:meta/">
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description rdf:about=""
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:pdf="http://ns.adobe.com/pdf/1.3/"
                xmlns:pdfa="http://www.aiim.org/pdfa/ns/id/"
                xmlns:pdfaid="http://www.aiim.org/pdfaid/ns/id/"
                xmlns:fx="urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#">
                
                <dc:title>
                    <rdf:Alt>
                        <rdf:li xml:lang="en">Invoice {invoice_number}</rdf:li>
                    </rdf:Alt>
                </dc:title>
                
                <dc:creator>
                    <rdf:Seq>
                        <rdf:li>Factur-X Express</rdf:li>
                    </rdf:Seq>
                </dc:creator>
                
                <dc:description>
                    <rdf:Alt>
                        <rdf:li xml:lang="en">Factur-X compliant invoice</rdf:li>
                    </rdf:Alt>
                </dc:description>
                
                <pdf:Producer>Factur-X Express v1.0</pdf:Producer>
                
                <pdfaid:part>3</pdfaid:part>
                <pdfaid:conformance>B</pdfaid:conformance>
                
                <fx:ConformanceLevel>EXTENDED</fx:ConformanceLevel>
                <fx:DocumentFileName>factur-x-{invoice_number}.xml</fx:DocumentFileName>
                <fx:DocumentType>INVOICE</fx:DocumentType>
                <fx:Version>1.0</fx:Version>
            </rdf:Description>
        </rdf:RDF>
    </x:xmpmeta>
    <?xpacket end="w"?>
    """
    
    metadata = xmp_template.format(
        invoice_number=invoice_data['invoice_number']
    )
    
    return metadata
```

---

## GDPR Compliance

### 3.1 Data Protection Principles

#### Lawfulness, Fairness, and Transparency
- **Legal Basis**: Legitimate interest for invoice processing
- **Transparency**: Clear privacy policy and data usage notices
- **Fairness**: Data processing serves legitimate business purposes

#### Purpose Limitation
- **Primary Purpose**: Invoice generation and management
- **Secondary Purposes**: Analytics (anonymized), customer support
- **Prohibited Uses**: Marketing without consent, data selling

#### Data Minimization
- **Collect Only**: Data necessary for invoice generation
- **Retention**: Minimum required for legal/business purposes
- **Access**: Role-based access controls

### 3.2 Data Subject Rights Implementation

#### Right of Access (Article 15)
```python
def export_user_data(user_id):
    """
    Export all personal data for a user (GDPR Article 15)
    """
    user_data = {
        'personal_information': get_user_profile(user_id),
        'invoices': get_user_invoices(user_id),
        'templates': get_user_templates(user_id),
        'api_usage': get_user_api_logs(user_id),
        'support_tickets': get_user_support_data(user_id)
    }
    
    # Remove sensitive internal data
    sanitized_data = sanitize_export_data(user_data)
    
    return {
        'export_date': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'data': sanitized_data
    }
```

#### Right to Rectification (Article 16)
```python
def update_user_data(user_id, updates):
    """
    Allow users to correct their personal data
    """
    # Validate updates
    validate_user_updates(updates)
    
    # Update user profile
    user = get_user(user_id)
    for field, value in updates.items():
        if field in ALLOWED_USER_FIELDS:
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Log the change for audit
    log_data_change(user_id, 'rectification', updates)
```

#### Right to Erasure (Article 17)
```python
def delete_user_data(user_id, reason='user_request'):
    """
    Delete user data (Right to be forgotten)
    """
    # Check if deletion is legally required
    if not can_delete_user_data(user_id):
        raise ValidationError("Cannot delete data due to legal retention requirements")
    
    # Anonymize instead of delete for invoices (legal requirement)
    anonymize_user_invoices(user_id)
    
    # Delete personal data
    delete_user_profile(user_id)
    delete_user_templates(user_id)
    delete_user_api_keys(user_id)
    
    # Log deletion for audit
    log_data_deletion(user_id, reason)
```

#### Right to Data Portability (Article 20)
```python
def export_portable_data(user_id):
    """
    Export user data in machine-readable format
    """
    data = {
        'invoices': export_invoices_json(user_id),
        'templates': export_templates_json(user_id),
        'preferences': export_preferences_json(user_id)
    }
    
    return {
        'format': 'JSON',
        'version': '1.0',
        'exported_at': datetime.utcnow().isoformat(),
        'data': data
    }
```

### 3.3 Privacy by Design Implementation

#### Data Encryption
```python
# Encryption at rest
class EncryptedField(db.TypeDecorator):
    impl = db.Text
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_data(value)
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_data(value)
        return value

# Usage in models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    # Encrypt sensitive fields
    phone = db.Column(EncryptedField())
    address = db.Column(EncryptedField())
```

#### Audit Logging
```python
def log_data_access(user_id, data_type, action, details=None):
    """
    Log all data access for GDPR compliance
    """
    audit_log = AuditLog(
        user_id=user_id,
        data_type=data_type,
        action=action,
        details=details,
        timestamp=datetime.utcnow(),
        ip_address=get_client_ip(),
        user_agent=get_user_agent()
    )
    db.session.add(audit_log)
    db.session.commit()
```

---

## French E-invoicing Regulations

### 4.1 PPF/PDP Reform Overview

**Timeline:**
- **September 2026**: Mandatory reception of e-invoices
- **2026-2027**: Mandatory emission (phased by company size)
- **Large companies**: September 2026
- **Medium companies**: September 2027
- **Small companies**: September 2027

### 4.2 Technical Requirements

#### Factur-X Format Compliance
```python
def validate_french_requirements(invoice_data):
    """
    Validate French-specific requirements for e-invoicing
    """
    validations = []
    
    # French VAT number format
    if invoice_data.get('seller_country') == 'FR':
        vat_number = invoice_data.get('seller_vat_id')
        if not validate_french_vat_number(vat_number):
            validations.append("Invalid French VAT number format")
    
    # SIRET number requirement for French companies
    if invoice_data.get('seller_country') == 'FR':
        siret = invoice_data.get('seller_siret')
        if not siret or not validate_siret_number(siret):
            validations.append("SIRET number required for French companies")
    
    # French address format
    seller_address = invoice_data.get('seller_address', {})
    if seller_address.get('country') == 'FR':
        if not validate_french_postal_code(seller_address.get('postal_code')):
            validations.append("Invalid French postal code")
    
    return validations

def validate_french_vat_number(vat_number):
    """
    Validate French VAT number format (FR + 11 digits)
    """
    import re
    pattern = r'^FR[0-9A-Z]{2}[0-9]{9}$'
    return bool(re.match(pattern, vat_number))

def validate_siret_number(siret):
    """
    Validate French SIRET number (14 digits with Luhn algorithm)
    """
    if not siret or len(siret) != 14 or not siret.isdigit():
        return False
    
    # Luhn algorithm validation
    total = 0
    for i, digit in enumerate(siret):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n = n // 10 + n % 10
        total += n
    
    return total % 10 == 0
```

#### Digital Signature Requirements
```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography import x509

def sign_invoice_xml(xml_content, private_key, certificate):
    """
    Digitally sign invoice XML for French compliance
    """
    # Create XML signature according to XMLDSig standard
    from lxml import etree
    from signxml import XMLSigner
    
    # Parse XML
    root = etree.fromstring(xml_content.encode('utf-8'))
    
    # Sign the document
    signer = XMLSigner(
        method=signxml.methods.enveloped,
        signature_algorithm="rsa-sha256",
        digest_algorithm="sha256"
    )
    
    signed_root = signer.sign(
        root,
        key=private_key,
        cert=certificate
    )
    
    return etree.tostring(signed_root, encoding='unicode')

def verify_invoice_signature(signed_xml):
    """
    Verify digital signature of invoice XML
    """
    from signxml import XMLVerifier
    
    verifier = XMLVerifier()
    try:
        verified_data = verifier.verify(signed_xml)
        return True, "Signature valid"
    except Exception as e:
        return False, f"Signature verification failed: {str(e)}"
```

### 4.3 Archive Requirements

#### 6-Year Retention Policy
```python
def archive_invoice(invoice_id):
    """
    Archive invoice for 6-year retention requirement
    """
    invoice = get_invoice(invoice_id)
    
    # Create archive record
    archive_record = InvoiceArchive(
        invoice_id=invoice_id,
        original_pdf_hash=calculate_file_hash(invoice.pdf_url),
        original_xml_hash=calculate_file_hash(invoice.xml_data),
        archive_date=datetime.utcnow(),
        retention_until=datetime.utcnow() + timedelta(days=2190)  # 6 years
    )
    
    # Store in long-term storage
    archive_s3_key = f"archives/{invoice.created_at.year}/{invoice_id}"
    store_in_archive_storage(archive_s3_key, invoice)
    
    # Update invoice status
    invoice.archive_status = 'archived'
    invoice.archive_location = archive_s3_key
    
    db.session.add(archive_record)
    db.session.commit()

def retrieve_archived_invoice(invoice_id):
    """
    Retrieve invoice from archive for audit purposes
    """
    archive_record = InvoiceArchive.query.filter_by(invoice_id=invoice_id).first()
    if not archive_record:
        raise NotFoundError("Invoice not found in archive")
    
    # Retrieve from long-term storage
    archived_data = retrieve_from_archive_storage(archive_record.archive_location)
    
    # Verify integrity
    if not verify_archive_integrity(archived_data, archive_record):
        raise ValidationError("Archive integrity check failed")
    
    return archived_data
```

---

## Compliance Monitoring

### 5.1 Automated Compliance Checks

```python
def run_daily_compliance_checks():
    """
    Daily automated compliance monitoring
    """
    results = {
        'en16931_compliance': check_en16931_compliance(),
        'pdfa3_compliance': check_pdfa3_compliance(),
        'gdpr_compliance': check_gdpr_compliance(),
        'french_compliance': check_french_compliance()
    }
    
    # Generate compliance report
    report = generate_compliance_report(results)
    
    # Alert on failures
    if any(not result['passed'] for result in results.values()):
        send_compliance_alert(results)
    
    return report

def check_en16931_compliance():
    """
    Check EN 16931 compliance for recent invoices
    """
    recent_invoices = get_recent_invoices(days=1)
    failed_validations = []
    
    for invoice in recent_invoices:
        try:
            validate_en16931_xml(invoice.xml_data)
        except ValidationError as e:
            failed_validations.append({
                'invoice_id': invoice.id,
                'error': str(e)
            })
    
    return {
        'passed': len(failed_validations) == 0,
        'total_checked': len(recent_invoices),
        'failures': failed_validations
    }
```

### 5.2 Compliance Metrics Dashboard

```python
def get_compliance_metrics():
    """
    Generate compliance metrics for dashboard
    """
    return {
        'validation_success_rate': calculate_validation_success_rate(),
        'pdfa3_compliance_rate': calculate_pdfa3_compliance_rate(),
        'gdpr_request_response_time': calculate_gdpr_response_time(),
        'archive_integrity_status': check_archive_integrity_status(),
        'certificate_expiry_status': check_certificate_expiry()
    }

def calculate_validation_success_rate(days=30):
    """
    Calculate validation success rate over specified period
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total_validations = ValidationResult.query.filter(
        ValidationResult.validated_at >= start_date
    ).count()
    
    successful_validations = ValidationResult.query.filter(
        ValidationResult.validated_at >= start_date,
        ValidationResult.is_valid == True
    ).count()
    
    if total_validations == 0:
        return 100.0
    
    return (successful_validations / total_validations) * 100
```

---

## Audit Procedures

### 6.1 Internal Audit Checklist

#### Monthly Compliance Audit
- [ ] **EN 16931 Compliance**
  - [ ] Validation success rate > 99%
  - [ ] All mandatory fields present
  - [ ] Business rules correctly implemented
  - [ ] XML schema validation passing

- [ ] **PDF/A-3 Compliance**
  - [ ] veraPDF validation success rate > 99%
  - [ ] All fonts embedded
  - [ ] No transparency or encryption
  - [ ] Proper metadata inclusion

- [ ] **GDPR Compliance**
  - [ ] Data subject requests processed within 30 days
  - [ ] Audit logs complete and secure
  - [ ] Data retention policies enforced
  - [ ] Privacy policy up to date

- [ ] **French Regulations**
  - [ ] SIRET numbers validated for French companies
  - [ ] Digital signatures working correctly
  - [ ] Archive system operational
  - [ ] 6-year retention policy enforced

### 6.2 External Audit Preparation

```python
def prepare_audit_package(audit_type, start_date, end_date):
    """
    Prepare comprehensive audit package
    """
    package = {
        'metadata': {
            'audit_type': audit_type,
            'period': f"{start_date} to {end_date}",
            'generated_at': datetime.utcnow().isoformat(),
            'system_version': get_system_version()
        },
        'compliance_reports': generate_period_compliance_reports(start_date, end_date),
        'validation_logs': export_validation_logs(start_date, end_date),
        'audit_trails': export_audit_trails(start_date, end_date),
        'system_documentation': get_system_documentation(),
        'certificates': export_certificates(),
        'sample_invoices': generate_sample_invoices(start_date, end_date)
    }
    
    return package
```

### 6.3 Compliance Certification

#### EN 16931 Certification Process
1. **Self-Assessment**: Internal validation using test suite
2. **Third-Party Testing**: External validation service
3. **Documentation Review**: Compliance documentation audit
4. **Certification Issuance**: Official compliance certificate

#### Certification Maintenance
- **Quarterly Reviews**: Internal compliance checks
- **Annual Recertification**: Full external audit
- **Continuous Monitoring**: Automated compliance tracking
- **Incident Response**: Immediate action on compliance failures

---

**Document Owner:** Compliance Team  
**Last Updated:** $(date)  
**Next Review:** Quarterly  
**Stakeholders:** Legal Team, CTO, Product Manager, Quality Assurance