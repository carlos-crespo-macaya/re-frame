"""Integration tests for ConfigCat feature flags."""

import os
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestConfigCatIntegration:
    """Test ConfigCat integration with the API."""

    def test_feature_flags_api_without_configcat(self):
        """Test API returns defaults when ConfigCat is not configured."""
        with patch.dict(os.environ, {}, clear=True):
            response = client.get("/api/feature-flags")

            assert response.status_code == 200
            data = response.json()

            # Should get default values
            assert data["textModeEnabled"] is True
            assert data["voiceModeEnabled"] is True

            # All languages should be enabled by default
            assert len(data["enabledLanguages"]) == 10
            assert "en" in data["enabledLanguages"]
            assert "es" in data["enabledLanguages"]

    def test_feature_flags_api_with_configcat(self):
        """Test API returns ConfigCat values when configured."""
        # Create a mock ConfigCat client instance
        mock_client_instance = MagicMock()

        # Configure the mock to return specific values for each flag
        def mock_get_flag_value(flag_name, default_value, user_context):
            flag_values = {
                "text_mode_enabled": True,
                "voice_mode_enabled": False,  # Voice disabled
                "language_en": True,
                "language_es": True,
                "language_pt": False,
                "language_fr": False,
                "language_de": False,
                "language_it": False,
                "language_nl": False,
                "language_pl": False,
                "language_uk": False,
                "language_cs": False,
            }
            return flag_values.get(flag_name, default_value)

        mock_client_instance.get_flag_value.side_effect = mock_get_flag_value

        with (
            patch.dict(os.environ, {"CONFIGCAT_SDK_KEY": "test-key"}),
            patch("src.utils.configcat_flags.ConfigCatClient") as mock_client_class,
        ):
            mock_client_class.return_value = mock_client_instance

            # Reset singleton to pick up new environment
            import src.utils.configcat_flags

            src.utils.configcat_flags._configcat_client = None
            src.utils.configcat_flags._configcat_flags = None

            response = client.get("/api/feature-flags")

            assert response.status_code == 200
            data = response.json()

            # Should get ConfigCat values
            assert data["textModeEnabled"] is True
            assert data["voiceModeEnabled"] is False

            # Only enabled languages
            assert len(data["enabledLanguages"]) == 2
            assert "en" in data["enabledLanguages"]
            assert "es" in data["enabledLanguages"]
            assert "pt" not in data["enabledLanguages"]

    def test_feature_flags_with_user_targeting(self):
        """Test feature flags respect user targeting attributes."""
        # Create a mock ConfigCat client instance
        mock_client_instance = MagicMock()

        # Capture user context
        captured_context = None

        def mock_get_flag_value(flag_name, default_value, user_context):
            nonlocal captured_context
            captured_context = user_context
            flag_values = {
                "text_mode_enabled": True,
                "voice_mode_enabled": True,
                "language_en": True,
                "language_es": True,
                "language_pt": True,
                "language_fr": False,
                "language_de": False,
                "language_it": False,
                "language_nl": False,
                "language_pl": False,
                "language_uk": False,
                "language_cs": False,
            }
            return flag_values.get(flag_name, default_value)

        mock_client_instance.get_flag_value.side_effect = mock_get_flag_value

        with (
            patch.dict(os.environ, {"CONFIGCAT_SDK_KEY": "test-key"}),
            patch("src.utils.configcat_flags.ConfigCatClient") as mock_client_class,
        ):
            mock_client_class.return_value = mock_client_instance

            # Reset singleton
            import src.utils.configcat_flags

            src.utils.configcat_flags._configcat_client = None
            src.utils.configcat_flags._configcat_flags = None

            response = client.get(
                "/api/feature-flags",
                headers={
                    "X-Session-ID": "user-123",
                    "X-User-Language": "es",
                    "X-User-Country": "MX",
                },
            )

            assert response.status_code == 200

            # Verify user context was passed to ConfigCat
            assert captured_context is not None
            assert captured_context["identifier"] == "user-123"
            assert captured_context["custom"]["language"] == "es"
            assert captured_context["custom"]["country"] == "MX"

    def test_mode_exclusivity_scenarios(self):
        """Test different mode exclusivity scenarios."""
        scenarios = [
            # Both enabled
            (
                {"text_mode_enabled": True, "voice_mode_enabled": True},
                {"textModeEnabled": True, "voiceModeEnabled": True},
            ),
            # Text only
            (
                {"text_mode_enabled": True, "voice_mode_enabled": False},
                {"textModeEnabled": True, "voiceModeEnabled": False},
            ),
            # Voice only
            (
                {"text_mode_enabled": False, "voice_mode_enabled": True},
                {"textModeEnabled": False, "voiceModeEnabled": True},
            ),
        ]

        for flags, expected_values in scenarios:
            # Create a mock ConfigCat client instance
            mock_client_instance = MagicMock()

            # Configure the mock to return specific values for each flag
            def make_mock_get_flag_value(scenario_flags):
                def mock_get_flag_value(flag_name, default_value, user_context):
                    # Add language flags to the test data
                    all_flags = {
                        **scenario_flags,
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
                    return all_flags.get(flag_name, default_value)

                return mock_get_flag_value

            mock_client_instance.get_flag_value.side_effect = make_mock_get_flag_value(
                flags
            )

            with (
                patch.dict(os.environ, {"CONFIGCAT_SDK_KEY": "test-key"}),
                patch("src.utils.configcat_flags.ConfigCatClient") as mock_client_class,
            ):
                mock_client_class.return_value = mock_client_instance

                # Reset singleton
                import src.utils.configcat_flags

                src.utils.configcat_flags._configcat_client = None
                src.utils.configcat_flags._configcat_flags = None

                response = client.get("/api/feature-flags")
                assert response.status_code == 200

                data = response.json()
                assert data["textModeEnabled"] == expected_values["textModeEnabled"]
                assert data["voiceModeEnabled"] == expected_values["voiceModeEnabled"]
