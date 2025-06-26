"""ADK runner for multilingual cognitive reframing assistant."""

from google.adk.runner import Runner
from reframe.orchestrators.multilingual_orchestrator import MultilingualReframeOrchestrator

# Initialize orchestrator
orchestrator = MultilingualReframeOrchestrator()

# Create runner
runner = Runner(
    agent=orchestrator.pipeline,
    app_name="multilingual_reframe_assistant",
    session_service=orchestrator.session_service,
)

print("✅ Multilingual ADK Runner configured")
print("🌐 Language detection: Google Cloud Translation API")
print("👥 Three agents: Intake → Analysis (with /exit) → PDF")
print(f"💾 Session management: {type(orchestrator.session_service).__name__}")
print("📊 Observability: Langfuse" + (" + Arize" if orchestrator.settings.arize_api_key else ""))
print("\nRun 'adk web' to start the interface")