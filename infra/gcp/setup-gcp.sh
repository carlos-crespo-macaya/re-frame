#!/bin/bash

# Google Cloud Setup Script for re-frame Cloud Run Deployment
# This script sets up all necessary GCP resources for deploying the frontend to Cloud Run

set -e

# Configuration
PROJECT_ID="macayaven"
SERVICE_ACCOUNT_NAME="github-actions-deploy"
REGION="us-central1"
ARTIFACT_REPO_NAME="re-frame"

echo "🚀 Setting up Google Cloud resources for re-frame deployment"
echo "Project: $PROJECT_ID"
echo ""

# Set the project
echo "Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com \
  containerregistry.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  --project=$PROJECT_ID

# Create service account
echo ""
echo "Creating service account..."
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com --project=$PROJECT_ID >/dev/null 2>&1; then
  echo "Service account already exists"
else
  gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="GitHub Actions Deploy" \
    --description="Service account for deploying from GitHub Actions to Cloud Run" \
    --project=$PROJECT_ID

  # Wait for service account to be fully created
  echo "Waiting for service account to be ready..."
  sleep 5
fi

# Grant necessary roles
echo ""
echo "Granting IAM roles..."
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

roles=(
  "roles/run.developer"
  "roles/iam.serviceAccountUser"
  "roles/storage.admin"
  "roles/artifactregistry.writer"
)

for role in "${roles[@]}"; do
  echo "Granting $role..."
  gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="$role" \
    --quiet
done

# Create Artifact Registry repository
echo ""
echo "Creating Artifact Registry repository..."
if gcloud artifacts repositories describe $ARTIFACT_REPO_NAME --location=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
  echo "Artifact Registry repository already exists"
else
  gcloud artifacts repositories create $ARTIFACT_REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Re-frame Docker images" \
    --project=$PROJECT_ID
fi

# Configure Docker for Artifact Registry
echo ""
echo "Configuring Docker authentication..."
gcloud auth configure-docker $REGION-docker.pkg.dev

# Create service account key
echo ""
echo "Creating service account key..."
KEY_FILE="github-actions-sa-key.json"
gcloud iam service-accounts keys create $KEY_FILE \
  --iam-account=$SERVICE_ACCOUNT_EMAIL \
  --project=$PROJECT_ID

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy the contents of $KEY_FILE to your GitHub repository secrets as GCP_SA_KEY"
echo "2. Add the following secrets to GitHub:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_SA_KEY: (contents of $KEY_FILE)"
echo "   - NEXT_PUBLIC_API_URL: (your backend API URL)"
echo ""
echo "3. The service account key is saved in: $KEY_FILE"
echo "   ⚠️  Keep this file secure and do not commit it to version control!"
echo ""
echo "4. To deploy manually, run:"
echo "   gcloud run deploy re-frame-frontend --source . --region $REGION --allow-unauthenticated"
echo ""
echo "5. Don't forget to delete the key file after adding it to GitHub secrets:"
echo "   rm $KEY_FILE"
