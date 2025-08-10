# SPDX-License-Identifier: MIT
import json
import re
from collections.abc import Callable
from typing import Any

from .composer import compose_system_prompt, retrieve_micro_knowledge
from .crisis import crisis_scan, safety_message
from .state import (
    PHASE_ORDER,
    ControlBlock,
    Phase,
    SessionState,
    model_dump,
    model_validate,
)


def _extract_between(text: str, tag: str) -> str | None:
    patt = re.compile(rf"<{tag}>\s*(.*?)\s*</{tag}>", re.S | re.I)
    m = patt.search(text or "")
    return m.group(1).strip() if m else None


def _sanitize_text(raw: str) -> str:
    """Remove tool/code fences and control blocks; trim whitespace.

    - Strips triple-backtick code blocks (```tool_code, ```python, or any fenced block)
    - Removes any remaining <control>...</control>
    - Collapses excessive whitespace
    """
    if not raw:
        return ""
    txt = re.sub(r"<control>.*?</control>", "", raw, flags=re.S | re.I)
    # Remove any triple backtick fenced code blocks
    txt = re.sub(r"```[a-zA-Z_]*\s*[\s\S]*?```", "", txt, flags=re.S)
    # Tidy up leftover backticks or stray markers
    txt = txt.replace("```", "")
    # Normalize whitespace
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _extract_control_block(raw: str) -> ControlBlock | None:
    block = _extract_between(raw, "control")
    if not block:
        return None
    try:
        data = json.loads(block)
        # Accept next_phase as string; coerce unknowns to current later.
        if isinstance(data.get("next_phase"), str):
            s = data["next_phase"].lower().strip()
            if s not in {p.value for p in PHASE_ORDER}:
                # Unknown phase label; let orchestrator ignore it.
                data["next_phase"] = None
        result = model_validate(ControlBlock, data)
        return result if isinstance(result, ControlBlock) else None
    except Exception:
        return None


def _extract_ui(raw: str) -> str:
    ui = _extract_between(raw, "ui")
    if ui:
        cleaned = _sanitize_text(ui)
        return cleaned if cleaned else "Thanks for sharing that."
    # Fallback: sanitize whole text (after removing control) and cap length
    cleaned = _sanitize_text(raw or "")
    return cleaned[:600] if cleaned else "Thanks for sharing that."


def _next_phase(current: Phase, suggested: Phase | None) -> Phase:
    idx = PHASE_ORDER.index(current)
    if suggested is None:
        return current
    try:
        sidx = PHASE_ORDER.index(suggested)
    except ValueError:
        return current
    # Allow same or forward only (prevents loops/backjumps).
    return PHASE_ORDER[max(idx, min(sidx, idx + 1))]


def _phase_banner(phase: Phase, note: str | None = None) -> str:
    labels = {
        Phase.WARMUP: "Phase: Warm-up — I'll make sure I understood you.",
        Phase.CLARIFY: "Phase: Clarify — I'll ask at most one quick question.",
        Phase.REFRAME: "Phase: Reframe — I'll offer a balanced perspective.",
        Phase.SUMMARY: "Phase: Summary — I'll recap and check how you feel.",
        Phase.FOLLOWUP: "Phase: Follow-ups — short answers based on the summary.",
        Phase.CLOSED: "Phase: Closed — this session has ended.",
    }
    msg = labels.get(phase, f"Phase: {phase.value.title()}")
    return f"{msg} {note}".strip() if note else msg


def _session_closed_message(language: str = "en") -> str:
    if language.lower().startswith("es"):
        return (
            "Gracias por conversar. Hemos llegado al final de las preguntas de seguimiento. "
            "Puedes volver cuando quieras para una nueva sesión."
        )
    return (
        "Thanks for talking with me. We've reached the end of the follow-ups. "
        "You can start a new session anytime."
    )


def _emit(
    state: SessionState,
    ui_text: str,
    *,
    banner: str | None = None,
    control: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "phase": state.phase.value,
        "turn": state.turn,
        "followups_left": state.followups_left,
        "banner": banner,
        "ui_text": ui_text,
        "control": control or {},
        "state": model_dump(state),
        "end_of_session": state.phase in (Phase.CLOSED,),
    }
    # If we are in FOLLOWUP, decrement the allowance now.
    if state.phase == Phase.FOLLOWUP and state.followups_left > 0:
        state.followups_left -= 1
    return payload


def handle_turn(
    state: SessionState,
    user_text: str,
    adk_llm_call: Callable[..., str],
) -> dict[str, Any]:
    """
    Orchestrates one turn of the session.
    - crisis handled first (backend)
    - builds compact system prompt and tiny micro-knowledge
    - enforces output contract <ui> + <control>{...}</control>
    - deterministic phase transitions + turn caps + banners
    """
    # 1) Crisis pre-check
    if crisis_scan(user_text):
        state.crisis_flag = True
        state.phase = Phase.SUMMARY  # pivot to a safe summary end
        ui = safety_message(state.user_language)
        return _emit(state, ui, banner=_phase_banner(state.phase))

    # 2) Prepare prompt materials
    sys_prompt = compose_system_prompt(state)
    kb_snippets = retrieve_micro_knowledge(state)

    # 3) Call your Google ADK agent (you pass your own callable)
    #    We pass state only for context; the model should not echo it.
    raw_reply = adk_llm_call(
        system=sys_prompt,
        kb=kb_snippets,
        state=model_dump(state),
        user=user_text,
    )

    # 4) Parse + pick next phase
    control = _extract_control_block(raw_reply)
    suggested = control.next_phase if control else None
    prev_phase = state.phase
    state.phase = _next_phase(state.phase, suggested)

    # 5) Turn management
    state.turn += 1
    halfway = state.turn == int(state.max_turns * 0.5)
    last_turn = state.turn >= state.max_turns - 1

    banner: str | None = None
    # Announce any phase change.
    if state.phase != prev_phase:
        banner = _phase_banner(state.phase)

    # Halfway nudge (non-intrusive).
    if halfway and state.phase not in (Phase.SUMMARY, Phase.FOLLOWUP, Phase.CLOSED):
        note = "Halfway through; we'll aim to reframe and move toward the summary soon."
        banner = _phase_banner(state.phase, note)

    # Enforce a timely summary near the end.
    if last_turn and state.phase not in (Phase.SUMMARY, Phase.FOLLOWUP, Phase.CLOSED):
        state.phase = Phase.SUMMARY
        banner = _phase_banner(
            state.phase, "We're at the end of this session. I'll summarize next."
        )

    # 6) Follow-up budget
    if state.phase == Phase.FOLLOWUP and state.followups_left <= 0:
        state.phase = Phase.CLOSED
        return _emit(
            state,
            _session_closed_message(state.user_language),
            banner=_phase_banner(state.phase),
        )

    # 7) Extract UI text and emit
    ui = _extract_ui(raw_reply)
    return _emit(
        state, ui, banner=banner, control=(model_dump(control) if control else {})
    )
