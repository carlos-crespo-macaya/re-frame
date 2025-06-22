"""ADK Session Manager for coordinating multi-agent workflows."""

import logging
import uuid
from datetime import datetime
from typing import Any

from .adk_base import ReFrameTransparencyData
from .adk_cbt_agent import ADKCBTFrameworkAgent
from .adk_intake_agent import ADKIntakeAgent
from .adk_synthesis_agent import ADKSynthesisAgent

logger = logging.getLogger(__name__)


class SessionData:
    """Data structure for managing session state."""

    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.user_inputs: list[str] = []
        self.agent_responses: list[dict[str, Any]] = []
        self.workflow_state = "initial"
        self.crisis_flags: list[dict[str, Any]] = []
        self.transparency_log: list[ReFrameTransparencyData] = []


class ADKSessionManager:
    """Manager for coordinating ADK-based multi-agent sessions."""

    def __init__(self):
        """Initialize the session manager with ADK agents."""
        self.intake_agent = ADKIntakeAgent()
        self.cbt_agent = ADKCBTFrameworkAgent()
        self.synthesis_agent = ADKSynthesisAgent()

        # Session storage (in production, this would be persistent)
        self.sessions: dict[str, SessionData] = {}

        logger.info("Initialized ADK Session Manager with multi-agent workflow")

    def create_session(self) -> str:
        """Create a new session and return session ID."""
        session = SessionData()
        self.sessions[session.session_id] = session

        logger.info(f"Created new session: {session.session_id}")
        return session.session_id

    def get_session(self, session_id: str) -> SessionData | None:
        """Get session data by ID."""
        return self.sessions.get(session_id)

    async def process_user_input(self, user_input: str, session_id: str = None) -> dict[str, Any]:
        """Process user input through the complete multi-agent workflow.

        Args:
            user_input: User's thought or message
            session_id: Optional session ID, creates new session if not provided

        Returns:
            Complete response with all agent outputs and transparency data
        """
        # Get or create session
        if session_id is None:
            session_id = self.create_session()

        session = self.get_session(session_id)
        if session is None:
            session_id = self.create_session()
            session = self.get_session(session_id)

        # Update session activity
        session.last_activity = datetime.utcnow()
        session.user_inputs.append(user_input)

        try:
            # Step 1: Intake processing
            logger.info(f"Session {session_id}: Starting intake processing")
            intake_result = await self.intake_agent.process_user_input(user_input)

            if not intake_result.success:
                # Return early if intake validation fails
                return self._format_final_response(
                    session_id=session_id,
                    success=False,
                    error=intake_result.error,
                    error_type=intake_result.error_type,
                    workflow_stage="intake_validation",
                    transparency_data=(
                        [intake_result.transparency_data] if intake_result.transparency_data else []
                    ),
                )

            # Check for crisis flags
            intake_data = self._parse_intake_response(intake_result.response)
            if intake_data and intake_data.get("requires_crisis_support"):
                session.crisis_flags.append(
                    {
                        "timestamp": datetime.utcnow().isoformat(),
                        "input": user_input,
                        "type": "crisis_support_required",
                    }
                )

                # Use specialized crisis response
                crisis_result = await self.synthesis_agent.create_crisis_response(intake_data)

                return self._format_final_response(
                    session_id=session_id,
                    success=True,
                    response=crisis_result.response,
                    workflow_stage="crisis_response",
                    transparency_data=[
                        intake_result.transparency_data,
                        crisis_result.transparency_data,
                    ],
                    crisis_flag=True,
                )

            # Step 2: CBT processing
            logger.info(f"Session {session_id}: Starting CBT processing")
            cbt_result = await self.cbt_agent.apply_cbt_techniques(intake_data)

            if not cbt_result.success:
                # Handle CBT processing error
                return self._format_final_response(
                    session_id=session_id,
                    success=False,
                    error=cbt_result.error,
                    error_type=cbt_result.error_type,
                    workflow_stage="cbt_processing",
                    transparency_data=[
                        intake_result.transparency_data,
                        cbt_result.transparency_data,
                    ],
                )

            # Step 3: Synthesis
            logger.info(f"Session {session_id}: Starting synthesis")
            cbt_data = self._parse_cbt_response(cbt_result.response)
            synthesis_result = await self.synthesis_agent.create_user_response(cbt_data)

            if not synthesis_result.success:
                # Handle synthesis error
                return self._format_final_response(
                    session_id=session_id,
                    success=False,
                    error=synthesis_result.error,
                    error_type=synthesis_result.error_type,
                    workflow_stage="synthesis",
                    transparency_data=[
                        intake_result.transparency_data,
                        cbt_result.transparency_data,
                        synthesis_result.transparency_data,
                    ],
                )

            # Success - compile complete response
            session.workflow_state = "completed"
            session.agent_responses.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_input": user_input,
                    "intake_result": intake_result.dict(),
                    "cbt_result": cbt_result.dict(),
                    "synthesis_result": synthesis_result.dict(),
                }
            )

            return self._format_final_response(
                session_id=session_id,
                success=True,
                response=synthesis_result.response,
                workflow_stage="completed",
                transparency_data=[
                    intake_result.transparency_data,
                    cbt_result.transparency_data,
                    synthesis_result.transparency_data,
                ],
                intake_data=intake_data,
                cbt_data=cbt_data,
            )

        except Exception as e:
            logger.error(f"Session {session_id}: Workflow error: {e!s}")
            session.workflow_state = "error"

            return self._format_final_response(
                session_id=session_id,
                success=False,
                error=f"Workflow processing error: {e!s}",
                error_type="workflow_error",
                workflow_stage="unknown",
            )

    def _parse_intake_response(self, response: str) -> dict[str, Any] | None:
        """Parse intake agent response."""
        try:
            return self.intake_agent.parse_json_response(response)
        except Exception as e:
            logger.warning(f"Failed to parse intake response: {e}")
            return None

    def _parse_cbt_response(self, response: str) -> dict[str, Any] | None:
        """Parse CBT agent response."""
        try:
            return self.cbt_agent.parse_json_response(response)
        except Exception as e:
            logger.warning(f"Failed to parse CBT response: {e}")
            return None

    def _format_final_response(
        self,
        session_id: str,
        success: bool,
        response: str = None,
        error: str = None,
        error_type: str = None,
        workflow_stage: str = None,
        transparency_data: list[ReFrameTransparencyData] = None,
        crisis_flag: bool = False,
        intake_data: dict[str, Any] = None,
        cbt_data: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Format the final response with all workflow information."""
        return {
            "session_id": session_id,
            "success": success,
            "response": response,
            "error": error,
            "error_type": error_type,
            "workflow_stage": workflow_stage,
            "crisis_flag": crisis_flag,
            "timestamp": datetime.utcnow().isoformat(),
            "transparency": {
                "agents_used": [data.agent_name for data in (transparency_data or [])],
                "techniques_applied": [
                    technique
                    for data in (transparency_data or [])
                    for technique in data.techniques_used
                ],
                "workflow_steps": [
                    data.reasoning_path.get("agent_type", "unknown")
                    for data in (transparency_data or [])
                ],
                "detailed_transparency": (
                    [data.dict() for data in (transparency_data or [])] if transparency_data else []
                ),
            },
            "agent_outputs": (
                {
                    "intake": intake_data,
                    "cbt": cbt_data,
                }
                if intake_data or cbt_data
                else None
            ),
        }

    def get_session_history(self, session_id: str) -> dict[str, Any] | None:
        """Get complete session history."""
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "workflow_state": session.workflow_state,
            "user_inputs": session.user_inputs,
            "response_count": len(session.agent_responses),
            "crisis_flags": session.crisis_flags,
            "has_crisis_history": len(session.crisis_flags) > 0,
        }

    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than max_age_hours."""
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if session.last_activity < cutoff_time
        ]

        for session_id in expired_sessions:
            del self.sessions[session_id]

        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)
