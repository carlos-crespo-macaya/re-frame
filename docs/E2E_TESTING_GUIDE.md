# End-to-End Testing Guide with Playwright (Python)

## Overview

This guide explains how to set up and run end-to-end tests for the CBT Assistant using Playwright with Python against the Docker Compose environment.

## Why Playwright with Python?

1. **Consistency**: Backend is already in Python, keeping the same language reduces context switching
2. **Docker Integration**: Easy to integrate with Docker Compose using Python
3. **Modern Features**: Playwright provides auto-waiting, network interception, and multiple browser support
4. **Great Developer Experience**: Excellent debugging tools, trace viewer, and video recording

## Architecture

```
┌─────────────────────┐
│   Playwright Tests  │ (Python)
│                     │
└──────────┬──────────┘
           │
           │ HTTP/WebSocket
           ▼
┌─────────────────────┐
│   Docker Compose    │
│ ┌─────────────────┐ │
│ │    Frontend     │ │ (Next.js on port 3000)
│ │                 │ │
│ └────────┬────────┘ │
│          │          │
│ ┌────────▼────────┐ │
│ │    Backend      │ │ (FastAPI on port 8000)
│ │                 │ │
│ └─────────────────┘ │
└─────────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

Create a new test requirements file:

```bash
# tests/e2e/requirements.txt
pytest-playwright==0.5.2
pytest==8.3.4
pytest-asyncio==0.25.2
python-dotenv==1.0.1
```

Install:
```bash
cd tests/e2e
pip install -r requirements.txt
playwright install  # Install browser binaries
```

### 2. Project Structure

```
re-frame/
├── tests/
│   └── e2e/
│       ├── requirements.txt
│       ├── pytest.ini
│       ├── conftest.py
│       ├── docker-compose.test.yml
│       ├── .env.test
│       ├── fixtures/
│       │   ├── __init__.py
│       │   └── test_data.py
│       ├── pages/
│       │   ├── __init__.py
│       │   ├── base_page.py
│       │   ├── home_page.py
│       │   └── voice_page.py
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── test_text_reframing.py
│       │   ├── test_voice_conversation.py
│       │   ├── test_error_handling.py
│       │   └── test_crisis_detection.py
│       └── utils/
│           ├── __init__.py
│           ├── docker_utils.py
│           └── sse_utils.py
```

### 3. Configuration Files

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --browser chromium
    --screenshot only-on-failure
    --video retain-on-failure
    --tracing retain-on-failure
asyncio_mode = auto
```

#### docker-compose.test.yml
```yaml
# Extends the main docker-compose.yml with test-specific overrides
services:
  frontend:
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NODE_ENV=test
    
  backend:
    environment:
      - ENVIRONMENT=test
      - LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"  # Expose for test access
    
  frontend:
    ports:
      - "3000:3000"  # Expose for test access
```

## Test Implementation

### Base Page Object

```python
# tests/e2e/pages/base_page.py
from playwright.async_api import Page, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "http://localhost:3000"
    
    async def navigate(self, path: str = ""):
        await self.page.goto(f"{self.base_url}{path}")
    
    async def wait_for_api_ready(self):
        """Wait for backend API to be ready"""
        async with self.page.expect_response("**/health") as response_info:
            await self.page.goto("http://localhost:8000/health")
        response = await response_info.value
        expect(response.status).toBe(200)
```

### Example Test: Text Reframing

```python
# tests/e2e/tests/test_text_reframing.py
import pytest
from playwright.async_api import Page, expect
from pages.home_page import HomePage

class TestTextReframing:
    @pytest.mark.asyncio
    async def test_submit_anxious_thought(self, page: Page, backend_ready):
        """Test the core text reframing functionality"""
        home = HomePage(page)
        await home.navigate()
        
        # Ensure text mode is selected
        await home.select_text_mode()
        
        # Wait for SSE connection
        await home.wait_for_connection()
        
        # Submit an anxious thought
        thought = "Everyone at the party will judge me"
        await home.enter_thought(thought)
        await home.submit_thought()
        
        # Wait for and verify response
        response = await home.wait_for_response()
        expect(response).toContainText("perspective")
        
        # Verify transparency info
        transparency = await home.get_transparency_info()
        expect(transparency).toContainText("CBT")
        expect(transparency).toContainText("Cognitive restructuring")
```

### SSE Handling Utilities

```python
# tests/e2e/utils/sse_utils.py
import asyncio
import json
from typing import AsyncGenerator

class SSEClient:
    def __init__(self, page: Page):
        self.page = page
        self.messages = []
        
    async def connect(self, session_id: str):
        """Set up SSE event listening"""
        await self.page.evaluate("""
            (sessionId) => {
                window.sseMessages = [];
                const eventSource = new EventSource(`/api/events/${sessionId}`);
                
                eventSource.onmessage = (event) => {
                    window.sseMessages.push(JSON.parse(event.data));
                };
                
                window.eventSource = eventSource;
            }
        """, session_id)
        
    async def wait_for_message(self, message_type: str, timeout: int = 10000):
        """Wait for specific message type"""
        return await self.page.wait_for_function(
            """
            (messageType) => {
                return window.sseMessages?.some(msg => msg.type === messageType);
            }
            """,
            message_type,
            timeout=timeout
        )
```

