# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is the **re-frame** monorepo - A transparent, AI-assisted cognitive behavioral therapy (CBT) tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety. It combines a Next.js 14 frontend with a FastAPI backend powered by Google's Agent Development Kit (ADK).

### Key Features
- **Multi-modal support**: Text-based interaction and optional voice conversations
- **Real-time streaming**: Server-Sent Events (SSE) for responsive interactions
- **Internationalization**: Support for multiple languages (currently English and Spanish)
- **Feature flags**: Dynamic feature toggling with ConfigCat integration
- **Safety-first**: Crisis detection at every user input
- **Privacy-focused**: No audio storage, only transcriptions are kept

## Core Programming Principles

### The Essence of Code Quality
- **Clean code is professional responsibility** - It reflects commitment to craftsmanship
- **Boy Scout Rule**: Always leave code cleaner than you found it
- **Simplicity over ease**: Simple (one role, one purpose) is better than easy (familiar, convenient)
- **Design lives in code**: Code should be a beautiful articulation of design efforts

### Naming Excellence
- **Intention-revealing**: Names should explain why, what, and how
- **Avoid disinformation**: Don't use `List` suffix unless it's actually a List
- **Pronounceable & searchable**: If you can't pronounce it, you can't discuss it
- **One word per concept**: Be consistent - use `fetch`, `retrieve`, or `get`, but pick one
- **No encodings**: Modern IDEs make Hungarian notation unnecessary

### Function Principles
- **Small is beautiful**: Functions should do one thing well
- **Descriptive names**: Spend time finding the perfect name
- **Few arguments**: Zero is ideal, one is good, two is okay, three needs justification
- **No side effects**: Functions should be predictable
- **Command Query Separation**: Either do something or answer something, not both

### Comments Philosophy
- **Code > Comments**: Don't comment bad code—rewrite it
- **Good comments are rare**: Legal notices, TODOs, intent clarification
- **Never comment out code**: Use version control instead
- **Keep comments local**: Don't describe distant code

### Managing Complexity
- **Complexity kills**: It makes products hard to plan, build, and test
- **State is complexity**: Prefer immutable values where possible
- **Declarative > Imperative**: Use SQL, LINQ, rules engines when appropriate
- **Postpone decisions**: Wait until the last responsible moment

### Testing & Design
- **TDD Second Law**: Write only enough production code to pass the failing test
- **Clean tests are first-class**: Maintain tests as diligently as production code
- **F.I.R.S.T**: Fast, Independent, Repeatable, Self-Validating, Timely
- **Emergent design**: Good design emerges from: tests passing, no duplication, clear expression, minimal entities

## Project Overview

This is the CBT Assistant POC monorepo, combining:
- **Frontend**: re-frame.social - Next.js 14 application for cognitive reframing support
- **Backend**: FastAPI with Google's Agent Development Kit (ADK) for CBT conversations

A transparent, AI-assisted tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety.

## Monorepo Structure

```
re-frame/
├── frontend/          # Next.js 14 frontend application
│   └── CLAUDE.md     # Frontend-specific instructions
├── backend/           # FastAPI backend with ADK agents
│   └── CLAUDE.md     # Backend-specific instructions
├── playwright-js/     # JavaScript E2E tests (primary testing infrastructure)
├── tests/             # Python tests and load testing
│   ├── e2e/          # Python E2E tests (legacy)
│   └── load/         # Load testing for voice functionality
├── infra/            # Infrastructure automation
│   ├── gcp/          # GCP-specific setup scripts
│   ├── github/       # GitHub-specific scripts
│   └── local/        # Local development docs
├── docs/             # Shared documentation
├── scripts/          # Utility scripts
├── .claude/          # Claude agent configurations
│   └── agents/       # Agent-specific instructions
└── docker-compose.yml # Local development setup
```

## Directory-Specific Instructions

Claude will automatically use the most specific CLAUDE.md based on your working directory:

| Directory | CLAUDE.md File | Purpose |
|-----------|---------------|---------|
| `/backend` | [backend/CLAUDE.md](backend/CLAUDE.md) | Backend development with FastAPI, ADK agents, and Python tooling |
| `/frontend` | [frontend/CLAUDE.md](frontend/CLAUDE.md) | Frontend development with Next.js, React, and TypeScript |
| `/infra` | [infra/CLAUDE.md](infra/CLAUDE.md) | Infrastructure scripts for GCP deployment and GitHub setup |
| `/` (root) | This file | General project guidance and monorepo commands |

