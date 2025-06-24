# Product Requirements Document (PRD) - re-frame.social
*Retrospective Analysis and Future Roadmap*

## Executive Summary

re-frame.social is a web-based cognitive reframing support tool designed specifically for individuals with Avoidant Personality Disorder (AvPD). The platform leverages multiple evidence-based therapeutic frameworks through an AI-powered multi-agent system to help users reframe negative thoughts and develop healthier cognitive patterns.

## Problem Statement

### The Challenge
People with AvPD experience:
- Intense fear of criticism and rejection
- Chronic feelings of inadequacy
- Avoidance of social interactions due to fear of negative evaluation
- Limited access to therapeutic support due to the very nature of their condition

### Current Solutions Gap
- Traditional therapy requires face-to-face interaction (triggering for AvPD)
- Generic mental health apps lack AvPD-specific adaptations
- AI chatbots often feel impersonal and untrustworthy
- Cost barriers to professional therapy

## Solution Overview

re-frame.social provides:
1. **Anonymous, low-pressure interaction** - No account required, no personal data stored
2. **Multiple therapeutic perspectives** - CBT, DBT, ACT, and Stoic approaches
3. **Transparent AI reasoning** - Users can see how conclusions are reached
4. **AvPD-specific adaptations** - Gentle language, no pressure, validation-focused

## System Architecture

### Multi-Agent AI System

```
User Input → Intake Agent → Framework Selector → Framework Agents → Synthesis Agent → User Response
                                                  ├── CBT Agent
                                                  ├── DBT Agent
                                                  ├── ACT Agent
                                                  └── Stoicism Agent
```

#### Component Details:

1. **Intake Agent** (`adk_intake_agent.py`)
   - Validates user input
   - Detects crisis situations
   - Identifies thought patterns and emotional content
   - Extracts key themes for framework selection

