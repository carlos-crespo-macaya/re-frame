"""Tests for PDF generation functionality."""

import base64

import pytest

from src.utils.pdf_download import PDFDownloadHandler
from src.utils.pdf_generator import PDFGenerator


class TestPDFGenerator:
    """Test cases for PDFGenerator class."""

    @pytest.fixture
    def pdf_generator(self):
        """Create a PDFGenerator instance."""
        return PDFGenerator()

    @pytest.fixture
    def sample_session_data(self):
        """Sample session data for testing."""
        return {
            "initial_thoughts": "I always mess up everything I do.",
            "distortions": [
                {
                    "name": "All-or-Nothing Thinking",
                    "explanation": "You're viewing situations in absolute terms.",
                },
                {
                    "name": "Overgeneralization",
                    "explanation": "You're making broad conclusions from single events.",
                },
            ],
            "reframed_thoughts": [
                "I make mistakes sometimes, but I also succeed at many things.",
                "Each situation is unique and doesn't define my entire worth.",
            ],
            "reflection": "I realize I've been too hard on myself.",
            "action_items": [
                "Practice self-compassion when I make mistakes",
                "Keep a success journal to track accomplishments",
            ],
            "resources": [
                {
                    "name": "Self-Compassion Exercises",
                    "description": "Guided practices for treating yourself kindly",
                },
                {
                    "name": "CBT Workbook",
                    "description": "Exercises for challenging negative thoughts",
                },
            ],
        }

    @pytest.fixture
    def sample_crisis_resources(self):
        """Sample crisis resources for testing."""
        return {
            "hotlines": [
                {
                    "name": "National Suicide Prevention Lifeline",
                    "number": "988",
                    "description": "24/7 crisis support",
                },
                {
                    "name": "Crisis Text Line",
                    "number": "Text HOME to 741741",
                    "description": "24/7 text-based support",
                },
            ]
        }

    def test_pdf_generator_initialization(self, pdf_generator):
        """Test PDFGenerator initializes with custom styles."""
        assert pdf_generator.styles is not None
        assert "CustomTitle" in pdf_generator.styles
        assert "SectionHeader" in pdf_generator.styles
        assert "SubsectionHeader" in pdf_generator.styles
        assert "CustomBody" in pdf_generator.styles
        assert "Disclaimer" in pdf_generator.styles

    def test_generate_session_pdf_returns_bytes(
        self, pdf_generator, sample_session_data
    ):
        """Test generate_session_pdf returns PDF as bytes."""
        pdf_content = pdf_generator.generate_session_pdf(sample_session_data)

        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        # PDF files start with %PDF
        assert pdf_content.startswith(b"%PDF")

    def test_generate_session_pdf_with_partial_data(self, pdf_generator):
        """Test PDF generation with incomplete session data."""
        partial_data = {
            "initial_thoughts": "I feel overwhelmed.",
            "reframed_thoughts": ["I can handle this one step at a time."],
        }

        pdf_content = pdf_generator.generate_session_pdf(partial_data)

        assert isinstance(pdf_content, bytes)
        assert pdf_content.startswith(b"%PDF")

    def test_generate_session_pdf_saves_to_file(
        self, pdf_generator, sample_session_data, tmp_path
    ):
        """Test saving PDF to file."""
        output_path = tmp_path / "test_session.pdf"

        pdf_content = pdf_generator.generate_session_pdf(
            sample_session_data, output_path
        )

        assert output_path.exists()
        assert output_path.stat().st_size > 0

        # Verify content matches
        saved_content = output_path.read_bytes()
        assert saved_content == pdf_content
        assert saved_content.startswith(b"%PDF")

    def test_generate_crisis_resources_pdf(
        self, pdf_generator, sample_crisis_resources
    ):
        """Test crisis resources PDF generation."""
        pdf_content = pdf_generator.generate_crisis_resources_pdf(
            sample_crisis_resources
        )

        assert isinstance(pdf_content, bytes)
        assert pdf_content.startswith(b"%PDF")

    def test_empty_session_data_handling(self, pdf_generator):
        """Test PDF generation with empty session data."""
        empty_data = {}

        pdf_content = pdf_generator.generate_session_pdf(empty_data)

        assert isinstance(pdf_content, bytes)
        assert pdf_content.startswith(b"%PDF")


