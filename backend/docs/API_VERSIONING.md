# API Versioning Strategy

## Overview

This document outlines the versioning strategy for the re-frame API to ensure backward compatibility while allowing for evolution and improvements.

## Current Version

- **Version**: 0.1.0 (Alpha)
- **Base Path**: `/api`
- **Status**: Development

## Versioning Scheme

We follow Semantic Versioning (SemVer) with the format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

## URL Versioning Strategy

### Current Implementation (v0.x - Alpha)

During alpha development, we use a single API version:
```
https://api.re-frame.social/api/reframe/
https://api.re-frame.social/api/health
```

### Future Implementation (v1.0+)

When we reach v1.0, we'll implement URL-based versioning:
```
https://api.re-frame.social/api/v1/reframe/
https://api.re-frame.social/api/v2/reframe/
```

## Version Lifecycle

### 1. Alpha (v0.x)
- Rapid iteration allowed
- Breaking changes permitted with notice
- No deprecation period required
- Used for: Initial development and testing

### 2. Beta (v1.0-beta.x)
- API stabilizing
- Breaking changes discouraged
- 2-week deprecation notice for changes
- Used for: Production testing with early adopters

### 3. Stable (v1.0+)
- API contract guaranteed
- Breaking changes only in major versions
- 3-month deprecation period
- Used for: Production use

## Deprecation Policy

### Alpha/Beta Versions
- Deprecation notice: 2 weeks minimum
- Sunset period: 1 month after notice
- Communication: GitHub releases, API responses

### Stable Versions
- Deprecation notice: 3 months minimum
- Sunset period: 6 months after notice
- Communication: Email, GitHub, API responses, documentation

### Deprecation Headers

When an endpoint or version is deprecated:
```
X-API-Deprecation: true
X-API-Deprecation-Date: 2024-06-01
X-API-Deprecation-Info: Use /api/v2/reframe instead
Link: <https://docs.re-frame.social/api/migration>; rel="deprecation"
```

## Backward Compatibility Rules

### What We Guarantee

1. **Existing fields** in responses will not be removed
2. **Required fields** in requests will not be added
3. **Endpoint URLs** will not change within a major version
4. **HTTP methods** will remain the same
5. **Authentication methods** will be backward compatible

### What May Change

1. **New optional fields** may be added to responses
2. **New optional parameters** may be added to requests
3. **New endpoints** may be added
4. **Response field order** may change (use names, not positions)
5. **Error message text** may be improved

## Migration Guide Template

For each major version change, provide:

```markdown
# Migrating from v1 to v2

## Breaking Changes
- [ ] Change 1: Description and migration path
- [ ] Change 2: Description and migration path

## New Features
- Feature 1: How to use
- Feature 2: How to use

## Deprecated Features
- Feature 1: Replacement available
- Feature 2: Will be removed in v3

## Code Examples
### Before (v1)
```python
# Old code
```

### After (v2)
```python
# New code
```
```

## Version Discovery

### 1. Via Headers
All responses include version information:
```
X-API-Version: 0.1.0
```

### 2. Via Version Endpoint
```
GET /api/version

{
  "version": "0.1.0",
  "supported_versions": ["0.1.0"],
  "latest_stable": null,
  "deprecation_info": {}
}
```

### 3. Via OpenAPI Spec
```
GET /api/openapi.json

{
  "openapi": "3.0.0",
  "info": {
    "version": "0.1.0",
    "x-api-versions": {
      "supported": ["0.1.0"],
      "deprecated": [],
      "sunset": []
    }
  }
}
```

## Client Best Practices

### 1. Version Pinning
Always specify the API version you're using:
```python
API_VERSION = "0.1.0"
BASE_URL = f"https://api.re-frame.social/api"  # Will be /api/v1 in future
```

### 2. Handle Version Headers
Check for deprecation warnings:
```python
response = requests.get(url)
if response.headers.get('X-API-Deprecation') == 'true':
    log_deprecation_warning(response.headers)
```

### 3. Graceful Degradation
Handle missing fields gracefully:
```python
# Good
confidence = response.get('transparency', {}).get('confidence', 0.5)

# Bad - will break if field is removed
confidence = response['transparency']['confidence']
```

### 4. Feature Detection
Check for feature availability:
```python
def supports_batch_processing(api_version):
    major, minor, patch = api_version.split('.')
    return int(major) >= 1 and int(minor) >= 2
```

## Implementation Checklist

When implementing a new version:

- [ ] Update version in `config/settings.py`
- [ ] Update OpenAPI spec version
- [ ] Add version to supported versions list
- [ ] Update deprecation headers for old versions
- [ ] Update documentation
- [ ] Create migration guide
- [ ] Add version-specific tests
- [ ] Update client SDKs
- [ ] Notify users via appropriate channels

## Version-Specific Features

### v0.1.0 (Current)
- Basic reframing endpoint
- Single framework processing (CBT)
- Session management
- Rate limiting

### v0.2.0 (Planned)
- Multi-framework support (CBT, DBT, ACT, Stoicism)
- Framework selection intelligence
- Enhanced transparency data
- Batch processing

### v1.0.0 (Future)
- Stable API contract
- Firebase authentication
- User preferences
- Conversation memory
- WebSocket support for real-time

## Testing Strategy

### Version Compatibility Tests
```python
@pytest.mark.parametrize("version", ["0.1.0", "0.2.0"])
def test_endpoint_compatibility(version):
    """Test that endpoints work across versions."""
    # Test implementation
```

### Deprecation Tests
```python
def test_deprecation_headers():
    """Test that deprecated endpoints return proper headers."""
    response = client.get("/api/old-endpoint")
    assert "X-API-Deprecation" in response.headers
```

## Communication Plan

### 1. Pre-release (2 weeks before)
- GitHub release notes
- API documentation update
- Email to registered developers

### 2. Release Day
- Update production API
- Update documentation site
- Post on GitHub discussions
- Update status page

### 3. Post-release (1 week after)
- Monitor error rates
- Gather feedback
- Plan patches if needed

## Emergency Rollback

If a version causes critical issues:

1. Rollback to previous version within 1 hour
2. Notify all users immediately
3. Post-mortem within 48 hours
4. Fix and re-release with patch version

## Future Considerations

### GraphQL Support
- May introduce GraphQL endpoint at `/api/graphql`
- REST API will continue to be supported
- Version strategy will apply to both

### gRPC Support
- For high-performance scenarios
- Separate versioning scheme
- Proto files will be versioned

### WebSocket Support
- For real-time features
- Version negotiation during handshake
- Graceful upgrade/downgrade