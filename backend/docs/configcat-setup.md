# ConfigCat Feature Flags Setup

This document describes how to set up and use ConfigCat feature flags in the CBT Assistant backend.

## Overview

The backend uses ConfigCat for feature flag management, allowing gradual rollout of features and A/B testing. The integration follows the singleton pattern and provides graceful fallback when ConfigCat is unavailable.

## Setup

### 1. Environment Variable

Set the ConfigCat SDK key in your environment:

```bash
export CONFIGCAT_SDK_KEY="YOUR-SDK-KEY-HERE"
```

Or add to your `.env` file:

```
CONFIGCAT_SDK_KEY=YOUR-SDK-KEY-HERE
```

### 2. ConfigCat Dashboard Setup

In the ConfigCat dashboard, create the following feature flags:

#### Communication Mode Flags
- `text_mode_enabled` (boolean) - Controls text mode availability
- `voice_mode_enabled` (boolean) - Controls voice mode availability

#### Language Feature Flags
- `language_en` (boolean) - English support
- `language_es` (boolean) - Spanish support
- `language_pt` (boolean) - Portuguese support
- `language_fr` (boolean) - French support
- `language_de` (boolean) - German support
- `language_it` (boolean) - Italian support
- `language_nl` (boolean) - Dutch support
- `language_pl` (boolean) - Polish support
- `language_uk` (boolean) - Ukrainian support
- `language_cs` (boolean) - Czech support

## API Endpoint

The feature flags are exposed via the API endpoint:

```
GET /api/feature-flags
```

### Response Format

```json
{
  "textModeEnabled": true,
  "voiceModeEnabled": true,
  "enabledLanguages": ["en", "es", "pt", "fr", "de", "it", "nl", "pl", "uk", "cs"]
}
```

### Headers for User Targeting

You can pass the following headers for user-specific targeting:

- `X-Session-ID`: Unique session identifier
- `X-User-Language`: User's preferred language
- `X-User-Country`: User's country code

Example:
```bash
curl -H "X-Session-ID: user-123" \
     -H "X-User-Language: es" \
     -H "X-User-Country: ES" \
     http://localhost:8000/api/feature-flags
```

## Implementation Details

### Auto-polling

The ConfigCat client uses auto-polling mode with 60-second intervals (default). The API response includes cache headers matching this interval:

```
Cache-Control: private, max-age=60
```

### Fallback Behavior

When ConfigCat is unavailable or no SDK key is provided:
- All communication modes are enabled by default
- All supported languages are enabled by default
- Warnings are logged but the service continues to function

### Singleton Pattern

The ConfigCat client is implemented as a singleton to ensure efficient resource usage:

```python
from src.utils.configcat_flags import get_configcat_flags

flags = get_configcat_flags()
is_text_enabled = flags.is_enabled("text_mode_enabled")
```

## Testing

### Unit Tests
Run unit tests for ConfigCat integration:
```bash
uv run pytest tests/test_configcat_feature_flags.py -v
```

### Integration Tests
Run API integration tests:
```bash
uv run pytest tests/test_feature_flag_router.py -v
```

### Manual Testing
Test the API endpoint:
```bash
# Without ConfigCat SDK key (fallback mode)
curl http://localhost:8000/api/feature-flags

# With user context
curl -H "X-Session-ID: test-123" http://localhost:8000/api/feature-flags
```

## Monitoring

Feature flag evaluations are logged with structured logging:

- `configcat_client_initialized` - Client successfully initialized
- `configcat_sdk_key_missing` - No SDK key found, using fallback
- `configcat_initialization_failed` - Client initialization failed
- `feature_flags_evaluated` - Flags evaluated for a user
- `feature_flags_api_error` - API endpoint error

## Best Practices

1. **Gradual Rollout**: Use percentage-based targeting for new features
2. **User Segmentation**: Target specific user groups for A/B testing
3. **Monitoring**: Watch logs for fallback mode activation
4. **Testing**: Always test with and without SDK key
5. **Caching**: Respect the 60-second cache interval for performance