"""Language utilities for consistent language handling."""

from typing import Optional

# Supported languages with their full names
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

# Default language
DEFAULT_LANGUAGE = "en-US"

# Short code mappings
SHORT_CODE_MAPPINGS = {
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


def validate_language_code(language_code: Optional[str]) -> bool:
    """Validate if language code is supported.

    Args:
        language_code: Language code to validate

    Returns:
        True if language is supported, False otherwise
    """
    if not language_code:
        return False
    return language_code in SUPPORTED_LANGUAGES


def normalize_language_code(language_code: Optional[str]) -> str:
    """Normalize language code to standard format.

    Args:
        language_code: Language code to normalize

    Returns:
        Normalized language code in xx-XX format, defaults to en-US
    """
    if not language_code:
        return DEFAULT_LANGUAGE

    # Remove whitespace
    normalized = language_code.strip()

    # Check if it's already a supported language
    if normalized in SUPPORTED_LANGUAGES:
        return normalized

    # Handle short codes
    if normalized.lower() in SHORT_CODE_MAPPINGS:
        return SHORT_CODE_MAPPINGS[normalized.lower()]

    # Try to parse xx-XX format
    if "-" in normalized:
        parts = normalized.split("-")
        if len(parts) == 2:
            formatted = f"{parts[0].lower()}-{parts[1].upper()}"
            if formatted in SUPPORTED_LANGUAGES:
                return formatted

    # If all else fails, return default
    return DEFAULT_LANGUAGE


def get_default_language() -> str:
    """Get default language code.

    Returns:
        Default language code (en-US)
    """
    return DEFAULT_LANGUAGE


def get_language_instruction(language_code: Optional[str] = None) -> str:
    """Generate language-specific instruction for agents.

    Args:
        language_code: Language code for instruction

    Returns:
        Language-specific instruction string
    """
    if not language_code:
        language_code = get_default_language()

    # Language-specific instructions
    language_instructions = {
        "en-US": "Respond in English. Use clear, simple language.",
        "es-ES": "Responde en español. Usa un lenguaje claro y sencillo.",
        "pt-BR": "Responda em português brasileiro. Use linguagem clara e simples.",
        "de-DE": "Antworten Sie auf Deutsch. Verwenden Sie eine klare, einfache Sprache.",
        "fr-FR": "Répondez en français. Utilisez un langage clair et simple.",
        "it-IT": "Rispondi in italiano. Usa un linguaggio chiaro e semplice.",
        "nl-NL": "Antwoord in het Nederlands. Gebruik duidelijke, eenvoudige taal.",
        "pl-PL": "Odpowiadaj po polsku. Używaj jasnego, prostego języka.",
        "hi-IN": "हिंदी में उत्तर दें। स्पष्ट, सरल भाषा का प्रयोग करें।",
        "ja-JP": "日本語で返信してください。明確で簡単な言葉を使ってください。",
        "ko-KR": "한국어로 답변해 주세요. 명확하고 간단한 언어를 사용하세요.",
        "zh-CN": "请用简体中文回复。使用清晰、简单的语言。",
        "zh-TW": "請用繁體中文回覆。使用清晰、簡單的語言。",
    }

    return language_instructions.get(language_code, language_instructions["en-US"])