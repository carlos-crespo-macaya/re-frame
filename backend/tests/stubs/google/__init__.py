"""Test stub for Google modules to avoid import errors in tests."""


# Mock the google namespace directly on the module
class adk:  # noqa: N801
    """Mock ADK module."""

    class agents:  # noqa: N801
        """Mock agents module."""

        pass


class genai:  # noqa: N801
    """Mock GenAI module."""

    pass


class cloud:  # noqa: N801
    """Mock Cloud module."""

    class speech:  # noqa: N801
        """Mock speech module."""

        pass

    class texttospeech:  # noqa: N801
        """Mock text-to-speech module."""

        pass


__all__ = ["adk", "cloud", "genai"]
