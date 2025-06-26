# Migration Guide: Multilingual 3-Agent System

## Overview

This guide helps migrate from the current mixed implementation to the clean multilingual 3-agent system.

## New File Structure

```
agentic_workflow/
├── reframe/
│   ├── agents/
│   │   ├── multilingual_intake_agent.py    # NEW: Agent 1
│   │   ├── multilingual_analysis_agent.py  # NEW: Agent 2
│   │   ├── multilingual_pdf_agent.py       # NEW: Agent 3
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── language_detector.py       # NEW: Language detection
│   │   └── callbacks/
│   │       ├── __init__.py
│   │       └── language_callback.py       # NEW: ADK callback
│   ├── orchestrators/
│   │   ├── __init__.py
│   │   └── multilingual_orchestrator.py   # NEW: Main orchestrator
│   └── core/
│       └── multilingual_models.py          # NEW: Data models
├── run_multilingual_adk.py                 # NEW: ADK runner
└── tests/
    └── test_multilingual_system.py         # NEW: Tests
```

## Files to Remove After Validation

### Agent Files (Remove ALL):
- `reframe/agents/maya_agent.py`
- `reframe/agents/maya_conversational_agent.py`
- `reframe/agents/intake_agent.py`
- `reframe/agents/reframe_agent.py`
- `reframe/agents/pdf_agent.py`
- `reframe/agents/conversational_intake_agent.py`
- `reframe/agents/conversational_reframe_agent.py`
- `reframe/agents/conversational_pdf_agent.py`
- All other agent variants

### Orchestrator Files (Remove):
- `reframe/core/orchestrator.py`
- `reframe/core/conversational_orchestrator.py`

### Other Files (Remove):
- `run_adk.py` (replaced by `run_multilingual_adk.py`)
- `adk_agent.py`
- `agent.py`
- `test_agent.py`
- `test_unified_agent.py`

## Update Required Files

### 1. Update `reframe/__init__.py`
```python
"""Re-frame multilingual cognitive reframing assistant."""

from reframe.orchestrators import MultilingualReframeOrchestrator

# For ADK compatibility
orchestrator = MultilingualReframeOrchestrator()
root_agent = orchestrator.pipeline

__all__ = ["MultilingualReframeOrchestrator", "root_agent"]
```

### 2. Update `reframe/agents/__init__.py`
```python
"""Multilingual agents for cognitive reframing."""

from .multilingual_intake_agent import MultilingualIntakeAgent
from .multilingual_analysis_agent import MultilingualAnalysisAgent
from .multilingual_pdf_agent import MultilingualPDFAgent

__all__ = [
    "MultilingualIntakeAgent",
    "MultilingualAnalysisAgent",
    "MultilingualPDFAgent",
]
```

### 3. Update `reframe/core/__init__.py`
```python
"""Core business logic for re-frame."""

from .multilingual_models import (
    ConversationPhase,
    ConversationTurn,
    IntakeData,
    AnalysisData,
    MultilingualSessionState,
)

__all__ = [
    "ConversationPhase",
    "ConversationTurn", 
    "IntakeData",
    "AnalysisData",
    "MultilingualSessionState",
]
```

## Environment Variables

No new environment variables needed. Uses existing:
- `GOOGLE_API_KEY`
- `LANGFUSE_HOST`
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`
- `SUPABASE_REFRAME_DB_CONNECTION_STRING` (optional)
- `ARIZE_SPACE_ID` (optional)
- `ARIZE_API_KEY` (optional)

For Google Cloud Translation API:
- `GOOGLE_APPLICATION_CREDENTIALS` (optional, uses API key if not set)

## Testing Migration

### 1. Test Environment
```bash
cd /Users/carlos/workspace/re-frame/agentic_workflow
python tests/test_multilingual_system.py
```

### 2. Test ADK Runner
```bash
python run_multilingual_adk.py
```

### 3. Start Web Interface
```bash
adk web
```

### 4. Test Languages
- Spanish: "Hola, tengo mucha ansiedad"
- English: "Hello, I'm feeling anxious"
- French: "Bonjour, je suis anxieux"
- Use `/exit` or `/salir` during analysis

## Validation Checklist

- [ ] All tests pass
- [ ] ADK web interface loads
- [ ] Language detection works
- [ ] Conversation flows through 3 agents
- [ ] Exit commands work
- [ ] PDF generates in correct language
- [ ] Session persistence works (if Supabase configured)
- [ ] Observability works (Langfuse/Arize)

## Rollback Plan

If issues occur:
1. Keep backup of old files
2. Restore from git if needed
3. The new system is completely separate until old files are removed

## Key Differences from Old System

1. **Clean 3-agent architecture** (not all-in-one Maya)
2. **Proper language detection** via Google Cloud API with fallback
3. **Extended conversation support** with `/exit` command
4. **Session state management** across agents
5. **Full observability** with Langfuse + Arize
6. **ADK best practices** throughout

## Support

Check logs for issues:
- Language detection: Look for "Language detected:" messages
- Agent transitions: Look for "Transitioning from X to Y"
- Session management: Check Supabase connection logs
- Observability: Check Langfuse/Arize dashboards