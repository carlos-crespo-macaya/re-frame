"""ConfigCat feature flags integration for gradual rollout of features."""

import os
from typing import Any

import configcatclient
from pydantic import BaseModel

from src.utils.logging import get_logger

logger = get_logger(__name__)


class FeatureFlagError(Exception):
    """Custom exception for feature flag related errors."""

    pass


class FeatureFlagResponse(BaseModel):
    """Response model for feature flags."""

    flags: dict[str, bool]
    error: str | None = None


class ConfigCatClient:
    """Wrapper around ConfigCat client for feature flag management."""

    def __init__(self, sdk_key: str | None):
        """Initialize ConfigCat client with SDK key."""
        if not sdk_key:
            raise FeatureFlagError("ConfigCat SDK key not provided")

        self._client = configcatclient.get(sdk_key)
        logger.info("configcat_client_initialized")

    def get_all_flags(
        self, user_context: dict[str, Any] | None = None
    ) -> dict[str, bool]:
        """Get all feature flags evaluated for the user."""
        try:
            result = self._client.get_all_values(user_context)
            return dict(result) if result else {}
        except Exception as e:
            logger.error(
                "configcat_get_all_flags_failed",
                error=str(e),
                user_context=user_context,
            )
            raise FeatureFlagError(f"Failed to fetch feature flags: {e!s}") from e

    def get_flag_value(
        self,
        flag_name: str,
        default_value: bool = False,
        user_context: dict[str, Any] | None = None,
    ) -> bool:
        """Get a single feature flag value."""
        try:
            result = self._client.get_value(flag_name, default_value, user_context)
            return bool(result)
        except Exception as e:
            logger.error(
                "configcat_get_flag_failed",
                flag=flag_name,
                error=str(e),
                user_context=user_context,
            )
            return default_value

    def close(self):
        """Close the ConfigCat client."""
        if self._client:
            self._client.close()
            logger.info("configcat_client_closed")


class ConfigCatFeatureFlags:
    """ConfigCat-based feature flag management system."""

    # Default feature flag values (used when ConfigCat is unavailable)
    DEFAULT_FLAGS = {
        "text_mode_enabled": True,
        "voice_mode_enabled": True,
        "language_en": True,
        "language_es": True,
        "language_pt": True,
        "language_fr": True,
        "language_de": True,
        "language_it": True,
        "language_nl": True,
        "language_pl": True,
        "language_uk": True,
        "language_cs": True,
    }

    def __init__(self):
        """Initialize ConfigCat client."""
        self.client: ConfigCatClient | None = None
        self._fallback_mode = False

        sdk_key = os.getenv("CONFIGCAT_SDK_KEY")
        if not sdk_key:
            logger.warning(
                "configcat_sdk_key_missing",
                message="No ConfigCat SDK key found, using fallback mode with defaults",
            )
            self._fallback_mode = True
            return

        try:
            self.client = ConfigCatClient(sdk_key)
            logger.info("configcat_client_initialized")
        except Exception as e:
            logger.error(
                "configcat_initialization_failed",
                error=str(e),
                message="Failed to initialize ConfigCat client, using fallback mode",
            )
            self._fallback_mode = True

    def is_enabled(self, flag_name: str, user: dict[str, Any] | None = None) -> bool:
        """
        Evaluate feature flag for given user context.

        Args:
            flag_name: Name of the feature flag
            user: Optional user context for targeting

        Returns:
            Boolean indicating if feature is enabled
        """
        if self._fallback_mode or not self.client:
            # Use default values in fallback mode
            return self.DEFAULT_FLAGS.get(flag_name, False)

        # Use client's get_flag_value which handles errors gracefully
        default_value = self.DEFAULT_FLAGS.get(flag_name, False)
        return self.client.get_flag_value(flag_name, default_value, user)

    def get_all_flags(self, user: dict[str, Any] | None = None) -> dict[str, bool]:
        """
        Get all feature flags evaluated for the given user.

        Args:
            user: Optional user context for targeting

        Returns:
            Dictionary of all feature flags and their values
        """
        flags = {}

        # Evaluate all known flags
        for flag_name in self.DEFAULT_FLAGS:
            flags[flag_name] = self.is_enabled(flag_name, user)

        # Log evaluated flags
        logger.info(
            "feature_flags_evaluated",
            flags=flags,
            user_id=user.get("identifier") if user else None,
            fallback_mode=self._fallback_mode,
        )

        return flags

    def get_enabled_languages(self, user: dict[str, Any] | None = None) -> list[str]:
        """
        Get list of enabled languages based on feature flags.

        Args:
            user: Optional user context for targeting

        Returns:
            List of enabled language codes
        """
        language_map = {
            "language_en": "en",
            "language_es": "es",
            "language_pt": "pt",
            "language_fr": "fr",
            "language_de": "de",
            "language_it": "it",
            "language_nl": "nl",
            "language_pl": "pl",
            "language_uk": "uk",
            "language_cs": "cs",
        }

        enabled_languages = []
        for flag_name, lang_code in language_map.items():
            if self.is_enabled(flag_name, user):
                enabled_languages.append(lang_code)

        return enabled_languages

    def get_enabled_modes(self, user: dict[str, Any] | None = None) -> dict[str, bool]:
        """
        Get enabled communication modes.

        Args:
            user: Optional user context for targeting

        Returns:
            Dictionary with text_enabled and voice_enabled flags
        """
        return {
            "text_enabled": self.is_enabled("text_mode_enabled", user),
            "voice_enabled": self.is_enabled("voice_mode_enabled", user),
        }

    def close(self):
        """Close ConfigCat client connection."""
        if self.client:
            self.client.close()
            logger.info("configcat_client_closed")


