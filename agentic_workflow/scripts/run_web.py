#!/usr/bin/env python3
"""Run the cognitive reframing agents as a web service using ADK's built-in server.

This script sets up the agents to run with ADK's web interface or API server.
"""

import os
from google.adk.runner import Runner
from reframe.orchestrators.multilingual_orchestrator import MultilingualReframeOrchestrator


def main():
    """Main entry point for running agents as web service."""
    # Check for required environment variables
    required_vars = [
        "GOOGLE_API_KEY",
        "LANGFUSE_HOST",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these environment variables before running ADK:")
        for var in missing_vars:
            print(f"  export {var}='your-value'")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Initialize multilingual orchestrator
    orchestrator = MultilingualReframeOrchestrator()

    # Create runner with the sequential pipeline
    return Runner(
        agent=orchestrator.pipeline,
        app_name="multilingual_reframe_assistant",
        session_service=orchestrator.session_service
    )


# Create runner at module level for ADK to find
try:
    runner = main()
except RuntimeError as e:
    print(f"\n⚠️  ADK Runner initialization failed: {e}")
    print("\n📋 Quick fix:")
    print("1. Set the required environment variables")
    print("2. Run 'adk web' again")
    runner = None  # ADK will fail gracefully

if __name__ == "__main__":
    # For direct execution if needed
    if not runner:
        print("Runner initialization failed. Check environment variables.")