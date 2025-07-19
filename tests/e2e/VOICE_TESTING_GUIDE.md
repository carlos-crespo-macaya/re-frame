# Voice Testing Guide with Google Cloud TTS

This guide explains how to set up and run E2E voice tests using real speech synthesis from Google Cloud Text-to-Speech.

## Prerequisites

1. **Google Cloud Account** with Text-to-Speech API enabled
2. **Service Account Key** or Application Default Credentials
3. **Node.js** installed
4. **Docker** and **Docker Compose** installed
5. **GEMINI_API_KEY** in your environment

## Setup Instructions

### 1. Enable Google Cloud Text-to-Speech API

```bash
# If using gcloud CLI
gcloud services enable texttospeech.googleapis.com
```

Or enable it from the [Google Cloud Console](https://console.cloud.google.com/apis/library/texttospeech.googleapis.com).

### 2. Set Up Authentication

Choose one of these methods:

#### Option A: Service Account Key (Recommended for CI/CD)
```bash
# Create a service account
gcloud iam service-accounts create tts-test-account \
    --display-name="TTS Test Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:tts-test-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudtexttospeech.client"

# Create and download key
gcloud iam service-accounts keys create ~/tts-key.json \
    --iam-account=tts-test-account@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/tts-key.json"
```

#### Option B: Application Default Credentials (For local development)
```bash
gcloud auth application-default login
```

### 3. Generate Audio Fixtures

```bash
cd tests/e2e/fixtures
./setup-and-generate.sh

# To also see available voices:
./setup-and-generate.sh --list-voices
```

This will:
- Install npm dependencies
- Generate all audio files using Google Cloud TTS
- Create metadata files for each audio
- Verify all files were created successfully

## Generated Audio Files

The script generates realistic speech audio for testing:

### English Phrases (en-US)
- `en-greeting.wav` - Female voice (Journey-F)
- `en-thought-1.wav` - Female voice (Journey-F)
- `en-insight.wav` - Female voice (Journey-F)
- `en-conclusion.wav` - Female voice (Journey-F)
- `en-sleep-worry.wav` - Male voice (Journey-D)

### Spanish Phrases (es-ES/es-MX)
- `es-greeting.wav` - Spanish female (Polyglot-1)
- `es-thought-1.wav` - Spanish female (Polyglot-1)
- `es-insight.wav` - Spanish female (Polyglot-1)
- `es-conclusion.wav` - Spanish female (Polyglot-1)
- `es-social.wav` - Mexican Spanish female (Journey-F)

## Running the Tests

### Run All Voice Tests
```bash
cd /Users/carlos/workspace/re-frame
make test-e2e
```

### Run Specific Language Tests
```bash
# English tests only
docker-compose -f docker-compose.integration.yml run --rm playwright \
  pnpm playwright test voice-english-fixtures.spec.ts

# Spanish tests only
docker-compose -f docker-compose.integration.yml run --rm playwright \
  pnpm playwright test voice-spanish-fixtures.spec.ts
```

### Debug Mode
```bash
make test-e2e --debug --keep-running
```

## Voice Quality Options

The generation script uses high-quality neural voices:

### English Voices
- **en-US-Journey-F**: Female, natural and expressive
- **en-US-Journey-D**: Male, clear and professional
- **en-US-Standard-***: Standard quality voices
- **en-US-Wavenet-***: WaveNet neural voices

### Spanish Voices
- **es-ES-Polyglot-1**: Spanish (Spain) multilingual
- **es-MX-Journey-F**: Mexican Spanish female
- **es-ES-Standard-***: Standard Spanish voices
- **es-ES-Wavenet-***: Neural Spanish voices

## Customizing Test Phrases

To add or modify test phrases:

1. Edit `generate-audio-fixtures.js`:
```javascript
english: [
  // Add new phrase
  {
    id: 'en-custom',
    text: "Your custom phrase here",
    description: 'Description',
    voice: { languageCode: 'en-US', name: 'en-US-Journey-F' }
  }
]
```

2. Regenerate fixtures:
```bash
cd tests/e2e/fixtures
node generate-audio-fixtures.js
```

3. Update test files to use new fixtures.

## Audio Specifications

All generated audio files have:
- **Format**: WAV (LINEAR16 PCM)
- **Sample Rate**: 16,000 Hz
- **Channels**: Mono
- **Bit Depth**: 16-bit
- **Optimization**: Small speaker device profile

These match the backend's expected format exactly.

## Cost Considerations

Google Cloud TTS pricing (as of 2024):
- **Standard voices**: $4 per 1 million characters
- **WaveNet/Neural2 voices**: $16 per 1 million characters
- **Journey voices**: Premium pricing

Our test phrases total ~500 characters, so generation cost is minimal.

## Troubleshooting

### Authentication Errors
```
Error: Could not load the default credentials
```
**Solution**: Ensure GOOGLE_APPLICATION_CREDENTIALS is set or run `gcloud auth application-default login`

### API Not Enabled
```
Error: Cloud Text-to-Speech API has not been used in project
```
**Solution**: Enable the API: `gcloud services enable texttospeech.googleapis.com`

### Voice Not Available
```
Error: Voice 'en-US-Journey-F' not found
```
**Solution**: Some voices may require allowlisting. Use `--list-voices` to see available options.

### Permission Denied
```
Error: Permission 'cloudtexttospeech.synthesizeSpeech' denied
```
**Solution**: Ensure your service account has the `roles/cloudtexttospeech.client` role.

## CI/CD Integration

For GitHub Actions:
```yaml
- name: Setup Google Cloud Auth
  uses: google-github-actions/auth@v2
  with:
    credentials_json: ${{ secrets.GCP_SA_KEY }}

- name: Generate Audio Fixtures
  run: |
    cd tests/e2e/fixtures
    npm install
    node generate-audio-fixtures.js

- name: Run Voice E2E Tests
  env:
    GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
  run: make test-e2e
```

## Verifying Audio Files

To check if all audio files exist:
```bash
cd tests/e2e/fixtures
node generate-audio-fixtures.js verify
```

To play an audio file (on macOS):
```bash
afplay audio/english/en-greeting.wav
```

## Next Steps

1. Generate the audio fixtures using the setup script
2. Run the E2E tests to verify the complete voice workflow
3. Monitor the test results in the Playwright report
4. Adjust voice parameters if needed for better recognition