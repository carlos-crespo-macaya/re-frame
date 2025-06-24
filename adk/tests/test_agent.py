"""Tests for the re-frame agent."""

import pytest
from reframe_agent import root_agent
from reframe_agent.models import IntakeAgentOutput, ReframeAnalysis


def test_agent_imports():
    """Test that all imports work correctly."""
    assert root_agent is not None
    assert root_agent.name == "ReFramePipeline"


def test_intake_model():
    """Test IntakeAgentOutput model."""
    output = IntakeAgentOutput(
        collection_complete=True,
        escalate=False,
        crisis_detected=False,
        data={
            "trigger_situation": "Test situation",
            "automatic_thought": "Test thought",
            "emotion_data": "Anxious 7/10"
        }
    )
    assert output.collection_complete is True
    assert output.data.trigger_situation == "Test situation"


def test_reframe_model():
    """Test ReframeAnalysis model."""
    analysis = ReframeAnalysis(
        distortions=["Catastrophizing", "Mind Reading"],
        evidence_for=["Someone frowned"],
        evidence_against=["They might have been thinking about something else"],
        balanced_thought="They might be having a bad day, it's not necessarily about me",
        micro_action="Focus on my own tasks for the next hour",
        certainty_before=85,
        certainty_after=40
    )
    assert len(analysis.distortions) == 2
    assert analysis.certainty_before > analysis.certainty_after