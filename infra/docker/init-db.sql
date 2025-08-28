-- Factur-X Database Initialization Script
-- PostgreSQL 16 compatible schema for invoice management

-- Enable UUID extension for generating unique IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE currency_code AS ENUM (
    'EUR', 'USD', 'GBP', 'CHF'
);

CREATE TYPE country_code AS ENUM (
    'FR', 'DE', 'IT', 'ES', 'BE', 'NL', 'LU', 'AT', 'PT', 'IE',
    'FI', 'GR', 'CY', 'EE', 'LV', 'LT', 'MT', 'SK', 'SI', 'HR',
    'BG', 'RO', 'CZ', 'HU', 'PL', 'DK', 'SE', 'US', 'GB', 'CH'
);

CREATE TYPE vat_category AS ENUM (
    'S',   -- Standard rate
    'Z',   -- Zero rated
    'E',   -- Exempt from VAT
    'AE',  -- Reverse charge
    'AA',  -- Reduced rate
    'AB'   -- Super reduced rate
);

CREATE TYPE invoice_type AS ENUM (
    '380', -- Commercial invoice
    '381', -- Credit note
    '383', -- Debit note
    '384'  -- Corrective invoice
);

CREATE TYPE payment_means AS ENUM (
    '30',  -- Credit transfer
    '49',  -- Direct debit
    '54',  -- Payment card
    '10',  -- In cash
    '20'   -- Cheque
);

-- Create addresses table
CREATE TABLE addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    street VARCHAR(200) NOT NULL,
    additional_street VARCHAR(200),
    city VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country_subdivision VARCHAR(100),
    country country_code NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create parties table (for both sellers and buyers)
CREATE TABLE parties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    trading_name VARCHAR(200),
    address_id UUID NOT NULL REFERENCES addresses(id) ON DELETE CASCADE,
    
    -- Tax registration
    vat_number VARCHAR(30),
    tax_registration_id VARCHAR(30),
    tax_scheme VARCHAR(20) DEFAULT 'VAT',
    
    -- Legal registration
    registration_name VARCHAR(200),
    company_id VARCHAR(50),
    company_legal_form VARCHAR(100),
    
    -- Contact information
    contact_name VARCHAR(100),
    contact_phone VARCHAR(50),
    contact_email VARCHAR(100),
    electronic_address VARCHAR(200),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create bank accounts table
CREATE TABLE bank_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    iban VARCHAR(34),
    bic VARCHAR(11),
    account_name VARCHAR(200),
    bank_name VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create invoices table
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    invoice_type invoice_type NOT NULL DEFAULT '380',
    issue_date DATE NOT NULL,
    due_date DATE,
    currency_code currency_code NOT NULL DEFAULT 'EUR',
    
    -- Parties
    seller_id UUID NOT NULL REFERENCES parties(id),
    buyer_id UUID NOT NULL REFERENCES parties(id),
    
    -- Payment information
    payment_means_code payment_means,
    payment_terms_description TEXT,
    payment_reference VARCHAR(100),
    bank_account_id UUID REFERENCES bank_accounts(id),
    
    -- Additional information
    order_reference VARCHAR(100),
    contract_reference VARCHAR(100),
    project_reference VARCHAR(100),
    invoice_note TEXT,
    
    -- Preceding invoice (for credit notes)
    preceding_invoice_number VARCHAR(50),
    preceding_invoice_date DATE,
    
    -- Totals
    line_total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    allowance_total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    charge_total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_exclusive_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    tax_inclusive_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    prepaid_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    payable_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create invoice lines table
CREATE TABLE invoice_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    line_id VARCHAR(50) NOT NULL,
    item_name VARCHAR(200) NOT NULL,
    item_description TEXT,
    quantity DECIMAL(15,3) NOT NULL CHECK (quantity > 0),
    unit_of_measure VARCHAR(10) NOT NULL DEFAULT 'C62',
    unit_price DECIMAL(15,2) NOT NULL CHECK (unit_price >= 0),
    line_total_amount DECIMAL(15,2) NOT NULL CHECK (line_total_amount >= 0),
    vat_category vat_category NOT NULL,
    vat_rate DECIMAL(5,2) NOT NULL CHECK (vat_rate >= 0 AND vat_rate <= 100),
    item_classification VARCHAR(100),
    origin_country country_code,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(invoice_id, line_id)
);

-- Create VAT breakdown table
CREATE TABLE vat_breakdown (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    vat_category vat_category NOT NULL,
    vat_rate DECIMAL(5,2) NOT NULL CHECK (vat_rate >= 0 AND vat_rate <= 100),
    taxable_amount DECIMAL(15,2) NOT NULL CHECK (taxable_amount >= 0),
    vat_amount DECIMAL(15,2) NOT NULL CHECK (vat_amount >= 0),
    vat_exemption_reason TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(invoice_id, vat_category, vat_rate)
);

-- Create indexes for better performance
CREATE INDEX idx_invoices_invoice_number ON invoices(invoice_number);
CREATE INDEX idx_invoices_issue_date ON invoices(issue_date);
CREATE INDEX idx_invoices_seller_id ON invoices(seller_id);
CREATE INDEX idx_invoices_buyer_id ON invoices(buyer_id);
CREATE INDEX idx_invoice_lines_invoice_id ON invoice_lines(invoice_id);
CREATE INDEX idx_vat_breakdown_invoice_id ON vat_breakdown(invoice_id);
CREATE INDEX idx_parties_vat_number ON parties(vat_number) WHERE vat_number IS NOT NULL;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_addresses_updated_at BEFORE UPDATE ON addresses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_parties_updated_at BEFORE UPDATE ON parties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at BEFORE UPDATE ON invoices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample business configuration (seller)
INSERT INTO addresses (id, street, city, postal_code, country) VALUES 
('550e8400-e29b-41d4-a716-446655440000', '42 Avenue des Champs-Élysées', 'Paris', '75008', 'FR');

INSERT INTO parties (id, name, address_id, vat_number, company_id, company_legal_form, contact_email, contact_phone) VALUES 
('550e8400-e29b-41d4-a716-446655440001', 'Factur-X Express SAS', '550e8400-e29b-41d4-a716-446655440000', 'FR12345678901', '123456789', 'SAS', 'contact@facturx-express.fr', '+33 1 23 45 67 89');

-- Create sequence for invoice numbering
CREATE SEQUENCE invoice_number_seq START 1;

-- Create function to generate invoice numbers
CREATE OR REPLACE FUNCTION generate_invoice_number()
RETURNS TEXT AS $$
DECLARE
    next_num INTEGER;
    year_part TEXT;
BEGIN
    next_num := nextval('invoice_number_seq');
    year_part := EXTRACT(YEAR FROM CURRENT_DATE)::TEXT;
    RETURN 'FX-' || year_part || '-' || LPAD(next_num::TEXT, 6, '0');
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- Create read-only user for reporting
CREATE USER facturx_readonly WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE facturx TO facturx_readonly;
GRANT USAGE ON SCHEMA public TO facturx_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO facturx_readonly;

COMMIT;