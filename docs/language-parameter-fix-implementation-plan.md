# Language Parameter Fix - TDD Implementation Plan

## Overview

This document provides a detailed Test-Driven Development (TDD) implementation plan for fixing the language parameter issue in text mode. We'll follow the red-green-refactor cycle for each component.

## Implementation Phases

### Phase 1: Test Infrastructure and Utilities
**Goal**: Create test fixtures and language validation utilities

### Phase 2: Session Language Management
**Goal**: Ensure language is properly stored and retrieved from sessions

### Phase 3: Agent Language Propagation
**Goal**: Pass language context to all agents

### Phase 4: Agent Language Instructions
**Goal**: Update agents to generate responses in specified language

### Phase 5: Integration and E2E Testing
**Goal**: Verify complete language flow works correctly

## Detailed Implementation Plan

### Phase 1: Test Infrastructure and Utilities (2 hours)

#### Step 1.1: Create Language Constants and Test Fixtures
```python
# File: backend/tests/fixtures/language_fixtures.py
"""
Test fixtures for language testing
"""

SUPPORTED_LANGUAGES = {
    "en-US": "English",
    "es-ES": "Spanish", 
    "pt-BR": "Portuguese",
    "de-DE": "German",
    "fr-FR": "French",
    "it-IT": "Italian",
    "nl-NL": "Dutch",
    "pl-PL": "Polish",
    "hi-IN": "Hindi",
    "ja-JP": "Japanese",
    "ko-KR": "Korean", 
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)"
}

LANGUAGE_TEST_CASES = [
    ("en-US", "Hello! I'm here to help you with cognitive reframing."),
    ("es-ES", "¡Hola! Estoy aquí para ayudarte con el reencuadre cognitivo."),
    ("pt-BR", "Olá! Estou aqui para ajudá-lo com a reestruturação cognitiva."),
    # Add more test cases
]
```

#### Step 1.2: Create Language Validation Tests
```python
# File: backend/tests/test_language_utils.py
"""
Tests for language utilities
"""
import pytest
from src.utils.language_utils import (
    validate_language_code,
    get_default_language,
    normalize_language_code
)

class TestLanguageValidation:
    def test_validate_supported_language(self):
        assert validate_language_code("en-US") == True
        assert validate_language_code("es-ES") == True
        
    def test_validate_unsupported_language(self):
        assert validate_language_code("xx-XX") == False
        assert validate_language_code("") == False
        assert validate_language_code(None) == False
        
    def test_normalize_language_code(self):
        assert normalize_language_code("en") == "en-US"
        assert normalize_language_code("es") == "es-ES"
        assert normalize_language_code("EN-us") == "en-US"
        
    def test_default_language(self):
        assert get_default_language() == "en-US"
```

#### Step 1.3: Implement Language Utilities
```python
# File: backend/src/utils/language_utils.py
"""
Language utilities for consistent language handling
"""
from typing import Optional

SUPPORTED_LANGUAGES = {
    "en-US": "English",
    "es-ES": "Spanish",
    # ... rest of languages
}

DEFAULT_LANGUAGE = "en-US"

def validate_language_code(language_code: Optional[str]) -> bool:
    """Validate if language code is supported."""
    if not language_code:
        return False
    return language_code in SUPPORTED_LANGUAGES

def normalize_language_code(language_code: Optional[str]) -> str:
    """Normalize language code to standard format."""
    if not language_code:
        return DEFAULT_LANGUAGE
        
    # Handle short codes
    short_codes = {
        "en": "en-US",
        "es": "es-ES",
        "pt": "pt-BR",
        # ... more mappings
    }
    
    # Normalize case and format
    normalized = language_code.strip()
    if normalized.lower() in short_codes:
        return short_codes[normalized.lower()]
    
    # Standard format: xx-XX
    parts = normalized.split("-")
    if len(parts) == 2:
        return f"{parts[0].lower()}-{parts[1].upper()}"
        
    return DEFAULT_LANGUAGE

def get_default_language() -> str:
    """Get default language code."""
    return DEFAULT_LANGUAGE
```

### Phase 2: Session Language Management (3 hours)

