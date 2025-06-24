"""Custom runner for the re-frame agent that handles multi-phase conversations."""

from typing import AsyncGenerator
from google.adk.events import Event
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents import SequentialAgent

from .agent import intake_agent, reframe_agent, report_agent
from ag

class ReFrameRunner:
    """Custom runner that switches between intake and reframing phases."""
    
    def __init__(self, app_name: str, session_service):
        self.app_name = app_name
        self.session_service = session_service
        self.intake_runner = Runner(
            agent=intake_agent,
            app_name=app_name,
            session_service=session_service
        )
        # Create a sequential pipeline for reframing
        self.reframe_pipeline = SequentialAgent(
            name="ReframePipeline",
            sub_agents=[reframe_agent, report_agent],
            description="Reframing and report generation pipeline"
        )
        self.reframe_runner = Runner(
            agent=self.reframe_pipeline,
            app_name=app_name,
            session_service=session_service
        )
    
    async def run_async(
        self,
        user_id: str,
        session_id: str,
        new_message: types.Content
    ) -> AsyncGenerator[Event, None]:
        """Run the appropriate agent based on the current state."""
        # Get the current session to check state
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Check if intake is complete
        collection_complete = session.state.get("collection_complete", False)
        
        if not collection_complete:
            # Still in intake phase
            async for event in self.intake_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                yield event
                
            # After intake completes, check if we should move to reframing
            session = await self.session_service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
            if session.state.get("collection_complete", False):
                # Automatically trigger reframing pipeline
                # Create a synthetic message to trigger the pipeline
                trigger_message = types.Content(
                    role="user",
                    parts=[types.Part(text="[System: Intake complete, proceeding to reframing]")]
                )
                async for event in self.reframe_runner.run_async(
                    user_id=user_id,
                    session_id=session_id,
                    new_message=trigger_message
                ):
                    yield event
        else:
            # Already completed intake, run reframing pipeline
            async for event in self.reframe_runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                yield event