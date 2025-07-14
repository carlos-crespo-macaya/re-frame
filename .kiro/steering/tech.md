# Technology Stack & Build System

## Architecture
**Monorepo** with separate frontend and backend services that communicate via REST API and Server-Sent Events (SSE).

## Frontend Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Package Manager**: pnpm 10.11.0+
- **Testing**: Jest + Testing Library + Playwright (E2E)
- **Build**: Static export for Cloud Run deployment

## Backend Stack
- **Framework**: FastAPI (Python web API)
- **AI Framework**: Google Agent Development Kit (ADK)
- **Language**: Python 3.12+
- **Package Manager**: uv (modern Python package manager)
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black, isort, ruff, mypy

## Key Libraries & Dependencies

### Frontend
- `clsx` + `tailwind-merge` for conditional styling
- `uuid` for session management
- Audio processing via Web APIs

### Backend
- `google-adk` for conversational AI agents
- `fastapi` for web API
- `langdetect` for language detection
- `reportlab` for PDF generation
- `crawl4ai` for knowledge gathering
- `pydotenv` for environment management

## Development Commands

### Root Level (uses npm/pnpm workspaces)
```bash
# Development
npm run dev              # Start frontend only
npm run dev:all          # Start both frontend and backend
make dev                 # Docker Compose development

# Testing
npm run test:all         # Run all tests
make test               # Run all tests via Makefile

# Building
npm run build           # Build frontend
make build              # Build all components

# Docker
make docker-up          # Start with Docker Compose
make docker-down        # Stop services
```

### Frontend Commands
```bash
cd frontend
pnpm dev                # Development server
pnpm build              # Production build
pnpm test               # Run Jest tests
pnpm lint               # ESLint
pnpm typecheck          # TypeScript checking
```

### Backend Commands
```bash
cd backend
uv run uvicorn main:app --reload    # Development server
uv run poe test                     # Run tests
uv run poe check                    # All quality checks
uv run poe format                   # Auto-format code
uv run poe lint                     # Linting
uv run mypy src                     # Type checking
```

## Environment Setup
- **Node.js**: 18+ required
- **Python**: 3.12+ required
- **Package Managers**: pnpm for frontend, uv for backend
- **Docker**: Required for full-stack development
- **API Keys**: Google Gemini API key required for backend

## Code Quality Standards
- **Frontend**: ESLint + Prettier, TypeScript strict mode
- **Backend**: 80% test coverage, black formatting, ruff linting, mypy type checking
- **Pre-commit hooks**: Automated formatting and linting
- **CI/CD**: GitHub Actions for automated testing and deployment

## Deployment
- **Platform**: Google Cloud Run
- **Frontend**: Static export deployed as container
- **Backend**: FastAPI container with health checks
- **Environment**: Separate dev/prod configurations