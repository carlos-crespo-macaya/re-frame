"""
Simple test to check if backend is sending heartbeats.
"""
import pytest
import asyncio
import aiohttp
from datetime import datetime


@pytest.mark.asyncio
async def test_backend_heartbeat_stream():
    """Test that backend sends heartbeats in SSE stream."""
    print("\n=== Testing backend heartbeat stream ===")
    
    backend_url = "http://localhost:8000"
    session_id = f"test-{datetime.now().timestamp()}"
    
    heartbeats = []
    messages = []
    
    async with aiohttp.ClientSession() as session:
        url = f"{backend_url}/api/events/{session_id}?language=en-US"
        
        print(f"Connecting to SSE endpoint: {url}")
        
        async with session.get(url) as response:
            print(f"Response status: {response.status}")
            
            if response.status != 200:
                print(f"Failed to connect: {await response.text()}")
                return
            
            # Read SSE stream for 35 seconds
            start_time = asyncio.get_event_loop().time()
            timeout = 35  # seconds
            
            async for line in response.content:
                current_time = asyncio.get_event_loop().time()
                elapsed = current_time - start_time
                
                if elapsed > timeout:
                    break
                
                line_str = line.decode('utf-8').strip()
                
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    
                    try:
                        import json
                        data = json.loads(data_str)
                        
                        print(f"[{elapsed:.1f}s] Received: {data}")
                        messages.append((elapsed, data))
                        
                        if data.get('type') == 'heartbeat':
                            heartbeats.append((elapsed, data))
                            print(f"💓 Heartbeat #{len(heartbeats)} at {elapsed:.1f}s")
                    except json.JSONDecodeError:
                        print(f"Failed to parse: {data_str}")
    
    print(f"\nResults:")
    print(f"  Total messages: {len(messages)}")
    print(f"  Heartbeats received: {len(heartbeats)}")
    
    # We should get at least 2 heartbeats in 35 seconds (one every 15s)
    assert len(heartbeats) >= 2, f"Expected at least 2 heartbeats, got {len(heartbeats)}"
    
    # Check heartbeat spacing
    if len(heartbeats) >= 2:
        for i in range(1, len(heartbeats)):
            time_diff = heartbeats[i][0] - heartbeats[i-1][0]
            print(f"  Heartbeat interval {i}: {time_diff:.1f}s")
            # Allow some variance (13-17 seconds)
            assert 13 <= time_diff <= 17, f"Heartbeat interval should be ~15s, got {time_diff:.1f}s"
    
    print("✅ Backend sends heartbeats correctly")