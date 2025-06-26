"""ADK runner configuration for the cognitive reframing assistant."""

import os
from google.adk.runner import Runner
from google.adk.sessions import InMemorySessionService
from reframe.agents.maya_conversational_agent import MayaConversationalMultilingualAgent


# Initialize the conversational multilingual agent with proper flow control
agent = MayaConversationalMultilingualAgent()

# Create session service for state management
session_service = InMemorySessionService()

# Create the runner with proper configuration
runner = Runner(
    agent=agent,
    app_name="maya_reframe_assistant",
    session_service=session_service,
    # Enable state tracking for debug UI
    debug=True
)

print("✅ ADK Runner configured with Maya Conversational Multilingual - Cognitive Reframing Assistant")
print("🌐 Language detection through instruction-based analysis")
print("📋 Conversation phases: Greeting → Discovery → Reframing → Summary")
print("🔍 State tracking enabled for debug UI")
print("📊 Session management: InMemorySessionService")