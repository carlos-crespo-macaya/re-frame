"""Pytest configuration and fixtures."""

import sys
from unittest.mock import Mock

# Mock the ADK imports before they're imported
sys.modules["google.adk"] = Mock()
sys.modules["google.adk.core"] = Mock()
sys.modules["google.adk.core.models"] = Mock()
sys.modules["google.adk.agents"] = Mock()
