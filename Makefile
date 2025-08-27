# Factur-X Express Makefile
# Provides convenient commands for development and deployment

.PHONY: help install dev test lint build clean docker-build docker-up docker-down

# Default target
help:
	@echo "Factur-X Express - Available commands:"
	@echo ""
	@echo "  install      Install all dependencies"
	@echo "  dev          Start development environment"
	@echo "  test         Run all tests"
	@echo "  lint         Run linting and formatting"
	@echo "  build        Build all applications"
	@echo "  clean        Clean build artifacts"
	@echo "  docker-build Build Docker images"
	@echo "  docker-up    Start Docker Compose environment"
	@echo "  docker-down  Stop Docker Compose environment"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✓ uv found"; \
	else \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@if command -v pnpm >/dev/null 2>&1; then \
		echo "✓ pnpm found"; \
	else \
		echo "Installing pnpm..."; \
		npm install -g pnpm; \
	fi
	@echo "Installing Python dependencies..."
	@cd apps/facturx-api && uv sync
	@echo "Installing Node.js dependencies..."
	@pnpm install

# Start development environment
dev:
	@echo "Starting development environment..."
	@docker-compose -f infra/compose/docker-compose.dev.yml up -d postgres
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	@echo "Starting FastAPI backend..."
	@cd apps/facturx-api && uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting Next.js frontend..."
	@cd apps/web && pnpm dev

# Run tests
test:
	@echo "Running tests..."
	@cd apps/facturx-api && uv run pytest
	@cd apps/web && pnpm test

# Run linting
lint:
	@echo "Running linting and formatting..."
	@cd apps/facturx-api && uv run ruff check . && uv run ruff format .
	@cd apps/web && pnpm lint
	@pnpm prettier --write .

# Build applications
build:
	@echo "Building applications..."
	@cd apps/web && pnpm build
	@cd apps/facturx-api && uv build

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf apps/web/.next
	@rm -rf apps/web/dist
	@rm -rf apps/facturx-api/dist
	@rm -rf apps/facturx-api/.pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "node_modules" -exec rm -rf {} +

# Docker commands
docker-build:
	@echo "Building Docker images..."
	@docker-compose -f infra/compose/docker-compose.prod.yml build

docker-up:
	@echo "Starting Docker Compose environment..."
	@docker-compose -f infra/compose/docker-compose.dev.yml up -d

docker-down:
	@echo "Stopping Docker Compose environment..."
	@docker-compose -f infra/compose/docker-compose.dev.yml down
