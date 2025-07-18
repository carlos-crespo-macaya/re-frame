"""
Test session persistence and reconnection after delays.
"""
import pytest
from playwright.async_api import Page
from pages.home_page import HomePage


class TestSessionPersistence:
    """Test that sessions persist across delays and potential disconnections."""
    
    @pytest.mark.asyncio
    async def test_session_persistence_with_delays(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that conversation continues correctly after delays between messages."""
        home = HomePage(authenticated_page)
        
        # Start a conversation about a specific topic
        print("\n=== Testing session persistence with delays ===")
        
        # First message - establish context
        thought1 = "I've been having trouble sleeping for the past week"
        await home.enter_thought(thought1)
        await home.submit_thought()
        
        response1 = await home.wait_for_response()
        print(f"\nUser: {thought1}")
        print(f"Assistant: {response1}")
        
        assert response1, "No initial response received"
        assert "sleep" in response1.lower() or "trouble" in response1.lower(), \
            "Response doesn't acknowledge sleep issue"
        
        # Simulate 30 seconds delay (more realistic for testing)
        print("\n⏱️  Simulating 30 second delay...")
        await authenticated_page.wait_for_timeout(30000)  # 30 seconds
        
        # Check connection status - we should see disconnection
        page_content = await authenticated_page.content()
        console_logs = []
        authenticated_page.on("console", lambda msg: console_logs.append(msg.text))
        
        # Clear form and continue conversation
        await home.clear_form()
        
        # Second message - reference the previous context implicitly
        thought2 = "I keep thinking about work deadlines when I try to sleep"
        await home.enter_thought(thought2)
        await home.submit_thought()
        
        # This should fail if reconnection doesn't work
        try:
            response2 = await home.wait_for_response(timeout=15000)
            print(f"\nUser: {thought2}")
            print(f"Assistant: {response2}")
            
            assert response2, "No response after delay"
            assert len(response2) > 30, "Response too short after delay"
            
            # Check that context is maintained (should reference sleep or work)
            response2_lower = response2.lower()
            context_maintained = any(word in response2_lower for word in 
                                   ["sleep", "deadline", "work", "thinking", "worry"])
            assert context_maintained, f"Context lost after delay. Response: {response2}"
            print("\n✅ Session persisted correctly across delay")
        except Exception as e:
            print(f"\n❌ Failed to get response after delay: {str(e)}")
            print(f"Console logs: {console_logs[-5:]}")  # Last 5 logs
            
            # Check if we see disconnection messages
            disconnected = any("disconnect" in log.lower() or "timeout" in log.lower() 
                             for log in console_logs)
            if disconnected:
                print("⚠️  Connection was lost and not properly restored")
            raise
    
    @pytest.mark.asyncio
    async def test_immediate_reconnection(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that the app reconnects immediately when connection is lost."""
        home = HomePage(authenticated_page)
        
        print("\n=== Testing immediate reconnection ===")
        
        # Monitor console for connection events
        connection_events = []
        def log_connection_event(msg):
            text = msg.text
            if any(keyword in text.lower() for keyword in ["connect", "disconnect", "sse", "error"]):
                connection_events.append(text)
                print(f"🔌 {text}")
        
        authenticated_page.on("console", log_connection_event)
        
        # Start a conversation
        thought1 = "I feel anxious about tomorrow's meeting"
        await home.enter_thought(thought1)
        await home.submit_thought()
        
        response1 = await home.wait_for_response()
        print(f"\nInitial response received: {response1[:100]}...")
        
        # Wait for potential timeout (based on the screenshot, seems to be around 30s)
        print("\n⏱️  Waiting for connection timeout...")
        await authenticated_page.wait_for_timeout(35000)  # 35 seconds
        
        # Check connection status in UI
        disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
        if disconnected_visible:
            print("⚠️  UI shows 'Disconnected' status")
        
        # Try to send another message - this should trigger reconnection
        await home.clear_form()
        thought2 = "I'm worried I'll forget important points"
        await home.enter_thought(thought2)
        
        # Check if submit button is enabled
        submit_button = authenticated_page.locator(home.SUBMIT_BUTTON)
        is_enabled = await submit_button.is_enabled()
        
        if not is_enabled:
            print("❌ Submit button is disabled after disconnection")
            assert False, "Cannot submit after disconnection - reconnection not working"
        
        await home.submit_thought()
        
        # Should reconnect and get response
        try:
            response2 = await home.wait_for_response(timeout=30000)
            print(f"\n✅ Reconnected and received response: {response2[:100]}...")
        except Exception as e:
            print(f"\n❌ Failed to reconnect: {str(e)}")
            print(f"Connection events: {connection_events[-10:]}")  # Last 10 events
            raise
    
    @pytest.mark.asyncio 
    async def test_heartbeat_keeps_connection_alive(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that heartbeat messages keep the connection alive."""
        home = HomePage(authenticated_page)
        
        print("\n=== Testing heartbeat keeps connection alive ===")
        
        # Monitor console for heartbeat messages
        heartbeat_count = 0
        def count_heartbeats(msg):
            nonlocal heartbeat_count
            if "heartbeat" in msg.text.lower():
                heartbeat_count += 1
                print(f"💓 Heartbeat #{heartbeat_count} received")
        
        authenticated_page.on("console", count_heartbeats)
        
        # Wait for initial connection
        await authenticated_page.wait_for_timeout(2000)
        
        # Start a conversation
        await home.enter_thought("Hello")
        await home.submit_thought()
        await home.wait_for_response()
        
        # Wait for 45 seconds (should receive ~2 heartbeats)
        print("⏱️  Waiting 45 seconds to verify heartbeats...")
        await authenticated_page.wait_for_timeout(45000)
        
        # Should have received heartbeats
        assert heartbeat_count >= 2, f"Expected at least 2 heartbeats, got {heartbeat_count}"
        
        # Connection should still be alive (no Disconnected message)
        disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
        assert not disconnected_visible, "Connection should still be alive thanks to heartbeats"
        
        print(f"✅ Connection stayed alive with {heartbeat_count} heartbeats")
        
        # Take screenshot for debugging
        await authenticated_page.screenshot(path="disconnected_state.png")
        print("📸 Screenshot saved as disconnected_state.png")
        
        # Submit a new message
        await home.clear_form()
        await home.enter_thought("Testing continuous conversation")
        await home.submit_thought()
        
        # Should get response without reconnection issues
        try:
            response = await home.wait_for_response(timeout=30000)
            print(f"✅ Got response: {response[:100]}...")
            
            # Verify no disconnection happened
            disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
            assert not disconnected_visible, "Should not show disconnected during active conversation"
        except Exception as e:
            print(f"❌ Failed to continue conversation: {str(e)}")
            raise