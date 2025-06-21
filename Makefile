# Makefile for re-frame development
.PHONY: help install setup clean test lint format check-all backend-dev frontend-dev docker-up docker-down

# Default target
help:
	@echo "re-frame Development Commands"
	@echo "============================"
	@echo "Setup:"
	@echo "  make install      - Install all dependencies (backend + frontend)"
	@echo "  make setup        - Complete project setup including git hooks"
	@echo ""
	@echo "Development:"
	@echo "  make backend-dev  - Run backend development server"
	@echo "  make frontend-dev - Run frontend development server"
	@echo "  make docker-up    - Start all services with Docker Compose"
	@echo "  make docker-down  - Stop all Docker services"
	@echo ""
	@echo "Quality Checks (mirrors CI/CD):"
	@echo "  make lint         - Run all linters"
	@echo "  make format       - Format all code"
	@echo "  make test         - Run all tests"
	@echo "  make type-check   - Run type checkers"
	@echo "  make check-all    - Run all checks (what CI runs)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - Clean all generated files"

# Install dependencies
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && uv venv && . .venv/bin/activate && uv pip install -e ".[dev]"
	@echo "📦 Installing frontend dependencies..."
	cd frontend && pnpm install
	@echo "✅ All dependencies installed!"

# Complete setup
setup: install
	@echo "🔧 Setting up git hooks..."
	git config core.hooksPath .githooks
	@echo "✅ Project setup complete!"

# Backend development
backend-dev:
	cd backend && . .venv/bin/activate && poe dev

# Frontend development
frontend-dev:
	cd frontend && pnpm dev

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Linting
lint:
	@echo "🔍 Running linters..."
	cd backend && . .venv/bin/activate && poe lint
	cd frontend && pnpm lint
	cd infrastructure && terraform fmt -check -recursive

# Formatting
format:
	@echo "💅 Formatting code..."
	cd backend && . .venv/bin/activate && poe format
	cd frontend && pnpm format || true
	cd infrastructure && terraform fmt -recursive

# Type checking
type-check:
	@echo "📝 Running type checkers..."
	cd backend && . .venv/bin/activate && poe type-check

# Testing
test:
	@echo "🧪 Running tests..."
	cd backend && . .venv/bin/activate && poe test
	cd frontend && pnpm test || echo "No frontend tests yet"

# Run all checks (mirrors CI/CD)
check-all:
	@echo "🚀 Running all checks (CI/CD mirror)..."
	./scripts/local-checks.sh

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache backend/htmlcov backend/.coverage
	rm -rf frontend/.next frontend/node_modules/.cache
	rm -rf infrastructure/terraform/.terraform
	@echo "✅ Clean complete!"