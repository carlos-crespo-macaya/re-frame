# Cognitive Reframing Assistant – High-Level Design

## 1. Vision
Help individuals recognise, challenge, and reframe unhelpful thoughts through a compassionate conversational experience grounded in evidence-based Cognitive Behavioural Therapy (CBT).

## 2. User Personas
1. **End User (Seeker)** – Anyone experiencing anxious or negative thoughts who wants a private, on-demand CBT-style conversation.
2. **Mental-Health Professional** – Therapists who may recommend or review the assistant’s outputs as supplemental material.
3. **Product Owner / Admin** – Oversees content quality, prompt versions, and monitors usage metrics.

## 3. Core Value Proposition
* 24 × 7 access to a structured CBT conversation.
* Multilingual engagement so users can converse in their preferred language without friction.
* Personalised PDF summary for reflection and future sessions.
* Seamless escalation path—users are nudged toward professional help if severe risk indicators surface.

## 4. Primary Capabilities
1. **Language Detection & Localisation**
   * Auto-detect the user’s language from their first message.
   * Conduct the entire dialogue in that language.
2. **Guided CBT Conversation**
   * Four distinct phases: Greeting → Discovery → Reframing → Summary.
   * Assistant adheres to CBT questioning techniques and cognitive distortion taxonomy.
3. **Session State Management**
   * Remembers prior dialogue turns to maintain context and phase progression.
4. **PDF Summary Generation**
   * Produces an optional, concise summary capturing key insights, balanced thoughts, and agreed micro-actions.
5. **Safety & Ethics Toolkit**
   * Detects crisis language (e.g., self-harm) and provides appropriate resources.
   * Ensures empathetic, non-diagnostic tone.
6. **Observability & Feedback**
   * Captures conversational metrics and user feedback for continuous improvement.

## 5. Experience Journey
1. **Onboarding / Greeting** – Assistant introduces itself, outlines the three-phase approach, and invites the user to share what’s on their mind.
2. **Discovery** – Assistant gathers details about the situation, automatic thoughts, and emotional intensity (1–10 scale).
3. **Reframing** – Assistant surfaces potential cognitive distortions, collaboratively formulates balanced thoughts, and suggests a small actionable step.
4. **Summary & Closure** – Assistant offers a PDF summary and thanks the user. If accepted, summary is generated and delivered (e.g., downloadable link or email).

## 6. High-Level Component View
* **Conversational Agent** – Orchestrates dialogue, enforces phase sequencing, and invokes specialised sub-skills (e.g., distortion classification).
* **Prompt Repository** – Central source of system, phase, and language-specific prompts, versioned for A/B testing.
* **Session Store** – Holds user messages, detected language, phase status, and CBT artefacts.
* **PDF Generator** – Converts structured summary data into a polished, user-friendly document.
* **Telemetry & Feedback Loop** – Gathers usage metrics, anonymised conversation summaries, and user ratings for continuous refinement.

## 7. Quality & Compliance Goals
* **Safety First** – Follow curated escalation guidelines when risk detected.
* **Accessibility** – Multilingual, emoji-free fallback mode for screen-readers.
* **Privacy** – PII minimisation and strong data-retention policies.
* **Reliability** – Graceful degradation if downstream services (e.g. PDF generation) fail.

## 8. Key Risks & Mitigations (Non-technical)
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Incorrect therapeutic guidance | Erodes trust, potential harm | Constrain assistant to evidence-based CBT patterns; periodic expert review |
| Language detection errors | User confusion | Provide manual language override command |
| Over-reliance on AI vs. professional help | Unmet clinical needs | Include clear disclaimers and crisis support links |

## 9. Success Metrics
* Conversation completion rate (all phases).
* User-reported helpfulness score ≥ 4/5.
* PDF summary opt-in rate.
* Language detection accuracy ≥ 95 %.

---
*This high-level design intentionally omits specific technologies, libraries, or architectural patterns. Those details live in the accompanying `implementation.md` once technical decisions are crystallised.*
