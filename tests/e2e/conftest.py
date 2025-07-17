"""
Pytest configuration and fixtures for E2E tests.
"""
import asyncio
import os
import subprocess
import time
import uuid
from typing import Generator, AsyncGenerator

import pytest
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from dotenv import load_dotenv

# Load test environment variables
load_dotenv('.env.test')

# Configuration
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
DOCKER_COMPOSE_FILE = os.getenv('DOCKER_COMPOSE_FILE', '../../docker-compose.yml')
HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'


@pytest.fixture(scope='session')
def docker_services() -> Generator[None, None, None]:
    """Start Docker Compose services for the test session."""
    print("Starting Docker Compose services...")
    
    # Start services
    compose_command = [
        'docker-compose',
        '-f', DOCKER_COMPOSE_FILE,
        'up', '-d'
    ]
    
    # Add test override file if it exists
    test_compose = '../../docker-compose.test.yml'
    if os.path.exists(test_compose):
        compose_command.extend(['-f', test_compose])
    
    subprocess.run(compose_command, check=True, cwd=os.path.dirname(__file__))
    
    # Wait for services to be healthy
    if not wait_for_services():
        raise RuntimeError("Services did not become healthy in time")
    
    yield
    
    # Teardown (optional - comment out to keep services running)
    if os.getenv('KEEP_SERVICES', 'false').lower() != 'true':
        print("Stopping Docker Compose services...")
        subprocess.run([
            'docker-compose',
            '-f', DOCKER_COMPOSE_FILE,
            'down'
        ], check=True, cwd=os.path.dirname(__file__))


@pytest.fixture(scope='function')
async def browser() -> AsyncGenerator[Browser, None]:
    """Create a browser instance for each test."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        yield browser
        await browser.close()


@pytest.fixture(scope='function')
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Create a new browser context for each test."""
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        ignore_https_errors=True,
        locale='en-US',
        timezone_id='America/New_York',
    )
    
    # Set up console message collection
    context.on('console', lambda msg: print(f'Browser console: {msg.text}'))
    
    yield context
    await context.close()


@pytest.fixture(scope='function')
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Create a new page for each test."""
    page = await context.new_page()
    
    # Set up request/response logging for debugging
    if os.getenv('DEBUG_NETWORK', 'false').lower() == 'true':
        page.on('request', lambda req: print(f'Request: {req.method} {req.url}'))
        page.on('response', lambda res: print(f'Response: {res.status} {res.url}'))
    
    yield page
    await page.close()


@pytest.fixture
def session_id() -> str:
    """Generate a unique session ID for each test."""
    return f"test-session-{uuid.uuid4().hex[:8]}"


@pytest.fixture
async def authenticated_page(page: Page) -> Page:
    """Provide a page that has already navigated to the app."""
    await page.goto(FRONTEND_URL)
    # Don't wait for networkidle as SSE keeps connection open
    await page.wait_for_load_state('domcontentloaded')
    # Wait a bit for React to render
    await page.wait_for_timeout(2000)
    return page


def wait_for_services(timeout: int = 60) -> bool:
    """Wait for Docker services to be healthy."""
    import requests
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Check backend health
            backend_response = requests.get(f"{BACKEND_URL}/health", timeout=2)
            if backend_response.status_code != 200:
                time.sleep(1)
                continue
            
            # Check frontend (Next.js might not have a health endpoint)
            frontend_response = requests.get(FRONTEND_URL, timeout=2)
            if frontend_response.status_code == 200:
                print("Services are healthy!")
                return True
                
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
    
    return False


@pytest.fixture
async def backend_ready(page: Page) -> None:
    """Ensure backend is ready before test execution."""
    max_retries = 30
    
    for i in range(max_retries):
        try:
            response = await page.request.get(f"{BACKEND_URL}/health")
            if response.status == 200:
                return
        except Exception:
            pass
        
        await asyncio.sleep(1)
    
    raise RuntimeError("Backend did not become ready in time")


# Pytest hooks
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "text_mode: mark test as text mode test")
    config.addinivalue_line("markers", "voice_mode: mark test as voice mode test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add integration marker to all tests by default
        item.add_marker(pytest.mark.integration)
        
        # Add mode-specific markers based on test name
        if 'voice' in item.nodeid:
            item.add_marker(pytest.mark.voice_mode)
        elif 'text' in item.nodeid:
            item.add_marker(pytest.mark.text_mode)