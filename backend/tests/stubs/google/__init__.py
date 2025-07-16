"""Test stub for Google modules to avoid import errors in tests."""

# Mock the google namespace directly on the module
class adk:
    """Mock ADK module."""
    
    class agents:
        """Mock agents module."""
        pass


class genai:
    """Mock GenAI module."""
    pass


class cloud:
    """Mock Cloud module."""
    
    class speech:
        """Mock speech module."""
        pass
    
    class texttospeech:
        """Mock text-to-speech module."""
        pass


__all__ = ['adk', 'genai', 'cloud']