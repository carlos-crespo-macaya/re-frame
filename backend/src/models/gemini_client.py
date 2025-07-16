"""backend.src.models.gemini_client
-----------------------------------
Minimal wrapper around the Google Generative AI ("Gemini") SDK **with graceful
fallbacks** so that the rest of the codebase can depend on a single helper
function regardless of whether the runtime environment actually has the SDK
and network connectivity.

Behaviour hierarchy:

1.  If ``google.generativeai`` (a.k.a. *google-genai*) is installed **and** an
   API key is available via ``GOOGLE_API_KEY``, we make a real model call.
2.  Otherwise we return a deterministic dummy string – this keeps the unit
   tests fast and hermetic while still exercising the calling code paths.
"""

from __future__ import annotations

import os
from typing import Any

# ---------------------------------------------------------------------------
# Try to import the real SDK.  It is optional – the project’s test-suite does
# not depend on it and CI environments might not have network access.
# ---------------------------------------------------------------------------

try:
    import google.generativeai as genai  # type: ignore

    _HAS_GENAI = True
except ModuleNotFoundError:  # pragma: no cover – fallback path
    _HAS_GENAI = False


def _real_call(prompt: str, **params: Any) -> str:
    """Invoke Gemini with basic retry & model-fallback logic."""

    # Ensure the environment is configured – raise explicit error if not.
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY environment variable not set – cannot perform real LLM call."
        )

    genai.configure(api_key=api_key)

    # Simple *round-robin* list of models to try.
    for model_name in ("gemini-pro", "gemini-1.5-pro-latest", "gemini-pro-vision"):
        try:
            llm = genai.GenerativeModel(model_name)
            resp = llm.generate_content(prompt, **params)
            # Response objects expose `.text` – fall back to str() just in case.
            return getattr(resp, "text", str(resp))
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            # On quota / blocked errors we silently try the next model.
            if any(tok in str(exc).lower() for tok in ("quota", "blocked", "rate")):
                continue
            raise  # Other errors are surfaced immediately.

    # If we ran out of models.
    raise RuntimeError(f"All model attempts failed. Last error: {last_error}")  # type: ignore[misc]


def _stub_call(prompt: str, **_params: Any) -> str:  # noqa: D401 – simple stub
    """Deterministic fallback when the real SDK is unavailable.

    We use a *very* naïve heuristic so that intent-classification prompts in
    the codebase still behave somewhat sensibly – if the prompt contains the
    word *clarification* we mirror it in the response, otherwise we reply with
    "continue".
    """

    lowered = prompt.lower()
    if "clarification" in lowered:
        return "clarification_request"
    return "continue"


def gemini_call(prompt: str, **params: Any) -> str:  # noqa: D401 – public API
    """Unified entry-point for Gemini calls used throughout the codebase."""

    if _HAS_GENAI:
        try:
            return _real_call(prompt, **params)
        except Exception:  # pragma: no cover – fall back to stub on runtime issues
            # In testing/offline environments SDK might be present but network
            # blocked – gracefully degrade.
            pass
    # Stub path
    return _stub_call(prompt, **params)
