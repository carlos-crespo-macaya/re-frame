"""Simple websocket echo-stream for tokenised assistant responses.

This module provides the `/ws` endpoint referenced in the UX patch.  It uses
the *orchestrator.stream* helper added earlier – that helper is a thin async
generator which yields space-separated *tokens* of a dummy assistant reply so
that the front-end can progressively render output.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.agents import orchestrator


router = APIRouter()


@router.websocket("/ws")
async def ws_chat(ws: WebSocket):  # noqa: D401 – FastAPI websocket route
    await ws.accept()

    tts_task = None  # Placeholder for future text-to-speech cancellation logic
    try:
        while True:
            msg = await ws.receive_text()

            # Special prefix used by the front-end to *barge-in* and cancel any
            # ongoing TTS playback. We do nothing in the stub besides ignoring
            # the message.
            if msg.startswith("__bargein__"):
                if tts_task:
                    tts_task.cancel()  # type: ignore[attr-defined]
                continue

            async for token in orchestrator.stream(msg):
                await ws.send_text(token)
    except WebSocketDisconnect:
        # Client disconnected – silent exit.
        return