Each CLAUDE.md file contains:
- Directory-specific commands and workflows
- Relevant architecture documentation
- Testing approaches for that component
- Environment variables and configuration
- Troubleshooting guides

## Commands Reference

### Frontend Development
```bash
cd frontend
pnpm run dev         # Start development server on http://localhost:3000
pnpm run build       # Build for production
pnpm run test        # Run all tests (Jest)
pnpm run test:watch  # Run tests in watch mode
pnpm run test:ci     # Run tests with coverage for CI
pnpm run lint        # Run ESLint
pnpm run typecheck   # TypeScript type checking
pnpm run generate:api # Generate API client from OpenAPI spec
```

### Backend Development
```bash
cd backend
uv sync --all-extras                      # Install all dependencies including voice
uv run python -m uvicorn src.main:app --reload  # Start API server
uv run poe test                          # Run all tests
uv run poe test-cov                      # Run tests with HTML coverage report
uv run poe check                         # Run ALL quality checks (format, lint, typecheck, test)
uv run poe format                        # Auto-fix formatting (black + isort)
uv run poe format-check                  # Check formatting without modifying
uv run poe lint                          # Run linting (ruff)
uv run poe lint-fix                      # Auto-fix linting issues
uv run poe typecheck                     # Run type checking (mypy)
uv run poe fix                           # Fix all auto-fixable issues (format + lint-fix)
uv run poe export-openapi                # Export OpenAPI schema for frontend
uv run poe setup                         # Development setup (sync deps + install pre-commit)

# Voice modality (optional)
uv sync --extra voice                    # Install voice dependencies only
```

### Monorepo Commands (from root)
```bash
npm run dev:frontend    # Run frontend
npm run dev:backend     # Run backend
npm run dev:all         # Run both concurrently
npm run test:all        # Test everything

# Additional commands from Makefile
make setup              # Initial project setup (installs pnpm, uv, dependencies)
make dev                # Start all services in development mode with Docker
make dev-frontend       # Start only frontend in development mode
make dev-backend        # Start only backend in development mode
make dev-docker-build   # Build all Docker images for development
make test               # Run all tests (frontend and backend)
make test-frontend      # Run frontend tests
make test-backend       # Run backend tests
make test-integration   # Run integration tests with Docker
make test-e2e           # Run E2E tests with Docker
make test-e2e-text      # Run text-only E2E tests
make test-e2e-voice     # Run voice-only E2E tests
make test-e2e-ui        # Run E2E tests in UI mode
make lint               # Run all linters
make lint-frontend      # Run frontend linter
make lint-backend       # Run backend linter
make format             # Format all code
make format-frontend    # Format frontend code
make format-backend     # Format backend code
make typecheck          # Run type checking
make typecheck-frontend # Run frontend type checking
make typecheck-backend  # Run backend type checking
make build              # Build all components
make build-frontend     # Build frontend
make build-backend      # Build backend Docker image
make docker-up          # Start all services with Docker Compose
make docker-down        # Stop all services
make docker-logs        # Show logs from all services
make docker-clean       # Clean up Docker resources
make install            # Install all dependencies
make install-frontend   # Install frontend dependencies
make install-backend    # Install backend dependencies
make pre-commit         # Run all pre-commit checks (lint, typecheck, test)
make clean              # Clean generated files and caches
make update-deps        # Update all dependencies (frontend and backend)
make deploy-frontend    # Deploy frontend via GitHub workflow
make deploy-backend     # Deploy backend via GitHub workflow
make ci-test            # Run tests as in CI
make check-docs         # Check if CLAUDE.md files need updating
make update-docs        # Update CLAUDE.md files (interactive)
make docs               # Serve documentation locally with MkDocs Material
```

### Docker Development
```bash
# Basic development (frontend + backend)
docker-compose up --build

# Full development environment (includes Redis, MailHog)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Run E2E tests
cd tests/e2e && ./run_tests.sh

# Stop all services
docker-compose down -v
```

### Utility Scripts
```bash
# From scripts/ directory
./run-e2e-tests.sh              # Run E2E tests with Docker environment
./run-e2e-tests.sh --text       # Run only text E2E tests
./run-e2e-tests.sh --voice      # Run only voice E2E tests
./run-e2e-tests.sh --ui         # Run E2E tests with UI mode
./export-openapi.sh             # Export OpenAPI schema from backend
./docker-build-with-schema.sh   # Build Docker images with OpenAPI schema
./check-github-secrets.sh       # Verify GitHub secrets are configured
./create_labels.sh              # Create GitHub issue labels
```

