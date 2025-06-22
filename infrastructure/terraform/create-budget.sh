#!/bin/bash
# Script to create budget alerts for re-frame project

set -e

# Variables
BILLING_ACCOUNT="01FB26-BC3BF1-C9A591"
PROJECT_ID="gen-lang-client-0135194996"
BUDGET_NAME="${PROJECT_ID}-budget"
BUDGET_AMOUNT="300"
EMAIL="macayaven@gmail.com"

echo "Creating budget for project: $PROJECT_ID"
echo "Budget amount: \$$BUDGET_AMOUNT USD"
echo "Alert email: $EMAIL"
echo ""

# First, check if budget already exists
EXISTING_BUDGETS=$(gcloud billing budgets list \
  --billing-account=$BILLING_ACCOUNT \
  --filter="displayName=$BUDGET_NAME" \
  --format="value(name)" 2>/dev/null || echo "")

if [ -n "$EXISTING_BUDGETS" ]; then
  echo "Budget already exists: $BUDGET_NAME"
  echo "Budget ID: $EXISTING_BUDGETS"
  exit 0
fi

# Create the budget using gcloud with proper JSON format
echo "Creating new budget with alerts..."

# Create a temporary JSON file for the budget configuration
cat > /tmp/budget-config.json << EOF
{
  "displayName": "$BUDGET_NAME",
  "budgetFilter": {
    "projects": ["projects/$PROJECT_ID"],
    "creditTypesTreatment": "INCLUDE_ALL_CREDITS"
  },
  "amount": {
    "specifiedAmount": {
      "currencyCode": "USD",
      "units": "$BUDGET_AMOUNT"
    }
  },
  "thresholdRules": [
    {"thresholdPercent": 0.03, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 0.17, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 0.33, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 0.50, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 0.67, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 0.83, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 0.90, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 1.00, "spendBasis": "CURRENT_SPEND"},
    {"thresholdPercent": 1.20, "spendBasis": "FORECASTED_SPEND"}
  ],
  "notificationsRule": {
    "pubsubTopic": "",
    "schemaVersion": "1.0",
    "monitoringNotificationChannels": []
  }
}
EOF

# Create the budget
BUDGET_ID=$(gcloud billing budgets create \
  --billing-account=$BILLING_ACCOUNT \
  --data-file=/tmp/budget-config.json \
  --format="value(name)" 2>&1 || echo "FAILED")

# Clean up temp file
rm -f /tmp/budget-config.json

if [ "$BUDGET_ID" = "FAILED" ]; then
  echo ""
  echo "❌ Failed to create budget automatically."
  echo ""
  echo "Please create the budget manually:"
  echo "1. Go to: https://console.cloud.google.com/billing/budgets?project=$PROJECT_ID"
  echo "2. Click 'Create Budget'"
  echo "3. Configure with these settings:"
  echo "   - Name: $BUDGET_NAME"
  echo "   - Projects: $PROJECT_ID"
  echo "   - Amount: \$$BUDGET_AMOUNT"
  echo "   - Alert thresholds: 3%, 17%, 33%, 50%, 67%, 83%, 90%, 100%, 120% (forecast)"
  echo "   - Email: $EMAIL"
  exit 1
fi

echo ""
echo "✅ Budget created successfully!"
echo "Budget ID: $BUDGET_ID"
echo ""
echo "Alert thresholds configured:"
echo "- \$10 (3%) - First alert"
echo "- \$50 (17%)"
echo "- \$100 (33%)"
echo "- \$150 (50%)"
echo "- \$200 (67%)"
echo "- \$250 (83%) - Critical"
echo "- \$270 (90%) - Emergency"
echo "- \$300 (100%) - Budget exhausted"
echo "- 120% forecast warning"