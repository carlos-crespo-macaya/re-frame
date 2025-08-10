import importlib
import os
from typing import Final

# Classic reCAPTCHA (v3 preferred) only
RECAPTCHA_VERIFY_URL: Final[str] = "https://www.google.com/recaptcha/api/siteverify"
SECRET: Final[str] = os.environ.get("RECAPTCHA_SECRET", "")


def verify_recaptcha(token: str, action: str = "submit_feedback") -> float:
    """Validate a Classic reCAPTCHA token and return a risk score in [0,1].

    - For v3: returns the provider score on success, 0.0 on failure
    - For v2: Google does not return a score; treat success as 0.9
    - If misconfigured (missing secret), raise to allow caller to return 503
    """
    if not (SECRET and token):
        raise RuntimeError("recaptcha_classic_misconfigured")

    httpx = importlib.import_module("httpx")
    resp = httpx.post(
        RECAPTCHA_VERIFY_URL,
        data={"secret": SECRET, "response": token},
        timeout=10,
    )
    data = resp.json()

    if not data.get("success"):
        return 0.0

    # If action is present (v3), validate it
    if "action" in data and data.get("action") != action:
        return 0.0

    # v3 provides score; v2 does not
    return float(data.get("score", 0.9))
