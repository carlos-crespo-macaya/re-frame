"""Very small stub replacement for the *langdetect* package used in tests.

The real *langdetect* library is relatively heavy and carries external
dependencies that are unnecessary for the unit-tests shipped in this
repository.  All the test-suite needs is:

* ``DetectorFactory`` with a writable ``seed`` attribute
* ``LangDetectException`` exception class
* ``detect_langs`` function returning an iterable whose items expose
  ``lang`` and ``prob`` attributes.

This stub provides exactly that – nothing more.
"""

from __future__ import annotations

from typing import List

__all__ = [
    "DetectorFactory",
    "LangDetectException",
    "detect_langs",
]


class LangDetectException(Exception):  # noqa: D401 – simple marker exception
    """Raised when language detection fails (stub)."""


class _DetectorFactory:  # noqa: D401 – mimics real DetectorFactory API
    seed = 0


DetectorFactory = _DetectorFactory  # noqa: N816 – keep same public name


class _Detection:  # noqa: D401 – represents a detected language entry
    def __init__(self, lang: str, prob: float):
        self.lang = lang
        self.prob = prob

    def __str__(self) -> str:  # noqa: D401
        return f"{self.lang}:{self.prob}"

    # Real detect_langs list items support truthiness & float conversion, but
    # the tests only access ``.lang`` and ``.prob`` attributes.


def detect_langs(text: str) -> List[_Detection]:  # noqa: D401
    """Very naive language *detection* – English unless obvious Spanish words."""

    lowered = text.lower()
    if any(word in lowered for word in ("hola", "gracias", "buenos", "día", "bien")):
        return [_Detection("es", 0.99)]
    return [_Detection("en", 0.99)]

