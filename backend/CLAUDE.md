# Backend CLAUDE.md

This file provides backend-specific guidance to Claude Code (claude.ai/code) when working in the `/backend` directory of the re-frame monorepo.

## Development Environment

Always use `uv` as the Python package manager for this project:

```bash
# Install dependencies
uv sync --all-extras

# Install with voice modality support (optional)
uv sync --extra voice

# Run quality checks
uv run poe check

# Run specific tools
uv run poe format
uv run poe lint
uv run poe typecheck
uv run poe test
uv run poe export-openapi     # Export OpenAPI schema (NEW)

# Start development server
uv run python -m uvicorn src.main:app --reload  # Note: src.main:app, not app.main:app
```

### Voice Modality (Optional)
The backend supports voice functionality through Google Cloud services:
- **Speech-to-Text**: For transcribing user voice input
- **Text-to-Speech**: For generating voice responses
- Install with: `uv sync --extra voice`
- Voice tests: `uv run pytest tests/test_voice_*.py`
- Load tests: `uv run pytest tests/load/test_voice_concurrency.py`

## Implementation Philosophy

### Core Guidelines
1. **Keep this as simple as possible. Question any complexity. If there's a simpler way, tell me first.**
2. Use the Sequential Thinking MCP for step-by-step validation. Break down the problem, but also break down the solutions. At each step, ask: "Is this necessary?"
3. Always think in an agile and lean way: **"What's the simplest thing that could possibly work?"**
4. Before implementing, list:
   - What assumptions you're making
   - What complexity you're adding
   - What simpler alternatives exist

## Project Management Guidelines

**GitHub Issues and Linear are used for project management.**

### Linear Project Tracking
- **Primary project tracking in Linear**: https://linear.app/carlos-crespo/project/re-framesocial-cbt-assistant-6c36f6288cc8
- **IMPORTANT**: Always update Linear issues as you make progress:
  - Mark tasks as "In Progress" when starting work
  - Check off completed subtasks in the issue description
  - Add comments for important findings or blockers
  - Update status to "Done" when complete
  - Use the Linear MCP tools to update issues programmatically

### GitHub Integration
All progress and current status should always be kept up to date in both Linear and GitHub issues. This dual tracking ensures complete visibility.

- Update issue status as work progresses
- Add comments to issues for important decisions or blockers
- Use issue labels to track phase, feature area, and priority
- Reference issue numbers in commits (e.g., "Implement greeting agent #5")
- Close issues only when all acceptance criteria are met

## Development Workflow & CI/CD Strategy

**CRITICAL: Always run checks before pushing**
```bash
uv run poe check  # Runs format check, lint, typecheck, and tests
```
If formatting fails, run:
```bash
uv run poe format  # Auto-fixes formatting issues
```

**Every feature must follow this workflow:**

