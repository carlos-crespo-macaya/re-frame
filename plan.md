# PR: Observability (Cloud Logging) + Anonymous Feedback (Firestore + reCAPTCHA) — **ship today**

This PR adds **metadata‑only observability** using **Cloud Logging**, an **anonymous feedback** endpoint backed by **Firestore**, and basic **privacy/terms** pages in the frontend. All components are **GCP‑native** and require no third‑party services.

> Assumes: Next.js frontend (`frontend/`) + FastAPI backend (`backend/src/main.py`).

---

## 1) Backend changes (FastAPI)

### 1.1 New: structured, PII‑free logging helper

**File:** `backend/src/utils/log.py`

```python
from google.cloud import logging as gcl
import hashlib, os

_client = gcl.Client()
_logger = _client.logger("backend_events")
_SALT = os.environ.get("OBS_SALT", "rotate-me")


def sha12(s: str) -> str:
    return hashlib.sha256((_SALT + (s or "")).encode()).hexdigest()[:12]


def log_event(event_type: str, **fields):
    # Allowlist only — avoid accidental PII leakage
    allow = {
        "phase",
        "model",
        "input_tokens_bucket",
        "output_tokens_bucket",
        "duration_ms_bucket",
        "route",
        "status",
        "error_code",
        "env",
        "platform",
        "session_hash",
        "opt_in_observability",
    }
    payload = {"event_type": event_type}
    payload.update({k: v for k, v in fields.items() if k in allow})
    _logger.log_struct(payload)
```

### 1.2 New: reCAPTCHA verification (Enterprise by default; classic fallback)

**File:** `backend/src/routes/recaptcha_util.py`

```python
import os
from typing import Optional

import httpx
from google.cloud import recaptchaenterprise_v1 as recaptcha

PROVIDER = os.environ.get("RECAPTCHA_PROVIDER", "enterprise").lower()
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "")  # Enterprise site key ID
SECRET = os.environ.get("RECAPTCHA_SECRET", "")      # Classic v3/v2 secret (if used)


def verify_recaptcha(token: str, action: str = "submit_feedback") -> float:
    """Return a risk score in [0,1]. 0 means reject.

    - Enterprise: uses ADC (no server secret), validates action, returns risk score.
    - Classic: calls https://www.google.com/recaptcha/api/siteverify; if success, use score if present (v3), else 0.9.
    """
    if PROVIDER == "enterprise":
        if not (PROJECT and SITE_KEY):
            return 0.0
        client = recaptcha.RecaptchaEnterpriseServiceClient()
        parent = f"projects/{PROJECT}"
        event = recaptcha.Event(token=token, site_key=SITE_KEY)
        req = recaptcha.CreateAssessmentRequest(parent=parent, assessment=recaptcha.Assessment(event=event))
        resp = client.create_assessment(request=req)
        if not (resp.token_properties.valid and resp.token_properties.action == action):
            return 0.0
        return float(resp.risk_analysis.score or 0.0)

    # Classic path (v3/v2)
    if not (SECRET and token):
        return 0.0
    r = httpx.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={"secret": SECRET, "response": token},
        timeout=10,
    )
    data = r.json()
    if not data.get("success"):
        return 0.0
    # v3 returns an action + score; v2 does not
    if "action" in data and data.get("action") != action:
        return 0.0
    return float(data.get("score", 0.9))
```

### 1.3 New: Anonymous feedback endpoint (Firestore + reCAPTCHA)

**File:** `backend/src/routes/feedback.py`

```python
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from google.cloud import firestore

from .recaptcha_util import verify_recaptcha
from utils.log import log_event, sha12

router = APIRouter(prefix="/api")
db = firestore.Client()

ALLOWED = {"too_fast", "too_slow", "confusing", "not_relevant"}


class FeedbackIn(BaseModel):
    helpful: bool
    reasons: list[str] = Field(default_factory=list)
    session_id: str | None = None
    lang: str | None = None
    platform: str | None = None
    recaptcha_token: str
    recaptcha_action: str = "submit_feedback"


@router.post("/feedback")
async def post_feedback(body: FeedbackIn, x_observability_opt_in: str | None = Header(default=None)):
    score = verify_recaptcha(token=body.recaptcha_token, action=body.recaptcha_action)
    if score < 0.5:
        raise HTTPException(status_code=400, detail="recaptcha_low_score")

    doc = {
        "helpful": body.helpful,
        "reasons": [r for r in body.reasons if r in ALLOWED],
        "session_hash": sha12(body.session_id or "none"),
        "lang": body.lang or "unknown",
        "platform": body.platform or "unknown",
        "opt_in_observability": x_observability_opt_in == "1",
    }

    db.collection("feedback_v1").add(doc)
    log_event("feedback", **doc)
    return {"ok": True}
```

