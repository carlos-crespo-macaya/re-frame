#!/bin/bash
set -euo pipefail

# Secure Setup Script using Workload Identity Federation
# This eliminates the need for service account keys

echo "🔐 Setting up Workload Identity Federation for GitHub Actions"
echo "==========================================================="

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-actions-provider"
SA_NAME="github-actions-deploy"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Get GitHub repository info
read -p "Enter your GitHub username/org: " GITHUB_ORG
read -p "Enter your GitHub repository name: " GITHUB_REPO

echo ""
echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  GitHub Repo: $GITHUB_ORG/$GITHUB_REPO"
echo "  Service Account: $SA_EMAIL"
echo ""

# Enable required APIs
echo "🔧 Enabling Workload Identity APIs..."
gcloud services enable iamcredentials.googleapis.com

# Create Workload Identity Pool
echo "🏊 Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create $POOL_NAME \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --description="Pool for GitHub Actions authentication" || echo "Pool already exists"

# Create Workload Identity Provider
echo "🔗 Creating Workload Identity Provider..."
# Note: The attribute-condition is required to avoid the "must reference provider claims" error
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
  --location="global" \
  --workload-identity-pool=$POOL_NAME \
  --display-name="GitHub Actions Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner == '${GITHUB_ORG}'" \
  --issuer-uri="https://token.actions.githubusercontent.com" || echo "Provider already exists"

# Get Workload Identity Pool ID
POOL_ID=$(gcloud iam workload-identity-pools describe $POOL_NAME \
  --location="global" \
  --format="value(name)")

# Grant service account permissions to use Workload Identity
echo "🔐 Configuring service account permissions..."
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Output configuration for GitHub Actions
echo ""
echo "✅ Workload Identity Federation setup complete!"
echo ""
echo "Add these to your GitHub repository secrets:"
echo "=========================================="
echo "WIF_PROVIDER: projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_NAME}/providers/${PROVIDER_NAME}"
echo "WIF_SERVICE_ACCOUNT: $SA_EMAIL"
echo ""
echo "Update your GitHub Actions workflow to use:"
echo "=========================================="
cat << 'EOF'
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
EOF
echo ""
echo "No service account keys needed! 🎉"