# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
├── docs/              # Shared documentation
├── scripts/           # Utility scripts
└── docker-compose.yml # Local development setup
```

## Directory-Specific Instructions

Claude will automatically use the most specific CLAUDE.md based on your working directory:
- **Working in `/frontend`**: Uses `frontend/CLAUDE.md` for frontend-specific guidance
- **Working in `/backend`**: Uses `backend/CLAUDE.md` for backend-specific guidance
- **Working in root or other directories**: Uses this file for general project guidance

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
make test-integration   # Run integration tests with Docker
make pre-commit         # Run all pre-commit checks (lint, typecheck, test)
make clean              # Clean generated files and caches
make update-deps        # Update all dependencies (frontend and backend)
make deploy-frontend    # Deploy frontend via GitHub workflow
make deploy-backend     # Deploy backend via GitHub workflow
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

### E2E Testing
```bash
# From root directory
npm run e2e                      # Run Playwright tests with main config
npm run e2e:ui                   # Run Playwright tests with UI mode
npm run e2e:js                   # Run JavaScript Playwright tests (playwright-js/)
npm run e2e:js:ui                # Run JavaScript Playwright tests with UI mode
npm run test:e2e:install         # Install Playwright browsers

# From frontend directory
cd frontend
pnpm run test:e2e                # Run Playwright tests
pnpm run test:e2e:ui             # Run with UI mode
pnpm run test:e2e:debug          # Run in debug mode
pnpm run test:e2e:headed         # Run with browser visible
pnpm run test:e2e:report         # Show test report

# Python E2E tests (separate infrastructure)
cd tests/e2e && ./run_tests.sh   # Run Python E2E tests with pytest-xdist

# Voice E2E tests
cd playwright-js && npm test tests/voice-network-resilience.spec.js
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
- **Frontend**: Google Cloud Run (containerized)
- **Backend**: Google Cloud Run (containerized)
- **CI/CD**: GitHub Actions with automated deployment

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
- Use `GEMINI_API_KEY` (not `GOOGLE_AI_API_KEY`) for Google AI services
- Docker uses `http://backend:8000` for service-to-service communication
- Local development uses `http://localhost:8000`

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

- **Epic 0**: Monorepo migration in progress
- **Frontend**: Fully functional, moved to frontend/ directory
- **Backend**: To be merged via git subtree (issue #136)

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