"""E2E tests package marker.

While running the E2E test-suite we want simple imports such as

    from pages.home_page import HomePage

to work, even though the *pages* package actually lives inside this
``tests/e2e`` directory.  When *pytest* sets ``rootdir`` to *tests/e2e* the
directory itself is already on ``sys.path``; however, because the package is
named *tests.e2e.pages*, the top-level alias *pages* is not automatically
available.

We create a lightweight alias so that either spelling can be imported.
"""

from importlib import import_module
import sys as _sys


# Expose shorter import aliases (``pages.*`` and ``utils.*``) so that
# test files can use concise absolute imports regardless of where the e2e
# package sits in ``sys.path``.

for _alias in ("pages", "utils"):
    if _alias not in _sys.modules:  # pragma: no cover – executed only during e2e
        _sys.modules[_alias] = import_module(f"{__name__}.{_alias}")
