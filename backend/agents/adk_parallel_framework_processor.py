"""Parallel framework processing extension for ADKSessionManager."""

import asyncio
from typing import Any

from agents.adk_base import ADKReFrameAgent


class ParallelFrameworkProcessor:
    """Mixin for parallel framework processing capabilities."""

    async def run_frameworks_parallel(
        self,
        framework_names: list[str],
        intake_data: dict[str, Any],
        session_id: str | None = None,
        timeout: float = 2.0,
    ) -> dict[str, dict[str, Any]]:
        """
        Run multiple frameworks in parallel and aggregate results.
        
        Args:
            framework_names: List of framework names to execute
            intake_data: Input data for frameworks
            session_id: Optional session ID for tracking
            timeout: Maximum time for each framework execution
            
        Returns:
            Dict mapping framework names to their outputs
        """
        if not framework_names:
            return {}
            
        # Get the framework agents
        framework_agents = self.get_framework_agents(framework_names)
        
        # Handle crisis prioritization
        if intake_data.get("is_crisis"):
            # Ensure DBT runs first if it's in the list
            if "DBT" in framework_agents:
                # Run DBT first, then others
                dbt_result = await self._run_single_framework(
                    "DBT", framework_agents["DBT"], intake_data, timeout
                )
                
                # Run remaining frameworks
                remaining_frameworks = {k: v for k, v in framework_agents.items() if k != "DBT"}
                other_results = await self._run_frameworks_batch(
                    remaining_frameworks, intake_data, timeout
                )
                
                # Combine results
                results = {"DBT": dbt_result} if dbt_result else {}
                results.update(other_results)
                return results
        
        # Normal parallel execution
        return await self._run_frameworks_batch(framework_agents, intake_data, timeout)

    async def _run_frameworks_batch(
        self,
        framework_agents: dict[str, ADKReFrameAgent],
        intake_data: dict[str, Any],
        timeout: float,
    ) -> dict[str, dict[str, Any]]:
        """Run a batch of frameworks in parallel."""
        tasks = []
        
        for name, agent in framework_agents.items():
            task = asyncio.create_task(
                self._run_single_framework(name, agent, intake_data, timeout)
            )
            tasks.append((name, task))
        
        # Wait for all tasks with timeout
        results = {}
        for name, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=timeout)
                if result:
                    results[name] = result
            except asyncio.TimeoutError:
                # Log timeout but continue
                continue
            except Exception:
                # Log error but continue with other frameworks
                continue
        
        return results

    async def _run_single_framework(
        self,
        framework_name: str,
        agent: ADKReFrameAgent,
        intake_data: dict[str, Any],
        timeout: float,
    ) -> dict[str, Any] | None:
        """Run a single framework with error handling."""
        try:
            result = await asyncio.wait_for(
                agent.process_with_transparency(intake_data),
                timeout=timeout
            )
            
            if result.success and result.response:
                return {
                    "success": True,
                    "framework": framework_name,
                    "response": result.response,
                    "reframed_thought": result.response,  # Compatibility
                    "transparency_data": result.transparency_data,
                    **self._extract_framework_output(result),
                }
            return None
            
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None

    def _extract_framework_output(self, result: Any) -> dict[str, Any]:
        """Extract standard framework output fields."""
        output = {}
        
        # Try to extract from transparency data if available
        if hasattr(result, "transparency_data") and result.transparency_data:
            td = result.transparency_data
            if hasattr(td, "reasoning_path"):
                output["reasoning_path"] = td.reasoning_path
            if hasattr(td, "techniques_used"):
                output["techniques_applied"] = td.techniques_used
                
        return output

    def get_framework_agents(self, framework_names: list[str]) -> dict[str, ADKReFrameAgent]:
        """Get framework agents by name."""
        available_agents = {}
        
        if hasattr(self, "framework_agents"):
            for name in framework_names:
                if name in self.framework_agents:
                    available_agents[name] = self.framework_agents[name]
                    
        return available_agents