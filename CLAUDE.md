# CLAUDE.md

This file provides specific guidance to Claude Code (claude.ai/code) when working with the reframe-agents repository.

## Development Environment

Always use `uv` as the Python package manager for this project:

```bash
# Install dependencies
uv sync --all-extras

# Run quality checks
uv run poe check

# Run specific tools
uv run poe format
uv run poe lint
uv run poe typecheck
uv run poe test
```

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

**GitHub Issues are the single source of truth for project management.**

All progress and current status should always be kept up to date in the issues created in the GitHub project. This will be the only and unique source of truth for project management. Let's prevent having scattered to-do documents, etc. Let's use issues exclusively for that.

- Update issue status as work progresses
- Add comments to issues for important decisions or blockers
- Use issue labels to track phase, feature area, and priority
- Reference issue numbers in commits (e.g., "Implement greeting agent #5")
- Close issues only when all acceptance criteria are met

## Development Workflow & CI/CD Strategy

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

## Documentation Reference

The `/Users/carlos/workspace/reframe-agents/docs` directory contains all relevant official documentation to be used as reference in case of doubt. This includes:
- Google ADK documentation in `docs/adk-docs/`
- Design documents in `docs/design/`
- Any additional reference materials

## Code Quality Standards

All tools are configured in `pyproject.toml` with balanced rules:
- **Black**: Standard Python formatting (88 char line length)
- **isort**: Import sorting compatible with Black
- **Ruff**: Fast linting with essential rules enabled
- **Mypy**: Type checking with gradual typing approach
- **Pytest**: Testing with 80% coverage requirement

Always run `uv run poe check` before committing changes.

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
