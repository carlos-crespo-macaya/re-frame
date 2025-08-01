# ConfigCat Feature Flags Integration

## Status: IMPLEMENTED ✅

This document describes the implemented ConfigCat feature flags integration in the re-frame CBT Assistant application. The implementation follows a **backend-first approach** where feature flags are evaluated on the backend and consumed by the frontend via API.

## Implementation Overview

### What Was Built
1. **ConfigCat Client Wrapper** (`/backend/src/utils/configcat_flags.py`)
   - Wraps ConfigCat SDK for clean integration
   - Handles errors gracefully with fallback to defaults
   - Supports user targeting based on session attributes

2. **Feature Flags API** (`/backend/src/routers/feature_flags.py`)
   - REST endpoint: `GET /api/feature-flags`
   - Returns evaluated flags for the current user
   - Supports user context via headers

3. **Migration Support** (`/backend/src/utils/feature_flags_migration.py`)
   - Backward compatibility with existing environment-based flags
   - Smooth transition path for gradual migration

### Implemented Feature Flags
1. **Mode Control:**
   - `text_mode_enabled` - Enable/disable text conversations
   - `voice_mode_enabled` - Enable/disable voice conversations

2. **Language Support:**
   - `language_en` - English
   - `language_es` - Spanish  
   - `language_pt` - Portuguese
   - `language_fr` - French
   - `language_de` - German
   - `language_it` - Italian
   - `language_nl` - Dutch
   - `language_pl` - Polish
   - `language_uk` - Ukrainian
   - `language_cs` - Czech

## Architecture

### Backend-First Implementation

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  ConfigCat  │────▶│   Backend   │────▶│  Frontend   │
│   Service   │     │   FastAPI  │     │  Next.js   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │
       │             ┌──────▼──────┐      ┌─────▼─────┐
       └────────────▶│   Feature   │      │  Cached   │
                     │ Evaluation  │      │   Flags   │
                     └──────────────┘      └───────────┘
```

**Key Benefits:**
- ✅ Security: SDK key remains on backend
- ✅ Performance: 60-second cache aligns with ConfigCat polling
- ✅ User targeting: Full session context available
- ✅ Fallback: Defaults ensure app works without ConfigCat

## API Usage

### Endpoint Details

**GET /api/feature-flags**

**Request Headers (Optional):**
```
X-Session-ID: <session-identifier>
X-User-Language: <language-code>
X-User-Country: <country-code>
```

**Response:**
```json
{
  "flags": {
    "text_mode_enabled": true,
    "voice_mode_enabled": true,
    "language_en": true,
    "language_es": true,
    "language_pt": false,
    "language_fr": false,
    "language_de": false,
    "language_it": false,
    "language_nl": false,
    "language_pl": false,
    "language_uk": false,
    "language_cs": false
  },
  "modes": {
    "text_enabled": true,
    "voice_enabled": true
  },
  "languages": ["en", "es"]
}
```

**Cache Headers:**
```
Cache-Control: private, max-age=60
```

## Configuration

### Environment Variables

```bash
# Required for ConfigCat integration
CONFIGCAT_SDK_KEY=your-sdk-key-here
```

### ConfigCat Dashboard Setup

1. **Create Feature Flags:**
   ```
   text_mode_enabled (Boolean, default: ON)
   voice_mode_enabled (Boolean, default: ON)
   language_en (Boolean, default: ON)
   language_es (Boolean, default: ON)
   language_pt (Boolean, default: ON)
   language_fr (Boolean, default: ON)
   language_de (Boolean, default: ON)
   language_it (Boolean, default: ON)
   language_nl (Boolean, default: ON)
   language_pl (Boolean, default: ON)
   language_uk (Boolean, default: ON)
   language_cs (Boolean, default: ON)
   ```

2. **Targeting Rules (Optional):**
   - Target by session ID
   - Target by user language preference
   - Target by country
   - Percentage-based rollouts

## Frontend Integration Guide

### Example React Integration

```typescript
// frontend/lib/feature-flags/use-feature-flags.ts
import { useEffect, useState } from 'react';
import { apiClient } from '@/lib/api/client';

interface FeatureFlags {
  flags: Record<string, boolean>;
  modes: {
    text_enabled: boolean;
    voice_enabled: boolean;
  };
  languages: string[];
}

