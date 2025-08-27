# Factur-X Express

A professional micro-SaaS for generating, validating, and exporting Factur-X invoices (PDF/A-3 + XML CII) compliant with EN 16931.

## Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd facturx

# Install dependencies
make install

# Start development environment
make dev
```

## Architecture

This is a monorepo containing:

- `/apps/web` - Next.js 14 frontend with Tailwind CSS and shadcn/ui
- `/apps/facturx-api` - FastAPI backend for Factur-X generation
- `/packages/ui` - Shared React components
- `/packages/config` - Shared configuration (ESLint, Prettier, TypeScript)
- `/infra` - Docker, nginx, and deployment configurations
- `/docs` - Public and technical documentation
- `/memory` - Project memory and decision records

## Technology Stack

- **Frontend**: Next.js 14, Tailwind CSS, Radix UI, shadcn/ui
- **Backend**: FastAPI (Python 3.11), PostgreSQL 15+
- **Factur-X**: factur-x library, veraPDF, Mustangproject
- **Infrastructure**: Docker, nginx/Caddy, Oracle VPS Ubuntu 24.04 ARM
- **Package Manager**: uv for Python, pnpm for Node.js

## Development

```bash
make dev      # Start development environment
make test     # Run all tests
make lint     # Run linting
make build    # Build all applications
make clean    # Clean build artifacts
```

## Documentation

See `/docs` directory for comprehensive documentation including:

- Architecture overview
- Factur-X compliance guide
- API documentation
- Deployment guide

## License

MIT License - see LICENSE file for details.