#### Step 2.1: Test Session Language Storage
```python
# File: backend/tests/test_session_language.py
"""
Tests for session language management
"""
import pytest
from src.session_manager import SessionManager
from src.models.session import SessionInfo

class TestSessionLanguageManagement:
    @pytest.fixture
    def session_manager(self):
        return SessionManager()
        
    def test_create_session_with_language(self, session_manager):
        session = session_manager.create_session(
            session_id="test-123",
            user_id="user-123"
        )
        session.metadata["language"] = "es-ES"
        
        retrieved = session_manager.get_session("test-123")
        assert retrieved.metadata.get("language") == "es-ES"
        
    def test_session_language_persistence(self, session_manager):
        # Create session with language
        session = session_manager.create_session(
            session_id="test-456",
            user_id="user-456"
        )
        session.metadata["language"] = "pt-BR"
        
        # Simulate retrieval in different request
        retrieved = session_manager.get_session("test-456")
        assert retrieved.metadata.get("language") == "pt-BR"
        
    def test_missing_language_defaults(self, session_manager):
        session = session_manager.create_session(
            session_id="test-789",
            user_id="user-789"
        )
        # Don't set language
        
        # Should return None or we handle default elsewhere
        assert session.metadata.get("language") is None
```

#### Step 2.2: Test SSE Endpoint Language Handling
```python
# File: backend/tests/test_text_router_language.py
"""
Tests for language handling in text router
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
class TestSSELanguageHandling:
    async def test_sse_endpoint_stores_language(self, async_client: AsyncClient):
        with patch("src.text.router.start_agent_session") as mock_start:
            mock_start.return_value = (AsyncMock(), AsyncMock(), {})
            
            # Connect with Spanish language
            response = await async_client.get(
                "/api/events/test-session-123?language=es-ES"
            )
            
            # Verify language was passed to agent creation
            mock_start.assert_called_once_with("test-session-123", "es-ES")
            
    async def test_sse_endpoint_default_language(self, async_client: AsyncClient):
        with patch("src.text.router.start_agent_session") as mock_start:
            mock_start.return_value = (AsyncMock(), AsyncMock(), {})
            
            # Connect without language parameter
            response = await async_client.get("/api/events/test-session-456")
            
            # Should use default language
            mock_start.assert_called_once_with("test-session-456", "en-US")
            
    async def test_sse_invalid_language_fallback(self, async_client: AsyncClient):
        with patch("src.text.router.start_agent_session") as mock_start:
            mock_start.return_value = (AsyncMock(), AsyncMock(), {})
            
            # Connect with invalid language
            response = await async_client.get(
                "/api/events/test-session-789?language=invalid"
            )
            
            # Should fallback to default
            mock_start.assert_called_once_with("test-session-789", "en-US")
```

#### Step 2.3: Update SSE Endpoint Implementation
```python
# File: backend/src/text/router.py (modifications)
from src.utils.language_utils import validate_language_code, get_default_language

@router.get("/api/events/{session_id}")
async def sse_endpoint(
    request: Request, 
    session_id: str, 
    language: str = Query(default="en-US")
):
    """SSE endpoint for agent to client communication"""
    
    # Validate and normalize language
    if not validate_language_code(language):
        logger.warning(
            "invalid_language_code",
            session_id=session_id,
            requested_language=language,
            fallback=get_default_language()
        )
        language = get_default_language()
    
    # Rest of implementation...
```

### Phase 3: Agent Language Propagation (4 hours)

#### Step 3.1: Test Language Context in Phase Manager
```python
# File: backend/tests/test_phase_manager_language.py
"""
Tests for language propagation in phase manager
"""
import pytest
from src.agents.phase_manager import PhaseManager
from src.utils.language_utils import SUPPORTED_LANGUAGES

class TestPhaseManagerLanguage:
    @pytest.fixture
    def phase_manager(self):
        return PhaseManager()
        
    def test_phase_transition_preserves_language(self, phase_manager):
        # Set initial phase with language
        context = {
            "current_phase": "greeting",
            "language": "es-ES",
            "user_id": "test-user"
        }
        
        # Transition to discovery phase
        new_context = phase_manager.transition_phase(
            context, 
            "discovery"
        )
        
        # Language should be preserved
        assert new_context["language"] == "es-ES"
        
    @pytest.mark.parametrize("language_code", SUPPORTED_LANGUAGES.keys())
    def test_all_phases_receive_language(self, phase_manager, language_code):
        phases = ["greeting", "discovery", "reframing", "summary"]
        
        context = {
            "current_phase": phases[0],
            "language": language_code,
            "user_id": "test-user"
        }
        
        for next_phase in phases[1:]:
            context = phase_manager.transition_phase(context, next_phase)
            assert context["language"] == language_code
```

