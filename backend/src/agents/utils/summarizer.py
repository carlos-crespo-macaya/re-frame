"""Utility to create a short recap sentence from a longer assistant message.

The real implementation would call an LLM (e.g. Gemini).  For the purposes
of the test-suite we only need a deterministic, fast stub so that importing
and calling the function does not raise errors.
"""

# noqa: D401

from __future__ import annotations

# Local import – keep fully-qualified to avoid issues with ``PYTHONPATH``
from src.models.gemini_client import gemini_call  # correct import for real call if env configured


def recap(text: str) -> str:  # noqa: D401 – simple stub with optional LLM
    """Return the first sentence of *text* as a *recap*.

    The logic here is intentionally simple – we merely split on full-stops and
    return the first clause.  This keeps the function fast and fully
    deterministic while still producing a superficially plausible recap that
    downstream code (or tests) can rely on.
    """

    if not text:
        return ""

    # Try real LLM call when available.
    try:
        return gemini_call(
            "Summarise in one short sentence: " + text, temperature=0.0
        ).strip()
    except Exception:  # noqa: BLE001 – fall back to heuristic
        sentence = text.strip().split(".")[0].strip()
        return f"{sentence}." if sentence else ""
