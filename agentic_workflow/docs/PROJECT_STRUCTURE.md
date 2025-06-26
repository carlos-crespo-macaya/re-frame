# Agentic Workflow Project Structure

This directory has been cleaned up and now contains only the essential files for the re-frame multi-agent system.

## Directory Overview

```
agentic-workflow/
├── Core Entry Points
│   ├── agent.py           # Simple entry point for the multi-agent system
│   ├── main.py            # Advanced entry with interactive/batch demos
│   └── orchestrator.py    # Central orchestration for the multi-agent workflow
│
├── Data Models
│   └── models.py          # Pydantic models for conversation state
│
├── Agent Implementations
│   └── agents/
│       ├── base.py        # Base classes (LoopReframeAgent, SequentialReframeAgent)
│       ├── intake_agent.py    # Trauma-informed intake agent
│       ├── cbt_agent.py       # Cognitive Behavioral Therapy agent
│       ├── dbt_agent.py       # Dialectical Behavior Therapy agent
│       ├── act_agent.py       # Acceptance and Commitment Therapy agent
│       ├── stoic_agent.py     # Stoicism framework agent
│       └── synthesis_agent.py # Synthesizes outputs from all frameworks
│
├── Configuration
│   └── config/
│       ├── settings.py    # Environment configuration with Pydantic
│       └── gemini.py      # Gemini model configuration
│
├── Utilities
│   └── utils/
│       ├── event_manager.py  # Event bus and routing system
│       ├── monitoring.py     # Performance monitoring
│       └── state_manager.py  # Session state management
│
├── Documentation
│   └── docs/
│       ├── Architecture documents (ADK implementation, optimal design)
│       ├── final-picture/   # Master plans and TDD implementation
│       └── poc/            # Agent prompts (v1 and v2-deep-research)
│
└── Project Files
    ├── pyproject.toml     # Project dependencies and configuration
    ├── uv.lock           # Locked dependencies
    ├── README.md         # Project documentation
    └── CLAUDE.md         # Instructions for Claude Code

```

## Key Components

### 1. **Multi-Agent Architecture**
- **Orchestrator** (`orchestrator.py`): Manages the entire workflow
- **Base Agent Classes** (`agents/base.py`): Provides LoopAgent and SequentialAgent patterns
- **Framework Agents**: Each implements a specific therapeutic approach

### 2. **Event-Driven Communication**
- **EventBus**: Central message passing system
- **EventRouter**: Routes events based on rules
- **AgentEvent**: Standardized event format

### 3. **State Management**
- **UnifiedSessionState**: Tracks the entire pipeline state
- **StateManager**: Persists state to Supabase
- **ConversationState**: Individual agent state

### 4. **Monitoring & Observability**
- **Langfuse Integration**: Configured via environment variables
- **OpenTelemetry**: For distributed tracing
- **AgentMonitor**: Performance tracking

## Running the System

```bash
# Interactive mode
python agent.py

# Process a single message
python agent.py "I made a mistake and feel terrible"

# Run demos
python main.py interactive
python main.py batch
```

## Environment Variables Required

```bash
GOOGLE_API_KEY              # For Gemini model
LANGFUSE_HOST              # Langfuse tracing
LANGFUSE_PUBLIC_KEY        # Langfuse auth
LANGFUSE_SECRET_KEY        # Langfuse auth
SUPABASE_CONNECTION_STRING # Session persistence
```

## Clean Architecture Benefits

1. **Clear Separation of Concerns**: Each component has a single responsibility
2. **Easy to Navigate**: Logical grouping of related files
3. **Extensible**: Easy to add new framework agents
4. **Testable**: Clean interfaces for unit testing
5. **Maintainable**: No obsolete code or test scripts cluttering the structure