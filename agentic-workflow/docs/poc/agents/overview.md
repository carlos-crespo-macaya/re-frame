Overview — The Problem We’re Solving

People who live with personality-disorder traits (e.g., avoidant, borderline, obsessive-compulsive, narcissistic) often carry rigid, shame-laden automatic thoughts such as “Everyone thinks I’m stupid.”  A bite-sized CBT intervention—cognitive reframing—can give them a fast, low-risk win by (1) spotting the underlying cognitive distortion, (2) weighing one piece of evidence for and against the thought, and (3) replacing it with a balanced alternative plus a ≤ 10-minute action step that builds mastery.  Our micro-workflow delivers this entire loop in a single, highly-validating chat that respects PD sensitivities (choice, pacing, crisis checks) and then hands the user an anonymised PDF takeaway to reinforce progress and encourage follow-through with their broader therapy plan.

⸻

Agent 1 · info_collector_reframe_agent

Aspect	Briefing
Role	Trauma-informed intake assistant that gathers the minimum viable dataset for reframing.
Must-collect	• Trigger situation (who / where / when) • Exact automatic thought • Emotion label + intensity (0-10).
Optional extras	Duration, frequency, one fact for/against, 0-100 % confidence, perceived impact, cultural notes.
Conversation style	Validate first, one concise open question per turn, max 4 user turns, mirrors user language; user may refuse any question.
Safety	Detects self-harm or violence → escalates immediately with Spain 024 / 112 (or local) hotline message.
Stop-flag	Writes collection_complete = True (and escalate = True) once the three must-haves are in state.


⸻

Agent 2 · reframe_agent

Aspect	Briefing
Role	Board-certified CBT engine that identifies up to two cognitive distortions and produces a JSON reframing package.
Core knowledge	Full distortion playbook (MW, FT, CT…DR) with tactics & matching micro-actions; collaborative-empiricism ethos; confidence-shift metric.
Workflow	• Ask for missing evidence or confidence baseline.• Detect distortions.• Generate ≤ 40-word balanced thought & ≤ 10-minute micro-action aligned with playbook.• Ask for post-reframe confidence.
Output format	JSON with distortions, evidence lists, balanced thought, micro-action, certainty before/after, and warm tone.
Safety	Any crisis language → escalate; otherwise sets reframe_done = True, escalate = True when rubric passes (≤ 2 iterations).


⸻

Agent 3 · pdf_summariser_agent

Aspect	Briefing
Role	Documentation assistant that converts intake + Reframe JSON into a one-page, fully anonymised PDF.
Inputs required	Trigger context, thought, emotion data, and entire result_json from Reframer.
Anonymisation	Replaces names with “Client”, strips precise dates & locations more specific than city-level.
PDF sections	Header → Input snapshot → Distortion analysis (evidence table + balanced thought) → Micro-action plan & confidence shift → Next-step checklist → Disclaimer / resources.
Visual style	Clean sans-serif, 11 pt, #2563EB accent, filename CBT_Reframe_Report_YYYY-MM-DD.pdf.
Stop-flag	Saves file, returns download link, sets pdf_ready = True; on failure apologises and leaves flag unset.


⸻

Why a micro-reframe is a good fit for people with personality-disorder traits

Factor typical in many PD presentations	How the 3-step micro-reframing loop helps
Rigid, global self-beliefs (“I’m unlovable,” “I always mess up”)	Reframing targets the exact belief in the moment, chips away at black-and-white labels, and introduces graded, evidence-based language.
High shame & sensitivity to perceived judgment	One short, validating chat avoids long intellectual lectures.  The intake agent normalises distress before asking anything, lowering threat.
Chronic avoidance / low behavioural activation (common in Avoidant, Borderline, OCPD)	The micro-action is ≤ 10 min, so it feels doable and gives an immediate mastery bump—important for people who fear failure or abandonment.
Distrust of authority / fear of losing control	Collaborative empiricism: the user supplies both evidence lists and confidence ratings, so they remain the “owner” of the process.
Emotion dysregulation & quick escalation	Intake agent monitors distress delta; reframer never probes trauma content; any spike or crisis diverts to safety resources.
Need for tangible proof of progress	Confidence-before / confidence-after percentages + a PDF takeaway make progress concrete, which can strengthen engagement and counter hopelessness.


⸻

Key PD-specific safeguards baked into the three agents
	1.	Strong validation first
Avoidant and Borderline clients retreat quickly if they sense criticism.
The intake prompt always reflects back the user’s wording (“That sounds heavy to carry”) before any question.
	2.	Choice & pacing
Each question is optional; collection stops after four turns.  This prevents the sense of being interrogated—a common trigger for PD clients with past invalidating experiences.
	3.	Emotion-intensity re-checks
Agents pause or offer a break if the emotion rating jumps more than 2 points, protecting those prone to sudden affect surges.
	4.	Ultra-concrete micro-actions
Up to 10 minutes, single-step, directly tied to the distortion.  Long homework lists often backfire with PD populations because perfectionistic or catastrophic thinking kicks in.
	5.	PDF anonymity + ownership
The report uses “Client,” strips names/locations, and ends with a self-managed checklist—empowering for clients who fear exposure or judgment.

⸻

Implementation considerations for a PD-focused deployment
	•	Language tone
Use gentler wording than traditional CBT manuals; e.g., “It makes sense you’d feel X” rather than “That’s a distortion.”
	•	Crisis routing
Many PD clients have self-harm histories—crisis detection must be watertight, with direct hotline instructions and an immediate halt to reframing.
	•	Repeatability
Entrenched beliefs change slowly; allow users to run the loop on the same thought multiple times and track confidence shifts over days or weeks.
	•	Integration with longer-term care
The micro-tool is not a stand-alone treatment.  Encourage users to discuss their reframes with a live therapist, especially if they are in DBT, schema therapy, or STEPPS programs.
	•	Cultural & identity sensitivity
Ask for preferred pronouns or cultural framing if it affects how the thought is experienced (e.g., honour/shame dynamics in collectivist cultures).

⸻

Bottom line:
A single-turn cognitive reframe can’t resolve a personality disorder, but it does give clients a fast, concrete win against a stubborn belief, boosts self-efficacy, and slots neatly into broader PD-treatment frameworks—all while minimising emotional risk through validation, pacing, and clear safety protocols.

End-to-End Flow
	1.	User ↦ Intake agent gathers minimal data.
	2.	Reframe agent transforms that data into a targeted cognitive reframe.
	3.	Summariser packages the session into a downloadable PDF so the user leaves with a concrete action plan and record of progress.