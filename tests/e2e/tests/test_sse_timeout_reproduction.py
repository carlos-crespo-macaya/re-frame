"""
Test to reproduce the exact SSE timeout issue from the logs.
"""
import pytest
from playwright.async_api import Page
from pages.home_page import HomePage


@pytest.mark.asyncio
async def test_reproduce_sse_timeout_issue(
    authenticated_page: Page,
    backend_ready
):
    """Reproduce the exact timeout issue from the user's logs."""
    home = HomePage(authenticated_page)
    
    print("\n=== Reproducing SSE timeout issue ===")
    
    # Monitor console for key events
    timeout_detected = False
    reconnection_attempts = 0
    
    def monitor_console(msg):
        nonlocal timeout_detected, reconnection_attempts
        text = msg.text
        
        # Log all SSE-related messages
        if any(keyword in text.lower() for keyword in ['sse', 'heartbeat', 'timeout', 'disconnect', 'reconnect']):
            print(f"🔍 Console: {text}")
        
        # Check for the specific error pattern from logs
        if "No events received, reconnecting..." in text:
            timeout_detected = True
            print(f"⚠️ TIMEOUT DETECTED: {text}")
        
        if "SSE connection error: Error: Connection timeout" in text:
            reconnection_attempts += 1
            print(f"❌ CONNECTION ERROR #{reconnection_attempts}: {text}")
    
    authenticated_page.on("console", monitor_console)
    
    # Simulate the conversation from the logs
    print("\n1️⃣ Sending first message...")
    await home.enter_thought("hi")
    await home.submit_thought()
    
    # Wait for response
    response1 = await home.wait_for_response()
    print(f"✅ Got response 1: {response1[:50]}...")
    
    # Send second message (longer one from logs)
    print("\n2️⃣ Sending second message...")
    message2 = """hello I am sad, because I have been Slowly isolating myself in work. Now everybody ignores me and I feel alone. I am sad about that, but I don't know what to do.

Any situation in which there is a group involved, I can interact with one person very well, but when there is a group, I just blackout, basically."""
    
    await home.clear_form()
    await home.enter_thought(message2)
    await home.submit_thought()
    
    # Wait for response
    print("⏳ Waiting for second response...")
    response2 = await home.wait_for_response()
    print(f"✅ Got response 2: {response2[:50]}...")
    
    # Now wait and monitor - this is where timeout happens in logs
    print("\n⏳ Monitoring for timeout (45 seconds)...")
    await authenticated_page.wait_for_timeout(45000)
    
    # Check for timeout
    if timeout_detected:
        print(f"\n❌ TIMEOUT OCCURRED!")
        print(f"   Reconnection attempts: {reconnection_attempts}")
        
        # Take screenshot
        await authenticated_page.screenshot(path="sse_timeout_reproduced.png")
        
        # Check UI state
        disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
        print(f"   UI shows disconnected: {disconnected_visible}")
    else:
        print(f"\n✅ No timeout detected after 45 seconds")
    
    # The bug is that timeout SHOULD NOT occur here
    assert not timeout_detected, "SSE connection timed out when it shouldn't have"