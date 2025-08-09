## GCP Cloud Run setup for frontend + backend with GitHub Actions and WIF

This guide documents the production setup used for this repository: Cloud Run frontend and backend, authenticated proxying from the frontend to the backend using Cloud Run IAM identity tokens, and GitHub Actions deployments via Workload Identity Federation (WIF). Each command includes a brief explanation of what it does.

### 1) Prerequisites

- A Google Cloud project with billing enabled
- gcloud CLI authenticated and configured (Owner or sufficient IAM to set up WIF and Cloud Run)
- Artifact Registry enabled if building/pushing images from CI

Set local variables (replace values accordingly):

```bash
PROJECT_ID="gen-lang-client-0105778560"     # Your GCP project ID
REGION="europe-west1"                      # Region for Cloud Run
FRONTEND_SERVICE="re-frame-frontend"       # Frontend Cloud Run service name
BACKEND_SERVICE="re-frame-backend"         # Backend Cloud Run service name
BACKEND_DOMAIN="api.re-frame.social"       # Public domain for backend
FRONTEND_DOMAIN="re-frame.social"          # Public domain for frontend
POOL_ID="github-deploy-pool"               # WIF pool
PROVIDER_ID="github"                       # WIF provider inside the pool
DEPLOY_SA="github-actions-deploy"          # Deploy service account (name only)
REPO_OWNER="carlos-crespo-macaya"          # GitHub owner/org
REPO_NAME="re-frame"                       # GitHub repo name
```

What this does:
- Defines environment variables used throughout the guide so you can copy/paste the commands.

### 2) Enable required services

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  iam.googleapis.com
```

What this does:
- Enables Cloud Run, Artifact Registry, and IAM APIs needed for deployments and identity federation.

### 3) Create the deploy Service Account

```bash
gcloud iam service-accounts create "$DEPLOY_SA" \
  --project="$PROJECT_ID" \
  --display-name="GitHub Actions Deploy"

DEPLOY_SA_EMAIL="${DEPLOY_SA}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${DEPLOY_SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${DEPLOY_SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

# Optional if building/pushing images from CI
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${DEPLOY_SA_EMAIL}" \
  --role="roles/artifactregistry.admin"
```

What this does:
- Creates a dedicated service account for CI deployments.
- Grants Cloud Run admin and Service Account User to allow deployments.
- Optionally grants Artifact Registry admin if CI will push images.

### 4) Configure Workload Identity Federation (WIF)

Create a WIF pool and GitHub OIDC provider:

```bash
gcloud iam workload-identity-pools create "$POOL_ID" \
  --project="$PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Deploy Pool"

gcloud iam workload-identity-pools providers create-oidc "$PROVIDER_ID" \
  --project="$PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="$POOL_ID" \
  --display-name="GitHub OIDC" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref,attribute.repository_owner=assertion.repository_owner"
```

What this does:
- Creates a federation pool and an OIDC provider for GitHub Actions tokens.
- Maps standard GitHub claims to WIF attributes.

Restrict which repositories/branches may impersonate the SA:

```bash
gcloud iam workload-identity-pools providers update-oidc "$PROVIDER_ID" \
  --project="$PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="$POOL_ID" \
  --attribute-condition="attribute.repository=='${REPO_OWNER}/${REPO_NAME}' && startsWith(attribute.ref,'refs/heads/main')"
```

What this does:
- Ensures only tokens from the given repo on `main` can use this provider.

Grant the WIF principalSet permission to impersonate the deploy SA:

```bash
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

gcloud iam service-accounts add-iam-policy-binding "$DEPLOY_SA_EMAIL" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${REPO_OWNER}/${REPO_NAME}"
```

What this does:
- Allows GitHub tokens matching the attribute condition to impersonate the deploy service account.

If you changed repo ownership later, update both the provider condition and this binding (replace owner/repo accordingly).

### 5) GitHub Actions: authentication and caching

Auth step in workflow:

```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/${{ secrets.GCP_PROJECT_NUMBER }}/locations/global/workloadIdentityPools/${{ secrets.GCP_WIF_POOL }}/providers/${{ secrets.GCP_WIF_PROVIDER }}
    service_account: ${{ secrets.GCP_DEPLOY_SA }}
```

What this does:
- Exchanges the GitHub OIDC token for GCP credentials bound to your deploy service account, without storing keys.

Cache Python deps with uv (no lockfile required):

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'

- uses: astral-sh/setup-uv@v3
  with:
    enable-cache: false

- name: Cache uv resolver
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-py${{ matrix.python-version || '3.12' }}-${{ hashFiles('backend/pyproject.toml') }}
    restore-keys: |
      uv-${{ runner.os }}-py${{ matrix.python-version || '3.12' }}-

- name: Install backend deps
  run: |
    cd backend
    uv sync --all-extras
```

What this does:
- Avoids depending on `uv.lock` in CI; installs from `pyproject.toml` and caches resolver results.

