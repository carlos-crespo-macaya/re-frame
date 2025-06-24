# Re-frame ADK Agent

A cognitive reframing assistant built with Google's Agent Development Kit (ADK) that helps users examine and reframe negative thoughts using Cognitive Behavioral Therapy (CBT) techniques.

## Overview

This agent implements a three-stage pipeline:

1. **Intake Conversation**: Collects information about the user's situation, automatic thoughts, and emotions
2. **Reframe Analysis**: Applies CBT techniques to identify cognitive distortions and create balanced perspectives
3. **Report Generation**: Creates a PDF summary of the session

## Project Structure

```
adk/
├── README.md
├── requirements.txt
├── .env.example
├── reframe_agent/
│   ├── __init__.py
│   ├── agent.py         # Main agent definitions
│   ├── models.py        # Pydantic models
│   ├── tools.py         # Tool implementations
│   └── prompts/         # Agent instruction prompts
│       ├── intake_agent.md
│       ├── reframe_agent.md
│       └── synthesis_agent.md
└── tests/
    └── test_agent.py
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

3. **Run the ADK web interface**:
   ```bash
   # From the adk directory
   adk web
   ```

4. **Select the agent**:
   - Open http://localhost:8000 in your browser
   - Select "reframe_agent" from the dropdown

## Agent Workflow

### 1. Intake Stage
The agent engages in a compassionate conversation to collect:
- **Trigger Situation**: What happened that triggered the negative thoughts
- **Automatic Thought**: The specific negative thought
- **Emotion Data**: How the person feels and the intensity (0-10)

### 2. Reframe Stage
The agent analyzes the collected data and:
- Identifies cognitive distortions (e.g., catastrophizing, black-and-white thinking)
- Explores evidence for and against the negative thought
- Creates a balanced perspective
- Suggests a small, actionable step

### 3. Report Stage
The agent generates a PDF report containing:
- Session summary
- Identified cognitive distortions
- Balanced perspective
- Recommended action
- Belief ratings (before and after reframing)

## Features

- **Structured Conversations**: Uses Pydantic models to ensure consistent data collection
- **Crisis Detection**: Automatically detects and escalates crisis situations
- **Loop Control**: Limits conversation to 5 iterations to prevent endless loops
- **PDF Generation**: Creates downloadable session summaries
- **Privacy-First**: No personal data is stored permanently

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Tools
1. Define the tool function in `tools.py`
2. Add the tool to the appropriate agent in `agent.py`
3. Update the agent's instruction prompt if needed

### Modifying Prompts
Edit the markdown files in `reframe_agent/prompts/` to change agent behavior.

## Deployment

This agent is designed to be integrated with the larger re-frame.social platform:
- The backend API will invoke this agent via the ADK Runner
- Session data is ephemeral and not persisted
- PDF reports can be downloaded by users

## License

Part of the re-frame.social project.