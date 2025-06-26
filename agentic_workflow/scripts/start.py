#!/usr/bin/env python3
"""Start the application with pre-downloaded prompts."""

import asyncio
from pathlib import Path
import sys

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reframe.core.orchestrator import POCReframeOrchestrator
from reframe.infrastructure.prompts import prompt_manager


async def start_application():
    """Download prompts and start the application."""

    # Step 1: Download prompts
    try:
        prompt_manager.download_all_prompts()
    except Exception:
        sys.exit(1)

    # Step 2: Start the orchestrator

    try:
        orchestrator = POCReframeOrchestrator()
        initial_message = input("What's on your mind today? ")
        await orchestrator.run_session(user_id="cli_user", initial_message=initial_message)
        orchestrator.langfuse.flush()
    except KeyboardInterrupt:
        pass
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(start_application())
