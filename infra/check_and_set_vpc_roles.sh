#!/usr/bin/env bash
# ensure_roles.sh  —  verify & grant Cloud Run + VPC + SA-user roles
#
# Prerequisites:
#   • gcloud CLI authenticated to the project
#   • env vars:
#         GCP_PROJECT_ID          (e.g. "my-project-123")
#         GCP_WIF_SERVICE_ACCOUNT (e.g. "github-wif-sa@my-project-123.iam.gserviceaccount.com")

set -euo pipefail

######################## 1. sanity-check env vars ########################
: "${GCP_PROJECT_ID:?Need env var GCP_PROJECT_ID}"
: "${GCP_WIF_SERVICE_ACCOUNT:?Need env var GCP_WIF_SERVICE_ACCOUNT}"

echo "Project ............: $GCP_PROJECT_ID"
echo "Workload SA ........: $GCP_WIF_SERVICE_ACCOUNT"
echo

######################## 2. role definitions #############################
PROJECT_ROLES=(
  "roles/run.admin"
  "roles/vpcaccess.user"
)
SA_ROLES=(
  "roles/iam.serviceAccountUser"
)

######################## 3. helper functions #############################
has_project_role () {
  local role=$1
  gcloud projects get-iam-policy "$GCP_PROJECT_ID" \
    --flatten="bindings[].members" \
    --filter="bindings.role:$role AND bindings.members:serviceAccount:$GCP_WIF_SERVICE_ACCOUNT" \
    --format="value(bindings.role)" | grep -q .
}

has_sa_role () {
  local role=$1
  gcloud iam service-accounts get-iam-policy "$GCP_WIF_SERVICE_ACCOUNT" \
    --format="value(bindings.role)" | grep -q "$role"
}

add_project_role () {
  local role=$1
  echo "• Granting $role (project-level)"
  gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
    --member="serviceAccount:$GCP_WIF_SERVICE_ACCOUNT" \
    --role="$role" \
    --quiet
}

add_sa_role () {
  local role=$1
  echo "• Granting $role (service-account-level)"
  gcloud iam service-accounts add-iam-policy-binding "$GCP_WIF_SERVICE_ACCOUNT" \
    --member="serviceAccount:$GCP_WIF_SERVICE_ACCOUNT" \
    --role="$role" \
    --quiet
}

######################## 4. check & grant ###############################
echo "Checking project-level roles …"
for role in "${PROJECT_ROLES[@]}"; do
  if has_project_role "$role"; then
    echo "✓ $role already present"
  else
    add_project_role "$role"
  fi
done
echo

echo "Checking service-account-level roles …"
for role in "${SA_ROLES[@]}"; do
  if has_sa_role "$role"; then
    echo "✓ $role already present"
  else
    add_sa_role "$role"
  fi
done
echo
echo "✅ All required bindings are now in place."
