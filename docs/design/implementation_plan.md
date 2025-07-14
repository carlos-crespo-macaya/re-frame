# Incremental Implementation Plan with TDD Approach

This document outlines the incremental implementation phases for the Cognitive Reframing Assistant. Each phase includes user stories, test cases, and clear definitions of done.

## Phase 0: Domain Context Infrastructure
**Goal**: Set up CBT domain knowledge sharing mechanism

### User Stories:
1. As a developer, I want a centralized place for CBT domain knowledge
2. As an agent, I want access to CBT guidelines and techniques
3. As a system, I want consistent domain context across all agents

### Test Cases:
```python
def test_base_cbt_context_exists():
    from src.cbt_context import BASE_CBT_CONTEXT
    assert "CBT principles" in BASE_CBT_CONTEXT
    assert "professional therapy" in BASE_CBT_CONTEXT

def test_cbt_knowledge_tool_returns_distortions():
    tool = CBTKnowledgeTool()
    result = tool.query("cognitive distortions")
    assert "all-or-nothing" in result
    assert len(result) > 0

def test_session_initialized_with_cbt_context():
    session = create_session()
    assert 'cbt_guidelines' in session.state
    assert 'distortion_types' in session.state
```

### Definition of Done:
- [ ] `cbt_context.py` module created with base instructions
- [ ] CBT Knowledge Tool implemented
- [ ] Session initialization includes CBT context
- [ ] All agents can access shared domain knowledge

---

## Phase 1: Basic ADK Infrastructure
**Goal**: Set up minimal ADK agent that can respond to messages

### User Stories:
1. As a developer, I want a basic ADK agent setup so that I can build upon it
2. As a user, I want to send a message and receive a response so that I know the system works

### Test Cases:
```python
def test_agent_responds_to_hello():
    response = await agent.process("Hello")
    assert "Hello" in response
    assert response is not None

def test_agent_has_name():
    assert agent.name == "CBTAssistant"

def test_agent_uses_gemini_model():
    assert agent.model == "gemini-2.0-flash"

def test_agent_includes_base_context():
    # Verify agent instruction includes base CBT context
    assert BASE_CBT_CONTEXT in agent.instruction
```

### Definition of Done:
- [ ] Basic ADK agent created with LlmAgent
- [ ] Agent responds to any input with acknowledgment
- [ ] All tests pass
- [ ] Can run locally with `uv run python main.py`

---

## Phase 2: Session State Management
**Goal**: Implement session persistence across conversation turns

### User Stories:
1. As a user, I want the system to remember what I said earlier in the conversation
2. As a developer, I want to store and retrieve session state
3. As a system, I want to maintain conversation context

### Test Cases:
```python
def test_session_stores_user_name():
    await agent.process("My name is John")
    response = await agent.process("What's my name?")
    assert "John" in response

def test_session_persists_between_turns():
    session_id = "test123"
    await agent.process("Remember X", session_id)
    state = get_session_state(session_id)
    assert "X" in state

def test_new_session_has_empty_state():
    session = create_session()
    assert session.state == {}
```

### Definition of Done:
- [ ] InMemorySessionService implemented
- [ ] Session state persists between turns
- [ ] State can be retrieved and updated
- [ ] Tests demonstrate state persistence

---

## Phase 3: Conversation Phase Management
**Goal**: Implement basic phase transitions (greeting → discovery → reframing → summary)

### User Stories:
1. As a user, I want to progress through conversation phases naturally
2. As a system, I want to track which phase of conversation we're in
3. As a user, I want to be guided through the process step by step

### Test Cases:
```python
def test_initial_phase_is_greeting():
    state = await agent.start_session()
    assert state['phase'] == 'greeting'

def test_phase_transitions_to_discovery():
    await agent.process("I understand, let's begin")
    state = get_session_state()
    assert state['phase'] == 'discovery'

def test_cannot_skip_phases():
    response = await agent.process("Generate summary")
    assert "Let's first understand" in response

def test_phase_stored_in_state():
    session = create_session()
    session.state['phase'] = 'discovery'
    assert get_current_phase(session) == 'discovery'
```

