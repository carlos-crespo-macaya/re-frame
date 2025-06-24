#!/bin/bash

# Create a named pipe for communication
mkfifo /tmp/adk_input

# Start the agent in background, reading from the pipe
(source /Users/carlos/workspace/re-frame/backend/.venv/bin/activate && adk run reframe_agent < /tmp/adk_input) &
ADK_PID=$!

# Give it time to start
sleep 3

# Send first message
echo "I feel stupid after that meeting" > /tmp/adk_input
sleep 5

# Send second message (if agent asks about situation)
echo "It was in a teams public channel" > /tmp/adk_input
sleep 5

# Send third message (if agent asks about thought)
echo "Everyone thinks I'm an asshole" > /tmp/adk_input
sleep 5

# Send fourth message (if agent asks about emotion)
echo "shame, 9 out of 10" > /tmp/adk_input
sleep 10

# Clean up
kill $ADK_PID 2>/dev/null
rm -f /tmp/adk_input