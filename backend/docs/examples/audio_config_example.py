"""
Example of configuring audio responses with Google ADK.

This example shows how to properly configure SpeechConfig with voice settings
for generating audio responses in the CBT Assistant.
"""

from google.adk.agents.run_config import RunConfig
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.genai.types import (
    SpeechConfig,
)


# Example 1: Basic audio configuration with default voice
def create_basic_audio_config():
    """Create a basic audio configuration with default voice."""
    run_config = RunConfig(
        response_modalities=["AUDIO"],
        speech_config=SpeechConfig(language_code="en-US"),
    )
    return run_config


# Example 2: Audio configuration with specific voice
def create_audio_config_with_voice():
    """Create audio configuration with a specific prebuilt voice."""
    run_config = RunConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"  # Available voices: Kore, Aoede, etc.
                )
            ),
        ),
    )
    return run_config


# Example 3: Full audio configuration with both audio and text response
def create_multimodal_config():
    """Create configuration for both audio and text responses."""
    run_config = RunConfig(
        response_modalities=["AUDIO", "TEXT"],
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Aoede"  # Different voice option
                )
            ),
        ),
    )
    return run_config


# Example 4: Language-specific voice configuration
def create_language_specific_config(language_code: str):
    """Create audio configuration based on language."""
    # Map languages to appropriate voices
    voice_mapping = {
        "en-US": "Kore",
        "en-GB": "Aoede",
        "es-US": "Kore",  # Spanish US
        "es-ES": "Aoede",  # Spanish Spain
    }

    voice_name = voice_mapping.get(language_code, "Kore")  # Default to Kore

    run_config = RunConfig(
        response_modalities=["AUDIO", "TEXT"],
        speech_config=types.SpeechConfig(
            language_code=language_code,
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            ),
        ),
    )
    return run_config


# Example 5: How to update the existing start_agent_session function
async def start_agent_session_with_voice(
    user_id, is_audio=False, language_code="en-US"
):
    """Updated version of start_agent_session with voice configuration."""
    from src.agents.cbt_assistant import create_cbt_assistant

    # Create the CBT assistant agent with language support
    cbt_agent = create_cbt_assistant(language_code=language_code)

    # Create a Runner
    runner = InMemoryRunner(
        app_name="CBT Reframing Assistant",
        agent=cbt_agent,
    )

    # Create a Session
    session = await runner.session_service.create_session(
        app_name="CBT Reframing Assistant",
        user_id=user_id,
    )

    # Set response modality and voice configuration
    modality = "AUDIO" if is_audio else "TEXT"

    if is_audio:
        # Configure with voice when audio is enabled
        run_config = RunConfig(
            response_modalities=[modality],
            speech_config=types.SpeechConfig(
                language_code=language_code,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"  # Or make this configurable
                    )
                ),
            ),
        )
    else:
        # Text-only configuration
        run_config = RunConfig(
            response_modalities=[modality],
            speech_config=SpeechConfig(language_code=language_code),
        )

    return runner, session, run_config


# Example 6: Environment variable based configuration
def create_config_from_env():
    """Create audio configuration from environment variables."""
    import os

    # Get settings from environment
    audio_enabled = os.getenv("AUDIO_ENABLED", "false").lower() == "true"
    voice_name = os.getenv("ADK_VOICE_NAME", "Kore")
    language_code = os.getenv("ADK_LANGUAGE_CODE", "en-US")

    modalities = ["AUDIO", "TEXT"] if audio_enabled else ["TEXT"]

    run_config = RunConfig(
        response_modalities=modalities,
        speech_config=types.SpeechConfig(
            language_code=language_code,
            voice_config=(
                types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
                if audio_enabled
                else None
            ),
        ),
    )
    return run_config


if __name__ == "__main__":
    # Example usage
    config1 = create_basic_audio_config()
    print("Basic config:", config1)

    config2 = create_audio_config_with_voice()
    print("Voice config:", config2)

    config3 = create_multimodal_config()
    print("Multimodal config:", config3)

    config4 = create_language_specific_config("es-US")
    print("Spanish config:", config4)
