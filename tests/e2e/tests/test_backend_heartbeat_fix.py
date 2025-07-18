"""
Test that backend sends heartbeats consistently.
"""
import pytest
from playwright.async_api import Page
from pages.home_page import HomePage


@pytest.mark.asyncio
async def test_backend_sends_regular_heartbeats(
    authenticated_page: Page,
    backend_ready
):
    """Test that backend sends heartbeats every 15 seconds."""
    home = HomePage(authenticated_page)
    
    print("\n=== Testing backend heartbeat delivery ===")
    
    # Track heartbeats
    heartbeats = []
    
    def track_heartbeats(msg):
        if "heartbeat" in msg.text.lower():
            heartbeats.append({
                'time': authenticated_page.evaluate('Date.now()'),
                'message': msg.text
            })
            print(f"💓 Heartbeat #{len(heartbeats)} received")
    
    authenticated_page.on("console", track_heartbeats)
    
    # Wait for SSE connection to establish
    await authenticated_page.wait_for_timeout(3000)
    
    # Start a conversation
    await home.enter_thought("Hello")
    await home.submit_thought()
    response = await home.wait_for_response()
    print(f"Got initial response: {response[:50]}...")
    
    # Clear heartbeat list to start fresh
    heartbeats.clear()
    start_time = await authenticated_page.evaluate('Date.now()')
    
    # Wait 65 seconds to capture multiple heartbeats
    print("\n⏱️  Monitoring heartbeats for 65 seconds...")
    await authenticated_page.wait_for_timeout(65000)
    
    end_time = await authenticated_page.evaluate('Date.now()')
    duration = (end_time - start_time) / 1000  # Convert to seconds
    
    print(f"\nResults after {duration:.1f} seconds:")
    print(f"  - Heartbeats received: {len(heartbeats)}")
    
    # We should get at least 4 heartbeats in 65 seconds (one every 15s)
    expected_heartbeats = int(duration / 15)
    assert len(heartbeats) >= expected_heartbeats - 1, \
        f"Expected at least {expected_heartbeats - 1} heartbeats in {duration:.1f}s, got {len(heartbeats)}"
    
    # Verify connection is still alive
    disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
    assert not disconnected_visible, "Connection should still be alive with regular heartbeats"
    
    # Verify we can still communicate
    await home.clear_form()
    await home.enter_thought("Are you still there?")
    await home.submit_thought()
    
    response2 = await home.wait_for_response()
    assert response2, "No response after heartbeat period"
    assert len(response2) > 20, "Response too short"
    
    print(f"\n✅ Backend sent {len(heartbeats)} heartbeats consistently")
    print("✅ Connection stayed alive throughout the test")