import os

from fastapi import APIRouter, Header, HTTPException
from google.cloud import firestore  # type: ignore[attr-defined]
from pydantic import BaseModel, Field

from src.utils.logging import get_logger

from .recaptcha_util import verify_recaptcha

router = APIRouter(prefix="/api")
logger = get_logger(__name__)

ALLOWED_REASONS = {"too_fast", "too_slow", "confusing", "not_relevant"}

_db_client: firestore.Client | None = None


def get_db_client() -> firestore.Client | None:
    global _db_client
    if _db_client is not None:
        return _db_client
    try:
        project = os.getenv("GOOGLE_CLOUD_PROJECT") or None
        _db_client = firestore.Client(project=project)
    except Exception as exc:
        logger.warning("firestore_client_unavailable", error=str(exc))
        _db_client = None
    return _db_client


class FeedbackIn(BaseModel):
    helpful: bool
    reasons: list[str] = Field(default_factory=list)
    session_id: str | None = None
    lang: str | None = None
    platform: str | None = None
    recaptcha_token: str
    recaptcha_action: str = "submit_feedback"


@router.post("/feedback")
async def post_feedback(
    body: FeedbackIn, x_observability_opt_in: str | None = Header(default=None)
):
    score = verify_recaptcha(token=body.recaptcha_token, action=body.recaptcha_action)
    if score < 0.5:
        raise HTTPException(status_code=400, detail="recaptcha_low_score")

    doc = {
        "helpful": body.helpful,
        "reasons": [r for r in body.reasons if r in ALLOWED_REASONS],
        "session_id": (body.session_id or "none")[:64],
        "lang": body.lang or "unknown",
        "platform": body.platform or "unknown",
        "opt_in_observability": x_observability_opt_in == "1",
    }

    client = get_db_client()
    if client is not None:
        client.collection("feedback_v1").add(doc)
        logger.info("feedback_received", **doc)
    else:
        logger.info("feedback_received_noop", **doc)
    return {"ok": True}
