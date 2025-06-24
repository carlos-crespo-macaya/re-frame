#!/usr/bin/env python3
"""Test script to verify the complete re-frame flow."""

import asyncio
import json
from pathlib import Path
import sys

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from google.adk.runner import InvokeContext, Runner
from reframe_agent import root_agent


async def test_complete_flow():
    """Test the complete flow from intake to report."""
    print("Testing complete re-frame flow...")
    print("=" * 50)
    
    # Initialize the runner
    runner = Runner(root_agent)
    
    # Create a test context with some initial state
    context = InvokeContext(
        session_state={
            "collection_complete": False,
            "crisis_detected": False,
        }
    )
    
    # Test conversation flow
    test_messages = [
        "Hi, I'd like to work on a negative thought I've been having",
        "I have a presentation tomorrow at work",
        "I keep thinking 'I'm going to mess up and everyone will think I'm incompetent'",
        "I feel anxious, maybe an 8 out of 10",
        "Last time I stumbled on a few answers",
        "Well, I have practiced a lot this time and my slides look good",
        "About 85%"
    ]
    
    print("\nStarting conversation flow:")
    print("-" * 50)
    
    for i, message in enumerate(test_messages):
        print(f"\n[User {i+1}]: {message}")
        
        try:
            # Send message to the agent
            response = await runner.run(message, context)
            
            # Print the response
            print(f"[Agent]: {response.model_response}")
            
            # Print session state for debugging
            if hasattr(response, 'session_state'):
                print(f"\n[Debug] Session state: {json.dumps(response.session_state, indent=2)}")
            
            # Check if we've completed the flow
            if "PDF report created successfully" in str(response.model_response):
                print("\n✅ Flow completed successfully!")
                break
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            break
    
    print("\n" + "=" * 50)
    print("Test complete.")


if __name__ == "__main__":
    asyncio.run(test_complete_flow())