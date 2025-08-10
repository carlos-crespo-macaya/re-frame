# SPDX-License-Identifier: MIT
"""
ADK Integration Wrapper

This module provides the bridge between the new orchestration system
and the existing Google ADK agents.
"""

import asyncio
import json
import logging
import re
from threading import RLock
from typing import Any

from google.generativeai import GenerativeModel

from src.knowledge.cbt_context import BASE_CBT_CONTEXT

from .orchestrator import handle_turn
from .state import SessionState
from .ui_contract import enforce_ui_contract

logger = logging.getLogger(__name__)


class ADKIntegration:
    """Wrapper to integrate new orchestration with existing ADK agents."""

    def __init__(self, model: GenerativeModel | None = None):
        """Initialize with optional Gemini model."""
        self.model = model or GenerativeModel("gemini-1.5-flash-latest")
        self.session_store: dict[str, SessionState] = {}
        self._lock = RLock()

    def get_or_create_session(self, session_id: str) -> SessionState:
        """Get existing session or create new one."""
        with self._lock:
            if session_id not in self.session_store:
                self.session_store[session_id] = SessionState()
            return self.session_store[session_id]

    def adk_llm_call(self, *, system: str, kb: str, state: dict, user: str) -> str:
        """
        Adapter function that calls ADK agent and returns formatted response.

        This function bridges the new orchestration system with existing ADK agents.
        It ensures the response contains the required <ui> and <control> sections.

        Args:
            system: System prompt with phase guidance
            kb: Micro-knowledge snippets for current phase
            state: Current session state as dict
            user: User's input text

        Returns:
            String containing <ui>...</ui> and <control>{...}</control> sections
        """
        # Include CBT context and enforce UI contract
        sys_ctx = BASE_CBT_CONTEXT + "\n" + system
        sys_ctx = enforce_ui_contract(sys_ctx, phase="adk")

        # Combine with knowledge base
        full_prompt = sys_ctx
        if kb:
            full_prompt += f"\n\nMICRO-KNOWLEDGE:\n{kb}"

        # Create messages for the model
        # Note: Adapt this to your specific ADK agent setup
        try:
            # Generate response using the model
            response = self.model.generate_content(
                [full_prompt, f"User: {user}"],
                generation_config={
                    "temperature": 0.4,
                    "max_output_tokens": 350,
                },
            )

            # Extract the text response more robustly
            response_text = getattr(response, "text", None)
            if not response_text:
                # Fallbacks for SDK variants
                candidates = getattr(response, "candidates", None)
                if candidates:
                    parts = [
                        getattr(c, "content", None) or getattr(c, "text", "")
                        for c in candidates
                    ]
                    response_text = " ".join([str(p) for p in parts if p]).strip()
            if not response_text:
                response_text = str(response).strip()

            # Ensure response has proper format with stricter validation
            ui_match = re.search(r"<ui>(.*?)</ui>", response_text, flags=re.S | re.I)
            ctrl_match = re.search(
                r"<control>(.*?)</control>", response_text, flags=re.S | re.I
            )
            valid = False
            if ui_match and ctrl_match:
                try:
                    json.loads(ctrl_match.group(1).strip())
                    valid = True
                except Exception:
                    valid = False
            if not valid:
                normalized_phase = str(state.get("phase", "warmup")).lower()
                response_text = (
                    f"<ui>{(ui_match.group(1).strip() if ui_match else response_text).strip()}</ui>\n"
                    f'<control>{{"next_phase":"{normalized_phase}","missing_fields":[],"suggest_questions":[],"crisis_detected":false}}</control>'
                )

            return response_text

        except Exception:
            logger.exception("adk_llm_call failed")
            # Error fallback
            return f"""<ui>I'm here to listen and help you explore your thoughts. Could you tell me what's on your mind?</ui>
<control>{{"next_phase":"{state.get('phase', 'warmup')}","missing_fields":[],"suggest_questions":[],"crisis_detected":false}}</control>"""

    def process_turn(self, session_id: str, user_text: str) -> dict[str, Any]:
        """
        Process one turn of conversation using the new orchestration system.

        Args:
            session_id: Unique session identifier
            user_text: User's input text

        Returns:
            Dict with phase, turn, banner, ui_text, control, state, and end_of_session
        """
        # Get or create session state
        state = self.get_or_create_session(session_id)

        # Process the turn using the new orchestrator
        result = handle_turn(state, user_text, adk_llm_call=self.adk_llm_call)

        # Update stored session state with thread safety
        with self._lock:
            self.session_store[session_id] = SessionState(**result["state"])

        return result


# Example usage function
def example_usage():
    """
    Example of how to use the ADK integration wrapper.

    This shows how to:
    1. Initialize the integration
    2. Process user turns
    3. Handle the response
    """
    # Initialize integration
    integration = ADKIntegration()

    # Example session
    session_id = "user_123"

    # Process first turn
    result = integration.process_turn(
        session_id, "I'm feeling anxious about an upcoming presentation"
    )

    # Use the result
    print(f"Phase: {result['phase']}")
    if result.get("banner"):
        print(f"Banner: {result['banner']}")
    print(f"Assistant: {result['ui_text']}")
    print(f"Turn: {result['turn']}/{result['state']['max_turns']}")

    # Check if session ended
    if result["end_of_session"]:
        print("Session has ended")
        # Clean up session
        del integration.session_store[session_id]

    return result


# Integration with existing routes
def integrate_with_fastapi():
    """
    Example of FastAPI integration.

    This would replace or augment existing chat endpoint logic.
    """
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    app = FastAPI()
    integration = ADKIntegration()

    class ChatRequest(BaseModel):
        session_id: str
        message: str

    class ChatResponse(BaseModel):
        phase: str
        turn: int
        banner: str | None
        message: str
        end_of_session: bool

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        try:
            # Run blocking I/O in thread to avoid blocking event loop
            result = await asyncio.to_thread(
                integration.process_turn, request.session_id, request.message
            )

            return ChatResponse(
                phase=result["phase"],
                turn=result["turn"],
                banner=result.get("banner"),
                message=result["ui_text"],
                end_of_session=result["end_of_session"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

    return app
