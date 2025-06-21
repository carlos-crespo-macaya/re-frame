# re-frame Terraform Infrastructure

This directory contains the Terraform configuration for deploying the re-frame.social infrastructure on Google Cloud Platform.

## Architecture Overview

The infrastructure includes:
- **Cloud Run**: Containerized backend API (scales to zero)
- **Firestore**: NoSQL database for sessions and reframes
- **Firebase**: Authentication and static hosting
- **Cloud Armor**: DDoS protection and rate limiting

## Cost Optimization Features

This configuration is optimized to stay within the $300 GCP credit budget:

1. **Cloud Run**: Scales to zero when not in use
2. **Minimal Resources**: 1 CPU, 512Mi memory per instance
3. **Rate Limiting**: 10 requests/hour per user
4. **Max Instances**: Limited to 1-2 instances
5. **No Vertex AI**: Uses Google AI Studio API keys instead

Estimated monthly cost: < $15/month with minimal usage

## Prerequisites

1. [Terraform](https://www.terraform.io/downloads.html) >= 1.0
2. [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. A GCP project with billing enabled
4. A Google AI Studio API key

## Initial Setup

1. Clone the repository and navigate to the terraform directory:
   ```bash
   cd infrastructure/terraform
   ```

2. Create a GCP project:
   ```bash
   gcloud projects create YOUR-PROJECT-ID
   gcloud config set project YOUR-PROJECT-ID
   ```

3. Enable billing for your project in the [GCP Console](https://console.cloud.google.com/billing)

4. Create a service account for Terraform:
   ```bash
   gcloud iam service-accounts create terraform \
     --display-name="Terraform Service Account"
   
   gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
     --member="serviceAccount:terraform@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
     --role="roles/owner"
   
   gcloud iam service-accounts keys create ~/terraform-key.json \
     --iam-account=terraform@YOUR-PROJECT-ID.iam.gserviceaccount.com
   ```

5. Set up authentication:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=~/terraform-key.json
   ```

6. Get a Google AI Studio API key:
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Create a new API key
   - Save it securely

## Configuration

1. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. Edit `terraform.tfvars` with your values:
   ```hcl
   project_id = "your-gcp-project-id"
   region     = "us-central1"
   
   # Update with your project-specific values
   backend_image_url = "gcr.io/your-project-id/re-frame-backend:latest"
   firebase_hosting_site_id = "your-firebase-site-id"
   ```

3. Set sensitive variables as environment variables:
   ```bash
   export TF_VAR_gemini_api_key="your-google-ai-studio-api-key"
   ```

## Deployment

### First Time Setup

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Review the planned changes:
   ```bash
   terraform plan -var-file=environments/alpha.tfvars
   ```

3. Apply the configuration:
   ```bash
   terraform apply -var-file=environments/alpha.tfvars
   ```

4. Note the outputs:
   - `cloud_run_url`: Your backend API endpoint
   - `firebase_hosting_url`: Your frontend URL

### Updating Infrastructure

1. Make your changes to the `.tf` files
2. Review changes:
   ```bash
   terraform plan -var-file=environments/alpha.tfvars
   ```
3. Apply changes:
   ```bash
   terraform apply -var-file=environments/alpha.tfvars
   ```

### Destroying Infrastructure

To completely remove all resources (careful!):
```bash
terraform destroy -var-file=environments/alpha.tfvars
```

## Module Structure

```
modules/
├── cloud-run/      # Cloud Run service configuration
├── firestore/      # Firestore database and security rules
├── firebase/       # Firebase Auth and Hosting
└── cloud-armor/    # Security policies and rate limiting
```

## Environment Management

Different environments can be managed using separate `.tfvars` files:

- `environments/alpha.tfvars` - Alpha/testing environment
- `environments/beta.tfvars` - Beta environment (future)
- `environments/prod.tfvars` - Production environment (future)

## Security Considerations

1. **Secrets**: Never commit API keys or sensitive data
2. **State**: Consider using remote state backend for team collaboration
3. **IAM**: Use least privilege principles for service accounts
4. **Cloud Armor**: Configured with rate limiting and attack pattern blocking

## Troubleshooting

### Common Issues

1. **API not enabled error**:
   ```bash
   gcloud services enable compute.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable firebase.googleapis.com
   ```

2. **Insufficient permissions**:
   - Ensure your service account has the necessary roles
   - Check that billing is enabled

3. **Resource already exists**:
   - Import existing resources or use different names
   - Check for resources created outside Terraform

### Getting Help

- Check Terraform logs: `TF_LOG=DEBUG terraform apply`
- Review GCP Console for detailed error messages
- Consult the [Terraform GCP Provider docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

## Next Steps

After infrastructure is deployed:

1. Build and push the backend Docker image
2. Deploy the frontend to Firebase Hosting
3. Configure monitoring and alerts
4. Set up CI/CD pipelines

## Cost Monitoring

Monitor your GCP spending:
```bash
gcloud beta billing budgets list
gcloud compute project-info describe --project=YOUR-PROJECT-ID
```

Set up budget alerts in the GCP Console to avoid unexpected charges.