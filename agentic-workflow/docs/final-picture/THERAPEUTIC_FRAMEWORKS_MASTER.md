# Therapeutic Frameworks Master Documentation

## Executive Summary

This document provides comprehensive details about the therapeutic frameworks implemented in the Re-frame project, based on GitHub issues #40, #57-#61. The current implementation appears to be an oversimplification that needs to be enhanced with complex, specialized framework-related theory and sophisticated agent capabilities.

## Overview of Multi-Framework System

### Current State
The existing implementation has a single orchestrator agent that attempts to handle all frameworks in one prompt, which lacks the depth and specialization required for meaningful therapeutic support.

### Target Architecture
A sophisticated multi-agent system where each framework has its own specialized agent with deep domain knowledge, specific tools, and framework-appropriate interventions.

## Framework 1: Cognitive Behavioral Therapy (CBT)

### Core Principles
CBT focuses on identifying and changing negative thought patterns and behaviors. It's based on the cognitive model that suggests our thoughts, feelings, and behaviors are interconnected.

### Key Components for AvPD

#### 1. Cognitive Distortion Identification
**Implementation Requirements:**
- **Mind Reading**: "They think I'm boring" → Assuming knowledge of others' thoughts
- **Fortune Telling**: "I'll embarrass myself" → Predicting negative futures
- **Catastrophizing**: "If I stutter, my life is over" → Worst-case thinking
- **All-or-Nothing**: "If not perfect, I'm worthless" → Black-and-white thinking
- **Mental Filtering**: Focusing only on negatives
- **Personalization**: Taking responsibility for external events
- **Labeling**: "I'm a loser" → Global self-judgments
- **Should Statements**: Rigid rules creating pressure

#### 2. Thought Challenging Techniques
```python
class ThoughtChallengingTool:
    def evidence_for_against(self, thought):
        # Systematic evaluation of evidence
        # Returns balanced perspective
    
    def alternative_explanations(self, situation):
        # Generate multiple interpretations
        # Challenge single explanation bias
    
    def best_worst_likely(self, worry):
        # Reality test catastrophic predictions
        # Identify most probable outcome
```

#### 3. Behavioral Experiments
- Prediction testing against reality
- Graded exposure planning
- Outcome tracking and analysis

#### 4. Core Belief Work
**AvPD-Specific Core Beliefs:**
- "I am fundamentally flawed/defective"
- "Others are critical and rejecting"
- "The world is dangerous for people like me"
- "I must be perfect to be accepted"

**Techniques:**
- Downward Arrow technique
- Historical evidence review
- Core belief logs

### Agent Implementation Specification

```python
class CBTFrameworkAgent(ADKBaseAgent):
    """
    Specialized CBT agent with deep understanding of cognitive therapy
    principles and AvPD-specific adaptations.
    """
    
    tools = [
        DistortionIdentifierTool(),
        ThoughtChallengeTool(),
        BehavioralExperimentTool(),
        CoreBeliefAnalyzerTool(),
        ThoughtRecordTool()
    ]
    
    def __init__(self):
        self.system_prompt = """
        You are a CBT therapist specializing in AvPD. Use Socratic questioning,
        collaborative empiricism, and gentle challenging. Focus on specific 
        situations, validate emotions while examining thoughts, and suggest
        small behavioral experiments.
        """
```

### Example CBT Process Flow
```json
{
  "input": {
    "thought": "My colleague didn't smile at me. I must have done something wrong.",
    "emotion": "anxiety, guilt",
    "intensity": 7
  },
  "process": {
    "1_identify_distortions": ["Mind Reading", "Personalization"],
    "2_socratic_questions": [
      "What evidence do you have that their behavior was about you?",
      "What other explanations might there be?"
    ],
    "3_evidence_analysis": {
      "for": ["They didn't smile"],
      "against": ["No feedback about wrongdoing", "Could be stressed"]
    },
    "4_balanced_thought": "Their lack of smile could mean many things",
    "5_behavioral_experiment": "Greet them tomorrow and observe response"
  }
}
```

## Framework 2: Dialectical Behavior Therapy (DBT)

### Core Principles
DBT combines acceptance strategies with change strategies, focusing on building skills for distress tolerance, emotion regulation, interpersonal effectiveness, and mindfulness.

