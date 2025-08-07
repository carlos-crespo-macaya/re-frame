"""Test fixtures for language testing."""

SUPPORTED_LANGUAGES = {
    "en-US": "English",
    "es-ES": "Spanish",
}

LANGUAGE_TEST_CASES = [
    ("en-US", "Hello! I'm here to help you with cognitive reframing."),
    ("es-ES", "¡Hola! Estoy aquí para ayudarte con el reencuadre cognitivo."),
]

# Language-specific greetings that agents should use
AGENT_GREETING_PATTERNS = {
    "en-US": ["hello", "welcome", "help", "cognitive", "reframing"],
    "es-ES": ["hola", "bienvenido", "ayudar", "cognitivo", "reencuadre"],
}

# Short language codes mapping
SHORT_LANGUAGE_CODES = {
    "en": "en-US",
    "es": "es-ES",
}