class TestPDFDownloadHandler:
    """Test cases for PDFDownloadHandler class."""

    @pytest.fixture
    def download_handler(self):
        """Create a PDFDownloadHandler instance."""
        return PDFDownloadHandler()

    @pytest.fixture
    def sample_session_data(self):
        """Sample session data for testing."""
        return {
            "initial_thoughts": "Test thoughts",
            "reframed_thoughts": ["Reframed test thoughts"],
        }

    def test_download_handler_initialization(self, download_handler):
        """Test PDFDownloadHandler initializes with PDFGenerator."""
        assert hasattr(download_handler, "pdf_generator")
        assert isinstance(download_handler.pdf_generator, PDFGenerator)

    def test_prepare_download_response(self, download_handler, sample_session_data):
        """Test prepare_download_response returns correct tuple."""
        pdf_content, filename, content_type = (
            download_handler.prepare_download_response(sample_session_data)
        )

        assert isinstance(pdf_content, bytes)
        assert pdf_content.startswith(b"%PDF")
        assert filename.startswith("cbt_session_summary_")
        assert filename.endswith(".pdf")
        assert content_type == "application/pdf"

    def test_prepare_download_response_with_custom_filename(
        self, download_handler, sample_session_data
    ):
        """Test prepare_download_response with custom filename."""
        custom_filename = "my_session.pdf"

        pdf_content, filename, content_type = (
            download_handler.prepare_download_response(
                sample_session_data, custom_filename
            )
        )

        assert filename == custom_filename
        assert content_type == "application/pdf"

    def test_generate_download_link(self, download_handler, sample_session_data):
        """Test generate_download_link creates valid data URL."""
        data_url = download_handler.generate_download_link(sample_session_data)

        assert data_url.startswith("data:application/pdf;base64,")

        # Extract and decode base64 content
        base64_content = data_url.split(",", 1)[1]
        pdf_content = base64.b64decode(base64_content)

        assert pdf_content.startswith(b"%PDF")

    def test_save_to_file(self, download_handler, sample_session_data, tmp_path):
        """Test save_to_file saves PDF correctly."""
        output_path = tmp_path / "session_summary.pdf"

        download_handler.save_to_file(sample_session_data, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0

        content = output_path.read_bytes()
        assert content.startswith(b"%PDF")

    def test_generate_crisis_resources_pdf(self, download_handler):
        """Test crisis resources PDF generation through download handler."""
        resources = {"hotlines": [{"name": "Test Hotline", "number": "123-456-7890"}]}

        pdf_content, filename, content_type = (
            download_handler.generate_crisis_resources_pdf(resources)
        )

        assert isinstance(pdf_content, bytes)
        assert pdf_content.startswith(b"%PDF")
        assert filename == "crisis_support_resources.pdf"
        assert content_type == "application/pdf"

    def test_generate_crisis_resources_pdf_custom_filename(self, download_handler):
        """Test crisis resources PDF with custom filename."""
        resources = {"hotlines": []}
        custom_filename = "emergency_contacts.pdf"

        pdf_content, filename, content_type = (
            download_handler.generate_crisis_resources_pdf(resources, custom_filename)
        )

        assert filename == custom_filename


class TestPDFErrorHandling:
    """Test error handling in PDF generation."""

    @pytest.fixture
    def pdf_generator(self):
        """Create a PDFGenerator instance."""
        return PDFGenerator()

    def test_pdf_generation_with_none_values(self, pdf_generator):
        """Test PDF generation handles None values gracefully."""
        data_with_none = {
            "initial_thoughts": None,
            "distortions": None,
            "reframed_thoughts": None,
        }

        # Should not raise exception
        pdf_content = pdf_generator.generate_session_pdf(data_with_none)
        assert isinstance(pdf_content, bytes)

    def test_pdf_generation_with_special_characters(self, pdf_generator):
        """Test PDF generation handles special characters."""
        data_with_special = {
            "initial_thoughts": "Test with special chars: & < > \" ' © ®",
            "reframed_thoughts": ["Unicode test: 你好 🎉 ñ é"],
        }

        pdf_content = pdf_generator.generate_session_pdf(data_with_special)
        assert isinstance(pdf_content, bytes)
        assert pdf_content.startswith(b"%PDF")

    def test_pdf_generation_with_long_text(self, pdf_generator):
        """Test PDF generation with very long text content."""
        long_text = "This is a very long text. " * 100

        data_with_long_text = {
            "initial_thoughts": long_text,
            "reflection": long_text,
        }

        pdf_content = pdf_generator.generate_session_pdf(data_with_long_text)
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 3000  # Should be a reasonably large PDF


class TestPDFIntegration:
    """Integration tests for PDF generation workflow."""

    @pytest.fixture
    def full_session_data(self):
        """Complete session data for integration testing."""
        return {
            "initial_thoughts": "I'm a failure because I made a mistake at work.",
            "distortions": [
                {
                    "name": "Labeling",
                    "explanation": "You're defining yourself based on a single event.",
                },
                {
                    "name": "Catastrophizing",
                    "explanation": "You're assuming the worst possible outcome.",
                },
            ],
            "reframed_thoughts": [
                "Making a mistake doesn't define who I am as a person.",
                "This mistake is an opportunity to learn and improve.",
                "My worth isn't determined by being perfect at work.",
            ],
            "reflection": (
                "I see now that I was being too harsh on myself. Everyone makes "
                "mistakes, and this doesn't mean I'm a failure. I can learn from "
                "this experience and do better next time."
            ),
            "action_items": [
                "Talk to my supervisor about the mistake and how to prevent it",
                "Practice self-compassion when I notice self-critical thoughts",
                "Keep a journal of my successes at work this week",
            ],
            "resources": [
                {
                    "name": "Mindful Self-Compassion",
                    "description": "Techniques for treating yourself with kindness",
                },
                {
                    "name": "Growth Mindset Resources",
                    "description": "Learn how mistakes contribute to growth",
                },
            ],
        }

    def test_full_workflow_integration(self, full_session_data, tmp_path):
        """Test complete PDF generation and download workflow."""
        handler = PDFDownloadHandler()

        # Test download response preparation
        pdf_content, filename, content_type = handler.prepare_download_response(
            full_session_data
        )

        assert isinstance(pdf_content, bytes)
        assert pdf_content.startswith(b"%PDF")
        assert ".pdf" in filename
        assert content_type == "application/pdf"

        # Test data URL generation
        data_url = handler.generate_download_link(full_session_data)
        assert data_url.startswith("data:application/pdf;base64,")

        # Test file saving
        output_path = tmp_path / "integration_test.pdf"
        handler.save_to_file(full_session_data, output_path)

        assert output_path.exists()
        saved_content = output_path.read_bytes()
        assert saved_content.startswith(b"%PDF")

        # Verify PDF has reasonable size (indicates content was written)
        assert len(saved_content) > 2000
