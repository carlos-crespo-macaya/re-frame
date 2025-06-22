"""Multi-Framework Synthesis Agent for combining framework outputs."""

from typing import Any

import google.generativeai as genai

from agents.base import ReFrameAgent


class MultiFrameworkSynthesisAgent(ReFrameAgent):
    """
    Synthesizes outputs from multiple therapeutic frameworks into cohesive guidance.

    This agent takes outputs from multiple framework agents (CBT, DBT, ACT, Stoicism)
    and creates an integrated response that leverages the strengths of each approach
    while maintaining coherence and avoiding contradictions.
    """

    def __init__(self):
        """Initialize the Multi-Framework Synthesis Agent."""
        super().__init__(
            name="Multi-Framework Synthesis Agent",
            instructions="""You are a therapeutic synthesis expert integrating multiple psychological frameworks.
Your role is to combine insights from CBT, DBT, ACT, and Stoicism into cohesive, non-contradictory guidance.
Focus on finding 'both/and' integrations rather than 'either/or' conflicts.
Maintain a supportive, non-judgmental tone appropriate for users with AvPD.""",
        )
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def synthesize_responses(
        self,
        framework_outputs: dict[str, dict[str, Any]],
        intake_data: dict[str, Any],
        user_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Synthesize multiple framework outputs into integrated guidance.

        Args:
            framework_outputs: Dict mapping framework names to their outputs
            intake_data: Original intake data from user
            user_context: Optional user preferences and history

        Returns:
            Synthesized response combining all frameworks
        """
        # Handle empty or single framework cases
        if not framework_outputs:
            return {
                "error": "No framework outputs to synthesize",
                "integrated_reframing": "Unable to process request",
                "reasoning_path": ["No frameworks were applied"],
                "combined_techniques": [],
            }

        if len(framework_outputs) == 1:
            # Single framework - return formatted version
            framework_name, output = list(framework_outputs.items())[0]
            return {
                "integrated_reframing": output.get("reframed_thought", ""),
                "reasoning_path": output.get("reasoning_path", []),
                "combined_techniques": output.get("techniques_applied", []),
                "primary_framework": framework_name,
                "framework_contributions": {framework_name: output},
            }

        # Determine synthesis priority
        priority_order = self.get_synthesis_priority(framework_outputs, intake_data)

        # Build synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(
            framework_outputs, intake_data, priority_order, user_context
        )

        # Generate synthesized response
        try:
            response = await self.model.generate_content_async(synthesis_prompt)

            # Parse the response
            parsed_response = self._parse_synthesis_response(
                response.text, framework_outputs, priority_order
            )

            return parsed_response

        except Exception:
            # Fallback to combining frameworks simply
            return self._simple_synthesis_fallback(framework_outputs, priority_order)

    def get_synthesis_priority(
        self, framework_outputs: dict[str, dict[str, Any]], intake_data: dict[str, Any]
    ) -> list[str]:
        """
        Determine priority order for framework synthesis.

        Crisis situations prioritize DBT, otherwise balance frameworks.
        """
        frameworks = list(framework_outputs.keys())

        # Crisis situations always prioritize DBT
        if intake_data.get("is_crisis") or any(
            output.get("is_crisis") for output in framework_outputs.values()
        ):
            if "DBT" in frameworks:
                frameworks.remove("DBT")
                return ["DBT"] + frameworks

        # Otherwise, maintain order they were selected
        return frameworks

    def _build_synthesis_prompt(
        self,
        framework_outputs: dict[str, dict[str, Any]],
        intake_data: dict[str, Any],
        priority_order: list[str],
        user_context: dict[str, Any] | None,
    ) -> str:
        """Build prompt for synthesis generation."""
        prompt = f"""
You are a therapeutic synthesis expert integrating multiple psychological frameworks.

ORIGINAL THOUGHT: {intake_data.get('original_thought', '')}
EMOTION INTENSITY: {intake_data.get('emotion_intensity', 'unknown')}/10

FRAMEWORK OUTPUTS TO SYNTHESIZE:
"""

        for framework in priority_order:
            output = framework_outputs[framework]
            prompt += f"""
{framework}:
- Reframed Thought: {output.get('reframed_thought', '')}
- Techniques: {', '.join(output.get('techniques_applied', []))}
- Key Insights: {'; '.join(output.get('reasoning_path', [])[:2])}
"""

        if user_context and "framework_effectiveness" in user_context:
            prompt += f"""
USER PREFERENCES:
Most effective frameworks for this user: {user_context['framework_effectiveness']}
"""

        prompt += """
SYNTHESIS INSTRUCTIONS:
1. Create an integrated reframing that combines insights from all frameworks
2. Ensure the message is coherent and non-contradictory
3. If frameworks seem to conflict, find the "both/and" integration
4. For crisis situations, maintain DBT's safety focus as primary
5. Keep language supportive and non-judgmental
6. Make it clear which framework contributed which insight

FORMAT YOUR RESPONSE AS:
**Integrated Reframing:**
[Your synthesized reframing that combines all frameworks coherently]

**Combined Techniques:**
- [Technique 1 (Framework)]: Brief description
- [Technique 2 (Framework)]: Brief description
[List all techniques from all frameworks]

**Reasoning Path:**
1. [First integrated insight combining frameworks]
2. [Second integrated insight]
[etc. - show how frameworks work together]

**Framework Contributions:**
- [Framework 1]: [What it uniquely contributed]
- [Framework 2]: [What it uniquely contributed]
[etc.]

Remember: This is peer support for someone with AvPD. Be validating and gentle.
"""
        return prompt

    def _parse_synthesis_response(
        self,
        response_text: str,
        framework_outputs: dict[str, dict[str, Any]],
        priority_order: list[str],
    ) -> dict[str, Any]:
        """Parse the synthesis response from the model."""
        # Extract sections from response
        sections = {
            "integrated_reframing": "",
            "combined_techniques": [],
            "reasoning_path": [],
            "framework_contributions": {},
        }

        # Simple parsing logic
        current_section = None
        lines = response_text.strip().split("\n")

        for line in lines:
            line = line.strip()

            if "**Integrated Reframing:**" in line:
                current_section = "integrated_reframing"
            elif "**Combined Techniques:**" in line:
                current_section = "combined_techniques"
            elif "**Reasoning Path:**" in line:
                current_section = "reasoning_path"
            elif "**Framework Contributions:**" in line:
                current_section = "framework_contributions"
            elif line and current_section:
                if current_section == "integrated_reframing":
                    sections["integrated_reframing"] += line + " "
                elif current_section == "combined_techniques" and line.startswith("- "):
                    sections["combined_techniques"].append(line[2:])
                elif current_section == "reasoning_path" and line[0].isdigit():
                    sections["reasoning_path"].append(
                        line.split(". ", 1)[1] if ". " in line else line
                    )
                elif current_section == "framework_contributions" and line.startswith("- "):
                    parts = line[2:].split(": ", 1)
                    if len(parts) == 2:
                        sections["framework_contributions"][parts[0]] = parts[1]

        # Clean up integrated reframing
        sections["integrated_reframing"] = sections["integrated_reframing"].strip()

        # Add metadata
        sections["frameworks_used"] = priority_order
        sections["synthesis_approach"] = "integrated" if len(framework_outputs) > 1 else "single"

        # Ensure we have all techniques from all frameworks
        if not sections["combined_techniques"]:
            for fw_name, fw_output in framework_outputs.items():
                for technique in fw_output.get("techniques_applied", []):
                    sections["combined_techniques"].append(f"{technique} ({fw_name})")

        return sections

    def _simple_synthesis_fallback(
        self, framework_outputs: dict[str, dict[str, Any]], priority_order: list[str]
    ) -> dict[str, Any]:
        """Simple fallback synthesis if AI generation fails."""
        # Combine reframed thoughts
        reframings = []
        all_techniques = []
        all_reasoning = []

        for framework in priority_order:
            output = framework_outputs[framework]
            if "reframed_thought" in output:
                reframings.append(f"{framework}: {output['reframed_thought']}")
            all_techniques.extend(
                [f"{t} ({framework})" for t in output.get("techniques_applied", [])]
            )
            all_reasoning.extend([f"{framework} - {r}" for r in output.get("reasoning_path", [])])

        integrated = " AND ".join(reframings) if reframings else "Multiple perspectives available"

        return {
            "integrated_reframing": integrated,
            "combined_techniques": all_techniques,
            "reasoning_path": all_reasoning[:5],  # Limit to top 5
            "framework_contributions": framework_outputs,
            "frameworks_used": priority_order,
            "synthesis_approach": "fallback",
        }

