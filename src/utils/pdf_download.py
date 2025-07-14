"""PDF download functionality for session summaries."""

import base64
from pathlib import Path


class PDFDownloadHandler:
    """Handles PDF generation and download for session summaries."""

    def __init__(self):
        """Initialize the PDF download handler."""
        from .pdf_generator import PDFGenerator

        self.pdf_generator = PDFGenerator()

    def prepare_download_response(
        self, session_data: dict, filename: str | None = None
    ) -> tuple[bytes, str, str]:
        """
        Prepare a PDF for download.

        Args:
            session_data: Session summary data
            filename: Optional custom filename

        Returns:
            Tuple of (pdf_content, filename, content_type)
        """
        # Generate PDF
        pdf_content = self.pdf_generator.generate_session_pdf(session_data)

        # Generate filename if not provided
        if not filename:
            from datetime import datetime

            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cbt_session_summary_{date_str}.pdf"

        content_type = "application/pdf"

        return pdf_content, filename, content_type

    def generate_download_link(
        self, session_data: dict, filename: str | None = None
    ) -> str:
        """
        Generate a data URL for client-side download.

        Args:
            session_data: Session summary data
            filename: Optional custom filename

        Returns:
            Data URL string for download
        """
        pdf_content, _, _ = self.prepare_download_response(session_data, filename)

        # Encode PDF to base64
        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        # Create data URL
        data_url = f"data:application/pdf;base64,{pdf_base64}"

        return data_url

    def save_to_file(self, session_data: dict, output_path: Path) -> None:
        """
        Save session summary as PDF to file.

        Args:
            session_data: Session summary data
            output_path: Path where to save the PDF
        """
        self.pdf_generator.generate_session_pdf(session_data, output_path)

    def generate_crisis_resources_pdf(
        self, resources: dict, filename: str | None = None
    ) -> tuple[bytes, str, str]:
        """
        Generate crisis resources PDF for download.

        Args:
            resources: Crisis resource information
            filename: Optional custom filename

        Returns:
            Tuple of (pdf_content, filename, content_type)
        """
        pdf_content = self.pdf_generator.generate_crisis_resources_pdf(resources)

        if not filename:
            filename = "crisis_support_resources.pdf"

        content_type = "application/pdf"

        return pdf_content, filename, content_type
