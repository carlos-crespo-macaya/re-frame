# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

re-frame.social is a web-based cognitive reframing support tool for people with Avoidant Personality Disorder (AvPD). It's a three-tier application using Google Cloud Platform services with a multi-agent AI system powered by Google Gemini 1.5 Flash.

## Architecture

- **Frontend**: Next.js 14 (TypeScript) in `frontend/` directory
- **Backend**: FastAPI (Python 3.12) in `backend/` directory  
- **Infrastructure**: Terraform configurations in `infrastructure/` directory
- **Multi-Agent System**: Intake → Framework → Synthesis agents with Knowledge/Query agents for data access

## Development Commands

### Backend (Python)
```bash
# Setup environment
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Development
poe dev        # Start FastAPI development server
poe test       # Run pytest tests
poe lint       # Run ruff linter
poe format     # Format with black
poe type-check # Run mypy type checking
poe check      # Run all checks (lint + format + type-check + tests)
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install   # Install dependencies
pnpm dev       # Start Next.js dev server on localhost:3000
pnpm build     # Build for production
pnpm test      # Run tests
pnpm lint      # Run ESLint
```

### Infrastructure (Terraform)
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
terraform fmt -check -recursive  # Check formatting
terraform validate              # Validate configuration
```

## Testing

- **Backend**: Run `poe test` to execute pytest suite. Single test: `pytest backend/tests/path/to/test.py::test_name`
- **Frontend**: Run `pnpm test` in frontend directory
- **CI**: All tests run automatically on PRs via GitHub Actions

## Key Conventions

1. **PR Titles**: Must include task ID prefix: [BE-XXX], [FE-XXX], [IF-XXX], or [ALL-XXX]
2. **Python**: Use UV for package management, Ruff for linting, Black for formatting
3. **TypeScript**: Use pnpm, follow Next.js 14 conventions
4. **API**: RESTful endpoints in `/api/v1/` namespace
5. **Environment Variables**: Store in `.env` files (never commit)

## Project Management

- The project management is done through github projects

## Multi-Agent AI System

The backend implements a multi-agent system using Google ADK:
- **Intake Agent**: Processes user input
- **Framework Agents**: Apply therapeutic frameworks (CBT, DBT, ACT, Stoicism)
- **Synthesis Agent**: Combines framework outputs
- **Knowledge/Query Agents**: Manage Firestore/FAISS data access

## Important Notes

- Project uses Google Cloud Platform services (Cloud Run, Firestore, Vertex AI)
- Designed for $300 GCP credit budget constraint
- Privacy-first: 7-day TTL for anonymous data
- Accessibility: WCAG AA compliance required
- Currently in Phase 0/Alpha - basic structure only, implementation pending

## Claude Workspace Guidelines

- All documentation, intermediate scripts, and other artifacts that are not intended to be part of the project codebases should be located in the claude directory

## Claude Code Instructions

- **Project Success Philosophy**: 
  - Your job is to make this project successful, maximizing the chances of success by proving me wrong in each assumption that is not correct
  - You will have failed if you allow me to take a decision that you know is not the best possible one and do not convince me otherwise

## Communication and Decision-Making Guidelines

- Any deviation from our guidelines should be previously communicated and agreed, no hidden decisions should be taken
- In the face of ambiguity or doubt, always ask until you have all the required information to successfully carry on the commended task at hand