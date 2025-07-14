[ Skip to content ](https://google.github.io/adk-docs/runtime/runconfig/#runtime-configuration)
# Runtime Configuration[¶](https://google.github.io/adk-docs/runtime/runconfig/#runtime-configuration "Permanent link")
`RunConfig` defines runtime behavior and options for agents in the ADK. It controls speech and streaming settings, function calling, artifact saving, and limits on LLM calls.
When constructing an agent run, you can pass a `RunConfig` to customize how the agent interacts with models, handles audio, and streams responses. By default, no streaming is enabled and inputs aren’t retained as artifacts. Use `RunConfig` to override these defaults.
## Class Definition[¶](https://google.github.io/adk-docs/runtime/runconfig/#class-definition "Permanent link")
The `RunConfig` class holds configuration parameters for an agent's runtime behavior.
  * Python ADK uses Pydantic for this validation.
  * Java ADK typically uses immutable data classes.


[Python](https://google.github.io/adk-docs/runtime/runconfig/#python)[Java](https://google.github.io/adk-docs/runtime/runconfig/#java)
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-1)classRunConfig(BaseModel):
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-2)"""Configs for runtime behavior of agents."""
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-3)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-4)  model_config = ConfigDict(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-5)    extra='forbid',
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-6)  )
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-7)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-8)  speech_config: Optional[types.SpeechConfig] = None
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-9)  response_modalities: Optional[list[str]] = None
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-10)  save_input_blobs_as_artifacts: bool = False
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-11)  support_cfc: bool = False
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-12)  streaming_mode: StreamingMode = StreamingMode.NONE
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-13)  output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-0-14)  max_llm_calls: int = 500

```

```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-1)publicabstractclass RunConfig{
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-2)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-3)publicenumStreamingMode{
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-4)NONE,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-5)SSE,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-6)BIDI
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-7)}
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-8)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-9)publicabstract@NullableSpeechConfigspeechConfig();
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-10)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-11)publicabstractImmutableList<Modality>responseModalities();
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-12)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-13)publicabstractbooleansaveInputBlobsAsArtifacts();
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-14)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-15)publicabstract@NullableAudioTranscriptionConfigoutputAudioTranscription();
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-16)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-17)publicabstractintmaxLlmCalls();
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-18)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-19)// ...
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-1-20)}

```

## Runtime Parameters[¶](https://google.github.io/adk-docs/runtime/runconfig/#runtime-parameters "Permanent link")
Parameter | Python Type | Java Type | Default (Py / Java) | Description
---|---|---|---|---
`speech_config` | `Optional[types.SpeechConfig]` | `SpeechConfig` (nullable via `@Nullable`) | `None` / `null` | Configures speech synthesis (voice, language) using the `SpeechConfig` type.
`response_modalities` | `Optional[list[str]]` | `ImmutableList<Modality>` | `None` / Empty `ImmutableList` | List of desired output modalities (e.g., Python: `["TEXT", "AUDIO"]`; Java: uses structured `Modality` objects).
`save_input_blobs_as_artifacts` | `bool` | `boolean` | `False` / `false` | If `true`, saves input blobs (e.g., uploaded files) as run artifacts for debugging/auditing.
`streaming_mode` | `StreamingMode` | _Currently not supported_ | `StreamingMode.NONE` / N/A | Sets the streaming behavior: `NONE` (default), `SSE` (server-sent events), or `BIDI` (bidirectional).
`output_audio_transcription` | `Optional[types.AudioTranscriptionConfig]` | `AudioTranscriptionConfig` (nullable via `@Nullable`) | `None` / `null` | Configures transcription of generated audio output using the `AudioTranscriptionConfig` type.
`max_llm_calls` | `int` | `int` | `500` / `500` | Limits total LLM calls per run. `0` or negative means unlimited (warned); `sys.maxsize` raises `ValueError`.
`support_cfc` | `bool` | _Currently not supported_ | `False` / N/A | **Python:** Enables Compositional Function Calling. Requires `streaming_mode=SSE` and uses the LIVE API. **Experimental.**
### `speech_config`[¶](https://google.github.io/adk-docs/runtime/runconfig/#speech_config "Permanent link")
Note
The interface or definition of `SpeechConfig` is the same, irrespective of the language.
Speech configuration settings for live agents with audio capabilities. The `SpeechConfig` class has the following structure:
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-1)classSpeechConfig(_common.BaseModel):
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-2)"""The speech generation configuration."""
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-3)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-4)  voice_config: Optional[VoiceConfig] = Field(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-5)    default=None,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-6)    description="""The configuration for the speaker to use.""",
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-7)  )
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-8)  language_code: Optional[str] = Field(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-9)    default=None,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-10)    description="""Language code (ISO 639. e.g. en-US) for the speech synthesization.
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-11)    Only available for Live API.""",
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-2-12)  )

```

