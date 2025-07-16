"""Very lightweight ASR *enhancement* endpoint stub.

The original patch suggests calling Google Cloud Speech-to-Text to refine
partial browser transcripts.  For local development and unit-testing we avoid
external dependencies and simply echo the provided partial back unchanged –
the contract remains identical so that the front-end integration works.
"""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class _Req(BaseModel):
    partial: str


@router.post("/enhance_asr")
async def enhance(req: _Req):  # noqa: D401 – FastAPI view
    """Return the (stub-) *enhanced* transcript of the partial ASR result."""

    # In a real implementation we would invoke Cloud Speech-to-Text here.
    # For the purposes of offline testing we consider the incoming partial to
    # already be the *best* transcript.
    return {"transcript": req.partial}
