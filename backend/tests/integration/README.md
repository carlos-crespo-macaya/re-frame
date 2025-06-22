# Integration Tests

This directory contains integration tests that require external services or API keys.

## Running Integration Tests

```bash
# Google AI Studio integration tests
GOOGLE_AI_REDACTED.py -v

# Run all integration tests (with required environment variables)
pytest tests/integration/ -v
```

## Test Categories

- `test_integration_google_ai.py` - Tests that make real API calls to Google AI Studio
- Additional integration tests will be added here as needed

These tests are separate from unit tests to avoid:
1. Requiring API keys for basic testing
2. Making external API calls during CI/CD
3. Cluttering the main test suite with slow integration tests