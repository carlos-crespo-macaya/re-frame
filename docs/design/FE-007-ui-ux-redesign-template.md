Below is a first-pass fill-in of your internal UI/UX Redesign Research Template [FE-007].
It focuses on moving away from anything that could read as childish, cutesy or condescending and toward a mature, warmly professional tone that earns trust from users with AvPD. (Feel free to tweak wording or add rows if more issues surface.)

⸻

UI/UX Redesign Research Template for [FE-007]

Project / Route: re-frame.social – Phase 1 → Phase 2

⸻

1. Voice & Tone Guidelines

	
Audience reminder	Adult users with AvPD / high social-evaluation fear. They respond best to genuine warmth, clarity and respect, not child-like cheerleading.

Current Problems (quick audit)
	•	Emoji overload (🥰 ⭐ 🌈) feels juvenile → may trigger “I’m not being taken seriously.”
	•	Hyper-cheerleading copy (“We’re listening with open hearts”) risks sounding forced or fake.
	•	Capital-L ‘Love’ language (“Built with love…”) can feel patronising or markety.
	•	“Gentle CBT techniques” is vague; experts prefer plain “CBT-based guidance.”

Proposed Voice Attributes

Attribute	Description	Micro-examples
Grounded warmth	Friendly but adult, like a calm therapist—not a cartoon friend.	“We’ll look at this together.”
Collaborative	Use we/you+I to signal partnership, not hierarchy.	“Let’s review what happened and explore alternatives.”
Non-judgmental	Avoid good/bad labels; replace with descriptive language.	“That thought feels heavy” vs. “That thought is negative.”
Transparent	Explicit about how AI works, what happens to data.	“Our model uses CBT logic to surface common distortions.”
Empowering	Reinforce agency, small wins.	“You chose to share— that’s a strong first step.”

Copy Rewrites (sample set)

Current (screenshot + UI)	Proposed	Rationale
Headline “How we journey together”	“How re-frame works”	Plainer, avoids “journey” trope.
Icon block 1 “Share what’s troubling you”	“Describe what happened”	Drops emoji; clarifies action.
Sub copy: “In your own words, at your own pace. We’re listening with open hearts.”	“Use your own words. Take the time you need.”	Removes florid sentiment; still supportive.
Icon block 2 “We explore together”	“Spot common thinking traps”	Explicit CBT outcome; avoids teacher-student vibe.
Sub copy: “Using gentle CBT techniques, we’ll help you see things from new angles.”	“We’ll apply CBT principles to highlight alternative perspectives.”	Concrete, adult.
Icon block 3 “Find new perspectives”	“Choose a perspective that feels true”	Emphasises user agency.
“Built with love for people with social anxiety and AvPD”	“Designed for people living with AvPD & social anxiety”	Respectful, factual.
“Let’s explore together” (button)	“Generate reframing”	Action-oriented; avoids playful metaphor.

(Continue table for all UI strings—menu items, tooltips, errors, etc.)

⸻

2. Visual Design Direction

Mood-Board Components

