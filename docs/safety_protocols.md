# Safety Protocols for Reframe Agents

## Overview

The Reframe Agents CBT chatbot includes comprehensive safety features to detect and respond appropriately to users in crisis. This document outlines the safety protocols implemented in the system.

## Crisis Detection

### Detection Categories

The system monitors for four main categories of crisis indicators:

1. **Suicide Risk**
   - Direct statements about ending life
   - Expressions of hopelessness
   - Statements about being better off dead

2. **Self-Harm Risk**
   - Mentions of cutting or self-injury
   - Expressions of wanting to hurt oneself
   - References to self-harm behaviors

3. **Violence Risk**
   - Threats to harm others
   - Violent thoughts or intentions
   - Homicidal ideation

4. **Immediate Danger**
   - Time-specific threats (tonight, now, today)
   - Concrete plans or methods mentioned
   - Urgent language combined with crisis indicators

### Context Awareness

The system considers context to reduce false positives:

- **Past Tense**: References to previous experiences are handled with lower priority
- **Academic Context**: Research or educational discussions are recognized
- **Third-Party References**: Discussions about others' experiences

## Response System

### Severity Levels

1. **Critical** (Immediate Danger/Active Suicide)
   - Immediate safety resources provided
   - Session focus shifts to crisis intervention
   - Multiple emergency contact options given

2. **High** (Self-Harm/Violence)
   - Crisis resources prominently displayed
   - Encouragement to seek immediate help
   - Follow-up questions about safety

3. **Medium** (General Crisis Indicators)
   - Professional resources suggested
   - Coping strategies offered if appropriate
   - Gentle redirection to professional help

### Response Components

Each crisis response includes:
- Validation of the user's distress
- Immediate resource provision
- Clear action steps
- Follow-up questions when appropriate

## Resource Provision

### Geographic Coverage

The system provides location-specific resources for:
- United States (988 Lifeline, Crisis Text Line)
- United Kingdom (Samaritans, SHOUT)
- Canada (Talk Suicide Canada)
- Australia (Lifeline, Beyond Blue)
- International (Befrienders Worldwide)

### Resource Types

1. **Emergency Contacts**
   - Country-specific emergency numbers (911, 999, 112)
   - National crisis hotlines

2. **24/7 Support Services**
   - Phone hotlines
   - Text-based crisis support
   - Online chat services

3. **Professional Resources**
   - Therapist directories
   - Treatment locators
   - Mental health organizations

## Implementation Guidelines

### Integration Points

Safety checks should be implemented at:
1. Every user input processing point
2. Before generating any response
3. During conversation transitions

### Code Usage Example

```python
from src.utils.safety_response import SafetyResponse

# Initialize safety responder
safety_responder = SafetyResponse()

# Check user input for crisis
user_input = "I'm thinking about ending it all"
crisis_response = safety_responder.get_crisis_response(user_input)

if crisis_response:
    # Handle crisis situation
    formatted_response = safety_responder.format_response_for_session(crisis_response)
    print(formatted_response)

    if crisis_response['should_end_session']:
        # Gracefully end the CBT session
        pass
```

### Testing Safety Features

Always test safety features with:
1. Various phrasings of crisis situations
2. Context variations (past/present/academic)
3. Different severity levels
4. Geographic variations for resources

## Ethical Considerations

1. **Never Ignore Crisis Indicators**
   - Even uncertain cases should err on the side of caution
   - Provide resources even if unsure

2. **Maintain User Agency**
   - Provide options, not commands
   - Respect user's ability to make choices
   - Offer multiple pathways to help

3. **Cultural Sensitivity**
   - Recognize cultural differences in expressing distress
   - Provide diverse resource options
   - Avoid assumptions about user's situation

4. **Privacy and Confidentiality**
   - No crisis data is stored beyond the session
   - No identifying information is collected
   - Resources are provided without requiring personal details

## Continuous Improvement

1. **Regular Review**
   - Update crisis patterns based on new research
   - Expand geographic resource coverage
   - Refine context detection

2. **Feedback Integration**
   - Monitor false positive/negative rates
   - Adjust sensitivity based on user feedback
   - Update resources for accuracy

3. **Professional Consultation**
   - Work with mental health professionals
   - Align with best practices in crisis intervention
   - Stay current with suicide prevention guidelines

## Important Reminders

- This system is **not** a replacement for professional mental health services
- Always encourage users to seek professional help
- The chatbot should clearly state its limitations
- Crisis detection is a supplement to, not a substitute for, human judgment

## Contact for Safety Concerns

If you identify any issues with the safety protocols or have suggestions for improvement, please contact the development team immediately through the project's issue tracker.
