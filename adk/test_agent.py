#!/usr/bin/env python3
"""Test script for the reframe agent."""

import asyncio
import sys
from pathlib import Path

# Add the agent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from reframe_agent.agent import root_agent


async def main():
    """Run the agent interactively."""
    # Create services
    session_service = InMemorySessionService()
    
    # Create runner
    runner = Runner(
        app_name="reframe_test",
        agent=root_agent,
        session_service=session_service
    )
    
    # Create a session
    session = await session_service.create_session(
        app_name="reframe_test",
        user_id="test_user"
    )
    
    print("AURA: Hello, I'm here to listen. How are you feeling today?")
    print("(Type 'quit' to exit)\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
            
        # Create user message
        user_message = types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
        
        # Run agent
        print("\nAURA: ", end="", flush=True)
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=user_message
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())