#### Step 3.2: Test Agent Language Instructions
```python
# File: backend/tests/test_agent_language_instructions.py
"""
Tests for agent language instruction generation
"""
import pytest
from src.agents.greeting_agent import create_greeting_agent
from src.agents.discovery_agent import create_discovery_agent
from src.agents.reframing_agent import create_reframing_agent
from src.agents.summary_agent import create_summary_agent

class TestAgentLanguageInstructions:
    def test_greeting_agent_language_instruction(self):
        agent = create_greeting_agent(language_code="es-ES")
        
        # Verify Spanish language instruction is included
        assert "Responde en español" in agent.instructions
        assert "Spanish" in agent.instructions
        
    def test_discovery_agent_language_instruction(self):
        agent = create_discovery_agent(language_code="pt-BR")
        
        # Verify Portuguese language instruction is included
        assert "Responda em português" in agent.instructions
        assert "Portuguese" in agent.instructions
        
    def test_agent_default_language(self):
        agent = create_greeting_agent()  # No language specified
        
        # Should default to English
        assert "Respond in English" in agent.instructions
        
    @pytest.mark.parametrize("agent_factory,phase_name", [
        (create_greeting_agent, "greeting"),
        (create_discovery_agent, "discovery"),
        (create_reframing_agent, "reframing"),
        (create_summary_agent, "summary")
    ])
    def test_all_agents_support_language(self, agent_factory, phase_name):
        # Test each agent with Spanish
        agent = agent_factory(language_code="es-ES")
        
        # All agents should have language instructions
        assert any(
            phrase in agent.instructions 
            for phrase in ["español", "Spanish", "es-ES"]
        )
```

#### Step 3.3: Implement Language Support in Agents
```python
# File: backend/src/agents/base_agent.py
"""
Base agent functionality with language support
"""
from typing import Optional
from src.utils.language_utils import get_default_language

def get_language_instruction(language_code: Optional[str] = None) -> str:
    """Generate language-specific instruction for agents."""
    if not language_code:
        language_code = get_default_language()
        
    language_instructions = {
        "en-US": "Respond in English. Use clear, simple language.",
        "es-ES": "Responde en español. Usa un lenguaje claro y sencillo.",
        "pt-BR": "Responda em português brasileiro. Use linguagem clara e simples.",
        "de-DE": "Antworten Sie auf Deutsch. Verwenden Sie eine klare, einfache Sprache.",
        "fr-FR": "Répondez en français. Utilisez un langage clair et simple.",
        "it-IT": "Rispondi in italiano. Usa un linguaggio chiaro e semplice.",
        "nl-NL": "Antwoord in het Nederlands. Gebruik duidelijke, eenvoudige taal.",
        "pl-PL": "Odpowiadaj po polsku. Używaj jasnego, prostego języka.",
        "hi-IN": "हिंदी में उत्तर दें। स्पष्ट, सरल भाषा का प्रयोग करें।",
        "ja-JP": "日本語で返信してください。明確で簡単な言葉を使ってください。",
        "ko-KR": "한국어로 답변해 주세요. 명확하고 간단한 언어를 사용하세요.",
        "zh-CN": "请用简体中文回复。使用清晰、简单的语言。",
        "zh-TW": "請用繁體中文回覆。使用清晰、簡單的語言。"
    }
    
    return language_instructions.get(language_code, language_instructions["en-US"])
```

```python
# File: backend/src/agents/greeting_agent.py (modifications)
from src.agents.base_agent import get_language_instruction

def create_greeting_agent(
    model: str = "gemini-2.0-flash",
    language_code: Optional[str] = None
) -> LlmAgent:
    """Create a greeting phase agent with language support."""
    
    language_instruction = get_language_instruction(language_code)
    
    greeting_instruction = (
        f"{BASE_CBT_CONTEXT}\n\n"
        f"LANGUAGE REQUIREMENT:\n{language_instruction}\n\n"
        f"You are in the GREETING PHASE. Your tasks:\n"
        f"1. Provide a warm, professional welcome\n"
        f"2. Briefly explain what cognitive reframing is\n"
        f"3. Set expectations about the conversation\n"
        f"4. Ask an open-ended question to understand their situation\n\n"
        f"Remember to respond in the specified language throughout the conversation."
    )
    
    return LlmAgent(
        name="GreetingAgent",
        instructions=greeting_instruction,
        model=model,
    )
```

