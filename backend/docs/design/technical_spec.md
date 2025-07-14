# Technical Specification: Cognitive Reframing Assistant using Google ADK

## 1. Architecture Overview

The system will be implemented as a multi-agent system using Google ADK, leveraging its built-in capabilities for:
- Conversational flow management via Sequential and LLM Agents
- Session state management for maintaining conversation context
- Memory service for long-term knowledge retention
- Safety features and guardrails

## 2. Agent Architecture

### 2.1 Main Orchestrator Agent
- **Type**: LlmAgent
- **Model**: gemini-2.0-flash
- **Role**: Routes conversations through the 4 phases and manages transitions
- **Sub-agents**: Language Detector, Phase Manager

### 2.2 Phase-Specific Agents (Sequential Agent containing):

#### a) Greeting Agent
- **Type**: LlmAgent
- **Role**: Welcome user, explain process, detect language
- **Output**: Detected language stored in session state

#### b) Discovery Agent
- **Type**: LlmAgent
- **Role**: Gather information about thoughts, emotions, situations
- **Tools**: Emotion scale validator (custom tool)
- **Output**: Structured data about user's current state

#### c) Reframing Agent
- **Type**: LlmAgent
- **Role**: Identify cognitive distortions, create balanced thoughts
- **Tools**: CBT pattern matcher (custom tool)
- **Output**: Reframed thoughts and actionable steps

#### d) Summary Agent
- **Type**: LlmAgent
- **Role**: Generate session summary and offer PDF creation
- **Tools**: PDF generator tool

## 3. Key Components

### 3.1 Domain Context Management
Since ADK doesn't support global system prompts, we'll use:
- **Base instruction template** included in all agent instructions
- **Session state initialization** with CBT domain knowledge
- **CBT context module** containing shared guidelines and techniques
- **CBT Knowledge Tool** for agents to query domain information

### 3.2 Session Management
- Use ADK's InMemorySessionService initially
- Migrate to persistent storage for production
- Store: conversation phase, language, emotional assessments, reframed thoughts
- Initialize with CBT domain context on session creation

### 3.3 Memory Service
- Start with InMemoryMemoryService for prototyping
- Consider VertexAiMemoryBankService for production
- Store anonymized patterns and successful reframing examples

### 3.4 Safety Implementation
- **Crisis Detection**: Custom callback to screen for self-harm language
- **Escalation Tool**: Provide crisis helpline resources
- **Content Filtering**: Use Gemini's built-in safety features
- **Disclaimer Tool**: Remind users this doesn't replace therapy

### 3.5 Custom Tools
1. **CBT Knowledge Tool**: Query domain-specific CBT information
2. **Emotion Scale Tool**: Validate 1-10 emotional intensity
3. **CBT Pattern Matcher**: Identify cognitive distortions
4. **PDF Generator**: Create session summaries
5. **Language Detector**: Auto-detect user language
6. **Crisis Resource Tool**: Provide emergency contacts

## 4. Conversation Flow Implementation

Using ADK's event-driven architecture:
1. User message → Main Orchestrator
2. Orchestrator determines current phase
3. Delegates to appropriate Phase Agent
4. Phase Agent processes and yields events
5. State updates persist between turns
6. Orchestrator manages phase transitions

## 5. Development Approach

### Phase 1: Core Conversation Flow
- Implement basic 4-phase structure with Sequential Agents
- Use hardcoded CBT patterns initially
- English-only prototype

### Phase 2: Enhanced Features
- Add language detection and localization
- Implement memory service
- Add PDF generation

### Phase 3: Safety & Production
- Implement all safety guardrails
- Add telemetry and feedback collection
- Deploy with proper authentication

## 6. Technology Stack
- **Framework**: Google ADK (Python)
- **LLM**: Gemini 2.0 Flash
- **Session Storage**: ADK SessionService
- **Memory**: ADK MemoryService
- **PDF Generation**: ReportLab or similar
- **Deployment**: Cloud Run or Vertex AI

## 7. Implementation Details

