"""Intake state management tool for the re-frame agent."""

from typing import Optional
from google.adk.tools import ToolContext


def update_intake_state(
    tool_context: ToolContext,
    trigger_situation: Optional[str] = None,
    automatic_thought: Optional[str] = None,
    emotion_data: Optional[str] = None,
    collection_complete: bool = False,
    crisis_detected: bool = False,
) -> dict:
    """Update the intake conversation state.
    
    This tool is used by the intake agent to track collected information.
    
    Args:
        tool_context: ADK tool context for state management
        trigger_situation: The situation/context when the thought occurred
        automatic_thought: The exact negative thought
        emotion_data: The emotion and intensity (e.g., "shame, 8/10")
        collection_complete: True when all 3 pieces are collected
        crisis_detected: True if user expresses suicidal ideation
        
    Returns:
        Dictionary with current state
    """
    # Update the tool context state
    if trigger_situation is not None:
        tool_context.state["trigger_situation"] = trigger_situation
    if automatic_thought is not None:
        tool_context.state["automatic_thought"] = automatic_thought
    if emotion_data is not None:
        tool_context.state["emotion_data"] = emotion_data
    if collection_complete:
        tool_context.state["collection_complete"] = collection_complete
    if crisis_detected:
        tool_context.state["crisis_detected"] = crisis_detected
    
    # Don't escalate here - let the agent handle the conversation flow
    # The runner will check the state to determine next steps
    
    return {
        "status": "updated",
        "trigger_situation": tool_context.state.get("trigger_situation"),
        "automatic_thought": tool_context.state.get("automatic_thought"),
        "emotion_data": tool_context.state.get("emotion_data"),
        "collection_complete": tool_context.state.get("collection_complete", False),
        "crisis_detected": tool_context.state.get("crisis_detected", False),
    }

def ask_for