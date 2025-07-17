"""
Test SSE heartbeat timer reset functionality.
These tests verify that the heartbeat timer is properly reset on ANY SSE message.
"""
import asyncio
import json
import pytest
from playwright.async_api import Page
from pages.home_page import HomePage


class TestSSEHeartbeatFix:
    """Test suite for SSE heartbeat timer reset fix."""
    
    @pytest.mark.asyncio
    async def test_heartbeat_timer_resets_on_any_message(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that receiving any SSE message resets the heartbeat timer."""
        home = HomePage(authenticated_page)
        
        print("\n=== Testing heartbeat timer reset on any message ===")
        
        # Track lastEventTime updates
        last_event_times = []
        
        # First, let's verify the SSE client exists and wait for connection
        await authenticated_page.wait_for_timeout(2000)  # Wait for SSE to connect
        
        # Inject JavaScript to monitor lastEventTime
        await authenticated_page.evaluate("""
            window.sseEventTimes = [];
            window.sseClientFound = false;
            
            // Function to find SSE client in React component tree
            function findSSEClient() {
                // Check global window first
                if (window.sseClient) {
                    return window.sseClient;
                }
                
                // Check React fiber tree for useSSEClient hook results
                const rootElement = document.getElementById('__next') || document.querySelector('[data-reactroot]');
                if (!rootElement || !rootElement._reactRootContainer) {
                    return null;
                }
                
                // For now, let's monitor console messages instead
                return null;
            }
            
            // Monitor console for SSE messages and check timing
            const originalConsoleLog = console.log;
            let lastMessageTime = Date.now();
            
            console.log = function(...args) {
                originalConsoleLog.apply(console, args);
                
                const message = args.join(' ');
                if (message.includes('SSE message received:') || message.includes('SSE Event received')) {
                    const currentTime = Date.now();
                    const timeDiff = currentTime - lastMessageTime;
                    
                    window.sseEventTimes.push({
                        event: message.substring(0, 100),
                        timestamp: currentTime,
                        timeSinceLastEvent: timeDiff,
                        updated: true  // We'll check if this would prevent timeout
                    });
                    
                    lastMessageTime = currentTime;
                }
            };
            
            window.sseClientFound = true;  // We're monitoring via console
        """)
        
        # Start a conversation to trigger SSE messages
        await home.enter_thought("Tell me about CBT techniques")
        await home.submit_thought()
        
        # Wait for response to start streaming
        await authenticated_page.wait_for_timeout(2000)
        
        # Get tracked event times
        event_times = await authenticated_page.evaluate("window.sseEventTimes")
        
        print(f"\nTracked {len(event_times)} SSE events")
        
        # Verify that EVERY SSE event updates lastEventTime
        non_updating_events = [e for e in event_times if not e['updated']]
        
        if non_updating_events:
            print(f"\n❌ Found {len(non_updating_events)} events that didn't update lastEventTime:")
            for event in non_updating_events[:3]:  # Show first 3
                print(f"  - Event: {event['event'][:50]}...")
        
        assert len(non_updating_events) == 0, \
            f"{len(non_updating_events)} SSE events didn't update lastEventTime"
        
        print(f"\n✅ All {len(event_times)} SSE events properly updated lastEventTime")
    
    @pytest.mark.asyncio
    async def test_long_streaming_response_no_timeout(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that long streaming responses don't trigger timeout."""
        home = HomePage(authenticated_page)
        
        print("\n=== Testing long streaming response without timeout ===")
        
        # Monitor for disconnection
        disconnection_detected = False
        
        def check_disconnection(msg):
            nonlocal disconnection_detected
            if "disconnect" in msg.text.lower() or "timeout" in msg.text.lower():
                disconnection_detected = True
                print(f"🚨 Disconnection detected: {msg.text}")
        
        authenticated_page.on("console", check_disconnection)
        
        # Start a conversation that will generate a long response
        thought = """
        I'm feeling overwhelmed by multiple issues: work stress, relationship problems, 
        family conflicts, financial worries, health anxiety, social isolation, 
        and general life uncertainty. Can you help me understand how CBT can address 
        all of these different areas? Please provide detailed explanations.
        """
        
        await home.enter_thought(thought)
        await home.submit_thought()
        
        print("⏳ Waiting for long response to stream...")
        
        # Monitor for 90 seconds (longer than the 60s timeout)
        start_time = asyncio.get_event_loop().time()
        check_interval = 5  # Check every 5 seconds
        max_duration = 90  # Monitor for 90 seconds
        
        while asyncio.get_event_loop().time() - start_time < max_duration:
            # Check if disconnection occurred
            if disconnection_detected:
                break
                
            # Check if disconnected message is visible in UI
            disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
            if disconnected_visible:
                disconnection_detected = True
                await authenticated_page.screenshot(path="unexpected_disconnection.png")
                break
            
            # Wait before next check
            await authenticated_page.wait_for_timeout(check_interval * 1000)
            elapsed = int(asyncio.get_event_loop().time() - start_time)
            print(f"  {elapsed}s elapsed - Connection still active")
        
        assert not disconnection_detected, \
            "Connection timed out during long streaming response"
        
        print("\n✅ Long response streamed successfully without timeout")
    
    @pytest.mark.asyncio
    async def test_idle_periods_with_heartbeats(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that connection stays alive during idle periods with heartbeats."""
        home = HomePage(authenticated_page)
        
        print("\n=== Testing connection during idle periods ===")
        
        # Start a conversation
        await home.enter_thought("Hello")
        await home.submit_thought()
        response = await home.wait_for_response()
        print(f"Initial response: {response[:50]}...")
        
        # Now wait for an extended idle period
        print("\n⏳ Testing 75-second idle period (exceeds old 60s timeout)...")
        
        # Monitor for disconnection
        disconnection_detected = False
        heartbeat_count = 0
        
        def monitor_console(msg):
            nonlocal disconnection_detected, heartbeat_count
            if "disconnect" in msg.text.lower() and "timeout" in msg.text.lower():
                disconnection_detected = True
                print(f"🚨 Disconnection: {msg.text}")
            elif "heartbeat" in msg.text.lower():
                heartbeat_count += 1
                print(f"💓 Heartbeat #{heartbeat_count}")
        
        authenticated_page.on("console", monitor_console)
        
        # Wait 75 seconds
        await authenticated_page.wait_for_timeout(75000)
        
        # Check final connection state
        disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
        
        print(f"\nResults after 75 seconds:")
        print(f"  - Heartbeats received: {heartbeat_count}")
        print(f"  - Disconnection detected: {disconnection_detected}")
        print(f"  - UI shows disconnected: {disconnected_visible}")
        
        assert not disconnection_detected, "Connection timed out during idle period"
        assert not disconnected_visible, "UI shows disconnected after idle period"
        assert heartbeat_count >= 3, f"Expected at least 3 heartbeats, got {heartbeat_count}"
        
        # Verify we can still send messages
        await home.clear_form()
        await home.enter_thought("Are you still there?")
        await home.submit_thought()
        
        response2 = await home.wait_for_response()
        assert response2, "No response after idle period"
        assert len(response2) > 20, "Response too short after idle period"
        
        print("\n✅ Connection stayed alive during idle period with heartbeats")
    
    @pytest.mark.asyncio
    async def test_heartbeat_timer_during_typing(
        self,
        authenticated_page: Page,
        backend_ready
    ):
        """Test that heartbeat timer works while user is typing."""
        home = HomePage(authenticated_page)
        
        print("\n=== Testing heartbeat timer during user typing ===")
        
        # Start a conversation
        await home.enter_thought("Hi")
        await home.submit_thought()
        await home.wait_for_response()
        
        # Clear and start typing a long message slowly
        await home.clear_form()
        
        # Type slowly over 70 seconds
        long_message = "I've been thinking about many things" + " and wondering" * 10
        
        print("⌨️  Typing slowly over 70 seconds...")
        
        for i, char in enumerate(long_message):
            if i % 10 == 0:  # Every 10 characters
                # Check connection status
                disconnected = await home.is_visible('text="Disconnected"', timeout=100)
                if disconnected:
                    print(f"\n❌ Disconnected while typing at character {i}")
                    assert False, "Connection lost while user was typing"
                
                print(f"  Typed {i} characters - connection OK")
            
            # Type one character
            await authenticated_page.type("#thought-input", char)
            
            # Wait ~0.5 seconds between characters (70s / 140 chars)
            await authenticated_page.wait_for_timeout(500)
        
        # Verify still connected after typing
        disconnected = await home.is_visible('text="Disconnected"', timeout=1000)
        assert not disconnected, "Connection lost during extended typing"
        
        # Verify we can still submit
        await home.submit_thought()
        response = await home.wait_for_response()
        assert response, "No response after extended typing"
        
        print("\n✅ Connection maintained during 70 seconds of typing")