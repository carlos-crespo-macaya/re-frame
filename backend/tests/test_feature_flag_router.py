"""Tests for feature flags API router."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestFeatureFlagsRouter:
    """Test suite for feature flags API endpoints."""

    @pytest.fixture
    def mock_feature_flags(self):
        """Mock feature flags response."""
        return {
            "text_mode_enabled": True,
            "voice_mode_enabled": True,
            "language_en": True,
            "language_es": False,
            "language_pt": False,
            "language_fr": True,
            "language_de": False,
            "language_it": False,
            "language_nl": False,
            "language_pl": False,
            "language_uk": False,
            "language_cs": False,
        }

    def test_get_feature_flags_endpoint(self, mock_feature_flags):
        """Test /api/feature-flags returns evaluated flags."""
        with patch("src.routers.feature_flags.get_configcat_flags") as mock_get_flags:
            mock_instance = mock_get_flags.return_value
            mock_instance.get_all_flags.return_value = mock_feature_flags
            mock_instance.get_enabled_modes.return_value = {
                "text_enabled": True,
                "voice_enabled": True,
            }
            # Only return languages that are enabled in mock_feature_flags
            mock_instance.get_enabled_languages.return_value = ["en", "fr"]

            response = client.get("/api/feature-flags")

            assert response.status_code == 200
            data = response.json()

            # Check structure
            assert "textModeEnabled" in data
            assert "voiceModeEnabled" in data
            assert "enabledLanguages" in data

            # Check modes
            assert data["textModeEnabled"] is True
            assert data["voiceModeEnabled"] is True

            # Check languages - should only get enabled ones
            assert "en" in data["enabledLanguages"]  # language_en is True
            assert "fr" in data["enabledLanguages"]  # language_fr is True
            assert "es" not in data["enabledLanguages"]  # language_es is False

    def test_feature_flags_with_user_context(self):
        """Test flags are evaluated with user attributes."""
        with patch("src.routers.feature_flags.get_configcat_flags") as mock_get_flags:
            mock_instance = mock_get_flags.return_value

            # Set up mock to capture user context
            user_context_captured = None

            def capture_user_context(user=None):
                nonlocal user_context_captured
                user_context_captured = user
                return {
                    "text_mode_enabled": True,
                    "voice_mode_enabled": False,
                    "language_en": True,
                    "language_es": True,
                }

            mock_instance.get_all_flags.side_effect = capture_user_context
            mock_instance.get_enabled_modes.return_value = {
                "text_enabled": True,
                "voice_enabled": False,
            }
            mock_instance.get_enabled_languages.return_value = ["en", "es"]

            # Send request with session ID header
            response = client.get(
                "/api/feature-flags", headers={"X-Session-ID": "test-session-123"}
            )

            assert response.status_code == 200

            # Verify user context was passed
            assert user_context_captured is not None
            assert user_context_captured["identifier"] == "test-session-123"

    def test_feature_flags_caching_headers(self):
        """Test appropriate cache headers are set."""
        with patch("src.routers.feature_flags.get_configcat_flags") as mock_get_flags:
            mock_instance = mock_get_flags.return_value
            mock_instance.get_all_flags.return_value = {}
            mock_instance.get_enabled_modes.return_value = {
                "text_enabled": True,
                "voice_enabled": True,
            }
            mock_instance.get_enabled_languages.return_value = ["en"]

            response = client.get("/api/feature-flags")

            assert response.status_code == 200

            # Check cache control headers
            assert "Cache-Control" in response.headers
            # Should cache for 60 seconds (same as ConfigCat polling interval)
            assert "max-age=60" in response.headers["Cache-Control"]
            assert "private" in response.headers["Cache-Control"]

    def test_feature_flags_error_handling(self):
        """Test error handling when feature flag service fails."""
        with patch("src.routers.feature_flags.get_configcat_flags") as mock_get_flags:
            mock_instance = mock_get_flags.return_value
            mock_instance.get_all_flags.side_effect = Exception("Service unavailable")

            response = client.get("/api/feature-flags")

            # Should still return 200 with defaults
            assert response.status_code == 200
            data = response.json()

            # Should have default structure
            assert "textModeEnabled" in data
            assert "voiceModeEnabled" in data
            assert "enabledLanguages" in data

            # Should use defaults
            assert data["textModeEnabled"] is True
            assert data["voiceModeEnabled"] is True
            assert "en" in data["enabledLanguages"]

    def test_feature_flags_response_format(self):
        """Test the response format matches expected structure."""
        with patch("src.routers.feature_flags.get_configcat_flags") as mock_get_flags:
            mock_instance = mock_get_flags.return_value
            mock_instance.get_all_flags.return_value = {
                "text_mode_enabled": True,
                "voice_mode_enabled": False,
                "language_en": True,
                "language_es": True,
                "language_pt": False,
            }
            mock_instance.get_enabled_modes.return_value = {
                "text_enabled": True,
                "voice_enabled": False,
            }
            mock_instance.get_enabled_languages.return_value = ["en", "es"]

            response = client.get("/api/feature-flags")

            assert response.status_code == 200
            data = response.json()

            # Expected structure
            expected_structure = {
                "textModeEnabled": True,
                "voiceModeEnabled": False,
                "enabledLanguages": ["en", "es"],
            }

            assert data == expected_structure

    def test_feature_flags_with_custom_headers(self):
        """Test feature flags with custom user attributes from headers."""
        with patch("src.routers.feature_flags.get_configcat_flags") as mock_get_flags:
            mock_instance = mock_get_flags.return_value

            # Capture user context
            user_context_captured = None

            def capture_user_context(user=None):
                nonlocal user_context_captured
                user_context_captured = user
                return {}

            mock_instance.get_all_flags.side_effect = capture_user_context
            mock_instance.get_enabled_modes.return_value = {
                "text_enabled": True,
                "voice_enabled": True,
            }
            mock_instance.get_enabled_languages.return_value = ["en"]

            # Send request with custom headers
            response = client.get(
                "/api/feature-flags",
                headers={
                    "X-Session-ID": "session-456",
                    "X-User-Language": "es",
                    "X-User-Country": "ES",
                },
            )

            assert response.status_code == 200

            # Verify user context includes custom attributes
            assert user_context_captured["identifier"] == "session-456"
            assert user_context_captured["custom"]["language"] == "es"
            assert user_context_captured["custom"]["country"] == "ES"

    def test_feature_flags_required_format(self):
        """Test that the API returns the exact required format."""
        with patch("src.routers.feature_flags.get_configcat_flags") as mock_get_flags:
            mock_instance = mock_get_flags.return_value
            mock_instance.get_all_flags.return_value = {
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
            mock_instance.get_enabled_modes.return_value = {
                "text_enabled": True,
                "voice_enabled": True,
            }
            mock_instance.get_enabled_languages.return_value = [
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
            ]

            response = client.get("/api/feature-flags")

            assert response.status_code == 200
            data = response.json()

            # Verify exact format required
            assert data == {
                "textModeEnabled": True,
                "voiceModeEnabled": True,
                "enabledLanguages": [
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
            }

    def test_configcat_integration_with_valid_sdk_key(self):
        """Test real ConfigCat integration when SDK key is provided."""
        import os

        # Only run this test if CONFIGCAT_SDK_KEY is set in environment
        if not os.getenv("CONFIGCAT_SDK_KEY"):
            pytest.skip("CONFIGCAT_SDK_KEY not set, skipping integration test")

        # This test uses the real ConfigCat client
        response = client.get("/api/feature-flags")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "textModeEnabled" in data
        assert "voiceModeEnabled" in data
        assert "enabledLanguages" in data

        # Verify types
        assert isinstance(data["textModeEnabled"], bool)
        assert isinstance(data["voiceModeEnabled"], bool)
        assert isinstance(data["enabledLanguages"], list)

        # At minimum, English should be enabled
        assert "en" in data["enabledLanguages"]
