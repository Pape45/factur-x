# Factur-X Express - Project Status & Roadmap

## 🎯 Project Overview
**Factur-X Express** is a micro-SaaS for generating, validating, and exporting Factur-X compliant invoices (PDF/A-3 + XML CII) conforming to EN 16931 standard.

## 📋 Current Status: **PHASE 2 - Factur-X Core** 🔄 **IN PROGRESS**

### ✅ Phase 0 - Documentation & Planning (COMPLETE)
- [x] Initial project analysis and requirements review
- [x] Created PROJECT_STATUS.md tracking file
- [x] Complete documentation structure creation:
  - [x] `/memory/` folder with 6 core documents
  - [x] `/docs/` folder with comprehensive technical documentation
  - [x] All compliance, security, and architecture documents
- [x] Memory and traceability systems established
- [x] Project roadmap and checkpoints defined

### ✅ Phase 1 - Bootstrap & Foundation (COMPLETE - December 2024)
- [x] Development environment verification (uv, Java 21, Node.js 22, pnpm)
- [x] Monorepo structure creation (/apps, /packages, /infra)
- [x] FastAPI project initialization with uv package management
- [x] pnpm workspaces configuration
- [x] ARM64-optimized Docker configuration (multi-stage builds)
- [x] docker-compose.yml with full stack (PostgreSQL 16, Redis 7, Nginx)
- [x] Nginx reverse proxy configuration
- [x] Security best practices implementation (non-root users, health checks)
- [x] Development environment ready for Factur-X implementation

### 🎯 Phase 2 - Current Focus
**Factur-X Core Implementation** - Building the core invoice generation and validation system:
1. FastAPI service implementation with invoice endpoints
2. XML CII generation (EN 16931 compliance)
3. PDF/A-3 embedding with factur-x library
4. Validation system (veraPDF + Mustangproject)
5. Frontend invoice form and PDF viewer

---

**Last Updated:** December 2024  
**Phase 1 Completion:** ✅ December 2024  
**Current Phase:** Phase 2 - Factur-X Core Implementation

---

## 🗺️ Complete Project Roadmap

### **Phase 0 - Documentation & Planning** ✅ **COMPLETE**
**Duration:** 1 day  
**Status:** ✅ Complete
**Completed:** December 2024

#### Tasks Completed:
- [x] Create PROJECT_STATUS.md
- [x] Create /memory/ folder structure
  - [x] /context/ONE_PAGER.md
  - [x] /decisions/TECHNICAL_DECISIONS.md
  - [x] /requirements/REQUIREMENTS_TRACEABILITY.md
  - [x] /checkpoints/PROJECT_CHECKPOINTS.md
  - [x] /prompts/AI_PROMPTS_TEMPLATES.md
  - [x] /runbooks/OPERATIONAL_RUNBOOKS.md
- [x] Create /docs/ folder structure
  - [x] TECHNICAL_ARCHITECTURE.md
  - [x] COMPLIANCE_FRAMEWORK.md
  - [x] SECURITY_ARCHITECTURE.md
  - [x] SOURCES.md
- [x] Complete documentation framework established

### **Phase 1 - Bootstrap & Foundation** ✅ **COMPLETE**
**Duration:** 2 days  
**Status:** ✅ Complete
**Completed:** December 2024

#### Key Deliverables Completed:
- [x] Development environment setup with `uv`
- [x] Project structure initialization (monorepo)
- [x] Core infrastructure setup (Docker, PostgreSQL, Redis)
- [x] Basic FastAPI application scaffold
- [x] CI/CD pipeline foundation

#### Tasks Completed:
- [x] Install and configure `uv` for Python package management
- [x] Create monorepo structure (/apps, /packages, /infra)
- [x] Initialize FastAPI project with dependencies
- [x] Setup Docker configuration for ARM64 deployment
- [x] Configure PostgreSQL and Redis services
- [x] Create basic API endpoints structure
- [x] Setup development scripts and tooling
- [x] Initialize Git repository with proper .gitignore
- [x] Create basic CI/CD workflow templates

