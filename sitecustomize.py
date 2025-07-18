"""Site customisation for the test runner.

This module is *automatically imported* by the Python interpreter at start-up
(if it can be found on ``sys.path``).  We take advantage of that behaviour to
inject a few placeholder modules so that absolute imports used by the E2E test
suite (e.g. ``import tests.e2e``) do not raise ``ModuleNotFoundError`` when we
run the **backend** unit-test subset in isolation.

The real E2E tests require Playwright, a running frontend and backend, and are
outside the scope of the lightweight CI job executed here.  By creating dummy
packages we ensure that Python can resolve the import while our
``pytest_ignore_collect`` hook (defined in *backend/tests/conftest.py*) skips
collection of those heavy tests.
"""

from types import ModuleType
import sys


def _create_package(name: str) -> None:
    """Ensure *name* (and its parent packages) exist in ``sys.modules``."""

    if name in sys.modules:  # Already present, nothing to do.
        return

    if '.' in name:
        parent, _ = name.rsplit('.', 1)
        _create_package(parent)

    module = ModuleType(name)
    module.__path__ = []  # Mark as *namespace* package
    sys.modules[name] = module


# Inject the stubs early so **any** subsequent import succeeds.
for pkg in ("tests", "tests.e2e"):
    _create_package(pkg)