### GCP Infrastructure Scripts (NEW)
```bash
# From infra/gcp/ directory
./setup-gcp-infrastructure.sh      # Complete GCP project setup
./bootstrap_vpc_and_roles.sh       # VPC and IAM roles setup
./setup-workload-identity.sh       # GitHub Actions authentication setup
./harden-backend.sh                # Security hardening for backend service
./fix-frontend-auth.sh             # Frontend service authentication fix
./update-backend-env-vars.sh       # Update backend environment variables
./update-frontend-env-vars.sh      # Update frontend environment variables (NEW)
./registry_clean_policy.sh         # Container registry cleanup policies
```

### E2E Testing
```bash
# JavaScript E2E Tests (PRIMARY - use these)
# From root directory
npm run e2e                      # Run all JavaScript Playwright tests
npm run e2e:ui                   # Run with UI mode
npm run e2e:headed               # Run with browser visible
npm run e2e:debug                # Run in debug mode
npm run e2e:install              # Install Playwright browsers

# From playwright-js directory
cd playwright-js
npm test                         # Run all tests
npm run test:ui                  # Run with UI mode
npm run test:headed              # Run with browser visible
npm run test:debug               # Run in debug mode
npm run install                  # Install Playwright browsers

# Specific test patterns
cd playwright-js && npm test tests/voice-*.spec.js              # All voice tests
cd playwright-js && npm test tests/text-*.spec.js               # All text tests
cd playwright-js && npm test tests/voice-network-resilience.spec.js  # Specific test

# Python E2E tests (LEGACY - still available)
cd tests/e2e && ./run_tests.sh   # Run Python E2E tests with pytest-xdist

# Run E2E tests with Docker (recommended for CI)
./scripts/run-e2e-tests.sh       # Run all E2E tests
./scripts/run-e2e-tests.sh --text  # Text tests only
./scripts/run-e2e-tests.sh --voice # Voice tests only
./scripts/run-e2e-tests.sh --ui    # With UI mode

# From frontend directory (DEPRECATED - use playwright-js instead)
cd frontend
pnpm run test:e2e                # Run Playwright tests
pnpm run test:e2e:ui             # Run with UI mode
pnpm run test:e2e:debug          # Run in debug mode
pnpm run test:e2e:headed         # Run with browser visible
pnpm run test:e2e:report         # Show test report
```

## Project Management

### Linear Project
- **Primary project tracking in Linear**: https://linear.app/carlos-crespo/project/re-framesocial-cbt-assistant-6c36f6288cc8
- All issues from the fix plan are tracked there:
  - CAR-24: Remove duplicate backend/main.py entry point (Urgent)
  - CAR-25: Migrate to FastAPI lifespan protocol (Urgent)
  - CAR-26: Fix performance monitor task tracking (High)
  - CAR-27: Implement real language detection (High)
  - CAR-28: Add missing test coverage for UI components (Medium)

### GitHub Project Board
- **All project management is done via GitHub Projects**: https://github.com/users/macayaven/projects/7
- Work on issues in priority order: P0 (Critical) → P1 (High) → P2 (Medium)
- Issues are organized by Epic (Epic 0: Migration, Epic 1: Local Docker, Epic 2: Cloud Run)

## Git Workflow & Standards

### Commit Message Format
Commits MUST start with a task ID prefix:
- `[BE-XXX]` for backend tasks
- `[FE-XXX]` for frontend tasks
- `[ALL-XXX]` for shared/monorepo tasks
- `[INF-XXX]` for infrastructure tasks

Example: `[BE-141] Update CORS configuration for local API routes`

### Pull Request Guidelines
- Branch naming: `issue-{number}-{short-description}` (e.g., `issue-141-backend-api-routes`)
- PR title should match commit format: `[BE-141] Update CORS configuration`
- Always include `Closes #XXX` in PR description to auto-close issues
- All CI checks must pass before merging

### Pre-Push Checklist
**ALWAYS run checks locally before pushing:**
- Backend: `cd backend && uv run poe check`
- Frontend: `cd frontend && pnpm run lint && pnpm run typecheck && pnpm run test`

## Architecture

