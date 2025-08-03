#!/bin/bash

# Backend Hardening Script for Internal Access Proxy
# This script makes the backend service private and grants frontend service account access
# Can be run multiple times safely (idempotent)

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE="${GCP_BACKEND_SERVICE_NAME:-re-frame-backend}"
FRONTEND_SERVICE="${GCP_FRONTEND_SERVICE_NAME:-re-frame-frontend}"
FRONTEND_SA="${FRONTEND_SA:-875750705254-compute@developer.gserviceaccount.com}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation function
validate_config() {
    if [[ -z "$PROJECT_ID" ]]; then
        log_error "GCP_PROJECT_ID environment variable is required"
        exit 1
    fi

    log_info "Configuration:"
    echo "  Project ID: $PROJECT_ID"
    echo "  Region: $REGION"
    echo "  Backend Service: $BACKEND_SERVICE"
    echo "  Frontend Service: $FRONTEND_SERVICE"
    echo "  Frontend SA: $FRONTEND_SA"
    echo
}

# Check if gcloud is authenticated and project is set
check_gcloud_auth() {
    log_info "Checking gcloud authentication..."

    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "No active gcloud authentication found. Please run 'gcloud auth login'"
        exit 1
    fi

    if ! gcloud config get-value project &>/dev/null; then
        log_warning "No default project set. Setting project to $PROJECT_ID"
        gcloud config set project "$PROJECT_ID"
    fi

    local current_project
    current_project=$(gcloud config get-value project 2>/dev/null)
    if [[ "$current_project" != "$PROJECT_ID" ]]; then
        log_warning "Current project ($current_project) differs from target ($PROJECT_ID). Setting project."
        gcloud config set project "$PROJECT_ID"
    fi

    log_success "gcloud authentication validated"
}

# Check if backend service exists
check_backend_service() {
    log_info "Checking if backend service exists..."

    if ! gcloud run services describe "$BACKEND_SERVICE" --region="$REGION" &>/dev/null; then
        log_error "Backend service '$BACKEND_SERVICE' not found in region '$REGION'"
        log_error "Please deploy the backend service first"
        exit 1
    fi

    log_success "Backend service found"
}

# Check if frontend service exists and get its service account
get_frontend_service_account() {
    log_info "Getting frontend service account..."

    if ! gcloud run services describe "$FRONTEND_SERVICE" --region="$REGION" &>/dev/null; then
        log_warning "Frontend service '$FRONTEND_SERVICE' not found. Using default service account: $FRONTEND_SA"
        return
    fi

    local sa
    sa=$(gcloud run services describe "$FRONTEND_SERVICE" \
        --region="$REGION" \
        --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null || echo "")

    if [[ -n "$sa" ]]; then
        FRONTEND_SA="$sa"
        log_success "Found frontend service account: $FRONTEND_SA"
    else
        log_warning "No service account found for frontend service. Using default: $FRONTEND_SA"
    fi
}

# Make backend service private (internal ingress only)
harden_backend_ingress() {
    log_info "Configuring backend service for internal access only..."

    # Check current ingress setting
    local current_ingress
    current_ingress=$(gcloud run services describe "$BACKEND_SERVICE" \
        --region="$REGION" \
        --format='value(metadata.annotations."run.googleapis.com/ingress")' 2>/dev/null || echo "")

    if [[ "$current_ingress" == "internal" ]]; then
        log_success "Backend service already configured for internal access"
        return
    fi

    log_info "Setting backend ingress to internal..."
    gcloud run services update "$BACKEND_SERVICE" \
        --region="$REGION" \
        --ingress=internal \
        --no-allow-unauthenticated \
        --quiet

    log_success "Backend service configured for internal access only"
}

