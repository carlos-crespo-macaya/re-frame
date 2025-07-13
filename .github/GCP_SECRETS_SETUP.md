# Google Cloud Secrets Configuration Guide

## Required Secrets for Cloud Run Deployment

These secrets must be added to your GitHub repository settings under Settings → Secrets and variables → Actions.

### 1. Google Cloud Authentication (Required)

#### `GCP_PROJECT_ID` (Required)
Your Google Cloud Project ID.

**How to get it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project from the dropdown
3. The Project ID is shown in the dashboard

#### `GCP_SA_KEY` (Required)
Service account key with necessary permissions for Cloud Run deployment.

**How to create it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "IAM & Admin" → "Service Accounts"
3. Click "Create Service Account"
4. Name it (e.g., `github-actions-deploy`)
5. Grant the following roles:
   - Cloud Run Developer
   - Service Account User
   - Container Registry Service Agent
   - Storage Object Admin (for GCR)
6. Click "Create Key" → Choose JSON
7. Copy the entire JSON content
8. Add it as `GCP_SA_KEY` secret in GitHub

### 2. Application Configuration

#### `NEXT_PUBLIC_API_URL` (Required)
The URL of your backend API service.

Example: `https://api-xxxxx.a.run.app` (your Cloud Run backend URL)

### 3. Optional Configuration

These can be set as secrets or hardcoded in the workflow:

- `GCP_REGION` - Default: `us-central1`
- `SERVICE_NAME` - Default: `re-frame-frontend`

## Setting Up Google Cloud

### 1. Enable Required APIs

Run these commands or enable in Console:

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Create Service Account (Alternative to Console)

Using gcloud CLI:

```bash
# Create service account
gcloud iam service-accounts create github-actions-deploy \
  --display-name="GitHub Actions Deploy"

# Grant permissions
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="github-actions-deploy@${PROJECT_ID}.iam.gserviceaccount.com"

# Cloud Run permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.developer"

# Service Account User
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Container Registry permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

# Create key
gcloud iam service-accounts keys create key.json \
  --iam-account="${SA_EMAIL}"

# Display key (copy this to GitHub secrets)
cat key.json
```

### 3. Set Up Artifact Registry (Recommended over GCR)

```bash
# Create repository
gcloud artifacts repositories create re-frame \
  --repository-format=docker \
  --location=us-central1 \
  --description="Re-frame Docker images"

# Configure Docker
gcloud auth configure-docker us-central1-docker.pkg.dev
```

## Local Development

### Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Ubuntu/Debian
curl https://sdk.cloud.google.com | bash
```

### Authenticate Locally

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### Test Deployment Locally

```bash
# Build image
docker build -t re-frame-frontend .

# Test locally
docker run -p 8080:8080 re-frame-frontend

# Deploy to Cloud Run
gcloud run deploy re-frame-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

Set these in Cloud Run or pass through deployment:

```yaml
NODE_ENV: production
NEXT_PUBLIC_API_URL: https://your-backend-url.a.run.app
```

## Cost Optimization

Cloud Run charges per request and compute time. To minimize costs:

1. Set minimum instances to 0
2. Use appropriate CPU and memory limits
3. Enable CPU throttling when idle
4. Set concurrency limits

## Monitoring

### View Logs

```bash
gcloud run services logs read re-frame-frontend --region us-central1
```

### View Metrics

Go to Cloud Console → Cloud Run → Select your service → Metrics tab

## Troubleshooting

### Build Fails
- Check if all APIs are enabled
- Verify service account permissions
- Check Docker build logs

### Deployment Fails
- Verify `GCP_SA_KEY` is valid JSON
- Check if service account has correct roles
- Ensure project ID is correct

### Service Not Accessible
- Check if `--allow-unauthenticated` is set
- Verify firewall rules
- Check Cloud Run service logs

### Image Push Fails
- Verify Container Registry/Artifact Registry permissions
- Check if Docker is configured: `gcloud auth configure-docker`

## Security Best Practices

1. Use least privilege for service accounts
2. Rotate service account keys periodically
3. Use Workload Identity Federation (advanced)
4. Enable Cloud Run Binary Authorization
5. Use Secret Manager for sensitive data

## Next Steps

After setting up secrets:

1. Push to main branch to trigger deployment
2. Check GitHub Actions for build status
3. Visit Cloud Run URL to verify deployment
4. Set up custom domain (optional)