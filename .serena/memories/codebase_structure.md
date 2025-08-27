# Factur-X Express - Codebase Structure

## Current Project Structure
```
facturx/
├── .github/
│   └── instructions/           # Development guidelines and best practices
│       ├── containerization-docker-best-practices.instructions.md
│       ├── devops-core-principles.instructions.md
│       ├── github-actions-ci-cd-best-practices.instructions.md
│       └── performance-optimization.instructions.md
├── .serena/
│   ├── memories/              # Serena AI memory files
│   └── project.yml            # Serena project configuration
├── .python-version            # Python version specification (3.11)
├── facturx_express_prompt.md  # Main project requirements and specifications
├── pyproject.toml            # Python project configuration
└── README.md                 # Project documentation (currently empty)
```

## Planned Monorepo Structure

Based on the project requirements, the following structure should be implemented:

```
facturx-express/
├── .github/
│   ├── workflows/             # GitHub Actions CI/CD pipelines
│   │   ├── ci.yml            # Continuous Integration
│   │   ├── cd.yml            # Continuous Deployment
│   │   └── security.yml      # Security scanning
│   └── instructions/          # Development guidelines (existing)
│
├── apps/
│   ├── frontend/             # Next.js application
│   │   ├── src/
│   │   │   ├── pages/        # Next.js pages
│   │   │   ├── components/   # React components
│   │   │   ├── hooks/        # Custom React hooks
│   │   │   ├── utils/        # Utility functions
│   │   │   └── styles/       # CSS/styling files
│   │   ├── public/           # Static assets
│   │   ├── package.json
│   │   ├── next.config.js
│   │   └── tsconfig.json
│   │
│   ├── backend/              # FastAPI application
│   │   ├── src/
│   │   │   ├── api/          # API routes and endpoints
│   │   │   ├── core/         # Core application logic
│   │   │   ├── models/       # Database models
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   ├── services/     # Business logic services
│   │   │   ├── utils/        # Utility functions
│   │   │   └── main.py       # FastAPI application entry point
│   │   ├── tests/            # Backend tests
│   │   ├── alembic/          # Database migrations
│   │   ├── requirements.txt  # Python dependencies
│   │   └── pyproject.toml    # Python project configuration
│   │
│   └── worker/               # Optional background worker
│       ├── src/
│       │   ├── tasks/        # Background tasks
│       │   ├── processors/   # Data processors
│       │   └── main.py       # Worker entry point
│       └── requirements.txt
│
├── packages/
│   ├── ui/                   # Shared UI components
│   │   ├── src/
│   │   │   ├── components/   # Reusable React components
│   │   │   ├── hooks/        # Shared React hooks
│   │   │   └── styles/       # Shared styling
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── config/               # Shared configuration
│   │   ├── src/
│   │   │   ├── env/          # Environment configurations
│   │   │   ├── constants/    # Application constants
│   │   │   └── schemas/      # Shared data schemas
│   │   └── package.json
│   │
│   └── types/                # Shared TypeScript types
│       ├── src/
│       │   ├── api/          # API type definitions
│       │   ├── models/       # Data model types
│       │   └── common/       # Common type definitions
│       ├── package.json
│       └── tsconfig.json
│
├── infrastructure/
│   ├── docker/               # Docker configurations
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.frontend
│   │   ├── Dockerfile.worker
│   │   └── docker-compose.yml
│   │
│   ├── nginx/                # Nginx configurations
│   │   ├── nginx.conf
│   │   ├── sites-available/
│   │   └── ssl/
│   │
│   └── k8s/                  # Kubernetes manifests (if needed)
│       ├── deployments/
│       ├── services/
│       └── ingress/
│
├── tools/
│   ├── scripts/              # Build and deployment scripts
│   │   ├── build.sh
│   │   ├── deploy.sh
│   │   ├── setup.sh
│   │   └── test.sh
│   │
│   └── ci/                   # CI/CD configurations
│       ├── lint.sh
│       ├── test.sh
│       └── security-scan.sh
│
├── docs/                     # Project documentation
│   ├── api/                  # API documentation
│   ├── architecture/         # Architecture diagrams and docs
│   ├── deployment/           # Deployment guides
│   └── user-guide/           # User documentation
│
├── tests/                    # Integration and E2E tests
│   ├── integration/          # Integration tests
│   ├── e2e/                  # End-to-end tests
│   └── fixtures/             # Test data and fixtures
│
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── .python-version          # Python version specification
├── docker-compose.yml       # Development Docker Compose
├── docker-compose.prod.yml  # Production Docker Compose
├── package.json             # Root package.json for monorepo
├── pyproject.toml           # Python project configuration
├── README.md                # Project documentation
└── workspace.json           # Workspace configuration (if using Nx)
```

## Key Directories Explained

### `/apps/`
Contains the main applications:
- **frontend**: Next.js React application for user interface
- **backend**: FastAPI Python application for API services
- **worker**: Optional background processing service

### `/packages/`
Shared packages used across applications:
- **ui**: Reusable React components and styling
- **config**: Shared configuration and constants
- **types**: TypeScript type definitions

### `/infrastructure/`
Deployment and infrastructure configurations:
- **docker**: Container definitions and orchestration
- **nginx**: Web server and reverse proxy configuration
- **k8s**: Kubernetes manifests for container orchestration

### `/tools/`
Development and deployment utilities:
- **scripts**: Automation scripts for common tasks
- **ci**: CI/CD pipeline configurations

## File Naming Conventions

### Python Files
- Use snake_case for file and directory names
- Use descriptive names: `invoice_generator.py`, `facturx_validator.py`
- Test files: `test_invoice_generator.py`

### JavaScript/TypeScript Files
- Use kebab-case for file names: `invoice-form.tsx`, `api-client.ts`
- Use PascalCase for React components: `InvoiceForm.tsx`
- Use camelCase for utility functions: `formatCurrency.ts`

### Configuration Files
- Use lowercase with dots: `docker-compose.yml`, `.env.example`
- Use descriptive prefixes: `Dockerfile.backend`, `nginx.conf`

## Import/Export Patterns

### Python
```python
# Absolute imports from project root
from src.api.routes import invoices
from src.services.facturx import InvoiceGenerator
from src.models.invoice import Invoice
```

### TypeScript
```typescript
// Relative imports for local files
import { InvoiceForm } from './components/InvoiceForm'
// Package imports
import { Button } from '@facturx/ui'
import { InvoiceSchema } from '@facturx/types'
```