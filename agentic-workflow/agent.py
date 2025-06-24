import asyncio
import os
import uuid

from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from langfuse import Langfuse

from .config.settings import get_settings
from .models import ConversationState

settings = get_settings()
langfuse = Langfuse(
    host=settings.langfuse_host,
    public_key=settings.langfuse_public_key,
    secret_key=settings.langfuse_secret_key,
)

# Configure OpenTelemetry endpoint & headers
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = settings.langfuse_host + "/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {settings.langfuse_bearer_token}"

USER_ID = f"Anonymous_{uuid.uuid4()}"
session_id = uuid.uuid4()

prompt = langfuse.get_prompt("intake-agent-adk-instructions")

root_agent = SequentialAgent(
    name="ReframeSequentialPipeline",
    description=prompt.prompt,
    max_iterations=10,
)

# --- Setup Runner and Session ---
session_service = DatabaseSessionService(db_url=settings.supabase_connection_string)

initial_state = ConversationState(
    intake_data=None,
    reframe_analysis=None,
    pdf_report=None
)

stateful_session = session_service.create_session(
    app_name=settings.app_name,
    user_id=USER_ID,
    session_id=str(session_id),
    state=initial_state.model_dump(),
)

runner = Runner(
    agent=root_agent,
    app_name=settings.app_name,
    session_service=session_service
)

state = ConversationState(
    intake_data=None,
    reframe_analysis=None,
    pdf_report=None
)



async def main():
    async for event in runner.run_async(user_id=session.user_id,
                                        session_id=session.id):
        print(event)

if __name__ == "__main__":
    asyncio.run(main())
