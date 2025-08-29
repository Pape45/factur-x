from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from ..models.invoice import Invoice
from ..models.business import get_business_config


class XMLGenerator:
    """Generator for Factur-X XML (CII format) compliant with EN 16931"""
    
    def __init__(self):
        # CII namespace definitions
        self.namespaces = {
            'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
            'qdt': 'urn:un:unece:uncefact:data:standard:QualifiedDataType:100',
            'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
        }
    
    def generate_cii_xml(self, invoice: Invoice) -> str:
        """Generate CII XML for Factur-X invoice"""
        # Create root element with namespaces
        root = Element('rsm:CrossIndustryInvoice')
        for prefix, uri in self.namespaces.items():
            root.set(f'xmlns:{prefix}', uri)
        
        # Add schema location
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:schemaLocation', 
                'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100 '
                'CrossIndustryInvoice_100pD16B.xsd')
        
        # Build document structure
        self._add_exchange_context(root, invoice)
        self._add_exchanged_document(root, invoice)
        self._add_supply_chain_trade_transaction(root, invoice)
        
        # Convert to pretty-printed string
        rough_string = tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent='  ', encoding=None)
    
    def _add_exchange_context(self, root: Element, invoice: Invoice) -> None:
        """Add ExchangedDocumentContext section"""
        context = SubElement(root, 'rsm:ExchangedDocumentContext')
        
        # Business process specified document context parameter
        business_process = SubElement(context, 'ram:BusinessProcessSpecifiedDocumentContextParameter')
        SubElement(business_process, 'ram:ID').text = 'A1'
        
        # Guideline specified document context parameter
        guideline = SubElement(context, 'ram:GuidelineSpecifiedDocumentContextParameter')
        SubElement(guideline, 'ram:ID').text = 'urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:basic'
    
    def _add_exchanged_document(self, root: Element, invoice: Invoice) -> None:
        """Add ExchangedDocument section"""
        document = SubElement(root, 'rsm:ExchangedDocument')
        
        # Document ID (invoice number)
        SubElement(document, 'ram:ID').text = invoice.invoice_number
        
        # Type code (380 = Commercial invoice)
        SubElement(document, 'ram:TypeCode').text = '380'
        
        # Issue date time
        issue_date_time = SubElement(document, 'ram:IssueDateTime')
        date_time_string = SubElement(issue_date_time, 'udt:DateTimeString')
        date_time_string.text = invoice.issue_date.strftime('%Y%m%d')
        date_time_string.set('format', '102')
        
        # Included note (optional but expected by schema)
        included_note = SubElement(document, 'ram:IncludedNote')
        SubElement(included_note, 'ram:Content').text = 'Commercial Invoice'
    
    def _add_supply_chain_trade_transaction(self, root: Element, invoice: Invoice) -> None:
        """Add SupplyChainTradeTransaction section"""
        transaction = SubElement(root, 'rsm:SupplyChainTradeTransaction')
        
        # Add invoice lines
        for line in invoice.invoice_lines:
            self._add_line_item(transaction, line)
        
        # Add applicable header trade agreement
        self._add_header_trade_agreement(transaction, invoice)
        
        # Add applicable header trade delivery
        self._add_header_trade_delivery(transaction, invoice)
        
        # Add applicable header trade settlement
        self._add_header_trade_settlement(transaction, invoice)
    
    def _add_line_item(self, transaction: Element, line) -> None:
        """Add individual line item"""
        line_item = SubElement(transaction, 'ram:IncludedSupplyChainTradeLineItem')
        
        # Associated document line document
        doc_line = SubElement(line_item, 'ram:AssociatedDocumentLineDocument')
        SubElement(doc_line, 'ram:LineID').text = str(line.line_id)
        
        # Specified trade product
        product = SubElement(line_item, 'ram:SpecifiedTradeProduct')
        SubElement(product, 'ram:Name').text = line.item_name
        
        # Line trade agreement
        line_agreement = SubElement(line_item, 'ram:SpecifiedLineTradeAgreement')
        
        # Net price product trade price
        net_price = SubElement(line_agreement, 'ram:NetPriceProductTradePrice')
        charge_amount = SubElement(net_price, 'ram:ChargeAmount')
        charge_amount.text = str(line.unit_price)
        charge_amount.set('currencyID', 'EUR')  # TODO: Get from invoice currency
        
        # Line trade delivery
        line_delivery = SubElement(line_item, 'ram:SpecifiedLineTradeDelivery')
        billed_quantity = SubElement(line_delivery, 'ram:BilledQuantity')
        billed_quantity.text = str(line.quantity)
        billed_quantity.set('unitCode', getattr(line, 'unit_code', 'C62'))  # Default to "one"
        
        # Line trade settlement
        line_settlement = SubElement(line_item, 'ram:SpecifiedLineTradeSettlement')
        
        # Applicable trade tax
        trade_tax = SubElement(line_settlement, 'ram:ApplicableTradeTax')
        SubElement(trade_tax, 'ram:TypeCode').text = 'VAT'
        SubElement(trade_tax, 'ram:CategoryCode').text = line.vat_category
        
        rate_applicable_percent = SubElement(trade_tax, 'ram:RateApplicablePercent')
        rate_applicable_percent.text = str(line.vat_rate)
        
        # Settlement monetary summation
        monetary_summation = SubElement(line_settlement, 'ram:SpecifiedTradeSettlementLineMonetarySummation')
        line_total = SubElement(monetary_summation, 'ram:LineTotalAmount')
        line_total.text = str(line.line_total_amount)
        line_total.set('currencyID', 'EUR')
    
    def _add_header_trade_agreement(self, transaction: Element, invoice: Invoice) -> None:
        """Add ApplicableHeaderTradeAgreement"""
        agreement = SubElement(transaction, 'ram:ApplicableHeaderTradeAgreement')
        
        # Buyer reference
        if invoice.order_reference:
            SubElement(agreement, 'ram:BuyerReference').text = invoice.order_reference
        
        # Seller trade party
        seller_party = SubElement(agreement, 'ram:SellerTradeParty')
        self._add_trade_party_info(seller_party, invoice.seller, 'seller')
        
        # Buyer trade party
        buyer_party = SubElement(agreement, 'ram:BuyerTradeParty')
        self._add_trade_party_info(buyer_party, invoice.buyer, 'buyer')
        
        # Contract referenced document (if contract reference exists)
        if invoice.contract_reference:
            contract_doc = SubElement(agreement, 'ram:ContractReferencedDocument')
            SubElement(contract_doc, 'ram:IssuerAssignedID').text = invoice.contract_reference
    
    def _add_header_trade_delivery(self, transaction: Element, invoice: Invoice) -> None:
        """Add ApplicableHeaderTradeDelivery"""
        delivery = SubElement(transaction, 'ram:ApplicableHeaderTradeDelivery')
        
        # Actual delivery supply chain event
        delivery_event = SubElement(delivery, 'ram:ActualDeliverySupplyChainEvent')
        occurrence_date = SubElement(delivery_event, 'ram:OccurrenceDateTime')
        
        # Use issue date as delivery date for services
        date_time = SubElement(occurrence_date, 'udt:DateTimeString')
        date_time.text = invoice.issue_date.strftime('%Y%m%d')
        date_time.set('format', '102')
    
    def _add_header_trade_settlement(self, transaction: Element, invoice: Invoice) -> None:
        """Add ApplicableHeaderTradeSettlement"""
        settlement = SubElement(transaction, 'ram:ApplicableHeaderTradeSettlement')
        
        # Invoice currency code
        SubElement(settlement, 'ram:InvoiceCurrencyCode').text = invoice.currency_code.value
        
        # Applicable trade tax (VAT breakdown)
        for vat_breakdown in invoice.vat_breakdown:
            trade_tax = SubElement(settlement, 'ram:ApplicableTradeTax')
            
            # Calculated amount (VAT amount)
            calculated_amount = SubElement(trade_tax, 'ram:CalculatedAmount')
            calculated_amount.text = str(vat_breakdown.vat_amount)
            calculated_amount.set('currencyID', invoice.currency_code.value)
            
            # Type code
            SubElement(trade_tax, 'ram:TypeCode').text = 'VAT'
            
            # Basis amount (taxable amount)
            basis_amount = SubElement(trade_tax, 'ram:BasisAmount')
            basis_amount.text = str(vat_breakdown.taxable_amount)
            basis_amount.set('currencyID', invoice.currency_code.value)
            
            # Category code
            SubElement(trade_tax, 'ram:CategoryCode').text = vat_breakdown.vat_category
            
            # Rate applicable percent
            if vat_breakdown.vat_rate > 0:
                rate_percent = SubElement(trade_tax, 'ram:RateApplicablePercent')
                rate_percent.text = str(vat_breakdown.vat_rate)
        
        # Specified trade payment terms
        if invoice.payment_terms:
            payment_terms = SubElement(settlement, 'ram:SpecifiedTradePaymentTerms')
            if invoice.payment_terms.payment_terms_description:
                SubElement(payment_terms, 'ram:Description').text = invoice.payment_terms.payment_terms_description
            
            # Due date
            if invoice.due_date:
                due_date_time = SubElement(payment_terms, 'ram:DueDateDateTime')
                due_date_string = SubElement(due_date_time, 'udt:DateTimeString')
                due_date_string.text = invoice.due_date.strftime('%Y%m%d')
                due_date_string.set('format', '102')
        
        # Specified trade settlement header monetary summation
        monetary_summation = SubElement(settlement, 'ram:SpecifiedTradeSettlementHeaderMonetarySummation')
        
        # Line total amount
        line_total = SubElement(monetary_summation, 'ram:LineTotalAmount')
        line_total.text = str(invoice.totals.line_total_amount)
        line_total.set('currencyID', invoice.currency_code.value)
        
        # Tax basis total amount
        tax_basis = SubElement(monetary_summation, 'ram:TaxBasisTotalAmount')
        tax_basis.text = str(invoice.totals.tax_exclusive_amount)
        tax_basis.set('currencyID', invoice.currency_code.value)
        
        # Tax total amount
        tax_total = SubElement(monetary_summation, 'ram:TaxTotalAmount')
        total_vat = sum(vat.vat_amount for vat in invoice.vat_breakdown)
        tax_total.text = str(total_vat)
        tax_total.set('currencyID', invoice.currency_code.value)
        
        # Grand total amount
        grand_total = SubElement(monetary_summation, 'ram:GrandTotalAmount')
        grand_total.text = str(invoice.totals.tax_inclusive_amount)
        grand_total.set('currencyID', invoice.currency_code.value)
        
        # Due payable amount
        due_payable = SubElement(monetary_summation, 'ram:DuePayableAmount')
        due_payable.text = str(invoice.totals.payable_amount)
        due_payable.set('currencyID', invoice.currency_code.value)
        
        # Invoice referenced document
        invoice_doc = SubElement(settlement, 'ram:InvoiceReferencedDocument')
        SubElement(invoice_doc, 'ram:IssuerAssignedID').text = invoice.invoice_number
        
        # Issue date time
        issue_date_time = SubElement(invoice_doc, 'ram:FormattedIssueDateTime')
        issue_date_string = SubElement(issue_date_time, 'qdt:DateTimeString')
        issue_date_string.text = invoice.issue_date.strftime('%Y%m%d')
        issue_date_string.set('format', '102')
    
    def _add_trade_party_info(self, party_element: Element, party, party_type: str) -> None:
        """Add trade party information (seller or buyer)"""
        # Party ID (optional but helps with schema validation)
        party_id = SubElement(party_element, 'ram:ID')
        party_id.text = getattr(party, 'party_id', f'{party_type.upper()}_001')
        
        # Party name
        SubElement(party_element, 'ram:Name').text = party.name
        
        # Postal trade address
        if party.address:
            postal_address = SubElement(party_element, 'ram:PostalTradeAddress')
            
            if party.address.street:
                SubElement(postal_address, 'ram:LineOne').text = party.address.street
            
            if party.address.city:
                SubElement(postal_address, 'ram:CityName').text = party.address.city
            
            if party.address.country:
                SubElement(postal_address, 'ram:CountryID').text = party.address.country.value
        
        # Tax registration
        if party.tax_registration and party.tax_registration.vat_number:
            tax_registration = SubElement(party_element, 'ram:SpecifiedTaxRegistration')
            tax_id = SubElement(tax_registration, 'ram:ID')
            tax_id.text = party.tax_registration.vat_number
            tax_id.set('schemeID', 'VA')
        
        # Legal registration (for seller) - removed as it's causing validation issues
        
        # Contact information
        if party.contact_name or party.contact_phone or party.contact_email:
            contact = SubElement(party_element, 'ram:DefinedTradeContact')
            
            if party.contact_name:
                SubElement(contact, 'ram:PersonName').text = party.contact_name
            
            if party.contact_phone:
                telephone = SubElement(contact, 'ram:TelephoneUniversalCommunication')
                SubElement(telephone, 'ram:CompleteNumber').text = party.contact_phone
            
            if party.contact_email:
                email = SubElement(contact, 'ram:EmailURIUniversalCommunication')
                SubElement(email, 'ram:URIID').text = party.contact_email
    
    def validate_xml_structure(self, xml_content: str) -> Dict[str, Any]:
        """Validate the generated XML structure"""
        try:
            from xml.etree.ElementTree import fromstring
            root = fromstring(xml_content)
            
            # Basic validation checks
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check required elements
            required_elements = [
                './/rsm:ExchangedDocumentContext',
                './/rsm:SupplyChainTradeTransaction',
                './/ram:SellerTradeParty',
                './/ram:BuyerTradeParty'
            ]
            
            for element_path in required_elements:
                if root.find(element_path, self.namespaces) is None:
                    validation_result['errors'].append(f'Missing required element: {element_path}')
                    validation_result['is_valid'] = False
            
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f'XML parsing error: {str(e)}'],
                'warnings': []
            }