Element	Phase 1 (Now)	Phase 2 (Ideal) & Rationale
Color Palette	Black / gradient + neon green accent	Primary: Deep charcoal (#161616) for safety & focus   Secondary: Calm moss green (#4A6B57) (growth)   Accent: Soft teal (#54B4A0) (hope)   Neutrals: Warm gray (#F5F5F4)  Evidence: dark neutrals + muted green family correlate with perceived trust & calm in mental-health UX studies.
Typography	SF Pro (system default)	Headers: Inter SemiBold (modern, clinical neutrality)Body: Inter Regular / Readable size 16 px+ & 1.5 line-height for anxiety readability.Evidence: Inter chosen by NHS Design System for legibility.
Visual Elements	Large emojis + pastel circles	Replace emojis with simple line icons (Feather Icons) or subtle illustrations (abstract leaf, compass).  Rounded rectangles remain (safety).  Evidence: Mature icons avoid infantile vibe; abstract nature motifs signal growth without cliché.
Animations	Glow / “goo” transitions	Micro-motion only on success (opacity fade-in, 150 ms).  “Breathing” background reserved for optional grounding mode.  Evidence: trauma-informed design warns against surprise movement; prefer subtle, predictable.

Competitive Analysis

App	What Works	What Doesn’t	Key Takeaway
Headspace	Friendly tone, big whitespace	Can feel too playful for adult trauma users	Borrow calm spacing, not mascot-heavy visuals
Calm	Cinematic visuals, robust accessibility	Heavy video bg → data & distraction	Use still imagery; avoid autoplay
Finch	Gamified self-care plans	Cute bird mascot = childish for AvPD	Avoid overt gamification
Sanvello	CBT modules, sober UI	Dense dashboards overwhelm	Keep content bite-sized
Stoic	Minimal interface	Copy feels cold	Balance minimalism with warmth


⸻

3. Interaction Patterns

Form Design States

State	Principles
Resting	Neutral border, placeholder “Describe what happened…”
Focused	2 px teal outline, calm offset shadow (elevates field)
Error	Descriptive message (“We couldn’t connect. Try again.”) – soft red #B00020, no exclamation icons
Success	Fade‐in progress bar & “Reframing generated” toast; no confetti

Micro-interactions
	•	Button hover: subtle up-lift (translateY -2 px, 120 ms ease-out)
	•	Submit: progress bar top-edge; skeleton loader for 1–3 s.
	•	Loading state: “Preparing your reframing…” with 3-dot pulse.

Accessibility Checklist
	•	WCAG AA contrast 4.5:1 on text.
	•	prefers-reduced-motion – disable all animations.
	•	Keyboard tab order verified.
	•	44 × 44 px touch targets.
	•	Aria-labels on form controls.

⸻

4. Emotional Design Framework

Journey Stage	Target Emotional State	Supporting UI Cues
Landing	Safe, welcomed	Neutral dark bg, single CTA, privacy tagline
Writing	Heard, respected	Placeholder normalises any phrasing; word-count optional
Waiting	Supported, not judged	Gentle progress bar + affirming message
Reading	Understood, empowered	Clear reasoning bullets, “Save” option, ability to tweak

Trust Builders
	•	Constant HTTPS lock icon + “Private session” text.
	•	“Why we ask” tooltips explaining any data request.
	•	“Delete session” one-tap action.

⸻

5. Dark-Mode Issues  (observed)
	•	Icons fade vs bg at 20 % brightness.
	•	Sub copy (#666) unreadable on #161616.

Solutions
	•	Re-map palette with accessible contrast tokens (lightest text #EDEDED, secondary #B0B0B0).
	•	Add subtle radial vignette behind icon clusters for depth.

⸻

6. Component Library Needs

Core components scoped in Phase 1 codebase (/components/ui/*):
	•	<Button> variants (primary | secondary | text)
	•	<Textarea> with char counter
	•	<Card> (info, result)
	•	<AlertDialog> (privacy, delete)
	•	<Toast> (success, error)
	•	<Skeleton> loader

Special (new) components Phase 2:
	•	<ReframeSteps> timeline view
	•	<TrustBadge> privacy blurb inline
	•	<ProgressChip> gentle milestone indicator

⸻

7. Implementation Priorities

Phase 1 (Critical, sprint 6 weeks)	Phase 2 (Enhancement)
1. Copy overhaul (remove child-like tone)	1. Community opt-in module
2. Color & contrast token refactor	2. Themes & font-size prefs
3. Replace emoji icons	3. Progress journaling dashboard
4. Component library harden	4. Optional breathing animation


⸻

8. Success Metrics

Qualitative	Quantitative
80 % testers say “feels respectful”	Baseline → Goal
70 % say “tone is adult/professional”	Avg. session completion ↑ 10 %
0 user complaints of infantilizing copy	Drop-off before submit ↓ 15 %
	Accessibility audit > 95 %


⸻

9. Research Resources
	•	Trauma-Informed Tech Design – Modus 2019
	•	“Designing for Social Anxiety” – Nielsen Norman Group
	•	ADA & WCAG 2.2 guidelines
	•	NHS Frontend Library (accessibility tokens)

User feedback channels: private Discord pilot group; r/AvPD weekly thread; therapist panel of 3 advisors.

⸻

10. Prototype / Testing Plan

Low-Fi Concepts:
	1.	Wireframe set A – Mature minimal (no emoji).
	2.	Set B – Subtle illustration accents.
	3.	Set C – Dark-first theme.

Method: 5 remote user interviews (AvPD volunteers) + unmoderated Maze test.
Key Qs:
	•	“Does this feel adult and trustworthy?”
	•	“Any wording feel patronising?”
Success: 4/5 users comfortable sharing first thought in <2 min.

⸻

Notes
	•	Keep all onboarding optional; 0 required fields.
	•	Avoid “journey,” “hero,” “tribe” clichés.

Decision Log

Date	Decision	Rationale
2025-06-22	Remove emoji iconography	Users report childish tone
2025-06-22	Adopt Inter typeface	Improved readability + professional feel


⸻

Next steps
	1.	Approve voice-tone rewrites (Product + Clinical advisors).
	2.	Create updated icon set (Feather Icons + custom leaf).
	3.	Implement color token refactor in Tailwind config.
	4.	Schedule 5-user test sprint.

This fills the template with actionable changes, balancing adult professionalism and warm safety. 

# **re‑frame – Figma File Blueprint (Phase 1)**

> *Purpose*: give designers a **ready‑to‑build map** in Figma so the team can move fast, iterate, and hand‑off to engineering with minimal back‑and‑forth.

---

## 🌳 File Structure (Pages)

| Page                     | Goal                                                     | Notes                                                          |
| ------------------------ | -------------------------------------------------------- | -------------------------------------------------------------- |
| **00 ✦ Cover & README**  | One‐screen overview, design credits, link to Spec FE‑007 | Include the mission statement & colour legend chips.           |
| **01 ✦ Foundations**     | Design tokens (colour, type, spacing, radii, shadows)    | Publish as Figma *Styles* so any component auto‑updates.       |
| **02 ✦ Components**      | Atomic UI kit (buttons, inputs, cards…)                  | Use Variants + Auto‑layout. Naming: `component/variant/state`. |
| **03 ✦ Patterns**        | Compound pieces (header bar, privacy banner, loader)     | Re‑use primitives; document intended behaviour.                |
| **04 ✦ Screens – Light** | End‑to‑end user flow in light theme 🌓                   | Breakpoints: 375 × 812 (mobile) and 1440 × 1024 (desktop).     |
| **05 ✦ Screens – Dark**  | Mirror of Page 04 with dark tokens                       | Turn on *Color Styles* swap to validate contrast.              |
| **06 ✦ Prototype Links** | Connection arrows + simple Smart Animate                 | For unmoderated Maze tests.                                    |
| **99 ✦ Archive**         | Old iterations; keep clutter away                        | Locked to editors only.                                        |

---

## 🎨 01 Foundations

### **Colour Styles**  \_(WCAG AA \_)

| Token             | Hex     | Usage                      |
| ----------------- | ------- | -------------------------- |
| `brand/green‑500` | #4A6B57 | Accent, CTA button default |
| `brand/green‑300` | #6F8E7C | Hover, focus rings         |
| `ui/bg‑800`       | #161616 | Dark canvas                |
| `ui/bg‑50`        | #F5F5F4 | Light canvas               |
| `text/high`       | #EDEDED | Primary on dark            |
| `text/low`        | #B0B0B0 | Secondary on dark          |
| `state/error`     | #B00020 | Validation & fatal banners |
| `state/success`   | #54B4A0 | Toast ✔                    |

### **Type Styles**  (using *Inter*)

| Style        | Weight/Size/Line | Example              |
| ------------ | ---------------- | -------------------- |
| `display-24` | 600 / 24 / 32    | "How re‑frame works" |
| `heading-18` | 600 / 18 / 26    | Card titles          |
| `body-16`    | 400 / 16 / 24    | Standard copy        |
| `caption-12` | 400 / 12 / 18    | Helper & chars‑left  |

### **Spacing Scale**

4 – 8 – 12 – 16 – 24 – 32 – 48

### **Elevation / Shadows** *(on dark BG)*

`card-default`: 0 2 4 – rgba(0,0,0,0.35)
`popover`: 0 4 12 – rgba(0,0,0,0.45)

---

## 🧩 02 Components (Variant grid)

1. **Button**

   * Variants: `primary`, `secondary`, `text`
   * States: `default`, `hover`, `pressed`, `disabled`
   * Auto‑layout padding 16 × 10; corner radii 8.

2. **Textarea**

   * Base 320×160 px, resizable
   * States: `rest`, `focus`, `error`, `disabled`
   * Slot for char counter.

3. **Card**

   * `info`, `result`, `danger`
   * Shadow tokens; 24 px radius.

4. **Toast**

   * Slide‑in top centre, duration 4 s.

*(include loaders, skeleton row, privacy banner, etc.)*

---

## 📱 04/05 Key Mobile Frames

1. **Landing**

   * Hero copy (24 px heading)
   * CTA `Generate reframing`
2. **Entry**

   * Textarea + char counter
   * Info footer "Private session"
3. **Processing**

   * Progress bar (60 % width) + calming dot‑pulse
4. **Result**

   * `ReframeSteps` timeline
   * `Save` star toggle + `Ask follow‑up` secondary btn

Desktop frames sit at top of same page (Auto Layout rows).

---

## 🔄 Interaction Notes

* **Hover**: 120 ms ease‑out translateY(-2 px).
* **Submit**: skeleton of result card appears within 300 ms.
* **Dark Mode** uses the same components with style swap ‑ verify all contrast tokens.

---

## 🔗 Prototype Tips

* Use **Smart Animate** on result card fade‑in (opacity 0→100, 250 ms).
* Use hot‑spot over navbar logo to reset flow in tests.
* Connect "Need Help?" link to overlay frame demonstrating crisis‑line contacts (for demo only).

---

## ✅ Handoff Checklist

* All text merged into **Localizable** text styles.
* Inspect panel shows Auto Layout paddings & constraints.
* Tokens exported to `tailwind.config.js` via Figma Tokens plugin.
* Zeplin/Dev Mode descriptions for each component.

---

# **re‑frame – Component Reference Library (v0.1)**

> An expanded, line‑by‑line specification for every reusable UI element. Use this file in parallel with the *Figma File Blueprint (Phase 1)* for pixel‑perfect implementation.

---

## 🔖 Legend

* **Token** → colour / shadow / radius from *01 Foundations* style library.
* **Motion** → duration · easing · delay (ms · curve · ms).
* **DP** = device‑independent pixels (1 dp = 1 px @1×).

---

## 1 • Buttons

| Prop         | Primary                                        | Secondary              | Text              | Danger        |
| ------------ | ---------------------------------------------- | ---------------------- | ----------------- | ------------- |
| Default Fill | `brand/green‑500`                              | transparent            | transparent       | `state/error` |
| Text Colour  | `text/high`                                    | `brand/green‑500`      | `brand/green‑500` | `text/high`   |
| Border       | none                                           | 1 dp `brand/green‑500` | none              | none          |
| Radius       | **8 dp**                                       | 8 dp                   | 8 dp              | 8 dp          |
| Padding      | 16 × 10 dp                                     | 16 × 10                | 16 × 10           | 16 × 10       |
| Motion Hover | **120 · easeOutCubic · 0**  (translateY ‑2 dp) |                        |                   |               |
| Motion Tap   | **70 · easeOutQuad · 0** (scale 0.97)          |                        |                   |               |

### States

* **Hover:** lighten +4 % (primary) or background tint `brand/green‑50` (secondary/text).
* **Pressed:** darken ‑6 %; keep text at 100 % opacity.
* **Disabled:** reduce opacity 60 %, pointer‑events: none.

---

## 2 • Textarea

| Attribute         | Value                                                         |
| ----------------- | ------------------------------------------------------------- |
| Min Size          | 320 × 160 dp (mobile) · 480 × 200 dp (desktop)                |
| Max Lines         | 12 before scroll                                              |
| Radius            | 12 dp                                                         |
| Border            | 1 dp `ui/border‑300` (rest) → 2 dp `brand/green‑300` (focus)  |
| Placeholder Style | `text/low` 80 % opacity                                       |
| Char Counter      | Caption‑12, right‑align, updates live                         |
| Error State       | Border → `state/error`, message below in `state/error` colour |

---

## 3 • Cards

| Variant | Elevation                        | Shadow Token   | Internal Padding           |
| ------- | -------------------------------- | -------------- | -------------------------- |
| Info    | 2 dp                             | `card-default` | 24 dp all sides            |
| Result  | 4 dp                             | `popover`      | 24 dp top/btm, 32 dp sides |
| Danger  | 2 dp, outline `state/error` 1 dp | none           | 24 dp                      |

---

## 4 • Icons

* **Library:** Feather Icons (MIT) – 24 × 24 dp, **1.5 dp stroke**.
* Line style only; avoid solid fills to keep mature aesthetic.
* Colour inherits from parent text (default `text/high`).
* Minimum interactive icon button target: 44 × 44 dp (invisible padding).

| Use‑case          | Icon Name                   | Notes                                 |
| ----------------- | --------------------------- | ------------------------------------- |
| Submit / Generate | `corner-right-up`           | Rotated 90° CCW for “send” arrow      |
| Save / Star       | `star` (filled when active) | Filled version uses `brand/green‑500` |
| Delete Entry      | `trash-2`                   | Danger colour                         |
| Privacy           | `lock`                      | 20 dp size inside caption             |

---

## 5 • Loaders & Skeletons

### Progress Bar

* **Height:** 3 dp
* **Fill:** `brand/green‑500`
* **Indeterminate Motion:** left‑to‑right sweep, 1 400 · linear · 0 (ms).

### Skeleton Card

| Element        | BG Token    | Animation                     |
| -------------- | ----------- | ----------------------------- |
| Base rectangle | `ui/bg‑700` | shimmer 1 000 · easeInOutSine |
| Corner radius  | 24 dp       |                               |

---

## 6 • Toast (Top‑centre)

| Prop      | Spec                                                             |
| --------- | ---------------------------------------------------------------- |
| Width     | 80 % viewport max‑width = 480 dp                                 |
| Elevation | 6 dp shadow                                                      |
| Entrance  | translateY(‑20 dp) · opacity 0 → 100 over **250 · easeOutCubic** |
| Exit      | reverse after 4 000 ms delay                                     |
| Types     | success (`state/success` left bar) · error (`state/error`)       |

---

## 7 • Motion Curves Reference

| Curve Name    | Cubic‑Bezier           | Use‑cases                 |
| ------------- | ---------------------- | ------------------------- |
| easeOutCubic  | 0.22, 1, 0.36, 1       | Button hover, toast enter |
| easeOutQuad   | 0.25, 0.46, 0.45, 0.94 | Button tap scale          |
| easeInOutSine | 0.37, 0, 0.63, 1       | Skeleton shimmer          |

### Global Motion Rules

* Respect **`prefers-reduced-motion`**: disable scale / translate; keep fade ≤100 ms.
* Max one animated element per view (except progress bar) to limit cognitive load.

---

## 8 • Grid & Layout

| Breakpoint       | Columns | Gutter |
| ---------------- | ------- | ------ |
| Mobile < 600 dp  | 4       | 16 dp  |
| Desktop ≥ 600 dp | 12      | 24 dp  |

Containers max‑width 1 120 dp.

---

## 9 • Compliance & Handoff

* **Colour contrast:** verify AA in both themes via Stark plugin.
* **RTL** readiness: icons mirrored where direction‑dependent.
* Each Variant frame labelled: *name/state/size*.

---

*End of component spec v0.1 – 2025‑06‑22*
