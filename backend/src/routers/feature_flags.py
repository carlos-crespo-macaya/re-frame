"""Feature flags API router."""

from typing import Any

from fastapi import APIRouter, Header, Response
from pydantic import BaseModel

from src.utils.configcat_flags import get_configcat_flags
from src.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/feature-flags", tags=["feature-flags"])


class FeatureFlagsResponse(BaseModel):
    """Response model for feature flags endpoint."""

    textModeEnabled: bool  # noqa: N815
    voiceModeEnabled: bool  # noqa: N815
    enabledLanguages: list[str]  # noqa: N815


def get_user_context(
    session_id: str | None = Header(None, alias="X-Session-ID"),
    user_language: str | None = Header(None, alias="X-User-Language"),
    user_country: str | None = Header(None, alias="X-User-Country"),
) -> dict | None:
    """
    Extract user context from request headers.

    Args:
        session_id: Session identifier
        user_language: User's preferred language
        user_country: User's country code

    Returns:
        User context dictionary for ConfigCat targeting
    """
    if not session_id:
        return None

    user_context: dict[str, Any] = {"identifier": session_id, "custom": {}}

    if user_language:
        user_context["custom"]["language"] = user_language

    if user_country:
        user_context["custom"]["country"] = user_country

    return user_context


@router.get("/", response_model=FeatureFlagsResponse)
async def get_feature_flags(
    response: Response,
    user_context: dict | None = None,
    session_id: str | None = Header(None, alias="X-Session-ID"),
    user_language: str | None = Header(None, alias="X-User-Language"),
    user_country: str | None = Header(None, alias="X-User-Country"),
) -> FeatureFlagsResponse:
    """
    Get all feature flags evaluated for the current user.

    Returns:
    - textModeEnabled: Whether text mode is enabled
    - voiceModeEnabled: Whether voice mode is enabled
    - enabledLanguages: List of enabled language codes
    """
    try:
        # Build user context for targeting
        if not user_context:
            user_context = get_user_context(session_id, user_language, user_country)

        # Get feature flags instance
        flags_service = get_configcat_flags()

        # Evaluate all flags
        _ = flags_service.get_all_flags(user_context)  # Evaluate for logging
        enabled_modes = flags_service.get_enabled_modes(user_context)
        enabled_languages = flags_service.get_enabled_languages(user_context)

        # Set cache headers (60 seconds to match ConfigCat polling interval)
        response.headers["Cache-Control"] = "private, max-age=60"

        return FeatureFlagsResponse(
            textModeEnabled=enabled_modes.get("text_enabled", True),
            voiceModeEnabled=enabled_modes.get("voice_enabled", True),
            enabledLanguages=enabled_languages,
        )

    except Exception as e:
        logger.error("feature_flags_api_error", error=str(e), session_id=session_id)

        # Return defaults on error
        response.headers["Cache-Control"] = "private, max-age=60"

        return FeatureFlagsResponse(
            textModeEnabled=True,
            voiceModeEnabled=True,
            enabledLanguages=[
                "en",
                "es",
                "pt",
                "fr",
                "de",
                "it",
                "nl",
                "pl",
                "uk",
                "cs",
            ],
        )
