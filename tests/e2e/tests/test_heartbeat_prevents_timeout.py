"""
Test that heartbeats prevent SSE timeout even without agent responses.
"""
import pytest
from playwright.async_api import Page
from pages.home_page import HomePage


@pytest.mark.asyncio
async def test_heartbeats_prevent_timeout(
    authenticated_page: Page,
    backend_ready
):
    """Test that backend heartbeats prevent connection timeout."""
    home = HomePage(authenticated_page)
    
    print("\n=== Testing heartbeats prevent timeout ===")
    
    # Track connection status
    heartbeat_count = 0
    disconnected = False
    
    def monitor_console(msg):
        nonlocal heartbeat_count, disconnected
        text = msg.text
        
        if "heartbeat" in text.lower():
            heartbeat_count += 1
            print(f"💓 Heartbeat #{heartbeat_count} received")
        
        if "disconnected" in text.lower() or "timeout" in text.lower():
            disconnected = True
            print(f"❌ DISCONNECTION/TIMEOUT: {text}")
    
    authenticated_page.on("console", monitor_console)
    
    # Just wait for 65 seconds (longer than 60s timeout)
    print("\n⏳ Monitoring connection for 65 seconds...")
    print("   (SSE timeout is 60 seconds without events)")
    
    # Check every 15 seconds, then final check at 65s
    for i in range(4):
        await authenticated_page.wait_for_timeout(15000)
        
        elapsed = (i + 1) * 15
        print(f"\n[{elapsed}s] Status check:")
        print(f"  - Heartbeats received: {heartbeat_count}")
        print(f"  - Connection lost: {disconnected}")
        
        # Check UI for disconnected message
        disconnected_visible = await home.is_visible('text="Disconnected"', timeout=100)
        print(f"  - UI shows disconnected: {disconnected_visible}")
        
        if disconnected or disconnected_visible:
            print(f"\n❌ Connection lost after {elapsed} seconds!")
            break
    
    # Wait final 5 seconds to reach 65s total
    await authenticated_page.wait_for_timeout(5000)
    
    # Final check
    print(f"\n✅ Final results after 65 seconds:")
    print(f"  - Total heartbeats: {heartbeat_count}")
    print(f"  - Expected heartbeats: ~4 (one every 15s)")
    print(f"  - Connection status: {'LOST' if disconnected else 'ALIVE'}")
    
    # Should have received at least 4 heartbeats in 65 seconds
    assert heartbeat_count >= 4, f"Expected at least 4 heartbeats, got {heartbeat_count}"
    
    # Connection should NOT have timed out
    assert not disconnected, "Connection should not timeout with regular heartbeats"
    
    # UI should NOT show disconnected
    disconnected_visible = await home.is_visible('text="Disconnected"', timeout=1000)
    assert not disconnected_visible, "UI should not show disconnected with regular heartbeats"
    
    print("\n✅ Heartbeats successfully prevented timeout!")