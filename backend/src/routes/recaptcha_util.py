import os
from typing import Final

import httpx

# Classic reCAPTCHA (v3 preferred) only
RECAPTCHA_VERIFY_URL: Final[str] = "https://www.google.com/recaptcha/api/siteverify"
SECRET: Final[str] = os.environ.get("RECAPTCHA_SECRET", "")


def verify_recaptcha(token: str, action: str = "submit_feedback") -> float:
    """Validate a Classic reCAPTCHA token and return a risk score in [0,1].

    - For v3: returns the provider score on success, 0.0 on failure
    - For v2: Google does not return a score; treat success as 0.9
    - If misconfigured (missing secret), raise to allow caller to return 503
    """
    if not SECRET:
        raise RuntimeError("recaptcha_classic_misconfigured")
    if not token:
        return 0.0

    try:
        resp = httpx.post(
            RECAPTCHA_VERIFY_URL,
            data={"secret": SECRET, "response": token},
            timeout=httpx.Timeout(10.0, connect=3.0),
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.TimeoutException:
        return 0.0
    except httpx.HTTPError:
        return 0.0
    except ValueError:
        # JSON parse error
        return 0.0

    if not data.get("success"):
        return 0.0

    # If action is present (v3), validate it
    if "action" in data and data.get("action") != action:
        return 0.0

    # v3 provides score; v2 does not
    return float(data.get("score", 0.9))
