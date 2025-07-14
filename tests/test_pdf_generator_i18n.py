"""Tests for PDF generator with internationalization support."""

import pytest

from src.utils.pdf_generator import PDFGenerator


class TestPDFGeneratorI18n:
    """Test suite for PDF generator with language support."""

    @pytest.fixture
    def pdf_generator(self):
        """Create a PDFGenerator instance."""
        return PDFGenerator()

    @pytest.fixture
    def sample_session_data(self):
        """Create sample session data for testing."""
        return {
            "initial_thoughts": "I'm a complete failure at work",
            "distortions": [
                {
                    "name": "All-or-Nothing Thinking",
                    "explanation": "Viewing situations in absolute terms",
                },
                {
                    "name": "Labeling",
                    "explanation": "Attaching a negative label to yourself",
                },
            ],
            "reframed_thoughts": [
                "I made a mistake at work, but that doesn't define my entire career",
                "I can learn from this experience and improve",
            ],
            "reflection": "I realize I was being too hard on myself",
            "action_items": [
                "Practice self-compassion when mistakes happen",
                "List three work accomplishments this week",
                "Talk to my supervisor about the situation",
            ],
            "resources": [
                {
                    "name": "Self-Compassion Exercises",
                    "description": "Techniques for being kinder to yourself",
                },
                {
                    "name": "CBT Workbook",
                    "description": "Exercises for challenging negative thoughts",
                },
            ],
        }

    def test_generate_english_pdf(self, pdf_generator, sample_session_data):
        """Test generating PDF in English."""
        pdf_content = pdf_generator.generate_session_pdf(
            sample_session_data, language="en"
        )
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        # PDF should start with %PDF
        assert pdf_content.startswith(b"%PDF")

    def test_generate_spanish_pdf(self, pdf_generator, sample_session_data):
        """Test generating PDF in Spanish."""
        pdf_content = pdf_generator.generate_session_pdf(
            sample_session_data, language="es"
        )
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        # PDF should start with %PDF
        assert pdf_content.startswith(b"%PDF")

    def test_pdf_default_language(self, pdf_generator, sample_session_data):
        """Test that default language is English."""
        pdf_content = pdf_generator.generate_session_pdf(sample_session_data)
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0

    def test_pdf_with_missing_sections(self, pdf_generator):
        """Test PDF generation with missing optional sections."""
        minimal_data = {
            "initial_thoughts": "I feel anxious",
            "distortions": [],
            "reframed_thoughts": ["I can handle this"],
        }
        pdf_content = pdf_generator.generate_session_pdf(minimal_data, language="en")
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0

    def test_pdf_with_empty_data(self, pdf_generator):
        """Test PDF generation with empty data."""
        empty_data = {}
        pdf_content = pdf_generator.generate_session_pdf(empty_data, language="en")
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0

    def test_pdf_save_to_file(self, pdf_generator, sample_session_data, tmp_path):
        """Test saving PDF to file."""
        output_path = tmp_path / "test_session.pdf"
        pdf_content = pdf_generator.generate_session_pdf(
            sample_session_data, output_path=output_path, language="en"
        )

        # Check that file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0

        # Check that returned content matches file content
        with output_path.open("rb") as f:
            file_content = f.read()
        assert pdf_content == file_content

    def test_pdf_spanish_content_structure(self, pdf_generator):
        """Test that Spanish PDF has correct structure."""
        spanish_data = {
            "initial_thoughts": "Soy un fracaso completo en el trabajo",
            "distortions": [
                {
                    "name": "Pensamiento de Todo o Nada",
                    "explanation": "Ver las situaciones en términos absolutos",
                }
            ],
            "reframed_thoughts": [
                "Cometí un error en el trabajo, pero eso no define toda mi carrera"
            ],
            "action_items": ["Practicar la autocompasión cuando ocurran errores"],
        }

        pdf_content = pdf_generator.generate_session_pdf(spanish_data, language="es")
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0

    def test_pdf_with_long_content(self, pdf_generator):
        """Test PDF generation with long content."""
        long_data = {
            "initial_thoughts": "This is a very long thought " * 50,
            "distortions": [
                {
                    "name": f"Distortion {i}",
                    "explanation": "This is a long explanation " * 20,
                }
                for i in range(10)
            ],
            "reframed_thoughts": [f"Reframed thought {i} " * 10 for i in range(5)],
            "action_items": [f"Action item {i}" for i in range(20)],
        }

        pdf_content = pdf_generator.generate_session_pdf(long_data, language="en")
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0

    def test_pdf_custom_styles(self, pdf_generator):
        """Test that custom styles are properly set up."""
        # Check that custom styles exist
        assert "CustomTitle" in pdf_generator.styles
        assert "SectionHeader" in pdf_generator.styles
        assert "SubsectionHeader" in pdf_generator.styles
        assert "CustomBody" in pdf_generator.styles
        assert "Disclaimer" in pdf_generator.styles

    @pytest.mark.parametrize("language", ["en", "es"])
    def test_pdf_generation_both_languages(
        self, pdf_generator, sample_session_data, language
    ):
        """Test PDF generation works for both supported languages."""
        pdf_content = pdf_generator.generate_session_pdf(
            sample_session_data, language=language
        )
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert pdf_content.startswith(b"%PDF")

    def test_pdf_special_characters(self, pdf_generator):
        """Test PDF generation with special characters."""
        special_data = {
            "initial_thoughts": "I can't handle the ñ, é, í, ó, ú characters",
            "distortions": [
                {
                    "name": "Catastrophizing",
                    "explanation": "Making things worse than they are",
                }
            ],
            "reframed_thoughts": ["I can handle special characters like ñ, ¿, ¡"],
        }

        # Test both languages
        for lang in ["en", "es"]:
            pdf_content = pdf_generator.generate_session_pdf(
                special_data, language=lang
            )
            assert isinstance(pdf_content, bytes)
            assert len(pdf_content) > 0