### Frontend Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS v3 with custom design tokens
- **Audio**: Web Audio API with AudioWorklets
- **Real-time**: Server-Sent Events (SSE) for streaming
- **Testing**: Jest with React Testing Library + Playwright
- **API Client**: Generated from OpenAPI schema using @hey-api/openapi-ts
  - **STRICT RULE**: Always use the auto-generated API client to prevent contract mismatches
  - Never manually implement API calls - use `/frontend/lib/api/generated-client.ts`

### Backend Tech Stack
- **Framework**: FastAPI
- **Language**: Python 3.12 (specifically requires 3.12)
- **Package Manager**: uv (NOT pip or poetry)
- **Main Module**: FastAPI app is at `src.main:app` (not `app.main:app`)
- **AI**: Google's Agent Development Kit (ADK) with Gemini models
- **Audio**: Processing for 16kHz PCM format
- **Voice** (optional): Google Cloud Speech-to-Text & Text-to-Speech
- **Testing**: pytest with 80% coverage requirement + pytest-xdist for parallel execution
- **Code Quality**: black, isort, ruff, mypy

### Deployment
- **Frontend**: Google Cloud Run (containerized, VPC egress for backend access)
- **Backend**: Google Cloud Run (containerized, internal ingress only)
- **CI/CD**: GitHub Actions with automated deployment
- **Service Auth**: Service-to-service authentication via Google Auth library
- **VPC Connector**: `run-to-run-connector` for internal communication
- **OpenAPI Integration**: Schema generated in backend CI, used in frontend build

## Key Architectural Patterns

### Frontend Architecture
- **Component Structure**: Components are in `/frontend/components/` with tests alongside
- **Core Libraries**: Business logic in `/frontend/lib/`
- **SSE Client**: Real-time streaming via `/frontend/lib/streaming/sse-client.ts`
- **Audio Processing**: Web Audio API with worklets in `/frontend/public/worklets/`
- **API Integration**: Type-safe client generated from backend OpenAPI schema

### Backend Architecture
- **Agent System**: Uses Google ADK Sequential Agents for conversation flow
- **Phases**: GREETING → DISCOVERY → REFRAMING → SUMMARY
- **Safety First**: Crisis detection at every user input
- **Session Management**: In-memory session state (no persistence beyond session)
- **Knowledge Base**: CBT context and techniques in `/backend/src/knowledge/`

## Environment Variables

### Backend Environment Variables
- `GEMINI_API_KEY`: Google AI services API key (not `GOOGLE_AI_API_KEY`)
- `CONFIGCAT_SDK_KEY`: Feature flags SDK key
- `SERVICE_NAME`: Service identifier for logging/monitoring
- `BACKEND_INTERNAL_HOST`: Internal service host for Cloud Run
- `BACKEND_PUBLIC_URL`: Public backend URL for authentication
- `GCP_PROJECT_ID`: Google Cloud project ID
- `GCP_REGION`: Google Cloud region

### Frontend Environment Variables
- `NEXT_PUBLIC_API_URL`: Public API URL for client-side calls
- `BACKEND_INTERNAL_HOST`: Internal backend host for service-to-service calls
- `BACKEND_PUBLIC_URL`: Public backend URL for authentication audience
- `NODE_ENV`: Environment (development/production)
- `SERVICE_NAME`: Service identifier for logging/monitoring
- `PORT`: Server port (default 3000 for dev, 8080 for production)

### Docker Development
- Docker uses `http://backend:8000` for service-to-service communication
- Local development uses `http://localhost:8000`
- Cloud Run uses internal hostnames like `re-frame-backend-yeetrlkwzq-ew.a.run.app`

## After Context Clear

When resuming work, provide:
1. Current issue number and description: "Working on issue #142 - Audio Conversion"
2. Link to GitHub project: https://github.com/users/macayaven/projects/7
3. Current branch: "We're on branch issue-142-audio-conversion"
4. Work completed so far: "We've already implemented X and Y"

## Working with Audio Features

- Frontend handles 48kHz WAV recording
- Backend expects 16kHz PCM (conversion handled by backend)
- No audio storage - only transcriptions are kept
- SSE for real-time streaming between frontend and backend

### Voice Modality (Optional)
- Google Cloud Speech-to-Text for voice input
- Google Cloud Text-to-Speech for voice output
- Voice tests located in `playwright-js/tests/voice-*.spec.js`
- Load tests for voice functionality in `tests/load/`
- Install with: `cd backend && uv sync --extra voice`

## Current Status

