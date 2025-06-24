"""Test script to verify the conversation flow works correctly."""

import asyncio
from google.genai import types
from google.adk.agents import InMemorySessionService, Runner

from reframe_agent.agent import root_agent


async def test_conversation():
    """Test the conversation flow with the intake agent."""
    # Set up session service
    session_service = InMemorySessionService()
    app_name = "reframe_test"
    user_id = "test_user"
    session_id = "test_session"
    
    # Create session
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service
    )
    
    # Test conversation turns
    print("=== Testing Conversation Flow ===\n")
    
    # Turn 1: Initial greeting
    print("User: hello")
    content = types.Content(role='user', parts=[types.Part(text='hello')])
    
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
                print(f"IntakeAgent: {response_text}\n")
            break
    
    # Check session state
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(f"State after turn 1: {session.state}\n")
    
    # Turn 2: Share a thought
    print("User: I messed up at work and feel terrible")
    content = types.Content(
        role='user', 
        parts=[types.Part(text='I messed up at work and feel terrible')]
    )
    
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
                print(f"IntakeAgent: {response_text}\n")
            break
    
    # Check session state
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(f"State after turn 2: {session.state}\n")
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(test_conversation())