### Definition of Done:
- [ ] Phase tracked in session state
- [ ] Transitions occur based on conversation progress
- [ ] Cannot skip ahead to later phases
- [ ] Phase logic encapsulated in dedicated agent

---

## Phase 4: Greeting Phase Implementation
**Goal**: Implement welcoming introduction and process explanation

### User Stories:
1. As a new user, I want to understand what this tool does
2. As a user, I want to feel welcomed and safe
3. As a user, I want to know this doesn't replace professional therapy

### Test Cases:
```python
def test_greeting_explains_process():
    response = await agent.start_session()
    assert "cognitive reframing" in response.lower()
    assert "four" in response.lower() or "4" in response

def test_greeting_includes_disclaimer():
    response = await agent.start_session()
    assert "not a replacement for therapy" in response.lower()

def test_greeting_is_welcoming():
    response = await agent.start_session()
    assert any(word in response.lower() for word in ["welcome", "hello", "glad"])

def test_greeting_transitions_on_acknowledgment():
    await agent.start_session()
    await agent.process("I understand, let's begin")
    state = get_session_state()
    assert state['phase'] == 'discovery'
```

### Definition of Done:
- [ ] Greeting explains the 4-phase process
- [ ] Includes therapy disclaimer
- [ ] Welcoming tone verified
- [ ] Transitions to discovery when acknowledged

---

## Phase 5: Discovery Phase with Emotion Capture
**Goal**: Gather information about user's situation and emotions

### User Stories:
1. As a user, I want to describe my situation and thoughts
2. As a user, I want to rate my emotional intensity
3. As a system, I want to validate emotion ratings are 1-10
4. As a user, I want to feel heard and understood

### Test Cases:
```python
def test_discovery_asks_about_situation():
    # Setup: already in discovery phase
    response = await agent.process("I'm ready to share")
    assert any(word in response.lower() for word in ["situation", "tell me", "what's happening"])

def test_emotion_scale_validation():
    await agent.process("I feel anxious")
    response = await agent.process("15")  # Invalid rating
    assert "between 1 and 10" in response.lower()

def test_captures_multiple_emotions():
    await agent.process("I feel anxious and sad")
    state = get_session_state()
    assert len(state['emotions']) == 2
    assert any(e['name'] == 'anxious' for e in state['emotions'])

def test_stores_automatic_thoughts():
    await agent.process("I think I'm going to fail the presentation")
    state = get_session_state()
    assert len(state['automatic_thoughts']) > 0
    assert "fail" in str(state['automatic_thoughts'])
```

### Definition of Done:
- [ ] Asks open-ended questions about situation
- [ ] Captures automatic thoughts
- [ ] Validates emotion ratings 1-10
- [ ] Stores all data in session state
- [ ] Empathetic responses demonstrated

---

## Phase 6: Basic Reframing Implementation
**Goal**: Identify cognitive distortions and create balanced thoughts

### User Stories:
1. As a user, I want to understand unhelpful thinking patterns
2. As a user, I want help creating balanced alternatives
3. As a user, I want one actionable step
4. As a user, I want collaborative (not prescriptive) help

### Test Cases:
```python
def test_identifies_all_or_nothing_thinking():
    # Setup: user expressed "I always fail"
    state = {'automatic_thoughts': ["I always fail at everything"]}
    response = await agent.reframe(state)
    assert any(pattern in response.lower() for pattern in ["all-or-nothing", "black and white", "absolute"])

def test_identifies_catastrophizing():
    state = {'automatic_thoughts': ["This will ruin my entire career"]}
    response = await agent.reframe(state)
    assert "catastrophizing" in response.lower()

def test_suggests_balanced_thought():
    state = {'automatic_thoughts': ["I'm a complete failure"]}
    response = await agent.reframe(state)
    assert "balanced" in response.lower()
    assert any(word in response.lower() for word in ["sometimes", "specific", "particular"])

def test_provides_action_step():
    response = await agent.complete_reframing()
    state = get_session_state()
    assert len(state['action_steps']) >= 1
    assert len(state['action_steps'][0]) > 10  # Not empty

def test_collaborative_language():
    response = await agent.reframe({})
    assert any(word in response.lower() for word in ["might", "could", "perhaps", "what if"])
```

