# Sources & References

**Document Version:** 1.0  
**Last Updated:** $(date)  
**Owner:** Technical Team  
**Status:** Active

---

## Overview

This document contains all external references, libraries, standards, and resources used in the Factur-X Express project. It serves as a comprehensive bibliography and resource guide for developers, auditors, and stakeholders.

---

## Standards & Specifications

### 1. Factur-X / ZUGFeRD Standards

| Standard | Version | Description | URL |
|----------|---------|-------------|-----|
| EN 16931 | 1.3.11 | European standard for electronic invoicing | [CEN Workshop](https://standards.cen.eu/dyn/www/f?p=204:110:0::::FSP_PROJECT:60602&cs=1B61B766636F9FB34B7DBD72CE9026C72) |
| Factur-X | 1.0.7 | Franco-German e-invoicing standard | [FNFE-MPE](https://fnfe-mpe.org/factur-x/) |
| ZUGFeRD | 2.3 | German e-invoicing standard | [FeRD](https://www.ferd-net.de/) |
| PDF/A-3 | ISO 19005-3 | PDF archival format with embedded files | [ISO](https://www.iso.org/standard/57229.html) |
| UN/CEFACT CII | D16B | Cross Industry Invoice XML schema | [UN/CEFACT](https://unece.org/trade/uncefact/xml-schemas) |

### 2. Security & Compliance Standards

| Standard | Version | Description | URL |
|----------|---------|-------------|-----|
| GDPR | 2018/679 | General Data Protection Regulation | [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2016/679/oj) |
| ISO 27001 | 2022 | Information Security Management | [ISO](https://www.iso.org/standard/27001) |
| SOC 2 | Type II | Service Organization Control 2 | [AICPA](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/sorhome.html) |
| OWASP Top 10 | 2021 | Web Application Security Risks | [OWASP](https://owasp.org/www-project-top-ten/) |

### 3. French Regulatory Framework

| Regulation | Description | URL |
|------------|-------------|-----|
| Ordonnance 2021-1190 | French e-invoicing mandate | [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000044143887) |
| Décret 2022-1299 | Implementation decree | [Légifrance](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000046344083) |
| Chorus Pro | French public e-invoicing platform | [Chorus Pro](https://chorus-pro.gouv.fr/) |

---

## Core Libraries & Dependencies

### 1. Backend Dependencies (Python)

#### Core Framework
```toml
[project.dependencies]
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
```

#### Factur-X Specific
```toml
factur-x = "^2.6"
WeasyPrint = "^60.2"
lxml = "^4.9.3"
xmlschema = "^2.5.1"
```

#### Database & Storage
```toml
psycopg2-binary = "^2.9.9"
sqlalchemy = "^2.0.23"
alembic = "^1.13.1"
redis = "^5.0.1"
```

#### Authentication & Security
```toml
pyjwt = {extras = ["crypto"], version = "^2.8.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
cryptography = "^41.0.7"
```

#### File Processing
```toml
boto3 = "^1.34.0"
pillow = "^10.1.0"
python-multipart = "^0.0.6"
```

#### Monitoring & Logging
```toml
sentry-sdk = {extras = ["fastapi"], version = "^1.38.0"}
prometheus-client = "^0.19.0"
structlog = "^23.2.0"
```

#### Testing
```toml
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
httpx = "^0.25.2"
factory-boy = "^3.3.0"
```

### 2. Frontend Dependencies (Node.js)

#### Core Framework
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.0"
  }
}
```

#### UI & Styling
```json
{
  "dependencies": {
    "tailwindcss": "^3.3.6",
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.0.18",
    "framer-motion": "^10.16.16"
  }
}
```

#### State Management & API
```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.8.4",
    "axios": "^1.6.2",
    "zustand": "^4.4.7"
  }
}
```

#### Forms & Validation
```json
{
  "dependencies": {
    "react-hook-form": "^7.48.2",
    "@hookform/resolvers": "^3.3.2",
    "zod": "^3.22.4"
  }
}
```

### 3. Infrastructure Dependencies

#### Container & Orchestration
- **Docker:** ^24.0.0
- **Docker Compose:** ^2.21.0
- **AWS ECS:** Latest
- **AWS Fargate:** Latest

#### Database & Cache
- **PostgreSQL:** ^15.0
- **Redis:** ^7.0
- **AWS RDS:** PostgreSQL 15.x
- **AWS ElastiCache:** Redis 7.x

#### Monitoring & Observability
- **Prometheus:** ^2.47.0
- **Grafana:** ^10.2.0
- **AWS CloudWatch:** Latest
- **Sentry:** SaaS

---

## External Services & APIs

### 1. Cloud Services (AWS)

| Service | Purpose | Documentation |
|---------|---------|---------------|
| ECS Fargate | Container orchestration | [AWS ECS](https://docs.aws.amazon.com/ecs/) |
| RDS PostgreSQL | Primary database | [AWS RDS](https://docs.aws.amazon.com/rds/) |
| ElastiCache Redis | Caching & sessions | [AWS ElastiCache](https://docs.aws.amazon.com/elasticache/) |
| S3 | File storage | [AWS S3](https://docs.aws.amazon.com/s3/) |
| CloudFront | CDN | [AWS CloudFront](https://docs.aws.amazon.com/cloudfront/) |
| Secrets Manager | Secret management | [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/) |
| CloudWatch | Monitoring & logging | [AWS CloudWatch](https://docs.aws.amazon.com/cloudwatch/) |
| Route 53 | DNS management | [AWS Route 53](https://docs.aws.amazon.com/route53/) |
| Certificate Manager | SSL/TLS certificates | [AWS ACM](https://docs.aws.amazon.com/acm/) |

### 2. Third-Party Services

| Service | Purpose | Documentation |
|---------|---------|---------------|
| Sentry | Error tracking & performance | [Sentry Docs](https://docs.sentry.io/) |
| GitHub Actions | CI/CD pipeline | [GitHub Actions](https://docs.github.com/en/actions) |
| Stripe | Payment processing | [Stripe API](https://stripe.com/docs/api) |
| SendGrid | Email delivery | [SendGrid API](https://docs.sendgrid.com/) |

### 3. Validation Services

| Service | Purpose | Documentation |
|---------|---------|---------------|
| veraPDF | PDF/A validation | [veraPDF](https://verapdf.org/) |
| Mustangproject | ZUGFeRD validation | [Mustangproject](https://www.mustangproject.org/) |
| XML Schema Validator | EN 16931 validation | [xmlschema](https://xmlschema.readthedocs.io/) |

---

## Development Tools & Resources

### 1. Development Environment

| Tool | Version | Purpose | Documentation |
|------|---------|---------|---------------|
| Python | ^3.11 | Backend runtime | [Python.org](https://docs.python.org/3.11/) |
| uv | ^0.1.0 | Python package manager | [uv docs](https://github.com/astral-sh/uv) |
| Node.js | ^20.0 | Frontend runtime | [Node.js](https://nodejs.org/docs/) |
| Docker | ^24.0 | Containerization | [Docker Docs](https://docs.docker.com/) |
| Git | ^2.40 | Version control | [Git SCM](https://git-scm.com/doc) |

### 2. Code Quality & Testing

| Tool | Purpose | Documentation |
|------|---------|---------------|
| Black | Python code formatting | [Black](https://black.readthedocs.io/) |
| isort | Python import sorting | [isort](https://pycqa.github.io/isort/) |
| flake8 | Python linting | [flake8](https://flake8.pycqa.org/) |
| mypy | Python type checking | [mypy](https://mypy.readthedocs.io/) |
| pytest | Python testing | [pytest](https://docs.pytest.org/) |
| ESLint | JavaScript/TypeScript linting | [ESLint](https://eslint.org/docs/) |
| Prettier | Code formatting | [Prettier](https://prettier.io/docs/) |
| Vitest | Frontend testing | [Vitest](https://vitest.dev/) |

### 3. Security Tools

| Tool | Purpose | Documentation |
|------|---------|---------------|
| Bandit | Python security linting | [Bandit](https://bandit.readthedocs.io/) |
| Safety | Python dependency scanning | [Safety](https://pyup.io/safety/) |
| Trivy | Container vulnerability scanning | [Trivy](https://trivy.dev/) |
| OWASP ZAP | Web application security testing | [OWASP ZAP](https://www.zaproxy.org/docs/) |

---

## Documentation & Learning Resources

### 1. Technical Documentation

| Resource | Description | URL |
|----------|-------------|-----|
| FastAPI Documentation | Comprehensive API framework guide | [FastAPI](https://fastapi.tiangolo.com/) |
| React Documentation | Frontend framework guide | [React](https://react.dev/) |
| PostgreSQL Documentation | Database documentation | [PostgreSQL](https://www.postgresql.org/docs/) |
| Docker Best Practices | Container optimization guide | [Docker](https://docs.docker.com/develop/dev-best-practices/) |
| AWS Well-Architected | Cloud architecture framework | [AWS](https://aws.amazon.com/architecture/well-architected/) |

### 2. Factur-X Resources

| Resource | Description | URL |
|----------|-------------|-----|
| Factur-X Specification | Official technical specification | [FNFE-MPE](https://fnfe-mpe.org/factur-x/factur-x_en/) |
| EN 16931 Implementation Guide | European standard implementation | [CEN](https://standards.cen.eu/) |
| ZUGFeRD Developer Guide | German standard implementation | [FeRD](https://www.ferd-net.de/zugferd/index.html) |
| PDF/A Technical Guide | PDF archival format guide | [PDF Association](https://www.pdfa.org/) |

### 3. Compliance & Legal Resources

| Resource | Description | URL |
|----------|-------------|-----|
| GDPR Implementation Guide | Data protection compliance | [ICO](https://ico.org.uk/for-organisations/guide-to-data-protection/) |
| French E-invoicing Guide | National implementation guide | [DGFiP](https://www.economie.gouv.fr/entreprises/facture-electronique) |
| OWASP Security Guide | Web application security | [OWASP](https://owasp.org/www-project-web-security-testing-guide/) |
| ISO 27001 Implementation | Information security management | [ISO](https://www.iso.org/isoiec-27001-information-security.html) |

---

## Sample Data & Test Resources

### 1. Test Invoice Data

| Resource | Description | Format |
|----------|-------------|--------|
| EN 16931 Test Invoices | Official test cases | XML, PDF |
| Factur-X Samples | Reference implementations | PDF/A-3 |
| ZUGFeRD Examples | German standard samples | PDF |
| Validation Test Suite | Compliance test cases | XML, JSON |

### 2. Schema Files

| Schema | Version | Purpose | Location |
|--------|---------|---------|----------|
| EN16931-CII.xsd | 1.3.11 | Invoice validation | `/schemas/en16931/` |
| Factur-X.xsd | 1.0.7 | Factur-X validation | `/schemas/facturx/` |
| ZUGFeRD.xsd | 2.3 | ZUGFeRD validation | `/schemas/zugferd/` |
| PDF/A-3.xsd | ISO 19005-3 | PDF validation | `/schemas/pdfa/` |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | $(date) | Initial documentation | Technical Team |

---

## Maintenance

- **Review Frequency:** Monthly
- **Update Trigger:** New dependency versions, standard updates
- **Owner:** Technical Lead
- **Stakeholders:** Development Team, Security Team, Compliance Team

---

**Document Status:** Active  
**Classification:** Internal  
**Distribution:** Development Team, Stakeholders