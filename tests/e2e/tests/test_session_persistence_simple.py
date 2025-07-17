"""
Simple test to verify session persistence with delays.
"""
import pytest
from playwright.async_api import Page
from pages.home_page import HomePage


@pytest.mark.asyncio
async def test_session_stays_alive_with_delays(
    authenticated_page: Page,
    backend_ready
):
    """Test that conversation works after delays without disconnection."""
    home = HomePage(authenticated_page)
    
    print("\n=== Testing session persistence with delays ===")
    
    # First message
    thought1 = "I've been feeling anxious about work"
    await home.enter_thought(thought1)
    await home.submit_thought()
    
    response1 = await home.wait_for_response()
    print(f"\nUser: {thought1}")
    print(f"Assistant: {response1[:100]}...")
    
    assert response1, "No initial response received"
    
    # Wait 40 seconds (longer than old timeout, but should stay alive with heartbeats)
    print("\n⏱️  Waiting 40 seconds...")
    await authenticated_page.wait_for_timeout(40000)
    
    # Check connection status - should NOT show disconnected
    disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
    if disconnected_visible:
        print("❌ Connection lost after 40 seconds")
        # Take screenshot for debugging
        await authenticated_page.screenshot(path="disconnected_after_delay.png")
    else:
        print("✅ Connection still alive after 40 seconds")
    
    assert not disconnected_visible, "Connection should stay alive with heartbeats"
    
    # Continue conversation
    await home.clear_form()
    thought2 = "I worry about making mistakes"
    await home.enter_thought(thought2)
    await home.submit_thought()
    
    response2 = await home.wait_for_response()
    print(f"\nUser: {thought2}")
    print(f"Assistant: {response2[:100]}...")
    
    assert response2, "No response after delay"
    assert len(response2) > 30, "Response too short after delay"
    
    print("\n✅ Session persisted successfully!")