#### Technical Stack Established:
- **Frontend:** Next.js 14 (App Router) - Ready for Phase 2
- **Backend:** FastAPI (Python 3.12) with uv package management ✅
- **Database:** PostgreSQL 16 (ARM64) ✅
- **Cache:** Redis 7 (ARM64) ✅
- **Container:** Docker/Compose (linux/arm64) ✅
- **Package Manager:** pnpm (Node.js), uv (Python) ✅
- **Development Environment:** Ready for Factur-X implementation ✅

### **Phase 2 - Factur-X Core** 🔄 **IN PROGRESS**
**Duration:** 3-4 days  
**Status:** 🔄 In Progress
**Started:** December 2024

#### Key Deliverables:
- [ ] FastAPI service implementation
- [ ] Invoice data models and validation
- [ ] XML CII generation (EN 16931)
- [ ] PDF/A-3 embedding with factur-x library
- [ ] Validation system (veraPDF + Mustangproject)

#### Tasks:
- [ ] Install factur-x Python library
- [ ] Create invoice data models (Pydantic)
- [ ] Implement XML CII generation endpoints
- [ ] Setup PDF/A-3 creation and embedding
- [ ] Integrate veraPDF for validation
- [ ] Create validation endpoints
- [ ] Add error handling and logging
- [ ] Write unit tests for core functionality
- [ ] Document API endpoints

#### Libraries & Tools:
- **Python:** factur-x, fastapi, pydantic, lxml, pikepdf
- **Validation:** veraPDF, Mustangproject
- **Frontend:** React Hook Form, Zod validation

### **Phase 3 - Compliance & UX (J8-J12)**
**Duration:** 5 days  
**Status:** ⏳ Pending

#### Key Deliverables:
- [ ] EN16931 mandatory fields implementation
- [ ] Frontend validation controls
- [ ] VAT code validation
- [ ] Units and totals validation
- [ ] Accessibility (WCAG AA)
- [ ] Internationalization (FR/EN)
- [ ] Transactional emails
- [ ] Compliance documentation
- [ ] Architecture Decision Records (ADRs)

#### Compliance Focus:
- **Standards:** EN 16931, UN/CEFACT CII, PDF/A-3
- **Validation:** Double validation (veraPDF + Mustangproject)
- **Documentation:** Complete compliance mapping

### **Phase 4 - Production & Security (J13-J15)**
**Duration:** 3 days  
**Status:** ⏳ Pending

#### Key Deliverables:
- [ ] GitHub Actions CI/CD pipeline
- [ ] ARM-compatible Docker builds
- [ ] Security scanning (Trivy)
- [ ] Staging environment deployment
- [ ] Production environment deployment (Ubuntu 24.04 ARM)
- [ ] TLS setup (Caddy/Nginx)
- [ ] Monitoring and logging
- [ ] Backup strategy

#### Infrastructure:
- **Target:** Oracle VPS Ubuntu 24.04 ARM (24GB RAM, 200GB SSD)
- **Runtime:** Node.js 20 LTS, Python 3.11, Java 21, PostgreSQL 15+
- **Deployment:** Docker Compose + Caddy/Nginx

### **Phase 5 - v1 Features (J16-J21)**
**Duration:** 6 days  
**Status:** ⏳ Pending

#### Key Deliverables:
- [ ] CSV import functionality
- [ ] Accounting export
- [ ] Webhook system
- [ ] Dashboard analytics
- [ ] Performance monitoring
- [ ] Optional: Stripe/Shopify connectors

### **Phase 6 - Beta Launch (J22+)**
**Duration:** Ongoing  
**Status:** ⏳ Pending

#### Key Deliverables:
- [ ] Pricing implementation (39€/month + 0.05€/invoice)
- [ ] Founder coupons
- [ ] GDPR compliance
- [ ] 6-year retention policy
- [ ] Log management policy

---

## 🔧 Technical Architecture Overview

