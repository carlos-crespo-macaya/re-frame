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

"""Tests for the PhaseManager and phase transition utilities."""

import pytest

from src.agents.phase_manager import (
    ConversationPhase,
    PhaseManager,
    check_phase_transition,
    get_current_phase_info,
)


class TestPhaseManager:
    @pytest.mark.parametrize(
        "state,expected",
        [
            ({}, ConversationPhase.GREETING),
            ({"phase": "discovery"}, ConversationPhase.DISCOVERY),
            ({"phase": "invalid"}, ConversationPhase.GREETING),
        ],
    )
    def test_get_current_phase(self, state, expected):
        assert PhaseManager.get_current_phase(state) is expected

    @pytest.mark.parametrize(
        "current,target,can",
        [
            (ConversationPhase.GREETING, ConversationPhase.DISCOVERY, True),
            (ConversationPhase.DISCOVERY, ConversationPhase.SUMMARY, False),
            (ConversationPhase.SUMMARY, ConversationPhase.GREETING, False),
        ],
    )
    def test_can_transition_to(self, current, target, can):
        assert PhaseManager.can_transition_to(current, target) is can

    @pytest.mark.parametrize(
        "phase",
        list(ConversationPhase),
    )
    def test_get_phase_instruction(self, phase):
        instr = PhaseManager.get_phase_instruction(phase)
        assert (
            isinstance(instr, str) and instr.strip()
        ), f"Instruction missing for {phase}"


class TestPhaseTools:
    @pytest.mark.parametrize(
        "target,valid",
        [
            ("greeting", True),
            ("reframing", True),
            ("unknown", False),
        ],
    )
    def test_check_phase_transition(self, target, valid):
        result = check_phase_transition(target)
        if valid:
            assert result.get("status") == "success"
            assert result.get("target_phase") == target
        else:
            assert result.get("status") == "error"
            assert "Invalid phase" in result.get("message", "")

    def test_get_current_phase_info(self):
        info = get_current_phase_info()
        assert info.get("status") == "success"
        flow = info.get("phase_flow")
        assert isinstance(flow, dict)
        for p in ["greeting", "discovery", "reframing", "summary"]:
            assert p in flow and "next_phases" in flow[p]
