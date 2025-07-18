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

"""Tests for the orchestrator crisis check and router agent."""

import pytest
from google.adk.agents import LlmAgent

from src.agents.orchestrator import (
    check_for_crisis,
    create_cbt_orchestrator,
)
from src.knowledge.cbt_context import CRISIS_RESPONSE_TEMPLATE


class TestCheckForCrisis:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("I feel like I want to die", True),
            ("This is okay", False),
            ("Thinking of SUICIDE scares me", True),
        ],
    )
    def test_crisis_detection_flag(self, text, expected):
        result = check_for_crisis(text)
        assert result.get("crisis_detected") is expected

    def test_crisis_response_included(self):
        sample = "I might kill myself"
        result = check_for_crisis(sample)
        assert result.get("crisis_detected")
        assert "support" in result.get("response", "").lower()
        assert CRISIS_RESPONSE_TEMPLATE in result.get("response")


class TestCreateOrchestrator:
    def test_router_agent_structure(self):
        router = create_cbt_orchestrator(model="test-model")
        assert isinstance(router, LlmAgent)
        assert router.name == "CBTRouter"
        tools = {tool.__name__ for tool in router.tools}
        assert "check_for_crisis" in tools
