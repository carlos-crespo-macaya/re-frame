# Integration Tests

This directory contains integration tests that require external services or API keys.

## Running Integration Tests

```bash
# Run all integration tests (with required environment variables)
pytest tests/integration/ -v
```

## Test Categories

- Additional integration tests will be added here as needed for:
  - Google AI Studio API integration
  - Firebase/Firestore integration  
  - External service endpoints

These tests are separate from unit tests to avoid:
1. Requiring API keys for basic testing
2. Making external API calls during CI/CD
3. Cluttering the main test suite with slow integration tests