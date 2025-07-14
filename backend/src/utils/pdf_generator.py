"""PDF generation utilities for session summaries."""

import io
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFGenerator:
    """Generates professional PDF documents from session summaries."""

    def __init__(self):
        """Initialize PDF generator with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles for the PDF."""
        # Title style
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Title"],
                fontSize=24,
                textColor=colors.HexColor("#1a1a1a"),
                spaceAfter=30,
                alignment=1,  # Center alignment
            )
        )

        # Section header style
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading1"],
                fontSize=16,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=12,
                spaceBefore=20,
                leftIndent=0,
            )
        )

        # Subsection header style
        self.styles.add(
            ParagraphStyle(
                name="SubsectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor("#34495e"),
                spaceAfter=10,
                spaceBefore=15,
                leftIndent=20,
            )
        )

        # Body text style
        self.styles.add(
            ParagraphStyle(
                name="CustomBody",
                parent=self.styles["BodyText"],
                fontSize=11,
                leading=16,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=10,
                leftIndent=20,
                rightIndent=20,
            )
        )

        # Disclaimer style
        self.styles.add(
            ParagraphStyle(
                name="Disclaimer",
                parent=self.styles["BodyText"],
                fontSize=9,
                textColor=colors.HexColor("#7f8c8d"),
                spaceAfter=10,
                leftIndent=20,
                rightIndent=20,
                fontName="Helvetica-Oblique",
            )
        )

    def generate_session_pdf(
        self, session_data: dict, output_path: Path | None = None, language: str = "en"
    ) -> bytes:
        """
        Generate a PDF from session summary data.

        Args:
            session_data: Dictionary containing session summary information
            output_path: Optional path to save the PDF file
            language: Language code for localized content (default: 'en')

        Returns:
            PDF content as bytes
        """
        # Create a BytesIO buffer to hold the PDF
        buffer = io.BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        # Build the content
        story = []

        # Add title
        title = (
            "CBT Thought Reframing Session Summary"
            if language == "en"
            else "Resumen de Sesión de Reformulación de Pensamientos TCC"
        )
        story.append(Paragraph(title, self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.2 * inch))

        # Add date
        date_str = datetime.now().strftime("%B %d, %Y")
        date_label = "Session Date" if language == "en" else "Fecha de Sesión"
        story.append(Paragraph(f"{date_label}: {date_str}", self.styles["CustomBody"]))
        story.append(Spacer(1, 0.3 * inch))

        # Add disclaimer
        if language == "es":
            disclaimer_text = (
                "<i>Este resumen se proporciona para tu referencia y reflexión personal. "
                "No es un sustituto del tratamiento profesional de salud mental. "
                "Si estás experimentando angustia significativa o tienes pensamientos de "
                "autolesión, por favor contacta a un profesional de salud mental o línea "
                "de crisis inmediatamente.</i>"
            )
        else:
            disclaimer_text = (
                "<i>This summary is provided for your personal reference and reflection. "
                "It is not a substitute for professional mental health treatment. "
                "If you are experiencing significant distress or having thoughts of "
                "self-harm, please contact a mental health professional or crisis hotline "
                "immediately.</i>"
            )
        story.append(Paragraph(disclaimer_text, self.styles["Disclaimer"]))
        story.append(Spacer(1, 0.3 * inch))

        # Add initial thoughts section
        if session_data.get("initial_thoughts"):
            header = (
                "Your Initial Thoughts"
                if language == "en"
                else "Tus Pensamientos Iniciales"
            )
            story.append(Paragraph(header, self.styles["SectionHeader"]))
            story.append(
                Paragraph(
                    str(session_data["initial_thoughts"]), self.styles["CustomBody"]
                )
            )
            story.append(Spacer(1, 0.2 * inch))

        # Add distortions identified
        if session_data.get("distortions"):
            header = (
                "Cognitive Distortions Identified"
                if language == "en"
                else "Distorsiones Cognitivas Identificadas"
            )
            story.append(Paragraph(header, self.styles["SectionHeader"]))
            for distortion in session_data["distortions"]:
                if distortion and isinstance(distortion, dict):
                    story.append(
                        Paragraph(
                            f"• <b>{distortion.get('name', 'Unknown')}</b>",
                            self.styles["SubsectionHeader"],
                        )
                    )
                    story.append(
                        Paragraph(
                            distortion.get("explanation", ""), self.styles["CustomBody"]
                        )
                    )
            story.append(Spacer(1, 0.2 * inch))

        # Add reframed thoughts
        if session_data.get("reframed_thoughts"):
            header = (
                "Reframed Thoughts" if language == "en" else "Pensamientos Reformulados"
            )
            story.append(Paragraph(header, self.styles["SectionHeader"]))
            for thought in session_data["reframed_thoughts"]:
                if thought:
                    story.append(Paragraph(f"• {thought}", self.styles["CustomBody"]))
            story.append(Spacer(1, 0.2 * inch))

        # Add reflection
        if session_data.get("reflection"):
            header = "Your Reflection" if language == "en" else "Tu Reflexión"
            story.append(Paragraph(header, self.styles["SectionHeader"]))
            story.append(
                Paragraph(str(session_data["reflection"]), self.styles["CustomBody"])
            )
            story.append(Spacer(1, 0.2 * inch))

        # Add action items
        if "action_items" in session_data:
            header = "Action Items" if language == "en" else "Elementos de Acción"
            story.append(Paragraph(header, self.styles["SectionHeader"]))
            action_data = []
            for item in session_data["action_items"]:
                action_data.append([f"□ {item}"])

            action_table = Table(action_data, colWidths=[6 * inch])
            action_table.setStyle(
                TableStyle(
                    [
                        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
                        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 11),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                        ("LEFTPADDING", (0, 0), (-1, -1), 20),
                    ]
                )
            )
            story.append(action_table)
            story.append(Spacer(1, 0.3 * inch))

        # Add resources
        if "resources" in session_data:
            header = "Helpful Resources" if language == "en" else "Recursos Útiles"
            story.append(Paragraph(header, self.styles["SectionHeader"]))
            for resource in session_data["resources"]:
                story.append(
                    Paragraph(
                        f"• <b>{resource['name']}</b>: {resource['description']}",
                        self.styles["CustomBody"],
                    )
                )
            story.append(Spacer(1, 0.2 * inch))

        # Add footer
        story.append(Spacer(1, 0.5 * inch))
        if language == "es":
            footer_text = (
                "<i>Recuerda: El cambio toma tiempo y práctica. Sé paciente contigo mismo "
                "mientras trabajas en implementar estos nuevos patrones de pensamiento.</i>"
            )
        else:
            footer_text = (
                "<i>Remember: Change takes time and practice. Be patient with yourself "
                "as you work on implementing these new thought patterns.</i>"
            )
        story.append(Paragraph(footer_text, self.styles["Disclaimer"]))

        # Build the PDF
        doc.build(story)

        # Get the PDF content
        pdf_content = buffer.getvalue()
        buffer.close()

        # Save to file if path provided
        if output_path:
            output_path.write_bytes(pdf_content)

        return pdf_content

    def generate_crisis_resources_pdf(
        self, resources: dict, output_path: Path | None = None
    ) -> bytes:
        """
        Generate a PDF containing crisis resources.

        Args:
            resources: Dictionary containing crisis resource information
            output_path: Optional path to save the PDF file

        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        story = []

        # Title
        story.append(Paragraph("Crisis Support Resources", self.styles["CustomTitle"]))
        story.append(Spacer(1, 0.3 * inch))

        # Important notice
        notice_text = (
            "<b>If you are in immediate danger or having thoughts of self-harm, "
            "please call emergency services (911) or go to your nearest emergency room.</b>"
        )
        story.append(Paragraph(notice_text, self.styles["CustomBody"]))
        story.append(Spacer(1, 0.3 * inch))

        # Add hotlines
        if resources.get("hotlines"):
            story.append(
                Paragraph("24/7 Crisis Hotlines", self.styles["SectionHeader"])
            )
            hotline_data = []
            for hotline in resources["hotlines"]:
                hotline_data.append(
                    [hotline["name"], hotline["number"], hotline.get("description", "")]
                )

            if hotline_data:  # Only create table if there's data
                hotline_table = Table(
                    hotline_data, colWidths=[2.5 * inch, 1.5 * inch, 2.5 * inch]
                )
                hotline_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ecf0f1")),
                            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 10),
                            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 12),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                            ("TOPPADDING", (0, 0), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ]
                    )
                )
                story.append(hotline_table)
                story.append(Spacer(1, 0.3 * inch))

        # Build and return PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()

        if output_path:
            output_path.write_bytes(pdf_content)

        return pdf_content