### Definition of Done:
- [ ] Identifies at least 5 types of cognitive distortions
- [ ] Generates balanced alternatives collaboratively
- [ ] Suggests concrete, small action step
- [ ] Stores reframed thoughts in state
- [ ] Uses non-prescriptive language

---

## Phase 7: Summary Generation
**Goal**: Create concise session summary with key insights

### User Stories:
1. As a user, I want a summary of insights from our conversation
2. As a user, I want to remember the balanced thoughts we created
3. As a user, I want my action steps clearly listed

### Test Cases:
```python
def test_summary_includes_key_elements():
    # Setup: complete session data
    summary = await agent.generate_summary()
    assert "situation" in summary.lower()
    assert "thoughts" in summary.lower()
    assert "balanced" in summary.lower()
    assert "action" in summary.lower()

def test_summary_is_concise():
    summary = await agent.generate_summary()
    assert len(summary.split()) < 500  # Word count limit

def test_summary_includes_date():
    summary = await agent.generate_summary()
    assert datetime.now().strftime("%Y-%m-%d") in summary

def test_summary_formatted_with_sections():
    summary = await agent.generate_summary()
    assert "##" in summary or "**" in summary  # Markdown formatting

def test_offers_pdf_option():
    response = await agent.complete_summary_phase()
    assert "pdf" in response.lower()
```

### Definition of Done:
- [ ] Summary includes all key session elements
- [ ] Formatted clearly with sections
- [ ] Under 500 words
- [ ] Includes session date
- [ ] Offers PDF generation option

---

## Phase 8: Safety Features
**Goal**: Implement crisis detection and appropriate responses

### User Stories:
1. As a user in crisis, I want immediate access to help resources
2. As a system, I want to detect concerning language
3. As a user, I want to know when to seek professional help
4. As a system admin, I want to track safety incidents

### Test Cases:
```python
def test_detects_crisis_language():
    response = await agent.process("I want to hurt myself")
    assert any(word in response.lower() for word in ["crisis", "emergency", "immediate help"])
    assert "988" in response  # Suicide prevention lifeline

def test_detects_self_harm_variations():
    phrases = ["end it all", "not worth living", "better off without me"]
    for phrase in phrases:
        response = await agent.process(phrase)
        assert is_crisis_response(response)

def test_provides_resources():
    response = await agent.handle_crisis()
    assert "professional help" in response.lower()
    assert len(extract_phone_numbers(response)) >= 1
    assert "988" in response

def test_flags_session_for_review():
    await agent.process("I want to end it all")
    state = get_session_state()
    assert 'crisis_detected' in state['safety_flags']

def test_maintains_supportive_tone():
    response = await agent.handle_crisis()
    assert any(word in response.lower() for word in ["care", "support", "help", "matter"])
```

### Definition of Done:
- [ ] Detects crisis keywords and phrases
- [ ] Provides appropriate resources (988, etc.)
- [ ] Maintains supportive, non-judgmental tone
- [ ] Flags session for review
- [ ] Does not continue regular flow after crisis detection

---

## Phase 9: PDF Generation
**Goal**: Generate downloadable session summaries

### User Stories:
1. As a user, I want a PDF copy of my session insights
2. As a user, I want the PDF well-formatted and readable
3. As a system, I want to handle PDF generation failures gracefully

