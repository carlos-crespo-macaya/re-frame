# Billing Setup Fix for re-frame Infrastructure

## The Problem

The current Terraform configuration fails to create billing budgets automatically because:
1. The service account needs `billing.budgets.create` permission at the billing account level
2. The Google provider needs explicit billing account configuration
3. The data source lookup for billing account may fail without proper permissions

## Required Permissions

The Terraform service account needs these roles:
- `roles/billing.admin` on the billing account (NOT just the project)
- `roles/billing.budgets.editor` on the billing account
- `roles/monitoring.notificationChannelEditor` on the project

## Manual Fix Steps

1. **Find your billing account ID**:
```bash
gcloud billing accounts list
# Note the ACCOUNT_ID (looks like 01A23B-4C5D6E-7F8G9H)
```

2. **Grant billing permissions to Terraform service account**:
```bash
# Replace with your actual values
BILLING_ACCOUNT_ID="01A23B-4C5D6E-7F8G9H"
SERVICE_ACCOUNT="terraform-sa@gen-lang-client-0135194996.iam.gserviceaccount.com"

# Grant billing admin role
gcloud billing accounts add-iam-policy-binding $BILLING_ACCOUNT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/billing.admin"

# Grant budget editor role
gcloud billing accounts add-iam-policy-binding $BILLING_ACCOUNT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/billing.budgets.editor"
```

3. **Enable required APIs**:
```bash
gcloud services enable billingbudgets.googleapis.com
gcloud services enable cloudbilling.googleapis.com
gcloud services enable monitoring.googleapis.com
```

## Terraform Configuration Fix

Instead of using a data source, directly specify the billing account ID:

```hcl
# In terraform.tfvars
billing_account_id = "01A23B-4C5D6E-7F8G9H"  # Your actual billing account ID
```

Then update billing.tf to use the ID directly instead of data source lookup.

## Alternative: Use gcloud CLI

If Terraform permissions remain an issue, create the budget using gcloud:

```bash
# Create budget
gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT_ID \
  --display-name="gen-lang-client-budget" \
  --budget-amount=300 \
  --threshold-rule=percent=0.03 \
  --threshold-rule=percent=0.17 \
  --threshold-rule=percent=0.33 \
  --threshold-rule=percent=0.50 \
  --threshold-rule=percent=0.67 \
  --threshold-rule=percent=0.83 \
  --threshold-rule=percent=0.90 \
  --threshold-rule=percent=1.0 \
  --filter-projects=projects/gen-lang-client-0135194996 \
  --credit-types-treatment=INCLUDE_ALL_CREDITS \
  --all-updates-rule-pubsub-topic=projects/gen-lang-client-0135194996/topics/budget-alerts
```

## Testing the Fix

After applying permissions and configuration:

1. Run Terraform plan to verify budget resource will be created:
```bash
terraform plan -target=google_billing_budget.project_budget
```

2. Apply just the budget configuration:
```bash
terraform apply -target=google_billing_budget.project_budget
```

3. Verify in GCP Console:
   - Go to Billing > Budgets & alerts
   - Confirm budget exists with all thresholds

## Evidence of Working Setup

Provide screenshots or command outputs showing:
- Budget created in GCP Console
- Alert thresholds configured
- Notification channels set up
- Test alert received (trigger manually if needed)