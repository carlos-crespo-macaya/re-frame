#!/bin/bash

echo "Testing SSE connection to backend..."
echo "Creating a new session..."

# Test SSE connection
curl -N http://localhost:8000/sse/connect &
SSE_PID=$!

# Wait a moment for connection
sleep 2

# Kill the SSE connection
kill $SSE_PID 2>/dev/null

echo "SSE connection test completed"