### Phase 4: Integration Testing (3 hours)

#### Step 4.1: Test Complete Language Flow
```python
# File: backend/tests/integration/test_language_flow.py
"""
Integration tests for complete language flow
"""
import pytest
import asyncio
from httpx import AsyncClient
import json

@pytest.mark.asyncio
class TestLanguageFlowIntegration:
    async def test_spanish_conversation_flow(self, async_client: AsyncClient):
        session_id = "test-spanish-flow"
        
        # Connect with Spanish language
        async with async_client.stream(
            "GET",
            f"/api/events/{session_id}?language=es-ES"
        ) as response:
            # Collect first few messages
            messages = []
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    messages.append(data)
                    if len(messages) >= 3:  # Get greeting
                        break
            
            # Verify greeting is in Spanish
            greeting_content = " ".join(
                msg.get("content", "") for msg in messages
            )
            
            # Should contain Spanish greeting
            assert any(
                spanish_word in greeting_content.lower()
                for spanish_word in ["hola", "bienvenido", "ayudar", "cognitivo"]
            )
            
            # Should NOT contain English greeting
            assert "hello" not in greeting_content.lower()
            assert "welcome" not in greeting_content.lower()
    
    async def test_language_persistence_across_messages(self, async_client: AsyncClient):
        session_id = "test-persistence"
        
        # Start session in Portuguese
        async with async_client.stream(
            "GET",
            f"/api/events/{session_id}?language=pt-BR"
        ) as response:
            # Get initial greeting
            await self._consume_greeting(response)
        
        # Send a message
        message_data = {
            "mime_type": "text/plain",
            "data": "Estou me sentindo ansioso sobre o trabalho"
        }
        
        response = await async_client.post(
            f"/api/send/{session_id}",
            json=message_data
        )
        assert response.status_code == 200
        
        # Reconnect and verify language is maintained
        async with async_client.stream(
            "GET",
            f"/api/events/{session_id}?language=pt-BR"
        ) as response:
            messages = await self._collect_messages(response, count=5)
            
            # All messages should be in Portuguese
            content = " ".join(msg.get("content", "") for msg in messages)
            
            # Check for Portuguese content
            assert any(
                portuguese_word in content.lower()
                for portuguese_word in ["compreendo", "trabalho", "sentir", "vamos"]
            )
    
    async def _consume_greeting(self, response):
        """Helper to consume greeting messages."""
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if data.get("type") == "phase_complete":
                    break
                    
    async def _collect_messages(self, response, count=5):
        """Helper to collect a number of messages."""
        messages = []
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                data = json.loads(line[6:])
                messages.append(data)
                if len(messages) >= count:
                    break
        return messages
```

#### Step 4.2: Test Edge Cases
```python
# File: backend/tests/integration/test_language_edge_cases.py
"""
Edge case tests for language handling
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestLanguageEdgeCases:
    async def test_language_switch_warning(self, async_client: AsyncClient):
        session_id = "test-switch"
        
        # Start in English
        async with async_client.stream(
            "GET",
            f"/api/events/{session_id}?language=en-US"
        ) as response:
            await self._consume_greeting(response)
        
        # Try to reconnect with different language (should warn)
        async with async_client.stream(
            "GET", 
            f"/api/events/{session_id}?language=es-ES"
        ) as response:
            # Should still use original language (English)
            messages = await self._collect_messages(response, count=3)
            content = " ".join(msg.get("content", "") for msg in messages)
            
            # Should remain in English
            assert "hello" in content.lower() or "welcome" in content.lower()
    
    async def test_unsupported_language_fallback(self, async_client: AsyncClient):
        session_id = "test-unsupported"
        
        # Try unsupported language
        async with async_client.stream(
            "GET",
            f"/api/events/{session_id}?language=klingon"
        ) as response:
            messages = await self._collect_messages(response, count=3)
            content = " ".join(msg.get("content", "") for msg in messages)
            
            # Should fallback to English
            assert any(
                english_word in content.lower()
                for english_word in ["hello", "welcome", "help", "cognitive"]
            )
```

### Phase 5: E2E Testing (2 hours)