### 6) Build and deploy Cloud Run services

You can build with Cloud Build or GitHub Actions. Example deploy commands (images assumed already available):

```bash
gcloud run deploy "$BACKEND_SERVICE" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="europe-west1-docker.pkg.dev/${PROJECT_ID}/re-frame/${BACKEND_SERVICE}:$GITHUB_SHA" \
  --allow-unauthenticated \
  --platform=managed

gcloud run deploy "$FRONTEND_SERVICE" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="europe-west1-docker.pkg.dev/${PROJECT_ID}/re-frame/${FRONTEND_SERVICE}:$GITHUB_SHA" \
  --allow-unauthenticated \
  --platform=managed \
  --set-env-vars BACKEND_INTERNAL_HOST=${BACKEND_DOMAIN},BACKEND_PUBLIC_URL=https://${BACKEND_DOMAIN}
```

What this does:
- Deploys backend and frontend Cloud Run services.
- Sets frontend env vars used by the proxy route:
  - `BACKEND_INTERNAL_HOST`: host used to construct the target URL.
  - `BACKEND_PUBLIC_URL`: used as the audience for Google Auth ID tokens.

Note: If your frontend cannot resolve the backend `.internal` hostname, set both to the public domain (as above). If both services are in the same VPC with internal DNS, you can instead set `BACKEND_INTERNAL_HOST` to `re-frame-backend.${REGION}.internal` and keep `BACKEND_PUBLIC_URL` to the public URL.

### 7) Custom domain mappings (optional but recommended)

We provide a helper script to create the mappings and print the exact DNS records you must set at your DNS provider (e.g., Name.com, Cloud DNS). It can also wait for certificate provisioning.

```bash
# One‑time, from repo root
chmod +x infra/gcp/setup-domain-mappings.sh

# Frontend mapping (apex)
PROJECT_ID="$PROJECT_ID" REGION="$REGION" \
FRONTEND_SERVICE="$FRONTEND_SERVICE" FRONTEND_DOMAIN="$FRONTEND_DOMAIN" \
WAIT_MINUTES=10 ./infra/gcp/setup-domain-mappings.sh

# Backend mapping (subdomain)
PROJECT_ID="$PROJECT_ID" REGION="$REGION" \
BACKEND_SERVICE="$BACKEND_SERVICE" BACKEND_DOMAIN="$BACKEND_DOMAIN" \
WAIT_MINUTES=10 ./infra/gcp/setup-domain-mappings.sh
```

What this does:
- Creates domain mappings in the specified region using the beta Run API (required for regional flag).
- Prints the required DNS records. Typical values:
  - Apex `re-frame.social`: 4 A records (216.239.32.21, .34.21, .36.21, .38.21) and 4 AAAA records (2001:4860:4802:32::15, ::34::15, ::36::15, ::38::15)
  - `www.re-frame.social`: CNAME `ghs.googlehosted.com.`
- Optionally polls readiness (certificate provisioning) for up to `WAIT_MINUTES`.

Notes:
- Do not purchase or upload a certificate at your registrar; Cloud Run issues a managed certificate automatically once DNS is correct and public.
- If you manage DNS elsewhere, ensure no URL forwarding/proxy is enabled for apex/`www`. If you publish CAA, include `0 issue "pki.goog"`.

### 8) Frontend proxy route: how it works

File: `frontend/app/api/proxy/[...path]/route.ts`

- Reads env vars: `BACKEND_INTERNAL_HOST`, `BACKEND_PUBLIC_URL`.
- Builds the target URL for backend calls as `https://${BACKEND_INTERNAL_HOST}/${path}?${search}`.
- Obtains a Google Auth ID token client with audience set to `BACKEND_PUBLIC_URL`.
- Sends the request to the backend with proper headers; SSE requests are handled via `fetch` with `duplex: 'half'`.

Key effects:
- Audience (public URL) must match the backend’s identity configuration so Cloud Run accepts the token.
- Using a public domain for both target and audience simplifies DNS resolution for the frontend service.

### 9) CI/CD: dynamic backend URL and internal host

The frontend proxy route uses two env vars at deploy time:

- `BACKEND_INTERNAL_HOST`: the host to which the frontend proxies (e.g. `api.re-frame.social`). In most setups, using the public backend domain is preferred; Cloud Run’s `.internal` names are not resolvable from the public frontend unless you configure VPC/DNS. Set it explicitly during deploy.
- `BACKEND_PUBLIC_URL`: audience for Cloud Run IAM identity tokens (must match the backend’s public URL). This is critical for authenticated proxying.

In GitHub Actions, set them via `--set-env-vars` when deploying the frontend, using your known backend domain:

```bash
gcloud run deploy "$FRONTEND_SERVICE" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --image="europe-west1-docker.pkg.dev/${PROJECT_ID}/re-frame/${FRONTEND_SERVICE}:$GITHUB_SHA" \
  --allow-unauthenticated \
  --platform=managed \
  --set-env-vars BACKEND_INTERNAL_HOST=${BACKEND_DOMAIN},BACKEND_PUBLIC_URL=https://${BACKEND_DOMAIN}
```

