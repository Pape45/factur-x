# Factur-X Express - Technology Stack

## Programming Languages
- **Python 3.11**: Backend API development with FastAPI
- **TypeScript/JavaScript**: Frontend development with Next.js
- **Java 21**: Integration with Mustangproject for Factur-X processing

## Frontend Stack
- **Framework**: Next.js (React-based)
- **Language**: TypeScript
- **Styling**: Modern CSS/Tailwind CSS (to be determined)
- **UI Components**: Shared UI package within monorepo

## Backend Stack
- **Framework**: FastAPI (Python)
- **API**: RESTful APIs with OpenAPI documentation
- **Authentication**: JWT-based authentication (implementation TBD)
- **Validation**: Pydantic for data validation

## Database
- **Primary**: PostgreSQL 15+
- **ORM**: SQLAlchemy (Python) or Prisma (if Node.js components)
- **Migrations**: Alembic for database schema management

## Factur-X Specific Libraries
- **Python**: `factur-x` library for invoice generation and processing
- **Java**: Mustangproject for advanced Factur-X operations
- **Validation**: veraPDF for PDF/A compliance validation
- **XML Processing**: Libraries for handling UBL/CII XML formats

## Infrastructure & DevOps
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose for local development
- **Web Server**: Nginx for reverse proxy and static file serving
- **Process Management**: Supervisor or similar for production

## Development Tools
- **Package Management**: 
  - Python: Poetry or pip with requirements.txt
  - Node.js: npm or yarn
  - Java: Maven or Gradle
- **Code Quality**: ESLint, Prettier, Black, isort
- **Testing**: pytest (Python), Jest (JavaScript), JUnit (Java)
- **Type Checking**: mypy (Python), TypeScript compiler

## Deployment Environment
- **Development**: macOS Apple Silicon
- **Production**: Oracle VPS Ubuntu 24.04 ARM
- **Runtime**: Node.js 20 LTS, Python 3.11, Java 21

## Monorepo Structure
```
facturx-express/
├── apps/
│   ├── frontend/          # Next.js application
│   ├── backend/           # FastAPI application
│   └── worker/            # Optional background worker
├── packages/
│   ├── ui/                # Shared UI components
│   ├── config/            # Shared configuration
│   └── types/             # Shared TypeScript types
├── infrastructure/
│   ├── docker/            # Docker configurations
│   └── nginx/             # Nginx configurations
└── tools/
    ├── scripts/           # Build and deployment scripts
    └── ci/                # CI/CD configurations
```