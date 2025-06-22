"""Tests for ADKSessionManager parallel framework processing."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agents.adk_session_manager import ADKSessionManager


class TestADKParallelFrameworkProcessing:
    """Test parallel framework processing capabilities."""

    @pytest.fixture
    def mock_framework_agents(self):
        """Create mock framework agents."""
        agents = {
            "CBT": Mock(),
            "DBT": Mock(),
            "ACT": Mock(),
            "Stoicism": Mock(),
        }
        
        # Set up async process methods
        for name, agent in agents.items():
            agent.process_with_transparency = AsyncMock()
            agent.name = name
            
        return agents

    @pytest.fixture
    def session_manager(self, mock_framework_agents):
        """Create ADKSessionManager with mock agents."""
        with patch.object(ADKSessionManager, "_initialize_agents"):
            manager = ADKSessionManager()
            manager.framework_agents = mock_framework_agents
            return manager

    @pytest.mark.asyncio
    async def test_parallel_framework_execution(self, session_manager, mock_framework_agents):
        """Test frameworks execute in parallel."""
        # Set up different delays to verify parallel execution
        async def delayed_response(delay, framework):
            await asyncio.sleep(delay)
            return {
                "framework": framework,
                "reframed_thought": f"{framework} reframing",
                "techniques_applied": [f"{framework.lower()}_technique"],
            }
        
        mock_framework_agents["CBT"].process_with_transparency.side_effect = lambda x: delayed_response(0.1, "CBT")
        mock_framework_agents["DBT"].process_with_transparency.side_effect = lambda x: delayed_response(0.2, "DBT")
        mock_framework_agents["ACT"].process_with_transparency.side_effect = lambda x: delayed_response(0.1, "ACT")

        # Execute frameworks in parallel
        frameworks_to_run = ["CBT", "DBT", "ACT"]
        intake_data = {"original_thought": "Test thought", "emotion_intensity": 7}
        
        # Time the execution
        import time
        start = time.time()
        
        results = await session_manager.run_frameworks_parallel(
            frameworks_to_run,
            intake_data
        )
        
        elapsed = time.time() - start
        
        # Should take ~0.2s (max delay) not 0.4s (sum of delays)
        assert elapsed < 0.3  # Some buffer for execution overhead
        assert len(results) == 3
        assert all(framework in results for framework in frameworks_to_run)

    @pytest.mark.asyncio
    async def test_handles_framework_failures_gracefully(self, session_manager, mock_framework_agents):
        """Test parallel execution continues despite individual failures."""
        # CBT succeeds
        mock_framework_agents["CBT"].process_with_transparency.return_value = {
            "success": True,
            "response": "CBT response",
            "framework": "CBT",
        }
        
        # DBT fails
        mock_framework_agents["DBT"].process_with_transparency.side_effect = Exception("DBT failed")
        
        # ACT succeeds
        mock_framework_agents["ACT"].process_with_transparency.return_value = {
            "success": True,
            "response": "ACT response",
            "framework": "ACT",
        }
        
        results = await session_manager.run_frameworks_parallel(
            ["CBT", "DBT", "ACT"],
            {"original_thought": "Test"}
        )
        
        # Should have results from successful frameworks
        assert len(results) == 2
        assert "CBT" in results
        assert "ACT" in results
        assert "DBT" not in results

    @pytest.mark.asyncio
    async def test_respects_framework_timeout(self, session_manager, mock_framework_agents):
        """Test framework timeout is enforced in parallel execution."""
        # Set up a framework that takes too long
        async def slow_framework():
            await asyncio.sleep(5)  # Way too long
            return {"framework": "CBT"}
        
        mock_framework_agents["CBT"].process_with_transparency.side_effect = slow_framework
        mock_framework_agents["DBT"].process_with_transparency.return_value = {
            "framework": "DBT",
            "response": "Quick response"
        }
        
        # Set a reasonable timeout
        session_manager.framework_timeout = 1.0
        
        results = await session_manager.run_frameworks_parallel(
            ["CBT", "DBT"],
            {"original_thought": "Test"},
            timeout=1.0
        )
        
        # Should only have DBT result
        assert len(results) == 1
        assert "DBT" in results
        assert "CBT" not in results

    @pytest.mark.asyncio
    async def test_crisis_framework_prioritization(self, session_manager, mock_framework_agents):
        """Test DBT runs first in crisis situations."""
        execution_order = []
        
        async def track_execution(framework):
            execution_order.append(framework)
            return {"framework": framework}
        
        for name, agent in mock_framework_agents.items():
            agent.process_with_transparency.side_effect = lambda x, fw=name: track_execution(fw)
        
        # Crisis situation
        intake_data = {
            "original_thought": "Crisis thought",
            "emotion_intensity": 10,
            "is_crisis": True
        }
        
        await session_manager.run_frameworks_parallel(
            ["CBT", "DBT", "ACT"],
            intake_data
        )
        
        # DBT should be first in execution order
        assert execution_order[0] == "DBT"

    @pytest.mark.asyncio
    async def test_framework_result_aggregation(self, session_manager, mock_framework_agents):
        """Test results are properly aggregated from parallel execution."""
        mock_framework_agents["CBT"].process_with_transparency.return_value = {
            "success": True,
            "reframed_thought": "CBT reframing",
            "techniques_applied": ["thought_challenging"],
            "reasoning_path": ["Identified distortion", "Challenged thought"],
        }
        
        mock_framework_agents["ACT"].process_with_transparency.return_value = {
            "success": True,
            "reframed_thought": "ACT reframing",
            "techniques_applied": ["acceptance", "defusion"],
            "reasoning_path": ["Acknowledged feeling", "Created space"],
        }
        
        results = await session_manager.run_frameworks_parallel(
            ["CBT", "ACT"],
            {"original_thought": "Test thought"}
        )
        
        # Results should be keyed by framework
        assert results["CBT"]["reframed_thought"] == "CBT reframing"
        assert results["ACT"]["reframed_thought"] == "ACT reframing"
        assert len(results["CBT"]["techniques_applied"]) == 1
        assert len(results["ACT"]["techniques_applied"]) == 2

    @pytest.mark.asyncio
    async def test_parallel_execution_with_session_tracking(self, session_manager):
        """Test session data is maintained during parallel execution."""
        session_id = "test-session-123"
        session = session_manager.get_session(session_id)
        
        # Add some initial context
        session.context["user_preferences"] = {"preferred_framework": "ACT"}
        session.conversation_history.append({
            "role": "user",
            "content": "Previous interaction"
        })
        
        # Mock framework execution
        for agent in session_manager.framework_agents.values():
            agent.process_with_transparency.return_value = {
                "success": True,
                "framework": agent.name
            }
        
        results = await session_manager.run_frameworks_parallel(
            ["CBT", "ACT"],
            {"original_thought": "New thought"},
            session_id=session_id
        )
        
        # Session should be updated
        updated_session = session_manager.get_session(session_id)
        assert len(updated_session.conversation_history) > 1
        assert updated_session.context["user_preferences"]["preferred_framework"] == "ACT"

    def test_get_framework_agents(self, session_manager):
        """Test retrieving specific framework agents."""
        agents = session_manager.get_framework_agents(["CBT", "DBT"])
        
        assert len(agents) == 2
        assert "CBT" in agents
        assert "DBT" in agents
        assert "ACT" not in agents

    @pytest.mark.asyncio
    async def test_empty_framework_list_handling(self, session_manager):
        """Test handling of empty framework list."""
        results = await session_manager.run_frameworks_parallel(
            [],
            {"original_thought": "Test"}
        )
        
        assert results == {}

    @pytest.mark.asyncio
    async def test_nonexistent_framework_handling(self, session_manager):
        """Test handling of non-existent framework names."""
        results = await session_manager.run_frameworks_parallel(
            ["CBT", "NonExistentFramework"],
            {"original_thought": "Test"}
        )
        
        # Should only process valid framework
        assert len(results) == 1
        assert "CBT" in results