# Test-Driven Development Plan for Re-frame Multi-Agent System

## Overview

This document outlines a comprehensive TDD approach for implementing the complete multi-agent therapeutic system with user management, guardrails, episodic memory, and session documentation.

## System Architecture Components

1. **Multi-Agent Therapeutic System** (Core ADK Implementation)
2. **User Management & Authentication API** (Separate Backend)
3. **Guardrails System** (Input/Output Validation)
4. **Episodic Memory System** (Pattern Recognition)
5. **PDF Generation & Storage** (Anonymized Session Records)
6. **Observability** (Via Google AI Studio)

## Phase 1: Core Infrastructure Tests

### 1.1 User Management & Authentication API

```python
# tests/test_auth_api.py

class TestUserAuthentication:
    """Test user authentication and management"""
    
    def test_user_registration_success(self):
        """
        Given: Valid registration data
        When: User registers
        Then: Account created, verification email sent
        """
        
    def test_user_registration_duplicate_email(self):
        """
        Given: Email already exists
        When: User tries to register
        Then: Appropriate error returned
        """
        
    def test_login_success(self):
        """
        Given: Valid credentials
        When: User logs in
        Then: JWT token returned, session created
        """
        
    def test_login_invalid_credentials(self):
        """
        Given: Invalid credentials
        When: User tries to login
        Then: Authentication error returned
        """
        
    def test_session_management(self):
        """
        Given: Authenticated user
        When: Making API calls
        Then: Session properly maintained
        """
        
    def test_logout_invalidates_session(self):
        """
        Given: Active session
        When: User logs out
        Then: Session invalidated, tokens revoked
        """

class TestUserDataPrivacy:
    """Test privacy and data protection"""
    
    def test_user_data_encryption_at_rest(self):
        """
        Given: User data stored
        When: Checking database
        Then: All PII encrypted
        """
        
    def test_gdpr_data_export(self):
        """
        Given: User requests data
        When: Export triggered
        Then: All user data provided in portable format
        """
        
    def test_account_deletion(self):
        """
        Given: User requests deletion
        When: Account deleted
        Then: All PII removed, sessions anonymized
        """
```

### 1.2 Guardrails System

```python
# tests/test_guardrails.py

class TestInputGuardrails:
    """Test input validation and topic filtering"""
    
    def test_therapeutic_topic_allowed(self):
        """
        Given: Valid therapeutic concern
        When: Input processed
        Then: Allowed through to agents
        """
        
    def test_off_topic_rejected(self):
        """
        Given: Non-therapeutic query (e.g., "Write me code")
        When: Input processed
        Then: Politely redirected
        """
        
    def test_harmful_content_blocked(self):
        """
        Given: Harmful or abusive content
        When: Input processed
        Then: Blocked with appropriate response
        """
        
    def test_pii_detection(self):
        """
        Given: Input containing PII
        When: Processed
        Then: PII masked before agent processing
        """
        
    def test_input_length_limits(self):
        """
        Given: Extremely long input
        When: Processed
        Then: Truncated or rejected appropriately
        """

class TestOutputGuardrails:
    """Test output validation and safety"""
    
    def test_no_harmful_advice(self):
        """
        Given: Agent response
        When: Output validated
        Then: No harmful suggestions pass through
        """
        
    def test_maintains_therapeutic_boundaries(self):
        """
        Given: Agent response
        When: Validated
        Then: Stays within therapeutic scope
        """
        
    def test_pii_removed_from_output(self):
        """
        Given: Response with potential PII
        When: Processed
        Then: PII removed or masked
        """
```

## Phase 2: Multi-Agent System Tests

### 2.1 Information Gathering Loop

```python
# tests/test_conversation_loop.py

class TestConversationalGathering:
    """Test the conversational information gathering loop"""
    
    def test_incomplete_information_prompts_questions(self):
        """
        Given: Vague input like "I feel bad"
        When: Processed by ConversationAgent
        Then: Asks clarifying questions
        """
        
    def test_complete_information_proceeds(self):
        """
        Given: Complete thought with context
        When: Validated
        Then: Proceeds to framework selection
        """
        
    def test_loop_exits_after_max_iterations(self):
        """
        Given: User provides insufficient info repeatedly
        When: Max iterations reached
        Then: Gracefully exits with best effort
        """
        
    def test_information_accumulation(self):
        """
        Given: Multiple conversation turns
        When: Information gathered
        Then: Session state properly accumulates data
        """
        
    def test_crisis_detection_exits_loop(self):
        """
        Given: Crisis indicators detected
        When: During conversation
        Then: Immediately exits to crisis handling
        """
```

### 2.2 Framework Selection

