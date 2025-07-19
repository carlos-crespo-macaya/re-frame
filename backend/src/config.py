"""Configuration settings for the backend application."""

import os

# Voice mode feature flag
VOICE_MODE_ENABLED = os.getenv("VOICE_MODE_ENABLED", "false").lower() == "true"

# Other configuration settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Audio configuration
AUDIO_SAMPLE_RATE = 16000  # Standard sample rate for audio processing
AUDIO_MAX_SIZE_MB = 10  # Maximum audio file size in MB
AUDIO_MAX_DURATION_SECONDS = 30  # Maximum audio duration in seconds
