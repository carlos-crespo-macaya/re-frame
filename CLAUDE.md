# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

re-frame is a web-based support tool for people with Avoidant Personality Disorder (AvPD), providing transparent AI-assisted cognitive reframing using evidence-based frameworks. The project is currently in planning phase with comprehensive specifications but no code implementation yet.

## Tech Stack (Planned)

- **Frontend**: Next.js 14 + Tailwind CSS v3 (static export to Firebase Hosting)
- **Backend**: Python 3.12 + FastAPI (containerized in Google Cloud Run)
- **LLMs**: Gemini 1.5 Flash via Vertex AI (PaLM 2 fallback)
- **Agent Framework**: Google AI Developer Kit (ADK)
- **Databases**: Cloud Firestore (documents), FAISS (vectors)
- **Auth**: Firebase Auth
- **Infrastructure**: Terraform
- **CI/CD**: GitHub Actions → Cloud Build

## Architecture

The system uses a multi-agent architecture:
- **Intake Agent**: Collects and validates user input
- **Framework Agent**: Applies CBT techniques for reframing
- **Synthesis Agent**: Processes raw LLM output into responses
- **Knowledge Agent**: Manages persistent learning data
- **Query Agent**: Handles semantic search

## Development Commands

As the project has no code yet, when implementation begins:

### Python Backend
```bash
# Setup virtual environment
python3.12 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies (once requirements.txt exists)
pip install -r requirements.txt

# Run tests (pytest will be used)
pytest
pytest --asyncio-mode=auto  # for async tests

# Run FastAPI locally
uvicorn main:app --reload

# Build Docker container
docker build --platform linux/amd64 -t re-frame-backend .
```

### Next.js Frontend
```bash
# Install dependencies (once package.json exists)
npm install

# Run development server
npm run dev

# Build for production
npm run build
npm run export  # for static export

# Run tests (when configured)
npm test
```

### Infrastructure
```bash
# Deploy with Terraform (once configured)
terraform init
terraform plan
terraform apply
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

## Project Structure (Planned)

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

## Important Context

- Target users have AvPD/severe social anxiety and may be skeptical of AI
- Building trust through transparency is critical
- The project follows a phased approach (P0 Alpha → P3)
- Each phase must deliver a complete, usable product
- Success metrics: 25 unique users, <10% abuse-flagged, ≥60% helpful feedback

When implementing, always consider the vulnerable user population and prioritize clear, non-judgmental communication in all UI/UX decisions.

## Project Management Protocol

When working on re-frame tasks:

1. **Start of Session**: 
   - Run `TodoRead` to check current tasks
   - Check GitHub Project board status (when available)
   - Review `/claude/project-management-plan.md` for task IDs
   - Note any blockers or dependencies

2. **During Work**:
   - Update task status when starting work using `TodoWrite`
   - Reference task IDs in all commits (e.g., `[BE-001] Add health check`)
   - Log time estimates vs actual in comments
   - Document any deviations from plan

3. **End of Session**:
   - Update all task statuses with `TodoWrite`
   - Create PR with task reference
   - Summarize progress and next steps

4. **Task References**:
   - Always include task ID in commits: `[BE-001] Add health check endpoint`
   - Link PRs to tasks using GitHub keywords (fixes #123)
   - Track completion in project management doc

5. **Important Decisions**:
   - **Therapist Portal**: DEFERRED to post-Phase 3 based on demand
   - Always challenge assumptions that could impact project success
   - No hidden decisions - communicate all architectural choices
   - Ask for clarification when requirements are ambiguous

## Task Management Reminders

### Automated Enforcement
- Git hooks enforce task IDs in commit messages (e.g., `[BE-001] Message`)
- Branch naming convention: `feature/BE-001-description` auto-populates task IDs
- GitHub Actions will comment on stale tasks (>24h without update)

### Task ID Format
- **INF-XXX**: Infrastructure tasks (Terraform, GCP, CI/CD)
- **BE-XXX**: Backend tasks (FastAPI, ADK agents, integrations)
- **FE-XXX**: Frontend tasks (Next.js, components, UX)
- **ALL-XXX**: Cross-team tasks (integration, testing, docs)

### Daily Checklist
- [ ] Morning: Check `/claude/project-management-plan.md` for assigned tasks
- [ ] Before coding: Update task to "in_progress" with `TodoWrite`
- [ ] During coding: Reference task ID in ALL commits
- [ ] After coding: Update task status and log actual time
- [ ] End of day: Note blockers and tomorrow's priorities

### Weekly Milestones
- **Monday**: Sprint planning, assign tasks from backlog
- **Wednesday**: Mid-week sync, address blockers
- **Friday**: Integration checkpoint, update project board

### Critical Path Awareness
Always prioritize tasks that:
1. Block other teams (API contracts, data models)
2. Have external dependencies (GCP setup, domain config)
3. Impact user-facing features directly
4. Relate to security or cost controls

### Cost & Quality Gates
Before marking any task complete:
- [ ] Verify no increase in GCP costs beyond plan
- [ ] Confirm all tests pass
- [ ] Check that documentation is updated
- [ ] Ensure security best practices followed
- [ ] Validate against success metrics

Remember: Each phase must deliver a **complete, usable product**. No task is done until it contributes to a deployable feature.

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

## Project Management Guidelines

- All documentation, intermediate scripts, and other artifacts that are not intended to be part of the project codebases should be located in the claude directory

## Claude Assistant Commitments

- Your job is to make this project successful, maximizing the chances of it by proving me wrong in each assumption that is not correct
- You will have failed if you allow me to take a decision that you know is not the best possible one and do not convince me out of it

## Communication and Decision-Making Guidelines

- Any deviation from our guidelines should be previously communicated and agreed, no hidden decisions should be taken
- In the face of ambiguity or doubt, always ask until you have all the required information to successfully carry out the commended task at hand