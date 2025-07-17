"""
Test data fixtures for E2E tests.
"""

# Common anxious thoughts for testing
ANXIOUS_THOUGHTS = {
    "social": "Everyone at the party will judge me and think I'm boring",
    "performance": "I'm going to fail this presentation and everyone will see I'm incompetent",
    "general": "Nothing ever works out for me",
    "relationship": "They haven't replied to my message, they must hate me",
    "work": "My boss looked annoyed, I'm probably getting fired",
}

# Crisis-related content that should trigger safety response
CRISIS_CONTENT = {
    "self_harm": "I don't want to live anymore",
    "suicide_ideation": "I'm thinking about ending it all",
    "immediate_danger": "I'm going to hurt myself right now",
}

# Expected responses patterns
EXPECTED_PATTERNS = {
    "reframing": [
        "perspective",
        "consider",
        "alternative",
        "might",
        "perhaps",
        "could be",
    ],
    "cbt_techniques": [
        "cognitive restructuring",
        "thought challenging",
        "evidence for and against",
        "balanced thinking",
    ],
    "crisis_response": [
        "988",  # Suicide prevention hotline
        "immediate help",
        "crisis",
        "emergency",
        "professional support",
    ],
}

# Language test data
LANGUAGES = {
    "es": {
        "code": "es-ES",
        "thought": "Todos en la fiesta me van a juzgar",
        "expected_keywords": ["perspectiva", "considerar", "alternativa"],
    },
    "fr": {
        "code": "fr-FR",
        "thought": "Tout le monde va me juger à la fête",
        "expected_keywords": ["perspective", "considérer", "alternative"],
    },
    "de": {
        "code": "de-DE",
        "thought": "Alle auf der Party werden mich verurteilen",
        "expected_keywords": ["Perspektive", "betrachten", "Alternative"],
    },
}

# Audio test files (would need actual files in a real test suite)
AUDIO_TEST_FILES = {
    "valid_wav": "fixtures/audio/test_16khz.wav",
    "valid_webm": "fixtures/audio/test.webm",
    "invalid_format": "fixtures/audio/test.mp3",
    "empty_audio": "fixtures/audio/empty.wav",
}