"""ADK Tools for re-frame agents."""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from google.adk.core.types import Tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ThoughtAnalysisInput(BaseModel):
    """Input schema for thought analysis tool."""
    
    thought: str = Field(description="The user's thought to analyze")
    context: Optional[str] = Field(default=None, description="Additional context about the situation")


class ThoughtAnalysisOutput(BaseModel):
    """Output schema for thought analysis tool."""
    
    cognitive_distortions: List[str] = Field(description="Identified cognitive distortions")
    emotional_intensity: int = Field(description="Emotional intensity from 1-10")
    avpd_patterns: List[str] = Field(description="AvPD-specific patterns identified")
    recommendations: List[str] = Field(description="Recommended CBT techniques")


class CrisisAssessmentInput(BaseModel):
    """Input schema for crisis assessment tool."""
    
    content: str = Field(description="Content to assess for crisis indicators")
    urgency_level: Optional[str] = Field(default="standard", description="Assessment urgency level")


class CrisisAssessmentOutput(BaseModel):
    """Output schema for crisis assessment tool."""
    
    crisis_risk_level: str = Field(description="Risk level: low, medium, high, critical")
    immediate_action_required: bool = Field(description="Whether immediate action is required")
    risk_factors: List[str] = Field(description="Identified risk factors")
    recommended_resources: List[str] = Field(description="Recommended crisis resources")


def create_thought_analysis_tool() -> Tool:
    """Create a tool for analyzing user thoughts for cognitive distortions and patterns."""
    
    def analyze_thought(input_data: ThoughtAnalysisInput) -> ThoughtAnalysisOutput:
        """Analyze a thought for cognitive distortions and AvPD patterns."""
        thought = input_data.thought.lower()
        context = (input_data.context or "").lower()
        
        # Identify cognitive distortions
        distortions = []
        distortion_patterns = {
            "all_or_nothing": [r"\b(always|never|everyone|no one|everything|nothing)\b"],
            "catastrophizing": [r"\b(disaster|terrible|awful|worst|end of the world)\b"],
            "mind_reading": [r"\b(they think|he thinks|she thinks|everyone thinks)\b"],
            "fortune_telling": [r"\b(will fail|going to|definitely|certainly|bound to)\b"],
            "emotional_reasoning": [r"\b(feel like|feels like|i feel)\b.*\b(so it must be|therefore|means)\b"],
            "should_statements": [r"\b(should|must|have to|ought to|supposed to)\b"],
            "labeling": [r"\b(i am|i'm).*\b(stupid|idiot|loser|failure|worthless)\b"],
            "personalization": [r"\b(my fault|i caused|because of me)\b"],
        }
        
        for distortion, patterns in distortion_patterns.items():
            for pattern in patterns:
                if re.search(pattern, thought):
                    distortions.append(distortion)
                    break
        
        # Identify AvPD-specific patterns
        avpd_patterns = []
        avpd_pattern_checks = {
            "fear_of_criticism": [r"\b(judge|criticize|disapprove|think badly)\b"],
            "social_avoidance": [r"\b(avoid|stay away|don't want to|cancel|skip)\b.*\b(social|people|meeting)\b"],
            "inadequacy_feelings": [r"\b(not good enough|inadequate|inferior|less than)\b"],
            "rejection_sensitivity": [r"\b(reject|abandon|leave me|don't want me)\b"],
            "perfectionism": [r"\b(perfect|flawless|mistake|error|wrong)\b"],
        }
        
        for pattern_name, patterns in avpd_pattern_checks.items():
            for pattern in patterns:
                if re.search(pattern, thought):
                    avpd_patterns.append(pattern_name)
                    break
        
        # Assess emotional intensity (basic heuristic)
        intensity_indicators = {
            r"\b(extremely|incredibly|absolutely|completely)\b": 3,
            r"\b(very|really|so)\b": 2,
            r"\b(quite|pretty|fairly)\b": 1,
            r"\b(!!!|multiple exclamation)\b": 2,
            r"\b(horrible|terrible|awful|devastating)\b": 3,
        }
        
        emotional_intensity = 5  # baseline
        for pattern, intensity_boost in intensity_indicators.items():
            if re.search(pattern, thought):
                emotional_intensity += intensity_boost
        
        emotional_intensity = min(10, max(1, emotional_intensity))
        
        # Generate recommendations based on identified patterns
        recommendations = []
        if "all_or_nothing" in distortions:
            recommendations.append("cognitive_restructuring")
        if "catastrophizing" in distortions:
            recommendations.append("decatastrophizing")
        if "fear_of_criticism" in avpd_patterns:
            recommendations.append("self_compassion_exercises")
        if "social_avoidance" in avpd_patterns:
            recommendations.append("gradual_exposure")
        if emotional_intensity > 7:
            recommendations.append("emotion_regulation")
        
        # Default recommendations if none identified
        if not recommendations:
            recommendations = ["cognitive_restructuring", "mindfulness"]
        
        return ThoughtAnalysisOutput(
            cognitive_distortions=distortions,
            emotional_intensity=emotional_intensity,
            avpd_patterns=avpd_patterns,
            recommendations=recommendations
        )
    
    return Tool(
        name="analyze_thought",
        description="Analyze user thoughts for cognitive distortions and AvPD-specific patterns",
        input_schema=ThoughtAnalysisInput.model_json_schema(),
        function=analyze_thought
    )


