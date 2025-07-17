# SSE Connection Timeout Issue - Analysis and Fix Proposal

## Problem Analysis

### What's Happening
1. User starts a conversation successfully
2. After the second response, the SSE connection times out with "No events received, reconnecting..."
3. The backend continues to send messages (including heartbeats) but they're not being received by the frontend
4. The frontend enters an infinite reconnection loop but never successfully reconnects
5. The UI shows "Disconnected - Connection timeout" and becomes unusable

### Root Cause Analysis

Looking at the logs, I identified several issues:

1. **Heartbeat Timing Issue**: The heartbeat is sent at the 2-minute mark (12:03:10), but the connection timeout happens before the next heartbeat at 12:04:58
   - The heartbeat interval is 20 seconds in the backend
   - The frontend expects heartbeats every 30 seconds but times out after 60 seconds
   - There's a gap where no heartbeat arrives in time

2. **Messages Not Triggering Activity Update**: Regular messages from the backend are not resetting the heartbeat timer
   - The frontend only updates `lastEventTime` when processing messages, but not for all SSE events
   - The heartbeat check is looking for "no events" but messages ARE being received

3. **Reconnection Failure**: When the connection times out, the reconnection attempts fail
   - The frontend tries to reconnect but the old EventSource isn't properly closed
   - Multiple reconnection attempts are happening simultaneously

## Proposed Fix

### 1. Fix Heartbeat Timer Reset (Frontend)

The main issue is that the heartbeat timer isn't being reset when receiving ANY message, only when processing specific message types.

**File: `/frontend/lib/streaming/sse-client.ts`**

```typescript
// In the connect method, update the event listener:
this.eventSource.onmessage = (event) => {
  // Reset heartbeat timer on ANY message received
  this.lastEventTime = Date.now();
  this.handleMessage(event);
};
```

### 2. Fix Backend Heartbeat Logic

The backend heartbeat logic has a flaw - it only sends heartbeats between agent messages, not during agent message streaming.

**File: `/backend/src/main.py`**

```python
async def event_generator():
    heartbeat_task = None
    last_heartbeat = time.time()
    
    async def send_heartbeat_if_needed():
        nonlocal last_heartbeat
        current_time = time.time()
        if current_time - last_heartbeat > 15:  # Send every 15 seconds
            yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
            last_heartbeat = current_time
    
    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'session_id': session_id})}\n\n"
        
        # Create a task for periodic heartbeats
        async def heartbeat_loop():
            while True:
                await asyncio.sleep(15)  # Check every 15 seconds
                try:
                    async for data in send_heartbeat_if_needed():
                        yield data
                except:
                    break
        
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(heartbeat_loop())
        
        # Process agent messages
        async for data in agent_to_client_sse(live_events):
            yield data
            # Also check for heartbeat after each message
            async for hb in send_heartbeat_if_needed():
                yield hb
                
    except Exception as e:
        print(f"Error in SSE stream: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    finally:
        if heartbeat_task:
            heartbeat_task.cancel()
        cleanup()
```

### 3. Improve Reconnection Logic (Frontend)

**File: `/frontend/lib/streaming/sse-client.ts`**

```typescript
private async attemptReconnect(): Promise<void> {
  // Cancel any existing reconnection attempts
  this.clearReconnectTimer();
  
  if (this.reconnectAttempts >= this.options.maxReconnectAttempts) {
    console.error('Max reconnection attempts reached');
    this.disconnect();
    return;
  }
  
  // Ensure old connection is fully closed
  if (this.eventSource) {
    this.eventSource.close();
    this.eventSource = null;
  }
  
  this.reconnectAttempts++;
  this.options.onReconnect(this.reconnectAttempts);
  
  // Add exponential backoff
  const backoffTime = Math.min(
    this.options.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
    30000 // Max 30 seconds
  );
  
  this.reconnectTimer = setTimeout(() => {
    if (this.session) {
      this.connect(this.session.id, this.currentLanguage).catch(console.error);
    }
  }, backoffTime);
}
```

### 4. Add Connection State Management

**File: `/frontend/lib/streaming/sse-client.ts`**

```typescript
private connectionState: 'disconnected' | 'connecting' | 'connected' | 'reconnecting' = 'disconnected';

private updateConnectionState(state: typeof this.connectionState): void {
  this.connectionState = state;
  // Update UI based on state
  if (state === 'connected') {
    this.reconnectAttempts = 0;
  }
}
```

## Implementation Priority

1. **Critical (Do First)**: Fix heartbeat timer reset on message receipt
2. **High**: Fix backend heartbeat sending logic  
3. **Medium**: Improve reconnection with exponential backoff
4. **Low**: Add better connection state management

