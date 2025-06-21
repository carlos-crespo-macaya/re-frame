# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

re-frame.social is a web-based cognitive reframing support tool for people with Avoidant Personality Disorder (AvPD). It's a three-tier application using Google Cloud Platform services with a multi-agent AI system powered by Google Gemini 1.5 Flash.

## Architecture

- **Frontend**: Next.js 14 (TypeScript) in `frontend/` directory
- **Backend**: FastAPI (Python 3.12) in `backend/` directory  
- **Infrastructure**: Terraform configurations in `infrastructure/` directory
- **Multi-Agent System**: Intake → Framework → Synthesis agents with Knowledge/Query agents for data access

## Tech Stack

- **Frontend**: Next.js 14 + Tailwind CSS v3 (static export to Firebase Hosting)
- **Backend**: Python 3.12 + FastAPI (containerized in Google Cloud Run)
- **LLMs**: Gemini 1.5 Flash via Vertex AI (PaLM 2 fallback)
- **Agent Framework**: Google AI Developer Kit (ADK)
- **Databases**: Cloud Firestore (documents), FAISS (vectors)
- **Auth**: Firebase Auth
- **Infrastructure**: Terraform
- **CI/CD**: GitHub Actions → Cloud Build

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

# Alternative setup (if UV not available)
python3.12 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run FastAPI locally
uvicorn main:app --reload

# Build Docker container
docker build --platform linux/amd64 -t re-frame-backend .
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

## Development Standards

### Mandatory Local Checks Before Pushing
**CRITICAL**: Every branch must pass ALL local checks before pushing. No exceptions.

1. **Run checks before EVERY push**:
   ```bash
   make check-all  # Runs all CI/CD checks locally
   # OR
   ./scripts/local-checks.sh  # Detailed output
   ```

2. **Local checks MUST be identical to CI/CD**:
   - Backend: Ruff linting, Black formatting, Mypy type checking, Pytest
   - Frontend: ESLint, build verification
   - Infrastructure: Terraform fmt and validate
   - Security: No secrets, no large files

3. **Never push if local checks fail** - fix issues first

### Test-Driven Development (TDD) Policy
**MANDATORY** for all feature development:

1. **Frontend & Backend**: TDD is required without exception
   - Write tests FIRST
   - Then write implementation to make tests pass
   - Refactor while keeping tests green

2. **Infrastructure**: May be excepted due to its nature

3. **No feature PRs without tests**:
   - Tests must exist before implementation
   - Tests must pass locally before pushing
   - Tests must cover the new functionality

4. **TDD Workflow**:
   ```bash
   # 1. Write failing test
   # 2. Run test to see it fail
   make test
   # 3. Write minimal code to pass
   # 4. Run test to see it pass
   make test
   # 5. Refactor if needed
   # 6. Ensure all checks pass
   make check-all
   ```

## Key Implementation Priorities

1. **Cost Efficiency**: Stay within $300 GCP credit budget
   - Use Gemini 1.5 Flash (cheapest model)
   - Implement aggressive caching
   - Rate limiting: 10 requests/hour per user

2. **Security & Privacy**:
   - No PII storage
   - Ephemeral sessions by default
   - Content filtering for harmful inputs
   - HTTPS-only with CSP headers

3. **Transparency**: 
   - All LLM reasoning paths must be exposed to users
   - Show which CBT techniques are being applied
   - Explain why specific reframings are suggested

4. **Phase 0 Alpha Goals**:
   - Single-page form for thought input
   - CBT-based reframing response
   - Basic rate limiting
   - Toxicity filtering

## Project Structure

```
re-frame/
├── backend/
│   ├── agents/          # ADK agent implementations
│   ├── api/            # FastAPI endpoints
│   ├── middleware/     # Rate limiting, auth
│   └── tests/          # Pytest test files
├── frontend/
│   ├── app/            # Next.js app directory
│   ├── components/     # React components
│   └── public/         # Static assets
├── infrastructure/
│   ├── terraform/      # IaC configuration
│   └── docker/         # Container definitions
└── docs/               # Product specs and documentation
```

## Project Management

**SINGLE SOURCE OF TRUTH**: GitHub Project "re-frame" (ID: 3)

### Project Management Protocol

**CRITICAL**: The GitHub project board is the ONLY place to track tasks, status, and progress. No local files or todo lists.

1. **Start of Session**: 
   - Check GitHub Project board: `gh project view 3 --owner macayaven`
   - Review open issues and their status
   - Check assigned tasks and priorities

2. **During Work**:
   - Update issue status on GitHub project board
   - Reference issue numbers in all commits (e.g., `[BE-001] Add health check #7`)
   - Comment on issues with progress updates
   - Use GitHub issue comments for any blockers or questions

3. **End of Session**:
   - Update issue status on GitHub project board
   - Comment on issues with work completed
   - Create PR linked to the issue

4. **Task References**:
   - Always include issue number in commits: `[BE-001] Add health check endpoint #7`
   - Link PRs to issues using GitHub keywords: `Fixes #7` or `Closes #7`
   - All task tracking happens in GitHub issues/project

5. **Important Decisions**:
   - Document architectural decisions in issue comments
   - Use issue labels for categorization
   - Create new issues for discovered tasks
   - No hidden decisions - everything tracked in GitHub

### Task Management Reminders

