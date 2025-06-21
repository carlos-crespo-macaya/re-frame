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
	cd backend && poetry install
	cd frontend && pnpm install
	pre-commit install

test:
	cd backend && poetry run pytest
	cd frontend && pnpm test

lint:
	cd backend && poetry run ruff check .
	cd frontend && pnpm lint
	cd infrastructure && tflint

format:
	cd backend && poetry run black . && poetry run ruff check --fix .
	cd frontend && pnpm format
	cd infrastructure && terraform fmt -recursive

type-check:
	cd backend && poetry run mypy .
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