#### Step 5.1: Create E2E Language Tests
```python
# File: frontend/tests/e2e/language-selection.spec.ts
"""
E2E tests for language selection functionality
"""
import { test, expect } from '@playwright/test'

test.describe('Language Selection', () => {
  test('should start conversation in selected language', async ({ page }) => {
    // Navigate to app
    await page.goto('/')
    
    // Select Spanish from language dropdown
    await page.selectOption('[data-testid="language-selector"]', 'es-ES')
    
    // Start conversation
    await page.click('[data-testid="start-conversation"]')
    
    // Wait for greeting
    const greeting = await page.waitForSelector('[data-testid="message-content"]')
    const greetingText = await greeting.textContent()
    
    // Verify Spanish greeting
    expect(greetingText?.toLowerCase()).toContain('hola')
    expect(greetingText?.toLowerCase()).not.toContain('hello')
  })
  
  test('should maintain language throughout conversation', async ({ page }) => {
    // Navigate and select Portuguese
    await page.goto('/')
    await page.selectOption('[data-testid="language-selector"]', 'pt-BR')
    
    // Start conversation
    await page.click('[data-testid="start-conversation"]')
    
    // Wait for greeting
    await page.waitForSelector('[data-testid="message-content"]')
    
    // Send a message in Portuguese
    await page.fill('[data-testid="thought-input"]', 'Estou preocupado com meu trabalho')
    await page.click('[data-testid="send-button"]')
    
    // Wait for response
    const response = await page.waitForSelector(
      '[data-testid="message-content"]:last-of-type'
    )
    const responseText = await response.textContent()
    
    // Verify response is in Portuguese
    expect(responseText?.toLowerCase()).toMatch(/compreendo|entendo|trabalho/)
  })
})
```

#### Step 5.2: Load Testing for Language
```python
# File: backend/tests/load/test_language_load.py
"""
Load tests for language functionality
"""
import pytest
import asyncio
from httpx import AsyncClient
import random

@pytest.mark.asyncio
async def test_concurrent_multilingual_sessions():
    """Test multiple sessions with different languages concurrently."""
    
    languages = ["en-US", "es-ES", "pt-BR", "de-DE", "fr-FR"]
    session_count = 50
    
    async def create_session(session_id: str, language: str):
        async with AsyncClient(base_url="http://localhost:8000") as client:
            async with client.stream(
                "GET",
                f"/api/events/{session_id}?language={language}"
            ) as response:
                message_count = 0
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        message_count += 1
                        if message_count >= 5:
                            break
                return session_id, language, message_count
    
    # Create sessions concurrently
    tasks = [
        create_session(
            f"load-test-{i}",
            random.choice(languages)
        )
        for i in range(session_count)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Verify all sessions succeeded
    for session_id, language, message_count in results:
        assert message_count >= 5, f"Session {session_id} failed"
```

## Testing Strategy

### Unit Tests
- Language utility functions
- Session language storage
- Agent language instruction generation
- Language validation and normalization

### Integration Tests
- Complete language flow from SSE to agent response
- Language persistence across messages
- Multi-phase language consistency
- Edge cases and error handling

### E2E Tests
- UI language selection to backend response
- Language persistence across reconnections
- Multiple language concurrent sessions

### Performance Tests
- No latency increase from language handling
- Concurrent multilingual session handling

## Implementation Timeline

1. **Day 1: Foundation (4 hours)**
   - Phase 1: Test infrastructure and utilities
   - Phase 2: Session language management

2. **Day 2: Agent Updates (4 hours)**
   - Phase 3: Agent language propagation
   - Update all agent implementations

3. **Day 3: Testing and Polish (4 hours)**
   - Phase 4: Integration testing
   - Phase 5: E2E testing
   - Bug fixes and documentation

## Success Metrics

1. **Test Coverage**: 100% coverage for new language code
2. **Performance**: No measurable latency increase
3. **Reliability**: All E2E tests passing consistently
4. **User Experience**: Immediate language response matching selection

## Rollback Plan

If issues arise:
1. Feature flag to disable language parameter usage
2. Fallback to detection-based approach
3. Clear error messages for unsupported scenarios
4. Monitoring for language-related errors

## Future Enhancements

1. **Dynamic Language Switching**: Allow changing language mid-conversation
2. **Language Auto-Detection**: Detect from browser settings
3. **Partial Language Support**: Graceful degradation for partially supported languages
4. **Language-Specific CBT Techniques**: Culturally adapted therapy approaches