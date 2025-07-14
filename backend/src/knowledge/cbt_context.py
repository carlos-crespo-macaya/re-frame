"""
CBT Domain Knowledge and Context Module

This module contains core CBT knowledge, principles, and guidelines
that are shared across all agents in the system.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# Base instruction template for all agents
BASE_CBT_CONTEXT = """
You are part of a cognitive reframing assistant based on Cognitive Behavioral Therapy (CBT) principles.

Core Guidelines:
- This tool does not replace professional therapy or provide diagnoses
- Use only evidence-based CBT techniques
- Maintain an empathetic, non-judgmental, and collaborative tone
- Focus on thoughts, feelings, and behaviors - not deep psychological analysis
- Encourage users to seek professional help when appropriate

CBT Principles:
- Thoughts, feelings, and behaviors are interconnected
- Identifying and challenging unhelpful thinking patterns can improve wellbeing
- Small behavioral changes can create positive cycles
- Collaboration and guided discovery are more effective than giving advice
"""

# CBT Cognitive Model
CBT_MODEL = {
    "components": ["Situation", "Automatic Thought", "Emotion", "Behavior"],
    "description": "The CBT model shows how thoughts, feelings, and behaviors interact",
    "flow": "Situation → Automatic Thought → Emotion → Behavior",
}

# Core therapeutic principles
THERAPEUTIC_PRINCIPLES = {
    "collaborative_empiricism": "Work with clients as teammates in joint investigation",
    "self_efficacy": "Beliefs stick best when clients discover insights themselves",
    "socratic_questioning": "Use open-ended, gentle inquiry focused on concrete details",
    "behavioral_experiments": "Test beliefs through real-world actions",
    "validation_first": "Always acknowledge emotions before questioning",
    "trauma_informed": "Prioritize safety, trust, empowerment, and collaboration",
}

# Complete cognitive distortions taxonomy
COGNITIVE_DISTORTIONS = {
    "mind_reading": {
        "code": "MW",
        "name": "Mind Reading",
        "definition": "Assuming you know what others are thinking without evidence",
        "examples": ["They think I'm incompetent", "Everyone can see how anxious I am"],
        "reframing_strategies": [
            "What evidence do I have for what they're thinking?",
            "What else might they be thinking?",
            "How could I find out what they actually think?",
        ],
        "micro_actions": [
            "Ask one person directly about their thoughts",
            "Notice when predictions about others' thoughts were wrong",
        ],
    },
    "fortune_telling": {
        "code": "FT",
        "name": "Fortune Telling",
        "definition": "Predicting the future negatively as if it's certain",
        "examples": [
            "I'll definitely fail the interview",
            "Things will never get better",
        ],
        "reframing_strategies": [
            "What are other possible outcomes?",
            "What's the most likely outcome based on past experience?",
            "How certain am I really about this prediction?",
        ],
        "micro_actions": [
            "Write down 3 alternative outcomes",
            "Track prediction accuracy for one week",
        ],
    },
    "catastrophizing": {
        "code": "CT",
        "name": "Catastrophizing",
        "definition": "Blowing things out of proportion or imagining worst-case scenarios",
        "examples": [
            "This mistake will ruin my entire career",
            "If I panic, I'll completely lose control",
        ],
        "reframing_strategies": [
            "What's the worst, best, and most likely outcome?",
            "How have I coped with difficulties before?",
            "Will this matter in 5 years?",
        ],
        "micro_actions": [
            "List past situations you successfully coped with",
            "Rate actual vs predicted severity of one worry",
        ],
    },
    "all_or_nothing": {
        "code": "AO",
        "name": "All-or-Nothing Thinking",
        "definition": "Seeing things in black-and-white categories with no middle ground",
        "examples": [
            "If I'm not perfect, I'm a failure",
            "Either they love me or they hate me",
        ],
        "reframing_strategies": [
            "What would the middle ground look like?",
            "Can I rate this on a scale of 0-100?",
            "What are the shades of gray here?",
        ],
        "micro_actions": [
            "Rate one achievement on a 0-100 scale",
            "Find 3 partial successes in your day",
        ],
    },
    "mental_filter": {
        "code": "MF",
        "name": "Mental Filter",
        "definition": "Focusing exclusively on negatives while filtering out positives",
        "examples": [
            "The whole presentation was terrible (despite mostly positive feedback)",
            "My day was ruined (one bad thing among many good)",
        ],
        "reframing_strategies": [
            "What positive aspects am I overlooking?",
            "What would a balanced view include?",
            "What went well, even if small?",
        ],
        "micro_actions": [
            "Write 3 good things that happened today",
            "Ask someone else what went well",
        ],
    },
    "personalization": {
        "code": "PR",
        "name": "Personalization",
        "definition": "Blaming yourself for things outside your control",
        "examples": [
            "It's my fault they're in a bad mood",
            "The team failed because of me",
        ],
        "reframing_strategies": [
            "What other factors contributed?",
            "What was actually within my control?",
            "Would I blame a friend this much?",
        ],
        "micro_actions": [
            "Create a responsibility pie chart",
            "List factors outside your control",
        ],
    },
    "labeling": {
        "code": "LB",
        "name": "Labeling",
        "definition": "Attaching global negative labels based on single instances",
        "examples": ["I'm a loser", "They're completely selfish"],
        "reframing_strategies": [
            "What specific behavior am I reacting to?",
            "Does one action define a whole person?",
            "What evidence contradicts this label?",
        ],
        "micro_actions": [
            "Replace one label with specific behavior description",
            "List 3 qualities that contradict the label",
        ],
    },
    "should_statements": {
        "code": "SH",
        "name": "Should Statements",
        "definition": "Rigid rules about how things must be, leading to guilt or frustration",
        "examples": [
            "I should always be productive",
            "They should understand without me explaining",
        ],
        "reframing_strategies": [
            "What would I prefer instead of 'should'?",
            "Where did this rule come from?",
            "What happens if this 'should' isn't met?",
        ],
        "micro_actions": [
            "Replace 'should' with 'would like to'",
            "Question one 'should' rule's origin",
        ],
    },
    "emotional_reasoning": {
        "code": "ER",
        "name": "Emotional Reasoning",
        "definition": "Believing something is true because it feels true",
        "examples": [
            "I feel worthless, so I must be worthless",
            "I feel anxious, so there must be danger",
        ],
        "reframing_strategies": [
            "What are the facts separate from feelings?",
            "Have my feelings been wrong before?",
            "What would I tell a friend feeling this way?",
        ],
        "micro_actions": [
            "List facts vs feelings about one situation",
            "Notice when feelings didn't match reality",
        ],
    },
    "discounting_positives": {
        "code": "DP",
        "name": "Discounting Positives",
        "definition": "Dismissing positive experiences or achievements as not counting",
        "examples": [
            "They only complimented me to be nice",
            "I only succeeded because it was easy",
        ],
        "reframing_strategies": [
            "What would it mean to fully accept this positive?",
            "How do I explain others' successes?",
            "What effort did I actually put in?",
        ],
        "micro_actions": [
            "Accept one compliment at face value",
            "Write down your role in one success",
        ],
    },
}

# Evidence gathering techniques
EVIDENCE_GATHERING = {
    "techniques": [
        "What evidence supports this thought?",
        "What evidence goes against it?",
        "What would you tell a friend in this situation?",
        "What's the worst/best/most likely outcome?",
        "Will this matter in 5 years?",
        "What are alternative explanations?",
    ],
    "principles": [
        "Be specific and concrete",
        "Focus on observable facts",
        "Consider multiple perspectives",
        "Examine past experiences",
    ],
}

# Balanced thought criteria
BALANCED_THOUGHT_CRITERIA = {
    "believable": "The person can actually believe it (not fake positivity)",
    "evidence_based": "Grounded in facts and evidence",
    "acknowledges_truth": "Recognizes any grain of truth in the original thought",
    "flexible": "Allows for nuance and complexity",
    "helpful": "Promotes adaptive behavior and emotional regulation",
}

# Micro-action design principles
MICRO_ACTION_PRINCIPLES = {
    "duration": "≤10 minutes to complete",
    "specific": "Clear, concrete, and measurable",
    "achievable": "Within person's current capacity",
    "relevant": "Directly targets the identified distortion",
    "experimental": "Framed as trying something out, not fixing oneself",
}

# Crisis indicators
CRISIS_INDICATORS = [
    "want to die",
    "kill myself",
    "end it all",
    "not worth living",
    "better off dead",
    "suicide",
    "self-harm",
    "hurt myself",
    "cutting",
    "overdose",
    "no point in living",
    "can't go on",
    "ending my life",
    "way out",
]

# Crisis response template
CRISIS_RESPONSE_TEMPLATE = """
I notice you're going through something really difficult right now, and I'm concerned about your safety.