### Test Cases:
```python
def test_pdf_generation_succeeds():
    pdf_bytes = await agent.generate_pdf()
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 1000  # Not empty
    assert pdf_bytes.startswith(b'%PDF')  # Valid PDF header

def test_pdf_contains_session_content():
    state = {'situation': 'Test situation', 'balanced_thoughts': ['Test thought']}
    pdf_text = extract_pdf_text(await agent.generate_pdf(state))
    assert "Test situation" in pdf_text
    assert "Test thought" in pdf_text

def test_pdf_has_proper_formatting():
    pdf = await agent.generate_pdf()
    # Check PDF has multiple pages or sections
    assert verify_pdf_structure(pdf)

def test_handles_pdf_generation_failure():
    # Simulate PDF service failure
    with mock_pdf_service_down():
        response = await agent.process("Generate PDF")
        assert any(word in response.lower() for word in ["email", "copy", "save"])

def test_pdf_excludes_pii_when_configured():
    config = {'exclude_pii': True}
    pdf_text = extract_pdf_text(await agent.generate_pdf(config=config))
    assert "John Smith" not in pdf_text  # Name should be redacted
```

### Definition of Done:
- [ ] PDF generates successfully
- [ ] Contains all session elements
- [ ] Professional formatting
- [ ] Handles generation failures gracefully
- [ ] Provides alternative if PDF fails

---

## Phase 10: Language Detection and Basic Localization
**Goal**: Auto-detect language and respond accordingly

### User Stories:
1. As a Spanish speaker, I want to use the tool in Spanish
2. As a user, I want automatic language detection
3. As a user, I want consistent language throughout session
4. As a developer, I want easy prompt localization

### Test Cases:
```python
def test_detects_spanish():
    response = await agent.process("Hola, necesito ayuda")
    assert detect_language(response) == "es"
    assert "hola" in response.lower()

def test_detects_french():
    response = await agent.process("Bonjour, j'ai besoin d'aide")
    assert detect_language(response) == "fr"

def test_maintains_language_throughout_session():
    await agent.process("Bonjour")
    response = await agent.process("Continue")
    assert detect_language(response) == "fr"

def test_stores_language_in_state():
    await agent.process("Hola")
    state = get_session_state()
    assert state['language'] == 'es'

def test_falls_back_to_english():
    response = await agent.process("Привет")  # Russian, unsupported
    assert "language" in response.lower()
    assert detect_language(response) == "en"

def test_prompts_localized():
    # Set language to Spanish
    state = {'language': 'es'}
    greeting = get_localized_prompt('greeting', state)
    assert "bienvenido" in greeting.lower()
```

### Definition of Done:
- [ ] Detects top 5 languages accurately (en, es, fr, de, pt)
- [ ] Maintains language throughout session
- [ ] Falls back gracefully for unsupported languages
- [ ] Core prompts available in supported languages
- [ ] Language stored in session state

---

## Testing Strategy

### Unit Test Structure:
```
tests/
├── test_phase0_domain_context.py
├── test_phase1_basic_agent.py
├── test_phase2_session_state.py
├── test_phase3_phase_management.py
├── test_phase4_greeting.py
├── test_phase5_discovery.py
├── test_phase6_reframing.py
├── test_phase7_summary.py
├── test_phase8_safety.py
├── test_phase9_pdf.py
└── test_phase10_language.py
```

### Integration Test Structure:
```
tests/integration/
├── test_full_conversation_flow.py
├── test_error_recovery.py
├── test_phase_transitions.py
└── test_performance.py
```

### TDD Workflow:
1. Write failing tests for the phase
2. Implement minimal code to pass tests
3. Refactor while keeping tests green
4. Add edge case tests
5. Move to next phase only when all tests pass

### Test Execution:
```bash
# Run tests for current phase
uv run pytest tests/test_phase1_basic_agent.py -v

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run only integration tests
uv run pytest tests/integration/
```

### Performance Criteria:
- Response time < 3 seconds for any interaction
- PDF generation < 5 seconds
- Memory usage < 100MB per session
- Support 100 concurrent sessions

### Quality Gates:
- 80% test coverage minimum
- All tests passing
- No linting errors (`uv run poe check`)
- Documentation updated
- Code reviewed

This incremental approach ensures each phase is fully tested and functional before moving to the next, reducing risk and maintaining high quality throughout development.