### Key Components for AvPD

#### 1. Distress Tolerance Module
**TIPP** (Temperature, Intense exercise, Paced breathing, Paired muscle relaxation)
- Crisis survival skills for high distress moments
- Immediate physiological regulation

**ACCEPTS** (Activities, Contributing, Comparisons, Emotions, Push away, Thoughts, Sensations)
- Distraction and self-soothing techniques

**IMPROVE** (Imagery, Meaning, Prayer, Relaxation, One thing, Vacation, Encouragement)
- Improving the moment strategies

#### 2. Emotion Regulation Module
**PLEASE** (PhysicaL illness, Eating, mood-Altering substances, Sleep, Exercise)
- Vulnerability factor management

**Check the Facts**
- Reality testing emotional responses

**Opposite Action**
- Acting opposite to emotion urges when not justified

#### 3. Interpersonal Effectiveness Module
**DEARMAN** (Describe, Express, Assert, Reinforce, Mindful, Appear confident, Negotiate)
- Objective effectiveness in relationships

**GIVE** (Gentle, Interested, Validate, Easy manner)
- Relationship preservation skills

**FAST** (Fair, Apologies, Stick to values, Truthful)
- Self-respect effectiveness

#### 4. Mindfulness (Core to all modules)
**Wise Mind**
- Balance of emotion mind and reasonable mind

**What/How Skills**
- Observe, Describe, Participate / Non-judgmentally, One-mindfully, Effectively

### Agent Implementation Specification

```python
class DBTFrameworkAgent(ADKBaseAgent):
    """
    DBT specialist focusing on dialectical balance between
    acceptance and change for AvPD challenges.
    """
    
    tools = [
        DistressToleranceTool(),
        EmotionRegulationTool(),
        InterpersonalEffectivenessTool(),
        MindfulnessTool()
    ]
    
    def __init__(self):
        self.system_prompt = """
        You are a DBT therapist specializing in AvPD. Balance validation
        with change. Use 'AND' statements, not 'BUT'. Prioritize distress
        tolerance in crisis. Teach specific DBT skills with acronyms when
        helpful but avoid overwhelming.
        """
```

### DBT Dialectical Approach
```json
{
  "situation": "Overwhelming party invitation",
  "dialectical_response": {
    "acceptance": "It's understandable to feel anxious about social events",
    "change": "AND you have skills to cope with this anxiety",
    "synthesis": "You can feel anxious AND still choose to attend with support",
    "skills_menu": ["TIPP before entering", "PLEASE check", "DEARMAN for boundaries"]
  }
}
```

## Framework 3: Acceptance and Commitment Therapy (ACT)

### Core Principles
ACT focuses on psychological flexibility through six core processes: contact with present moment, acceptance, cognitive defusion, self-as-context, values clarification, and committed action.

### Key Components for AvPD

#### 1. Present Moment Awareness
- 5-4-3-2-1 grounding exercise
- Mindful breathing anchors
- Here-and-now focus vs. anxious predictions

#### 2. Acceptance (Willingness)
- Expansion exercises for difficult emotions
- Struggle switch metaphor
- Guest house metaphor (Rumi)

#### 3. Cognitive Defusion
**Techniques:**
- "I'm having the thought that..."
- Singing thoughts to silly tunes
- Leaves on a stream visualization
- Thank your mind practice

#### 4. Self-as-Context
- Chessboard metaphor (board vs. pieces)
- Sky and weather metaphor
- Continuous self exercises

#### 5. Values Clarification
- Values card sort for AvPD
- Sweet spot identification
- Values vs. goals distinction

#### 6. Committed Action
- Willingness scale (1-10)
- Baby steps toward values
- Passengers on the bus metaphor

### Agent Implementation Specification

```python
class ACTFrameworkAgent(ADKBaseAgent):
    """
    ACT specialist focusing on psychological flexibility
    and values-based action despite anxiety.
    """
    
    tools = [
        MindfulnessTool(),
        AcceptanceTool(),
        DefusionTool(),
        ObserverSelfTool(),
        ValuesClarificationTool(),
        CommittedActionTool()
    ]
    
    def __init__(self):
        self.system_prompt = """
        You are an ACT therapist specializing in AvPD. Normalize difficult
        experiences, use defusion for thought believability, connect to
        values not anxiety reduction. Emphasize willingness over willpower.
        Never promise anxiety will disappear.
        """
```