### 7.1 Domain Context Architecture
```python
# cbt_context.py
BASE_CBT_CONTEXT = """
You are part of a cognitive reframing assistant based on CBT principles...
"""

CBT_DISTORTIONS = {
    "all-or-nothing": "Seeing things in black and white categories",
    "overgeneralization": "Drawing broad conclusions from single events",
    # ... more distortions
}

def initialize_session_with_cbt_context(session):
    """Initialize session state with CBT domain knowledge"""
    session.state.update({
        'cbt_guidelines': CBT_GUIDELINES,
        'distortion_types': list(CBT_DISTORTIONS.keys()),
        'phase': 'greeting'
    })

# Agent creation with base context
def create_agent_with_context(name, specific_instruction, **kwargs):
    return LlmAgent(
        name=name,
        instruction=BASE_CBT_CONTEXT + "\n\n" + specific_instruction,
        **kwargs
    )
```

### 7.2 State Schema
```python
{
    "phase": "greeting|discovery|reframing|summary",
    "language": "en|es|fr|...",
    "situation": "user's described situation",
    "automatic_thoughts": ["thought1", "thought2"],
    "emotions": [{"name": "anxiety", "intensity": 8}],
    "cognitive_distortions": ["all-or-nothing", "catastrophizing"],
    "balanced_thoughts": ["balanced thought 1"],
    "action_steps": ["step1", "step2"],
    "session_start": "timestamp",
    "safety_flags": []
}
```

### 7.3 Agent Instructions

#### Base CBT Context (included in all agents)
```
You are part of a cognitive reframing assistant based on Cognitive Behavioral Therapy (CBT) principles.

Core Guidelines:
- This tool does not replace professional therapy or provide diagnoses
- Use only evidence-based CBT techniques
- Maintain an empathetic, non-judgmental, and collaborative tone
- Focus on thoughts, feelings, and behaviors - not deep psychological analysis
- Encourage users to seek professional help when appropriate

CBT Principles:
- Thoughts, feelings, and behaviors are interconnected
- Identifying and challenging unhelpful thinking patterns can improve wellbeing
- Small behavioral changes can create positive cycles
- Collaboration and guided discovery are more effective than giving advice
```

#### Main Orchestrator
```
{BASE_CBT_CONTEXT}

Your specific role is to:
1. Determine which conversation phase we're in
2. Route to the appropriate phase agent
3. Ensure smooth transitions between phases
4. Monitor for safety concerns
```

#### Discovery Agent
```
{BASE_CBT_CONTEXT}

Your specific role is to gather information about the user's situation.
Ask open-ended questions about:
- The situation they're facing
- Their automatic thoughts
- How they're feeling (use 1-10 scale)
- Physical sensations
Be empathetic but maintain professional boundaries.
```

#### Reframing Agent
```
{BASE_CBT_CONTEXT}

Your specific role is to help identify and reframe unhelpful thinking patterns.
Based on the user's thoughts:
1. Gently point out potential cognitive distortions
2. Collaborate to create balanced alternatives
3. Suggest one small, actionable step
Use Socratic questioning and guided discovery.
```

### 7.4 Safety Guardrails

1. **Pre-processing Callback**: Screen all inputs for crisis indicators
2. **Tool Authorization**: Restrict tools based on conversation phase
3. **Response Validation**: Ensure outputs align with CBT best practices
4. **Audit Trail**: Log all interactions for quality review

### 7.5 Localization Strategy

- Store prompts in structured format with language keys
- Use ADK's state management to maintain language consistency
- Implement fallback to English for unsupported languages

### 7.6 Error Handling

- Graceful degradation if PDF generation fails
- Fallback responses for LLM errors
- Clear user communication about system limitations

## 8. Testing Strategy

### 8.1 Unit Tests
- Individual agent responses
- Tool functionality
- State transitions

### 8.2 Integration Tests
- Full conversation flows
- Multi-language scenarios
- Safety trigger responses

### 8.3 Evaluation Metrics
- Conversation completion rate
- User satisfaction scores
- Safety incident rate
- Language detection accuracy

## 9. Deployment Considerations

### 9.1 Scalability
- Stateless agent design
- Horizontal scaling via Cloud Run
- Caching for common patterns

### 9.2 Monitoring
- Response latency
- Token usage
- Error rates
- User engagement metrics

### 9.3 Security
- No PII in logs
- Encrypted session storage
- API key rotation
- Rate limiting

This specification provides a comprehensive blueprint for implementing the cognitive reframing assistant using Google ADK's capabilities while maintaining simplicity and focusing on user safety and effectiveness.
