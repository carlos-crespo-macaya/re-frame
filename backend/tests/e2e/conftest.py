"""Test fixtures for E2E tests."""

import os
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def test_client():
    """Create an async test client for E2E tests."""
    # Set test environment
    os.environ["GEMINI_API_KEY"] = "test-api-key"
    
    # Import app here to avoid import errors
    from src.main import app
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        timeout=30.0  # 30 second timeout for E2E tests
    ) as client:
        yield client