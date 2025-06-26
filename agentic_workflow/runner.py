"""ADK runner for conversational cognitive reframing."""

from google.adk.runner import Runner
from reframe.orchestrators.conversational_orchestrator import ConversationalOrchestrator

# Initialize orchestrator
orchestrator = ConversationalOrchestrator()

# Create runner
runner = Runner(
    agent=orchestrator.pipeline,
    app_name="cognitive_reframing_conversational",
    session_service=orchestrator.session_service,
)

print("=" * 60)
print("💬 Conversational Cognitive Reframing System")
print("=" * 60)
print("Phase 1: Intake - Warm conversation to understand your situation")
print("Phase 2: Analysis - Collaborative CBT exploration")
print("Phase 3: Summary - Encouraging recap and next steps")
print("=" * 60)
print("✅ Ready. Run 'adk web' to start.")