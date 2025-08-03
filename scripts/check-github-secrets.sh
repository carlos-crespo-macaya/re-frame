#!/bin/bash
set -euo pipefail

# Check GitHub Secrets for re-frame deployment
echo "🔍 Checking GitHub Secrets Configuration"
echo "========================================"

# Required secrets for basic deployment
REQUIRED_SECRETS=(
    "GCP_WIF_PROVIDER"
    "GCP_WIF_SERVICE_ACCOUNT"
    "GCP_PROJECT_ID"
    "GCP_BILLING_ACCOUNT_ID"
    "GEMINI_API_KEY"
)

# Optional secrets for IAP (Identity-Aware Proxy) and other features
OPTIONAL_SECRETS=(
    "GCP_REGION"
    "GCP_REFRAME_IAP_CLIENT_ID"
    "GCP_REFRAME_IAP_CLIENT_SECRET"
    "AUTHORIZED_DOMAIN"
)

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "   Install it from: https://cli.github.com/"
    echo ""
    echo "   On macOS: brew install gh"
    echo "   Then run: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ Not authenticated with GitHub CLI."
    echo "   Run: gh auth login"
    exit 1
fi

# Get repository (owner/name format)
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo "❌ Not in a GitHub repository or can't detect it."
    echo "   Make sure you're in the repository directory."
    exit 1
fi

echo "Repository: $REPO"
echo ""

# Get all secrets
echo "Fetching repository secrets..."
EXISTING_SECRETS=$(gh secret list --repo "$REPO" --json name -q '.[].name' 2>/dev/null || echo "")

# Check each required secret
echo ""
echo "Secret Status:"
echo "=============="

MISSING_SECRETS=()
FOUND_SECRETS=()
MISSING_OPTIONAL_SECRETS=()
FOUND_OPTIONAL_SECRETS=()

echo "Required Secrets:"
echo "=================="
for SECRET in "${REQUIRED_SECRETS[@]}"; do
    if echo "$EXISTING_SECRETS" | grep -q "^${SECRET}$"; then
        echo "✅ $SECRET"
        FOUND_SECRETS+=("$SECRET")
    else
        echo "❌ $SECRET (missing)"
        MISSING_SECRETS+=("$SECRET")
    fi
done

echo ""
echo "Optional Secrets:"
echo "================="
for SECRET in "${OPTIONAL_SECRETS[@]}"; do
    if echo "$EXISTING_SECRETS" | grep -q "^${SECRET}$"; then
        echo "✅ $SECRET (optional)"
        FOUND_OPTIONAL_SECRETS+=("$SECRET")
    else
        case $SECRET in
            "GCP_REGION")
                echo "⚠️  $SECRET (optional - hardcoded to europe-west1)"
                ;;
            *)
                echo "⚠️  $SECRET (optional - for IAP protection)"
                ;;
        esac
        MISSING_OPTIONAL_SECRETS+=("$SECRET")
    fi
done

echo ""
echo "Summary:"
echo "========"
echo "✅ Required secrets found: ${#FOUND_SECRETS[@]}/${#REQUIRED_SECRETS[@]}"
echo "❌ Required secrets missing: ${#MISSING_SECRETS[@]}"
echo "✅ Optional secrets found: ${#FOUND_OPTIONAL_SECRETS[@]}/${#OPTIONAL_SECRETS[@]}"
echo "⚠️  Optional secrets missing: ${#MISSING_OPTIONAL_SECRETS[@]}"

# Show expected values for missing secrets
if [ ${#MISSING_SECRETS[@]} -gt 0 ]; then
    echo ""
    echo "Missing Secret Values:"
    echo "===================="

    for SECRET in "${MISSING_SECRETS[@]}"; do
        case $SECRET in
            "GCP_WIF_PROVIDER")
                echo "$SECRET:"
                echo "  Value: projects/875750705254/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider"
                echo ""
                ;;
            "GCP_WIF_SERVICE_ACCOUNT")
                echo "$SECRET:"
                echo "  Value: github-actions-deploy@gen-lang-client-0105778560.iam.gserviceaccount.com"
                echo ""
                ;;
            "GCP_PROJECT_ID")
                echo "$SECRET:"
                echo "  Value: gen-lang-client-0105778560"
                echo ""
                ;;
            "GCP_REGION")
                echo "$SECRET:"
                echo "  Value: europe-west1"
                echo ""
                ;;
            "GCP_BILLING_ACCOUNT_ID")
                echo "$SECRET:"
                echo "  Value: 01FB26-BC3BF1-C9A591"
                echo ""
                ;;
            "GEMINI_API_KEY")
                echo "$SECRET:"
                echo "  Get from: https://aistudio.google.com/app/apikey"
                echo ""
                ;;
            "IAP_CLIENT_ID")
                echo "$SECRET:"
                echo "  Get from OAuth credentials you created in GCP Console"
                echo ""
                ;;
            "IAP_CLIENT_SECRET")
                echo "$SECRET:"
                echo "  Get from OAuth credentials you created in GCP Console"
                echo ""
                ;;
            "AUTHORIZED_DOMAIN")
                echo "$SECRET:"
                echo "  Value: run.app"
                echo ""
                ;;
        esac
    done

    echo "To add missing secrets:"
    echo "====================="
    echo "1. Go to: https://github.com/$REPO/settings/secrets/actions"
    echo "2. Click 'New repository secret' for each missing secret"
    echo "3. Use the values shown above"
    echo ""
    echo "Or use gh CLI:"
    echo "gh secret set SECRET_NAME --repo $REPO"
else
    echo ""
    echo "🎉 All required secrets are configured!"
    echo ""
    if [ ${#MISSING_OPTIONAL_SECRETS[@]} -gt 0 ]; then
        echo "ℹ️  Note: Optional secrets are missing but not required for basic deployment"
        echo "   - GCP_REGION is hardcoded to europe-west1"
        echo "   - IAP secrets can be added later for Identity-Aware Proxy protection"
        echo ""
    fi
    echo "You're ready to deploy! Run:"
    echo "  git tag v0.1.0-beta"
    echo "  git push origin v0.1.0-beta"
fi
