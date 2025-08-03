"""Tests for the feature flags implementation."""

from unittest.mock import MagicMock

from src.utils.feature_flags.models import (
    FeatureFlagConfig,
    FeatureFlagKey,
    FeatureFlags,
)
from src.utils.feature_flags.service import (
    FeatureFlagServiceImpl,
    create_feature_flag_service,
)


class TestFeatureFlags:
    """Test the FeatureFlags data model."""

    def test_defaults(self):
        """Test default values."""
        flags = FeatureFlags.defaults()
        assert flags.chat_mode_enabled is True
        assert flags.voice_mode_enabled is False
        assert flags.notepad_mode_enabled is False

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            FeatureFlagKey.CHAT_MODE_ENABLED: False,
            FeatureFlagKey.VOICE_MODE_ENABLED: True,
            FeatureFlagKey.NOTEPAD_MODE_ENABLED: True,
        }
        flags = FeatureFlags.from_dict(data)

        assert flags.chat_mode_enabled is False
        assert flags.voice_mode_enabled is True
        assert flags.notepad_mode_enabled is True

    def test_to_dict(self):
        """Test conversion to dictionary."""
        flags = FeatureFlags(chat_mode_enabled=False, voice_mode_enabled=True)
        result = flags.to_dict()

        expected = {
            "chat_mode_enabled": False,
            "voice_mode_enabled": True,
            "notepad_mode_enabled": False,
        }
        assert result == expected


class TestFeatureFlagConfig:
    """Test the configuration."""

    def test_defaults(self):
        """Test default configuration values."""
        config = FeatureFlagConfig()
        assert config.sdk_key == ""
        assert config.timeout_seconds == 5.0
        assert config.enable_caching is True
        assert config.log_flag_access is False

    def test_from_environment(self, monkeypatch):
        """Test loading from environment variables."""
        monkeypatch.setenv("FEATURE_FLAGS_SDK_KEY", "test-key")
        monkeypatch.setenv("FEATURE_FLAGS_TIMEOUT", "2.0")
        monkeypatch.setenv("FEATURE_FLAGS_CACHE", "false")
        monkeypatch.setenv("FEATURE_FLAGS_LOG_ACCESS", "true")

        config = FeatureFlagConfig.from_environment()
        assert config.sdk_key == "test-key"
        assert config.timeout_seconds == 2.0
        assert config.enable_caching is False
        assert config.log_flag_access is True


class TestFeatureFlagService:
    """Test the feature flag service."""

    def test_service_with_no_sdk_key(self):
        """Test service behavior when SDK key is missing."""
        config = FeatureFlagConfig(sdk_key="")
        service = FeatureFlagServiceImpl(config)

        flags = service.get_ui_flags()
        assert isinstance(flags, FeatureFlags)
        assert flags == FeatureFlags.defaults()

    def test_service_with_mock_client(self):
        """Test service with a mock ConfigCat client."""
        config = FeatureFlagConfig(sdk_key="test-key")

        # Create mock client
        mock_client = MagicMock()
        mock_client.get_value.side_effect = lambda key, default: {
            "chat_mode_enabled": False,
            "voice_mode_enabled": True,
            "notepad_mode_enabled": True,
        }.get(key, default)

        # Create mock factory
        mock_factory = MagicMock()
        mock_factory.get.return_value = mock_client

        service = FeatureFlagServiceImpl(config, mock_factory)
        flags = service.get_ui_flags()

        assert flags.chat_mode_enabled is False
        assert flags.voice_mode_enabled is True
        assert flags.notepad_mode_enabled is True

    def test_is_enabled(self):
        """Test individual flag checking."""
        config = FeatureFlagConfig(sdk_key="test-key")

        # Create mock client
        mock_client = MagicMock()
        mock_client.get_value.return_value = True

        mock_factory = MagicMock()
        mock_factory.get.return_value = mock_client

        service = FeatureFlagServiceImpl(config, mock_factory)

        assert service.is_enabled(FeatureFlagKey.CHAT_MODE_ENABLED) is True
        mock_client.get_value.assert_called_with("chat_mode_enabled", True)

    def test_fallback_on_client_error(self):
        """Test fallback behavior when client throws an error."""
        config = FeatureFlagConfig(sdk_key="test-key")

        # Create mock client that throws an error
        mock_client = MagicMock()
        mock_client.get_value.side_effect = Exception("ConfigCat error")

        mock_factory = MagicMock()
        mock_factory.get.return_value = mock_client

        service = FeatureFlagServiceImpl(config, mock_factory)
        flags = service.get_ui_flags()

        # Should fallback to defaults
        assert flags == FeatureFlags.defaults()

    def test_close(self):
        """Test resource cleanup."""
        config = FeatureFlagConfig(sdk_key="test-key")

        mock_client = MagicMock()
        mock_factory = MagicMock()
        mock_factory.get.return_value = mock_client

        service = FeatureFlagServiceImpl(config, mock_factory)
        service.close()

        mock_client.close.assert_called_once()

    def test_log_flag_access(self):
        """Test flag access logging."""
        config = FeatureFlagConfig(sdk_key="test-key", log_flag_access=True)

        mock_client = MagicMock()
        mock_client.get_value.return_value = True

        mock_factory = MagicMock()
        mock_factory.get.return_value = mock_client

        service = FeatureFlagServiceImpl(config, mock_factory)
        service.is_enabled(FeatureFlagKey.CHAT_MODE_ENABLED)

        # Should have called get_value with logging enabled
        mock_client.get_value.assert_called_with("chat_mode_enabled", True)


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_create_feature_flag_service(self):
        """Test the convenience function."""
        service = create_feature_flag_service()
        assert isinstance(service, FeatureFlagServiceImpl)

    def test_create_with_custom_config(self):
        """Test creating with custom configuration."""
        config = FeatureFlagConfig(sdk_key="custom-key")
        service = create_feature_flag_service(config)
        assert service.config.sdk_key == "custom-key"

    def test_create_with_client_factory(self):
        """Test creating with custom client factory."""
        config = FeatureFlagConfig(sdk_key="test-key")
        mock_factory = MagicMock()

        service = create_feature_flag_service(config, mock_factory)
        assert isinstance(service, FeatureFlagServiceImpl)