The `voice_config` parameter uses the `VoiceConfig` class:
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-3-1)classVoiceConfig(_common.BaseModel):
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-3-2)"""The configuration for the voice to use."""
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-3-3)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-3-4)  prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-3-5)    default=None,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-3-6)    description="""The configuration for the speaker to use.""",
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-3-7)  )

```

And `PrebuiltVoiceConfig` has the following structure:
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-4-1)classPrebuiltVoiceConfig(_common.BaseModel):
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-4-2)"""The configuration for the prebuilt speaker to use."""
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-4-3)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-4-4)  voice_name: Optional[str] = Field(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-4-5)    default=None,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-4-6)    description="""The name of the prebuilt voice to use.""",
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-4-7)  )

```

These nested configuration classes allow you to specify:
  * `voice_config`: The name of the prebuilt voice to use (in the `PrebuiltVoiceConfig`)
  * `language_code`: ISO 639 language code (e.g., "en-US") for speech synthesis


When implementing voice-enabled agents, configure these parameters to control how your agent sounds when speaking.
### `response_modalities`[¶](https://google.github.io/adk-docs/runtime/runconfig/#response_modalities "Permanent link")
Defines the output modalities for the agent. If not set, defaults to AUDIO. Response modalities determine how the agent communicates with users through various channels (e.g., text, audio).
### `save_input_blobs_as_artifacts`[¶](https://google.github.io/adk-docs/runtime/runconfig/#save_input_blobs_as_artifacts "Permanent link")
When enabled, input blobs will be saved as artifacts during agent execution. This is useful for debugging and audit purposes, allowing developers to review the exact data received by agents.
### `support_cfc`[¶](https://google.github.io/adk-docs/runtime/runconfig/#support_cfc "Permanent link")
Enables Compositional Function Calling (CFC) support. Only applicable when using StreamingMode.SSE. When enabled, the LIVE API will be invoked as only it supports CFC functionality.
Warning
The `support_cfc` feature is experimental and its API or behavior might change in future releases.
### `streaming_mode`[¶](https://google.github.io/adk-docs/runtime/runconfig/#streaming_mode "Permanent link")
Configures the streaming behavior of the agent. Possible values:
  * `StreamingMode.NONE`: No streaming; responses delivered as complete units
  * `StreamingMode.SSE`: Server-Sent Events streaming; one-way streaming from server to client
  * `StreamingMode.BIDI`: Bidirectional streaming; simultaneous communication in both directions


Streaming modes affect both performance and user experience. SSE streaming lets users see partial responses as they're generated, while BIDI streaming enables real-time interactive experiences.
### `output_audio_transcription`[¶](https://google.github.io/adk-docs/runtime/runconfig/#output_audio_transcription "Permanent link")
Configuration for transcribing audio outputs from live agents with audio response capability. This enables automatic transcription of audio responses for accessibility, record-keeping, and multi-modal applications.
### `max_llm_calls`[¶](https://google.github.io/adk-docs/runtime/runconfig/#max_llm_calls "Permanent link")
Sets a limit on the total number of LLM calls for a given agent run.
  * Values greater than 0 and less than `sys.maxsize`: Enforces a bound on LLM calls
  * Values less than or equal to 0: Allows unbounded LLM calls _(not recommended for production)_


This parameter prevents excessive API usage and potential runaway processes. Since LLM calls often incur costs and consume resources, setting appropriate limits is crucial.
## Validation Rules[¶](https://google.github.io/adk-docs/runtime/runconfig/#validation-rules "Permanent link")
The `RunConfig` class validates its parameters to ensure proper agent operation. While Python ADK uses `Pydantic` for automatic type validation, Java ADK relies on its static typing and may include explicit checks in the RunConfig's construction. For the `max_llm_calls` parameter specifically:
  1. Extremely large values (like `sys.maxsize` in Python or `Integer.MAX_VALUE` in Java) are typically disallowed to prevent issues.
  2. Values of zero or less will usually trigger a warning about unlimited LLM interactions.


## Examples[¶](https://google.github.io/adk-docs/runtime/runconfig/#examples "Permanent link")
### Basic runtime configuration[¶](https://google.github.io/adk-docs/runtime/runconfig/#basic-runtime-configuration "Permanent link")
[Python](https://google.github.io/adk-docs/runtime/runconfig/#python_1)[Java](https://google.github.io/adk-docs/runtime/runconfig/#java_1)
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-5-1)fromgoogle.genai.adkimport RunConfig, StreamingMode
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-5-2)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-5-3)config = RunConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-5-4)  streaming_mode=StreamingMode.NONE,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-5-5)  max_llm_calls=100
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-5-6))

