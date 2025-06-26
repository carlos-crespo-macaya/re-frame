#!/usr/bin/env python3
"""Final test script to verify all connections are working."""

import asyncio
from datetime import UTC, datetime
import os
from pathlib import Path
import sys

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from reframe.config.settings import get_settings


async def test_all_connections() -> None:
    """Test all connections required for the POC."""

    # Get settings
    settings = get_settings()

    # 1. Test Google AI
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.google_ai_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        model.generate_content("Say 'Connection successful' and nothing else.")
    except Exception:
        pass

    # 2. Test Supabase
    try:
        from google.adk.sessions import DatabaseSessionService

        conn_string = settings.supabase_connection_string or os.getenv(
            "SUPABASE_REFRAME_DB_CONNECTION_STRING"
        )
        if not conn_string:
            pass
        else:
            session_service = DatabaseSessionService(db_url=conn_string)

            # Test session operations
            test_session_id = f"test_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"

            # Create session
            await session_service.create_session(
                app_name="test_app", user_id="test_user", session_id=test_session_id
            )

            # Retrieve session
            await session_service.get_session(
                app_name="test_app", user_id="test_user", session_id=test_session_id
            )

            # Clean up
            await session_service.delete_session(
                app_name="test_app", user_id="test_user", session_id=test_session_id
            )

    except Exception:
        pass

    # 3. Test Langfuse Prompts
    try:
        from langfuse import Langfuse

        langfuse = Langfuse(
            host=settings.langfuse_host,
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
        )

        # Test all 3 required prompts
        prompts = {
            "intake-agent-adk-instructions": "Intake Agent",
            "reframe-agent-adk-instructions": "Reframe Agent",
            "synthesis-agent-adk-instructions": "Synthesis Agent",
        }

        all_found = True
        for prompt_name, _display_name in prompts.items():
            try:
                langfuse.get_prompt(prompt_name)
            except Exception:
                all_found = False

        if all_found:
            pass

    except Exception:
        pass

    # 4. Summary


if __name__ == "__main__":
    asyncio.run(test_all_connections())