1. **Create Branch from Issue**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b issue-1-phase-0-cbt-context
   ```
   - Branch naming: `issue-{number}-{short-description}`
   - Always branch from latest main

2. **Development Process**
   - Make changes incrementally
   - Run tests locally: `uv run poe test`
   - Run all checks: `uv run poe check`
   - Commit with issue reference: `git commit -m "Add CBT context module #1"`

3. **Push and Verify**
   ```bash
   git push origin issue-1-phase-0-cbt-context
   ```
   - Ensure all local tests pass
   - Pre-commit hooks must pass
   - CI/CD workflow must show green

4. **Merge to Main**
   - Create PR referencing the issue
   - Wait for all CI checks to pass
   - Merge PR (squash and merge preferred)
   - Delete feature branch

5. **Update Local Main**
   ```bash
   git checkout main
   git pull origin main
   ```
   - **CRITICAL**: Always pull main before starting next task
   - This ensures you have the latest changes

### CI/CD Checks Required
- All unit tests pass (`pytest`)
- Code formatting correct (`black`, `isort`)
- Linting passes (`ruff`)
- Type checking passes (`mypy`)
- Coverage meets minimum (80%)

### Important Rules
- **Never work directly on main branch**
- **One issue = One branch = One PR**
- **Don't start new work until previous PR is merged**
- **Always verify CI passes before considering work complete**

## Backend Architecture

### Core Components
- **FastAPI Application**: Main app at `src/main.py` with lifespan management
- **Agent System**: Google ADK Sequential Agents for conversation flow
- **Session Management**: In-memory session state with cleanup tasks
- **Feature Flags**: ConfigCat integration for dynamic feature toggling
- **Performance Monitoring**: Built-in metrics and periodic reporting
- **Lifespan Protocol**: Uses FastAPI lifespan for startup/shutdown (NEW)
- **OpenAPI Generation**: Automatic schema export for frontend type safety (NEW)

### API Routers (UPDATED)
- **Text Router** (`src/text/router.py`): SSE endpoints for text conversations
- **Voice Router** (`src/voice/router.py`): Optional voice modality endpoints
- **Health Endpoint** (`/health`): Application health check
- **Metrics Endpoint** (`/metrics`): Performance metrics and monitoring (NEW)
- **Status Endpoint** (`/status`): Service status information (NEW)
- **Feature Flags** (`/api/feature-flags`): Dynamic UI configuration
- **API Documentation** (`/docs`): Auto-generated OpenAPI documentation
- **OpenAPI Schema** (`/openapi.json`): Machine-readable API specification

### Agent Phases
1. **GREETING**: Initial welcome and session setup
2. **DISCOVERY**: Understanding user's situation
3. **REFRAMING**: Applying CBT techniques
4. **SUMMARY**: Session recap and resources

### New Features
- **Feature Flags Service** (`src/utils/feature_flags/`): Dynamic feature management
- **Internationalization**: Multi-language support with language detection
- **Enhanced Logging**: Structured logging with performance metrics

## Environment Variables (NEW)

### Required Variables
- `GEMINI_API_KEY`: Google AI services API key (not `GOOGLE_AI_API_KEY`)
- `CONFIGCAT_SDK_KEY`: Feature flags SDK key

### Optional Variables
- `SERVICE_NAME`: Service identifier for logging (default: "re-frame-backend")
- `GCP_PROJECT_ID`: Google Cloud project ID (for voice features)
- `GCP_REGION`: Google Cloud region (for voice features)
- `BACKEND_INTERNAL_HOST`: Internal service host for Cloud Run
- `BACKEND_PUBLIC_URL`: Public backend URL for authentication

### Cloud Run Deployment
- **Internal Ingress**: Backend is not publicly accessible
- **VPC Connector**: Service-to-service communication via `run-to-run-connector`
- **OpenAPI Schema**: Generated in CI and used by frontend build

## Code Quality Standards

All tools are configured in `pyproject.toml` with balanced rules:
- **Black**: Standard Python formatting (88 char line length)
- **isort**: Import sorting compatible with Black
- **Ruff**: Fast linting with essential rules enabled
- **Mypy**: Type checking with gradual typing approach
- **Pytest**: Testing with 80% coverage requirement

Always run `uv run poe check` before committing changes.

## OpenAPI Schema Generation (NEW)

The backend automatically generates OpenAPI schema for frontend type safety:

```bash
# Generate OpenAPI schema manually
uv run poe export-openapi

# Or use Python directly
uv run python -c "from src.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json
```

### CI/CD Integration
- Schema is generated automatically in backend CI workflow
- Uploaded as artifact for frontend build to consume
- Ensures frontend/backend contract consistency

## Implementation Notes

When implementing features:
- Review the ADK documentation in `docs/adk-docs/` for agent development patterns
- Follow the conversation flow outlined in the design documents
- Ensure all CBT techniques are evidence-based
- Include appropriate disclaimers about not replacing professional therapy
- Implement robust error handling for service failures
- Write tests first (TDD approach)

### ADK-Specific Guidelines
- Use Sequential Agents for the main conversation flow
- Implement each conversation phase as a separate agent
- Use the CBT Knowledge Tool for domain-specific queries
- Include `BASE_CBT_CONTEXT` from `cbt_context.py` in all agent instructions
- Store conversation state in session memory between phases

### Testing Requirements
- Each phase must have comprehensive unit tests
- Test conversation transitions between phases
- Include edge case testing (empty inputs, crisis scenarios)
- Mock external dependencies (PDF generation, etc.)
- Aim for 80% code coverage minimum
- Use pytest-xdist for parallel test execution: `uv run pytest -n auto`

### Safety Implementation
- Crisis detection must be checked at every user input
- Implement fail-safe responses for crisis situations
- Never store sensitive user data beyond the session
- Include clear disclaimers in greeting and summary phases

## Important Reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless they're absolutely necessary
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files unless explicitly requested
