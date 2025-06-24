# Re-Frame Agent Architecture Documentation

## Overview

The Re-Frame cognitive reframing assistant is built using Google's Agent Development Kit (ADK). It implements a multi-agent pipeline that guides users through a therapeutic conversation to help reframe negative thoughts using Cognitive Behavioral Therapy (CBT) techniques.

## Architecture Diagram

```
User Input
    ↓
┌─────────────────────────────────────┐
│      INTAKE LOOP (Max 5 turns)      │
│  ┌─────────────────────────────┐    │
│  │     INTAKE AGENT (AURA)     │    │
│  │  - Conversational responses  │    │
│  │  - Collects 3 pieces of data│    │
│  │  - Uses update_intake_state  │    │
│  │    tool to track progress    │    │
│  └─────────────────────────────┘    │
│         ↓ (loops until complete)     │
└─────────────────────────────────────┘
    ↓ (when collection_complete=True)
┌─────────────────────────────────────┐
│         REFRAME AGENT               │
│  - Analyzes collected data          │
│  - Applies CBT techniques           │
│  - Calls process_reframe_data tool  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│         REPORT AGENT                │
│  - Generates PDF report             │
│  - Calls create_pdf_report tool     │
│  - Anonymizes data                  │
└─────────────────────────────────────┘
    ↓
Final PDF Report
```

## Key Components

### 1. **Intake Agent (AURA)**

**Purpose**: Collect information through empathetic conversation

**Key Features**:
- NO structured output schema (no JSON responses)
- Natural, conversational text responses only
- Follows therapeutic best practices from `prompts/intake_agent.md`

**Data Collection Goals**:
1. **trigger_situation**: The context (when/where/who was involved)
2. **automatic_thought**: The exact negative thought (quoted verbatim)
3. **emotion_data**: The emotion and intensity (0-10 scale)

**Tool Usage**:
- Uses `update_intake_state()` tool to track collected information
- Sets `collection_complete=True` when all 3 pieces are gathered
- Sets `crisis_detected=True` if user expresses suicidal ideation

### 2. **Intake Loop**

**Purpose**: Manage the conversation flow

**Configuration**:
- Uses `LoopAgent` to repeat intake conversation
- Maximum 5 iterations (turns)
- Terminates when:
  - `collection_complete=True` (all data collected)
  - `crisis_detected=True` (crisis protocol activated)
  - Maximum iterations reached

### 3. **Reframe Agent**

**Purpose**: Apply CBT techniques to analyze the negative thought

**Process**:
1. Reviews conversation history from intake
2. Extracts the 3 data points
3. Identifies cognitive distortions
4. Finds evidence for/against the thought
5. Creates a balanced perspective
6. Suggests a micro-action

**Tool Usage**:
- Calls `process_reframe_data()` with analysis results
- Stores results in session state for next agent

### 4. **Report Agent**

**Purpose**: Generate a PDF summary of the session

**Process**:
1. Reviews conversation and reframe analysis
2. Checks for crisis flags
3. Anonymizes all personal information
4. Creates structured PDF report

**Tool Usage**:
- Calls `create_pdf_report()` with session data
- Skips PDF generation if crisis was detected

## ADK Best Practices Implemented

### 1. **Conversational Design**
- Removed `output_schema` from intake agent to allow natural language
- Agent responds with warm, empathetic text (not JSON)
- Follows therapeutic conversation examples

### 2. **State Management**
- Uses tools to update internal state
- State persists across loop iterations
- Loop termination based on state flags

### 3. **Sequential Pipeline**
- Clear separation of concerns
- Each agent has a specific role
- Data flows through conversation history

### 4. **Error Prevention**
- No hardcoded context variables in prompts
- Agents extract data from conversation history
- Graceful handling of missing data

## How It Works - Step by Step

### Step 1: User Initiates Conversation
```
User: "I feel so stupid after that work meeting"
```

### Step 2: Intake Agent Responds Conversationally
```
AURA: "That sounds like a really heavy feeling to carry. Thank you for 
sharing that with me. If you're comfortable, could you tell me a bit 
more about what happened during the meeting?"
```

**Behind the scenes**: Agent calls `update_intake_state(automatic_thought="I feel so stupid")`

### Step 3: Conversation Continues
The loop continues with AURA asking gentle, one-at-a-time questions until all three pieces of information are collected.

### Step 4: Loop Termination
When all data is collected, the agent calls:
```python
update_intake_state(
    trigger_situation="10am team video call with boss and coworkers",
    automatic_thought="Everyone here thinks I'm an idiot",
    emotion_data="shame, 8/10",
    collection_complete=True
)
```

### Step 5: Reframe Analysis
The Reframe Agent analyzes the thought pattern and creates a balanced perspective.

### Step 6: PDF Generation
The Report Agent creates an anonymized PDF summary of the session.

## Key Design Decisions

### Why No Output Schema for Intake?
- Output schemas force structured (JSON) responses
- AURA needs to respond conversationally
- Tools handle state management internally

### Why Extract from Conversation History?
- Avoids "Context variable not found" errors
- More flexible and robust
- Aligns with ADK best practices

### Why Separate Agents?
- Clear separation of concerns
- Easier to test and debug
- Can swap out individual components

## Common Issues and Solutions

### Issue: Agent outputs JSON instead of conversation
**Solution**: Remove `output_schema` parameter from LlmAgent

### Issue: "Context variable not found" errors
**Solution**: Don't use `{variable}` in prompts; extract from conversation history

### Issue: Loop doesn't terminate
**Solution**: Ensure tool updates state correctly and sets termination flags

## Testing the Agent

1. Start ADK web interface:
   ```bash
   cd /Users/carlos/workspace/re-frame/adk
   adk web reframe_agent
   ```

2. Navigate to http://localhost:8000

3. Start conversation with a negative thought

4. Observe:
   - Conversational responses (not JSON)
   - Empathetic validation
   - One question at a time
   - Proper loop termination

## Future Improvements

1. **Persistence**: Add database storage for sessions
2. **Analytics**: Track common thought patterns
3. **Customization**: Allow therapist-defined prompts
4. **Integration**: Connect with therapy practice management systems