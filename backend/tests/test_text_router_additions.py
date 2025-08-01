import asyncio
import contextlib
from collections.abc import AsyncIterator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.requests import Request
from starlette.responses import StreamingResponse

# Import the router module directly to test internal functions and mount HTTP routes
from src.text import router as text_router


class DummySession:
    def __init__(self, session_id: str, user_id: str = "user"):
        self.session_id = session_id
        self.user_id = user_id
        now = asyncio.get_event_loop().time()
        self.created_at = now
        self.last_activity = now

        # Minimal fields used by get_session_info and list_sessions
        self.request_queue = None
        self.metadata: dict[str, Any] = {}
        # Expose properties used in list_sessions
        self.age_seconds = 0
        self.inactive_seconds = 0


@pytest.fixture
def fastapi_app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    """
    Build a minimal FastAPI app mounting the text router to exercise HTTP endpoints.
    """
    app = FastAPI()
    app.include_router(text_router.router)
    return app


@pytest.fixture
async def async_client(fastapi_app: FastAPI) -> AsyncIterator[AsyncClient]:
    # httpx 0.28+ removed 'app' kwarg; use ASGITransport explicitly
    import httpx

    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_session_manager(monkeypatch: pytest.MonkeyPatch):
    """
    Provide a fake session_manager with minimal behavior needed for tests.
    """
    sessions: dict[str, DummySession] = {}

    class FakeSessionManager:
        def __init__(self):
            self._sessions = sessions

        def create_session(self, session_id: str, user_id: str, request_queue=None):
            s = DummySession(session_id=session_id, user_id=user_id)
            s.request_queue = request_queue
            self._sessions[session_id] = s
            return s

        def get_session(self, session_id: str):
            return self._sessions.get(session_id)

        def get_session_readonly(self, session_id: str):
            return self._sessions.get(session_id)

        def list_sessions(self):
            return list(self._sessions.values())

    fake = FakeSessionManager()
    monkeypatch.setattr(text_router, "session_manager", fake)
    return fake


@pytest.fixture
def mock_performance_monitor(monkeypatch: pytest.MonkeyPatch):
    """
    Stub performance monitor to avoid real timing and provide observability.
    """

    class FakePerf:
        def __init__(self):
            self.started: list[str] = []
            self.tracked: list[str] = []

        async def start_session(self, session_id: str):
            self.started.append(session_id)

        @contextlib.asynccontextmanager
        async def track_request(self, kind: str):
            self.tracked.append(kind)
            yield

    perf = FakePerf()
    monkeypatch.setattr(text_router, "get_performance_monitor", lambda: perf)
    return perf


