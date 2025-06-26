# Documentation Overview

This directory contains the essential documentation for the re-frame POC implementation.

## Key Documents

- **MINIMAL_POC_SPECIFICATION.md** - The authoritative specification for the 3-agent POC
- **PROJECT_STRUCTURE.md** - Current codebase organization
- **SESSION_FLOW_DIAGRAM.md** - User interaction flow through the agents

## Prompts

Agent prompts are stored in `poc/agents/prompts/current/`. These are the exact prompts used by:
- Intake Agent
- Reframe Agent  
- PDF Summarizer Agent

## Architecture Notes

This POC implements a simplified version of the full re-frame vision:
- 3 agents only (not the full multi-framework system)
- Minimal viable features for alpha testing
- Focus on core CBT reframing functionality

For implementation details, see the main README.md in the parent directory.