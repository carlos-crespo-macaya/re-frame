"""Integration tests for Google AI Studio API calls.

These tests are skipped unless GOOGLE_AI_API_KEY is set in the environment.
Run with: GOOGLE_AI_API_KEY=your-key pytest tests/test_integration_google_ai.py -v
"""

import os

import pytest

from agents.base import ReFrameAgent


@pytest.mark.skipif(not os.getenv("GOOGLE_AI_API_KEY"), reason="GOOGLE_AI_API_KEY not set")
class TestGoogleAIIntegration:
    """Integration tests that make real API calls to Google AI Studio."""

    @pytest.mark.asyncio
    async def test_real_api_call_success(self):
        """Test successful API call to Google AI Studio."""
        agent = ReFrameAgent(
            name="TestAgent",
            instructions="You are a helpful assistant. Return a JSON object with a 'message' field containing a greeting.",
        )

        input_data = {"request": "Say hello"}
        response = await agent.run(input_data)

        assert response  # Should have content
        assert isinstance(response, str)

        # Try to parse the response
        parsed = agent.parse_json_response(response)
        assert "message" in parsed
        assert isinstance(parsed["message"], str)

    @pytest.mark.asyncio
    async def test_real_api_call_with_transparency(self):
        """Test API call with transparency tracking."""
        agent = ReFrameAgent(
            name="TestAgent",
            instructions="You are a helpful assistant. Return a JSON object with a 'result' field.",
        )

        input_data = {"query": "What is 2+2?"}
        result = await agent.process_with_transparency(input_data)

        assert result["success"] is True
        assert "response" in result
        assert "reasoning_path" in result
        assert result["agent_name"] == "TestAgent"
        assert result["model_used"] == "gemini-1.5-flash"

    @pytest.mark.asyncio
    async def test_empty_api_key_error(self):
        """Test that empty API key raises authentication error."""
        # Temporarily override the API key
        original_key = os.environ.get("GOOGLE_AI_API_KEY")
        os.environ["GOOGLE_AI_API_KEY"] = ""

        try:
            agent = ReFrameAgent(name="TestAgent", instructions="Test")

            result = await agent.process_with_transparency({"test": "data"})

            assert result["success"] is False
            assert result["error_type"] in ["auth", "unknown"]
        finally:
            # Restore original key
            if original_key:
                os.environ["GOOGLE_AI_API_KEY"] = original_key
            else:
                os.environ.pop("GOOGLE_AI_API_KEY", None)


# Manual test script (not run by pytest)
if __name__ == "__main__":
    import asyncio

    async def manual_test():
        """Manual test to verify API functionality."""
        print("Running manual API test...")
        print(f"API Key present: {'GOOGLE_AI_API_KEY' in os.environ}")

        if "GOOGLE_AI_API_KEY" not in os.environ:
            print("Please set GOOGLE_AI_API_KEY environment variable")
            return

        agent = ReFrameAgent(
            name="ManualTestAgent",
            instructions="""You are a CBT therapist assistant. 
Return a JSON object with these fields:
- thought: The original thought
- reframed: A more balanced perspective
- technique: The CBT technique used""",
        )

        test_input = {
            "thought": "Nobody likes me because I'm boring",
            "context": "At a party where people didn't talk to me much",
        }

        print("\nSending request to Google AI Studio...")
        result = await agent.process_with_transparency(test_input)

        if result["success"]:
            print("\n✅ Success!")
            print(f"Response: {result['response']}")
            try:
                parsed = agent.parse_json_response(result["response"])
                print("\nParsed response:")
                for key, value in parsed.items():
                    print(f"  {key}: {value}")
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
        else:
            print(f"\n❌ Error: {result['error']}")
            print(f"Error type: {result.get('error_type', 'unknown')}")

    asyncio.run(manual_test())
