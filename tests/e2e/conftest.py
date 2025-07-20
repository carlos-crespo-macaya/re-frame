"""
Pytest configuration for E2E tests using REAL backend services without mocks.
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
    
    # Ensure we're in the correct directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Start services with both compose files
    compose_command = [
        'docker-compose',
        '-f', os.path.join(test_dir, '../../docker-compose.yml'),
        '-f', os.path.join(test_dir, 'docker-compose.test.yml'),
        'up', '-d', '--build'
    ]
    
    print(f"Running command: {' '.join(compose_command)}")
    subprocess.run(compose_command, check=True)
    
    # Wait for services to be healthy
    if not wait_for_services():
        # Show logs if services fail to start
        subprocess.run(['docker-compose', 'logs'], cwd=test_dir)
        raise RuntimeError("Services did not become healthy in time")
    
    yield
    
    # Teardown
    if os.getenv('KEEP_SERVICES', 'false').lower() != 'true':
        print("Stopping Docker Compose services...")
        subprocess.run([
            'docker-compose',
            '-f', os.path.join(test_dir, '../../docker-compose.yml'),
            '-f', os.path.join(test_dir, 'docker-compose.test.yml'),
            'down', '-v'
        ], check=True)


@pytest.fixture(scope='function')
async def browser() -> AsyncGenerator[Browser, None]:
    """Create a browser instance for each test."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
            ]
        )
        yield browser
        await browser.close()


@pytest.fixture(scope='function')
async def context(browser: Browser) -> AsyncGenerator[BrowserContext, None]:
    """Create a new browser context for each test - NO MOCKS."""
    context = await browser.new_context(
        viewport={'width': 1280, 'height': 720},
        ignore_https_errors=True,
        locale='en-US',
        timezone_id='America/New_York',
        # Grant permissions for voice tests
        permissions=['microphone']
    )
    
    # Set up console message collection
    context.on('console', lambda msg: print(f'Browser console: {msg.text}'))
    
    yield context
    await context.close()


@pytest.fixture(scope='function')
async def page(context: BrowserContext) -> AsyncGenerator[Page, None]:
    """Create a new page for each test - NO ROUTE MOCKS."""
    page = await context.new_page()
    
    # Set up logging for debugging
    # page.on('console', lambda msg: print(f'Console message'))
    # page.on('pageerror', lambda error: print(f'Page error'))
    
    if os.getenv('DEBUG_NETWORK', 'false').lower() == 'true':
        page.on('request', lambda req: print(f'Request: {req.method} {req.url}'))
        page.on('response', lambda res: print(f'Response: {res.status} {res.url}'))
    
    yield page
    await page.close()


@pytest.fixture
def session_id(worker_id) -> str:
    """Generate a unique session ID for each test."""
    return f"test-session-{worker_id}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
async def authenticated_page(page: Page) -> Page:
    """Provide a page that has already navigated to the app."""
    await page.goto(FRONTEND_URL)
    # Don't wait for networkidle as SSE keeps connection open
    await page.wait_for_load_state('domcontentloaded')
    # Wait for React to render
    await page.wait_for_timeout(2000)
    return page


def wait_for_services(timeout: int = 120) -> bool:
    """Wait for Docker services to be healthy."""
    import requests
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Check backend health
            backend_response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            backend_data = backend_response.json()
            if backend_response.status_code == 200 and backend_data.get("status") == "healthy":
                print(f"Backend healthy: {backend_data}")
                
                # Check frontend
                frontend_response = requests.get(FRONTEND_URL, timeout=5)
                if frontend_response.status_code == 200:
                    print("Frontend is accessible!")
                    
                    # Give services a bit more time to fully initialize
                    time.sleep(5)
                    return True
                    
        except requests.exceptions.RequestException as e:
            print(f"Waiting for services... {e}")
        
        time.sleep(2)
    
    return False


@pytest.fixture
async def wait_for_backend(page: Page) -> None:
    """Ensure backend is ready before test execution."""
    max_retries = 30
    
    for i in range(max_retries):
        try:
            response = await page.request.get(f"{BACKEND_URL}/health")
            data = await response.json()
            if response.status == 200 and data.get("status") == "healthy":
                print(f"Backend ready: {data}")
                return
        except Exception as e:
            print(f"Backend not ready yet: {e}")
        
        await asyncio.sleep(2)
    
    raise RuntimeError("Backend did not become ready in time")


# Pytest hooks
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "real_backend: test uses real backend without mocks")
    config.addinivalue_line("markers", "text_workflow: test for text conversation workflow")
    config.addinivalue_line("markers", "voice_workflow: test for voice conversation workflow")
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add real_backend marker to all tests
        item.add_marker(pytest.mark.real_backend)
        item.add_marker(pytest.mark.integration)