```

```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-6-1)importcom.google.adk.agents.RunConfig;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-6-2)importcom.google.adk.agents.RunConfig.StreamingMode;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-6-3)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-6-4)RunConfigconfig=RunConfig.builder()
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-6-5).setStreamingMode(StreamingMode.NONE)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-6-6).setMaxLlmCalls(100)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-6-7).build();

```

This configuration creates a non-streaming agent with a limit of 100 LLM calls, suitable for simple task-oriented agents where complete responses are preferable.
### Enabling streaming[¶](https://google.github.io/adk-docs/runtime/runconfig/#enabling-streaming "Permanent link")
[Python](https://google.github.io/adk-docs/runtime/runconfig/#python_2)[Java](https://google.github.io/adk-docs/runtime/runconfig/#java_2)
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-7-1)fromgoogle.genai.adkimport RunConfig, StreamingMode
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-7-2)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-7-3)config = RunConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-7-4)  streaming_mode=StreamingMode.SSE,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-7-5)  max_llm_calls=200
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-7-6))

```

```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-8-1)importcom.google.adk.agents.RunConfig;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-8-2)importcom.google.adk.agents.RunConfig.StreamingMode;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-8-3)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-8-4)RunConfigconfig=RunConfig.builder()
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-8-5).setStreamingMode(StreamingMode.SSE)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-8-6).setMaxLlmCalls(200)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-8-7).build();

```

Using SSE streaming allows users to see responses as they're generated, providing a more responsive feel for chatbots and assistants.
### Enabling speech support[¶](https://google.github.io/adk-docs/runtime/runconfig/#enabling-speech-support "Permanent link")
[Python](https://google.github.io/adk-docs/runtime/runconfig/#python_3)[Java](https://google.github.io/adk-docs/runtime/runconfig/#java_3)
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-1)fromgoogle.genai.adkimport RunConfig, StreamingMode
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-2)fromgoogle.genaiimport types
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-3)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-4)config = RunConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-5)  speech_config=types.SpeechConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-6)    language_code="en-US",
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-7)    voice_config=types.VoiceConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-8)      prebuilt_voice_config=types.PrebuiltVoiceConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-9)        voice_name="Kore"
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-10)      )
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-11)    ),
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-12)  ),
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-13)  response_modalities=["AUDIO", "TEXT"],
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-14)  save_input_blobs_as_artifacts=True,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-15)  support_cfc=True,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-16)  streaming_mode=StreamingMode.SSE,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-17)  max_llm_calls=1000,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-9-18))

```

```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-1)importcom.google.adk.agents.RunConfig;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-2)importcom.google.adk.agents.RunConfig.StreamingMode;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-3)importcom.google.common.collect.ImmutableList;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-4)importcom.google.genai.types.Content;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-5)importcom.google.genai.types.Modality;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-6)importcom.google.genai.types.Part;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-7)importcom.google.genai.types.PrebuiltVoiceConfig;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-8)importcom.google.genai.types.SpeechConfig;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-9)importcom.google.genai.types.VoiceConfig;
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-10)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-11)RunConfigrunConfig=
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-12)RunConfig.builder()
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-13).setStreamingMode(StreamingMode.SSE)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-14).setMaxLlmCalls(1000)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-15).setSaveInputBlobsAsArtifacts(true)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-16).setResponseModalities(ImmutableList.of(newModality("AUDIO"),newModality("TEXT")))
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-17).setSpeechConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-18)SpeechConfig.builder()
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-19).voiceConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-20)VoiceConfig.builder()
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-21).prebuiltVoiceConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-22)PrebuiltVoiceConfig.builder().voiceName("Kore").build())
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-23).build())
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-24).languageCode("en-US")
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-25).build())
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-10-26).build();

```

This comprehensive example configures an agent with:
  * Speech capabilities using the "Kore" voice (US English)
  * Both audio and text output modalities
  * Artifact saving for input blobs (useful for debugging)
  * Experimental CFC support enabled **(Python only)**
  * SSE streaming for responsive interaction
  * A limit of 1000 LLM calls


### Enabling Experimental CFC Support[¶](https://google.github.io/adk-docs/runtime/runconfig/#enabling-experimental-cfc-support "Permanent link")
![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue)
```
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-11-1)fromgoogle.genai.adkimport RunConfig, StreamingMode
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-11-2)
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-11-3)config = RunConfig(
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-11-4)  streaming_mode=StreamingMode.SSE,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-11-5)  support_cfc=True,
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-11-6)  max_llm_calls=150
[](https://google.github.io/adk-docs/runtime/runconfig/#__codelineno-11-7))

```

Enabling Compositional Function Calling creates an agent that can dynamically execute functions based on model outputs, powerful for applications requiring complex workflows.
Back to top
