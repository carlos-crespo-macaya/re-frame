"""Tests for localization functionality."""

import pytest

from src.utils.localization import Localizer


class TestLocalizer:
    """Test suite for Localizer class."""

    def test_get_english_translations(self):
        """Test getting English translations."""
        # Test greeting messages
        assert (
            Localizer.get("en", "greeting.welcome")
            == "Welcome! I'm here to help you reframe negative thoughts using CBT techniques."
        )
        assert (
            Localizer.get("en", "greeting.disclaimer")
            == "Please note that I'm not a replacement for professional therapy."
        )
        assert Localizer.get("en", "greeting.prompt") == "What's on your mind today?"

    def test_get_spanish_translations(self):
        """Test getting Spanish translations."""
        # Test greeting messages
        assert (
            Localizer.get("es", "greeting.welcome")
            == "¡Bienvenido! Estoy aquí para ayudarte a reformular pensamientos negativos usando técnicas de TCC."
        )
        assert (
            Localizer.get("es", "greeting.disclaimer")
            == "Por favor, ten en cuenta que no soy un reemplazo para la terapia profesional."
        )
        assert Localizer.get("es", "greeting.prompt") == "¿Qué tienes en mente hoy?"

    def test_get_nested_translations(self):
        """Test getting nested translations."""
        # English discovery questions
        assert (
            Localizer.get("en", "discovery.questions.situation")
            == "Can you tell me more about the situation?"
        )
        assert (
            Localizer.get("en", "discovery.questions.emotions")
            == "How are you feeling about this?"
        )

        # Spanish discovery questions
        assert (
            Localizer.get("es", "discovery.questions.situation")
            == "¿Puedes contarme más sobre la situación?"
        )
        assert (
            Localizer.get("es", "discovery.questions.emotions")
            == "¿Cómo te sientes al respecto?"
        )

    def test_get_distortion_names(self):
        """Test getting cognitive distortion names."""
        # English distortions
        assert (
            Localizer.get("en", "reframing.distortions.all-or-nothing")
            == "All-or-Nothing Thinking"
        )
        assert (
            Localizer.get("en", "reframing.distortions.catastrophizing")
            == "Catastrophizing"
        )

        # Spanish distortions
        assert (
            Localizer.get("es", "reframing.distortions.all-or-nothing")
            == "Pensamiento de Todo o Nada"
        )
        assert (
            Localizer.get("es", "reframing.distortions.catastrophizing")
            == "Catastrofización"
        )

    def test_fallback_to_english(self):
        """Test fallback to English for unsupported languages."""
        # Request translation in unsupported language
        assert (
            Localizer.get("fr", "greeting.welcome")
            == "Welcome! I'm here to help you reframe negative thoughts using CBT techniques."
        )

    def test_missing_key_returns_default(self):
        """Test that missing keys return the default value."""
        assert Localizer.get("en", "nonexistent.key", "default") == "default"
        assert Localizer.get("es", "nonexistent.key", "default") == "default"

    def test_get_all_translations(self):
        """Test getting all translations under a prefix."""
        # Get all greeting translations
        en_greetings = Localizer.get_all("en", "greeting")
        assert isinstance(en_greetings, dict)
        assert "welcome" in en_greetings
        assert "disclaimer" in en_greetings
        assert "prompt" in en_greetings

        # Get all Spanish discovery questions
        es_questions = Localizer.get_all("es", "discovery.questions")
        assert isinstance(es_questions, dict)
        assert "situation" in es_questions
        assert "emotions" in es_questions
        assert "thoughts" in es_questions
        assert "impact" in es_questions

    def test_format_translations(self):
        """Test formatting translations with arguments."""
        # For this test, we'll need to add a translation with placeholders
        # Since we don't have any in the current translations, we'll test the method
        template = "Hello {name}, welcome to {service}!"
        Localizer.TRANSLATIONS["en"]["test_format"] = template

        result = Localizer.format("en", "test_format", name="John", service="CBT")
        assert result == "Hello John, welcome to CBT!"

        # Cleanup
        del Localizer.TRANSLATIONS["en"]["test_format"]

    def test_get_crisis_resources(self):
        """Test getting localized crisis resources."""
        # English resources
        en_resources = Localizer.get_crisis_resources("en")
        assert "National Suicide Prevention Lifeline" in en_resources
        assert en_resources["National Suicide Prevention Lifeline"] == "988"
        assert "Crisis Text Line" in en_resources
        assert en_resources["Crisis Text Line"] == "Text HOME to 741741"
        assert "Emergency Services" in en_resources
        assert en_resources["Emergency Services"] == "911"

        # Spanish resources
        es_resources = Localizer.get_crisis_resources("es")
        assert "Línea Nacional de Prevención del Suicidio" in es_resources
        assert es_resources["Línea Nacional de Prevención del Suicidio"] == "988"
        assert "Línea de Crisis por Texto" in es_resources
        assert es_resources["Línea de Crisis por Texto"] == "Envía 'AYUDA' al 741741"
        assert "Emergencias" in es_resources
        assert es_resources["Emergencias"] == "911"

    def test_all_error_messages(self):
        """Test all error message translations."""
        # English errors
        assert (
            Localizer.get("en", "errors.general")
            == "I apologize, but I encountered an error. Please try again."
        )
        assert (
            Localizer.get("en", "errors.pdf_generation")
            == "I couldn't generate the PDF summary, but here's your text summary:"
        )

        # Spanish errors
        assert (
            Localizer.get("es", "errors.general")
            == "Lo siento, pero encontré un error. Por favor, inténtalo de nuevo."
        )
        assert (
            Localizer.get("es", "errors.pdf_generation")
            == "No pude generar el resumen en PDF, pero aquí está tu resumen en texto:"
        )

    def test_summary_translations(self):
        """Test summary phase translations."""
        # English summary
        assert (
            Localizer.get("en", "summary.intro")
            == "Here's a summary of our conversation:"
        )
        assert (
            Localizer.get("en", "summary.thought_patterns")
            == "Thought Patterns Identified:"
        )
        assert (
            Localizer.get("en", "summary.closing")
            == "Remember, changing thought patterns takes practice. Be patient with yourself."
        )

        # Spanish summary
        assert (
            Localizer.get("es", "summary.intro")
            == "Aquí está el resumen de nuestra conversación:"
        )
        assert (
            Localizer.get("es", "summary.thought_patterns")
            == "Patrones de Pensamiento Identificados:"
        )
        assert (
            Localizer.get("es", "summary.closing")
            == "Recuerda, cambiar los patrones de pensamiento requiere práctica. Sé paciente contigo mismo."
        )

    @pytest.mark.parametrize(
        "language,key,expected",
        [
            (
                "en",
                "discovery.intro",
                "I'd like to understand more about what you're experiencing.",
            ),
            (
                "es",
                "discovery.intro",
                "Me gustaría entender más sobre lo que estás experimentando.",
            ),
            (
                "en",
                "reframing.intro",
                "Let's explore different ways to look at this situation.",
            ),
            (
                "es",
                "reframing.intro",
                "Exploremos diferentes formas de ver esta situación.",
            ),
            (
                "en",
                "crisis.detected",
                "I notice you might be going through a really difficult time.",
            ),
            (
                "es",
                "crisis.detected",
                "Noto que podrías estar pasando por un momento muy difícil.",
            ),
        ],
    )
    def test_key_translations(self, language, key, expected):
        """Test specific key translations."""
        assert Localizer.get(language, key) == expected
