# Re-frame POC - Cognitive Reframing Assistant

## Overview

This is the Proof of Concept (POC) implementation for re-frame - a cognitive reframing support tool for people with Avoidant Personality Disorder (AvPD). It implements a streamlined 3-agent system using Google ADK (AI Developer Kit) and Gemini 2.0 Flash Lite.

## Quick Start

### Prerequisites
- Python 3.12+
- Google AI API key
- Langfuse account (for prompt management)
- Supabase account (for session storage)

### Installation

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
cd agentic_workflow
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Running the Application

### CLI Interface
```bash
# Run the CLI interface
uv run python scripts/run_cli.py
```

### Web Interface (ADK)
```bash
# Start the ADK web interface
adk run
# Open http://localhost:5173 in your browser
```

### Verification Scripts
```bash
# Test all connections
uv run python scripts/verify_connections.py

# Test Langfuse tracing
uv run python scripts/verify_langfuse_tracing.py

# Test implementation against POC spec
uv run python scripts/verify_implementation.py
```

## Architecture

### 3-Agent System

1. **Intake Agent** - Empathetically gathers user information
   - Collects: trigger situation, automatic thought, emotion data
   - Maximum 4 conversation turns
   - Crisis detection and safety features

2. **Reframe Agent** - Applies CBT techniques
   - Identifies cognitive distortions
   - Provides evidence-based reframing
   - Offers micro-actions (≤10 minutes)

3. **PDF Agent** - Creates anonymized summaries
   - Generates takeaway document
   - Removes identifying information
   - Provides action plan

### Technology Stack

- **LLM**: Google Gemini 2.0 Flash Lite (cost-optimized)
- **Framework**: Google ADK for agent orchestration
- **Prompt Management**: Langfuse (cached locally)
- **Session Storage**: Supabase
- **Tracing**: Arize (ADK-integrated)

## Development

### Project Structure
```
agentic_workflow/
├── agents/              # Agent implementations
├── config/              # Settings and configuration
├── models.py           # Data models
├── orchestrator.py     # Main workflow orchestration
├── utils/              # Utilities (cache, prompts)
└── tests/              # Test files
```

### Running Tests
```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov

# Type checking
uv run python -m mypy .

# Linting
uv run ruff check .
```

### Verification Scripts
```bash
# Verify all connections (Google AI, Langfuse, Supabase)
uv run python verify_connections.py

# Verify agent implementations
uv run python verify_implementation.py

# Verify Langfuse tracing
uv run python verify_langfuse_tracing.py
```

### Environment Variables
Create a `.env` file with:
```env
# Google AI
GOOGLE_API_KEY=your_key_here

# Langfuse (prompt management)
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key

# Supabase (session storage)
SUPABASE_REFRAME_DB_CONNECTION_STRING=your_connection_string

# Arize (tracing)
ARIZE_SPACE_ID=your_space_id
ARIZE_API_KEY=your_api_key
```

## Cost Optimization

The system is optimized for minimal API costs:
- Uses Gemini 2.0 Flash Lite (cheapest Google model)
- Prompts cached locally after first download
- Token limits: 1024 global, 300 for intake agent
- Response caching utility available

## Safety Features

- Crisis keyword detection with hotline information (024 Spain)
- Emotion escalation monitoring
- Maximum conversation limits
- Immediate flow interruption on crisis detection

## API Integration

This POC is designed to integrate with the main re-frame backend API. The workflow can be exposed through FastAPI endpoints defined in the parent backend directory.

## Important Notes

- This is a POC implementation - not production-ready
- Designed for $300 GCP credit budget constraint
- Privacy-first: No PII storage, ephemeral sessions
- Target: 25 unique users for alpha testing

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're using the virtual environment
2. **Langfuse Connection**: Check credentials and network
3. **Type Errors**: Run `uv run python -m mypy .` to identify issues

### Support

For issues, check the main project documentation or create an issue in the GitHub repository.