### ACT Values-Based Action
```json
{
  "thought": "I want to join the book club but I'll embarrass myself",
  "act_intervention": {
    "defusion": "Notice 'I'll embarrass myself' is your mind's prediction",
    "values_exploration": "Intellectual connection matters to you",
    "acceptance": "Fear is normal when approaching something meaningful",
    "metaphor": "Like sailing by stars (values) not avoiding storms (anxiety)",
    "committed_action": "Attend first 15 minutes with anxiety as companion",
    "willingness_check": "How willing are you to feel awkward for connection?"
  }
}
```

## Framework 4: Stoicism

### Core Principles
Stoic philosophy emphasizes accepting what we cannot control while taking responsibility for what we can, focusing on virtue over external validation.

### Key Components for AvPD

#### 1. Dichotomy of Control
**In Our Control:**
- Our judgments and responses
- Our efforts and intentions
- Our character and choices

**Not In Our Control:**
- Others' opinions and reactions
- Outcomes and external events
- Past and future

#### 2. Negative Visualization (Premeditatio Malorum)
- Gentle preparation without catastrophizing
- Outcome independence
- Resilience through mental rehearsal

#### 3. View from Above (Cosmic Perspective)
- Zoom out exercises
- Temporal perspective
- Universal human experience

#### 4. Virtue Ethics
**Four Cardinal Virtues:**
- **Wisdom**: Understanding what's truly important
- **Justice**: Treating self and others fairly
- **Courage**: Acting despite fear
- **Temperance**: Balance and moderation

#### 5. Amor Fati (Love of Fate)
- Reframing challenges as teachers
- Finding hidden opportunities
- Strength through adversity

#### 6. Present Moment Focus
- Avoiding rumination on past
- Not projecting into future
- Action in the present

### Agent Implementation Specification

```python
class StoicismFrameworkAgent(ADKBaseAgent):
    """
    Stoic philosophy specialist adapting ancient wisdom
    for modern AvPD challenges.
    """
    
    tools = [
        DichotomyOfControlTool(),
        NegativeVisualizationTool(),
        CosmicPerspectiveTool(),
        VirtueEthicsTool(),
        AmorFatiTool(),
        PresentMomentTool()
    ]
    
    def __init__(self):
        self.system_prompt = """
        You are a Stoic philosopher specializing in social anxiety and AvPD.
        Channel Marcus Aurelius, Epictetus, and Seneca with warmth. Distinguish
        controllable from uncontrollable, emphasize virtue over reputation,
        use accessible metaphors, balance acceptance with action.
        """
```

### Stoic Wisdom Application
```json
{
  "thought": "They didn't invite me. I'm clearly unwanted.",
  "stoic_response": {
    "control_analysis": {
      "your_control": ["Your response", "Your character", "Future choices"],
      "not_your_control": ["Their decisions", "Their reasons", "The past"]
    },
    "virtue_focus": "You showed courage by being open to connection",
    "perspective": "In your life's story, this is one small chapter",
    "practical_wisdom": "Focus on being a good friend, not being seen as one",
    "quote": "Epictetus: 'It's not what happens to you, but how you react.'"
  }
}
```

## Multi-Framework Integration Strategy

### Framework Selection Logic

```python
class FrameworkSelector:
    def select_frameworks(self, thought_record, user_context):
        """
        Intelligently selects 1-3 frameworks based on:
        - Thought pattern analysis
        - Emotional intensity
        - User preferences
        - Situation type
        """
        
        selection_criteria = {
            "catastrophizing": "CBT",  # Best for thought challenging
            "high_distress": "DBT",    # Best for crisis skills
            "values_conflict": "ACT",   # Best for values clarity
            "control_struggle": "Stoicism"  # Best for acceptance
        }
        
        # Also considers complementary pairings:
        # CBT + Stoicism: Thought work + acceptance
        # DBT + ACT: Distress tolerance + values
        # ACT + Stoicism: Values + virtue ethics
```

