#!/usr/bin/env bash
# Configure reCAPTCHA v3 (classic) for Cloud Run frontend and backend
# - Frontend: sets NEXT_PUBLIC_RECAPTCHA_* envs (public)
# - Backend: by default, stores the secret in Secret Manager and wires it via --update-secrets
#            (recommended). Optionally, you can force a literal env var.
#
# Defaults are aligned with docs/gcp-cloud-run-setup.md
#
# Usage:
#   ./infra/gcp/setup-recaptcha-classic.sh \
#     --site-key "<your_v3_site_key>" \
#     --secret "<your_v3_secret_key>" \
#     [--project-id "$PROJECT_ID"] [--region "$REGION"] \
#     [--frontend-service "$FRONTEND_SERVICE"] [--backend-service "$BACKEND_SERVICE"] \
#     [--secret-name recaptcha-secret] \
#     [--grant-scope secret|project]           # default: secret  (where to grant secretAccessor)
#     [--use-literal-backend]                  # optional: store backend secret as literal env (not recommended)
#     [--github-repo owner/repo]               # optional: also set GitHub repo secrets via gh CLI
#
# Examples:
#   ./infra/gcp/setup-recaptcha-classic.sh \
#     --site-key "SITE_KEY" --secret "SECRET_KEY" \
#     --github-repo "carlos-crespo-macaya/re-frame"
#
# After running, verify:
#   gcloud run services describe "$FRONTEND_SERVICE" --project="$PROJECT_ID" --region="$REGION" | grep NEXT_PUBLIC_RECAPTCHA
#   gcloud run services describe "$BACKEND_SERVICE"  --project="$PROJECT_ID" --region="$REGION" | grep RECAPTCHA_

set -euo pipefail

# --- Defaults ---
: "${PROJECT_ID:=gen-lang-client-0105778560}"
: "${REGION:=europe-west1}"
: "${FRONTEND_SERVICE:=re-frame-frontend}"
: "${BACKEND_SERVICE:=re-frame-backend}"
: "${SECRET_NAME:=recaptcha-secret}"
: "${GRANT_SCOPE:=secret}"   # secret|project

SITE_KEY="${NEXT_PUBLIC_RECAPTCHA_SITE_KEY:-}"
SECRET_KEY="${RECAPTCHA_SECRET:-}"
GITHUB_REPO="${GITHUB_REPO:-}"
USE_LITERAL_BACKEND=false

print_usage() {
  sed -n '1,120p' "$0" | sed 's/^# \{0,1\}//'
}

# --- Parse flags ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --site-key)            SITE_KEY="$2"; shift 2;;
    --secret)              SECRET_KEY="$2"; shift 2;;
    --project-id)          PROJECT_ID="$2"; shift 2;;
    --region)              REGION="$2"; shift 2;;
    --frontend-service)    FRONTEND_SERVICE="$2"; shift 2;;
    --backend-service)     BACKEND_SERVICE="$2"; shift 2;;
    --secret-name)         SECRET_NAME="$2"; shift 2;;
    --grant-scope)         GRANT_SCOPE="$2"; shift 2;;
    --use-literal-backend) USE_LITERAL_BACKEND=true; shift 1;;
    --github-repo)         GITHUB_REPO="$2"; shift 2;;
    -h|--help)             print_usage; exit 0;;
    *) echo "Unknown argument: $1" >&2; print_usage; exit 1;;
  esac
done

# --- Validate inputs ---
if [[ -z "$SITE_KEY" || -z "$SECRET_KEY" ]]; then
  echo "Error: --site-key and --secret are required (or set NEXT_PUBLIC_RECAPTCHA_SITE_KEY / RECAPTCHA_SECRET)." >&2
  exit 1
fi

command -v gcloud >/dev/null 2>&1 || { echo "gcloud not found in PATH" >&2; exit 1; }

echo "==> Updating Cloud Run FRONTEND env (public site key)"
gcloud run services update "$FRONTEND_SERVICE" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --set-env-vars NEXT_PUBLIC_RECAPTCHA_PROVIDER=classic,NEXT_PUBLIC_RECAPTCHA_SITE_KEY="$SITE_KEY"

if [[ "$USE_LITERAL_BACKEND" == true ]]; then
  echo "==> Using LITERAL backend secret (not recommended)"
  # If the service previously used a secret reference, remove it first
  set +e
  gcloud run services update "$BACKEND_SERVICE" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --remove-secrets RECAPTCHA_SECRET >/dev/null 2>&1
  set -e

  gcloud run services update "$BACKEND_SERVICE" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --set-env-vars RECAPTCHA_PROVIDER=classic,RECAPTCHA_SECRET="$SECRET_KEY"
else
  echo "==> Storing backend secret in Secret Manager and wiring via --update-secrets"
  # Create or update the secret value
  if ! gcloud secrets describe "$SECRET_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo -n "$SECRET_KEY" | gcloud secrets create "$SECRET_NAME" \
      --project="$PROJECT_ID" \
      --data-file=- \
      --replication-policy="automatic"
  else
    echo -n "$SECRET_KEY" | gcloud secrets versions add "$SECRET_NAME" \
      --project="$PROJECT_ID" \
      --data-file=-
  fi

  # Discover runtime service account used by the backend service
  RUNTIME_SA="$(gcloud run services describe "$BACKEND_SERVICE" \
    --project="$PROJECT_ID" --region="$REGION" \
    --format='value(spec.template.spec.serviceAccountName)')"
  if [[ -z "$RUNTIME_SA" ]]; then
    PROJECT_NUMBER="$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')"
    RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
  fi
  echo "Using backend runtime service account: $RUNTIME_SA"

  # Grant Secret Manager access
  if [[ "$GRANT_SCOPE" == "project" ]]; then
    echo "==> Granting roles/secretmanager.secretAccessor at PROJECT level"
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
      --member="serviceAccount:$RUNTIME_SA" \
      --role="roles/secretmanager.secretAccessor" \
      --quiet
  else
    echo "==> Granting roles/secretmanager.secretAccessor on SECRET '$SECRET_NAME'"
    gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
      --project="$PROJECT_ID" \
      --member="serviceAccount:$RUNTIME_SA" \
      --role="roles/secretmanager.secretAccessor" \
      --quiet
  fi

  # Update Cloud Run to use the secret
  gcloud run services update "$BACKEND_SERVICE" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --update-secrets RECAPTCHA_SECRET="$SECRET_NAME:latest" \
    --set-env-vars RECAPTCHA_PROVIDER=classic
fi

# Optionally set GitHub repo secrets
if [[ -n "$GITHUB_REPO" ]]; then
  if command -v gh >/dev/null 2>&1; then
    echo "==> Setting GitHub repo secrets in $GITHUB_REPO"
    gh secret set NEXT_PUBLIC_RECAPTCHA_SITE_KEY --repo "$GITHUB_REPO" --body "$SITE_KEY"
    gh secret set RECAPTCHA_SECRET               --repo "$GITHUB_REPO" --body "$SECRET_KEY"
  else
    echo "gh CLI not found; skipping GitHub secrets." >&2
  fi
fi

echo "==> Done. Verification hints:"
echo "  gcloud run services describe \"$FRONTEND_SERVICE\" --project=\"$PROJECT_ID\" --region=\"$REGION\" | grep NEXT_PUBLIC_RECAPTCHA || true"
echo "  gcloud run services describe \"$BACKEND_SERVICE\"  --project=\"$PROJECT_ID\" --region=\"$REGION\" | grep RECAPTCHA_ || true"