def create_crisis_assessment_tool() -> Tool:
    """Create a tool for assessing crisis risk in user content."""
    
    def assess_crisis_risk(input_data: CrisisAssessmentInput) -> CrisisAssessmentOutput:
        """Assess content for crisis indicators and risk level."""
        content = input_data.content.lower()
        
        # Crisis keywords with severity levels
        critical_keywords = [
            r"\b(suicide|kill myself|end my life|want to die)\b",
            r"\b(hurt myself|harm myself|cut myself)\b",
            r"\b(better off dead|can't go on|no point living)\b"
        ]
        
        high_keywords = [
            r"\b(hopeless|worthless|burden|pain is too much)\b",
            r"\b(no one cares|alone|isolated|give up)\b",
            r"\b(escape|way out|end it all)\b"
        ]
        
        medium_keywords = [
            r"\b(depressed|anxious|overwhelmed|can't cope)\b",
            r"\b(stressed|struggling|difficult|hard)\b"
        ]
        
        # Assess risk level
        risk_level = "low"
        risk_factors = []
        immediate_action = False
        
        # Check for critical indicators
        for pattern in critical_keywords:
            if re.search(pattern, content):
                risk_level = "critical"
                immediate_action = True
                risk_factors.append("direct_self_harm_mention")
                break
        
        # Check for high indicators if not critical
        if risk_level != "critical":
            for pattern in high_keywords:
                if re.search(pattern, content):
                    if risk_level != "high":
                        risk_level = "high"
                    risk_factors.append("high_risk_language")
        
        # Check for medium indicators
        if risk_level not in ["critical", "high"]:
            for pattern in medium_keywords:
                if re.search(pattern, content):
                    risk_level = "medium"
                    risk_factors.append("emotional_distress_indicators")
                    break
        
        # Additional risk factors
        if re.search(r"\b(plan|method|when|how)\b.*\b(hurt|harm|kill|end)\b", content):
            risk_factors.append("planning_indicators")
            if risk_level in ["low", "medium"]:
                risk_level = "high"
        
        if re.search(r"\b(goodbye|final|last time|won't see)\b", content):
            risk_factors.append("farewell_language")
            if risk_level == "low":
                risk_level = "medium"
        
        # Recommended resources based on risk level
        recommended_resources = []
        if risk_level == "critical":
            recommended_resources = [
                "988_suicide_crisis_lifeline",
                "emergency_services_911",
                "crisis_text_line_741741",
                "immediate_professional_help"
            ]
        elif risk_level == "high":
            recommended_resources = [
                "988_suicide_crisis_lifeline",
                "crisis_text_line_741741",
                "mental_health_professional",
                "trusted_friend_or_family"
            ]
        elif risk_level == "medium":
            recommended_resources = [
                "mental_health_professional",
                "support_groups",
                "trusted_friend_or_family",
                "crisis_text_line_741741"
            ]
        else:
            recommended_resources = [
                "self_care_resources",
                "mental_health_professional_if_needed"
            ]
        
        return CrisisAssessmentOutput(
            crisis_risk_level=risk_level,
            immediate_action_required=immediate_action,
            risk_factors=risk_factors,
            recommended_resources=recommended_resources
        )
    
    return Tool(
        name="assess_crisis_risk",
        description="Assess content for crisis indicators and determine appropriate response",
        input_schema=CrisisAssessmentInput.model_json_schema(),
        function=assess_crisis_risk
    )


class CBTTechniqueInput(BaseModel):
    """Input schema for CBT technique selection tool."""
    
    distortions: List[str] = Field(description="Identified cognitive distortions")
    avpd_patterns: List[str] = Field(description="AvPD-specific patterns")
    emotional_intensity: int = Field(description="Emotional intensity 1-10")
    user_readiness: str = Field(default="medium", description="User's readiness for change: low, medium, high")