If you later change the backend domain, redeploy the frontend with updated values. There’s no need to “discover” internal IPs; Cloud Run uses HTTPS hostnames and manages IPs behind anycast.

### 10) Troubleshooting

- unauthorized_client during `google-github-actions/auth@v2`:
  - Your WIF provider’s `attribute-condition` likely doesn’t match the current repository or branch. Update it if the repo owner changed:
  ```bash
  gcloud iam workload-identity-pools providers update-oidc "$PROVIDER_ID" \
    --project="$PROJECT_ID" \
    --location=global \
    --workload-identity-pool="$POOL_ID" \
    --attribute-condition="attribute.repository=='${REPO_OWNER}/${REPO_NAME}' && startsWith(attribute.ref,'refs/heads/main')"
  ```

- 500: Backend URL not configured:
  - Ensure `BACKEND_PUBLIC_URL` is set on the frontend Cloud Run service.

- Proxy disabled in dev:
  - In local dev, create `frontend/.env.local` with `BACKEND_INTERNAL_HOST` and `BACKEND_PUBLIC_URL`.

- ENOTFOUND for internal host in prod:
  - Set `BACKEND_INTERNAL_HOST` to the public backend domain instead of `.internal`.

- Docker build failing on missing `uv.lock`:
  - Make lock optional in `backend/Dockerfile` (copy only `pyproject.toml` and run `uv sync`; use `--frozen` if `uv.lock` exists).

### 11) Minimal backend Dockerfile approach (no lock required)

```Dockerfile
# Copy dependency file first
COPY pyproject.toml ./

# Install Python dependencies via uv (resolve from pyproject)
RUN uv sync --no-dev
```

What this does:
- Avoids requiring `uv.lock` so CI/CD does not fail when the lockfile isn’t committed.

### 12) Health checks

- Backend: `GET ${BACKEND_PUBLIC_URL}/api/health`
- Via proxy: `GET https://${FRONTEND_DOMAIN}/api/proxy/api/health`

What this does:
- Validates connectivity and identity token-based auth between frontend and backend.

### 13) reCAPTCHA v3 (classic) setup

This project supports Google reCAPTCHA v3 (classic) for the frontend. The frontend loads the appropriate script based on `NEXT_PUBLIC_RECAPTCHA_PROVIDER`. The helper will call `grecaptcha.execute(siteKey, { action })` and your backend should verify the token.

Frontend environment variables:

```bash
# Classic v3 (client-side only)
NEXT_PUBLIC_RECAPTCHA_PROVIDER=classic
NEXT_PUBLIC_RECAPTCHA_SITE_KEY="<your-v3-classic-site-key>"
```

Local development:

1) In `frontend/.env.local` add:

```bash
NEXT_PUBLIC_RECAPTCHA_PROVIDER=classic
NEXT_PUBLIC_RECAPTCHA_SITE_KEY=<your_v3_site_key>
```

2) Restart `next dev`.

Cloud Run (frontend):

```bash
gcloud run services update "$FRONTEND_SERVICE" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --set-env-vars NEXT_PUBLIC_RECAPTCHA_PROVIDER=classic,NEXT_PUBLIC_RECAPTCHA_SITE_KEY=<your_v3_site_key>
```

Backend verification (recommended):

The frontend sends the token (e.g., `recaptcha_token` + `recaptcha_action`) to your backend. On the backend, verify it using your secret key:

```bash
# Store secret on backend Cloud Run service (do not expose to frontend)
gcloud run services update "$BACKEND_SERVICE" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --set-env-vars RECAPTCHA_SECRET=<your_v3_secret>
```

Then, server-side, call Google verify API:

```
POST https://www.google.com/recaptcha/api/siteverify
  -d secret=<RECAPTCHA_SECRET>
  -d response=<token_from_client>
  -d remoteip=<optional_user_ip>
```

Accept the request only if `success === true` and (optionally) `score >= 0.5` and `action` matches your expected action.

reCAPTCHA Console configuration:

- Create a v3 site (classic) and add allowed domains (production + staging + `localhost`).
- Use the Site key in `NEXT_PUBLIC_RECAPTCHA_SITE_KEY`.
- Keep the Secret key private on the backend only.

Troubleshooting:

- “Missing NEXT_PUBLIC_RECAPTCHA_SITE_KEY”: Set the env var on the frontend service or in `.env.local`.
- Using v2 key with v3 code will fail; ensure the site is v3 classic.
- Token fails verification in prod: confirm the prod domain is listed in the reCAPTCHA console allowed domains.

---

This setup ensures:
- No long-lived service account keys are stored in CI (WIF-only).
- Frontend proxies calls to backend with Cloud Run IAM identity tokens using a consistent audience.
- CI installs Python deps without committing a lockfile, with caching for speed.

