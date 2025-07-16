"""
Ultra‑light, single‑call intent classification to keep the agentic graph smooth.
"""
from functools import lru_cache
# Local import – keep fully-qualified to avoid issues with ``PYTHONPATH``
from src.models.gemini_client import gemini_call

PROMPT = """Classify the user's sentence into one of these labels:
1. clarification_request – user wants to go back or explain more
2. continue             – user is happy to proceed

Return only the label.
Sentence: "{sentence}" =>"""

@lru_cache(maxsize=256)
def classify_intent(sentence: str) -> str:
    resp = gemini_call(PROMPT.format(sentence=sentence), temperature=0.0)
    return "clarification_request" if "clarification" in resp.lower() else "continue"