class CBTTechniqueOutput(BaseModel):
    """Output schema for CBT technique selection."""
    
    primary_techniques: List[str] = Field(description="Primary CBT techniques to use")
    secondary_techniques: List[str] = Field(description="Secondary techniques for follow-up")
    approach_notes: str = Field(description="Notes on how to approach the user")
    gentleness_level: str = Field(description="Recommended gentleness level: high, medium, low")


def create_cbt_technique_selector() -> Tool:
    """Create a tool for selecting appropriate CBT techniques."""
    
    def select_cbt_techniques(input_data: CBTTechniqueInput) -> CBTTechniqueOutput:
        """Select appropriate CBT techniques based on user presentation."""
        
        distortions = input_data.distortions
        avpd_patterns = input_data.avpd_patterns
        emotional_intensity = input_data.emotional_intensity
        user_readiness = input_data.user_readiness
        
        primary_techniques = []
        secondary_techniques = []
        
        # Map distortions to techniques
        distortion_technique_map = {
            "all_or_nothing": ["cognitive_restructuring", "balanced_thinking"],
            "catastrophizing": ["decatastrophizing", "probability_estimation"],
            "mind_reading": ["evidence_examination", "alternative_explanations"],
            "fortune_telling": ["reality_testing", "evidence_for_against"],
            "emotional_reasoning": ["thought_emotion_distinction", "evidence_examination"],
            "should_statements": ["flexible_thinking", "preference_vs_demand"],
            "labeling": ["self_compassion", "behavioral_evidence"],
            "personalization": ["responsibility_reattribution", "external_factors_analysis"],
        }
        
        # Map AvPD patterns to techniques
        avpd_technique_map = {
            "fear_of_criticism": ["self_compassion", "criticism_coping_skills"],
            "social_avoidance": ["gradual_exposure", "social_skills_practice"],
            "inadequacy_feelings": ["strength_identification", "achievement_review"],
            "rejection_sensitivity": ["relationship_reframing", "secure_attachment_building"],
            "perfectionism": ["good_enough_standards", "mistake_normalization"],
        }
        
        # Select techniques based on identified patterns
        for distortion in distortions:
            if distortion in distortion_technique_map:
                primary_techniques.extend(distortion_technique_map[distortion])
        
        for pattern in avpd_patterns:
            if pattern in avpd_technique_map:
                primary_techniques.extend(avpd_technique_map[pattern])
        
        # Remove duplicates while preserving order
        primary_techniques = list(dict.fromkeys(primary_techniques))
        
        # Adjust for emotional intensity
        if emotional_intensity > 7:
            primary_techniques.insert(0, "emotional_regulation")
            secondary_techniques.append("grounding_techniques")
        
        # Adjust for user readiness
        if user_readiness == "low":
            # Focus on gentler, more accepting techniques first
            gentle_techniques = [
                "validation", "self_compassion", "psychoeducation"
            ]
            primary_techniques = gentle_techniques + primary_techniques
            gentleness_level = "high"
        elif user_readiness == "high":
            # Can use more challenging techniques
            secondary_techniques.extend([
                "behavioral_experiments", "exposure_exercises"
            ])
            gentleness_level = "medium"
        else:
            gentleness_level = "high"  # Default to high gentleness for AvPD
        
        # Ensure we always have some techniques
        if not primary_techniques:
            primary_techniques = ["cognitive_restructuring", "self_compassion"]
        
        # Limit to top 3 primary techniques to avoid overwhelming
        primary_techniques = primary_techniques[:3]
        
        # Generate approach notes
        approach_notes = f"Use {gentleness_level} gentleness approach. "
        if emotional_intensity > 7:
            approach_notes += "High emotional intensity - prioritize validation and emotional regulation. "
        if "fear_of_criticism" in avpd_patterns:
            approach_notes += "Avoid any language that could feel critical or judgmental. "
        if user_readiness == "low":
            approach_notes += "Focus on building rapport and providing psychoeducation before challenging thoughts. "
        
        return CBTTechniqueOutput(
            primary_techniques=primary_techniques,
            secondary_techniques=secondary_techniques,
            approach_notes=approach_notes,
            gentleness_level=gentleness_level
        )
    
    return Tool(
        name="select_cbt_techniques",
        description="Select appropriate CBT techniques based on user's cognitive patterns and readiness",
        input_schema=CBTTechniqueInput.model_json_schema(),
        function=select_cbt_techniques
    )


def get_all_reframe_tools() -> List[Tool]:
    """Get all re-frame ADK tools."""
    return [
        create_thought_analysis_tool(),
        create_crisis_assessment_tool(),
        create_cbt_technique_selector(),
    ]