#!/bin/bash
set -euo pipefail

# GCP Infrastructure Setup Script for re-frame
# This script sets up the necessary GCP resources for deploying the application
#
# Environment variables (optional):
#   GCP_PROJECT_ID - Your GCP project ID
#   GCP_REGION - Your preferred region (default: europe-west1)
#   GCP_BILLING_ACCOUNT_ID - Your GCP billing account ID
#
# Usage:
#   ./setup-gcp-infrastructure.sh
#   
#   # Or with environment variables:
#   GCP_PROJECT_ID=my-project GCP_REGION=us-central1 ./setup-gcp-infrastructure.sh

echo "🚀 GCP Infrastructure Setup for re-frame"
echo "======================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configuration - check for environment variables first
if [ -n "$GCP_PROJECT_ID" ]; then
    PROJECT_ID=$GCP_PROJECT_ID
    echo "Using GCP_PROJECT_ID from environment: $PROJECT_ID"
else
    read -p "Enter your GCP Project ID: " PROJECT_ID
fi

if [ -n "$GCP_REGION" ]; then
    REGION=$GCP_REGION
    echo "Using GCP_REGION from environment: $REGION"
else
    read -p "Enter your preferred region (default: europe-west1): " REGION
    REGION=${REGION:-europe-west1}
fi

# For Cloud Run, we'll use the automatic domain (*.run.app)
echo "ℹ️  Cloud Run will provide automatic domains (*.run.app)"
echo "   You can add a custom domain later if needed."
DOMAIN="run.app"

# Service account name
SA_NAME="github-actions-deploy"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo ""
echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Domain: $DOMAIN"
echo "  Service Account: $SA_EMAIL"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Set project
echo "📋 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    iap.googleapis.com \
    cloudresourcemanager.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com

# Create Artifact Registry repository (if not exists)
echo "📦 Creating Artifact Registry repository..."
if ! gcloud artifacts repositories describe re-frame --location=$REGION &>/dev/null; then
    gcloud artifacts repositories create re-frame \
        --repository-format=docker \
        --location=$REGION \
        --description="Docker images for re-frame application"
else
    echo "  Repository already exists, skipping..."
fi

# Create service account for GitHub Actions
echo "👤 Creating service account for GitHub Actions..."
if ! gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
    gcloud iam service-accounts create $SA_NAME \
        --display-name="GitHub Actions Deploy"
else
    echo "  Service account already exists, skipping..."
fi

# Grant necessary permissions
echo "🔐 Granting permissions to service account..."
ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/storage.admin"
    "roles/artifactregistry.admin"
    "roles/cloudbuild.builds.editor"
)

for ROLE in "${ROLES[@]}"; do
    echo "  Granting $ROLE..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SA_EMAIL" \
        --role="$ROLE" \
        --quiet
done

# Create and download service account key
echo "🔑 Creating service account key..."
KEY_FILE="${SA_NAME}-key.json"
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL

echo ""
echo "⚠️  IMPORTANT: Service account key saved to $KEY_FILE"
echo "   1. Add this as GCP_SA_KEY secret in GitHub"
echo "   2. Delete the local file after adding to GitHub"
echo "   3. Keep this key secure!"

# Create OAuth 2.0 credentials for IAP
echo ""
echo "🔒 Setting up IAP (Identity-Aware Proxy)..."
echo ""
echo "Please follow these manual steps in the GCP Console:"
echo "1. Go to: https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
echo "2. Click 'Create Credentials' → 'OAuth client ID'"
echo "3. If prompted, configure the OAuth consent screen:"
echo "   - User Type: Internal (for organization) or External"
echo "   - Add authorized domains:"
echo "     • run.app (for Cloud Run services)"
echo "     • Your organization domain (if using Google Workspace)"
echo "4. Application type: Web application"
echo "5. Name: re-frame IAP"
echo "6. Authorized redirect URIs:"
echo "   - https://iap.googleapis.com/v1/oauth/clientIds/[CLIENT_ID]:handleRedirect"
echo "7. Save the Client ID and Client Secret"
echo ""
read -p "Press Enter when you've created the OAuth credentials..."

# Get OAuth credentials
read -p "Enter the OAuth Client ID: " CLIENT_ID
read -sp "Enter the OAuth Client Secret: " CLIENT_SECRET
echo ""

# Configure firewall rules for Cloud Run
echo "🔥 Configuring firewall rules..."
gcloud compute firewall-rules create allow-iap-ingress \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:80,tcp:443 \
    --source-ranges=35.235.240.0/20 \
    --target-tags=allow-iap \
    2>/dev/null || echo "  Firewall rule already exists, skipping..."

# Create secrets in Secret Manager
echo "🔐 Creating secrets in Secret Manager..."
echo -n "$CLIENT_ID" | gcloud secrets create iap-client-id --data-file=- 2>/dev/null || \
    echo -n "$CLIENT_ID" | gcloud secrets versions add iap-client-id --data-file=-

echo -n "$CLIENT_SECRET" | gcloud secrets create iap-client-secret --data-file=- 2>/dev/null || \
    echo -n "$CLIENT_SECRET" | gcloud secrets versions add iap-client-secret --data-file=-

# Grant GitHub Actions access to secrets
echo "📝 Granting access to secrets..."
gcloud secrets add-iam-policy-binding iap-client-id \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding iap-client-secret \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor"

# Get billing account - check environment variable first
if [ -n "$GCP_BILLING_ACCOUNT_ID" ]; then
    BILLING_ACCOUNT=$GCP_BILLING_ACCOUNT_ID
    echo "Using GCP_BILLING_ACCOUNT_ID from environment: $BILLING_ACCOUNT"
else
    BILLING_ACCOUNT=$(gcloud billing accounts list --format="value(ACCOUNT_ID)" --limit=1)
    if [ -z "$BILLING_ACCOUNT" ]; then
        echo "⚠️  No billing account found. Please set up billing in GCP Console."
        read -p "Enter your billing account ID (format: XXXXXX-XXXXXX-XXXXXX): " BILLING_ACCOUNT
    fi
fi

# Output summary
echo ""
echo "✅ Infrastructure setup complete!"
echo ""
echo "GitHub Secrets to add:"
echo "====================="
echo "1. GCP_PROJECT_ID: $PROJECT_ID"
echo "2. GCP_REGION: $REGION"
echo "3. GCP_BILLING_ACCOUNT_ID: $BILLING_ACCOUNT"
echo "4. GCP_SA_KEY: (contents of $KEY_FILE)"
echo "5. IAP_CLIENT_ID: $CLIENT_ID"
echo "6. IAP_CLIENT_SECRET: $CLIENT_SECRET"
echo "7. AUTHORIZED_DOMAIN: $DOMAIN"
echo "8. GEMINI_API_KEY: (your Gemini API key)"
echo ""
echo "Next steps:"
echo "==========="
echo "1. Add the above secrets to your GitHub repository:"
echo "   https://github.com/$GITHUB_REPOSITORY/settings/secrets/actions"
echo "2. Delete the local service account key file:"
echo "   rm $KEY_FILE"
echo "3. Create a git tag to trigger deployment:"
echo "   git tag v1.0.0 && git push origin v1.0.0"
echo ""
echo "Cloud Run Services will be created at:"
echo "  Frontend: https://re-frame-frontend-[HASH]-$REGION.run.app"
echo "  Backend: https://re-frame-backend-[HASH]-$REGION.run.app"
echo ""
echo "IAP will protect access to the frontend service."