#!/bin/bash

echo "Testing API alignment flow..."

# Generate a session ID
SESSION_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
echo "Session ID: $SESSION_ID"

# 1. Connect to SSE endpoint
echo -e "\n1. Connecting to SSE endpoint..."
curl -N "http://localhost:8000/api/events/$SESSION_ID?language=en-US" &
SSE_PID=$!

# Wait for connection
sleep 2

# 2. Send a test message
echo -e "\n2. Sending test message..."
curl -X POST "http://localhost:8000/api/send/$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "thought",
    "data": "I am afraid people will judge me",
    "mime_type": "text/plain",
    "session_id": "'$SESSION_ID'",
    "turn_complete": true
  }'

# Wait for response
sleep 5

# Kill SSE connection
kill $SSE_PID 2>/dev/null

echo -e "\nTest completed!"