"""Feature flag service implementation with ConfigCat integration."""

from typing import Any

from src.utils.logging import get_logger

from .models import FeatureFlagConfig, FeatureFlagKey, FeatureFlags
from .protocols import FeatureFlagService

logger = get_logger(__name__)


class FeatureFlagServiceImpl(FeatureFlagService):
    """Feature flag service with ConfigCat integration and automatic fallbacks."""

    def __init__(self, config: FeatureFlagConfig, client_factory: Any | None = None):
        """Initialize the service.

        Args:
            config: Feature flag configuration.
            client_factory: Optional factory for creating ConfigCat clients (for testing).
        """
        self.config = config
        self._client = None
        self._init_configcat_client(client_factory)

    def _init_configcat_client(self, client_factory: Any | None = None) -> None:
        """Initialize ConfigCat client if possible."""
        if not self.config.sdk_key:
            logger.warning("ConfigCat SDK key is missing, will use fallback values")
            return

        try:
            if client_factory:
                # Use provided factory (for testing)
                self._client = client_factory.get(self.config.sdk_key)
            else:
                # Try to load ConfigCat SDK
                self._client = self._load_configcat_client()
        except Exception as e:
            logger.error("Failed to initialize ConfigCat client", error=str(e))

    def _load_configcat_client(self) -> Any | None:
        """Load ConfigCat client from SDK."""
        try:
            from configcatclient.configcatclient import ConfigCatClient

            return ConfigCatClient.get(self.config.sdk_key)
        except ImportError:
            logger.warning("ConfigCat SDK not available, using fallback values")
            return None
        except Exception as e:
            logger.error("Failed to load ConfigCat SDK", error=str(e))
            return None

    def get_ui_flags(self) -> FeatureFlags:
        """Get all UI feature flags with automatic fallback."""
        # Try ConfigCat first
        if self._client:
            try:
                flags_data = {}
                for flag_key in FeatureFlagKey:
                    default_value = self._get_default_value(flag_key)
                    flags_data[flag_key] = self._get_flag_from_client(
                        flag_key, default_value
                    )

                return FeatureFlags.from_dict(flags_data)
            except Exception as e:
                logger.warning("ConfigCat failed, using fallback values", error=str(e))

        # Fallback to defaults
        return FeatureFlags.defaults()

    def is_enabled(self, flag: FeatureFlagKey) -> bool:
        """Check if a specific flag is enabled."""
        try:
            if self._client:
                default_value = self._get_default_value(flag)
                return self._get_flag_from_client(flag, default_value)
        except Exception as e:
            logger.warning(
                "Failed to get flag, using default", flag=flag.value, error=str(e)
            )

        # Return default value
        return self._get_default_value(flag)

    def _get_flag_from_client(self, flag: FeatureFlagKey, default: bool) -> bool:
        """Get flag value from ConfigCat client."""
        if not self._client:
            return default

        if not hasattr(self._client, "get_value"):
            return default

        value = self._client.get_value(flag.value, default)

        if self.config.log_flag_access:
            logger.info("Feature flag accessed", flag=flag.value, value=value)

        return bool(value)

    def _get_default_value(self, flag: FeatureFlagKey) -> bool:
        """Get the default value for a flag."""
        defaults = {
            FeatureFlagKey.CHAT_MODE_ENABLED: True,
            FeatureFlagKey.VOICE_MODE_ENABLED: False,
            FeatureFlagKey.NOTEPAD_MODE_ENABLED: False,
        }
        return defaults.get(flag, False)

    def close(self) -> None:
        """Clean up resources."""
        if self._client and hasattr(self._client, "close"):
            try:
                self._client.close()
            except Exception as e:
                logger.warning("Failed to close ConfigCat client", error=str(e))


def create_feature_flag_service(
    config: FeatureFlagConfig | None = None,
    client_factory: Any | None = None,
) -> FeatureFlagService:
    """Create a feature flag service instance.

    Args:
        config: Configuration for the service. If None, loads from environment.
        client_factory: Optional factory for creating ConfigCat clients (for testing).

    Returns:
        A configured FeatureFlagService instance.
    """
    if config is None:
        config = FeatureFlagConfig.from_environment()

    return FeatureFlagServiceImpl(config, client_factory)
