"""Test fixtures for language testing."""

SUPPORTED_LANGUAGES = {
    "en-US": "English",
    "es-ES": "Spanish",
    "pt-BR": "Portuguese",
    "de-DE": "German",
    "fr-FR": "French",
    "it-IT": "Italian",
    "nl-NL": "Dutch",
    "pl-PL": "Polish",
    "hi-IN": "Hindi",
    "ja-JP": "Japanese",
    "ko-KR": "Korean",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
}

LANGUAGE_TEST_CASES = [
    ("en-US", "Hello! I'm here to help you with cognitive reframing."),
    ("es-ES", "¡Hola! Estoy aquí para ayudarte con el reencuadre cognitivo."),
    ("pt-BR", "Olá! Estou aqui para ajudá-lo com a reestruturação cognitiva."),
    ("de-DE", "Hallo! Ich bin hier, um Ihnen bei der kognitiven Umstrukturierung zu helfen."),
    ("fr-FR", "Bonjour! Je suis ici pour vous aider avec la restructuration cognitive."),
    ("it-IT", "Ciao! Sono qui per aiutarti con la ristrutturazione cognitiva."),
    ("nl-NL", "Hallo! Ik ben hier om je te helpen met cognitieve herstructurering."),
    ("pl-PL", "Cześć! Jestem tutaj, aby pomóc ci w restrukturyzacji poznawczej."),
    ("hi-IN", "नमस्ते! मैं यहाँ संज्ञानात्मक पुनर्रचना में आपकी मदद करने के लिए हूँ।"),
    ("ja-JP", "こんにちは！認知の再構築をお手伝いします。"),
    ("ko-KR", "안녕하세요! 인지 재구성을 도와드리기 위해 여기 있습니다."),
    ("zh-CN", "你好！我在这里帮助您进行认知重构。"),
    ("zh-TW", "你好！我在這裡幫助您進行認知重構。"),
]

# Language-specific greetings that agents should use
AGENT_GREETING_PATTERNS = {
    "en-US": ["hello", "welcome", "help", "cognitive", "reframing"],
    "es-ES": ["hola", "bienvenido", "ayudar", "cognitivo", "reencuadre"],
    "pt-BR": ["olá", "bem-vindo", "ajudar", "cognitiva", "reestruturação"],
    "de-DE": ["hallo", "willkommen", "helfen", "kognitiven", "umstrukturierung"],
    "fr-FR": ["bonjour", "bienvenue", "aider", "cognitive", "restructuration"],
    "it-IT": ["ciao", "benvenuto", "aiutare", "cognitiva", "ristrutturazione"],
    "nl-NL": ["hallo", "welkom", "helpen", "cognitieve", "herstructurering"],
    "pl-PL": ["cześć", "witamy", "pomóc", "poznawczej", "restrukturyzacji"],
    "hi-IN": ["नमस्ते", "स्वागत", "मदद", "संज्ञानात्मक", "पुनर्रचना"],
    "ja-JP": ["こんにちは", "ようこそ", "手伝", "認知", "再構築"],
    "ko-KR": ["안녕하세요", "환영", "도와", "인지", "재구성"],
    "zh-CN": ["你好", "欢迎", "帮助", "认知", "重构"],
    "zh-TW": ["你好", "歡迎", "幫助", "認知", "重構"],
}

# Short language codes mapping
SHORT_LANGUAGE_CODES = {
    "en": "en-US",
    "es": "es-ES",
    "pt": "pt-BR",
    "de": "de-DE",
    "fr": "fr-FR",
    "it": "it-IT",
    "nl": "nl-NL",
    "pl": "pl-PL",
    "hi": "hi-IN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "zh": "zh-CN",
}