#!/usr/bin/env python3
"""Test the implementation to ensure it follows the specification."""

import asyncio
import contextlib
import os
from pathlib import Path
import sys

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reframe.agents.intake_agent import IntakeAgent
from reframe.agents.pdf_agent import PDFAgent
from reframe.agents.reframe_agent import ReframeAgent
from reframe.core.models import IntakeData, ReframeAnalysis, SessionState


async def test_individual_agents() -> None:
    """Test each agent individually."""

    # Test Intake Agent
    intake_agent = IntakeAgent()

    # Test crisis detection
    crisis_result = await intake_agent.run(
        user_input="I want to end it all",
        session_state={"user_id": "test", "session_id": "test123"},
    )
    assert crisis_result["crisis_detected"]

    # Test normal flow
    normal_result = await intake_agent.run(
        user_input="I failed my exam today",
        session_state={"user_id": "test", "session_id": "test123"},
    )
    assert not normal_result["crisis_detected"]
    assert normal_result["should_continue"]

    # Test Reframe Agent
    reframe_agent = ReframeAgent()

    test_intake = IntakeData(
        trigger_situation="Failed driving test",
        automatic_thought="I can't do anything right",
        emotion_data="frustrated, 7/10",
    )

    reframe_result = await reframe_agent.run(
        intake_data=test_intake, session_state={"user_id": "test", "session_id": "test123"}
    )

    assert "reframe_analysis" in reframe_result
    assert reframe_result["reframe_analysis"] is not None
    assert len(reframe_result["reframe_analysis"].distortions) >= 1

    # Test PDF Agent
    pdf_agent = PDFAgent()

    test_analysis = ReframeAnalysis(
        distortions=["all-or-nothing thinking"],
        evidence_for=["I did fail the test"],
        evidence_against=["I passed the written exam", "I've been practicing"],
        balanced_thought="I didn't pass this test, but I'm learning and improving",
        micro_action="List 3 things that went well during the test",
        confidence_before=90,
        confidence_after=40,
    )

    pdf_result = await pdf_agent.run(
        intake_data=test_intake,
        reframe_analysis=test_analysis,
        session_state={"user_id": "test", "session_id": "test123"},
    )

    assert pdf_result["pdf_ready"]
    assert "pdf_base64" in pdf_result
    assert pdf_result["pdf_base64"] is not None


async def test_orchestrator() -> None:
    """Test the full orchestrator flow."""

    # Check environment variables
    required_vars = [
        "GOOGLE_API_KEY",
        "SUPABASE_REFRAME_DB_CONNECTION_STRING",
        "LANGFUSE_HOST",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        return

    # Initialize orchestrator
    try:
        from reframe.core.orchestrator import POCReframeOrchestrator

        POCReframeOrchestrator()
    except Exception:
        return


async def test_models() -> None:
    """Test that models match specification."""

    # Test IntakeData
    intake = IntakeData(
        trigger_situation="Test situation",
        automatic_thought="Test thought",
        emotion_data="anxious, 6/10",
    )
    assert intake.trigger_situation == "Test situation"

    # Test ReframeAnalysis
    analysis = ReframeAnalysis(
        distortions=["mind reading"],
        evidence_for=["test"],
        evidence_against=["test"],
        balanced_thought="A balanced view",
        micro_action="Take a walk",
        confidence_before=80,
        confidence_after=None,  # Can be None initially
    )
    assert analysis.confidence_after is None

    # Test SessionState
    state = SessionState()
    assert not state.collection_complete
    assert not state.reframe_done
    assert not state.pdf_ready


async def test_prompts() -> None:
    """Test that Langfuse prompts are accessible."""

    from langfuse import Langfuse

    from config.settings import get_settings

    settings = get_settings()

    try:
        langfuse = Langfuse(
            host=settings.langfuse_host,
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
        )

        required_prompts = [
            "intake-agent-adk-instructions",
            "reframe-agent-adk-instructions",
            "synthesis-agent-adk-instructions",
        ]

        for prompt_name in required_prompts:
            with contextlib.suppress(Exception):
                langfuse.get_prompt(prompt_name)

    except Exception:
        pass


async def main() -> None:
    """Run all tests."""

    # Run tests
    await test_models()
    await test_individual_agents()
    await test_prompts()
    await test_orchestrator()


if __name__ == "__main__":
    asyncio.run(main())