### Synthesis Patterns

#### Pattern 1: Layered Integration
```
Foundation: Stoicism (accept uncontrollables)
    ↓
Skills: DBT (manage distress)
    ↓
Direction: ACT (values-based action)
    ↓
Refinement: CBT (specific thoughts)
```

#### Pattern 2: Crisis vs Growth
- **Crisis Mode**: DBT → Stoicism → Simple action
- **Growth Mode**: ACT → CBT → Stoic reflection

### Enhanced Synthesis Agent

```python
class EnhancedSynthesisAgent(ADKBaseAgent):
    """
    Weaves insights from multiple frameworks into
    cohesive, personalized responses.
    """
    
    def synthesize_responses(self, framework_outputs):
        # Extract core insights
        # Map complementary elements
        # Resolve contradictions
        # Create unified narrative
        # Personalize for user
        
        synthesis_rules = [
            "No contradictions between frameworks",
            "Maintain coherent therapeutic voice",
            "Progress from acceptance to action",
            "Prioritize safety in crisis",
            "Adapt to user preferences"
        ]
```

## Implementation Roadmap

### Phase 1: Individual Framework Agents
1. Implement each framework agent with full capabilities
2. Create framework-specific tools and prompts
3. Test individual framework effectiveness

### Phase 2: Integration Layer
1. Build framework selector logic
2. Implement parallel processing
3. Create synthesis rules engine

### Phase 3: Personalization
1. User preference tracking
2. Framework effectiveness metrics
3. Adaptive selection algorithms

### Phase 4: Advanced Features
1. Session continuity
2. Progress tracking
3. Homework suggestions
4. Crisis protocols

## Quality Assurance Requirements

### Framework Fidelity
- Each agent must accurately represent its therapeutic approach
- Techniques must be evidence-based and properly adapted for AvPD
- Language must be accessible while maintaining theoretical integrity

### Integration Coherence
- No contradictory advice between frameworks
- Smooth transitions between approaches
- Clear explanation of which framework is being used and why

### User Experience
- Responses must not overwhelm with technical jargon
- Each response should include at least one actionable suggestion
- Emotional validation must be present in all frameworks

## Technical Implementation Considerations

### Agent Architecture
```python
# Base class for all framework agents
class TherapeuticFrameworkAgent(ADKBaseAgent):
    def __init__(self, framework_name, system_prompt, tools):
        super().__init__(
            name=f"{framework_name} Framework Agent",
            system_prompt=system_prompt,
            tools=tools
        )
    
    @abstractmethod
    async def apply_framework(self, thought_record):
        """Each framework implements its specific approach"""
        pass
    
    def adapt_for_avpd(self, intervention):
        """Ensures all interventions consider AvPD sensitivity"""
        return self._soften_language(
            self._add_validation(
                self._reduce_social_pressure(intervention)
            )
        )
```

### Data Models Enhancement
```python
class FrameworkOutput(BaseModel):
    framework: str
    techniques_used: List[str]
    key_insights: List[str]
    reframes: List[ReframedThought]
    action_suggestions: List[ActionItem]
    metaphors_used: List[str]
    homework: Optional[List[HomeworkAssignment]]
    confidence_level: float
    
class TherapeuticResponse(BaseModel):
    primary_framework: str
    secondary_frameworks: List[str]
    integrated_message: str
    framework_specific_insights: Dict[str, FrameworkOutput]
    unified_action_plan: List[ActionItem]
    session_notes: str
    follow_up_suggestions: List[str]
```

## Conclusion

The current implementation lacks the depth and sophistication required for meaningful therapeutic support. By implementing specialized agents for each framework with deep domain knowledge, framework-specific tools, and intelligent integration, we can create a system that provides genuinely helpful, theoretically sound, and practically applicable support for people with AvPD.

Each framework brings unique strengths:
- **CBT**: Systematic thought challenging and behavioral change
- **DBT**: Crisis skills and dialectical balance
- **ACT**: Values-based action and psychological flexibility  
- **Stoicism**: Wisdom, acceptance, and virtue focus

The key is not just implementing these frameworks individually, but creating an intelligent integration system that knows when and how to apply each approach for maximum therapeutic benefit.