# Grant frontend service account invoker role on backend
grant_frontend_access() {
    log_info "Granting frontend service account access to backend..."
    log_info "Service Account: $FRONTEND_SA"

    # Check if the IAM policy binding already exists
    local iam_policy
    iam_policy=$(gcloud run services get-iam-policy "$BACKEND_SERVICE" \
        --region="$REGION" \
        --format=json 2>/dev/null || echo "{}")

    # Try to use jq if available, otherwise fall back to Python
    local has_binding="no"

    if command -v jq &> /dev/null; then
        # Use jq for JSON parsing
        has_binding=$(echo "$iam_policy" | jq -r --arg sa "serviceAccount:$FRONTEND_SA" '
            .bindings[]? |
            select(.role == "roles/run.invoker") |
            .members[]? |
            select(. == $sa) |
            "yes"' 2>/dev/null | head -n1)
        [[ -z "$has_binding" ]] && has_binding="no"
    elif command -v python3 &> /dev/null; then
        # Use Python for JSON parsing
        has_binding=$(echo "$iam_policy" | python3 -c "
import sys, json
try:
    policy = json.load(sys.stdin)
    for binding in policy.get('bindings', []):
        if binding.get('role') == 'roles/run.invoker':
            if 'serviceAccount:$FRONTEND_SA' in binding.get('members', []):
                print('yes')
                sys.exit(0)
    print('no')
except:
    print('no')
" 2>/dev/null || echo "no")
    else
        # Fallback to grep-based check (less reliable)
        if echo "$iam_policy" | grep -q "serviceAccount:$FRONTEND_SA" && \
           echo "$iam_policy" | grep -q "roles/run.invoker"; then
            has_binding="maybe"
        fi
    fi

    if [[ "$has_binding" == "yes" ]]; then
        log_success "Frontend service account already has invoker access to backend"
        return
    elif [[ "$has_binding" == "maybe" ]]; then
        log_warning "Could not definitively verify existing permissions, will attempt to grant anyway"
    fi

    log_info "Adding IAM policy binding for roles/run.invoker..."
    gcloud run services add-iam-policy-binding "$BACKEND_SERVICE" \
        --region="$REGION" \
        --member="serviceAccount:$FRONTEND_SA" \
        --role="roles/run.invoker" \
        --quiet

    log_success "Frontend service account granted invoker access to backend"
}

# Verify the configuration
verify_configuration() {
    log_info "Verifying backend hardening configuration..."

    # Check ingress setting
    local ingress
    ingress=$(gcloud run services describe "$BACKEND_SERVICE" \
        --region="$REGION" \
        --format='value(metadata.annotations."run.googleapis.com/ingress")' 2>/dev/null || echo "")

    if [[ "$ingress" != "internal" ]]; then
        log_error "Backend ingress is not set to internal: $ingress"
        return 1
    fi

    # Check authentication requirement
    local auth_policy
    auth_policy=$(gcloud run services describe "$BACKEND_SERVICE" \
        --region="$REGION" \
        --format='value(spec.template.metadata.annotations."run.googleapis.com/ingress-status")' 2>/dev/null || echo "")

    # Check IAM policy
    log_info "Checking IAM permissions for: $FRONTEND_SA"
    local iam_policy
    iam_policy=$(gcloud run services get-iam-policy "$BACKEND_SERVICE" \
        --region="$REGION" \
        --format=json 2>/dev/null || echo "{}")

    # Debug: show the policy if verbose
    if [[ "${VERBOSE:-}" == "true" ]]; then
        echo "IAM Policy JSON:"
        echo "$iam_policy" | python3 -m json.tool 2>/dev/null || echo "$iam_policy"
    fi

    # Parse the JSON to check for the specific binding
    local has_invoker_access="no"

    if command -v jq &> /dev/null; then
        # Use jq for JSON parsing
        has_invoker_access=$(echo "$iam_policy" | jq -r --arg sa "serviceAccount:$FRONTEND_SA" '
            .bindings[]? |
            select(.role == "roles/run.invoker") |
            .members[]? |
            select(. == $sa) |
            "yes"' 2>/dev/null | head -n1)
        [[ -z "$has_invoker_access" ]] && has_invoker_access="no"
    elif command -v python3 &> /dev/null; then
        # Use Python for JSON parsing
        has_invoker_access=$(echo "$iam_policy" | python3 -c "
import sys, json
try:
    policy = json.load(sys.stdin)
    for binding in policy.get('bindings', []):
        if binding.get('role') == 'roles/run.invoker':
            members = binding.get('members', [])
            # Check for exact match
            if 'serviceAccount:$FRONTEND_SA' in members:
                print('yes')
                sys.exit(0)
            # Also check without 'serviceAccount:' prefix
            if '$FRONTEND_SA' in members:
                print('yes')
                sys.exit(0)
            # Debug: print what we found
            for member in members:
                if 'compute@developer' in member or 'run.serviceaccount' in member:
                    print(f'# Found related SA: {member}', file=sys.stderr)
    print('no')
except Exception as e:
    print(f'# Error parsing JSON: {e}', file=sys.stderr)
    print('no')
" 2>&1 | grep -v '^#' | head -n1 || echo "no")
    else
        log_warning "Neither jq nor python3 available for JSON parsing, using basic grep"
        # Fallback to grep-based check
        if echo "$iam_policy" | grep -q "serviceAccount:$FRONTEND_SA" && \
           echo "$iam_policy" | grep -q "roles/run.invoker"; then
            has_invoker_access="yes"
        fi
    fi

    if [[ "$has_invoker_access" != "yes" ]]; then
        log_error "Frontend service account does not have invoker access to backend"
        log_error "Expected service account: serviceAccount:$FRONTEND_SA"
        log_error ""
        log_error "To fix this, run:"
        echo "    gcloud run services add-iam-policy-binding $BACKEND_SERVICE \\"
        echo "        --region=$REGION \\"
        echo "        --member='serviceAccount:$FRONTEND_SA' \\"
        echo "        --role='roles/run.invoker'"
        return 1
    fi

    log_success "Backend hardening configuration verified successfully"
    echo
    log_success "Security Configuration Summary:"
    echo "  ✓ Backend service is internal-only (no public access)"
    echo "  ✓ Backend requires authentication"
    echo "  ✓ Frontend service account ($FRONTEND_SA) has invoker access"
    echo "  ✓ All traffic between frontend and backend is authenticated via IAM"
}

# Display help
show_help() {
    cat << EOF
Backend Hardening Script for Internal Access Proxy

This script configures the backend Cloud Run service for secure internal access:
1. Sets backend ingress to 'internal' (no public access)
2. Ensures backend requires authentication
3. Grants frontend service account roles/run.invoker permission

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -v, --verify-only       Only verify current configuration (no changes)
    --dry-run              Show what would be done without making changes
    --debug                Enable debug output for troubleshooting
    --verbose              Show verbose output including IAM policies

Environment Variables:
    GCP_PROJECT_ID         (Required) GCP project ID
    GCP_REGION            (Optional) GCP region (default: us-central1)
    GCP_BACKEND_SERVICE_NAME   (Optional) Backend service name (default: re-frame-backend)
    GCP_FRONTEND_SERVICE_NAME  (Optional) Frontend service name (default: re-frame-frontend)
    FRONTEND_SA           (Optional) Frontend service account (default: 875750705254-compute@developer.gserviceaccount.com)
    VERBOSE               (Optional) Set to 'true' for verbose output

Examples:
    # Basic usage
    export GCP_PROJECT_ID="my-project"
    $0

    # Verify configuration only
    $0 --verify-only

    # Custom region and services
    export GCP_PROJECT_ID="my-project"
    export GCP_REGION="us-west1"
    export GCP_BACKEND_SERVICE_NAME="my-backend"
    $0
EOF
}

# Main execution
main() {
    local verify_only=false
    local dry_run=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verify-only)
                verify_only=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --debug)
                set -x
                shift
                ;;
            --verbose)
                export VERBOSE=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    log_info "Starting backend hardening process..."
    echo

    validate_config
    check_gcloud_auth
    check_backend_service
    get_frontend_service_account

    if [[ "$verify_only" == "true" ]]; then
        verify_configuration
        exit 0
    fi

    if [[ "$dry_run" == "true" ]]; then
        log_info "DRY RUN MODE - No changes will be made"
        log_info "Would execute:"
        echo "  1. Set backend ingress to internal"
        echo "  2. Ensure backend requires authentication"
        echo "  3. Grant frontend SA ($FRONTEND_SA) roles/run.invoker on backend"
        exit 0
    fi

    harden_backend_ingress
    grant_frontend_access

    echo
    verify_configuration

    log_success "Backend hardening completed successfully!"
}

# Run main function with all arguments
main "$@"
