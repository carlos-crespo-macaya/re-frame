"""Pytest configuration for backend tests."""

import sys
from pathlib import Path


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Add the backend directory to Python path for imports
    backend_dir = Path(__file__).parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    # Ensure repository root (two levels up) is importable so that optional
    # helper modules such as ``sitecustomize`` and the *E2E* package stubs are
    # discoverable even when the working directory is ``backend``.
    repo_root = backend_dir.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    # Add test stubs to Python path for modules that might not be installed
    stubs_dir = Path(__file__).parent / "stubs"
    if str(stubs_dir) not in sys.path:
        sys.path.insert(0, str(stubs_dir))


# ---------------------------------------------------------------------------
# Collection hooks
# ---------------------------------------------------------------------------


def pytest_ignore_collect(path, config):  # noqa: D401 – pytest naming
    """Skip E2E playwright tests during the backend unit-test run.

    These tests live under ``tests/e2e`` at the repository root and require a
    running frontend/backend stack plus the Playwright browser binaries.  They
    are out of scope for the lightweight backend unit-test suite executed in
    CI.  By returning *True* for matching paths we instruct *pytest* to ignore
    them completely, avoiding import-time errors and heavy dependencies.
    """

    # We receive *path* as a ``py.path.local`` / ``Path``-like object.
    return "tests/e2e" in str(path)


# Common fixtures can be added here as needed
