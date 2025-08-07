#!/usr/bin/env bash
# bootstrap_vpc_and_roles.sh  —  one-time "Option B" helper
# -------------------------------------------------------------------
# • Verifies roles on the GitHub WIF SA
# • Enables Cloud Run + VPC Access APIs
# • Creates the VPC Access connector if missing
#
# Run this locally (or in Cloud Shell) with OWNER or Network Admin perms.
# -------------------------------------------------------------------

set -euo pipefail

# Load configuration
SCRIPT_DIR="$(dirname "$0")"
source "${SCRIPT_DIR}/config.sh"

: "${GCP_WIF_SERVICE_ACCOUNT:?Need env var GCP_WIF_SERVICE_ACCOUNT}"

# Use values from config.sh (VPC_CONNECTOR, GCP_REGION, VPC_RANGE already set)
CONNECTOR="$VPC_CONNECTOR"
REGION="$GCP_REGION"
NETWORK="default"
RANGE="$VPC_RANGE"     # /28 → 16 IPs (good for dozens of Cloud Run services)

echo "Project      : $GCP_PROJECT_ID"
echo "WIF SA       : $GCP_WIF_SERVICE_ACCOUNT"
echo "Connector    : $CONNECTOR  ($REGION | $NETWORK | $RANGE)"
echo

# ---------- 0. helpers -------------------------------------------------
api_enabled () {
  gcloud services list --enabled --project "$GCP_PROJECT_ID" \
    --format="value(config.name)" | grep -q "^$1$"
}
enable_api () {
  local api=$1
  if api_enabled "$api"; then
    echo "✓ $api already enabled"
  else
    echo "• Enabling $api ..."
    gcloud services enable "$api" --project "$GCP_PROJECT_ID"
  fi
}

role_present () {
  local role=$1
  gcloud projects get-iam-policy "$GCP_PROJECT_ID" \
    --flatten="bindings[].members" \
    --filter="bindings.role:$role AND bindings.members:serviceAccount:$GCP_WIF_SERVICE_ACCOUNT" \
    --format="value(bindings.role)" | grep -q .
}
grant_role () {
  echo "• Granting $1"
  gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
    --member="serviceAccount:$GCP_WIF_SERVICE_ACCOUNT" \
    --role="$1" --quiet
}

sa_role_present () {
  gcloud iam service-accounts get-iam-policy "$GCP_WIF_SERVICE_ACCOUNT" \
    --format="value(bindings.role)" | grep -q "$1"
}
grant_sa_role () {
  echo "• Granting SA-level $1"
  gcloud iam service-accounts add-iam-policy-binding "$GCP_WIF_SERVICE_ACCOUNT" \
    --member="serviceAccount:$GCP_WIF_SERVICE_ACCOUNT" \
    --role="$1" --quiet
}

# ---------- 1. roles ---------------------------------------------------
PROJECT_ROLES=(
  "roles/run.admin"
  "roles/vpcaccess.user"             # only *use* rights, not admin
  "roles/serviceusage.serviceUsageAdmin"
)
SA_ROLES=("roles/iam.serviceAccountUser")

echo "🔑 Ensuring project-level roles …"
for r in "${PROJECT_ROLES[@]}"; do
  role_present "$r" || grant_role "$r"
done

echo "🔑 Ensuring SA-level roles …"
for r in "${SA_ROLES[@]}"; do
  sa_role_present "$r" || grant_sa_role "$r"
done
echo "✅ Roles ready."
echo

# ---------- 2. APIs ----------------------------------------------------
enable_api "run.googleapis.com"
enable_api "vpcaccess.googleapis.com"
echo "✅ APIs ready."
echo

# ---------- 3. Connector ----------------------------------------------
if gcloud compute networks vpc-access connectors describe "$CONNECTOR" \
     --project "$GCP_PROJECT_ID" --region "$REGION" >/dev/null 2>&1; then
  echo "✓ Connector '$CONNECTOR' already exists."
else
  echo "• Creating connector '$CONNECTOR' (this takes ~3-4 min)…"
  gcloud compute networks vpc-access connectors create "$CONNECTOR" \
    --project "$GCP_PROJECT_ID" \
    --region  "$REGION" \
    --network "$NETWORK" \
    --range   "$RANGE"
fi

echo
echo "🎉 Bootstrap complete — your GitHub Actions workflow can now"
echo "   attach '$CONNECTOR' with only roles/vpcaccess.user."
