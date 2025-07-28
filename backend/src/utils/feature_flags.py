"""Feature flag management for gradual rollout of new features."""

import os

from src.utils.logging import get_logger

logger = get_logger(__name__)


class FeatureFlags:
    """Simple feature flag management system."""

    def __init__(self):
        self._flags: dict[str, bool] = {}
        self._load_from_env()

    def _load_from_env(self):
        """Load feature flags from environment variables."""
        # Reactive greeting feature flag
        self._flags["reactive_greeting"] = os.getenv(
            "FEATURE_REACTIVE_GREETING", "false"
        ).lower() in ("true", "1", "yes", "on")

        # Log loaded flags
        logger.info("feature_flags_loaded", flags=self._flags)

    def is_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled."""
        return self._flags.get(flag_name, False)

    def set_flag(self, flag_name: str, enabled: bool):
        """Set a feature flag value (for testing)."""
        self._flags[flag_name] = enabled
        logger.info(
            "feature_flag_updated",
            flag=flag_name,
            enabled=enabled,
        )

    def get_all_flags(self) -> dict[str, bool]:
        """Get all feature flags and their states."""
        return self._flags.copy()


# Singleton instance
_feature_flags: FeatureFlags | None = None


def get_feature_flags() -> FeatureFlags:
    """Get the singleton feature flags instance."""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags()
    return _feature_flags


def is_feature_enabled(flag_name: str) -> bool:
    """Convenience function to check if a feature is enabled."""
    return get_feature_flags().is_enabled(flag_name)
