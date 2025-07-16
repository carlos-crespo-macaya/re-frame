"""Stub package for google.* imports used in tests."""

import types
import sys


def _ensure_submodule(path: str) -> types.ModuleType:  # noqa: D401
    """Ensure that the given dotted-path module exists in ``sys.modules``.

    This helper makes it easy to create a nested module hierarchy like
    ``google.adk.agents`` so that ``import`` statements in the test-suite
    succeed without bringing the real Google SDKs into the dependency tree.
    """
    segments = path.split(".")
    built = []
    for i, segment in enumerate(segments, 1):
        module_name = ".".join(segments[:i])
        if module_name not in sys.modules:
            mod = types.ModuleType(module_name)
            # Attach the newly created module to its parent (if any) so that
            # attribute-style access works during normal import resolution.
            if i > 1:
                parent_name = ".".join(segments[: i - 1])
                setattr(sys.modules[parent_name], segment, mod)
            sys.modules[module_name] = mod
        else:
            # Ensure the parent chain has attributes set even if the module
            # already existed from a previous call.
            if i > 1:
                parent_name = ".".join(segments[: i - 1])
                setattr(sys.modules[parent_name], segment, sys.modules[module_name])
        built.append(sys.modules[module_name])
    return built[-1]


# ---------------------------------------------------------------------------
# Stub for ``google.adk.agents`` – provides a **very** lightweight LlmAgent
# class with just the attributes accessed by the test-suite.
# ---------------------------------------------------------------------------

_agents_mod = _ensure_submodule("google.adk.agents")


class LlmAgent:  # noqa: D101 – simple stub
    def __init__(self, *, model: str, name: str, instruction: str, tools: list | None = None):
        self.model = model
        self.name = name
        self.instruction = instruction
        self.tools = tools or []

    # The real class exposes ``__str__`` to get the instruction text; some
    # tests rely on this behaviour when they cast the instruction to ``str``.
    def __str__(self) -> str:  # type: ignore[override]
        return str(self.instruction)


# Expose in the stub module namespace
_agents_mod.LlmAgent = LlmAgent  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Stub for ``google.adk.runners`` – InMemoryRunner with minimal behaviour.
# ---------------------------------------------------------------------------

_runners_mod = _ensure_submodule("google.adk.runners")


class _Session:  # noqa: D101 – internal helper
    def __init__(self):
        self.state: dict = {}


class InMemorySessionService:  # noqa: D101 – stub
    def __init__(self):
        # Nested dict [app_name][user_id][session_id] -> _Session
        self._store: dict[str, dict[str, dict[str, _Session]]] = {}

    async def create_session(self, *, app_name: str, user_id: str, session_id: str):  # noqa: D401
        self._store.setdefault(app_name, {}).setdefault(user_id, {})[session_id] = _Session()

    async def get_session(self, *, app_name: str, user_id: str, session_id: str):  # noqa: D401
        return self._store[app_name][user_id][session_id]


class InMemoryRunner:  # noqa: D101 – very thin wrapper for tests
    def __init__(self, *, agent):
        self.agent = agent
        self.app_name = "test_app"
        self.session_service: InMemorySessionService = InMemorySessionService()

    # The real runner is an async generator; tests patch this method, but it
    # still needs to *exist*.
    async def run_async(self, *args, **kwargs):  # noqa: D401, ANN001
        if False:
            yield  # This makes run_async an async generator.


_runners_mod.InMemoryRunner = InMemoryRunner  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Stub for ``google.genai.types`` – Content and Part containers.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Stub for ``google.genai.types`` used by the tests.
# ---------------------------------------------------------------------------

_genai_mod = _ensure_submodule("google.genai")
_types_mod = _ensure_submodule("google.genai.types")


class Part:  # noqa: D101 – simple holder
    def __init__(self, text: str):
        self.text = text


class Content:  # noqa: D101 – container matching the minimal interface
    def __init__(self, *, parts: list[Part], role: str):
        self.parts = parts
        self.role = role


_types_mod.Part = Part  # type: ignore[attr-defined]
_types_mod.Content = Content  # type: ignore[attr-defined]
