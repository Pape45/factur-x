# Factur-X Express - Code Style Guide

## General Principles

### Code Quality Standards
- **Readability**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns throughout the codebase
- **Maintainability**: Write code that is easy to modify and extend
- **Performance**: Consider performance implications, especially for invoice processing
- **Security**: Follow security best practices, especially for financial data

### Documentation
- Use clear, descriptive variable and function names
- Add docstrings/comments for complex business logic
- Document API endpoints with OpenAPI/Swagger
- Maintain README files for each package/app

## Python Code Style (FastAPI Backend)

### Formatting
- **Formatter**: Black with default settings (88 character line length)
- **Import Sorting**: isort with Black compatibility
- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)

### Naming Conventions
```python
# Variables and functions: snake_case
invoice_total = calculate_total_amount()
def generate_facturx_invoice():
    pass

# Classes: PascalCase
class InvoiceGenerator:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_INVOICE_AMOUNT = 10000
DEFAULT_CURRENCY = "EUR"

# Private methods: leading underscore
def _validate_invoice_data(self):
    pass

# File names: snake_case
# invoice_generator.py, facturx_validator.py
```

### Type Hints
```python
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

def calculate_tax_amount(
    net_amount: Decimal,
    tax_rate: Decimal,
    currency: str = "EUR"
) -> Decimal:
    """Calculate tax amount for invoice line item."""
    return net_amount * tax_rate

class Invoice:
    def __init__(
        self,
        invoice_number: str,
        issue_date: datetime,
        line_items: List[Dict[str, Any]]
    ) -> None:
        self.invoice_number = invoice_number
        self.issue_date = issue_date
        self.line_items = line_items
```

### Docstrings
```python
def generate_facturx_pdf(
    invoice_data: Dict[str, Any],
    template_path: str
) -> bytes:
    """
    Generate a Factur-X compliant PDF invoice.
    
    Args:
        invoice_data: Dictionary containing invoice information
        template_path: Path to the PDF template file
        
    Returns:
        bytes: The generated PDF as bytes
        
    Raises:
        ValidationError: If invoice data is invalid
        FileNotFoundError: If template file is not found
    """
    pass
```

### Error Handling
```python
from fastapi import HTTPException
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

try:
    result = process_invoice(invoice_data)
except ValidationError as e:
    logger.error(f"Invoice validation failed: {e}")
    raise HTTPException(status_code=400, detail="Invalid invoice data")
except Exception as e:
    logger.exception("Unexpected error processing invoice")
    raise HTTPException(status_code=500, detail="Internal server error")
```

## TypeScript/JavaScript Code Style (Frontend)

### Formatting
- **Formatter**: Prettier with these settings:
  - Semi-colons: true
  - Single quotes: true
  - Trailing commas: es5
  - Tab width: 2
  - Print width: 80

### Naming Conventions
```typescript
// Variables and functions: camelCase
const invoiceTotal = calculateTotalAmount();
function generateInvoicePreview() {}

// Classes and Components: PascalCase
class InvoiceService {}
const InvoiceForm: React.FC = () => {};

// Constants: UPPER_SNAKE_CASE
const MAX_INVOICE_AMOUNT = 10000;
const DEFAULT_CURRENCY = 'EUR';

// Interfaces and Types: PascalCase
interface InvoiceData {
  invoiceNumber: string;
  issueDate: Date;
  lineItems: LineItem[];
}

type InvoiceStatus = 'draft' | 'sent' | 'paid' | 'cancelled';

// File names: kebab-case
// invoice-form.tsx, api-client.ts
```

### React Component Structure
```typescript
import React, { useState, useEffect } from 'react';
import { Button } from '@facturx/ui';
import { InvoiceData } from '@facturx/types';

interface InvoiceFormProps {
  initialData?: InvoiceData;
  onSubmit: (data: InvoiceData) => void;
  isLoading?: boolean;
}

export const InvoiceForm: React.FC<InvoiceFormProps> = ({
  initialData,
  onSubmit,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<InvoiceData>(
    initialData || getDefaultInvoiceData()
  );

  useEffect(() => {
    // Effect logic here
  }, []);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form content */}
      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'Generating...' : 'Generate Invoice'}
      </Button>
    </form>
  );
};
```

### API Client Structure
```typescript
import axios, { AxiosResponse } from 'axios';
import { InvoiceData, InvoiceResponse } from '@facturx/types';

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async createInvoice(data: InvoiceData): Promise<InvoiceResponse> {
    try {
      const response: AxiosResponse<InvoiceResponse> = await axios.post(
        `${this.baseURL}/invoices`,
        data
      );
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create invoice: ${error.message}`);
    }
  }
}

export const apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL!);
```

## CSS/Styling Guidelines

### CSS Modules or Styled Components
```typescript
// Using CSS Modules
import styles from './InvoiceForm.module.css';

const InvoiceForm = () => (
  <div className={styles.container}>
    <h1 className={styles.title}>Create Invoice</h1>
  </div>
);

// Using Styled Components (if chosen)
import styled from 'styled-components';

const Container = styled.div`
  padding: 1rem;
  background-color: var(--background-color);
`;

const Title = styled.h1`
  font-size: 1.5rem;
  color: var(--primary-color);
`;
```

### CSS Custom Properties
```css
:root {
  /* Colors */
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Typography */
  --font-family-primary: 'Inter', sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
}
```

## Git Commit Conventions

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```
feat(invoice): add Factur-X PDF generation
fix(api): handle validation errors in invoice creation
docs(readme): update installation instructions
refactor(ui): extract reusable Button component
test(invoice): add unit tests for tax calculation
chore(deps): update FastAPI to v0.104.0
```

## Code Review Guidelines

### What to Look For
1. **Functionality**: Does the code work as intended?
2. **Security**: Are there any security vulnerabilities?
3. **Performance**: Are there performance bottlenecks?
4. **Maintainability**: Is the code easy to understand and modify?
5. **Testing**: Are there adequate tests?
6. **Documentation**: Is the code properly documented?

### Review Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Type safety maintained (TypeScript/Python type hints)

## Linting and Formatting Configuration

### Python (.flake8)
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.venv,migrations
```

### TypeScript (eslint.config.js)
```javascript
module.exports = {
  extends: [
    'next/core-web-vitals',
    '@typescript-eslint/recommended',
    'prettier'
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'prefer-const': 'error'
  }
};
```

### Prettier (.prettierrc)
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80
}
```