```python
# tests/test_framework_selection.py

class TestFrameworkSelector:
    """Test intelligent framework selection"""
    
    def test_high_distress_selects_dbt(self):
        """
        Given: Emotion intensity >= 7
        When: Framework selected
        Then: DBT prioritized
        """
        
    def test_catastrophizing_selects_cbt(self):
        """
        Given: Catastrophic thinking patterns
        When: Analyzed
        Then: CBT selected as primary
        """
        
    def test_values_conflict_selects_act(self):
        """
        Given: Clear values vs fear conflict
        When: Analyzed
        Then: ACT selected
        """
        
    def test_control_issues_select_stoicism(self):
        """
        Given: Struggling with uncontrollables
        When: Analyzed
        Then: Stoicism selected
        """
        
    def test_multiple_frameworks_selected(self):
        """
        Given: Complex situation
        When: Analyzed
        Then: 2-3 complementary frameworks selected
        """
```

### 2.3 Individual Framework Agents

```python
# tests/test_framework_agents.py

class TestCBTAgent:
    """Test CBT framework agent"""
    
    def test_identifies_cognitive_distortions(self):
        """
        Given: Thought with distortions
        When: CBT agent analyzes
        Then: Correctly identifies distortion types
        """
        
    def test_evidence_for_against(self):
        """
        Given: Negative thought
        When: Processed
        Then: Balanced evidence provided
        """
        
    def test_creates_behavioral_experiment(self):
        """
        Given: Testable prediction
        When: Analyzed
        Then: Appropriate experiment suggested
        """

class TestDBTAgent:
    """Test DBT framework agent"""
    
    def test_high_distress_triggers_tipp(self):
        """
        Given: Intensity >= 8
        When: DBT processes
        Then: TIPP technique provided
        """
        
    def test_dialectical_statements(self):
        """
        Given: Black-white thinking
        When: Processed
        Then: AND statements used
        """
        
    def test_skills_menu_provided(self):
        """
        Given: Distressing situation
        When: Analyzed
        Then: Multiple DBT skills offered
        """

class TestACTAgent:
    """Test ACT framework agent"""
    
    def test_values_clarification(self):
        """
        Given: Values conflict
        When: Processed
        Then: Values explored and clarified
        """
        
    def test_defusion_techniques(self):
        """
        Given: Fused with thoughts
        When: Analyzed
        Then: Defusion techniques provided
        """
        
    def test_committed_action_steps(self):
        """
        Given: Values identified
        When: Processed
        Then: Small actionable steps suggested
        """

class TestStoicismAgent:
    """Test Stoicism framework agent"""
    
    def test_dichotomy_of_control(self):
        """
        Given: Worry about others' opinions
        When: Analyzed
        Then: Clear control boundaries identified
        """
        
    def test_virtue_focus(self):
        """
        Given: External validation seeking
        When: Processed
        Then: Redirected to virtue/character
        """
        
    def test_perspective_exercises(self):
        """
        Given: Catastrophic thinking
        When: Analyzed
        Then: Zoom out perspective provided
        """
```

### 2.4 Synthesis and Integration

```python
# tests/test_synthesis.py

class TestSynthesisAgent:
    """Test multi-framework synthesis"""
    
    def test_no_contradictions(self):
        """
        Given: Multiple framework outputs
        When: Synthesized
        Then: No contradictory advice
        """
        
    def test_coherent_narrative(self):
        """
        Given: 2-3 framework insights
        When: Combined
        Then: Flows naturally, not list-like
        """
        
    def test_actionable_suggestions(self):
        """
        Given: Synthesis complete
        When: Response generated
        Then: Contains 2-3 concrete actions
        """
        
    def test_appropriate_length(self):
        """
        Given: Multiple insights
        When: Synthesized
        Then: Under 300 words
        """
```

## Phase 3: Episodic Memory System

```python
# tests/test_episodic_memory.py

class TestEpisodicMemory:
    """Test pattern recognition and memory"""
    
    def test_stores_session_patterns(self):
        """
        Given: Completed session
        When: Processed
        Then: Key patterns stored in memory
        """
        
    def test_retrieves_relevant_history(self):
        """
        Given: New session with returning user
        When: Started
        Then: Relevant past patterns retrieved
        """
        
    def test_pattern_recognition(self):
        """
        Given: Multiple sessions
        When: Analyzed
        Then: Recurring patterns identified
        """
        
    def test_privacy_preserved(self):
        """
        Given: Memory storage
        When: Inspected
        Then: No raw PII, only patterns
        """
        
    def test_memory_influences_framework_selection(self):
        """
        Given: User history showing framework effectiveness
        When: New session
        Then: Preferred frameworks prioritized
        """
```

## Phase 4: PDF Generation and Storage

```python
# tests/test_pdf_generation.py

class TestPDFGeneration:
    """Test session documentation"""
    
    def test_pdf_contains_all_sections(self):
        """
        Given: Completed session
        When: PDF generated
        Then: Contains situation, framework, reasoning, output
        """
        
    def test_pii_masked_in_pdf(self):
        """
        Given: Session with PII
        When: PDF generated
        Then: All PII replaced with placeholders
        """
        
    def test_pdf_encrypted_at_rest(self):
        """
        Given: PDF stored
        When: In document DB
        Then: Encrypted using user-specific key
        """
        
    def test_pdf_accessible_to_user_only(self):
        """
        Given: Stored PDFs
        When: Accessed
        Then: Only owner can retrieve
        """
        
    def test_pdf_formatting_readable(self):
        """
        Given: Generated PDF
        When: Opened
        Then: Professional, readable format
        """
```