- **Monorepo**: Successfully migrated and operational
- **Frontend**: Fully functional with i18n support, enhanced UI components, and service-to-service auth
- **Backend**: Feature flags integration with ConfigCat, internal-only ingress for security
- **Infrastructure**: Complete GCP setup with VPC, IAM roles, and workload identity
- **Deployment**: Automated CI/CD to Google Cloud Run with OpenAPI schema integration
- **Testing**: Dual E2E test infrastructure - JavaScript (playwright-js/) as primary, Python (tests/e2e/) as legacy
- **Security**: Backend hardened with internal ingress, frontend uses VPC egress for backend access

## Key Files

- `/backend/CLAUDE.md` - Backend-specific development guidelines
- `/frontend/app/` - Next.js pages and routes
- `/frontend/components/` - React components
- `/frontend/lib/` - Core functionality
- `/backend/src/` - Backend source code (note: NOT `/backend/app/`)
- `/backend/src/agents/` - ADK agents
- `/docs/TEAM_COORDINATION_GUIDE.md` - Development workflow
- `/docs/archive/MONOREPO_MIGRATION_CHECKLIST.md` - Migration progress

## Testing Approach

Always check for existing test patterns before writing new tests:
- Frontend: Look for `*.test.tsx` files alongside components
- Backend: Look for `test_*.py` files in tests directory
- Use existing mocks and test utilities where available
- Coverage: Backend requires 80% minimum (excludes `src/utils/crawl.py`)

### Running Specific Tests
```bash
# Frontend - run single test file
cd frontend && pnpm test -- MessageList.test.tsx

# Backend - run single test file
cd backend && uv run pytest tests/test_greeting_phase.py -v

# Backend - run with specific test pattern
cd backend && uv run pytest -k "test_greeting" -v

# Integration tests with Docker
make test-integration

# Show Docker logs during tests
make docker-logs
```

### E2E Test Infrastructure
- **Python E2E tests**: Located in `tests/e2e/` with separate virtual environment
- **JavaScript E2E tests**: Located in `playwright-js/` directory (self-contained)
- **Voice E2E tests**: Voice network resilience tests in `playwright-js/tests/`
- **Environment**: E2E tests use `.env.test` file
- **Docker**: Integration tests use dedicated `docker-compose.integration.yml`
- **Parallel execution**: pytest-xdist enabled for faster test runs

## Important Implementation Notes

### When implementing features:
1. **Always run quality checks before committing**: Use `uv run poe check` for backend, full lint/test suite for frontend
2. **Follow existing patterns**: Check similar components/modules before creating new ones
3. **Maintain test coverage**: Backend requires 80% minimum
4. **Handle errors gracefully**: Especially for SSE connections and external API calls
5. **Keep security in mind**: Never log sensitive data, use environment variables for secrets

### OpenAPI Schema Integration (NEW)
- **Backend**: Automatically generates OpenAPI schema in CI workflow
- **Frontend**: Downloads schema artifact from backend CI for type-safe API client generation
- **CRITICAL**: Always use the auto-generated API client to prevent contract mismatches
- **Location**: `/frontend/lib/api/generated-client.ts`
- **Generation Command**: `pnpm run generate:api` in frontend

### Service-to-Service Authentication (NEW)
- **Cloud Run**: Internal backend with VPC connector for secure communication
- **Authentication**: Google Auth library handles service tokens automatically
- **Security**: Backend uses internal ingress (not publicly accessible)
- **Frontend Proxy**: `/app/api/proxy/[...path]/route.ts` handles backend authentication
- **VPC Configuration**: Uses `run-to-run-connector` with range `10.8.0.0/28`

### Code Quality Checklist
- [ ] **Names reveal intent**: Would a new developer understand what this does?
- [ ] **Functions do one thing**: Can you describe the function without using "and"?
- [ ] **No duplication**: Is this logic repeated elsewhere?
- [ ] **Tests are clean**: Are tests as readable as production code?
- [ ] **Complexity is managed**: Can you reason about this code easily?
- [ ] **Boy Scout Rule applied**: Is the code cleaner than when you started?

### Backend-Specific Guidelines
- Use `uv` as package manager (NOT pip or poetry)
- Follow ADK patterns for agent development
- Include `BASE_CBT_CONTEXT` in all agent instructions
- Implement crisis detection at every user input
- Write tests first (TDD approach)

### Frontend-Specific Guidelines
- Use App Router (not Pages Router)
- Follow existing component patterns in `/frontend/components/`
- Keep audio processing in Web Workers/AudioWorklets
- Handle SSE reconnection gracefully
- Maintain TypeScript strict mode
