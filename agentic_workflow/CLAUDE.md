# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL: Implementation Guide

**THIS PROJECT MUST FOLLOW THE MINIMAL POC SPECIFICATION**

The ONLY valid specification is: `/Users/carlos/workspace/re-frame/agentic-workflow/docs/MINIMAL_POC_SPECIFICATION.md`

**MANDATORY REQUIREMENTS**:
1. **ONLY 3 agents**: intake-agent-adk-instructions, reframe-agent-adk-instructions, synthesis-agent-adk-instructions
2. **EXACT env vars**: Use SUPABASE_REFRAME_DB_CONNECTION_STRING (NOT SUPABASE_CONNECTION_STRING)
3. **Langfuse tracing**: ALL operations must be traced - see verify_langfuse_tracing.py
4. **Test files**: Use verify_connections.py and verify_langfuse_tracing.py as implementation references

**IGNORE**:
- All other architecture documents
- Any mentions of framework agents (CBT, DBT, ACT, Stoicism)
- Complex orchestration patterns
- Features not in the POC specification

The POC specification is the SINGLE SOURCE OF TRUTH for:
- Agent architecture (only 3 agents: intake, reframe, synthesis)
- Prompt names (exact names verified to exist in Langfuse)
- Data models (only IntakeData, ReframeAnalysis, SessionState)
- Workflow (sequential, no complex orchestration)
- Features (no multi-framework analysis, no complex tools)

## Project Overview

This is the **agentic-workflow** component of re-frame.social, containing the multi-agent AI system for cognitive reframing support. It implements a therapeutic agent system using Google ADK (AI Developer Kit) to help users with Avoidant Personality Disorder (AvPD) through CBT-based cognitive reframing techniques.

## Architecture (Per POC Specification)

### Three-Agent System ONLY
1. **Intake Agent** (info_collector_reframe_agent): Gathers trigger, thought, emotion
2. **Reframe Agent** (reframe_agent): CBT analysis + conversational support
3. **PDF Agent** (pdf_summariser_agent): Creates anonymized takeaway

### Implementation Rules
- Use ADK SequentialAgent (NOT LoopAgent or complex orchestration)
- Use DatabaseSessionService with Supabase (NOT InMemorySessionService)
- Load prompts from Langfuse (NOT local files)
- Simple models only: IntakeData, ReframeAnalysis, SessionState

## Development Commands

### IMPORTANT: Package Management & Python Execution
**ALWAYS use `uv` for Python package management AND running Python scripts** - never use pip or python directly.

**CRITICAL**: All Python commands must be run through `uv run`:
- ❌ NEVER: `python script.py`
- ✅ ALWAYS: `uv run python script.py`

### Environment Setup
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies with development extras
uv pip install -e ".[dev]"

# Install specific packages
uv pip install langfuse psycopg2-binary sqlalchemy

# Never use pip directly - always use uv pip
```

### Running Python Scripts
```bash
# ALWAYS use uv run for ANY Python execution
uv run python agent.py

# Run with specific configuration
GOOGLE_API_KEY=your-key uv run python agent.py

# Run any Python script
uv run python script_name.py

# Run pytest
uv run pytest tests/
```

### Testing & Quality
```bash
# Run all tests
poe test

# Run with coverage
poe test-cov

# Run specific test file
uv run pytest tests/test_agent.py::test_name

# Code quality checks
poe lint          # Run ruff linter
poe format        # Format with black
poe type-check    # Run mypy
poe check         # Run all checks (lint + format + type-check + tests)
```

### Utilities
```bash
# Clean generated files
poe clean

# Install/sync dependencies
poe install       # Install in editable mode
poe sync          # Sync from requirements.txt
```

## Key Technical Details

### Agent Configuration
- Uses Gemini 2.0 Flash model by default
- Retrieves prompts from Langfuse prompt management
- Implements session state management via Supabase
- OpenTelemetry integration for observability

### Safety Features
- Crisis detection with emergency hotline routing
- Emotion intensity monitoring (escalates if >2 point jump)
- Maximum 4 user turns for intake to prevent overwhelm
- Anonymization in PDF reports (replaces names with "Client")

### PD-Specific Design Principles
1. **Validation First**: Always acknowledge user's experience before questions
2. **User Control**: All questions optional, user owns the process
3. **Micro-Actions**: ≤10 minute tasks to avoid perfectionism triggers
4. **Concrete Progress**: Confidence ratings before/after for tangible proof

## Integration with Main Project

This component integrates with the broader re-frame system:
- **Backend API** (../backend/): Handles user management, auth, rate limiting
- **Frontend** (../frontend/): React UI for user interaction
- **Infrastructure** (../infrastructure/): GCP deployment configuration

### Environment Variables Required
```bash
GOOGLE_API_KEY              # Google AI Studio API key
SUPABASE_REFRAME_DB_CONNECTION_STRING  # For session state management
LANGFUSE_HOST              # Prompt management host
LANGFUSE_PUBLIC_KEY        # Langfuse authentication
LANGFUSE_SECRET_KEY        # Langfuse authentication
```

## Agent Prompt Management

Agent prompts are versioned in `docs/poc/agents/prompts/`:
- **v1/**: Initial prompt versions
- **v2-deep-research/**: Enhanced prompts with deeper therapeutic knowledge

Prompts are loaded from Langfuse in production but can be overridden locally.

## Therapeutic Approach

**ONLY CBT as specified in the POC**:
- Identify 1-2 cognitive distortions
- Evidence for/against
- Balanced thought (≤40 words)
- Micro-action (≤10 minutes)
- Confidence ratings

**NO** multiple frameworks, **NO** DBT/ACT/Stoicism agents.

## Development Workflow

1. **Feature Development**:
   - Create feature branch: `feature/AG-XXX-description`
   - Write tests first (TDD mandatory)
   - Implement agent logic
   - Ensure prompts align with therapeutic guidelines

2. **Testing Agents**:
   - Unit test individual agents
   - Integration test full conversation flow
   - Validate safety features trigger appropriately
   - Check PDF generation and anonymization

3. **Prompt Engineering**:
   - Test prompts with diverse inputs
   - Validate therapeutic accuracy
   - Ensure PD-sensitive language
   - Check crisis detection reliability

## Important Constraints

- **Budget**: Optimize for Gemini 1.5 Flash usage (cheapest model)
- **Safety**: Crisis detection must be 100% reliable
- **Privacy**: No PII storage, full anonymization in outputs
- **Therapeutic Integrity**: Align with evidence-based practices
- **User Trust**: Transparent reasoning, collaborative approach

## Common Development Tasks

### DO NOT Add New Agents
The POC specifies ONLY 3 agents. No framework agents, no additional agents.

### Modifying Agent Behavior
1. Update prompt in Langfuse (production) 
2. Test with edge cases (crisis, high emotion, refusal)
3. Ensure it matches POC specification
4. Update tests to cover new behavior

### Debugging
1. Check Langfuse traces for conversation flow
2. Review Supabase session state
3. Verify against POC specification
4. Use logging for agent decisions

## Implementation Checklist

Before ANY code changes:
- [ ] Have I read `/docs/MINIMAL_POC_SPECIFICATION.md`?
- [ ] Does this change align with the 3-agent POC?
- [ ] Am I adding unnecessary complexity?
- [ ] Am I using the specified tools (Langfuse, Supabase)?
- [ ] Will this pass code quality checks (ruff, black, mypy)?