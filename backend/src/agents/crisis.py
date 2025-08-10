# SPDX-License-Identifier: MIT

# Keep conservative for PoC. Backend-only.
DANGER_TERMS = [
    "suicide",
    "kill myself",
    "end it all",
    "self harm",
    "self-harm",
    "cutting",
    "overdose",
    "harm others",
    "hurt someone",
    "no reason to live",
]


def crisis_scan(text: str) -> bool:
    """
    Scan text for crisis/danger keywords.

    Args:
        text: The text to scan for crisis indicators

    Returns:
        True if crisis keywords are detected, False otherwise
    """
    if not text:
        return False

    lower_text = text.lower()
    return any(term in lower_text for term in DANGER_TERMS)


def safety_message(language: str | None = "en") -> str:
    # Minimal, locale-agnostic wording to avoid giving specific instructions.
    if language and language.lower().startswith("es"):
        return (
            "Lamento que te sientas así. Tu seguridad importa. "
            "Si estás en peligro o pensando en hacerte daño, por favor busca ayuda inmediata "
            "de un profesional de tu zona o contacta a servicios de emergencia. "
            "Si te parece bien, puedo cerrar esta sesión con un breve resumen."
        )
    return (
        "I'm really sorry you're feeling this way. Your safety matters. "
        "If you are in danger or thinking about harming yourself, please seek immediate help "
        "from a local professional or emergency services. "
        "If it's okay with you, I can close this session with a brief summary."
    )
