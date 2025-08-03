# Deployment Options Guide

This document provides comprehensive guidance for deploying the re-frame application across different environments and scenarios.

## Table of Contents
1. [Local Development Deployment](#local-development-deployment)
2. [GitHub Actions Deployment](#github-actions-deployment)
3. [Manual Cloud Run Deployment](#manual-cloud-run-deployment)
4. [Deployment Comparison](#deployment-comparison)
5. [Troubleshooting](#troubleshooting)

---

## Local Development Deployment

### Option 1: Docker Compose (Recommended)

**Best for**: Full-stack development with all services running locally

#### Prerequisites
- Docker Desktop installed and running
- At least 8GB RAM allocated to Docker
- Ports 3000, 8000, 6379, 8025 available

#### Basic Setup
```bash
# From repository root
docker-compose up --build
```

**Services Started**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Redis: localhost:6379
- MailHog: http://localhost:8025

#### Development Mode with Hot Reload
```bash
# Use the development override
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

**Additional Features**:
- Volume mounts for hot reload
- Debug logging enabled
- Source maps enabled
- Development error pages

#### Environment Variables
Create `.env.local` in root:
```env
# Backend
GEMINI_API_KEY=your-api-key
CONFIGCAT_SDK_KEY=your-sdk-key
LOG_LEVEL=debug
ENVIRONMENT=development

# Frontend
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Option 2: Native Development

**Best for**: Rapid iteration, debugging, or working on single service

#### Backend Only
```bash
cd backend
uv sync --all-extras
uv run python -m uvicorn src.main:app --reload --port 8000
```

#### Frontend Only
```bash
cd frontend
pnpm install
pnpm run dev
```

#### Both Services (Concurrently)
```bash
# From root
make dev
# Or
npm run dev:all
```

### Option 3: Integration Testing Environment

**Best for**: Running E2E tests, testing service interactions

```bash
# Start integration environment
docker-compose -f docker-compose.integration.yml up --build

# In another terminal, run tests
cd playwright-js
npm test
```

**Differences from Development**:
- Optimized builds (production mode)
- No volume mounts
- Isolated network
- Pre-seeded test data
- Predictable service URLs

### Option 4: Minikube/Kind (Kubernetes Local)

**Best for**: Testing Kubernetes deployments, learning K8s

```bash
# Using Kind
kind create cluster --name re-frame-local

# Build and load images
docker build -t re-frame-frontend:local ./frontend
docker build -t re-frame-backend:local ./backend
kind load docker-image re-frame-frontend:local --name re-frame-local
kind load docker-image re-frame-backend:local --name re-frame-local

# Apply manifests (you'll need to create these)
kubectl apply -f ./infra/k8s/local/
```

---

## GitHub Actions Deployment

### Automated Workflow Trigger

The GitHub Actions deployment is triggered automatically or manually through `.github/workflows/deploy-cloudrun.yml`.

#### Automatic Triggers
1. **On CI Success**: Deploys after both Backend CI and Frontend CI pass
   ```yaml
   on:
     workflow_run:
       workflows: ["Backend CI", "Frontend CI"]
       types: [completed]
   ```

2. **Workflow Conditions**:
   - Only runs on `main` branch
   - Both CI workflows must succeed
   - Checks commit SHA consistency

#### Manual Trigger
```bash
# Via GitHub CLI
gh workflow run deploy-cloudrun.yml \
  -f environment=production \
  -f imageTag=v1.2.3 \
  -f force=false

# Via GitHub UI
# Go to Actions � Deploy to Cloud Run � Run workflow
```

### Deployment Process

#### Phase 1: Gate Check
- Verifies CI status
- Validates permissions
- Sets deployment parameters

#### Phase 2: Build & Push
```yaml
# Parallel build for both services
- Backend: Dockerfile with production target
- Frontend: Dockerfile.standalone with build args
- Push to: europe-west1-docker.pkg.dev/{project}/re-frame/
```

#### Phase 3: Deploy Backend (Internal)
```yaml
# Backend deployed with:
- Ingress: internal (VPC only)
- Authentication: Required (IAM)
- VPC Connector: run-to-run-connector
- Environment: Gen2
- Timeout: 300s
- Resources: 2 CPU, 1Gi RAM
```

#### Phase 4: Deploy Frontend (Public)
```yaml
# Frontend deployed with:
- Ingress: all (public access)
- Authentication: Not required
- VPC Egress: all (can reach backend)
- Backend URL: via BACKEND_INTERNAL_HOST
- Resources: 2 CPU, 1Gi RAM
```

#### Phase 5: IAM Configuration
```bash
# Automatic permission grant
gcloud run services add-iam-policy-binding backend \
  --member="serviceAccount:frontend-sa@project.iam" \
  --role="roles/run.invoker"
```

### Required Secrets

Configure in GitHub repository settings:

```yaml
# Authentication
GCP_WIF_PROVIDER: projects/{number}/locations/global/workloadIdentityPools/{pool}/providers/{provider}
GCP_WIF_SERVICE_ACCOUNT: github-actions-deploy@{project}.iam.gserviceaccount.com

# Project Configuration
GCP_PROJECT_ID: your-project-id
GCP_REGION: europe-west1
GCP_REGISTRY: europe-west1-docker.pkg.dev/{project}/re-frame

# API Keys
GEMINI_API_KEY: your-gemini-key
CONFIGCAT_API_KEY: your-configcat-key
```

---

## Manual Cloud Run Deployment

### Prerequisites

1. **Install gcloud CLI**:
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Ubuntu/Debian
   echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
   sudo apt-get update && sudo apt-get install google-cloud-cli
   ```

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable required APIs**:
   ```bash
   gcloud services enable \
     run.googleapis.com \
     artifactregistry.googleapis.com \
     cloudbuild.googleapis.com \
     vpcaccess.googleapis.com
   ```

### Step-by-Step Deployment

#### 1. Create Artifact Registry Repository
```bash
export PROJECT_ID="your-project-id"
export REGION="europe-west1"

gcloud artifacts repositories create re-frame \
  --repository-format=docker \
  --location=$REGION \
  --description="Re-frame application images"
```

#### 2. Build and Push Images
```bash
# Configure Docker
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build backend
cd backend
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/backend:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/backend:latest

# Build frontend
cd ../frontend
docker build -f Dockerfile.standalone \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/frontend:latest .
docker push $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/frontend:latest
```

#### 3. Create VPC Connector
```bash
gcloud compute networks vpc-access connectors create run-to-run-connector \
  --region=$REGION \
  --network=default \
  --range=10.8.0.0/28
```

#### 4. Deploy Backend (Internal)
```bash
gcloud run deploy re-frame-backend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/re-frame/backend:latest \
  --platform=managed \
  --region=$REGION \
  --execution-environment=gen2 \
  --timeout=300 \
  --vpc-connector=run-to-run-connector \
  --ingress=internal \
  --no-allow-unauthenticated \
  --port=8000 \
  --cpu=2 \
  --memory=1Gi \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=info,GEMINI_API_KEY=$GEMINI_API_KEY,CONFIGCAT_SDK_KEY=$CONFIGCAT_SDK_KEY"
```

#### 5. Deploy Frontend (Public)
```bash
gcloud run deploy re-frame-frontend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/re-frame/frontend:latest \
  --platform=managed \
  --region=$REGION \
  --execution-environment=gen2 \
  --timeout=300 \
  --allow-unauthenticated \
  --vpc-connector=run-to-run-connector \
  --vpc-egress=all \
  --port=8080 \
  --cpu=2 \
  --memory=1Gi \
  --min-instances=0 \
  --max-instances=10 \
  --set-env-vars="NODE_ENV=production,BACKEND_INTERNAL_HOST=re-frame-backend.$REGION.internal"
```

#### 6. Configure IAM Permissions
```bash
# Get frontend service account
FRONTEND_SA=$(gcloud run services describe re-frame-frontend \
  --region=$REGION \
  --format='value(spec.template.spec.serviceAccountName)')

# Grant backend access
gcloud run services add-iam-policy-binding re-frame-backend \
  --region=$REGION \
  --member="serviceAccount:$FRONTEND_SA" \
  --role="roles/run.invoker"
```

#### 7. Run Hardening Script
```bash
cd infra/gcp
./harden-backend.sh
```

### Quick Deployment Script

Create `deploy-to-cloudrun.sh`:
```bash
#!/bin/bash
set -euo pipefail

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:?"Set GCP_PROJECT_ID"}
REGION=${GCP_REGION:-"europe-west1"}
GEMINI_API_KEY=${GEMINI_API_KEY:?"Set GEMINI_API_KEY"}
CONFIGCAT_SDK_KEY=${CONFIGCAT_SDK_KEY:?"Set CONFIGCAT_SDK_KEY"}

echo "=� Starting deployment to Cloud Run..."

# Build and push images
echo "=� Building images..."
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/backend:latest ./backend
docker build -f ./frontend/Dockerfile.standalone \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/frontend:latest ./frontend

echo " Pushing images..."
docker push $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/backend:latest
docker push $REGION-docker.pkg.dev/$PROJECT_ID/re-frame/frontend:latest

echo "=' Creating VPC connector..."
gcloud compute networks vpc-access connectors create run-to-run-connector \
  --region=$REGION --network=default --range=10.8.0.0/28 --quiet || true

echo "= Deploying backend (internal)..."
gcloud run deploy re-frame-backend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/re-frame/backend:latest \
  --region=$REGION \
  --platform=managed \
  --execution-environment=gen2 \
  --timeout=300 \
  --vpc-connector=run-to-run-connector \
  --ingress=internal \
  --no-allow-unauthenticated \
  --port=8000 \
  --cpu=2 --memory=1Gi \
  --min-instances=0 --max-instances=10 \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=info,GEMINI_API_KEY=$GEMINI_API_KEY,CONFIGCAT_SDK_KEY=$CONFIGCAT_SDK_KEY" \
  --quiet

echo "< Deploying frontend (public)..."
gcloud run deploy re-frame-frontend \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/re-frame/frontend:latest \
  --region=$REGION \
  --platform=managed \
  --execution-environment=gen2 \
  --timeout=300 \
  --allow-unauthenticated \
  --vpc-connector=run-to-run-connector \
  --vpc-egress=all \
  --port=8080 \
  --cpu=2 --memory=1Gi \
  --min-instances=0 --max-instances=10 \
  --set-env-vars="NODE_ENV=production,BACKEND_INTERNAL_HOST=re-frame-backend.$REGION.internal" \
  --quiet

echo "= Configuring IAM..."
FRONTEND_SA=$(gcloud run services describe re-frame-frontend \
  --region=$REGION --format='value(spec.template.spec.serviceAccountName)')
gcloud run services add-iam-policy-binding re-frame-backend \
  --region=$REGION \
  --member="serviceAccount:$FRONTEND_SA" \
  --role="roles/run.invoker" \
  --quiet

echo " Deployment complete!"
echo "Frontend URL: $(gcloud run services describe re-frame-frontend --region=$REGION --format='value(status.url)')"
```

---

## Deployment Comparison

### Feature Matrix

| Feature | Docker Compose | Native Dev | GitHub Actions | Manual Cloud Run |
|---------|---------------|------------|----------------|------------------|
| **Setup Complexity** | Low | Low | Medium | High |
| **Environment Parity** | High | Low | Exact | Exact |
| **Hot Reload** | Yes* | Yes | No | No |
| **Debugging** | Medium | Easy | Hard | Hard |
| **Resource Usage** | High | Low | N/A | N/A |
| **Cost** | Free | Free | Free** | Pay-per-use |
| **Scalability** | No | No | Yes | Yes |
| **SSL/TLS** | Manual | No | Automatic | Automatic |
| **Custom Domain** | No | No | Yes | Yes |
| **IAM Security** | No | No | Yes | Yes |
| **CI/CD Integration** | No | No | Built-in | Manual |
| **Rollback** | Manual | Git | Automatic | Manual |

*With dev overlay
**Within GitHub Actions limits

### Key Differences

#### Development vs Production

**Local Development**:
- Direct file access and editing
- Immediate feedback loops
- Full debugging capabilities
- No authentication required
- Services communicate directly

**Cloud Run Production**:
- Containerized and isolated
- IAM-based authentication
- VPC-internal communication
- Auto-scaling and load balancing
- Managed SSL certificates

#### Security Model

**Local**:
```
Browser � Frontend (3000) � Backend (8000)
         Direct HTTP calls, no auth
```

**Cloud Run**:
```
Browser � Frontend (Public) � Proxy � Backend (Internal)
         HTTPS only        IAM Token    VPC-only access
```

#### Environment Variables

**Local Development**:
- `.env.local` files
- Direct API URLs
- Debug logging enabled
- Local service endpoints

**Cloud Run**:
- Injected at deployment
- Internal DNS names
- Production logging
- Managed secrets

### Best Practices

#### For Development
1. Use Docker Compose for full-stack work
2. Use native development for single-service debugging
3. Keep `.env.local` in sync with team
4. Test with integration environment before pushing

#### For Production
1. Always use GitHub Actions for consistency
2. Test in staging environment first
3. Use preview deployments for PRs
4. Monitor costs and set budget alerts

#### For Testing
1. Integration tests with Docker Compose
2. E2E tests against staging
3. Load tests against preview deployments
4. Security scans in CI pipeline

---

## Troubleshooting

### Common Issues

#### Docker Compose Issues

**Problem**: Services won't start
```bash
# Check logs
docker-compose logs -f [service-name]

# Reset everything
docker-compose down -v
docker system prune -a
docker-compose up --build
```

**Problem**: Port conflicts
```bash
# Find process using port
lsof -i :3000
kill -9 [PID]

# Or change ports in docker-compose.override.yml
```

#### Cloud Run Issues

**Problem**: Backend returns 403
```bash
# Check IAM permissions
gcloud run services get-iam-policy re-frame-backend --region=$REGION

# Re-run hardening script
./infra/gcp/harden-backend.sh
```

**Problem**: Frontend can't reach backend
```bash
# Verify VPC connector
gcloud compute networks vpc-access connectors describe run-to-run-connector --region=$REGION

# Check backend ingress setting
gcloud run services describe re-frame-backend --region=$REGION --format='value(metadata.annotations."run.googleapis.com/ingress")'
```

**Problem**: Deployment fails with quota error
```bash
# Check quotas
gcloud compute project-info describe --project=$PROJECT_ID

# Request increase via Console
```

### Debug Commands

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Test internal connectivity
gcloud run services proxy re-frame-backend --region=$REGION

# Check service status
gcloud run services list --region=$REGION

# View recent deployments
gcloud run revisions list --service=re-frame-frontend --region=$REGION
```

### Getting Help

1. Check logs first (always!)
2. Review this documentation
3. Check GitHub Issues
4. Ask in team Slack channel
5. Create detailed bug report with:
   - Deployment method used
   - Error messages
   - Steps to reproduce
   - Environment details

---

## Appendix

### Useful Scripts

Located in `/scripts/`:
- `deploy-to-cloudrun.sh` - Manual deployment
- `setup-gcp-infrastructure.sh` - Initial GCP setup
- `harden-backend.sh` - Security configuration
- `run-e2e-tests.sh` - E2E test runner

### Environment Templates

Find templates in `/templates/`:
- `.env.local.template` - Local development
- `.env.test.template` - Testing
- `secrets.yaml.template` - Kubernetes secrets

### Related Documentation

- [Internal Access Proxy Spec](../../internal_access.md)
- [Architecture Overview](../../../docs/architecture/README.md)
- [CI/CD Pipeline](../.github/workflows/README.md)
- [Security Guidelines](../../../docs/security/README.md)