@pytest.mark.asyncio
async def test_sse_heartbeat_when_idle(
    async_client: AsyncClient,
    mock_session_manager,
    mock_performance_monitor,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Verify that SSE emits heartbeats when there are no queued events.
    We set HEARTBEAT_INTERVAL_SECONDS=1 to make the test fast.
    """
    monkeypatch.setenv("HEARTBEAT_INTERVAL_SECONDS", "1")

    # Prepare request and invoke endpoint to obtain StreamingResponse
    # Build a minimal Starlette Request that looks like a GET and supports is_disconnected
    async def _noop_receive():
        return {"type": "http.request"}

    class ReqAdapter(Request):
        def __init__(self):
            scope = {
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "path": "/api/events/sess-hb",
                "query_string": b"",
                "headers": [],
                "client": None,
                "scheme": "http",
                "server": ("testserver", 80),
            }
            super().__init__(scope, receive=_noop_receive)

        async def is_disconnected(self) -> bool:
            # Allow a couple of loop iterations before signalling disconnect
            await asyncio.sleep(2.2)
            return True

    resp = await text_router.sse_endpoint(ReqAdapter(), "sess-hb", language="en-US")
    assert isinstance(resp, StreamingResponse)

    # Consume a few chunks and assert at least one heartbeat arrives
    body_iter = resp.body_iterator
    got_heartbeat = False
    chunks = 0
    async for chunk in body_iter:
        chunks += 1
        # Normalize to string for assertions
        if isinstance(chunk, (bytes | bytearray | memoryview)):  # ruff UP038
            s = bytes(chunk).decode("utf-8", errors="ignore")
        else:
            s = str(chunk)
        if '"type": "heartbeat"' in s:
            got_heartbeat = True
            break
        if chunks > 20:
            break

    assert got_heartbeat, "Expected at least one heartbeat event to be sent"


@pytest.mark.asyncio
async def test_sse_shutdown_flag_ends_stream(
    async_client: AsyncClient,
    mock_session_manager,
    mock_performance_monitor,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    When session.metadata['sse_shutdown']=True, the streaming loop should exit promptly.
    """

    # Build a request that never disconnects on its own
    async def _noop_receive2():
        return {"type": "http.request"}

    class ReqAdapter(Request):
        def __init__(self):
            scope = {
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "path": "/api/events/sess-shutdown",
                "query_string": b"",
                "headers": [],
                "client": None,
                "scheme": "http",
                "server": ("testserver", 80),
            }
            super().__init__(scope, receive=_noop_receive2)

        async def is_disconnected(self) -> bool:
            await asyncio.sleep(0.1)
            return False

    # Kick off stream
    resp = await text_router.sse_endpoint(
        ReqAdapter(), "sess-shutdown", language="en-US"
    )
    assert isinstance(resp, StreamingResponse)

    # Flip shutdown flag after a short delay
    session = text_router.session_manager.get_session("sess-shutdown")
    assert session is not None
    session.metadata["sse_shutdown"] = True

    # Attempt to iterate; the stream should end quickly (iterator exhausts)
    async def consume_some():
        async for _ in resp.body_iterator:
            # Should end after shutdown; if it yields many times, it's a problem
            break

    try:
        await asyncio.wait_for(consume_some(), timeout=3.0)
    except TimeoutError:
        pytest.fail("SSE stream did not terminate after setting shutdown flag")


@pytest.mark.asyncio
async def test_send_message_initialization_guard_returns_500(
    async_client: AsyncClient, mock_session_manager, mock_performance_monitor
):
    """
    If a session exists but is missing mandatory metadata (runner/adk_session/run_config/message_queue),
    the endpoint should return 500 with 'Session not properly initialized'.
    """
    # Create a session without required metadata
    mock_session_manager.create_session(
        "sess-bad", user_id="sess-bad", request_queue=None
    )
    # Intentionally do not set runner/adk_session/run_config/message_queue

    r = await async_client.post(
        "/api/send/sess-bad",
        json={"data": "Hello", "mime_type": "text/plain"},
    )
    assert r.status_code == 500
    assert "Session not properly initialized" in r.text


@pytest.mark.asyncio
async def test_send_message_whitespace_only_is_ignored(
    async_client: AsyncClient, mock_session_manager, mock_performance_monitor
):
    """
    Whitespace-only message should be treated as empty and return 200 without queuing content.
    """
    # Properly initialized session metadata (minimal)
    s = mock_session_manager.create_session(
        "sess-ws", user_id="sess-ws", request_queue=None
    )
    s.metadata["runner"] = object()
    s.metadata["adk_session"] = object()
    s.metadata["run_config"] = object()
    s.metadata["message_queue"] = asyncio.Queue()

    r = await async_client.post(
        "/api/send/sess-ws",
        json={"data": "   \n\t  ", "mime_type": "text/plain"},
    )
    assert r.status_code == 200
    # Queue should remain empty (no content or turn_complete added on early-return)
    assert s.metadata["message_queue"].empty()


@pytest.mark.asyncio
async def test_pdf_headers_and_status(async_client: AsyncClient, mock_session_manager):
    """
    Validate Content-Disposition filename and media type for the PDF placeholder endpoint.
    """
    mock_session_manager.create_session(
        "sess-pdf", user_id="sess-pdf", request_queue=None
    )

    r = await async_client.get("/api/pdf/sess-pdf")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "text/plain; charset=utf-8"
    cd = r.headers.get("content-disposition", "")
    assert "attachment;" in cd and "session_sess-pdf_summary.txt" in cd
