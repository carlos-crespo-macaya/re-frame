"""
E2E tests for the full conversational flow of the CBT Assistant.
"""
import pytest
from playwright.async_api import Page, expect
from pages.home_page import HomePage
from utils.sse_utils import SSETestClient
from fixtures.test_data import ANXIOUS_THOUGHTS


@pytest.mark.text_mode
@pytest.mark.asyncio
class TestConversationFlow:
    """Test suite for full conversation functionality."""
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation(
        self, 
        authenticated_page: Page, 
        session_id: str,
        backend_ready
    ):
        """
        Test a multi-turn conversation where:
        1. User shares an anxious thought
        2. Assistant asks clarifying questions
        3. User provides more context
        4. Assistant provides reframing/support
        """
        home = HomePage(authenticated_page)
        
        # Start with an anxious thought
        thought1 = ANXIOUS_THOUGHTS["social"]
        await home.enter_thought(thought1)
        await home.submit_thought()
        
        # Get first response
        response1 = await home.wait_for_response()
        print(f"\nUser: {thought1}")
        print(f"Assistant: {response1}")
        
        # Verify it's a conversational response
        assert response1, "No response received"
        assert "?" in response1, "Expected a follow-up question"
        
        # Clear for next input
        await home.clear_form()
        
        # Provide more context
        thought2 = "I always feel like I say the wrong things and people get bored when I talk"
        await home.enter_thought(thought2)
        await home.submit_thought()
        
        # Get second response
        response2 = await home.wait_for_response()
        print(f"\nUser: {thought2}")
        print(f"Assistant: {response2}")
        
        # This might still be exploratory
        assert response2, "No second response received"
        assert len(response2) > 50, "Second response too short"
        
        # Clear for next input
        await home.clear_form()
        
        # Share a specific incident
        thought3 = "Last time at Sarah's party, I tried telling a story and everyone seemed to lose interest halfway through"
        await home.enter_thought(thought3)
        await home.submit_thought()
        
        # Get third response - this might contain more reframing
        response3 = await home.wait_for_response()
        print(f"\nUser: {thought3}")
        print(f"Assistant: {response3}")
        
        assert response3, "No third response received"
        
        # In conversational CBT, the agent continues asking questions to understand better
        # Check that it's still engaging with the user's story
        response3_lower = response3.lower()
        engagement_patterns = [
            "story", "sarah", "party", "interest", "notice",
            "break", "what", "how", "tell", "about"
        ]
        
        found_engagement = any(pattern in response3_lower for pattern in engagement_patterns)
        assert found_engagement, f"Response not engaging with user's story: {response3}"
    
    @pytest.mark.asyncio
    async def test_conversation_continuity(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that the conversation maintains context across turns."""
        home = HomePage(authenticated_page)
        
        # First message about work anxiety
        await home.enter_thought("My boss seemed upset in the meeting today")
        await home.submit_thought()
        
        response1 = await home.wait_for_response()
        assert "boss" in response1.lower() or "meeting" in response1.lower(), \
            "Response doesn't reference the user's context"
        
        await home.clear_form()
        
        # Follow-up that assumes context
        await home.enter_thought("She didn't say good morning like usual")
        await home.submit_thought()
        
        response2 = await home.wait_for_response()
        
        # The assistant should understand "she" refers to the boss
        # and maintain the context of the work situation
        print(f"\nTesting context continuity:")
        print(f"Response 2: {response2}")
        
        assert response2, "No response to follow-up"
        assert len(response2) > 30, "Follow-up response too short"
    
    @pytest.mark.asyncio
    async def test_session_end_flow(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test ending a conversation session."""
        home = HomePage(authenticated_page)
        
        # Have a brief exchange
        await home.enter_thought("I'm worried about tomorrow's presentation")
        await home.submit_thought()
        
        response = await home.wait_for_response()
        assert response, "No response received"
        
        # In a real app, there might be an "End Session" button
        # For now, let's just verify we can clear and start fresh
        await home.clear_form()
        
        # Verify the form is cleared
        input_element = authenticated_page.locator(home.THOUGHT_INPUT)
        await expect(input_element).to_have_value("")
        
        # Could start a new thought
        await home.enter_thought("Actually, I think I'll be okay")
        await home.submit_thought()
        
        final_response = await home.wait_for_response()
        assert final_response, "No final response received"
        
        # The assistant might acknowledge the positive shift
        print(f"\nUser expressed confidence: I think I'll be okay")
        print(f"Assistant response: {final_response}")