What you're feeling is important, and there are people who want to help:

**Immediate Support:**
- 🇺🇸 US: 988 (Suicide & Crisis Lifeline)
- 🇬🇧 UK: 116 123 (Samaritans)
- 🇦🇺 AU: 13 11 14 (Lifeline)
- 🇨🇦 CA: 833-456-4566

**Text Support:**
- US: Text "HELLO" to 741741
- UK: Text "SHOUT" to 85258

Please reach out to someone - you don't have to go through this alone. If you're in immediate danger, please call emergency services (911/999/112).

Would you like to talk about what's making you feel this way? I'm here to listen.
"""


# Session state initialization
def initialize_session_with_cbt_context(session):
    """Initialize session state with CBT domain knowledge"""
    session.state.update(
        {
            "cbt_guidelines": THERAPEUTIC_PRINCIPLES,
            "distortion_types": list(COGNITIVE_DISTORTIONS.keys()),
            "phase": "greeting",
            "language": "en",
            "safety_flags": [],
        }
    )


# Helper function to create agents with base context
def create_agent_with_context(name, specific_instruction, **kwargs):
    """Create an agent with base CBT context included in instructions"""
    try:
        from google.adk.agents import LlmAgent
    except ImportError as e:
        raise ImportError(
            "Google ADK is not installed. Please install it with: pip install google-adk"
        ) from e

    return LlmAgent(
        name=name,
        instruction=BASE_CBT_CONTEXT + "\n\n" + specific_instruction,
        **kwargs,
    )


# Distortion detection helper
def detect_distortions(thought_text):
    """
    Analyze text for potential cognitive distortions.
    Returns list of likely distortion codes.
    """
    thought_lower = thought_text.lower()
    detected = []

    # Simple keyword-based detection (can be enhanced with NLP)
    # Check for absolute words
    if any(
        word in thought_lower
        for word in ["always", "never", "everyone", "everything", "none", "nothing"]
    ):
        detected.append("AO")

    # Fortune telling - look for future predictions with negative outcomes
    future_words = ["will", "going to", "definitely", "won't", "can't"]
    negative_outcomes = ["fail", "disaster", "embarrass", "handle"]
    if any(word in thought_lower for word in future_words) and any(
        neg in thought_lower for neg in negative_outcomes
    ):
        detected.append("FT")

    if any(word in thought_lower for word in ["should", "must", "have to", "ought"]):
        detected.append("SH")

    # Labeling - check for "I am/I'm" followed by negative labels
    if "i am" in thought_lower or "i'm" in thought_lower:
        labels = ["stupid", "loser", "failure", "worthless", "idiot", "incompetent"]
        if any(label in thought_lower for label in labels):
            detected.append("LB")

    return detected