## Testing Plan

1. Test normal conversation flow with delays between messages
2. Test with 45-second gaps between user messages
3. Test network interruption scenarios
4. Test rapid message sending
5. Monitor heartbeat messages in console

## Expected Outcome

- Connection should stay alive during active conversations
- Heartbeats should be sent every 15 seconds regardless of message activity
- If connection is lost, reconnection should succeed within 1-2 attempts
- Users should never see "Disconnected" during normal usage

## Alternative Approach (Simpler)

If the above is too complex, a simpler fix would be:

1. Reduce heartbeat interval to 10 seconds
2. Increase timeout threshold to 45 seconds
3. Reset timer on ANY SSE event (not just processed messages)

This would provide more margin for error while keeping the implementation simple.

## Test-Driven Development Implementation Plan

### Phase 1: Fix Critical Heartbeat Timer Reset

#### User Story
As a user having a conversation, I want my connection to stay alive during the entire conversation so that I don't see disconnection errors while actively chatting.

#### Reason for Change
- Currently, the heartbeat timer is only reset when specific message types are processed
- Regular SSE events (like agent responses) don't reset the timer, causing false timeouts
- Users see "Disconnected - Connection timeout" even while receiving messages

#### Test Cases
```python
# tests/e2e/tests/test_sse_heartbeat_fix.py

@pytest.mark.asyncio
async def test_heartbeat_timer_resets_on_any_message():
    """Test that receiving any SSE message resets the heartbeat timer"""
    # Setup: Start conversation
    # Action: Send message, wait for response to start streaming
    # Assert: lastEventTime updates with each SSE event
    # Assert: No timeout occurs during active message streaming

@pytest.mark.asyncio
async def test_long_streaming_response_no_timeout():
    """Test that long responses don't trigger timeout"""
    # Setup: Trigger a response that takes 90+ seconds to stream
    # Assert: Connection stays alive throughout
    # Assert: No disconnection message appears
```

#### Implementation
```typescript
// frontend/lib/streaming/sse-client.ts
// Change in connect() method:
this.eventSource.onmessage = (event) => {
  // CRITICAL FIX: Reset timer on ANY message
  this.lastEventTime = Date.now();
  this.handleMessage(event);
};
```

#### Impact Analysis
- **Positive**: Prevents false timeouts during active conversations
- **Risk**: None - only changes when timer resets, not timeout logic
- **Dependencies**: None

#### Edge Cases
1. Malformed SSE events - timer still resets
2. Empty events - timer still resets
3. Binary data events - timer still resets

#### Definition of Done
- [ ] Unit test passes showing lastEventTime updates on any SSE event
- [ ] E2E test passes for long streaming responses
- [ ] Manual test: 2-minute conversation with no disconnection
- [ ] No regression in existing SSE tests

---

### Phase 2: Improve Backend Heartbeat Delivery

#### User Story
As a user taking time to think between messages, I want the system to keep my connection alive with regular heartbeats so I can continue my conversation after pauses.

#### Reason for Change
- Current implementation only sends heartbeats between agent messages
- During long agent responses, no heartbeats are sent
- Heartbeat interval (20s) is too close to timeout threshold (60s)

#### Test Cases
```python
# tests/e2e/tests/test_backend_heartbeat.py

@pytest.mark.asyncio
async def test_heartbeats_during_agent_streaming():
    """Test that heartbeats are sent even during agent message streaming"""
    # Setup: Monitor SSE events
    # Action: Trigger long agent response
    # Assert: Heartbeats received every 15 seconds during streaming

@pytest.mark.asyncio
async def test_heartbeats_during_idle_connection():
    """Test heartbeats during idle periods"""
    # Setup: Establish connection
    # Action: Wait 90 seconds without sending messages
    # Assert: At least 5 heartbeats received (one every 15s)
```

#### Implementation
```python
# backend/src/main.py
# Use asyncio task with proper merging of streams
# Ensure heartbeats are yielded even during agent streaming
```

#### Impact Analysis
- **Positive**: Consistent heartbeat delivery prevents timeouts
- **Risk**: Increased server load from more frequent heartbeats
- **Mitigation**: 15s interval balances reliability vs performance
- **Dependencies**: Requires asyncio stream merging

#### Edge Cases
1. Agent sends rapid messages - heartbeats still sent at intervals
2. Very slow agent response - heartbeats interleaved
3. Network congestion - heartbeats may queue

#### Definition of Done
- [ ] Backend sends heartbeats every 15 seconds regardless of agent activity
- [ ] E2E test confirms heartbeats during streaming
- [ ] Load test shows acceptable performance with 1000 concurrent connections
- [ ] Heartbeats don't interrupt message ordering

