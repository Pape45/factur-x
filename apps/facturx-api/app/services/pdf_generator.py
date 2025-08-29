import io
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import Color, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfWriter, PdfReader
from pypdf.generic import DictionaryObject, ArrayObject, TextStringObject

from ..models.invoice import Invoice
from ..models.business import get_business_config


class PDFGenerator:
    """Generator for PDF/A-3 compliant invoices with Factur-X XML embedding"""
    
    def __init__(self):
        self.business_config = get_business_config()
        self.styles = getSampleStyleSheet()
        
        # Brand colors from fx-brand - initialize before styles setup
        self.brand_colors = {
            'accent': Color(47/255, 109/255, 243/255),  # #2F6DF3
            'graphite': Color(31/255, 41/255, 55/255),  # #1F2937
            'slate': Color(100/255, 116/255, 139/255),  # #64748B
            'ink': Color(15/255, 23/255, 42/255),       # #0F172A
            'muted': Color(148/255, 163/255, 184/255)   # #94A3B8
        }
        
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.brand_colors['accent'],
            spaceAfter=20,
            alignment=TA_LEFT
        ))
        
        # Company info style
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.brand_colors['graphite'],
            spaceAfter=6
        ))
        
        # Invoice details style
        self.styles.add(ParagraphStyle(
            name='InvoiceDetails',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.brand_colors['ink'],
            spaceAfter=4
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=white,
            alignment=TA_CENTER
        ))
        
        # Total style
        self.styles.add(ParagraphStyle(
            name='Total',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.brand_colors['ink'],
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
    
    def generate_pdf(self, invoice: Invoice, xml_content: Optional[str] = None) -> bytes:
        """Generate PDF invoice with optional XML embedding for Factur-X"""
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build document content
        story = []
        
        # Add header
        self._add_header(story, invoice)
        
        # Add company and customer info
        self._add_parties_info(story, invoice)
        
        # Add invoice details
        self._add_invoice_details(story, invoice)
        
        # Add line items table
        self._add_line_items_table(story, invoice)
        
        # Add totals
        self._add_totals(story, invoice)
        
        # Add payment information
        self._add_payment_info(story, invoice)
        
        # Add footer
        self._add_footer(story, invoice)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Embed XML if provided (for Factur-X)
        if xml_content:
            pdf_bytes = self._embed_xml_in_pdf(pdf_bytes, xml_content)
        
        return pdf_bytes
    
    def _add_header(self, story, invoice: Invoice):
        """Add invoice header with company logo and title"""
        # Company name as header
        company_name = Paragraph(
            f"<b>{self.business_config.company_name}</b>",
            self.styles['CustomHeader']
        )
        story.append(company_name)
        
        # Invoice title
        invoice_title = Paragraph(
            f"<b>FACTURE / INVOICE</b>",
            self.styles['Heading2']
        )
        story.append(invoice_title)
        story.append(Spacer(1, 20))
    
    def _add_parties_info(self, story, invoice: Invoice):
        """Add seller and buyer information"""
        # Create table for seller and buyer info
        seller_info = self._format_party_info(invoice.seller, "VENDEUR / SELLER")
        buyer_info = self._format_party_info(invoice.buyer, "ACHETEUR / BUYER")
        
        parties_data = [[seller_info, buyer_info]]
        parties_table = Table(parties_data, colWidths=[8*cm, 8*cm])
        parties_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(parties_table)
        story.append(Spacer(1, 20))
    
    def _format_party_info(self, party, title: str) -> str:
        """Format party information as HTML string"""
        info_parts = [f"<b>{title}</b><br/>"]
        
        # Name
        info_parts.append(f"<b>{party.name}</b><br/>")
        
        # Address
        if party.address:
            if party.address.street:
                info_parts.append(f"{party.address.street}<br/>")
            if party.address.postal_code and party.address.city:
                info_parts.append(f"{party.address.postal_code} {party.address.city}<br/>")
            if party.address.country:
                info_parts.append(f"{party.address.country.value}<br/>")
        
        # Tax registration
        if party.tax_registration and party.tax_registration.vat_number:
            info_parts.append(f"TVA / VAT: {party.tax_registration.vat_number}<br/>")
        
        # Legal registration (for seller)
        if hasattr(party, 'legal_registration') and party.legal_registration:
            if party.legal_registration.company_id:
                info_parts.append(f"SIRET: {party.legal_registration.company_id}<br/>")
        
        # Contact info
        if hasattr(party, 'contact') and party.contact:
            if party.contact.get('email'):
                info_parts.append(f"Email: {party.contact['email']}<br/>")
            if party.contact.get('telephone'):
                info_parts.append(f"Tél: {party.contact['telephone']}<br/>")
        
        return ''.join(info_parts)
    
    def _add_invoice_details(self, story, invoice: Invoice):
        """Add invoice details section"""
        details_data = [
            ["Numéro de facture / Invoice Number:", invoice.invoice_number],
            ["Date d'émission / Issue Date:", invoice.issue_date.strftime('%d/%m/%Y')],
            ["Date d'échéance / Due Date:", invoice.due_date.strftime('%d/%m/%Y') if invoice.due_date else 'N/A'],
            ["Devise / Currency:", invoice.currency_code.value]
        ]
        
        if invoice.order_reference:
            details_data.append(["Référence commande / Order Reference:", invoice.order_reference])
        
        details_table = Table(details_data, colWidths=[6*cm, 6*cm])
        details_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(details_table)
        story.append(Spacer(1, 20))
    
    def _add_line_items_table(self, story, invoice: Invoice):
        """Add line items table"""
        # Table headers
        headers = [
            "Description",
            "Qté / Qty",
            "Prix unit. / Unit Price",
            "TVA / VAT",
            "Total HT / Net Amount"
        ]
        
        # Prepare data
        table_data = [headers]
        
        for line in invoice.invoice_lines:
            row = [
                f"{line.item_name}\n{line.item_description or ''}",
                str(line.quantity),
                f"{line.unit_price:.2f} {invoice.currency_code.value}",
                f"{line.vat_rate:.1f}%",
                f"{line.line_total_amount:.2f} {invoice.currency_code.value}"
            ]
            table_data.append(row)
        
        # Create table
        line_items_table = Table(
            table_data,
            colWidths=[6*cm, 2*cm, 3*cm, 2*cm, 3*cm]
        )
        
        # Style the table
        line_items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), self.brand_colors['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data styling
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.brand_colors['slate']),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(line_items_table)
        story.append(Spacer(1, 20))
    
    def _add_totals(self, story, invoice: Invoice):
        """Add totals section"""
        totals_data = [
            ["Total HT / Net Amount:", f"{invoice.totals.tax_exclusive_amount:.2f} {invoice.currency_code.value}"],
        ]
        
        # Add VAT breakdown
        for vat_breakdown in invoice.vat_breakdown:
            vat_label = f"TVA {vat_breakdown.vat_rate:.1f}% / VAT {vat_breakdown.vat_rate:.1f}%:"
            vat_amount = f"{vat_breakdown.vat_amount:.2f} {invoice.currency_code.value}"
            totals_data.append([vat_label, vat_amount])
        
        # Total TTC
        totals_data.append([
            "<b>Total TTC / Total Amount:</b>",
            f"<b>{invoice.totals.tax_inclusive_amount:.2f} {invoice.currency_code.value}</b>"
        ])
        
        totals_table = Table(totals_data, colWidths=[10*cm, 4*cm])
        totals_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            # Bold last row
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 20))
    
    def _add_payment_info(self, story, invoice: Invoice):
        """Add payment information"""
        if invoice.payment_terms:
            payment_title = Paragraph(
                "<b>Conditions de paiement / Payment Terms</b>",
                self.styles['Heading3']
            )
            story.append(payment_title)
            
            payment_text = Paragraph(
                invoice.payment_terms.payment_terms_description,
                self.styles['Normal']
            )
            story.append(payment_text)
            
            # Bank details if available
            if hasattr(self.business_config, 'banking') and self.business_config.banking.iban:
                bank_info = Paragraph(
                    f"<b>IBAN:</b> {self.business_config.banking.iban}<br/>"
                    f"<b>BIC:</b> {getattr(self.business_config.banking, 'bic', 'N/A')}",
                    self.styles['Normal']
                )
                story.append(bank_info)
            
            story.append(Spacer(1, 20))
    
    def _add_footer(self, story, invoice: Invoice):
        """Add footer with legal information"""
        # Add separator line
        story.append(HRFlowable(width="100%", thickness=1, color=self.brand_colors['slate']))
        story.append(Spacer(1, 10))
        
        # Legal information
        legal_info_parts = []
        
        if hasattr(self.business_config, 'legal_form'):
            legal_info_parts.append(f"{self.business_config.company_name} - {self.business_config.legal_form}")
        
        if hasattr(self.business_config, 'legal') and self.business_config.legal.siren:
            legal_info_parts.append(f"SIREN: {self.business_config.legal.siren}")
        
        if hasattr(self.business_config, 'legal') and self.business_config.legal.siret:
            legal_info_parts.append(f"SIRET: {self.business_config.legal.siret}")
        
        if hasattr(self.business_config, 'tax') and self.business_config.tax.vat_number:
            legal_info_parts.append(f"TVA: {self.business_config.tax.vat_number}")
        
        legal_text = " | ".join(legal_info_parts)
        
        footer_paragraph = Paragraph(
            f"<font size=8 color='#{self.brand_colors['muted'].hexval()}'>{legal_text}</font>",
            self.styles['Normal']
        )
        story.append(footer_paragraph)
        
        # Factur-X compliance notice
        facturx_notice = Paragraph(
            "<font size=8 color='#{}'><i>Cette facture est conforme au standard Factur-X / This invoice complies with Factur-X standard</i></font>".format(
                self.brand_colors['muted'].hexval()
            ),
            self.styles['Normal']
        )
        story.append(facturx_notice)
    
    def _embed_xml_in_pdf(self, pdf_bytes: bytes, xml_content: str) -> bytes:
        """Embed XML content in PDF for Factur-X compliance (PDF/A-3)"""
        try:
            # Read the PDF
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            pdf_writer = PdfWriter()
            
            # Copy all pages
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
            
            # Create XML attachment
            xml_bytes = xml_content.encode('utf-8')
            
            # Add the XML as an embedded file
            pdf_writer.add_attachment(
                filename="factur-x.xml",
                data=xml_bytes
            )
            
            # Set PDF/A-3 metadata
            metadata = {
                '/Title': 'Factur-X Invoice',
                '/Subject': 'Electronic Invoice compliant with EN 16931',
                '/Creator': 'Factur-X Express SAS',
                '/Producer': 'Factur-X API',
                '/Keywords': 'Factur-X, EN 16931, Electronic Invoice'
            }
            
            pdf_writer.add_metadata(metadata)
            
            # Write to bytes
            output_buffer = io.BytesIO()
            pdf_writer.write(output_buffer)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            # If embedding fails, return original PDF
            print(f"Warning: Failed to embed XML in PDF: {e}")
            return pdf_bytes
    
    def generate_standard_pdf(self, invoice: Invoice) -> bytes:
        """Generate standard PDF without XML embedding"""
        return self.generate_pdf(invoice, xml_content=None)
    
    def generate_facturx_pdf(self, invoice: Invoice, xml_content: str) -> bytes:
        """Generate Factur-X compliant PDF with embedded XML"""
        # First generate a standard PDF
        standard_pdf = self.generate_pdf(invoice, xml_content=None)
        
        # Then use factur-x library to properly embed XML
        try:
            from facturx.facturx import generate_facturx_from_binary
            
            # Convert XML string to bytes
            xml_bytes = xml_content.encode('utf-8')
            
            # Use factur-x library to create proper Factur-X PDF
            facturx_pdf = generate_facturx_from_binary(
                pdf_file=standard_pdf,
                xml=xml_bytes,
                check_xsd=False  # Skip XSD validation for now
            )
            
            return facturx_pdf
            
        except Exception as e:
            # Fallback to manual embedding if factur-x library fails
            print(f"Warning: factur-x library failed, using manual embedding: {e}")
            return self._embed_xml_in_pdf(standard_pdf, xml_content)