# Singleton instance
_configcat_client: ConfigCatClient | None = None
_configcat_flags: ConfigCatFeatureFlags | None = None


def get_configcat_client() -> ConfigCatClient | None:
    """Get the singleton ConfigCat client instance."""
    global _configcat_client
    if _configcat_client is None:
        sdk_key = os.getenv("CONFIGCAT_SDK_KEY")
        if sdk_key:
            try:
                _configcat_client = ConfigCatClient(sdk_key)
            except Exception as e:
                logger.error("configcat_client_init_failed", error=str(e))
                return None
    return _configcat_client


def get_feature_flags(
    user_context: dict[str, Any] | None = None,
) -> FeatureFlagResponse:
    """Get all feature flags with error handling."""
    client = get_configcat_client()

    # Default values for backward compatibility
    default_flags = {
        "text_mode_enabled": True,
        "voice_mode_enabled": True,
        "language_en": True,
        "language_es": True,
        "language_pt": True,
        "language_fr": True,
        "language_de": True,
        "language_it": True,
        "language_nl": True,
        "language_pl": True,
        "language_uk": True,
        "language_cs": True,
    }

    if not client:
        return FeatureFlagResponse(
            flags=default_flags, error="ConfigCat not configured"
        )

    try:
        flags = client.get_all_flags(user_context)
        return FeatureFlagResponse(flags=flags)
    except FeatureFlagError as e:
        return FeatureFlagResponse(flags=default_flags, error=str(e))


def get_configcat_flags() -> ConfigCatFeatureFlags:
    """Get the singleton ConfigCat feature flags instance."""
    global _configcat_flags
    if _configcat_flags is None:
        _configcat_flags = ConfigCatFeatureFlags()
    return _configcat_flags


def is_feature_enabled(flag_name: str, user: dict[str, Any] | None = None) -> bool:
    """Convenience function to check if a feature is enabled."""
    return get_configcat_flags().is_enabled(flag_name, user)


def get_enabled_languages(user: dict[str, Any] | None = None) -> list[str]:
    """Convenience function to get enabled languages."""
    return get_configcat_flags().get_enabled_languages(user)


def get_enabled_modes(user: dict[str, Any] | None = None) -> dict[str, bool]:
    """Convenience function to get enabled modes."""
    return get_configcat_flags().get_enabled_modes(user)