export function useFeatureFlags() {
  const [flags, setFlags] = useState<FeatureFlags | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetchFlags();
  }, []);

  const fetchFlags = async () => {
    try {
      const response = await apiClient.get('/api/feature-flags');
      setFlags(response.data);
      
      // Cache for 60 seconds
      sessionStorage.setItem('feature-flags', JSON.stringify({
        data: response.data,
        timestamp: Date.now()
      }));
    } catch (err) {
      // Try to use cached flags
      const cached = sessionStorage.getItem('feature-flags');
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < 60000) { // 60 seconds
          setFlags(data);
          return;
        }
      }
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return { flags, loading, error, refetch: fetchFlags };
}
```

### Example Component Usage

```typescript
// frontend/components/VoiceControls.tsx
import { useFeatureFlags } from '@/lib/feature-flags/use-feature-flags';

export function VoiceControls() {
  const { flags, loading } = useFeatureFlags();
  
  if (loading) return <Skeleton />;
  
  if (!flags?.modes.voice_enabled) {
    return null; // Voice mode disabled
  }
  
  return (
    <div className="voice-controls">
      {/* Voice UI components */}
    </div>
  );
}
```

```typescript
// frontend/components/LanguageSelector.tsx
export function LanguageSelector() {
  const { flags } = useFeatureFlags();
  
  const availableLanguages = flags?.languages || ['en'];
  
  return (
    <Select>
      {availableLanguages.map(lang => (
        <Option key={lang} value={lang}>
          {getLanguageName(lang)}
        </Option>
      ))}
    </Select>
  );
}
```

## Testing

### Unit Tests
- ✅ ConfigCat client wrapper tests
- ✅ Feature flag API endpoint tests
- ✅ Fallback behavior tests
- ✅ User targeting tests

### Integration Tests
- ✅ API integration with ConfigCat
- ✅ Mode exclusivity scenarios
- ✅ User context propagation

### Test Coverage
- All critical paths tested
- Mocking strategy for ConfigCat SDK
- Error scenarios covered

## Migration from Old System

### Migration Helper Available
The `feature_flags_migration.py` module provides:
- Backward compatibility with environment-based flags
- Parallel evaluation for monitoring
- Gradual migration support

### Migration Steps
1. Deploy ConfigCat integration alongside existing system
2. Monitor for any discrepancies
3. Gradually move flags to ConfigCat
4. Remove old system once all flags migrated

## Monitoring

### Log Events
- `configcat_client_initialized` - Successful initialization
- `configcat_sdk_key_missing` - Fallback mode activated
- `configcat_evaluation_failed` - Error during flag evaluation
- `feature_flags_evaluated` - Successful evaluation with context
- `feature_flags_api_error` - API endpoint errors

### Key Metrics
- API response time (target: <50ms)
- Cache hit rate (60-second TTL)
- Fallback activation frequency
- Feature flag evaluation errors

## Best Practices

### Flag Naming Convention
- Mode flags: `{mode}_mode_enabled`
- Language flags: `language_{code}`
- Feature flags: `{feature}_enabled`

### User Targeting
- Use session ID as primary identifier
- Include language and country for targeting
- Keep user context minimal for privacy

### Performance
- 60-second cache aligns with ConfigCat polling
- Frontend should cache responses
- Use sessionStorage for browser caching

## Security Considerations

1. **SDK Key Protection**
   - Backend-only SDK key usage
   - Never expose to frontend
   - Rotate quarterly

2. **User Privacy**
   - Minimal user context
   - No PII in targeting rules
   - Session-based identification

3. **Fallback Safety**
   - All features enabled by default
   - Graceful degradation
   - No breaking changes on failure

## Future Enhancements

### Potential New Flags
1. **Feature Flags:**
   - `reactive_greeting_enabled` - Dynamic greeting behavior
   - `natural_conversation_enabled` - Advanced AI features
   - `debug_mode_enabled` - Developer tools visibility

2. **Experiment Flags:**
   - `ui_variant_{name}` - A/B test UI variations
   - `prompt_variant_{name}` - Test different AI prompts

3. **Operational Flags:**
   - `maintenance_mode_enabled` - Service maintenance
   - `rate_limit_override` - Dynamic rate limiting

### Advanced Targeting
- User cohorts based on behavior
- Geographic targeting
- Time-based feature releases
- Progressive rollouts by percentage

## Conclusion

The ConfigCat integration is fully implemented and tested. It provides a robust, secure, and performant way to manage feature flags across the CBT Assistant application. The backend-first approach ensures security while maintaining flexibility for future enhancements.