---

### Phase 3: Robust Reconnection Logic

#### User Story
As a user experiencing network issues, I want the application to automatically reconnect so I can continue my conversation without losing context.

#### Reason for Change
- Current reconnection creates multiple overlapping attempts
- Old EventSource connections aren't properly cleaned up
- No exponential backoff causes server flood on failures

#### Test Cases
```python
# tests/e2e/tests/test_reconnection_logic.py

@pytest.mark.asyncio
async def test_reconnection_with_backoff():
    """Test exponential backoff on reconnection attempts"""
    # Setup: Establish connection
    # Action: Simulate network failure
    # Assert: Reconnection attempts at 1s, 2s, 4s, 8s intervals
    # Assert: Max 5 attempts before giving up

@pytest.mark.asyncio
async def test_clean_reconnection_no_duplicates():
    """Test that reconnection doesn't create duplicate connections"""
    # Setup: Monitor active connections
    # Action: Force disconnect and reconnect
    # Assert: Only one active connection at a time
    # Assert: Old connection properly closed

@pytest.mark.asyncio
async def test_reconnection_preserves_session():
    """Test that reconnection maintains conversation context"""
    # Setup: Start conversation
    # Action: Force disconnect, reconnect, continue conversation
    # Assert: Conversation context maintained
```

#### Implementation
```typescript
// frontend/lib/streaming/sse-client.ts
// Add connection state management
// Implement exponential backoff
// Ensure single connection at a time
```

#### Impact Analysis
- **Positive**: Prevents connection flooding, cleaner reconnections
- **Risk**: Longer reconnection times with backoff
- **Mitigation**: Cap max backoff at 30 seconds
- **Dependencies**: May affect connection status UI

#### Edge Cases
1. User manually triggers reconnect during auto-reconnect
2. Server rejects reconnection (401/403)
3. Browser goes offline during reconnect attempt
4. Multiple tabs attempting reconnection

#### Definition of Done
- [ ] Reconnection uses exponential backoff (1s, 2s, 4s, 8s, 16s, 30s)
- [ ] Only one EventSource connection exists at a time
- [ ] E2E tests pass for all reconnection scenarios
- [ ] No memory leaks from unclosed connections
- [ ] Connection status UI accurately reflects state

---

### Phase 4: Connection State Management UI

#### User Story
As a user, I want clear visual feedback about my connection status so I know when I can send messages and when to wait.

#### Reason for Change
- Current UI shows disconnected state in development mode only
- Users need feedback during reconnection attempts
- No indication of reconnection progress

#### Test Cases
```python
# tests/e2e/tests/test_connection_ui.py

@pytest.mark.asyncio
async def test_connection_states_displayed():
    """Test all connection states are properly displayed"""
    # Assert: "Connecting..." shown on initial load
    # Assert: "Connected" (or no indicator) when active
    # Assert: "Reconnecting... (attempt 2/5)" during reconnection
    # Assert: "Disconnected" only after all attempts fail

@pytest.mark.asyncio
async def test_ui_disabled_during_disconnection():
    """Test that UI prevents actions when disconnected"""
    # Setup: Force disconnection
    # Assert: Submit button disabled
    # Assert: Text input shows visual indication
    # Assert: Clear message about connection issue
```

#### Implementation
- Add connection state indicator component
- Update form UI based on connection state
- Show reconnection progress

#### Impact Analysis
- **Positive**: Better user experience and clarity
- **Risk**: UI changes may affect layout
- **Dependencies**: Requires connection state from SSE client

#### Edge Cases
1. Rapid connection state changes
2. Multiple status updates in quick succession
3. Browser in background tab

#### Definition of Done
- [ ] Connection states visible in production mode
- [ ] Form UI reflects connection state
- [ ] Smooth transitions between states
- [ ] Accessible status announcements for screen readers
- [ ] E2E tests cover all state transitions

---

## Overall Success Criteria

1. **Zero false disconnections** during active conversations
2. **Successful reconnection** within 30 seconds of network recovery
3. **No duplicate connections** or memory leaks
4. **Clear user feedback** at all connection states
5. **All existing tests pass** (no regressions)
6. **New E2E tests** provide comprehensive coverage

## Rollout Strategy

1. **Phase 1**: Deploy immediately (critical fix)
2. **Phase 2**: Deploy after Phase 1 validation (1-2 days)
3. **Phase 3**: Deploy after load testing (3-4 days)
4. **Phase 4**: Deploy with next UI update cycle (1 week)

## Monitoring

- Track disconnection events in production
- Monitor heartbeat delivery rates
- Alert on reconnection failure rates > 5%
- User feedback on connection stability