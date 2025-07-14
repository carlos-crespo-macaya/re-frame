# CI/CD Workflow Coordination Plan

## Overview

This document outlines the plan for updating CI/CD workflows to support the monorepo structure, ensuring efficient and correct builds for both frontend and backend components.

## Current State

### Frontend Workflows (Currently Active)
- **ci.yml**: Runs lint, typecheck, test, build, accessibility, and security checks
- **deploy-cloudrun.yml**: Production deployment to Cloud Run
- **deploy.yml**: General deployment workflow
- **release.yml**: Release management
- **security.yml**: Security scanning

### Backend Workflows (From git subtree)
- **backend/.github/workflows/ci.yml**: Python tests with uv, black, isort, ruff, mypy, pytest

### Disabled Workflows
- preview-cloudrun.yml.disabled
- cleanup-preview.yml.disabled
- pr-validation.yml.disabled

## Proposed Monorepo CI/CD Structure

### 1. Main CI Workflow (`ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # Determine what changed
  changes:
    runs-on: ubuntu-latest
    outputs:
      frontend: ${{ steps.changes.outputs.frontend }}
      backend: ${{ steps.changes.outputs.backend }}
      docs: ${{ steps.changes.outputs.docs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            frontend:
              - 'frontend/**'
              - '.github/workflows/frontend-*.yml'
              - 'package.json'
            backend:
              - 'backend/**'
              - '.github/workflows/backend-*.yml'
            docs:
              - 'docs/**'
              - '*.md'

  # Frontend Jobs (only run if frontend changed)
  frontend-lint:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    # ... existing frontend lint job with working-directory: frontend

  frontend-test:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    # ... existing frontend test job with working-directory: frontend

  # Backend Jobs (only run if backend changed)
  backend-test:
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12"]
    steps:
      - uses: actions/checkout@v4
      - name: Install uv
        uses: astral-sh/setup-uv@v3
      - name: Set up Python
        run: uv python install ${{ matrix.python-version }}
      - name: Install dependencies
        working-directory: backend
        run: uv sync --all-extras
      - name: Run checks
        working-directory: backend
        run: |
          uv run black --check .
          uv run isort --check-only .
          uv run ruff check .
          uv run mypy src
          uv run pytest

  # Integration tests (run if either changed)
  integration-tests:
    needs: changes
    if: needs.changes.outputs.frontend == 'true' || needs.changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      # Setup both environments and run integration tests
```

### 2. Deployment Workflows

#### Frontend Deployment (`deploy-frontend.yml`)
```yaml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
```

#### Backend Deployment (`deploy-backend.yml`)
```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
```

### 3. Workflow Organization

```
.github/workflows/
├── ci.yml                    # Main CI for all components
├── deploy-frontend.yml       # Frontend deployment
├── deploy-backend.yml        # Backend deployment
├── release.yml              # Release management (updated for monorepo)
├── security.yml             # Security scanning (both frontend & backend)
└── integration-tests.yml    # E2E tests when both components are involved
```

## Implementation Steps

### Phase 1: Update Main CI Workflow
1. Add path filtering to detect changes
2. Split jobs into frontend/backend sections
3. Add conditional execution based on changes
4. Ensure all jobs use correct working directories

### Phase 2: Create Separate Deployment Workflows
1. Split current deploy-cloudrun.yml into frontend/backend versions
2. Add path-based triggers
3. Update deployment scripts for monorepo structure
4. Test deployment pipelines independently

### Phase 3: Integration Testing
1. Create integration test workflow
2. Setup docker-compose for local testing
3. Add E2E tests that verify frontend/backend communication
4. Ensure tests run on PRs affecting either component

### Phase 4: Optimization
1. Implement caching strategies:
   - pnpm cache for frontend
   - uv cache for backend
   - Docker layer caching for builds
2. Parallelize independent jobs
3. Use matrix builds where appropriate

## Key Decisions Needed

1. **Deployment Strategy**:
   - Deploy both components together or independently?
   - Use separate Cloud Run services or single service with multiple containers?
   - How to handle database migrations?

2. **Version Management**:
   - Unified versioning or separate frontend/backend versions?
   - How to handle API versioning between components?

3. **Environment Variables**:
   - Centralized or separate .env files?
   - How to manage secrets in the monorepo?

4. **Testing Strategy**:
   - When to run integration tests vs unit tests?
   - Minimum coverage requirements for each component?

## Benefits of This Approach

1. **Efficiency**: Only run CI/CD for changed components
2. **Speed**: Parallel execution of independent jobs
3. **Clarity**: Clear separation of concerns
4. **Flexibility**: Easy to add new components
5. **Cost-Effective**: Reduced CI minutes by avoiding unnecessary runs

## Monitoring and Maintenance

1. **Workflow Analytics**:
   - Track CI run times
   - Monitor failure rates by component
   - Identify bottlenecks

2. **Regular Reviews**:
   - Monthly review of workflow performance
   - Quarterly optimization passes
   - Annual strategy reassessment

## Next Steps

1. Create a feature branch for CI/CD updates
2. Implement Phase 1 (Main CI Workflow)
3. Test with various change scenarios
4. Gradually roll out remaining phases
5. Document any decisions made during implementation