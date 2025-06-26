# Multilingual Implementation Guide

## Overview

Maya now uses Google Cloud Translation API for accurate language detection, supporting 100+ languages with automatic conversation flow in the detected language.

## Setup Requirements

### 1. Google Cloud Translation API

Enable the Translation API in your Google Cloud project:

```bash
# Enable the API
gcloud services enable translate.googleapis.com

# Set up authentication (if not already done)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

### 2. Install Dependencies

The Google Cloud Translation client is included in the standard google-cloud-translate package:

```bash
uv pip install google-cloud-translate
```

## How It Works

### Language Detection Flow

1. **User sends first message** → Maya calls `detect_language(text)`
2. **Google Translation API** → Returns language code and confidence score
3. **Store preference** → Language saved for entire session
4. **Respond in language** → Maya uses appropriate greeting and continues in that language
5. **Generate PDF** → Summary created in user's language

### Supported Languages (with full translations)

- **Spanish (es)** - Full support with culturally appropriate responses
- **English (en)** - Complete implementation
- **French (fr)** - Full conversational support
- **German (de)** - Complete translations
- **Italian (it)** - Full support
- **Portuguese (pt)** - Complete implementation
- **Catalan (ca)** - Regional language support

### Additional Detected Languages

Google Translation API can detect 100+ languages. While Maya has specific greetings for the languages above, she can detect and attempt to respond in many more languages including:

- Dutch (nl)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- And many more...

## Testing the Implementation

### Test Different Languages

```bash
# Run the ADK web interface
cd /Users/carlos/workspace/re-frame/agentic_workflow
adk web
```

Then test with different language inputs:

1. **Spanish**: "Hola, me siento muy ansioso por una presentación"
2. **English**: "Hello, I'm feeling anxious about a presentation"
3. **French**: "Bonjour, je me sens anxieux pour une présentation"
4. **German**: "Hallo, ich bin nervös wegen einer Präsentation"
5. **Italian**: "Ciao, sono ansioso per una presentazione"
6. **Portuguese**: "Olá, estou ansioso com uma apresentação"
7. **Catalan**: "Hola, estic nerviós per una presentació"

### Expected Behavior

1. Maya detects the language from the first message
2. Responds with greeting in that language
3. Continues entire conversation in detected language
4. Phase transitions shown in user's language
5. PDF generated with all content translated

## Configuration Notes

### Environment Variables

No additional environment variables needed beyond standard Google Cloud authentication:

```bash
# Standard Google Cloud auth (already set if using Gemini)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"

# OR use Application Default Credentials
gcloud auth application-default login
```

### API Quotas

Google Cloud Translation API quotas:
- **Free tier**: 500,000 characters/month
- **Detection**: Counts as minimal character usage
- **Cost**: ~$20 per million characters after free tier

For our use case (detecting ~50 characters per session), this is extremely cost-effective.

## Error Handling

If language detection fails:
1. Maya defaults to Spanish (primary user base)
2. Error is logged but doesn't interrupt flow
3. User can still continue conversation
4. PDF generation proceeds normally

## Future Enhancements

### Phase 2: Voice Support
- Add Web Speech API for voice input
- Integrate Google Cloud Text-to-Speech
- Maintain language consistency in voice mode

### Enhanced Translations
- Add more languages with full conversation support
- Implement region-specific variations (es-MX, pt-BR)
- Support for right-to-left languages (Arabic, Hebrew)

### Dynamic Language Switching
- Allow users to change language mid-conversation
- Implement language preference storage
- Support multilingual PDFs

## Troubleshooting

### Common Issues

1. **"Could not detect language" error**
   - Check GOOGLE_APPLICATION_CREDENTIALS
   - Verify Translation API is enabled
   - Check network connectivity

2. **Wrong language detected**
   - Usually happens with very short messages
   - Maya will still respond appropriately
   - Longer messages improve accuracy

3. **PDF shows English instead of detected language**
   - Verify language_code is passed to generate_multilingual_pdf_summary
   - Check that translations dict includes the language

### Debug Mode

To see language detection details:

```python
# In detect_language function, add:
print(f"Detected: {result}")
print(f"Language: {language_code}, Confidence: {confidence}")
```

## Performance Impact

- **Detection latency**: ~100-200ms (acceptable)
- **No impact on conversation flow**
- **PDF generation unchanged**
- **Token usage**: Same as monolingual version

## Security Considerations

- User messages sent to Google for detection
- No storage of language preference beyond session
- All Google Cloud security policies apply
- Consider data residency requirements

## Testing Checklist

- [ ] Test each supported language greeting
- [ ] Verify phase transitions in each language
- [ ] Check PDF generation per language
- [ ] Test error handling (invalid credentials)
- [ ] Verify crisis messages in each language
- [ ] Test with mixed-language input
- [ ] Validate date formatting per language