### 1.4 New: routes package init

**File:** `backend/src/routes/__init__.py`

```python
# Makes the routes directory a package
```

### 1.5 Wire router into app

**Edit:** `backend/src/main.py` — add the import and include the router (adapt to your file):

```python
from routes.feedback import router as feedback_router

# After you create the FastAPI app instance `app = FastAPI(...)`:
app.include_router(feedback_router)
```

> If you already have a routers section, just add the `include_router` line there.

### 1.6 Backend dependencies

Update `backend` deps (using `uv`):

```bash
cd backend
uv add google-cloud-logging google-cloud-firestore google-cloud-recaptcha-enterprise httpx
```

---

## 2) Frontend changes (Next.js)

### 2.1 reCAPTCHA helper (Enterprise)

**File:** `frontend/lib/recaptcha.ts`

```ts
export async function executeRecaptcha(action: string, siteKey: string): Promise<string> {
  await new Promise<void>((resolve) => {
    if ((window as any).grecaptcha?.enterprise) return resolve();
    const s = document.createElement("script");
    s.src = "https://www.google.com/recaptcha/enterprise.js?render=" + siteKey;
    s.async = true; s.defer = true; s.onload = () => resolve();
    document.head.appendChild(s);
  });
  return await (window as any).grecaptcha.enterprise.execute(siteKey, { action });
}
```

### 2.2 Settings page with anonymous telemetry toggle + simple feedback

**File:** `frontend/app/settings/page.tsx`

