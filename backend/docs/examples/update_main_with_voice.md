# How to Add Voice Configuration to Google ADK Audio Responses

## Current Implementation

The backend currently uses a basic `SpeechConfig` with only the language code:

```python
run_config = RunConfig(
    response_modalities=[modality],
    speech_config=SpeechConfig(language_code=language_code),
)
```

## Enhanced Implementation with Voice Selection

To add voice configuration, you need to:

1. Import the additional types:
```python
from google.genai.types import Content, Part, SpeechConfig, VoiceConfig, PrebuiltVoiceConfig
# Or use the types module:
from google.genai import types
```

2. Update the `start_agent_session` function in `/backend/src/main.py`:

```python
async def start_agent_session(user_id, is_audio=False, language_code="en-US"):
    """Starts an agent session"""
    logger.info(
        "agent_session_starting",
        user_id=user_id,
        is_audio=is_audio,
        language_code=language_code,
    )
    
    # Create the CBT assistant agent with language support
    cbt_agent = create_cbt_assistant(language_code=language_code)
    logger.debug("cbt_agent_created", agent_name=cbt_agent.name)
    
    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=cbt_agent,
    )
    logger.debug("runner_created", app_name=APP_NAME)
    
    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
    )
    logger.info("adk_session_created", session=str(session), user_id=user_id)
    
    # Set response modality with enhanced voice configuration
    modality = "AUDIO" if is_audio else "TEXT"
    
    # Enhanced configuration with voice selection
    if is_audio:
        # Use types module for cleaner syntax
        from google.genai import types
        
        run_config = RunConfig(
            response_modalities=[modality],
            speech_config=types.SpeechConfig(
                language_code=language_code,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"  # Options: Kore, Aoede, etc.
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
    
    # Return runner, session, and run_config for later use
    return runner, session, run_config
```

## Available Voice Options

Based on the ADK documentation, the prebuilt voices include:
- **Kore**: A general-purpose voice
- **Aoede**: Another voice option with different characteristics

## Language-Specific Voice Selection

For better user experience, you might want to select voices based on language:

```python
def get_voice_for_language(language_code: str) -> str:
    """Select appropriate voice based on language."""
    voice_mapping = {
        "en-US": "Kore",
        "en-GB": "Aoede",
        "es-US": "Kore",
        "es-ES": "Aoede",
        # Add more mappings as needed
    }
    return voice_mapping.get(language_code, "Kore")  # Default to Kore
```

## Environment Variable Configuration

You can also make the voice configurable via environment variables:

```python
# In config.py or at the top of main.py
ADK_VOICE_NAME = os.getenv("ADK_VOICE_NAME", "Kore")

# Then in start_agent_session:
voice_name = ADK_VOICE_NAME if is_audio else None
```

## Testing Audio with Voice

To test the audio generation with specific voices:

1. Set the `is_audio` parameter to `True` when calling the SSE endpoint
2. The system will use the configured voice for audio responses
3. The frontend will receive audio data in PCM format with the selected voice characteristics

## Notes

- Voice configuration only applies when `response_modalities` includes "AUDIO"
- The `language_code` in `SpeechConfig` should match the language of your agent's responses
- Different voices may have different characteristics (tone, speed, etc.)
- Not all voices support all languages - check ADK documentation for compatibility