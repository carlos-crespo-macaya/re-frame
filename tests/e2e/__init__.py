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


if "pages" not in _sys.modules:  # pragma: no cover – executed only for e2e run
    _sys.modules["pages"] = import_module(__name__ + ".pages")
