"""Tools for the re-frame cognitive reframing agent."""

import base64
import datetime
from datetime import UTC
import io
import json

from fpdf import FPDF
from google.adk.tools import ToolContext

from .models import (
    PdfReportResponse,
    ProcessReframeResponse,
    ReframeAnalysis,
    StatusEnum,
)


def process_reframe_data(
    tool_context: ToolContext,
    distortions: list[str],
    evidence_for: list[str],
    evidence_against: list[str],
    balanced_thought: str,
    micro_action: str,
    certainty_before: int,
    certainty_after: int,
    tone: str = "warm",
) -> ProcessReframeResponse:
    """Process and store the reframe analysis data.

    Args:
        tool_context: ADK tool context
        distortions: List of cognitive distortions identified
        evidence_for: Evidence supporting the negative thought
        evidence_against: Evidence contradicting the negative thought
        balanced_thought: A more balanced perspective
        micro_action: Small actionable step
        certainty_before: Initial certainty rating (0-100)
        certainty_after: Post-reframe certainty rating (0-100)
        tone: Tone of the response (default: "warm")

    Returns:
        ProcessReframeResponse with status and stored data
    """
    try:
        # Log intake data from state for debugging
        trigger = tool_context.state.get("trigger_situation", "Not provided")
        thought = tool_context.state.get("automatic_thought", "Not provided")
        emotion = tool_context.state.get("emotion_data", "Not provided")
        
        print(f"[DEBUG] Processing reframe for:")
        print(f"  Trigger: {trigger}")
        print(f"  Thought: {thought}")
        print(f"  Emotion: {emotion}")
        # Create the reframe analysis
        analysis = ReframeAnalysis(
            distortions=distortions,
            evidence_for=evidence_for,
            evidence_against=evidence_against,
            balanced_thought=balanced_thought,
            micro_action=micro_action,
            certainty_before=certainty_before,
            certainty_after=certainty_after,
            tone=tone,
        )

        # Store in state as JSON
        result_json = analysis.model_dump_json()
        tool_context.state["result_json"] = result_json

        # Include intake data in response message
        intake_summary = f"Reframe analysis processed successfully for thought: '{thought}' in situation: '{trigger}' with emotion: {emotion}"
        
        return ProcessReframeResponse(
            status=StatusEnum.SUCCESS,
            message=intake_summary,
            result_json=result_json,
        )
    except Exception as e:
        return ProcessReframeResponse(
            status=StatusEnum.FAILURE,
            message=f"Failed to process reframe data: {str(e)}",
        )


def create_pdf_report(
    tool_context: ToolContext,
    include_timestamps: bool = True,
) -> PdfReportResponse:
    """Create a PDF report from the session data.

    Args:
        tool_context: ADK tool context
        include_timestamps: Whether to include timestamps in the report

    Returns:
        PdfReportResponse with status and base64 encoded PDF
    """
    try:
        # Get data from state
        trigger = tool_context.state.get("trigger_situation", "Not provided")
        thought = tool_context.state.get("automatic_thought", "Not provided")
        emotion = tool_context.state.get("emotion_data", "Not provided")
        
        # Parse reframe analysis
        result_json = tool_context.state.get("result_json", "{}")
        analysis = json.loads(result_json) if result_json else {}

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Cognitive Reframing Session Report", ln=1, align="C")
        
        if include_timestamps:
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 10, f"Generated: {datetime.datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}", ln=1, align="C")
        
        pdf.ln(10)

        # Session Summary
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Session Summary", ln=1)
        pdf.set_font("Arial", "", 11)
        
        # Intake data
        pdf.multi_cell(0, 7, f"Situation: {trigger}")
        pdf.ln(3)
        pdf.multi_cell(0, 7, f"Automatic Thought: {thought}")
        pdf.ln(3)
        pdf.multi_cell(0, 7, f"Emotion: {emotion}")
        pdf.ln(10)

        # Reframe Analysis
        if analysis:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Reframe Analysis", ln=1)
            pdf.set_font("Arial", "", 11)
            
            # Cognitive distortions
            if distortions := analysis.get("distortions", []):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, "Cognitive Distortions Identified:", ln=1)
                pdf.set_font("Arial", "", 11)
                for distortion in distortions:
                    pdf.cell(10, 7, "")  # Indent
                    pdf.cell(0, 7, f"• {distortion}", ln=1)
                pdf.ln(5)

            # Balanced thought
            if balanced := analysis.get("balanced_thought"):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, "Balanced Perspective:", ln=1)
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 7, balanced, 0, 1)
                pdf.ln(5)

            # Micro action
            if action := analysis.get("micro_action"):
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, "Recommended Action:", ln=1)
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 7, action, 0, 1)
                pdf.ln(5)

            # Certainty ratings
            before = analysis.get("certainty_before", 0)
            after = analysis.get("certainty_after", 0)
            if before or after:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 8, "Belief Ratings:", ln=1)
                pdf.set_font("Arial", "", 11)
                pdf.cell(0, 7, f"Before reframing: {before}%", ln=1)
                pdf.cell(0, 7, f"After reframing: {after}%", ln=1)

        # Convert to base64
        pdf_output = pdf.output(dest="S").encode("latin-1")
        pdf_base64 = base64.b64encode(pdf_output).decode("utf-8")

        # Store in state
        tool_context.state["final_artifact"] = pdf_base64

        return PdfReportResponse(
            status=StatusEnum.SUCCESS,
            message="PDF report created successfully",
            pdf_base64=pdf_base64,
        )
    except Exception as e:
        return PdfReportResponse(
            status=StatusEnum.FAILURE,
            message=f"Failed to create PDF report: {str(e)}",
        )