# Makefile for CBT Assistant POC Monorepo

.PHONY: help
help: ## Show this help message
	@echo "CBT Assistant POC - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development commands
.PHONY: dev
dev: ## Start all services in development mode
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

.PHONY: dev-frontend
dev-frontend: ## Start only frontend in development mode
	cd frontend && pnpm dev

.PHONY: dev-backend
dev-backend: ## Start only backend in development mode
	cd backend && uv run uvicorn main:app --reload

.PHONY: dev-docker-build
dev-docker-build: ## Build all Docker images for development
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

# Testing commands
.PHONY: test
test: test-frontend test-backend ## Run all tests

.PHONY: test-frontend
test-frontend: ## Run frontend tests
	cd frontend && pnpm test

.PHONY: test-backend
test-backend: ## Run backend tests
	cd backend && uv run poe test

.PHONY: test-integration
test-integration: ## Run integration tests
	docker-compose -f docker-compose.yml -f docker-compose.integration.yml up --abort-on-container-exit

# Linting and formatting
.PHONY: lint
lint: lint-frontend lint-backend ## Run all linters

.PHONY: lint-frontend
lint-frontend: ## Run frontend linter
	cd frontend && pnpm lint

.PHONY: lint-backend
lint-backend: ## Run backend linter
	cd backend && uv run poe lint

.PHONY: format
format: format-frontend format-backend ## Format all code

.PHONY: format-frontend
format-frontend: ## Format frontend code
	cd frontend && pnpm lint --fix

.PHONY: format-backend
format-backend: ## Format backend code
	cd backend && uv run poe format

# Type checking
.PHONY: typecheck
typecheck: typecheck-frontend typecheck-backend ## Run type checking

.PHONY: typecheck-frontend
typecheck-frontend: ## Run frontend type checking
	cd frontend && pnpm tsc --noEmit

.PHONY: typecheck-backend
typecheck-backend: ## Run backend type checking
	cd backend && uv run mypy src

# Build commands
.PHONY: build
build: build-frontend build-backend ## Build all components

.PHONY: build-frontend
build-frontend: ## Build frontend
	cd frontend && pnpm build

.PHONY: build-backend
build-backend: ## Build backend Docker image
	docker build -t cbt-backend:latest ./backend

# Docker commands
.PHONY: docker-up
docker-up: ## Start all services with Docker Compose
	docker-compose up -d

.PHONY: docker-down
docker-down: ## Stop all services
	docker-compose down

.PHONY: docker-logs
docker-logs: ## Show logs from all services
	docker-compose logs -f

.PHONY: docker-clean
docker-clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

# Database commands (if needed in future)
.PHONY: db-migrate
db-migrate: ## Run database migrations
	@echo "No database migrations configured yet"

# Documentation management
.PHONY: check-docs
check-docs: ## Check if CLAUDE.md files need updating
	@./scripts/update-claude-docs.sh

.PHONY: update-docs
update-docs: ## Update CLAUDE.md files (interactive)
	@echo "Run: /update-claude-docs"
	@echo "This will analyze recent changes and update CLAUDE.md files"

# Dependency management
.PHONY: install
install: install-frontend install-backend ## Install all dependencies

.PHONY: install-frontend
install-frontend: ## Install frontend dependencies
	cd frontend && pnpm install

.PHONY: install-backend
install-backend: ## Install backend dependencies
	cd backend && uv sync --all-extras

.PHONY: update-deps
update-deps: ## Update all dependencies
	cd frontend && pnpm update
	cd backend && uv sync --upgrade

# CI/CD commands
.PHONY: ci-test
ci-test: ## Run tests as in CI
	@echo "Running frontend tests..."
	cd frontend && pnpm test:ci
	@echo "Running backend tests..."
	cd backend && uv run pytest --cov=src --cov-report=xml

# Deployment commands
.PHONY: deploy-frontend
deploy-frontend: ## Deploy frontend to Cloud Run
	@echo "Triggering frontend deployment workflow..."
	gh workflow run deploy-frontend.yml

.PHONY: deploy-backend
deploy-backend: ## Deploy backend to Cloud Run
	@echo "Triggering backend deployment workflow..."
	gh workflow run deploy-backend.yml

# Utility commands
.PHONY: clean
clean: ## Clean generated files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".next" -exec rm -rf {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

.PHONY: pre-commit
pre-commit: lint typecheck test ## Run all pre-commit checks

.PHONY: setup
setup: ## Initial project setup
	@echo "Setting up CBT Assistant POC development environment..."
	@command -v pnpm >/dev/null 2>&1 || { echo "Installing pnpm..."; npm install -g pnpm; }
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	@echo "Installing dependencies..."
	@$(MAKE) install
	@echo "Setup complete! Run 'make dev' to start development."

# Documentation
.PHONY: docs
docs: ## Serve documentation locally
	docker run --rm -it -p 8001:8000 -v ${PWD}/docs:/docs squidfunk/mkdocs-material