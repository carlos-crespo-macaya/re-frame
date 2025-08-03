"""Feature flags protocols and interfaces."""

from abc import ABC, abstractmethod

from .models import FeatureFlagKey, FeatureFlags


class FeatureFlagService(ABC):
    """Interface for feature flag services."""

    @abstractmethod
    def get_ui_flags(self) -> FeatureFlags:
        """Get all UI feature flags."""
        ...

    @abstractmethod
    def is_enabled(self, flag: FeatureFlagKey) -> bool:
        """Check if a specific flag is enabled."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Clean up resources."""
        ...
