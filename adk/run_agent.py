#!/usr/bin/env python3
"""Run the re-frame agent interactively."""

import asyncio
import os
import sys

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from reframe_agent import root_agent


async def main():
    """Run the agent interactively."""
    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        print("Please set it with your Google AI Studio API key.")
        sys.exit(1)
    
    # Create runner with session service
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="reframe_social",
        agent=root_agent,
        session_service=session_service
    )
    
    # Create session
    session = await session_service.create_session(
        app_name="reframe_social",
        user_id="anonymous_user"
    )
    
    # Interactive loop
    print("Welcome to re-frame.social Cognitive Reframing Assistant")
    print("Type 'quit' to exit\n")
    
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() == "quit":
                break
            
            # Run the pipeline
            message = types.Content(role="user", parts=[types.Part(text=user_input)])
            events = runner.run(
                user_id=session.user_id,
                session_id=session.id,
                new_message=message
            )
            
            # Display response
            for event in events:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(f"Assistant: {part.text}")
    
    except KeyboardInterrupt:
        print("\nGoodbye!")


if __name__ == "__main__":
    asyncio.run(main())