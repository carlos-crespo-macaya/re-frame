"""Feature flags domain models and configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum


class FeatureFlagKey(Enum):
    """Available feature flags."""

    CHAT_MODE_ENABLED = "chat_mode_enabled"
    VOICE_MODE_ENABLED = "voice_mode_enabled"
    NOTEPAD_MODE_ENABLED = "notepad_mode_enabled"


@dataclass(frozen=True)
class FeatureFlags:
    """UI feature flags data model."""

    chat_mode_enabled: bool = True
    voice_mode_enabled: bool = False
    notepad_mode_enabled: bool = False

    @classmethod
    def defaults(cls) -> FeatureFlags:
        """Create FeatureFlags with safe default values."""
        return cls()

    @classmethod
    def from_dict(cls, data: dict[FeatureFlagKey, bool]) -> FeatureFlags:
        """Create FeatureFlags from a dictionary."""
        return cls(
            chat_mode_enabled=data.get(FeatureFlagKey.CHAT_MODE_ENABLED, True),
            voice_mode_enabled=data.get(FeatureFlagKey.VOICE_MODE_ENABLED, False),
            notepad_mode_enabled=data.get(FeatureFlagREDACTED, False),
        )

    def to_dict(self) -> dict[str, bool]:
        """Convert to dictionary for API responses."""
        return {
            "chat_mode_enabled": self.chat_mode_enabled,
            "voice_mode_enabled": self.voice_mode_enabled,
            "notepad_mode_enabled": self.notepad_mode_enabled,
        }


@dataclass(frozen=True)
class FeatureFlagConfig:
    """Configuration for feature flags."""

    sdk_key: str = ""
    timeout_seconds: float = 5.0
    enable_caching: bool = True
    log_flag_access: bool = False

    @classmethod
    def from_environment(cls) -> FeatureFlagConfig:
        """Create configuration from environment variables.

        Environment variables:
            FEATURE_FLAGS_SDK_KEY: Provider SDK key
            FEATURE_FLAGS_TIMEOUT: Timeout in seconds (default: 5.0)
            FEATURE_FLAGS_CACHE: Enable caching (default: true)
            FEATURE_FLAGS_LOG_ACCESS: Log flag access (default: false)
        """
        return cls(
            sdk_key=os.getenv(
                "FEATURE_FLAGS_SDK_KEY", os.getenv("CONFIGCAT_SDK_KEY", "")
            ),
            timeout_seconds=float(os.getenv("FEATURE_FLAGS_TIMEOUT", "5.0")),
            enable_caching=_parse_bool(os.getenv("FEATURE_FLAGS_CACHE", "true")),
            log_flag_access=_parse_bool(os.getenv("FEATURE_FLAGS_LOG_ACCESS", "false")),
        )


def _parse_bool(value: str) -> bool:
    """Parse a string as a boolean value."""
    return value.lower() in ("true", "1", "yes", "on")
