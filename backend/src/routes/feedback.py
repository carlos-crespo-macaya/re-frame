import os

from fastapi import APIRouter, Header, HTTPException
from fastapi.concurrency import run_in_threadpool
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
        database_id = (
            os.getenv("FIRESTORE_DATABASE_ID") or os.getenv("FIRESTORE_DB") or "reframe"
        )
        _db_client = firestore.Client(project=project, database=database_id)
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
    comment: str | None = None
    recaptcha_token: str
    recaptcha_action: str = "submit_feedback"


@router.post("/feedback")
async def post_feedback(
    body: FeedbackIn, x_observability_opt_in: str | None = Header(default=None)
):
    try:
        score = await run_in_threadpool(
            verify_recaptcha, body.recaptcha_token, body.recaptcha_action
        )
    except Exception as err:
        # Treat provider/network/auth outages as temporary service issues
        raise HTTPException(status_code=503, detail="recaptcha_unavailable") from err
    if score < 0.5:
        raise HTTPException(status_code=400, detail="recaptcha_low_score")

    # Normalize optional free text (truncate to prevent abuse)
    normalized_comment = (body.comment or "").strip()
    if len(normalized_comment) > 1000:
        normalized_comment = normalized_comment[:1000]

    doc = {
        "helpful": body.helpful,
        "reasons": [r for r in body.reasons if r in ALLOWED_REASONS],
        "session_id": (body.session_id or "none")[:64],
        "lang": body.lang or "unknown",
        "platform": body.platform or "unknown",
        "opt_in_observability": x_observability_opt_in == "1",
        "comment": normalized_comment or None,
    }

    client = get_db_client()
    if client is not None:
        client.collection("feedback_v1").add(doc)
        logger.info("feedback_received", **doc)
    else:
        logger.info("feedback_received_noop", **doc)
    return {"ok": True}
