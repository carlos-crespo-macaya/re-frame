# Backend Worktree Handoff - Issue #137 CI/CD Workflows

## Current Status

You are working in a **git worktree** for the backend team to avoid collisions with the frontend work. This worktree should be on branch `feat/issue-137-backend-cicd`.

### What Has Been Done So Far:

1. **Issue #135** ✅ - Frontend repository restructured into monorepo
2. **Issue #136** ✅ - Backend code merged via git subtree 
3. **Issue #137** 🚧 - Currently working on CI/CD workflows (both teams collaborating)

### Recent Backend Commits:
```
8bb89bf5 [BE-137] Add unified monorepo CI workflow #137
734f62e2 [BE-137] Add backend CI workflow for testing and deployment #137
2aca7483 [BE-137] Add health check endpoint and Docker configuration for Cloud Run #137
```

## Your Current Task: Complete Issue #137

### Files Already Created by Backend Team:
- `.github/workflows/ci-monorepo.yml` - Main CI workflow with path filtering
- `.github/workflows/backend-ci.yml` - Backend-specific CI workflow
- `docker-compose.yml` - Basic docker-compose setup
- `backend/Dockerfile` - Already exists from your previous work

### Files Created by Frontend Team (in main repo):
- `.github/workflows/deploy-frontend.yml` - Frontend deployment workflow
- `docker-compose.dev.yml` - Development overrides
- `Makefile` - Common development commands
- Updated `frontend/Dockerfile` - Added development stage

## What You Need to Do:

### 1. Create Backend Deployment Workflow
Create `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

env:
  PYTHON_VERSION: '3.12'
  UV_VERSION: '0.4.15'
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_NAME: 'cbt-assistant-api'
  REGION: 'us-central1'

jobs:
  build-and-deploy:
    name: Build and Deploy Backend
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'production' }}
    permissions:
      contents: read
      id-token: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: ${{ env.UV_VERSION }}

      - name: Set up Python
        run: uv python install ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        working-directory: backend
        run: uv sync --all-extras

      - name: Run tests
        working-directory: backend
        run: uv run pytest

      # Authenticate to Google Cloud
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Configure Docker for Artifact Registry
        run: |
          gcloud auth configure-docker ${REGION}-docker.pkg.dev

      # Build and push Docker image
      - name: Build Docker image
        working-directory: backend
        run: |
          docker build \
            --build-arg PYTHON_VERSION=${{ env.PYTHON_VERSION }} \
            --build-arg UV_VERSION=${{ env.UV_VERSION }} \
            -t ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cbt-assistant/${SERVICE_NAME}:${{ github.sha }} \
            -t ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cbt-assistant/${SERVICE_NAME}:latest \
            .

      - name: Push Docker image
        run: |
          docker push ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cbt-assistant/${SERVICE_NAME}:${{ github.sha }}
          docker push ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cbt-assistant/${SERVICE_NAME}:latest

      # Deploy to Cloud Run
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy ${SERVICE_NAME} \
            --image ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/cbt-assistant/${SERVICE_NAME}:${{ github.sha }} \
            --platform managed \
            --region ${REGION} \
            --allow-unauthenticated \
            --min-instances 1 \
            --max-instances 10 \
            --memory 2Gi \
            --cpu 2 \
            --port 8000 \
            --set-env-vars "ENVIRONMENT=production" \
            --set-env-vars "GOOGLE_API_KEY=${{ secrets.GOOGLE_API_KEY }}" \
            --set-env-vars "LOG_LEVEL=info" \
            --service-account ${{ secrets.CLOUD_RUN_SERVICE_ACCOUNT }}

      - name: Get service URL
        id: get-url
        run: |
          SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
            --platform managed \
            --region ${REGION} \
            --format 'value(status.url)')
          echo "service_url=${SERVICE_URL}" >> $GITHUB_OUTPUT
          echo "Deployed to: ${SERVICE_URL}"

      # Run smoke tests
      - name: Run smoke tests
        run: |
          SERVICE_URL="${{ steps.get-url.outputs.service_url }}"
          echo "Testing deployment at ${SERVICE_URL}"
          
          # Test health endpoint
          HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}/health")
          if [ $HTTP_CODE -ne 200 ]; then
            echo "Health check returned HTTP ${HTTP_CODE}"
            exit 1
          fi
          echo "✅ Health check passed"
          
          # Test SSE endpoint availability
          SSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}/api/events/test-session")
          if [ $SSE_CODE -ne 200 ]; then
            echo "⚠️  SSE endpoint returned HTTP ${SSE_CODE}"
          fi

      # Deployment summary
      - name: Deployment summary
        run: |
          echo "## Deployment Summary 🚀"
          echo "- **Service**: ${SERVICE_NAME}"
          echo "- **Version**: ${{ github.sha }}"
          echo "- **Environment**: ${{ github.event.inputs.environment || 'production' }}"
          echo "- **URL**: ${{ steps.get-url.outputs.service_url }}"
          echo "- **Region**: ${REGION}"
```

### 2. Create Integration Tests Workflow
Create `.github/workflows/integration-tests.yml` - This should test both frontend and backend together when either changes.

### 3. Update Your Backend Dockerfile
Ensure your `backend/Dockerfile` supports both development and production stages (similar to how frontend was updated).

### 4. Create docker-compose.test.yml
For running integration tests in CI.

## Coordination Points with Frontend:

1. **CI Workflow Structure** - We're using path-based filtering
   - Frontend changes only trigger frontend CI
   - Backend changes only trigger backend CI
   - Both changed = integration tests run

2. **Docker Compose** - Shared services defined
   - Backend on port 8000
   - Frontend on port 3000
   - Redis for session management
   - Development overrides in docker-compose.dev.yml

3. **Deployment Strategy** - Separate Cloud Run services
   - Frontend: `cbt-assistant-web`
   - Backend: `cbt-assistant-api`
   - Independent scaling and deployment

## Environment Variables Needed:

### GitHub Secrets (should already be configured):
- `GCP_PROJECT_ID`
- `WIF_PROVIDER` 
- `WIF_SERVICE_ACCOUNT`
- `CLOUD_RUN_SERVICE_ACCOUNT`
- `GOOGLE_API_KEY`
- `CODECOV_TOKEN`
- `SNYK_TOKEN`

### GitHub Variables:
- `NEXT_PUBLIC_API_URL` (for frontend to know backend URL)

## Testing Your Changes:

1. **Test CI locally** (if you have act installed):
   ```bash
   act -W .github/workflows/backend-ci.yml push
   ```

2. **Test Docker build**:
   ```bash
   cd backend
   docker build -t cbt-backend:test .
   ```

3. **Test docker-compose**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up backend
   ```

## Next Steps After Completing CI/CD:

1. **Issue #139** - Archive the reframe-agents repository
2. Create PR for all CI/CD changes
3. Test the complete workflow from PR to deployment

## Important Notes:

- Keep all changes in your worktree branch `feat/issue-137-backend-cicd`
- The frontend team is working in parallel on their CI/CD parts
- Once both teams are done, we'll merge both branches
- The main `ci-monorepo.yml` should be the primary CI workflow

## Questions to Consider:

1. Do you need any additional deployment configuration for ADK/FastAPI?
2. Are there any special Cloud Run settings needed for the backend?
3. Do we need to set up any Cloud SQL or other GCP services?
4. What monitoring/logging should be configured?

## Frontend Team Contact:
If you need to coordinate or have questions, post in the GitHub Discussion #168 or comment on issue #137.

Good luck! 🚀