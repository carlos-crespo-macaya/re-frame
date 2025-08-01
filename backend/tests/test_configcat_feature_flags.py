"""Tests for ConfigCat feature flags integration."""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.utils.configcat_flags import ConfigCatFeatureFlags


class TestConfigCatFeatureFlags:
    """Test suite for ConfigCat feature flags integration."""

    @pytest.fixture
    def mock_configcat_client(self):
        """Create a mock ConfigCat client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def feature_flags(self, mock_configcat_client):
        """Create a ConfigCatFeatureFlags instance with mocked client."""
        with (
            patch.dict(os.environ, {"CONFIGCAT_SDK_KEY": "test-sdk-key"}),
            patch("src.utils.configcat_flags.ConfigCatClient") as mock_client_class,
        ):
            mock_client_class.return_value = mock_configcat_client
            flags = ConfigCatFeatureFlags()
            return flags

    def test_configcat_client_initialization(self):
        """Test ConfigCat client is properly initialized with SDK key."""
        with (
            patch.dict(os.environ, {"CONFIGCAT_SDK_KEY": "test-sdk-key"}),
            patch("src.utils.configcat_flags.ConfigCatClient") as mock_client_class,
        ):
            ConfigCatFeatureFlags()
            mock_client_class.assert_called_once_with("test-sdk-key")

    def test_feature_flag_evaluation(self, feature_flags, mock_configcat_client):
        """Test feature flag evaluation returns expected values."""
        # Test text mode enabled
        mock_configcat_client.get_flag_value.return_value = True
        assert feature_flags.is_enabled("text_mode_enabled") is True
        mock_configcat_client.get_flag_value.assert_called_with(
            "text_mode_enabled", True, None
        )

        # Test voice mode disabled
        mock_configcat_client.get_flag_value.return_value = False
        assert feature_flags.is_enabled("voice_mode_enabled") is False

    def test_user_targeting(self, feature_flags, mock_configcat_client):
        """Test feature flags respect user attributes."""
        user_context = {
            "identifier": "user-123",
            "custom": {"session_id": "session-456", "language": "es"},
        }

        mock_configcat_client.get_flag_value.return_value = True
        result = feature_flags.is_enabled("language_es", user_context)

        assert result is True
        mock_configcat_client.get_flag_value.assert_called_with(
            "language_es", True, user_context
        )

    def test_fallback_on_error(self, mock_configcat_client):
        """Test system falls back gracefully when ConfigCat is unavailable."""
        # Simulate ConfigCat client error
        with patch("src.utils.configcat_flags.ConfigCatClient") as mock_client_class:
            mock_client_class.side_effect = Exception("Connection error")

            # Should not raise exception and use defaults
            flags = ConfigCatFeatureFlags()
            assert flags.is_enabled("text_mode_enabled") is True  # Default
            assert flags.is_enabled("voice_mode_enabled") is True  # Default

    def test_caching_behavior(self, feature_flags, mock_configcat_client):
        """Test flags are cached appropriately."""
        # ConfigCat client handles caching internally
        # Test that we're not adding extra caching layer
        mock_configcat_client.get_flag_value.return_value = True

        # Multiple calls should go through to client (client handles caching)
        for _ in range(3):
            feature_flags.is_enabled("text_mode_enabled")

        assert mock_configcat_client.get_flag_value.call_count == 3

    def test_get_all_flags(self, feature_flags, mock_configcat_client):
        """Test getting all feature flags for a user."""

        # Mock different values for different flags
        def mock_get_flag_value(flag_name, default, user):
            flag_values = {
                "text_mode_enabled": True,
                "voice_mode_enabled": True,
                "language_en": True,
                "language_es": False,
                "language_pt": False,
                "language_fr": False,
                "language_de": False,
                "language_it": False,
                "language_nl": False,
                "language_pl": False,
                "language_uk": False,
                "language_cs": False,
            }
            return flag_values.get(flag_name, default)

        mock_configcat_client.get_flag_value.side_effect = mock_get_flag_value

        all_flags = feature_flags.get_all_flags()

        assert all_flags["text_mode_enabled"] is True
        assert all_flags["voice_mode_enabled"] is True
        assert all_flags["language_en"] is True
        assert all_flags["language_es"] is False

    def test_feature_flags_with_missing_sdk_key(self):
        """Test behavior when SDK key is not provided."""
        with patch.dict(os.environ, {}, clear=True):
            flags = ConfigCatFeatureFlags()
            # Should use fallback mode with defaults
            assert flags.is_enabled("text_mode_enabled") is True
            assert flags.is_enabled("voice_mode_enabled") is True

    def test_language_flags(self, feature_flags, mock_configcat_client):
        """Test language-specific feature flags."""
        languages = ["en", "es", "pt", "fr", "de", "it", "nl", "pl", "uk", "cs"]

        for lang in languages:
            flag_name = f"language_{lang}"
            mock_configcat_client.get_flag_value.return_value = True
            assert feature_flags.is_enabled(flag_name) is True
            mock_configcat_client.get_flag_value.assert_called_with(
                flag_name, True, None
            )

    def test_configcat_singleton_pattern(self):
        """Test singleton pattern for ConfigCat feature flags."""
        from src.utils.configcat_flags import get_configcat_flags

        # Multiple calls should return the same instance
        flags1 = get_configcat_flags()
        flags2 = get_configcat_flags()

        assert flags1 is flags2

    def test_configcat_sdk_key_environment_variable(self):
        """Test that CONFIGCAT_SDK_KEY environment variable is used correctly."""
        test_sdk_key = "test-sdk-key-12345"

        with (
            patch.dict(os.environ, {"CONFIGCAT_SDK_KEY": test_sdk_key}),
            patch("src.utils.configcat_flags.ConfigCatClient") as mock_client_class,
        ):
            # Clear singleton to force reinitialization
            import src.utils.configcat_flags

            src.utils.configcat_flags._configcat_flags = None

            ConfigCatFeatureFlags()

            # Verify SDK key was passed to client
            mock_client_class.assert_called_once_with(test_sdk_key)

    def test_mode_flags_mutual_exclusivity(self, feature_flags, mock_configcat_client):
        """Test that mode flags can be configured for mutual exclusivity."""
        # Scenario 1: Both modes enabled (default)
        mock_configcat_client.get_flag_value.side_effect = (
            lambda flag, default, user: True
        )
        assert feature_flags.is_enabled("text_mode_enabled") is True
        assert feature_flags.is_enabled("voice_mode_enabled") is True

        # Scenario 2: Only text mode
        mock_configcat_client.get_flag_value.side_effect = lambda flag, default, user: (
            True if flag == "text_mode_enabled" else default
        )
        assert feature_flags.is_enabled("text_mode_enabled") is True
        assert (
            feature_flags.is_enabled("voice_mode_enabled") is True
        )  # Falls back to default

        # Scenario 3: Only voice mode
        mock_configcat_client.get_flag_value.side_effect = lambda flag, default, user: (
            True if flag == "voice_mode_enabled" else default
        )
        assert (
            feature_flags.is_enabled("text_mode_enabled") is True
        )  # Falls back to default
        assert feature_flags.is_enabled("voice_mode_enabled") is True
