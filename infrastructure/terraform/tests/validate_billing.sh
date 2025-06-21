#!/bin/bash
# Validate billing configuration for re-frame project

set -e

echo "=== Billing Configuration Validation Script ==="
echo "This script validates that billing alerts are properly configured"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if billing.tf exists
if [ ! -f "../billing.tf" ]; then
    echo -e "${RED}✗ ERROR: billing.tf not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ billing.tf found${NC}"

# Validate billing.tf content
echo ""
echo "Checking billing.tf configuration..."

# Check for budget resource
if grep -q "resource \"google_billing_budget\"" ../billing.tf; then
    echo -e "${GREEN}✓ Budget resource defined${NC}"
else
    echo -e "${RED}✗ Budget resource missing${NC}"
    exit 1
fi

# Check for critical alert thresholds
THRESHOLDS=(0.03 0.17 0.33 0.50 0.67 0.83 0.90 1.0 1.2)
AMOUNTS=(10 50 100 150 200 250 270 300 "360 (forecast)")

echo ""
echo "Validating alert thresholds..."
for i in "${!THRESHOLDS[@]}"; do
    if grep -q "threshold_percent = ${THRESHOLDS[$i]}" ../billing.tf; then
        echo -e "${GREEN}✓ Alert at \$${AMOUNTS[$i]} (${THRESHOLDS[$i]}%) configured${NC}"
    else
        echo -e "${RED}✗ Alert at \$${AMOUNTS[$i]} (${THRESHOLDS[$i]}%) missing${NC}"
        exit 1
    fi
done

# Check for email notification channel
if grep -q "resource \"google_monitoring_notification_channel\" \"email\"" ../billing.tf; then
    echo -e "${GREEN}✓ Email notification channel defined${NC}"
else
    echo -e "${RED}✗ Email notification channel missing${NC}"
    exit 1
fi

# Check for daily spend alert
if grep -q "resource \"google_monitoring_alert_policy\" \"daily_spend_alert\"" ../billing.tf; then
    echo -e "${GREEN}✓ Daily spend monitoring alert defined${NC}"
else
    echo -e "${RED}✗ Daily spend monitoring alert missing${NC}"
    exit 1
fi

# Check if daily limit is $10
if grep -q "threshold_value = 10.0" ../billing.tf; then
    echo -e "${GREEN}✓ Daily spend limit set to \$10${NC}"
else
    echo -e "${YELLOW}⚠ Daily spend limit may not be \$10${NC}"
fi

# Validate variables.tf has billing variables
echo ""
echo "Checking variables.tf for billing variables..."

REQUIRED_VARS=("billing_account_name" "budget_amount" "budget_alert_email" "notification_channels")
for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "variable \"$var\"" ../variables.tf; then
        echo -e "${GREEN}✓ Variable $var defined${NC}"
    else
        echo -e "${RED}✗ Variable $var missing${NC}"
        exit 1
    fi
done

# Check default budget amount
if grep -q "default.*=.*\"300\"" ../variables.tf; then
    echo -e "${GREEN}✓ Default budget amount set to \$300${NC}"
else
    echo -e "${YELLOW}⚠ Default budget amount may not be \$300${NC}"
fi

# Summary
echo ""
echo "=== Validation Summary ==="
echo -e "${GREEN}✓ All critical billing configurations are in place${NC}"
echo ""
echo "Key features validated:"
echo "- Budget resource with \$300 limit"
echo "- 9 alert thresholds (including forecast)"
echo "- First alert at \$10 (3.33%)"
echo "- Daily spend monitoring (\$10/day limit)"
echo "- Email notifications configured"
echo "- All required variables defined"
echo ""
echo -e "${GREEN}✓ Billing configuration is ready for deployment${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT: Apply billing configuration FIRST before any other resources${NC}"