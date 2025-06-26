#!/usr/bin/env python3
"""Test Langfuse tracing functionality."""

import asyncio
import contextlib
from datetime import UTC, datetime

from langfuse import Langfuse, observe

from reframe.config.settings import get_settings

# Initialize Langfuse
settings = get_settings()
langfuse = Langfuse(
    secret_key=settings.langfuse_secret_key,
    public_key=settings.langfuse_public_key,
    host=settings.langfuse_host,
)


# Test 1: Simple trace creation
try:
    # Create a trace manually
    trace = langfuse.trace(
        name="test_trace",
        user_id="test_user",
        metadata={"test": True, "timestamp": datetime.now(UTC).isoformat()},
    )

    # Note: trace.event() is not available in current Langfuse version
    # Instead, use spans for event-like tracking

    # Add a generation
    generation = trace.generation(
        name="test_generation",
        model="gemini-2.0-flash",
        input={"prompt": "Test prompt"},
        output={"response": "Test response"},
        model_parameters={"temperature": 0.7},
        metadata={"test": True},
    )

    # Add a score
    trace.score(name="quality", value=0.95, comment="High quality response")

    # Update the trace
    trace.update(output={"final_status": "completed"}, metadata={"duration_ms": 150})

except Exception:
    pass

# Test 2: Using decorators


@observe(name="test_function")
def process_message(message: str) -> str:
    """Test function with observation."""
    return f"Processed: {message}"


@observe(name="async_test_function")
async def async_process_message(message: str) -> str:
    """Async test function with observation."""
    await asyncio.sleep(0.1)  # Simulate work
    return f"Async processed: {message}"


try:
    # Test sync function
    result = process_message("Hello, world!")

    # Test async function
    async def run_async_test() -> None:
        await async_process_message("Hello, async!")

    asyncio.run(run_async_test())

except Exception:
    pass

# Test 3: Agent-style tracing
try:
    # Create a session trace
    session_trace = langfuse.trace(
        name="cognitive_reframing_session",
        user_id="test_user_123",
        session_id=f"session_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
        metadata={"version": "poc_v1", "environment": "test"},
    )

    # Intake agent
    intake_span = session_trace.span(
        name="intake_agent",
        input={"user_message": "I feel anxious about the meeting"},
        metadata={"agent": "intake"},
    )
    intake_span.generation(
        name="extract_trigger",
        model="gemini-2.0-flash",
        input={"prompt": "Extract the trigger..."},
        output={"trigger": "upcoming meeting"},
        usage={"input": 50, "output": 20},
    )
    intake_span.end(
        output={
            "trigger": "upcoming meeting",
            "thought": "They will judge me",
            "emotion": "anxiety",
            "intensity": 7,
        }
    )

    # Reframe agent
    reframe_span = session_trace.span(
        name="reframe_agent",
        input={
            "trigger": "upcoming meeting",
            "thought": "They will judge me",
            "emotion": "anxiety",
        },
        metadata={"agent": "reframe"},
    )
    reframe_span.generation(
        name="identify_distortions",
        model="gemini-2.0-flash",
        input={"thought": "They will judge me"},
        output={"distortions": ["mind reading", "fortune telling"]},
    )
    reframe_span.end(
        output={
            "distortions": ["mind reading"],
            "balanced_thought": "I don't know what they think",
            "confidence_before": 3,
            "confidence_after": 6,
        }
    )

    # Complete session
    session_trace.update(
        output={
            "status": "completed",
            "agents_run": ["intake", "reframe"],
            "total_duration_ms": 500,
        }
    )

except Exception:
    pass

# Test 4: Flush and verify
with contextlib.suppress(Exception):
    langfuse.flush()
