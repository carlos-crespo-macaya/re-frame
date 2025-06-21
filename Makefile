# Makefile
.PHONY: help install test lint format type-check

help:
	@echo "Available commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linters"
	@echo "  make format     - Format code"
	@echo "  make type-check - Run type checkers"
	@echo "  make dev        - Start development servers"

install:
	cd backend && uv venv && . .venv/bin/activate && uv pip install -e ".[dev]"
	cd frontend && pnpm install
	pre-commit install

test:
	cd backend && . .venv/bin/activate && poe test
	cd frontend && pnpm test

lint:
	cd backend && . .venv/bin/activate && poe lint
	cd frontend && pnpm lint
	cd infrastructure && tflint

format:
	cd backend && . .venv/bin/activate && poe format
	cd frontend && pnpm format
	cd infrastructure && terraform fmt -recursive

type-check:
	cd backend && . .venv/bin/activate && poe type-check
	cd frontend && pnpm type-check

dev:
	docker-compose up

# Individual services
dev-backend:
	cd backend && poetry run uvicorn main:app --reload

dev-frontend:
	cd frontend && pnpm dev

# CI/CD simulation
ci:
	make lint
	make type-check
	make test