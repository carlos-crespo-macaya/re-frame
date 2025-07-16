"""Pytest configuration for backend tests."""

import sys
from pathlib import Path


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add the backend directory to Python path for imports
    backend_dir = Path(__file__).parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # Add test stubs to Python path for modules that might not be installed
    stubs_dir = Path(__file__).parent / "stubs"
    if str(stubs_dir) not in sys.path:
        sys.path.insert(0, str(stubs_dir))


# Common fixtures can be added here as needed