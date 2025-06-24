"""Callbacks for sharing data between agents in the re-frame pipeline."""

from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types


def inject_intake_data_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Injects intake data into the reframe agent's prompt."""
    
    # Only inject for ReframeAgent
    if callback_context.agent_name != "ReframeAgent":
        return None
    
    # Get intake data from state
    trigger = callback_context.state.get("trigger_situation")
    thought = callback_context.state.get("automatic_thought") 
    emotion = callback_context.state.get("emotion_data")
    
    # If we don't have complete data, let the agent handle it
    if not all([trigger, thought, emotion]):
        return None
    
    # Inject the data into the prompt
    data_prompt = f"""
The intake agent has collected the following information from the user:

Trigger Situation: {trigger}
Automatic Thought: {thought}
Emotion Data: {emotion}

Now analyze this data and call the process_reframe_data tool with your CBT analysis.
Remember: Do NOT output any text or JSON to the user - ONLY call the tool.
"""
    
    # Modify the request to include this data
    if llm_request.contents:
        # Create a new content with our data
        new_content = types.Content(
            role="user",
            parts=[types.Part(text=data_prompt)]
        )
        # Add it to the contents
        llm_request.contents.append(new_content)
    
    return None  # Continue processing


def ensure_report_data_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest  
) -> Optional[LlmResponse]:
    """Ensures the report agent has the necessary data."""
    
    # Only for ReportAgent
    if callback_context.agent_name != "ReportAgent":
        return None
        
    # Check if we have the reframe analysis
    if not callback_context.state.get("result_json"):
        # Create an error response
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="Unable to generate report: Reframing analysis not found in session data.")]
            )
        )
    
    return None  # Continue processing