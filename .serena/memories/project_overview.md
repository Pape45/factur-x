# Factur-X Express - Project Overview

## Purpose
Factur-X Express is a micro-SaaS application for generating, validating, and exporting Factur-X invoices. It aims to provide a comprehensive solution for businesses to create compliant electronic invoices according to the Factur-X standard.

## Key Objectives
- **Invoice Creation**: Generate Factur-X compliant invoices
- **Validation**: Validate invoices against Factur-X standards
- **Export**: Export invoices in various formats
- **Compliance**: Ensure full compliance with Factur-X regulations
- **User Experience**: Provide intuitive UX/UI for invoice management

## Target Architecture
- **Monorepo Structure**: Single repository containing all components
- **Frontend**: Next.js application for user interface
- **Backend**: FastAPI for API services
- **Optional Worker**: Background processing capabilities
- **Shared Packages**: UI components and configuration packages
- **Infrastructure**: Docker/Nginx for deployment

## Hardware Constraints
- **Development**: macOS Apple Silicon
- **Production**: Oracle VPS Ubuntu 24.04 ARM

## Target Runtimes
- Node.js 20 LTS
- Python 3.11
- Java 21
- PostgreSQL 15+
- Docker/Compose

## Key Technologies for Factur-X
- **Python**: `factur-x` library for invoice generation
- **Java**: Mustangproject tool for Factur-X processing
- **Validation**: veraPDF for PDF/A compliance

## Development Approach
- **Ask-First Mode**: Request clarification for missing information
- **Detailed Roadmap**: Comprehensive planning and documentation
- **Memory and Traceability**: Maintain artifacts for project history
- **Git/CI/CD**: Modern development practices
- **Design Guidelines**: Consistent UI/UX patterns