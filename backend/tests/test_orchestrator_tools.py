# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the new orchestrator crisis check and session management."""

import pytest

from src.agents.crisis import crisis_scan, safety_message
from src.agents.orchestrator import handle_turn
from src.agents.state import SessionState


class TestCrisisDetection:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("I want to kill myself", True),
            ("I'm going to end it all", True),
            ("I want to harm others", True),
            ("I'm feeling sad", False),
            ("I'm anxious", False),
            ("I'm stressed about work", False),
        ],
    )
    def test_crisis_scan(self, text, expected):
        """Test crisis keyword detection."""
        assert crisis_scan(text) == expected

    def test_safety_message_english(self):
        """Test English safety message."""
        message = safety_message("en")
        assert "safety matters" in message
        assert "immediate help" in message

    def test_safety_message_spanish(self):
        """Test Spanish safety message."""
        message = safety_message("es")
        assert "seguridad importa" in message
        assert "ayuda inmediata" in message


class TestOrchestrator:
    def test_handle_turn_crisis(self):
        """Test that crisis detection triggers safety response."""
        state = SessionState()
        
        # Mock ADK call function
        def mock_adk_call(**kwargs):
            return '<ui>Response</ui><control>{"next_phase":"warmup","missing_fields":[],"suggest_questions":[],"crisis_detected":false}</control>'
        
        # Test crisis detection
        result = handle_turn(state, "I want to kill myself", mock_adk_call)
        
        assert state.crisis_flag is True
        assert state.phase.value == "summary"
        assert "safety matters" in result["ui_text"]

    def test_handle_turn_normal(self):
        """Test normal conversation flow."""
        state = SessionState()
        
        # Mock ADK call function
        def mock_adk_call(**kwargs):
            return '<ui>Hello! What brings you here today?</ui><control>{"next_phase":"clarify","missing_fields":[],"suggest_questions":[],"crisis_detected":false}</control>'
        
        result = handle_turn(state, "I'm feeling anxious", mock_adk_call)
        
        assert state.crisis_flag is False
        assert result["ui_text"] == "Hello! What brings you here today?"
        assert state.turn == 1

    def test_session_state_initialization(self):
        """Test that SessionState initializes correctly."""
        state = SessionState()
        
        assert state.phase.value == "warmup"
        assert state.turn == 0
        assert state.max_turns == 14
        assert state.followups_left == 3
        assert state.crisis_flag is False