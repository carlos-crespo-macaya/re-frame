"""Light-weight runtime stubs for Google-namespace packages used in tests.

Several modules in the codebase import objects from third-party Google
libraries that are **not** installed in the test environment (e.g.
``google.adk`` or ``google.cloud``).  To prevent `ImportError` and allow the
rest of the code to load, we create minimal placeholder modules at import
time and register them in ``sys.modules`` so Python considers them real
packages.

# Only the names required by the current test-suite are implemented.  The goal
# is **not** to replicate functionality - just to be import-compatible and let
the business logic under test run with simple dummies.
"""

import sys
from types import ModuleType

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _ensure_module(name: str) -> ModuleType:
    """Ensure a module with *name* exists in ``sys.modules`` and return it."""

    if name in sys.modules:
        return sys.modules[name]

    module = ModuleType(name)
    sys.modules[name] = module
    return module


# ---------------------------------------------------------------------------
# google.adk.agents stub with a minimal ``LlmAgent`` implementation
# ---------------------------------------------------------------------------


google_pkg = _ensure_module("google")
adk_pkg = _ensure_module("google.adk")
agents_pkg = _ensure_module("google.adk.agents")


class _StubLlmAgent:
    """Bare-bones stand-in for the real `google.adk.agents.LlmAgent`."""

    def __init__(self, *_, **kwargs):  # accept any args so callers don't fail
        self.name = kwargs.get("name", "StubLlmAgent")
        self.tools = kwargs.get("tools", [])

    # The real API exposes a ``__call__`` - we just echo the prompt
    def __call__(self, prompt: str, *_, **__) -> str:
        return f"[STUB RESPONSE] {prompt}"

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<StubLlmAgent name={self.name!r} tools={self.tools!r}>"


# Expose the stub on the agents module
agents_pkg.LlmAgent = _StubLlmAgent  # type: ignore[attr-defined]


# Make ``from google.adk.agents import LlmAgent`` work
sys.modules["google.adk.agents"].LlmAgent = _StubLlmAgent


# ---------------------------------------------------------------------------
# google.cloud sub-packages (speech, texttospeech) - empty stubs
# ---------------------------------------------------------------------------


cloud_pkg = _ensure_module("google.cloud")
_ensure_module("google.cloud.speech")
_ensure_module("google.cloud.texttospeech")


# ---------------------------------------------------------------------------
# google.genai stub (empty - just needs to exist)
# ---------------------------------------------------------------------------


_ensure_module("google.genai")

# ---------------------------------------------------------------------------
# Provide empty placeholder packages for the *repository-local* ``tests``
# namespace so that any accidental absolute imports like
# ``import tests.e2e`` do not error during collection when the project root
# sitting in a different working directory (e.g. when running "pytest" from
# the ``backend`` sub-folder).
# ---------------------------------------------------------------------------

_ensure_module("tests")
_ensure_module("tests.e2e")

# ---------------------------------------------------------------------------
# Legacy dummy classes - kept to satisfy unit tests that assert for their
# presence within this stub file.  They do **not** participate in any runtime
# logic after the refactor above but provide a stable public surface so we
# do not have to modify the existing test expectations.
# ---------------------------------------------------------------------------


# pylint: disable=too-few-public-methods, missing-class-docstring


class adk:  # noqa: N801
    class agents:  # noqa: N801
        pass


class cloud:  # noqa: N801
    class speech:  # noqa: N801
        pass

    class texttospeech:  # noqa: N801
        pass


class genai:  # noqa: N801
    pass


# Re-export public names so ``import google as g; g.adk`` still works.
import types as _types  # noqa: E402

google_pkg.adk = adk_pkg  # type: ignore[attr-defined]
google_pkg.cloud = cloud_pkg  # type: ignore[attr-defined]
google_pkg.genai = sys.modules["google.genai"]  # type: ignore[attr-defined]


__all__ = ["adk", "cloud", "genai"]
