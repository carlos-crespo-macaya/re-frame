# E2E Tests for CBT Assistant

This directory contains end-to-end tests for the CBT Assistant application using Playwright with Python.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Chrome/Chromium browser

### Running Tests Locally

1. **Using the test runner script (recommended):**
   ```bash
   cd tests/e2e
   ./run_tests.sh
   ```

2. **Manual setup:**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   playwright install chromium

   # Start services
   docker-compose -f ../../docker-compose.yml -f docker-compose.test.yml up -d

   # Run tests
   pytest
   ```

## 📁 Project Structure

```
e2e/
├── conftest.py          # Pytest configuration and fixtures
├── pytest.ini           # Pytest settings
├── requirements.txt     # Python dependencies
├── .env.test           # Test environment variables
├── docker-compose.test.yml  # Docker overrides for testing
├── run_tests.sh        # Test runner script
│
├── fixtures/           # Test data and fixtures
│   └── test_data.py   # Common test data
│
├── pages/             # Page Object Model
│   ├── base_page.py   # Base page class
│   └── home_page.py   # Home page objects
│
├── tests/             # Test suites
│   └── test_text_reframing.py  # Text mode tests
│
└── utils/             # Test utilities
    ├── docker_utils.py  # Docker management
    └── sse_utils.py     # SSE testing helpers
```

## 🧪 Running Specific Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_text_reframing.py

# Run specific test
pytest tests/test_text_reframing.py::TestTextReframing::test_basic_reframing_flow

# Run with markers
pytest -m smoke           # Run smoke tests only
pytest -m text_mode      # Run text mode tests only

# Run with options
pytest --headed          # Run with browser visible
pytest --slowmo 1000     # Slow down actions by 1 second
pytest -v               # Verbose output
pytest --maxfail=1      # Stop after first failure
```

## 🐛 Debugging Tests

### View Browser During Tests
```bash
HEADLESS=false pytest
```

### Enable Network Debugging
```bash
DEBUG_NETWORK=true pytest
```

### Keep Services Running After Tests
```bash
KEEP_SERVICES=true ./run_tests.sh
```

### Generate Playwright Trace
```bash
pytest --tracing on
playwright show-trace trace.zip
```

## 📋 Test Markers

- `@pytest.mark.smoke` - Core functionality tests
- `@pytest.mark.text_mode` - Text-based interaction tests
- `@pytest.mark.voice_mode` - Voice-based interaction tests
- `@pytest.mark.slow` - Tests that take longer to run

## 🔧 Configuration

### Environment Variables (.env.test)
- `FRONTEND_URL` - Frontend application URL (default: http://localhost:3000)
- `BACKEND_URL` - Backend API URL (default: http://localhost:8000)
- `HEADLESS` - Run browser in headless mode (default: true)
- `DEBUG_NETWORK` - Enable network request logging (default: false)
- `KEEP_SERVICES` - Keep Docker services running after tests (default: false)

### Docker Compose Override
The `docker-compose.test.yml` file provides test-specific configurations:
- Faster health checks
- Debug logging enabled
- Test environment variables

## 🚀 CI/CD Integration

Tests run automatically on:
- Push to main or develop branches
- Pull requests to main
- Manual workflow dispatch

See `.github/workflows/e2e-tests.yml` for CI configuration.

## 📝 Writing New Tests

1. **Create a new test file** in `tests/`
2. **Use Page Object Model** - Create page objects in `pages/`
3. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`
4. **Use fixtures** from `conftest.py`
5. **Add appropriate markers**

### Example Test
```python
@pytest.mark.smoke
@pytest.mark.asyncio
async def test_example(authenticated_page: Page, backend_ready):
    """Test description."""
    home = HomePage(authenticated_page)
    
    # Test implementation
    await home.enter_thought("Test thought")
    await home.submit_thought()
    
    response = await home.wait_for_response()
    assert response, "No response received"
```

## 🔍 Troubleshooting

### Services won't start
```bash
# Check Docker logs
docker-compose logs

# Rebuild services
docker-compose -f ../../docker-compose.yml -f docker-compose.test.yml build --no-cache
```

### Tests timeout
- Increase timeout in `conftest.py`
- Check service health: `docker-compose ps`
- Review service logs: `docker-compose logs backend`

### SSE connection issues
- Verify CORS settings in backend
- Check browser console for errors
- Use SSE debugging utilities in `utils/sse_utils.py`

## 🤝 Contributing

1. Write tests for new features
2. Ensure all tests pass locally
3. Add appropriate test markers
4. Update this README if needed
5. Submit PR with test results