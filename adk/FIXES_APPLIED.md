# Fixes Applied to Re-Frame Agent

## Issues Identified and Fixed

### 1. Agent Not Waiting for User Responses ✅

**Problem**: The intake agent was extracting all information from the initial user message instead of having a conversational back-and-forth.

**Fix**: Added explicit instructions to the intake agent to enforce turn-based conversation:
```python
CRITICAL RULES FOR CONVERSATION FLOW:
1. ONLY respond to the CURRENT user message - do not extract information from previous messages
2. Ask ONE question at a time and WAIT for the user's response
3. Do NOT infer or assume information not explicitly provided
4. Do NOT call update_intake_state with data unless the user explicitly provides it in their current response
5. The conversation should be turn-based
```

### 2. Agent Outputting JSON Instead of Conversational Text ✅

**Problem**: Both intake and reframe agents were outputting raw JSON to users.

**Fixes**:
- Removed `output_schema=IntakeAgentOutput` from intake agent
- Updated reframe agent instructions to use tools instead of outputting JSON
- Added instruction: "Do NOT output JSON directly to the user"

### 3. Context Variable Errors ✅

**Problem**: ADK was throwing "Context variable not found" errors for `{trigger_situation}`, etc.

**Fix**: Removed hardcoded context variable placeholders from agent instructions and changed to descriptive text about extracting from conversation history.

### 4. PDF Generation Error ✅

**Problem**: FPDF was throwing "1 cannot be converted to Align" errors.

**Fix**: Updated all `pdf.cell()` calls to use named parameters:
```python
# Before:
pdf.cell(0, 10, "Title", 0, 1, "C")

# After:
pdf.cell(0, 10, "Title", ln=1, align="C")
```

### 5. Type Annotation Compatibility ✅

**Problem**: ADK's automatic function calling doesn't support Python 3.10+ union syntax (`str | None`).

**Fix**: Changed to use `Optional[str]` from typing module.

## Testing Instructions

### Web Interface (Recommended)
```bash
cd /Users/carlos/workspace/re-frame/adk
adk web reframe_agent
```
Then navigate to http://localhost:8000

### Command Line
```bash
cd /Users/carlos/workspace/re-frame/adk
adk run reframe_agent
```

## Expected Behavior

1. **Initial Message**: User shares a concern
2. **Agent Response**: AURA acknowledges and asks about the situation
3. **User Response**: Provides situation details
4. **Agent Response**: AURA asks for the exact negative thought
5. **User Response**: Provides the thought
6. **Agent Response**: AURA asks for emotion and intensity
7. **User Response**: Provides emotion data
8. **Completion**: Agent moves to reframe analysis and PDF generation

The agent should NOT:
- Extract all information from the first message
- Output JSON to the user
- Skip ahead in the conversation
- Make assumptions about missing data