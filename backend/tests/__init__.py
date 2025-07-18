"""Tests for Reframe Agents."""

# ---------------------------------------------------------------------------
# Make the *tests.e2e* namespace resolvable when the backend test-suite is run
# in isolation.  This avoids ``ModuleNotFoundError`` during pytest collection
# caused by the nested *pytest.ini* file inside ``tests/e2e`` which attempts to
# import the package for configuration discovery.
# ---------------------------------------------------------------------------

# Provide minimal stubs so that absolute imports like ``import tests.e2e`` do
# not fail when the *e2e* directory is skipped.

from types import ModuleType
import sys as _sys


def _ensure(name: str):
    if name not in _sys.modules:
        mod = ModuleType(name)
        mod.__path__ = []  # type: ignore[attr-defined]
        _sys.modules[name] = mod


_ensure("tests.e2e")
_ensure("tests.e2e.fixtures")
_ensure("tests.e2e.tests")
_ensure("tests.e2e.conftest")
