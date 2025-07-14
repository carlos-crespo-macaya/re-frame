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
├── backend/           # FastAPI backend with ADK agents
├── docs/              # Shared documentation
├── scripts/           # Utility scripts
└── docker-compose.yml # Local development setup
```

## Project Management

## GitHub Project Board
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

## Environment Variables
- Use `GEMINI_API_KEY` (not `GOOGLE_AI_API_KEY`) for Google AI services
- Docker uses `http://backend:8000` for service-to-service communication
- Local development uses `http://localhost:8000`

# Key Commands

### Frontend Development
```bash
cd frontend
pnpm run dev        # Start development server on http://localhost:3000
pnpm run build      # Build for production
pnpm run test       # Run all tests
pnpm run lint       # Run ESLint
```

### Backend Development (after merge)
```bash
cd backend
python -m uvicorn app.main:app --reload  # Start API server
pytest              # Run tests
ruff check .        # Lint Python code
```

### Monorepo Commands (from root)
```bash
npm run dev:frontend    # Run frontend
npm run dev:backend     # Run backend
npm run dev:all         # Run both concurrently
npm run test:all        # Test everything
```

## Architecture

### Frontend Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript with strict mode
- **Styling**: Tailwind CSS v3 with custom design tokens
- **Audio**: Web Audio API with AudioWorklets
- **Real-time**: Server-Sent Events (SSE) for streaming
- **Testing**: Jest with React Testing Library

### Backend Tech Stack (coming soon)
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **AI**: Google's Agent Development Kit (ADK)
- **Audio**: Processing for 16kHz PCM format
- **Testing**: pytest

### Deployment
- **Frontend**: Google Cloud Run (containerized)
- **Backend**: Google Cloud Run (containerized)
- **CI/CD**: GitHub Actions with automated deployment

## After Context Clear

When resuming work, provide:
1. Current issue number and description: "Working on issue #142 - Audio Conversion"
2. Link to GitHub project: https://github.com/users/macayaven/projects/7
3. Current branch: "We're on branch issue-142-audio-conversion"
4. Work completed so far: "We've already implemented X and Y"

## Important Patterns

1. **Monorepo Structure**: Frontend and backend are separate but coordinated
2. **Path Prefixes**: Use relative paths within each project
3. **Shared Resources**: Documentation and scripts at root level
4. **Independent Builds**: Each service builds and deploys separately

## Working with Audio Features

- Frontend handles 48kHz WAV recording
- Backend expects 16kHz PCM (conversion handled by backend)
- No audio storage - only transcriptions are kept
- SSE for real-time streaming between frontend and backend

## Current Status

- **Epic 0**: Monorepo migration in progress
- **Frontend**: Fully functional, moved to frontend/ directory
- **Backend**: To be merged via git subtree (issue #136)

## Key Files

- `/backend/CLAUDE.md` - Backend-specific development guidelines
- `/frontend/app/` - Next.js pages and routes
- `/frontend/components/` - React components
- `/frontend/lib/` - Core functionality
- `/backend/app/` - FastAPI application (coming soon)
- `/backend/agents/` - ADK agents (coming soon)
- `/docs/TEAM_COORDINATION_GUIDE.md` - Development workflow
- `/docs/MONOREPO_MIGRATION_CHECKLIST.md` - Migration progress

## Testing Approach

Always check for existing test patterns before writing new tests:
- Frontend: Look for `*.test.tsx` files alongside components
- Backend: Look for `test_*.py` files in tests directory
- Use existing mocks and test utilities where available