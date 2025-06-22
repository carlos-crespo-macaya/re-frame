# Infrastructure Setup Instructions

## Overview

This Terraform configuration sets up the GCP infrastructure for re-frame.social with a strong focus on cost control through billing alerts.

## Prerequisites

1. **GCP Account Setup**
   - Active GCP account with billing enabled
   - $300 free credits (or billing account with payment method)
   - Project created or permission to create projects

2. **Required Tools**
   - `gcloud` CLI installed and authenticated
   - `terraform` >= 1.0
   - `jq` (for JSON processing in scripts)

3. **Required Permissions**
   - Project Owner or Editor role
   - Billing Account Administrator (for budget creation)

## Step-by-Step Setup

### 1. Get Your Billing Account ID

```bash
# List your billing accounts
gcloud billing accounts list

# Output example:
# ACCOUNT_ID            NAME                OPEN  MASTER_ACCOUNT_ID
# 01A23B-4C5D6E-7F8G9H  My Billing Account  True
```

Note your `ACCOUNT_ID` - you'll need it for Terraform.

### 2. Create or Select GCP Project

```bash
# Create new project (if needed)
gcloud projects create YOUR-PROJECT-ID --name="re-frame Social"

# Set as active project
gcloud config set project YOUR-PROJECT-ID

# Link billing account
gcloud billing projects link YOUR-PROJECT-ID \
  --billing-account=01A23B-4C5D6E-7F8G9H
```

### 3. Enable Required APIs

```bash
# Enable all required APIs
gcloud services enable \
  billingbudgets.googleapis.com \
  cloudbilling.googleapis.com \
  monitoring.googleapis.com \
  compute.googleapis.com \
  run.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com \
  firebaserules.googleapis.com \
  firebasehosting.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 4. Create Terraform Service Account

```bash
# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account" \
  --project=YOUR-PROJECT-ID

# Grant project permissions
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
  --member="serviceAccount:terraform-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/owner"

# CRITICAL: Grant billing permissions
gcloud billing accounts add-iam-policy-binding 01A23B-4C5D6E-7F8G9H \
  --member="serviceAccount:terraform-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/billing.budgets.editor"

# Create key file
gcloud iam service-accounts keys create ~/terraform-sa-key.json \
  --iam-account=terraform-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/terraform-sa-key.json
```

### 5. Create Terraform State Bucket

```bash
# Create bucket for Terraform state
gsutil mb -p YOUR-PROJECT-ID gs://YOUR-PROJECT-ID-terraform-state/

# Enable versioning
gsutil versioning set on gs://YOUR-PROJECT-ID-terraform-state/

# Update backend.tf with your bucket name
```

### 6. Configure Terraform Variables

Create `terraform.tfvars`:

```hcl
# Project Configuration
project_id = "YOUR-PROJECT-ID"
region     = "us-central1"

# Billing Configuration (REQUIRED)
billing_account_id = "01A23B-4C5D6E-7F8G9H"  # From step 1
budget_amount      = "300"
budget_alert_email = "your-email@example.com"

# Cloud Run Configuration
cloud_run_service_name  = "re-frame-backend"
backend_image_url      = "gcr.io/YOUR-PROJECT-ID/re-frame-backend:latest"
cloud_run_max_instances = 2
cloud_run_cpu          = "1"
cloud_run_memory       = "512Mi"

# Firebase Configuration
firebase_hosting_site_id = "YOUR-PROJECT-ID"
auth_domain             = "YOUR-PROJECT-ID.firebaseapp.com"

# Set API key as environment variable
# export TF_VAR_gemini_api_key="your-api-key"
```

### 7. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan deployment (review carefully)
terraform plan

# Apply ONLY billing configuration first
terraform apply -target=google_billing_budget.project_budget \
                -target=google_monitoring_notification_channel.email \
                -target=google_monitoring_alert_policy.daily_spend_alert

# Verify budget was created
gcloud billing budgets list --billing-account=01A23B-4C5D6E-7F8G9H

# Apply remaining infrastructure
terraform apply
```

### 8. Verify Billing Alerts

1. **Check in GCP Console**:
   - Go to [Billing > Budgets & alerts](https://console.cloud.google.com/billing)
   - Verify budget exists with correct thresholds

2. **Run Test Script**:
   ```bash
   ./test-deployment.sh
   ```

3. **Test Alert (Optional)**:
   - Temporarily lower a threshold to $1
   - Deploy a small resource
   - Verify email alert is received

## Troubleshooting

### Budget Creation Fails

**Error**: "Error creating Budget: googleapi: Error 403"

**Solution**: Grant billing permissions to service account:
```bash
gcloud billing accounts add-iam-policy-binding YOUR-BILLING-ACCOUNT \
  --member="serviceAccount:terraform-sa@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
  --role="roles/billing.budgets.editor"
```

### Terraform State Lock

**Error**: "Error acquiring the state lock"

**Solution**: Someone else is running Terraform. Wait or break lock:
```bash
terraform force-unlock LOCK_ID
```

### API Not Enabled

**Error**: "API [service.googleapis.com] not enabled"

**Solution**: Enable the mentioned API:
```bash
gcloud services enable SERVICE_NAME.googleapis.com
```

## Cost Control Measures

This infrastructure implements aggressive cost controls:

1. **Budget Alerts**: 
   - First alert at $10 (3.3% of budget)
   - Critical alert at $250 (83% of budget)
   - Daily spend monitoring (alert if >$10/day)

2. **Resource Limits**:
   - Cloud Run: Scale to zero, max 2 instances
   - Minimal CPU/memory allocations
   - Rate limiting on API calls

3. **Monitoring**:
   - Daily cost emails
   - Forecasted spend alerts
   - Real-time budget tracking

## Next Steps

After successful deployment:

1. Deploy backend application to Cloud Run
2. Configure Firebase Authentication
3. Deploy frontend to Firebase Hosting
4. Set up CI/CD pipelines
5. Configure domain and SSL

## Emergency Procedures

If costs spike unexpectedly:

1. **Immediate Actions**:
   ```bash
   # Scale down Cloud Run to zero
   gcloud run services update re-frame-backend --max-instances=0
   
   # Disable expensive APIs
   gcloud services disable run.googleapis.com
   ```

2. **Investigation**:
   - Check GCP Console > Billing > Reports
   - Review Cloud Run metrics
   - Check for unusual API usage

3. **Contact**:
   - Email the budget alert address immediately
   - Review logs for potential abuse