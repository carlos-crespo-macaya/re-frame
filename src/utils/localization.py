"""Localization system for multi-language support."""

from typing import Any, ClassVar


class Localizer:
    """Handles localization of prompts and system messages."""

    TRANSLATIONS: ClassVar[dict[str, dict[str, Any]]] = {
        "en": {
            "greeting": {
                "welcome": "Welcome! I'm here to help you reframe negative thoughts using CBT techniques.",
                "disclaimer": "Please note that I'm not a replacement for professional therapy.",
                "prompt": "What's on your mind today?",
            },
            "discovery": {
                "intro": "I'd like to understand more about what you're experiencing.",
                "questions": {
                    "situation": "Can you tell me more about the situation?",
                    "emotions": "How are you feeling about this?",
                    "thoughts": "What thoughts are going through your mind?",
                    "impact": "How is this affecting your daily life?",
                },
                "acknowledgment": "Thank you for sharing that with me.",
            },
            "reframing": {
                "intro": "Let's explore different ways to look at this situation.",
                "distortions": {
                    "all-or-nothing": "All-or-Nothing Thinking",
                    "overgeneralization": "Overgeneralization",
                    "catastrophizing": "Catastrophizing",
                    "mind-reading": "Mind Reading",
                    "fortune-telling": "Fortune Telling",
                    "personalization": "Personalization",
                },
                "reframe_prompt": "Here's an alternative way to think about this:",
            },
            "summary": {
                "intro": "Here's a summary of our conversation:",
                "thought_patterns": "Thought Patterns Identified:",
                "reframes": "Alternative Perspectives:",
                "resources": "Additional Resources:",
                "closing": "Remember, changing thought patterns takes practice. Be patient with yourself.",
            },
            "crisis": {
                "detected": "I notice you might be going through a really difficult time.",
                "resources": "Please consider reaching out to these crisis resources:",
                "immediate_help": "If you need immediate help, please contact:",
            },
            "errors": {
                "general": "I apologize, but I encountered an error. Please try again.",
                "pdf_generation": "I couldn't generate the PDF summary, but here's your text summary:",
            },
        },
        "es": {
            "greeting": {
                "welcome": "¡Bienvenido! Estoy aquí para ayudarte a reformular pensamientos negativos usando técnicas de TCC.",
                "disclaimer": "Por favor, ten en cuenta que no soy un reemplazo para la terapia profesional.",
                "prompt": "¿Qué tienes en mente hoy?",
            },
            "discovery": {
                "intro": "Me gustaría entender más sobre lo que estás experimentando.",
                "questions": {
                    "situation": "¿Puedes contarme más sobre la situación?",
                    "emotions": "¿Cómo te sientes al respecto?",
                    "thoughts": "¿Qué pensamientos pasan por tu mente?",
                    "impact": "¿Cómo está afectando esto tu vida diaria?",
                },
                "acknowledgment": "Gracias por compartir eso conmigo.",
            },
            "reframing": {
                "intro": "Exploremos diferentes formas de ver esta situación.",
                "distortions": {
                    "all-or-nothing": "Pensamiento de Todo o Nada",
                    "overgeneralization": "Sobregeneralización",
                    "catastrophizing": "Catastrofización",
                    "mind-reading": "Lectura de Mente",
                    "fortune-telling": "Adivinación del Futuro",
                    "personalization": "Personalización",
                },
                "reframe_prompt": "Aquí hay una forma alternativa de pensar sobre esto:",
            },
            "summary": {
                "intro": "Aquí está el resumen de nuestra conversación:",
                "thought_patterns": "Patrones de Pensamiento Identificados:",
                "reframes": "Perspectivas Alternativas:",
                "resources": "Recursos Adicionales:",
                "closing": "Recuerda, cambiar los patrones de pensamiento requiere práctica. Sé paciente contigo mismo.",
            },
            "crisis": {
                "detected": "Noto que podrías estar pasando por un momento muy difícil.",
                "resources": "Por favor, considera contactar estos recursos de crisis:",
                "immediate_help": "Si necesitas ayuda inmediata, por favor contacta:",
            },
            "errors": {
                "general": "Lo siento, pero encontré un error. Por favor, inténtalo de nuevo.",
                "pdf_generation": "No pude generar el resumen en PDF, pero aquí está tu resumen en texto:",
            },
        },
    }

    @classmethod
    def get(
        cls, language: str, key_path: str, default: str | None = None
    ) -> str | None:
        """
        Get a localized string for the given language and key path.

        Args:
            language: Language code (e.g., 'en', 'es')
            key_path: Dot-separated path to the translation (e.g., 'greeting.welcome')
            default: Default value if translation not found

        Returns:
            The localized string or default value
        """
        if language not in cls.TRANSLATIONS:
            language = "en"  # Fallback to English

        translation_dict = cls.TRANSLATIONS[language]
        keys = key_path.split(".")

        try:
            result: Any = translation_dict
            for key in keys:
                result = result[key]
            if isinstance(result, str):
                return result
            return default
        except (KeyError, TypeError):
            # If key not found, try English as fallback
            if language != "en":
                return cls.get("en", key_path, default)
            return default

    @classmethod
    def get_all(cls, language: str, prefix: str) -> dict[str, Any]:
        """
        Get all translations under a given prefix.

        Args:
            language: Language code
            prefix: Dot-separated prefix path

        Returns:
            Dictionary of all translations under the prefix
        """
        # Special handling for get_all - we need to navigate to the prefix
        # and return the dictionary at that location
        if language not in cls.TRANSLATIONS:
            language = "en"  # Fallback to English

        translation_dict = cls.TRANSLATIONS[language]
        keys = prefix.split(".")

        try:
            result: Any = translation_dict
            for key in keys:
                result = result[key]
            if isinstance(result, dict):
                return result
            return {}
        except (KeyError, TypeError):
            # If key not found, try English as fallback
            if language != "en":
                return cls.get_all("en", prefix)
            return {}

    @classmethod
    def format(cls, language: str, key_path: str, **kwargs) -> str:
        """
        Get a localized string and format it with the given arguments.

        Args:
            language: Language code
            key_path: Dot-separated path to the translation
            **kwargs: Format arguments

        Returns:
            The formatted localized string
        """
        template = cls.get(language, key_path, "")
        if template:
            return template.format(**kwargs)
        return ""

    @classmethod
    def get_crisis_resources(cls, language: str) -> dict[str, str]:
        """Get crisis resources localized for the given language."""
        if language == "es":
            return {
                "Línea Nacional de Prevención del Suicidio": "988",
                "Línea de Crisis por Texto": "Envía 'AYUDA' al 741741",
                "Emergencias": "911",
            }
        else:  # Default to English
            return {
                "National Suicide Prevention Lifeline": "988",
                "Crisis Text Line": "Text HOME to 741741",
                "Emergency Services": "911",
            }
