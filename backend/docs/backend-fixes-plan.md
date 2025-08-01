# Backend Fixes Plan

## Overview
This document outlines the fixes needed to resolve backend test failures and improve code coverage to meet the 80% requirement.

## 1. ConfigCat Integration Test Failures

### Root Cause Analysis
The integration tests are failing because there's a **mismatch between the test expectations and the actual API response structure**.

**Test Expectation:**
```json
{
  "flags": {
    "text_mode_enabled": true,
    "voice_mode_enabled": true
  },
  "modes": {
    "text_enabled": true,
    "voice_enabled": true
  },
  "languages": ["en", "es", ...]
}
```

**Actual API Response (from FeatureFlagsResponse model):**
```json
{
  "textModeEnabled": true,
  "voiceModeEnabled": true,
  "enabledLanguages": ["en", "es", ...]
}
```

### Solution
The tests are looking for a different response structure than what the API actually returns. We have two options:

**Option A (Recommended): Update the tests to match the actual API response**
- Update all integration tests to expect the correct field names
- This maintains consistency with the frontend expectations

**Option B: Change the API response to match test expectations**
- Would require updating the frontend client
- Not recommended as it would break existing integrations

### Code Changes Needed

**File: `/backend/tests/integration/test_configcat_integration.py`**

Replace all occurrences of:
- `data["flags"]["text_mode_enabled"]` → `data["textModeEnabled"]`
- `data["flags"]["voice_mode_enabled"]` → `data["voiceModeEnabled"]`
- `data["modes"]["text_enabled"]` → `data["textModeEnabled"]`
- `data["modes"]["voice_enabled"]` → `data["voiceModeEnabled"]`
- `data["languages"]` → `data["enabledLanguages"]`

## 2. Test Coverage Improvement Strategy

### Current Coverage: 74.81% (Need: 80%)

### Files with Low Coverage:
1. **`src/voice/stream_handler.py`** - 27% coverage (38/52 lines uncovered)
2. **`src/voice/session_manager.py`** - 54% coverage (67/147 lines uncovered)
3. **`src/utils/performance_monitor.py`** - 80% coverage (24/123 lines uncovered)
4. **`src/utils/configcat_flags.py`** - Unknown (need to check)
5. **`src/routers/feature_flags.py`** - Unknown (need to check)

### Priority Order for Test Coverage:
1. **High Priority - Voice Components** (biggest coverage gap):
   - `src/voice/stream_handler.py` - Add unit tests for all stream handling methods
   - `src/voice/session_manager.py` - Add tests for session lifecycle, cleanup, and error handling

2. **Medium Priority - Utility Components**:
   - `src/utils/performance_monitor.py` - Add tests for periodic summary logging
   - `src/utils/configcat_flags.py` - Ensure all flag evaluation paths are tested

3. **Low Priority - Already Well Covered**:
   - Focus on the above first before optimizing already well-covered files

## 3. OpenAPI Schema Integration

### Current Status
✅ The feature-flags endpoint IS properly included in the OpenAPI schema at path `/api/feature-flags/`

### Verification Steps
1. Run `uv run poe export-openapi` to generate the schema
2. The endpoint is already included with proper models
3. Ensure CI/CD pipeline always exports fresh schema before frontend build

### Important Note
The endpoint path in the schema includes a trailing slash: `/api/feature-flags/` (not `/api/feature-flags`). This is because the router prefix includes the full path and the route is mounted at `/`.

### Recommended CI/CD Addition
Add to GitHub Actions workflow:
```yaml
- name: Export OpenAPI Schema
  run: |
    cd backend
    uv run poe export-openapi
    
- name: Verify Schema Contains All Endpoints
  run: |
    # Check that feature-flags endpoint is in schema
    grep -q '"path": "/api/feature-flags"' frontend/openapi.json || exit 1
```

## 4. Implementation Priority

### Phase 1: Fix Failing Tests (Immediate)
1. Update ConfigCat integration tests to match actual API response
2. Run tests to verify fixes

### Phase 2: Improve Test Coverage (High Priority)
1. Add comprehensive tests for `src/voice/stream_handler.py`
2. Add tests for `src/voice/session_manager.py` 
3. Add missing tests for `src/utils/performance_monitor.py`

### Phase 3: Ensure API Contract (Medium Priority)
1. Add automated OpenAPI schema validation in CI
2. Create integration test that validates all endpoints are in schema
3. Add pre-commit hook to update schema when routes change

## 5. Specific Test Examples Needed

### For `src/voice/stream_handler.py`:
```python
# Test WebSocket message handling
# Test audio chunk processing
# Test error handling and reconnection
# Test stream lifecycle (start, process, close)
```

### For `src/voice/session_manager.py`:
```python
# Test session creation and cleanup
# Test concurrent session limits
# Test session timeout handling
# Test error recovery scenarios
```

### For `src/utils/performance_monitor.py`:
```python
# Test metric collection
# Test periodic summary generation
# Test metric aggregation
# Test cleanup of old metrics
```

## 6. Quick Fix Script

To immediately fix the failing tests, run:
```bash
cd backend

# Fix the integration tests
sed -i '' 's/data\["flags"\]\["text_mode_enabled"\]/data["textModeEnabled"]/g' tests/integration/test_configcat_integration.py
sed -i '' 's/data\["flags"\]\["voice_mode_enabled"\]/data["voiceModeEnabled"]/g' tests/integration/test_configcat_integration.py
sed -i '' 's/data\["modes"\]\["text_enabled"\]/data["textModeEnabled"]/g' tests/integration/test_configcat_integration.py
sed -i '' 's/data\["modes"\]\["voice_enabled"\]/data["voiceModeEnabled"]/g' tests/integration/test_configcat_integration.py
sed -i '' 's/data\["languages"\]/data["enabledLanguages"]/g' tests/integration/test_configcat_integration.py

# Run tests to verify
uv run pytest tests/integration/test_configcat_integration.py -v
```

## 7. Long-term Recommendations

1. **API Contract Testing**: Implement contract tests between frontend and backend
2. **Schema-First Development**: Consider using OpenAPI schema as source of truth
3. **Coverage Monitoring**: Add coverage badges and fail builds on coverage drop
4. **Voice Module Testing**: Create comprehensive test suite for voice features
5. **Integration Test Environment**: Use testcontainers for better isolation

## 8. Validation Checklist

- [ ] All ConfigCat integration tests pass
- [ ] Test coverage reaches 80% or higher
- [ ] OpenAPI schema includes all endpoints
- [ ] Frontend client can be generated without errors
- [ ] No regression in existing functionality