## Phase 5: Integration Tests

```python
# tests/test_full_integration.py

class TestFullUserJourney:
    """End-to-end integration tests"""
    
    def test_new_user_complete_journey(self):
        """
        Given: New user
        When: Registers → First session → Receives help
        Then: All components work together
        """
        
    def test_returning_user_with_history(self):
        """
        Given: User with past sessions
        When: New session started
        Then: History influences personalization
        """
        
    def test_crisis_handling_full_flow(self):
        """
        Given: Crisis situation
        When: Detected
        Then: Appropriate response, documentation, follow-up
        """
        
    def test_feedback_loop(self):
        """
        Given: User provides feedback
        When: Stored
        Then: Influences future sessions
        """
```

## Phase 6: Performance and Reliability

```python
# tests/test_performance.py

class TestSystemPerformance:
    """Test performance requirements"""
    
    def test_response_time_under_5_seconds(self):
        """
        Given: Normal load
        When: Processing request
        Then: Response within 5 seconds
        """
        
    def test_parallel_framework_processing(self):
        """
        Given: Multiple frameworks selected
        When: Processing
        Then: Run in parallel, not sequential
        """
        
    def test_handles_concurrent_users(self):
        """
        Given: 100 concurrent users
        When: System loaded
        Then: All receive timely responses
        """
        
    def test_graceful_degradation(self):
        """
        Given: One service fails
        When: Request processed
        Then: Degrades gracefully, partial response
        """
```

## Implementation Order (TDD Approach)

### Week 1: Foundation
1. **Day 1-2**: User Authentication API
   - Write auth tests first
   - Implement JWT-based auth
   - Test session management

2. **Day 3-4**: Guardrails System
   - Write input/output validation tests
   - Implement guardrails
   - Test topic filtering

3. **Day 5**: Database Setup
   - Write encryption tests
   - Set up encrypted document store
   - Test data privacy

### Week 2: Core Agents
1. **Day 1-2**: Conversational Loop
   - Write conversation tests
   - Implement LoopAgent with ConversationAgent
   - Test information gathering

2. **Day 3-4**: Framework Agents
   - Write individual framework tests
   - Implement CBT and DBT agents first
   - Test framework-specific logic

3. **Day 5**: Framework Selector
   - Write selection logic tests
   - Implement intelligent routing
   - Test selection criteria

### Week 3: Integration
1. **Day 1-2**: Synthesis Agent
   - Write synthesis tests
   - Implement multi-framework integration
   - Test coherence and quality

2. **Day 3-4**: Memory System
   - Write episodic memory tests
   - Implement pattern storage/retrieval
   - Test personalization

3. **Day 5**: PDF Generation
   - Write documentation tests
   - Implement PDF generator with PII masking
   - Test encryption and storage

### Week 4: Polish and Deploy
1. **Day 1-2**: Full Integration Testing
   - Write end-to-end tests
   - Fix integration issues
   - Test complete user journeys

2. **Day 3-4**: Performance Optimization
   - Write performance tests
   - Optimize parallel processing
   - Test under load

3. **Day 5**: Deployment
   - Final security audit
   - Deploy to production
   - Monitor initial usage

## Key Testing Principles

1. **Write Tests First**: Every feature starts with failing tests
2. **Test Behavior, Not Implementation**: Focus on what, not how
3. **Isolated Unit Tests**: Mock external dependencies
4. **Integration Tests**: Test component interactions
5. **End-to-End Tests**: Validate complete user journeys
6. **Privacy-First Testing**: Ensure no PII leakage
7. **Performance Benchmarks**: Set and test SLAs

## Continuous Integration Setup

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          
      - name: Run unit tests
        run: pytest tests/unit -v --cov
        
      - name: Run integration tests
        run: pytest tests/integration -v
        
      - name: Check security
        run: |
          bandit -r src/
          safety check
          
      - name: Test guardrails
        run: pytest tests/guardrails -v
```

## Observability Notes

Google AI Studio provides:
- Request/response tracing
- Token usage monitoring
- Latency metrics
- Error tracking

Additional monitoring needed:
- User session analytics
- Framework effectiveness metrics
- Crisis detection accuracy
- PDF generation success rates

## Success Metrics

1. **Technical**:
   - 95% test coverage
   - <5s response time (p95)
   - Zero PII leakage
   - 99.9% uptime

2. **Therapeutic**:
   - 80% user satisfaction
   - 70% return user rate
   - <5% false positive crisis detection
   - 90% appropriate framework selection

3. **Privacy**:
   - 100% PII masked in outputs
   - 100% encrypted storage
   - GDPR compliant
   - User data fully exportable/deletable