2. **Framework Selector** (Proposed in #40)
   - Analyzes intake data to determine most relevant frameworks
   - Selects 1-3 frameworks based on:
     - Thought patterns identified
     - Emotional intensity
     - Situation type
     - User preferences (future)

3. **Framework Agents**
   - **CBT Agent** (#61): Cognitive restructuring, evidence analysis
   - **DBT Agent** (#57): Distress tolerance, emotion regulation
   - **ACT Agent** (#58): Values clarification, psychological flexibility
   - **Stoicism Agent** (#59): Control focus, virtue ethics

4. **Synthesis Agent** (`adk_synthesis_agent.py`)
   - Combines multiple framework outputs
   - Resolves conflicting advice
   - Creates coherent, unified response
   - Handles crisis responses separately

### Technical Stack

**Backend:**
- Python 3.12 + FastAPI
- Google ADK (Agent Development Kit)
- Gemini 1.5 Flash LLM
- Firebase Admin SDK
- Cloud Firestore (future: user data)

**Frontend:**
- Next.js 14 (TypeScript)
- Tailwind CSS v3
- Static export to Firebase Hosting

**Infrastructure:**
- Google Cloud Run (containerized backend)
- Firebase Hosting (frontend)
- Terraform IaC
- GitHub Actions CI/CD

## Information Sources & Therapeutic Basis

### Evidence-Based Frameworks

1. **CBT (Cognitive Behavioral Therapy)**
   - Source: Beck's cognitive model
   - Focus: Identifying and challenging cognitive distortions
   - AvPD adaptation: Gentle challenging, emphasis on evidence

2. **DBT (Dialectical Behavior Therapy)**
   - Source: Linehan's biosocial theory
   - Focus: Balancing acceptance and change
   - AvPD adaptation: Radical acceptance of social fears

3. **ACT (Acceptance and Commitment Therapy)**
   - Source: Hayes' psychological flexibility model
   - Focus: Values-based action despite discomfort
   - AvPD adaptation: Small, values-aligned social steps

4. **Stoicism**
   - Source: Classical Stoic philosophy (Epictetus, Marcus Aurelius)
   - Focus: Distinguishing what's in our control
   - AvPD adaptation: Reducing catastrophic thinking about others' opinions

### Clinical Guidelines Referenced
- DSM-5 criteria for AvPD
- Evidence-based treatment guidelines for personality disorders
- Trauma-informed care principles
- Crisis intervention protocols

## Success Metrics (Phase 0 Alpha)

### Primary Metrics
1. **User Engagement**
   - Target: 25 unique users during alpha
   - Measurement: Anonymous session tracking

2. **Safety & Moderation**
   - Target: <10% of responses flagged for harmful content
   - Measurement: Automated content filtering + user reports

3. **Therapeutic Helpfulness**
   - Target: ≥60% of users rate responses as "helpful"
   - Measurement: Optional post-response feedback

### Secondary Metrics
1. **Technical Performance**
   - API response time <5 seconds
   - 99% uptime during testing period
   - Stay within $300 GCP credit budget

2. **Framework Utilization**
   - Distribution of frameworks selected
   - Correlation between input types and frameworks

3. **Crisis Detection**
   - Appropriate crisis response rate
   - False positive/negative rates

## User Journey

### Phase 0 Alpha Journey
1. User visits re-frame.social
2. Reads brief introduction (no sign-up pressure)
3. Enters thought/situation (up to 1000 characters)
4. Receives reframed perspective with framework indicators
5. Optionally views transparency data
6. Optionally provides feedback

### Privacy-First Approach
- No account creation required
- No personal data stored
- 7-day automatic data deletion
- Anonymous usage only
- Clear privacy messaging throughout

## Constraints & Considerations

### Technical Constraints
- $300 GCP credit budget
- Gemini 1.5 Flash token limits
- 10 requests/hour rate limiting per user
- Response generation <5 seconds

### User Population Considerations
- Extreme sensitivity to criticism
- Need for validation before challenging
- Skepticism of AI/technology
- Low tolerance for complexity
- Fear of data exposure

### Ethical Considerations
- Not a replacement for therapy
- Clear disclaimers about limitations
- Crisis resource information readily available
- Transparent about AI involvement
- No diagnostic claims

## Current Implementation Status

### Completed
- ✅ Basic infrastructure setup (Terraform)
- ✅ Frontend UI with single-thought input
- ✅ ADK integration with session management
- ✅ CBT framework agent
- ✅ Intake and synthesis agents
- ✅ Basic API structure

### In Progress
- 🔄 Remaining framework agents (DBT, ACT, Stoicism)
- 🔄 Framework selection logic
- 🔄 Multi-framework synthesis
- 🔄 Frontend updates for multi-framework display

### Not Started
- ❌ User feedback collection
- ❌ Analytics integration
- ❌ Crisis resource integration
- ❌ Performance optimization
- ❌ Comprehensive testing

## Next Steps & Roadmap

### Immediate (Complete Alpha - 2 weeks)
1. Complete framework agent implementations
2. Implement framework selector
3. Update frontend for multi-framework support
4. Deploy to production environment
5. Begin alpha testing with limited users

### Phase 1 (Post-Alpha - 1 month)
1. Implement user feedback mechanism
2. Add basic analytics (privacy-preserving)
3. Optimize framework selection algorithm
4. Add session continuity option
5. Implement A/B testing framework

### Phase 2 (Growth - 3 months)
1. Mobile-responsive optimizations
2. Extended session support (optional accounts)
3. Personalization based on usage patterns
4. Integration with crisis resources
5. Community feedback incorporation

### Phase 3 (Maturity - 6 months)
1. Multiple language support
2. Voice input option
3. Therapist dashboard (for professional use)
4. Research collaboration features
5. Potential clinical validation study

## Risk Analysis

### Technical Risks
1. **LLM costs exceed budget**
   - Mitigation: Aggressive caching, rate limiting
   - Contingency: Reduce to cached responses only

2. **Framework conflicts in synthesis**
   - Mitigation: Clear hierarchy, conflict resolution rules
   - Contingency: Single framework fallback

### User Risks
1. **Over-reliance on tool**
   - Mitigation: Clear messaging about supplementary nature
   - Contingency: Session limits, therapy referrals

2. **Triggering content**
   - Mitigation: Gentle language, validation-first approach
   - Contingency: Quick exit options, crisis resources

### Business Risks
1. **Low user adoption**
   - Mitigation: AvPD community outreach, testimonials
   - Contingency: Pivot to broader anxiety support

## Conclusion

re-frame.social represents a thoughtful approach to supporting individuals with AvPD through technology. By combining multiple therapeutic frameworks with transparent AI and privacy-first design, the platform aims to provide accessible cognitive support for those who struggle with traditional therapeutic interventions.

The Phase 0 Alpha will validate core assumptions about user needs and technical feasibility, setting the foundation for a tool that could meaningfully impact the AvPD community.

---

*Document Version: 1.0*  
*Last Updated: December 2024*  
*Status: Alpha Development*