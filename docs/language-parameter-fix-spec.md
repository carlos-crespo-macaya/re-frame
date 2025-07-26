# Language Parameter Fix Specification

## Executive Summary

Currently, the language parameter is not being properly utilized in text mode conversations. While voice mode correctly uses the specified language for TTS/STT services, text mode ignores the language parameter passed during SSE connection and instead relies on post-hoc language detection from user input. This leads to inconsistent behavior where the UI language selector doesn't affect text conversations.

## Problem Statement

### Current Behavior
1. User selects a language in the UI (e.g., Spanish)
2. Frontend passes language parameter to `/api/events/{session_id}?language=es-ES`
3. Backend stores language in session metadata but doesn't use it
4. Agent responds in English until it detects Spanish from user input
5. Language detection happens reactively, not proactively

### Expected Behavior
1. User selects a language in the UI
2. Frontend passes language parameter to backend
3. Backend configures all agents to respond in the selected language
4. First greeting and all subsequent responses are in the selected language
5. System respects user's language preference from the start

## Technical Analysis

### Root Cause
The language parameter flow breaks at the agent initialization level:
- `create_cbt_assistant()` accepts `language_code` parameter
- However, this only affects the initial agent creation
- Subsequent agent phases don't receive or use the language context
- The greeting agent relies on `detect_language()` instead of session language

### Affected Components
1. **Backend**
   - `/src/text/router.py` - SSE endpoint stores but doesn't propagate language
   - `/src/agents/greeting_agent.py` - Uses detection instead of session language
   - `/src/agents/phase_manager.py` - Doesn't pass language between phases
   - All phase agents - Don't receive language context

2. **Frontend**
   - Already correctly passes language parameter
   - No changes needed

## Solution Overview

### High-Level Approach
1. Propagate language from session metadata to all agent phases
2. Modify each agent to accept and respect language parameter
3. Update agent instructions to generate responses in specified language
4. Maintain language detection as fallback for edge cases
5. Ensure language consistency across entire conversation

### Key Principles
- **Explicit over Implicit**: Use provided language parameter instead of detection
- **Consistency**: All phases should use the same language
- **Fallback Safety**: Keep detection for cases where language isn't specified
- **Non-Breaking**: Maintain backward compatibility

## Functional Requirements

### FR1: Language Propagation
- The system SHALL use the language parameter provided during SSE connection
- The system SHALL pass language context to all agent phases
- The system SHALL maintain language consistency throughout the session

### FR2: Agent Language Support
- Each agent SHALL accept a language parameter
- Agents SHALL generate all responses in the specified language
- Agents SHALL include language-specific prompts in their instructions

### FR3: Greeting Behavior
- The greeting agent SHALL use session language, not detection
- The initial greeting SHALL be in the user's selected language
- The greeting SHALL include language-appropriate welcome messages

### FR4: Language Persistence
- The system SHALL store language preference in session metadata
- The system SHALL use stored language for all subsequent interactions
- The system SHALL maintain language even across reconnections

## Non-Functional Requirements

### NFR1: Performance
- Language parameter usage SHALL NOT increase response latency
- Language context SHALL be lightweight (just a string parameter)

### NFR2: Compatibility
- Changes SHALL be backward compatible
- Missing language parameter SHALL default to "en-US"
- Existing sessions SHALL continue to work

### NFR3: Maintainability
- Language handling SHALL be centralized and consistent
- Language configuration SHALL be easily testable
- Code changes SHALL follow existing patterns

## Success Criteria

1. **Immediate Language Response**: First greeting is in selected language
2. **Consistency**: All responses maintain the selected language
3. **No Detection Delay**: No waiting for user input to determine language
4. **UI Synchronization**: Language selector immediately affects conversation
5. **Test Coverage**: All language flows have comprehensive tests

## Out of Scope

- Changing the language detection algorithm
- Adding new language support
- Modifying voice mode language handling
- Frontend UI changes
- Real-time language switching mid-conversation

## Risks and Mitigations

### Risk 1: Breaking Existing Sessions
- **Mitigation**: Default to "en-US" when language not specified
- **Mitigation**: Graceful handling of missing metadata

### Risk 2: Language Mismatch
- **Mitigation**: Validate language codes against supported list
- **Mitigation**: Clear error messages for unsupported languages

### Risk 3: Increased Complexity
- **Mitigation**: Centralize language handling logic
- **Mitigation**: Comprehensive test coverage