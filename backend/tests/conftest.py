"""Pytest configuration and fixtures."""

import sys
from unittest.mock import Mock

# Mock the ADK imports before they're imported
sys.modules['google.adk'] = Mock()
sys.modules['google.adk.core'] = Mock()
sys.modules['google.adk.core.models'] = Mock()
sys.modules['google.adk.agents'] = Mock()

# Create mock classes
class MockADKSessionManager:
    """Mock ADK session manager."""
    
    def __init__(self):
        self.sessions = {}
    
    async def process_user_input(self, thought: str):
        """Mock process method."""
        if "crisis" in thought.lower():
            return {
                "success": True,
                "crisis_flag": True,
                "response": "Crisis support message",
                "transparency": {"crisis_detected": True},
            }
        
        return {
            "success": True,
            "response": '{"main_response": "Reframed thought"}',
            "transparency": {
                "techniques_applied": ["cognitive_restructuring"],
                "reasoning_path": ["Step 1", "Step 2"],
            },
        }
    
    def get_session_history(self, session_id: str):
        """Mock session history."""
        if session_id == "test-123":
            return {
                "session_id": session_id,
                "created_at": "2024-01-01T00:00:00",
                "interactions": [],
            }
        return None


class MockObservabilityManager:
    """Mock observability manager."""
    
    def get_performance_summary(self):
        return {"avg_response_time": 0.5, "total_requests": 100}
    
    def get_error_analysis(self):
        return {"error_rate": 0.02, "common_errors": []}
    
    def enable_debug_mode(self):
        pass
    
    def disable_debug_mode(self):
        pass


# Patch the agents module
mock_agents = Mock()
mock_agents.ADKSessionManager = MockADKSessionManager
mock_agents.observability_manager = MockObservabilityManager()

sys.modules['agents'] = mock_agents