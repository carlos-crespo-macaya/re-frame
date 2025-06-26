#!/usr/bin/env python3
"""CLI entry point for re-frame assistant."""

import asyncio
from pathlib import Path
import sys

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reframe.core.orchestrator import POCReframeOrchestrator


async def main():
    """Run the CLI interface."""
    orchestrator = POCReframeOrchestrator()

    # Get initial input
    initial_message = input("What's on your mind today? ")

    # Run session
    await orchestrator.run_session(
        user_id="cli_user",
        initial_message=initial_message
    )

    # Ensure traces are sent
    orchestrator.langfuse.flush()


if __name__ == "__main__":
    asyncio.run(main())
