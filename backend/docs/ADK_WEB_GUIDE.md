# ADK Web Interface Guide

## Overview

The ADK web interface provides a development UI for testing and debugging the re-frame multi-agent system. It allows you to:

- Interact with agents through a chat interface
- Visualize agent traces and execution flow
- Inspect function calls and responses
- Test individual agents or the full workflow

## Setup

### Prerequisites

1. Install Google ADK:
```bash
pip install google-generativeai-adk
```

2. Set your Google AI API key:
```bash
export GOOGLE_AI_API_KEY='your-api-key-here'
```

### Running ADK Web

1. Navigate to the backend directory:
```bash
cd backend/
```

2. Run the ADK web launcher:
```bash
python run_adk_web.py
```

Or directly with ADK:
```bash
adk web
```

3. Open your browser to http://localhost:8000

## Using the Interface

### Agent Selection

The dropdown menu shows available agents:
- **ReFrameAssistant**: Main agent for complete reframing workflow
- **IntakeAgent**: Test input validation and extraction
- **CBTAgent**: Test CBT technique application  
- **SynthesisAgent**: Test response synthesis

### Features

1. **Chat Interface**
   - Type thoughts/situations in the input box
   - View agent responses with transparency data
   - See techniques applied and reasoning

2. **Trace Viewer**
   - Click "Show Traces" to see execution details
   - View timing and latency information
   - Inspect individual function calls

3. **Voice Input**
   - Click microphone icon for voice input
   - Useful for testing natural language variations

## Testing Workflows

### Complete Reframing Flow
Select "ReFrameAssistant" and enter:
```
I'm afraid to join the team lunch because I think everyone will judge me
```

### Individual Agent Testing

**Intake Agent**:
```json
{
  "user_thought": "I feel anxious about the presentation"
}
```

**CBT Agent** (requires intake output):
```json
{
  "is_valid": true,
  "extracted_elements": {
    "situation": "Upcoming presentation",
    "thoughts": ["I'll mess up"],
    "emotions": ["Anxiety"],
    "behaviors": ["Avoiding preparation"]
  }
}
```

## Debugging Tips

1. **Check Logs**: The terminal shows detailed logs
2. **Trace Errors**: Use trace viewer to identify failures
3. **Test Edge Cases**: Try various input lengths and formats
4. **Monitor Latency**: Watch for slow operations

## Common Issues

### "No agents found"
- Ensure you're in the backend directory
- Check that agents are properly registered in `adk_registry.py`

### "API Key Error"
- Verify GOOGLE_AI_API_KEY is set
- Check key permissions for Gemini API

### Windows Issues
- Use `adk web --no-reload` to avoid subprocess errors

## Development Workflow

1. Make changes to agent code
2. Restart ADK web to reload agents
3. Test changes through the interface
4. Use traces to debug issues
5. Iterate based on results