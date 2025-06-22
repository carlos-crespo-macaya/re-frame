# GCP Project Setup Checklist for re-frame.social

## Prerequisites
- [ ] GCP account with billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Terraform >= 1.0 installed
- [ ] GitHub repository access

## 1. Create GCP Project
```bash
# Create new project
gcloud projects create re-frame-social-alpha \
  --name="re-frame Social Alpha" \
  --organization=[YOUR_ORG_ID]  # Optional

# Set as default project
gcloud config set project re-frame-social-alpha
```

## 2. Enable Billing & Set Budget Alerts
### Enable Billing Account
```bash
# List billing accounts
gcloud billing accounts list

# Link billing account to project
gcloud billing projects link re-frame-social-alpha \
  --billing-account=[BILLING_ACCOUNT_ID]
```

### Create Budget with $10 Alert Threshold
```bash
# Enable Billing Budget API
gcloud services enable billingbudgets.googleapis.com

# Budget will be created via Terraform (see billing.tf)
```

## 3. Enable Required APIs
The following APIs will be enabled via Terraform:
- Cloud Run API (run.googleapis.com)
- Firestore API (firestore.googleapis.com)
- Firebase API (firebase.googleapis.com)
- Firebase Rules API (firebaserules.googleapis.com)
- Firebase Hosting API (firebasehosting.googleapis.com)
- Cloud Build API (cloudbuild.googleapis.com)
- Container Registry API (containerregistry.googleapis.com)
- Compute Engine API (compute.googleapis.com)
- Cloud Armor API (cloudarmor.googleapis.com)

## 4. Set Up Service Account for Terraform
```bash
# Create service account
gcloud iam service-accounts create terraform-sa \
  --display-name="Terraform Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding re-frame-social-alpha \
  --member="serviceAccount:terraform-sa@re-frame-social-alpha.iam.gserviceaccount.com" \
  --role="roles/owner"

# Create and download key
gcloud iam service-accounts keys create ~/terraform-key.json \
  --iam-account=terraform-sa@re-frame-social-alpha.iam.gserviceaccount.com
```

## 5. Configure Terraform Backend
```bash
# Create GCS bucket for Terraform state
gsutil mb -p re-frame-social-alpha gs://re-frame-social-terraform-state/

# Enable versioning
gsutil versioning set on gs://re-frame-social-terraform-state/
```

## 6. Set Up Required Secrets
```bash
# Create Google AI Studio API key
# Visit: https://makersuite.google.com/app/apikey

# Store in Secret Manager (optional but recommended)
gcloud services enable secretmanager.googleapis.com
echo -n "YOUR_GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
```

## 7. Initialize Firebase Project
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login and init
firebase login
firebase projects:addfirebase re-frame-social-alpha
```

## 8. Prepare Terraform Variables
Create `terraform.tfvars`:
```hcl
project_id               = "re-frame-social-alpha"
region                   = "us-central1"
environment              = "alpha"
cloud_run_service_name   = "re-frame-backend"
firebase_hosting_site_id = "re-frame-social-alpha"
auth_domain              = "re-frame-social-alpha.firebaseapp.com"
gemini_api_key           = "YOUR_GEMINI_API_KEY"  # Or use env var
```

## 9. Cost Control Measures
- [ ] Cloud Run: min_instances = 0 (scale to zero)
- [ ] Cloud Run: max_instances = 2
- [ ] Cloud Run: CPU = 1, Memory = 512Mi (minimum)
- [ ] Rate limiting: 10 requests/hour per user
- [ ] Billing alerts at $10, $50, $100, $250
- [ ] Daily cost monitoring

## 10. Verification Checklist
- [ ] Project created and billing enabled
- [ ] Budget alerts configured
- [ ] All required APIs enabled
- [ ] Service account created with proper permissions
- [ ] Terraform state bucket created
- [ ] Firebase project initialized
- [ ] terraform.tfvars configured
- [ ] Cost controls in place

## Important Notes
- **Budget**: Total budget is $300 GCP credits
- **Priority**: Set up billing alerts FIRST before any other resources
- **Monitoring**: Check daily costs via GCP Console
- **Emergency**: If costs exceed $10/day, immediately scale down or disable services