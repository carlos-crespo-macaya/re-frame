# Workload Identity Federation Setup Guide

This guide explains how to set up Workload Identity Federation (WIF) for GitHub Actions to deploy to Google Cloud Run without using service account keys.

## Overview

Workload Identity Federation allows GitHub Actions to authenticate with Google Cloud using OpenID Connect (OIDC) tokens, eliminating the need for long-lived service account keys.

## Prerequisites

- GCP Project with billing enabled
- `gcloud` CLI installed and authenticated
- GitHub repository with admin access

## Setup Instructions

### 1. Run the Setup Script

We provide an automated script that sets up WIF:

```bash
export GCP_PROJECT_ID="your-project-id"
./scripts/setup-workload-identity.sh
```

The script will prompt for:
- Your GitHub username/organization
- Your repository name

### 2. Manual Setup (Alternative)

If the automated script fails, you can set up WIF manually:

```bash
# Set variables
PROJECT_ID="your-project-id"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
POOL_NAME="github-actions-pool"
PROVIDER_NAME="github-actions-provider"
GITHUB_ORG="your-github-org"
GITHUB_REPO="your-repo-name"

# Enable APIs
gcloud services enable iamcredentials.googleapis.com

# Create pool
gcloud iam workload-identity-pools create $POOL_NAME \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --description="Pool for GitHub Actions authentication"

# Create provider with attribute condition (REQUIRED)
# Note: The attribute-condition is necessary to avoid the error:
# "The attribute condition must reference one of the provider's claims"
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
  --location="global" \
  --workload-identity-pool=$POOL_NAME \
  --display-name="GitHub Actions Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,\
attribute.actor=assertion.actor,\
attribute.repository=assertion.repository,\
attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner == '$GITHUB_ORG'"

# Configure service account permissions
gcloud iam service-accounts add-iam-policy-binding \
  "github-actions-deploy@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleREDACTED/$POOL_NAME/attribute.repository/$GITHUB_ORG/$GITHUB_REPO"
```

### 3. Configure GitHub Secrets

Add these secrets to your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:

| Secret Name | Value |
|------------|-------|
| `GCP_WIF_PROVIDER` | `projects/{PROJECT_NUMBER}/locations/global/workloadIdentityPools/{POOL_NAME}/providers/{PROVIDER_NAME}` |
| `GCP_WIF_SERVICE_ACCOUNT` | `github-actions-deploy@{PROJECT_ID}.iam.gserviceaccount.com` |
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_REGION` | Your preferred region (e.g., `us-central1`) |
| `GCP_BILLING_ACCOUNT_ID` | Your billing account ID |
| `GEMINI_API_KEY` | Your Gemini API key for the backend |

### 4. Workflow Configuration

Your GitHub Actions workflow should use the following authentication step:

```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.GCP_WIF_PROVIDER }}
    service_account: ${{ secrets.GCP_WIF_SERVICE_ACCOUNT }}
```

## Troubleshooting

### Error: "The attribute condition must reference one of the provider's claims"

This error occurs when creating a WIF provider without an attribute condition. The solution is to include the `--attribute-condition` parameter when creating the provider:

```bash
--attribute-condition="assertion.repository_owner == 'your-github-org'"
```

This condition ensures that only workflows from your GitHub organization can use this provider.

### Error: "failed to generate Google Cloud federated token"

This usually means:
1. The WIF provider doesn't exist
2. The GitHub secrets are incorrect
3. The service account doesn't have the correct IAM binding

To fix:
1. Verify the provider exists:
   ```bash
   gcloud iam workload-identity-pools providers list \
     --location=global \
     --workload-identity-pool=github-actions-pool
   ```

2. Check the exact provider name:
   ```bash
   gcloud iam workload-identity-pools providers describe github-actions-provider \
     --location=global \
     --workload-identity-pool=github-actions-pool \
     --format="value(name)"
   ```

3. Verify the service account IAM policy:
   ```bash
   gcloud iam service-accounts get-iam-policy \
     github-actions-deploy@your-project-id.iam.gserviceaccount.com
   ```

## Security Considerations

1. **Attribute Conditions**: The `repository_owner` condition ensures only your repositories can authenticate
2. **Least Privilege**: Grant only necessary permissions to the service account
3. **No Keys**: This approach eliminates the risk of leaked service account keys
4. **Audit Logging**: All authentications are logged in Cloud Audit Logs

## Additional Resources

- [Google Cloud WIF Documentation](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [google-github-actions/auth](https://github.com/google-github-actions/auth)