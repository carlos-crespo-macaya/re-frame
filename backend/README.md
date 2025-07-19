# reframe-agents

A Cognitive Reframing Assistant that helps individuals recognize, challenge, and reframe unhelpful thoughts through a conversational experience grounded in Cognitive Behavioural Therapy (CBT).

## Overview

This project implements a multi-agent conversational system using Google's Agent Development Kit (ADK) to guide users through the CBT process of identifying and reframing cognitive distortions. The assistant provides a safe, evidence-based approach to thought examination without replacing professional therapy.

## Key Features

- **Four-phase conversation flow**: Greeting  →  Discovery  →  Reframing  →  Summary
- **Evidence-based CBT techniques**: Grounded in established cognitive distortion taxonomy
- **Multi-language support**: Auto-detects language and conducts entire dialogue in user's language
- **Safety first**: Crisis detection with appropriate escalation paths
- **Privacy-focused**: Minimal PII collection with strict data retention policies
- **PDF summaries**: Generates downloadable session summaries with insights and action steps

## Project Status

The project is in early development stages. See our [GitHub Issues](https://github.com/macayaven/reframe-agents/issues) for detailed implementation phases and progress tracking.

### Currently Implemented
- Web crawler for documentation gathering
- CBT domain knowledge modules (`src/knowledge/cbt_context.py`)
- CBT knowledge query tool (`src/tools/cbt_knowledge_tool.py`)
- Simplified prompt templates for all conversation phases
- Project configuration with uv package manager
- Basic CBT Assistant agent with Gemini integration
- FastAPI application with SSE streaming (`src/main.py`)

### In Progress
See [Phase 1: Basic ADK Infrastructure](https://github.com/macayaven/reframe-agents/issues/2) and subsequent phases in our issue tracker.

## Getting Started

### Prerequisites
- Python 3.12+
- uv package manager
- Google API key for Gemini (get one at https://aistudio.google.com/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/macayaven/reframe-agents.git
cd reframe-agents

# Install all dependencies including dev tools
uv sync --all-extras

# Set up pre-commit hooks
uv run pre-commit install

# Copy the environment file and add your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running the Assistant

```bash
# Set your API key (or add to .env file)
export GOOGLE_API_KEY="your-api-key-here"

# Option 1: Run with ADK Web UI (recommended for development)
cd src/agents
adk web

# Option 2: Run with ADK CLI
cd src/agents
adk run

# Option 3: Run as API server
cd src/agents
adk api_server

# Option 4: Run API server locally
uv run python -m uvicorn src.main:app --reload
```

### Development Commands

All quality checks are managed through poethepoet (poe):

```bash
# Run all checks (format, lint, type, test)
uv run poe check

# Auto-fix formatting and linting issues
uv run poe fix

# Individual commands
uv run poe format        # Format with black and isort
uv run poe lint          # Check with ruff
uv run poe typecheck     # Type check with mypy
uv run poe test          # Run tests with pytest
uv run poe test-cov      # Generate HTML coverage report
```

## Architecture

### Conversation Phases

1. **Greeting**: Introduction, language detection, and initial rapport building
2. **Discovery**: Gathering details about thoughts, emotions, and situations
3. **Reframing**: Identifying cognitive distortions and creating balanced alternatives
4. **Summary**: Generating insights, action steps, and PDF summary

### Key Components

- **Conversational Agents**: ADK-based agents for each conversation phase
- **CBT Knowledge Base**: Centralized domain knowledge and distortion taxonomy
- **Session Store**: User message and context storage throughout conversation
- **PDF Generator**: Professional summary document creation
- **Safety Module**: Crisis detection and intervention system

### Technology Stack

- **Framework**: Google Agent Development Kit (ADK)
- **Language**: Python 3.12+
- **Package Manager**: uv
- **Testing**: pytest with 80% coverage requirement
- **Code Quality**: black, isort, ruff, mypy
- **Documentation**: ADK docs available in `docs/adk-docs/`

## Project Management

**GitHub Issues are the single source of truth for project management.**

All progress and status updates are tracked in [GitHub Issues](https://github.com/macayaven/reframe-agents/issues). We follow a phased implementation approach with Test-Driven Development (TDD):

- Phase 0-10: Core functionality implementation
- Each phase includes user stories, test cases, and clear acceptance criteria
- Reference issue numbers in commits (e.g., "Implement greeting agent #5")

## Contributing

1. Check the [GitHub Issues](https://github.com/macayaven/reframe-agents/issues) for current tasks
2. Follow the code quality standards (run `uv run poe check` before committing)
3. Write tests for new functionality
4. Update issue status and add comments for important decisions
5. Reference issue numbers in your commits

## Design Philosophy

1. **Keep it simple**: Question any complexity. If there's a simpler way, discuss it first.
2. **Evidence-based**: All CBT techniques must be grounded in established research.
3. **User safety**: Crisis detection and appropriate escalation are non-negotiable.
4. **Privacy first**: Minimize data collection and enforce retention policies.
5. **Test-driven**: Write tests before implementation.

## License

[To be determined]

## Acknowledgments

- Built with Google's Agent Development Kit (ADK)
- CBT principles based on established cognitive behavioral therapy research
- Safety protocols informed by crisis intervention best practices

---

For Claude Code specific guidelines, see [CLAUDE.md](CLAUDE.md).
