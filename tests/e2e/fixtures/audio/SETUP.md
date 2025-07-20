# Audio Fixtures Setup Guide

This directory contains pre-generated audio fixtures for E2E voice testing in both English and Spanish.

## Quick Start

1. **Generate the audio fixtures** (one-time setup):
   ```bash
   cd tests/e2e/fixtures
   npm install @google/generative-ai  # If using Gemini
   node generate-audio-fixtures.js
   ```

2. **Run the voice tests**:
   ```bash
   # English voice tests
   ./run-e2e-docker.sh --text voice-english-fixtures.spec.ts
   
   # Spanish voice tests
   ./run-e2e-docker.sh --text voice-spanish-fixtures.spec.ts
   ```

## Audio Files Structure

```
audio/
├── index.json           # Metadata about all fixtures
├── english/
│   ├── en-greeting.wav     # "Hello, I'm feeling anxious about an upcoming presentation at work"
│   ├── en-greeting.json    # Metadata
│   ├── en-thought-1.wav    # "I keep thinking that everyone will judge me..."
│   ├── en-thought-1.json
│   ├── en-insight.wav      # "You're right, I guess I'm assuming the worst..."
│   ├── en-insight.json
│   ├── en-conclusion.wav   # "Thank you, I feel more confident now..."
│   ├── en-conclusion.json
│   ├── en-sleep-worry.wav  # "I can't sleep at night because I keep worrying..."
│   └── en-sleep-worry.json
└── spanish/
    ├── es-greeting.wav     # "Hola, me siento ansioso por una presentación..."
    ├── es-greeting.json
    ├── es-thought-1.wav    # "Sigo pensando que todos me van a juzgar..."
    ├── es-thought-1.json
    ├── es-insight.wav      # "Tienes razón, creo que estoy asumiendo lo peor..."
    ├── es-insight.json
    ├── es-conclusion.wav   # "Gracias, me siento más confiado ahora..."
    ├── es-conclusion.json
    ├── es-social.wav       # "Me cuesta mucho hablar con personas nuevas..."
    └── es-social.json
```

## Audio Format Specifications

All audio files follow these specifications:
- **Format**: WAV (PCM)
- **Sample Rate**: 16,000 Hz (16kHz)
- **Channels**: 1 (Mono)
- **Bit Depth**: 16-bit
- **Encoding**: Linear PCM

These match the backend's expected audio format.

## Generating Real Audio with Google Cloud TTS

For more realistic testing, you can use Google Cloud Text-to-Speech:

1. **Set up Google Cloud credentials**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```

2. **Install the TTS library**:
   ```bash
   npm install @google-cloud/text-to-speech
   ```

3. **Modify `generate-audio-fixtures.js`** to use the real TTS API (see comments in the file).

## Generating Real Audio with Gemini

While Gemini doesn't directly generate audio, you can:
1. Use Gemini to generate natural variations of the test phrases
2. Use Google Cloud TTS or another service to convert to audio

## Test Scenarios Covered

### English Tests
1. **Complete CBT Conversation** - Full workflow through all phases
2. **Background Noise Handling** - Tests with simulated noisy audio
3. **Mixed Voice/Text Input** - Switching between modalities

### Spanish Tests  
1. **Complete Spanish CBT Conversation** - Full workflow in Spanish
2. **Social Anxiety Scenario** - Different anxiety type
3. **Language Switching** - Starting in Spanish, switching to English

## Customizing Test Phrases

To add new test scenarios:

1. Edit `generate-audio-fixtures.js` and add to `testPhrases`:
   ```javascript
   english: [
     // ... existing phrases
     {
       id: 'en-custom',
       text: "Your new test phrase here",
       description: 'Description of scenario'
     }
   ]
   ```

2. Regenerate fixtures:
   ```bash
   node generate-audio-fixtures.js
   ```

3. Update test files to use the new fixtures.

## Troubleshooting

### Audio files not found
- Run `node generate-audio-fixtures.js` first
- Check that files exist in `audio/english/` and `audio/spanish/`

### Tests fail with transcription errors
- The backend might not recognize synthetic audio
- Try using real TTS-generated audio
- Mock the transcription endpoint in tests

### Different audio format needed
- Modify the WAV generation in `generate-audio-fixtures.js`
- Update sample rate, channels, or bit depth as needed

## CI/CD Integration

For CI environments:
1. Pre-generate fixtures and commit them to the repo
2. Or generate them as part of the CI pipeline
3. Ensure GEMINI_API_KEY is available in CI secrets