```tsx
"use client";
import { useEffect, useState } from "react";
import { executeRecaptcha } from "@/lib/recaptcha";

const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY!;
const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || ""; // empty => same origin/proxy

export default function SettingsPage() {
  const [optIn, setOptIn] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    const v = localStorage.getItem("telemetry_opt_in");
    setOptIn(v === "true");
  }, []);

  function saveOptIn(v: boolean) {
    setOptIn(v);
    localStorage.setItem("telemetry_opt_in", v ? "true" : "false");
  }

  async function sendFeedback(helpful: boolean) {
    try {
      setSubmitting(true); setMsg(null);
      const token = await executeRecaptcha("submit_feedback", siteKey);
      const res = await fetch(`${API_BASE}/api/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(optIn ? { "X-Observability-Opt-In": "1" } : {}),
        },
        body: JSON.stringify({
          helpful,
          reasons: [],
          session_id: crypto.getRandomValues(new Uint32Array(1))[0].toString(16),
          lang: navigator.language.split("-")[0] || "en",
          platform: "web",
          recaptcha_token: token,
          recaptcha_action: "submit_feedback",
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setMsg("Thanks for the feedback!");
    } catch (e: any) {
      setMsg("Could not submit feedback. Please try later.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="max-w-2xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Settings</h1>

      <section className="p-4 rounded-xl border">
        <h2 className="text-lg font-medium mb-2">Help us improve anonymously</h2>
        <p className="text-sm text-gray-600 mb-3">
          We measure anonymous technical signals (timing, error rates). No message content is stored.
        </p>
        <label className="inline-flex items-center gap-3">
          <input type="checkbox" checked={optIn} onChange={(e) => saveOptIn(e.target.checked)} />
          <span>Enable anonymous telemetry</span>
        </label>
      </section>

      <section className="p-4 rounded-xl border">
        <h2 className="text-lg font-medium mb-2">Quick feedback</h2>
        <div className="flex gap-3">
          <button className="px-3 py-2 rounded bg-gray-200" disabled={submitting} onClick={() => sendFeedback(true)}>Yes</button>
          <button className="px-3 py-2 rounded bg-gray-200" disabled={submitting} onClick={() => sendFeedback(false)}>Not really</button>
        </div>
        {msg && <p className="mt-3 text-sm">{msg}</p>}
      </section>
    </main>
  );
}
```

### 2.3 Minimal privacy & terms pages

**File:** `frontend/app/privacy/page.tsx`

```tsx
export default function PrivacyPage() {
  return (
    <main className="prose mx-auto p-6">
      <h1>Privacy Policy</h1>
      <p>We measure anonymous technical signals (performance timing, model usage, error rates) to keep the service reliable. We do not store your message content by default. We remove or anonymize anything that could identify you. You can turn this measurement off any time in Settings.</p>
      <h2>Legal Basis</h2>
      <p>Legitimate interests (reliability & security). Consent applies to the optional anonymous telemetry toggle.</p>
      <h2>Retention</h2>
      <p>Observability logs: 30 days. Feedback: up to 6 months. Aggregated, non-personal statistics may be kept longer.</p>
      <h2>Processors</h2>
      <p>Google Cloud (Cloud Run, Logging/Monitoring/Trace, Firestore, Secret Manager) and reCAPTCHA Enterprise.</p>
      <h2>Contact</h2>
      <p>Data requests: hello@re-frame.social</p>
    </main>
  );
}
```

**File:** `frontend/app/terms/page.tsx`

```tsx
export default function TermsPage() {
  return (
    <main className="prose mx-auto p-6">
      <h1>Terms of Use</h1>
      <p>This app provides informational support and is not a substitute for professional medical advice. If you are in crisis, please contact your local emergency services.</p>
    </main>
  );
}
```

### 2.4 Frontend env

Add to your build/deploy env:

* `NEXT_PUBLIC_RECAPTCHA_SITE_KEY=<your enterprise site key>`
* (optional) `NEXT_PUBLIC_BACKEND_URL=https://api.re-frame.social`

---

## 3) GCP setup (one-time)

> Replace `$PROJECT` and `$REGION` as needed (assuming `europe-west1`). Service account is your backend’s Cloud Run SA: `reframe-backend@$PROJECT.iam.gserviceaccount.com`.

### 3.1 Enable APIs

```bash
gcloud services enable run.googleapis.com logging.googleapis.com monitoring.googleapis.com \
  secretmanager.googleapis.com firestore.googleapis.com recaptchaenterprise.googleapis.com
```

### 3.2 Firestore (Native)

Create Firestore **Native** in your region via Console (fastest) or CLI:

```bash
gcloud alpha firestore databases create --location=europe-west1 --type=firestore-native || true
```

Grant backend SA minimal access:

```bash
SA="reframe-backend@$PROJECT.iam.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/datastore.user"
```

### 3.3 Secret Manager (hash salt)

```bash
openssl rand -hex 32 | gcloud secrets create obs_salt --data-file=-
gcloud secrets add-iam-policy-binding obs_salt \
  --member="serviceAccount:$SA" --role="roles/secretmanager.secretAccessor"
```

### 3.4 reCAPTCHA Enterprise

* Console → **Security > reCAPTCHA Enterprise** → create a **site key** for your domains (dev + prod).
* Grant backend SA:

```bash
gcloud projects add-iam-policy-binding $PROJECT \
  --member="serviceAccount:$SA" --role="roles/recaptchaenterprise.agent"
```

### 3.5 Cloud Logging — dedicated bucket + sink (30‑day retention)

```bash
gcloud logging buckets create backend-anon --location=global --retention-days=30 || true

gcloud logging sinks create backendAnonSink \
  "logging.googleapis.com/projects/$PROJECT/locations/global/buckets/backend-anon" \
  --log-filter='logName:"backend_events" OR jsonPayload.event_type:*' || true
```

*(Optional)* add exclusion filters for any default HTTP payload logs in your project (via Console) — keep only our `backend_events` structured logs.

### 3.6 Deploy backend (Cloud Run)

```bash
gcloud run deploy re-frame-backend \
  --image gcr.io/$PROJECT/reframe-backend:prod \
  --region europe-west1 \
  --service-account $SA \
  --set-env-vars ENV=prod,GOOGLE_CLOUD_PROJECT=$PROJECT,RECAPTCHA_PROVIDER=enterprise,RECAPTCHA_SITE_KEY=<SITE_KEY> \
  --set-secrets "OBS_SALT=obs_salt:latest"
```

> If you decide to use **classic** reCAPTCHA v3/v2 instead: create a Secret `recaptcha_secret`, grant accessor to `$SA`, and add `--set-secrets "RECAPTCHA_SECRET=recaptcha_secret:latest"` with `RECAPTCHA_PROVIDER=classic`.

### 3.7 Frontend — env at build time

Ensure `NEXT_PUBLIC_RECAPTCHA_SITE_KEY` is available at **build** (Next.js inlines it): build the image with the arg, or set the env before `next build`. If you deploy an already‑built image, re‑build with this env.

---

## 4) Minimal GDPR copy (already included on `/privacy`)

* **Observability & Monitoring:** Anonymous technical signals only; no message content by default; off by default; user can opt in.
* **Legal Basis:** Legitimate interests; consent for the toggle.
* **Retention:** Logs 30 days; feedback up to 6 months.
* **Rights/Contact:** `hello@re-frame.social`.

---

## 5) Test plan

* **Feedback path**: submit from `/settings` → Firestore doc appears in `feedback_v1`, Cloud Logging shows `event_type=feedback` with no PII.
* **reCAPTCHA**: reject when `score < 0.5` (simulate by tampering token in DevTools).
* **No content leakage**: grep Logs Explorer for `jsonPayload` fields — should match allowlist only.

---


```
```