#### Automated Enforcement
- Git hooks enforce task IDs in commit messages (e.g., `[BE-001] Message`)
- Branch naming convention: `feature/BE-001-description` auto-populates task IDs
- GitHub Actions will comment on stale tasks (>24h without update)

#### Task ID Format
- **INF-XXX**: Infrastructure tasks (Terraform, GCP, CI/CD)
- **BE-XXX**: Backend tasks (FastAPI, ADK agents, integrations)
- **FE-XXX**: Frontend tasks (Next.js, components, UX)
- **ALL-XXX**: Cross-team tasks (integration, testing, docs)

#### Daily Checklist
- [ ] Morning: Check `/claude/project-management-plan.md` for assigned tasks
- [ ] Before coding: Update task to "in_progress" with `TodoWrite`
- [ ] During coding: Reference task ID in ALL commits
- [ ] After coding: Update task status and log actual time
- [ ] End of day: Note blockers and tomorrow's priorities

#### Weekly Milestones
- **Monday**: Sprint planning, assign tasks from backlog
- **Wednesday**: Mid-week sync, address blockers
- **Friday**: Integration checkpoint, update project board

#### Critical Path Awareness
Always prioritize tasks that:
1. Block other teams (API contracts, data models)
2. Have external dependencies (GCP setup, domain config)
3. Impact user-facing features directly
4. Relate to security or cost controls

#### Cost & Quality Gates
Before marking any task complete:
- [ ] Verify no increase in GCP costs beyond plan
- [ ] Confirm all tests pass
- [ ] Check that documentation is updated
- [ ] Ensure security best practices followed
- [ ] Validate against success metrics

Remember: Each phase must deliver a **complete, usable product**. No task is done until it contributes to a deployable feature.

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
- Target users have AvPD/severe social anxiety and may be skeptical of AI
- Building trust through transparency is critical
- The project follows a phased approach (P0 Alpha → P3)
- Each phase must deliver a complete, usable product
- Success metrics: 25 unique users, <10% abuse-flagged, ≥60% helpful feedback

When implementing, always consider the vulnerable user population and prioritize clear, non-judgmental communication in all UI/UX decisions.

## MCP (Model Context Protocol) Tools

Always check available MCP tools when encountering issues or needing specialized functionality. Key MCPs include:

### Development & Documentation
- **mcp__sequential-thinking__sequentialthinking**: For complex problem-solving and planning
- **mcp__memory__***: Knowledge graph operations for persistent information
- **mcp__server-github__***: GitHub operations (repos, issues, PRs)
- **mcp__playwright__***: Browser automation and testing

### Infrastructure & Cloud
- **mcp__docker-mcp__***: Docker container management
- **mcp__mcp-server-kubernetes__***: Kubernetes operations
- **mcp__gcp__***: Google Cloud Platform operations
- **mcp__terraform__***: Terraform documentation and modules

### When to Use MCPs
- **Tool/Script Failures**: Use appropriate MCP for updated documentation
- **GitHub Operations**: Use mcp__server-github instead of gh CLI when possible
- **Cloud Setup**: Use mcp__gcp for GCP operations
- **Testing**: Use mcp__playwright for browser testing
- **Complex Planning**: Use mcp__sequential-thinking for multi-step problems

Example: If `gh project create` fails, check GitHub API docs via MCP tools for current syntax.

## Git Workflow Protocol

### Branch Management
**NEVER commit directly to main branch**. Always follow this workflow:

1. **Create feature branch**:
   ```bash
   git checkout -b feature/[TASK-ID]-brief-description
   # Examples:
   # feature/BE-001-fastapi-setup
   # feature/INF-002-terraform-config
   # fix/FE-003-form-validation
   ```

2. **Make changes and commit**:
   ```bash
   # Stage changes
   git add .
   # Commit with task ID (hooks will enforce this)
   git commit -m "[BE-001] Initialize FastAPI project structure"
   ```

3. **Push to origin**:
   ```bash
   git push -u origin feature/[TASK-ID]-brief-description
   ```

4. **Create Pull Request**:
   ```bash
   # Using gh CLI
   gh pr create --title "[TASK-ID] Brief description" \
                --body "## Summary\n- What changed\n- Why it changed\n\n## Testing\n- How to test\n\n## Task\nCloses #issue-number"
   ```

### Commit Guidelines
- Always include task ID: `[BE-001] Message`
- Keep commits atomic and focused
- Write clear, imperative mood messages
- If fixing a bug, reference issue: `[BE-001] Fix auth error (fixes #123)`

### PR Requirements
- Link to GitHub issue/task
- Include testing instructions
- Update documentation if needed
- Ensure all checks pass before merge

### My Responsibilities
When you ask me to implement a task, I will:
1. Create appropriate feature branch
2. Make necessary changes
3. Commit with proper task ID
4. Push to remote
5. Create PR for your review
6. Never merge without your approval

## Claude Workspace Guidelines

- All documentation, intermediate scripts, and other artifacts that are not intended to be part of the project codebases should be located in the claude directory

## Claude Code Instructions

- **Project Success Philosophy**: 
  - Your job is to make this project successful, maximizing the chances of success by proving me wrong in each assumption that is not correct
  - You will have failed if you allow me to take a decision that you know is not the best possible one and do not convince me otherwise

## Communication and Decision-Making Guidelines

- Any deviation from our guidelines should be previously communicated and agreed, no hidden decisions should be taken
- In the face of ambiguity or doubt, always ask until you have all the required information to successfully carry on the commended task at hand
