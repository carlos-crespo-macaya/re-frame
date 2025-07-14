"""
Main entry point for the CBT Reframing Assistant.

This module sets up the basic ADK infrastructure and provides
a simple interface for interacting with the CBT assistant.
"""

import asyncio
import sys

from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from src.agents.cbt_assistant import create_cbt_assistant


async def main():
    """Main entry point for the CBT Assistant."""
    print("CBT Reframing Assistant")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the conversation.")
    print("=" * 50)
    print()

    # Create the agent
    agent = create_cbt_assistant()

    # Create runner with default session service
    # InMemoryRunner includes InMemorySessionService for state management
    runner = InMemoryRunner(agent=agent)

    # Session info
    user_id = "user"
    session_id = "main_session"

    print("Session initialized. The assistant will remember context between turns.\n")

    # Simple interactive loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            # Check for exit commands
            if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                print(
                    "\nAssistant: Thank you for using the CBT Reframing Assistant. Take care!"
                )
                break

            # Skip empty input
            if not user_input:
                continue

            # Create message content
            message = Content(parts=[Part(text=user_input)], role="user")

            # Process with runner
            # The InMemoryRunner automatically manages session state
            async for event in runner.run_async(
                user_id=user_id, session_id=session_id, new_message=message
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    response = event.content.parts[0].text
                    print(f"\nAssistant: {response}\n")

        except KeyboardInterrupt:
            print("\n\nAssistant: Session interrupted. Take care!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.\n")


if __name__ == "__main__":
    # Run the main async function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
