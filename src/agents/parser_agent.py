"""
Parser Agent for CBT Assistant.

This module implements a parser agent that analyzes user thoughts
to identify cognitive distortions without direct user interaction.
"""

from google.adk.agents import LlmAgent

from src.knowledge.cbt_context import BASE_CBT_CONTEXT, COGNITIVE_DISTORTIONS


def analyze_thought_for_distortions(
    thought: str,
) -> dict:  # pylint: disable=unused-argument
    """
    Analyze a thought to identify potential cognitive distortions.

    This tool examines the user's automatic thought and identifies
    which cognitive distortions may be present.

    Args:
        thought: The automatic thought to analyze

    Returns:
        dict: Analysis results with identified distortions
    """
    # This is a placeholder that returns guidance for the agent
    # The actual analysis is done by the LLM based on the instructions
    return {
        "status": "success",
        "instructions": "Analyze the thought for cognitive distortions and return JSON",
        "distortion_codes": list(COGNITIVE_DISTORTIONS.keys()),
    }


def create_parser_agent(model: str = "gemini-2.0-flash") -> LlmAgent:
    """
    Create a parser agent for analyzing thoughts and identifying distortions.

    Args:
        model: The Gemini model to use

    Returns:
        An LlmAgent configured for parsing and analysis
    """
    # Build distortion reference for the agent
    distortion_reference = "\n\n## Cognitive Distortions Reference:\n"
    for _, distortion in COGNITIVE_DISTORTIONS.items():
        distortion_reference += f"\n### {distortion['code']} - {distortion['name']}\n"
        distortion_reference += f"Definition: {distortion['definition']}\n"
        distortion_reference += f"Examples: {', '.join(distortion['examples'])}\n"

    parser_instruction = (
        BASE_CBT_CONTEXT
        + "\n\n## Parser Agent Role\n\n"
        + "You are a silent data extraction specialist that analyzes user thoughts "
        + "to identify cognitive distortions. You never interact with the user directly.\n\n"
        + "## Your Task\n"
        + "When given a thought to analyze:\n"
        + "1. Identify which cognitive distortions are present\n"
        + "2. Provide evidence for each identified distortion\n"
        + "3. Return ONLY a JSON response\n\n"
        + "## Output Format\n"
        + "You must return ONLY valid JSON in this exact format:\n"
        + "```json\n"
        + "{\n"
        + '  "thought_analyzed": "<the original thought>",\n'
        + '  "identified_distortions": [\n'
        + "    {\n"
        + '      "code": "<distortion code>",\n'
        + '      "name": "<distortion name>",\n'
        + '      "evidence": "<specific part of thought showing this distortion>",\n'
        + '      "confidence": <0.0-1.0>\n'
        + "    }\n"
        + "  ],\n"
        + '  "primary_distortion": "<code of the most prominent distortion>",\n'
        + '  "analysis_notes": "<brief notes about the analysis>"\n'
        + "}\n"
        + "```\n\n"
        + "## Analysis Guidelines\n"
        + "- Look for key words and phrases that indicate specific distortions\n"
        + "- A thought can have multiple distortions\n"
        + "- Focus on the most clear and impactful distortions\n"
        + "- Be specific about which part of the thought shows each distortion\n"
        + "- Only identify distortions you're confident about (confidence > 0.7)\n"
        + "- Maximum 3 distortions per thought\n"
        + distortion_reference
        + "\n\n## Important\n"
        + "- Output ONLY valid JSON, no other text\n"
        + "- Never address the user directly\n"
        + "- Focus on accurate distortion identification"
    )

    return LlmAgent(
        model=model,
        name="ParserAgent",
        instruction=parser_instruction,
        tools=[analyze_thought_for_distortions],
    )