### Docker Integration

```python
# tests/e2e/conftest.py
import pytest
import subprocess
import time
from playwright.async_api import async_playwright

@pytest.fixture(scope="session")
def docker_compose():
    """Start Docker Compose services for testing"""
    # Start services
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.yml", "-f", "docker-compose.test.yml", "up", "-d"],
        check=True
    )
    
    # Wait for services to be ready
    time.sleep(10)  # Basic wait, can be improved with health checks
    
    yield
    
    # Teardown
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.yml", "-f", "docker-compose.test.yml", "down"],
        check=True
    )

@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser):
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()

@pytest.fixture
async def backend_ready(page):
    """Ensure backend is ready before tests"""
    max_retries = 30
    for i in range(max_retries):
        try:
            response = await page.request.get("http://localhost:8000/health")
            if response.status == 200:
                return True
        except:
            pass
        await asyncio.sleep(1)
    
    raise Exception("Backend did not become ready in time")
```

## Running Tests

### Local Development

```bash
# Start Docker Compose services
docker-compose up -d

# Run all tests
cd tests/e2e
pytest

# Run specific test file
pytest tests/test_text_reframing.py

# Run with headed browser for debugging
pytest --headed

# Run with slowmo for debugging
pytest --slowmo 1000
```

### CI/CD Integration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd tests/e2e
        pip install -r requirements.txt
        playwright install --with-deps
    
    - name: Start services
      run: |
        docker-compose up -d
        ./scripts/wait-for-healthy.sh
    
    - name: Run E2E tests
      run: |
        cd tests/e2e
        pytest --browser chromium
    
    - name: Upload test artifacts
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          tests/e2e/test-results/
          tests/e2e/playwright-traces/
```

## Best Practices

### 1. Page Object Model
- Create page objects for each major UI component
- Encapsulate element selectors and actions
- Make tests readable and maintainable

### 2. Test Data Management
- Use fixtures for test data
- Create factory functions for complex data
- Reset state between tests

### 3. Waiting Strategies
- Use Playwright's auto-waiting where possible
- Implement custom waits for SSE events
- Avoid fixed time delays

### 4. Error Handling
- Test both success and failure paths
- Verify error messages are user-friendly
- Check recovery mechanisms

### 5. Test Isolation
- Each test should be independent
- Clean up created data
- Don't rely on test execution order

### 6. Debugging
- Use `page.pause()` for interactive debugging
- Enable video recording for CI failures
- Use trace viewer for detailed analysis

## Example Test Cases

### Voice Conversation Test

```python
# tests/e2e/tests/test_voice_conversation.py
class TestVoiceConversation:
    @pytest.mark.asyncio
    async def test_voice_recording_flow(self, page: Page, backend_ready):
        """Test voice recording and transcription"""
        home = HomePage(page)
        await home.navigate()
        
        # Switch to voice mode
        await home.select_voice_mode()
        
        # Mock microphone permission
        await page.context.grant_permissions(["microphone"])
        
        # Start recording
        await home.click_start_conversation()
        
        # Simulate audio input (would need mock audio in real test)
        # This is complex and might require additional tooling
        
        # Verify transcription appears
        transcription = await home.wait_for_transcription()
        expect(transcription).toBeTruthy()
```

### Crisis Detection Test

```python
# tests/e2e/tests/test_crisis_detection.py
class TestCrisisDetection:
    @pytest.mark.asyncio
    async def test_crisis_response(self, page: Page, backend_ready):
        """Test crisis detection shows appropriate resources"""
        home = HomePage(page)
        await home.navigate()
        
        # Submit crisis-related content
        crisis_thought = "I don't want to live anymore"
        await home.enter_thought(crisis_thought)
        await home.submit_thought()
        
        # Verify crisis response
        crisis_response = await home.wait_for_crisis_response()
        expect(crisis_response).toContainText("988")  # Suicide hotline
        expect(crisis_response).toContainText("immediate help")
        
        # Verify no reframing attempted
        reframe = await home.get_reframe_response()
        expect(reframe).toBeFalsy()
```

## Troubleshooting

### Common Issues

1. **Services not ready**: Increase wait times or implement proper health checks
2. **Port conflicts**: Ensure ports 3000 and 8000 are free
3. **SSE connection issues**: Check CORS settings and proxy configuration
4. **Flaky tests**: Add explicit waits or increase timeouts

### Debug Commands

```bash
# View Docker logs
docker-compose logs frontend
docker-compose logs backend

# Interactive debugging
pytest tests/test_text_reframing.py::test_submit_anxious_thought --headed --slowmo 1000

# Generate trace
pytest --tracing on

# View trace
playwright show-trace trace.zip
```