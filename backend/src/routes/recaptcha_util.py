import os

import httpx
from google.cloud import recaptchaenterprise_v1 as recaptcha

PROVIDER = os.environ.get("RECAPTCHA_PROVIDER", "enterprise").lower()
PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY", "")  # Enterprise site key ID
SECRET = os.environ.get("RECAPTCHA_SECRET", "")  # Classic v3/v2 secret (if used)


def verify_recaptcha(token: str, action: str = "submit_feedback") -> float:
    """Validate a reCAPTCHA token and return a risk score in [0,1].

    - Enterprise path uses ADC (no server secret) and validates action.
    - Classic path (v3/v2) posts to siteverify using SECRET; returns score (v3) or 0.9 if success (v2).
    """
    if PROVIDER == "enterprise":
        if not (PROJECT and SITE_KEY):
            return 0.0
        client = recaptcha.RecaptchaEnterpriseServiceClient()
        parent = f"projects/{PROJECT}"
        event = recaptcha.Event(token=token, site_key=SITE_KEY)
        req = recaptcha.CreateAssessmentRequest(
            parent=parent, assessment=recaptcha.Assessment(event=event)
        )
        resp = client.create_assessment(request=req)
        if not (
            resp.token_properties.valid
            and (resp.token_properties.action or action) == action
        ):
            return 0.0
        return float(resp.risk_analysis.score or 0.0)

    # Classic path
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
    if "action" in data and data.get("action") != action:
        return 0.0
    return float(data.get("score", 0.9))