### Monorepo Structure
```
/apps
  /web            → Next.js 14 (App Router, Server Actions), Tailwind, Radix UI, shadcn/ui
  /facturx-api    → FastAPI (Python 3.11): XML CII generation + PDF/A-3 packaging
  /worker         → (optional) Heavy tasks/queue (RQ/Celery)
/packages
  /ui             → Shared React components
  /config         → Shared ESLint/Prettier/TS config
/infra
  /docker         → Dockerfiles (linux/arm64), docker-compose.{dev,prod}.yml
  /nginx          → Reverse proxy + TLS (Caddy or Nginx + certbot)
  /github         → GitHub Actions (CI/CD)
/docs             → Public & technical documentation
/memory           → Project "long memory"
```

### Key Libraries & Standards
- **Factur-X Generation:** factur-x (Akretion) - [PyPI](https://pypi.org/project/factur-x/)
- **Validation:** Mustangproject - [GitHub](https://github.com/ZUGFeRD/mustangproject)
- **PDF/A-3 Validation:** veraPDF - [Website](https://verapdf.org/home/)
- **Standards:** EN 16931, UN/CEFACT CII, PDF/A-3 (ISO 19005-3)

---

## 🚨 Ask-First Requirements

Before implementation, the following information must be collected:

### Business & Legal
- [ ] Legal company name
- [ ] Logo
- [ ] Business address
- [ ] SIREN/SIRET number
- [ ] VAT number
- [ ] IBAN/BIC
- [ ] VAT regime
- [ ] Legal mentions

### Product Configuration
- [ ] Default currencies
- [ ] Default tax rates
- [ ] Invoice numbering format (e.g., FX-{{YYYY}}-{{seq}})
- [ ] Terms of Service
- [ ] Privacy Policy

### Branding
- [ ] Color palette
- [ ] Brand tone
- [ ] Baseline/tagline

### Infrastructure
- [ ] Domain name
- [ ] DNS configuration
- [ ] Email setup (SPF/DKIM)
- [ ] Storage preferences (S3/MinIO)
- [ ] SMTP configuration

### Deployment
- [ ] Deployment preferences (Docker vs bare-metal)
- [ ] TLS certificates
- [ ] Port mapping

---

## 📊 Success Metrics (DORA)

### Target Metrics
- **Deployment Frequency:** Multiple times per day
- **Lead Time for Changes:** < 1 hour
- **Change Failure Rate:** 0-15%
- **Mean Time to Recovery:** < 1 hour

### Quality Gates
- All tests passing
- Security scans clean
- Documentation updated
- Staging deployment successful

---

## 🔗 Key Resources

### Standards & Compliance
- [Factur-X 1.07.3 (FNFE-MPE)](https://fnfe-mpe.org/factur-x/factur-x_en/)
- [EN 16931 (European Commission)](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Obtaining%2Ba%2Bcopy%2Bof%2Bthe%2BEuropean%2Bstandard%2Bon%2BeInvoicing)
- [UN/CEFACT CII (UNECE)](https://unece.org/trade/uncefact/e-invoice)
- [PDF/A-3 (PDF Association)](https://pdfa.org/resource/iso-19005-3-pdf-a-3/)

### Tools & Libraries
- [factur-x Python Library](https://pypi.org/project/factur-x/)
- [Mustangproject](https://github.com/ZUGFeRD/mustangproject)
- [veraPDF](https://verapdf.org/home/)

### French Regulation
- [PPF/PDP Reform](https://entreprendre.service-public.fr/actualites/A15683?lang=en)
- [DGFiP Specifications](https://www.impots.gouv.fr/specifications-externes-b2b)

---

## 📝 Notes

- **Package Manager:** Use `uv` for Python (uv init, uv add, uv run, uv pip install)
- **Development Environment:** macOS Apple Silicon (M1 2020)
- **Production Environment:** Oracle VPS Ubuntu 24.04 ARM (Ampere)
- **Container Architecture:** linux/arm64

---

**Last Updated:** $(date)  
**Next Review:** After Phase 0 completion