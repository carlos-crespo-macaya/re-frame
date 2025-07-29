# Feature Flags Behavior Analysis

## Current Implementation Status

### Backend Configuration
- **ConfigCat Integration**: ✅ Implemented but not configured
- **Current Mode**: Fallback mode (using hardcoded defaults)
- **SDK Key**: Not provided (CONFIGCAT_SDK_KEY environment variable is missing)

### Current Behavior

1. **Without ConfigCat SDK Key (Current State)**:
   - All feature flags return hardcoded default values
   - No dynamic updates possible
   - User targeting/segmentation not available
   - A/B testing not possible
   - Changes require code deployment

2. **Default Values**:
   ```json
   {
     "textModeEnabled": true,
     "voiceModeEnabled": true,
     "enabledLanguages": ["en", "es", "pt", "fr", "de", "it", "nl", "pl", "uk", "cs"]
   }
   ```

### Expected Behavior with ConfigCat

When a ConfigCat SDK key is configured:

1. **Dynamic Updates**:
   - Feature flags are fetched from ConfigCat dashboard
   - Changes propagate within 60 seconds (cache duration)
   - No code deployment needed for flag changes

2. **User Targeting**:
   - Flags can be targeted based on:
     - Session ID (X-Session-ID header)
     - User Language (X-User-Language header)
     - User Country (X-User-Country header)
   - Enable gradual rollouts (e.g., 10% of users get new feature)

3. **A/B Testing**:
   - Different user segments can get different feature configurations
   - Track feature adoption and usage patterns
   - Make data-driven decisions

### Frontend Behavior

1. **Feature Flag Provider**:
   - Fetches flags on mount
   - Caches in sessionStorage for resilience
   - Retries on failure (up to 3 times with exponential backoff)
   - Provides flags via React Context

2. **UI Behavior**:
   - Voice/Text toggle button only shows when BOTH modes are enabled
   - If only voice mode is enabled, defaults to voice
   - If only text mode is enabled, defaults to text
   - Language selector filters based on enabledLanguages

3. **Real-time Updates**:
   - Frontend polls backend every page load
   - Backend caches ConfigCat results for 60 seconds
   - Changes visible after refresh or navigation

## Testing Feature Flag Changes

### To Enable ConfigCat:

1. **Set up ConfigCat account** at https://configcat.com
2. **Add SDK key to backend**:
   ```bash
   docker run -e CONFIGCAT_SDK_KEY=your-sdk-key ... re-frame-backend
   ```

3. **Create feature flags in ConfigCat dashboard**:
   - `text_mode_enabled` (boolean)
   - `voice_mode_enabled` (boolean)
   - `language_en`, `language_es`, etc. (boolean for each language)

4. **Test scenarios**:
   - Disable voice mode: Set `voice_mode_enabled` to false
   - Enable only Spanish: Set all language flags to false except `language_es`
   - Target specific users: Use session ID targeting rules

### Current Limitations

1. **No Real-time Push**: Changes require page refresh
2. **60-second Cache**: Minimum delay for propagation
3. **Fallback Mode**: Always returns defaults without SDK key

## Verification

The feature flags are working as designed:
- ✅ Backend serves feature flags via API
- ✅ Frontend fetches and caches flags
- ✅ UI responds to flag values correctly
- ✅ Fallback mechanism works when ConfigCat unavailable
- ⚠️  Dynamic updates require ConfigCat SDK key configuration