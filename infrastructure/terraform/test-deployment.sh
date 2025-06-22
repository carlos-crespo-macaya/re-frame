#!/bin/bash
# Test script to verify billing alerts are properly configured

set -e

echo "=== Billing Alerts Deployment Test ==="
echo "This script will verify that billing alerts are properly configured"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "1. Checking prerequisites..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗ gcloud CLI not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ gcloud CLI found${NC}"

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}✗ terraform not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ terraform found${NC}"

# Get current project
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}✗ No GCP project set${NC}"
    echo "Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi
echo -e "${GREEN}✓ Using project: $PROJECT_ID${NC}"

# Check if billing is enabled
echo ""
echo "2. Checking billing status..."
BILLING_ENABLED=$(gcloud billing projects describe $PROJECT_ID --format="value(billingEnabled)" 2>/dev/null || echo "false")
if [ "$BILLING_ENABLED" != "True" ]; then
    echo -e "${RED}✗ Billing not enabled for project${NC}"
    echo "Run: gcloud billing projects link $PROJECT_ID --billing-account=YOUR_BILLING_ACCOUNT_ID"
    exit 1
fi
echo -e "${GREEN}✓ Billing is enabled${NC}"

# Get billing account ID
BILLING_ACCOUNT=$(gcloud billing projects describe $PROJECT_ID --format="value(billingAccountName)" | cut -d'/' -f2)
echo -e "${GREEN}✓ Billing account: $BILLING_ACCOUNT${NC}"

# Check if required APIs are enabled
echo ""
echo "3. Checking required APIs..."
REQUIRED_APIS=(
    "billingbudgets.googleapis.com"
    "cloudbilling.googleapis.com"
    "monitoring.googleapis.com"
)

for api in "${REQUIRED_APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo -e "${GREEN}✓ $api enabled${NC}"
    else
        echo -e "${YELLOW}! $api not enabled, enabling now...${NC}"
        gcloud services enable $api
    fi
done

# Check Terraform service account permissions
echo ""
echo "4. Checking service account permissions..."
SERVICE_ACCOUNT=$(terraform output -raw terraform_service_account 2>/dev/null || echo "")
if [ -z "$SERVICE_ACCOUNT" ]; then
    echo -e "${YELLOW}! No terraform service account found in outputs${NC}"
    echo "Using default credentials"
else
    echo "Service account: $SERVICE_ACCOUNT"
    
    # Check billing permissions
    echo "Checking billing permissions..."
    if gcloud billing accounts get-iam-policy $BILLING_ACCOUNT --flatten="bindings[].members" --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT" --format="value(bindings.role)" | grep -q "billing.admin\|billing.budgets.editor"; then
        echo -e "${GREEN}✓ Service account has billing permissions${NC}"
    else
        echo -e "${RED}✗ Service account lacks billing permissions${NC}"
        echo "Grant permissions with:"
        echo "  gcloud billing accounts add-iam-policy-binding $BILLING_ACCOUNT \\"
        echo "    --member=\"serviceAccount:$SERVICE_ACCOUNT\" \\"
        echo "    --role=\"roles/billing.budgets.editor\""
    fi
fi

# Test Terraform configuration
echo ""
echo "5. Testing Terraform configuration..."
echo "Running terraform plan for billing resources..."

# Create a test plan
terraform plan -target=google_billing_budget.project_budget \
               -target=google_monitoring_notification_channel.email \
               -target=google_monitoring_alert_policy.daily_spend_alert \
               -out=billing-test.plan

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Terraform plan succeeded${NC}"
    
    echo ""
    echo "6. Would you like to apply the billing configuration? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Applying billing configuration..."
        terraform apply billing-test.plan
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Billing configuration applied successfully${NC}"
            
            # Verify the budget was created
            echo ""
            echo "7. Verifying budget creation..."
            BUDGET_NAME="${PROJECT_ID}-budget"
            
            if gcloud billing budgets list --billing-account=$BILLING_ACCOUNT --filter="displayName:$BUDGET_NAME" --format="value(name)" | grep -q "."; then
                echo -e "${GREEN}✓ Budget '$BUDGET_NAME' found${NC}"
                
                # Show budget details
                echo ""
                echo "Budget details:"
                gcloud billing budgets describe $(gcloud billing budgets list --billing-account=$BILLING_ACCOUNT --filter="displayName:$BUDGET_NAME" --format="value(name)" | head -1) --billing-account=$BILLING_ACCOUNT
                
                # Generate evidence
                echo ""
                echo "8. Generating evidence for PR..."
                EVIDENCE_FILE="billing-setup-evidence-$(date +%Y%m%d-%H%M%S).txt"
                
                {
                    echo "=== Billing Setup Evidence ==="
                    echo "Generated: $(date)"
                    echo "Project: $PROJECT_ID"
                    echo "Billing Account: $BILLING_ACCOUNT"
                    echo ""
                    echo "=== Budget Configuration ==="
                    gcloud billing budgets describe $(gcloud billing budgets list --billing-account=$BILLING_ACCOUNT --filter="displayName:$BUDGET_NAME" --format="value(name)" | head -1) --billing-account=$BILLING_ACCOUNT
                    echo ""
                    echo "=== Alert Policies ==="
                    gcloud monitoring policies list --filter="displayName:$PROJECT_ID-daily-spend-alert" --format="table(displayName,enabled)"
                    echo ""
                    echo "=== Terraform Outputs ==="
                    terraform output -json
                } > "$EVIDENCE_FILE"
                
                echo -e "${GREEN}✓ Evidence saved to: $EVIDENCE_FILE${NC}"
                echo ""
                echo "Next steps:"
                echo "1. Review the evidence file"
                echo "2. Take a screenshot of the GCP Console Budgets page"
                echo "3. Add both to the PR as proof of working setup"
            else
                echo -e "${RED}✗ Budget not found in GCP${NC}"
                echo "Check the GCP Console: https://console.cloud.google.com/billing/$BILLING_ACCOUNT/budgets"
            fi
        else
            echo -e "${RED}✗ Terraform apply failed${NC}"
        fi
    else
        echo "Skipping apply. Run 'terraform apply billing-test.plan' when ready."
    fi
else
    echo -e "${RED}✗ Terraform plan failed${NC}"
    echo "Fix the errors above and try again."
fi

# Cleanup
rm -f billing-test.plan

echo ""
echo "=== Test Complete ==="