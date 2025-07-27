"""E2E tests for language parameter functionality."""

import json
import logging

import pytest
from httpx import AsyncClient

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
class TestLanguageParameterE2E:
    """E2E tests for language parameter propagation."""

    async def test_spanish_conversation_flow(self, test_client: AsyncClient):
        """Test complete Spanish conversation flow."""
        # Create a session
        session_response = await test_client.post("/api/sessions", json={})
        assert session_response.status_code == 200
        session_data = session_response.json()
        session_id = session_data["session_id"]

        # Start SSE connection with Spanish language
        messages = []
        async with test_client.stream(
            "GET", f"/api/events/{session_id}?language=es-ES"
        ) as response:
            # Send initial Spanish message
            await test_client.post(
                f"/api/sessions/{session_id}/messages",
                json={"content": "Hola, necesito ayuda con mis pensamientos"},
            )

            # Collect responses
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "text":
                            messages.append(data["content"])
                    except json.JSONDecodeError:
                        continue

                # Stop after getting greeting
                if len(messages) >= 1:
                    break

        # Verify Spanish greeting
        assert len(messages) > 0
        greeting = messages[0]
        assert "Hola" in greeting or "hola" in greeting
        assert any(
            word in greeting.lower()
            for word in ["ayudarte", "ayudar", "asistente", "cbt"]
        )

        # Verify it's not in English
        assert "Hello" not in greeting
        assert "help" not in greeting.lower()

    async def test_portuguese_conversation_flow(self, test_client: AsyncClient):
        """Test complete Portuguese conversation flow."""
        # Create a session
        session_response = await test_client.post("/api/sessions", json={})
        session_id = session_response.json()["session_id"]

        # Start SSE connection with Portuguese language
        messages = []
        async with test_client.stream(
            "GET", f"/api/events/{session_id}?language=pt-BR"
        ) as response:
            # Send initial Portuguese message
            await test_client.post(
                f"/api/sessions/{session_id}/messages",
                json={"content": "Olá, preciso de ajuda"},
            )

            # Collect responses
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "text":
                            messages.append(data["content"])
                    except json.JSONDecodeError:
                        continue

                if len(messages) >= 1:
                    break

        # Verify Portuguese greeting
        assert len(messages) > 0
        greeting = messages[0]
        assert "Olá" in greeting or "olá" in greeting
        assert any(word in greeting.lower() for word in ["ajudar", "assistente", "cbt"])

    async def test_language_normalization(self, test_client: AsyncClient):
        """Test that language codes are normalized."""
        # Create a session
        session_response = await test_client.post("/api/sessions", json={})
        session_id = session_response.json()["session_id"]

        # Test lowercase language code
        messages = []
        async with test_client.stream(
            "GET", f"/api/events/{session_id}?language=es"  # lowercase, no region
        ) as response:
            await test_client.post(
                f"/api/sessions/{session_id}/messages", json={"content": "Hola"}
            )

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "text":
                            messages.append(data["content"])
                    except json.JSONDecodeError:
                        continue

                if len(messages) >= 1:
                    break

        # Should still get Spanish response
        assert len(messages) > 0
        greeting = messages[0]
        assert "Hola" in greeting or "hola" in greeting

    async def test_invalid_language_fallback(self, test_client: AsyncClient):
        """Test fallback to English for invalid languages."""
        # Create a session
        session_response = await test_client.post("/api/sessions", json={})
        session_id = session_response.json()["session_id"]

        # Test invalid language code
        messages = []
        async with test_client.stream(
            "GET", f"/api/events/{session_id}?language=klingon"
        ) as response:
            await test_client.post(
                f"/api/sessions/{session_id}/messages", json={"content": "Hello"}
            )

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "text":
                            messages.append(data["content"])
                    except json.JSONDecodeError:
                        continue

                if len(messages) >= 1:
                    break

        # Should get English response
        assert len(messages) > 0
        greeting = messages[0]
        assert "Hello" in greeting or "Hi" in greeting
        assert "help" in greeting.lower()

    async def test_language_persistence_across_phases(self, test_client: AsyncClient):
        """Test that language persists across conversation phases."""
        # Create a session
        session_response = await test_client.post("/api/sessions", json={})
        session_id = session_response.json()["session_id"]

        # Start Spanish conversation
        messages = []
        async with test_client.stream(
            "GET", f"/api/events/{session_id}?language=es-ES"
        ) as response:
            # Greeting phase
            await test_client.post(
                f"/api/sessions/{session_id}/messages",
                json={"content": "Hola, quiero trabajar en mis pensamientos"},
            )

            # Collect greeting
            greeting_collected = False
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "text":
                            messages.append(data["content"])
                            greeting_collected = True
                    except json.JSONDecodeError:
                        continue

                if greeting_collected:
                    break

            # Move to discovery phase
            await test_client.post(
                f"/api/sessions/{session_id}/messages",
                json={"content": "Sí, estoy listo"},
            )

            # Collect discovery response
            discovery_collected = False
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "text":
                            messages.append(data["content"])
                            discovery_collected = True
                    except json.JSONDecodeError:
                        continue

                if discovery_collected and len(messages) >= 2:
                    break

        # Verify all responses are in Spanish
        assert len(messages) >= 2
        for message in messages:
            # Should not contain common English CBT terms
            assert not any(
                word in message.lower()
                for word in ["thought", "feeling", "emotion", "reframe", "hello"]
            )
            # Should contain Spanish indicators
            assert any(
                char in message for char in ["á", "é", "í", "ó", "ú", "ñ", "¿", "¡"]
            )

    @pytest.mark.parametrize(
        "language_code,expected_greeting",
        [
            ("es-ES", ["hola", "ayudar"]),
            ("pt-BR", ["olá", "ajudar"]),
            ("fr-FR", ["bonjour", "aider"]),
            ("de-DE", ["hallo", "helfen"]),
            ("it-IT", ["ciao", "aiutare"]),
            ("ja-JP", ["こんにちは", "助け"]),
            ("ko-KR", ["안녕하세요", "도움"]),
            ("zh-CN", ["你好", "帮助"]),
            ("ru-RU", ["привет", "помочь"]),
            ("ar-SA", ["مرحبا", "مساعدة"]),
            ("hi-IN", ["नमस्ते", "मदद"]),
            ("nl-NL", ["hallo", "helpen"]),
            ("pl-PL", ["cześć", "pomóc"]),
        ],
    )
    async def test_all_supported_languages(
        self, test_client: AsyncClient, language_code: str, expected_greeting: list[str]
    ):
        """Test that all supported languages work correctly."""
        # Create a session
        session_response = await test_client.post("/api/sessions", json={})
        session_id = session_response.json()["session_id"]

        # Start conversation in specified language
        messages = []
        async with test_client.stream(
            "GET", f"/api/events/{session_id}?language={language_code}"
        ) as response:
            await test_client.post(
                f"/api/sessions/{session_id}/messages", json={"content": "Hello"}
            )

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data["type"] == "text":
                            messages.append(data["content"])
                    except json.JSONDecodeError:
                        continue

                if len(messages) >= 1:
                    break

        # Verify response is in expected language
        assert len(messages) > 0
        greeting = messages[0].lower()

        # Check for language-specific indicators
        assert any(indicator in greeting for indicator in expected_greeting)
