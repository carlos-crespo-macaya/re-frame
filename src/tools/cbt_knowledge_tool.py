"""
CBT Knowledge Tool

Provides agents with access to CBT domain knowledge including
cognitive distortions, therapeutic techniques, and clinical strategies.
"""

from typing import Any

from ..knowledge.cbt_context import (
    BALANCED_THOUGHT_CRITERIA,
    CBT_MODEL,
    COGNITIVE_DISTORTIONS,
    EVIDENCE_GATHERING,
    MICRO_ACTION_PRINCIPLES,
    THERAPEUTIC_PRINCIPLES,
)


async def query_cbt_knowledge(
    query_type: str, distortion_code: str | None = None
) -> dict[str, Any]:
    """
    Query CBT concepts, cognitive distortions, and therapeutic techniques.

    Args:
        query_type: Type of CBT knowledge to retrieve. Options:
            - "distortion_info": Get info about a specific distortion (requires distortion_code)
            - "all_distortions": List all cognitive distortions
            - "reframing_strategies": Get reframing strategies
            - "micro_actions": Get micro-action suggestions
            - "evidence_gathering": Get evidence gathering techniques
            - "therapeutic_principles": Get core CBT principles
            - "balanced_thought_criteria": Get criteria for balanced thoughts
            - "cbt_model": Get the CBT model explanation
        distortion_code: Specific distortion code (e.g., 'MW', 'FT') when querying distortion info

    Returns:
        Dictionary containing the requested CBT knowledge
    """
    if query_type == "distortion_info":
        if not distortion_code:
            return {
                "error": "distortion_code required for distortion_info query",
                "status": "error",
            }
        for _REDACTED.items():
            if distortion["code"] == distortion_code.upper():
                return {"status": "success", "distortion": distortion}
        return {
            "error": f"Unknown distortion code: {distortion_code}",
            "status": "error",
        }

    elif query_type == "all_distortions":
        return {
            "status": "success",
            "distortions": [
                {
                    "code": d["code"],
                    "name": d["name"],
                    "definition": d["definition"],
                }
                for d in COGNITIVE_DISTORTIONS.values()
            ],
        }

    elif query_type == "reframing_strategies":
        if distortion_code:
            # Get strategies for specific distortion
            for _REDACTED.items():
                if distortion["code"] == distortion_code.upper():
                    return {
                        "status": "success",
                        "distortion": distortion["name"],
                        "strategies": distortion["reframing_strategies"],
                    }
        # Return general evidence gathering techniques
        return {"status": "success", "strategies": EVIDENCE_GATHERING}

    elif query_type == "micro_actions":
        if distortion_code:
            # Get micro-actions for specific distortion
            for _REDACTED.items():
                if distortion["code"] == distortion_code.upper():
                    return {
                        "status": "success",
                        "distortion": distortion["name"],
                        "micro_actions": distortion["micro_actions"],
                    }
        # Return micro-action design principles
        return {"status": "success", "principles": MICRO_ACTION_PRINCIPLES}

    elif query_type == "evidence_gathering":
        return {"status": "success", "techniques": EVIDENCE_GATHERING}

    elif query_type == "therapeutic_principles":
        return {"status": "success", "principles": THERAPEUTIC_PRINCIPLES}

    elif query_type == "balanced_thought_criteria":
        return {"status": "success", "criteria": BALANCED_THOUGHT_CRITERIA}

    elif query_type == "cbt_model":
        return {"status": "success", "model": CBT_MODEL}

    else:
        return {
            "error": f"Unknown query_type: {query_type}",
            "status": "error",
            "valid_types": [
                "distortion_info",
                "all_distortions",
                "reframing_strategies",
                "micro_actions",
                "evidence_gathering",
                "therapeutic_principles",
                "balanced_thought_criteria",
                "cbt_model",
            ],
        }


def get_agent_prompt_for_phase(phase: str) -> list[str]:
    """Get the appropriate prompt file content for a conversation phase."""
    prompts_map = {
        "greeting": "greeting",
        "discovery": "discovery",
        "parser": "parser",
        "reframing": "reframing",
        "summary": "summary",
    }

    if phase not in prompts_map:
        return []

    try:
        from pathlib import Path

        prompt_file = (
            Path(__file__).parent.parent / "prompts" / f"{prompts_map[phase]}.md"
        )
        if prompt_file.exists():
            return [prompt_file.read_text()]
        return []
    except Exception:
        return []


def get_phase_tools(phase: str) -> list[str]:
    """Get the list of tools needed for a specific conversation phase."""
    phase_tools = {
        "greeting": [],
        "discovery": ["query_cbt_knowledge"],
        "parser": ["query_cbt_knowledge"],
        "reframing": ["query_cbt_knowledge"],
        "summary": [],
    }
    return phase_tools.get(phase, [])
