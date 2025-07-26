"""Tests for language propagation to agents."""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.discovery_agent import create_discovery_agent
from src.agents.greeting_agent import create_greeting_agent
from src.agents.reframing_agent import create_reframing_agent
from src.agents.summary_agent import create_summary_agent
from src.utils.language_utils import get_language_instruction
from tests.fixtures.language_fixtures import SUPPORTED_LANGUAGES


class TestAgentLanguageInstructions:
    """Test that all agents properly receive language instruction."""

    def test_greeting_agent_language_instruction(self):
        """Test greeting agent includes language instruction."""
        # Test with Spanish
        agent = create_greeting_agent(language_code="es-ES")
        
        # Check that Spanish instruction is included
        spanish_instruction = get_language_instruction("es-ES")
        assert spanish_instruction in agent.instruction
        assert "Responde en español" in agent.instruction

    def test_discovery_agent_language_instruction(self):
        """Test discovery agent includes language instruction."""
        # Test with Portuguese
        agent = create_discovery_agent(language_code="pt-BR")
        
        # Check that Portuguese instruction is included
        portuguese_instruction = get_language_instruction("pt-BR")
        assert portuguese_instruction in agent.instruction
        assert "Responda em português" in agent.instruction

    def test_reframing_agent_language_instruction(self):
        """Test reframing agent includes language instruction."""
        # Test with German
        agent = create_reframing_agent(language_code="de-DE")
        
        # Check that German instruction is included
        german_instruction = get_language_instruction("de-DE")
        assert german_instruction in agent.instruction
        assert "Antworten Sie auf Deutsch" in agent.instruction

    def test_summary_agent_language_instruction(self):
        """Test summary agent includes language instruction."""
        # Test with French
        agent = create_summary_agent(language_code="fr-FR")
        
        # Check that French instruction is included
        french_instruction = get_language_instruction("fr-FR")
        assert french_instruction in agent.instruction
        assert "Répondez en français" in agent.instruction

    def test_agent_default_language(self):
        """Test agents default to English when no language specified."""
        agents = [
            create_greeting_agent(),
            create_discovery_agent(),
            create_reframing_agent(),
            create_summary_agent(),
        ]
        
        english_instruction = get_language_instruction("en-US")
        for agent in agents:
            assert english_instruction in agent.instruction
            assert "Respond in English" in agent.instruction

    @pytest.mark.parametrize("agent_factory,agent_name", [
        (create_greeting_agent, "greeting"),
        (create_discovery_agent, "discovery"),
        (create_reframing_agent, "reframing"),
        (create_summary_agent, "summary"),
    ])
    def test_all_agents_support_all_languages(self, agent_factory, agent_name):
        """Test that all agents support all languages."""
        for lang_code in SUPPORTED_LANGUAGES:
            agent = agent_factory(language_code=lang_code)
            
            # Get the expected instruction
            expected_instruction = get_language_instruction(lang_code)
            
            # Verify instruction is included
            assert expected_instruction in agent.instruction
            
            # Also verify the agent has phase-specific content
            assert "CBT" in agent.instruction or "cognitive" in agent.instruction


class TestPhaseManagerLanguageHandling:
    """Test that phase manager preserves language across transitions."""

    def test_phase_manager_preserves_language(self):
        """Test that language is preserved when transitioning phases."""
        from src.agents.phase_manager import PhaseManager
        
        phase_manager = PhaseManager()
        
        # Initial context with language
        context = {
            "current_phase": "greeting",
            "language": "es-ES",
            "user_id": "test-user",
            "session_id": "test-session",
        }
        
        # Transition through phases
        phases = ["discovery", "reframing", "summary"]
        
        for next_phase in phases:
            # Transition to next phase
            new_context = phase_manager.transition_to_phase(context, next_phase)
            
            # Verify language is preserved
            assert new_context.get("language") == "es-ES"
            
            # Update context for next iteration
            context = new_context

    def test_phase_manager_handles_missing_language(self):
        """Test phase manager handles context without language."""
        from src.agents.phase_manager import PhaseManager
        
        phase_manager = PhaseManager()
        
        # Context without language
        context = {
            "current_phase": "greeting",
            "user_id": "test-user",
            "session_id": "test-session",
        }
        
        # Transition should not fail
        new_context = phase_manager.transition_to_phase(context, "discovery")
        
        # Language should remain unset (None or missing)
        assert new_context.get("language") is None


class TestOrchestrator:
    """Test orchestrator language handling."""

    @pytest.mark.skip(reason="Orchestrator refactoring needed")
    def test_orchestrator_passes_language_to_agents(self):
        """Test that orchestrator passes language to all phase agents."""
        # This will be implemented when we update the orchestrator
        pass