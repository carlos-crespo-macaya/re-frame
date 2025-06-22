"""Mock session manager for API testing."""

from typing import Any


class MockSessionManager:
    """Mock ADK session manager for testing."""
    
    def __init__(self):
        self.sessions = {}
        self.process_calls = []
    
    async def process_user_input(self, thought: str) -> dict[str, Any]:
        """Mock process user input."""
        self.process_calls.append(thought)
        
        # Mock different responses based on input
        if "crisis" in thought.lower() or "hurt myself" in thought.lower():
            return {
                "success": True,
                "crisis_flag": True,
                "response": "Crisis support message",
                "transparency": {"crisis_detected": True},
            }
        
        if len(thought) < 10:
            return {
                "success": False,
                "error": "Failed to process thought",
                "workflow_stage": "intake",
            }
        
        # Normal response
        return {
            "success": True,
            "response": '{"main_response": "Here\'s a different way to think about it..."}',
            "transparency": {
                "techniques_applied": ["cognitive_restructuring", "decatastrophizing"],
                "reasoning_path": ["Identified pattern", "Applied technique"],
            },
            "workflow_stage": "synthesis",
        }
    
    def get_session_history(self, session_id: str) -> dict[str, Any] | None:
        """Mock get session history."""
        if session_id == "test-123":
            return {
                "session_id": session_id,
                "created_at": "2024-01-01T00:00:00",
                "last_activity": "2024-01-01T01:00:00",
                "interactions": [
                    {
                        "timestamp": "2024-01-01T00:00:00",
                        "thought": "Test thought",
                        "response": "Test response",
                        "techniques_used": ["test_technique"],
                    }
                ],
            }
        return None


class MockObservabilityManager:
    """Mock observability manager for testing."""
    
    def __init__(self):
        self.debug_enabled = False
    
    def get_performance_summary(self) -> dict[str, Any]:
        """Mock performance summary."""
        return {
            "avg_response_time": 0.5,
            "p95_response_time": 1.0,
            "p99_response_time": 2.0,
            "total_requests": 100,
            "success_rate": 0.95,
            "error_rate": 0.05,
            "requests_per_minute": 10.0,
            "active_sessions": 5,
            "cache_hit_rate": 0.8,
        }
    
    def get_error_analysis(self) -> dict[str, Any]:
        """Mock error analysis."""
        return {
            "total_errors": 5,
            "error_rate": 0.05,
            "errors_by_type": {
                "validation": 2,
                "timeout": 1,
                "internal": 2,
            },
            "common_errors": [
                {"error": "Validation failed", "count": 2, "percentage": 0.4},
            ],
            "error_trend": "stable",
        }
    
    def enable_debug_mode(self):
        """Enable debug mode."""
        self.debug_enabled = True
    
    def disable_debug_mode(self):
        """Disable debug mode."""
        self.debug_enabled = False