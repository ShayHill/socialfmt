"""Replace straight quotes with curly & make other "smart" typographical substitutions.

The public functions respect code blocks.

:author: Shay Hill
:created: 2026-01-02
"""

import re
from collections.abc import Callable

# Because there is no visual difference in a fixed-width font.
_EN_DASH = "–"
_EM_DASH = "—"

# Fenced code blocks (``` ... ```) and inline code spans (` ... ` or ``...``).
# Inline spans are delimited by a run of backticks closed by an equal-length run.
CODE_RE = re.compile(r"```.*?```|(`+)(?:(?!\1).)+?\1", re.DOTALL)


def _apply_outside_code(text: str, transform: Callable[[str], str]) -> str:
    """Apply transform to segments of text that are not inside code blocks."""
    parts: list[str] = []
    last_end = 0
    for match in CODE_RE.finditer(text):
        parts.append(transform(text[last_end : match.start()]))
        parts.append(match.group(0))
        last_end = match.end()
    parts.append(transform(text[last_end:]))
    return "".join(parts)


# ===================================================================================
#   Make smart text dumb.
# ===================================================================================


def _dumb_quotes(text: str) -> str:
    """Convert curly quotes in text to straight quotes."""
    text = text.replace("“", '"').replace("”", '"')
    return text.replace("‘", "'").replace("’", "'")


def _dumb_guillemets(text: str) -> str:
    """Convert angle quotes in text to straight quotes."""
    return text.replace("«", "<<").replace("»", ">>")


def _dumb_dashes(text: str) -> str:
    """Convert em and en dashes to hyphens."""
    return text.replace(_EN_DASH, "--").replace(_EM_DASH, "---")


def _dumb_ellipses(text: str) -> str:
    """Convert ellipsis character to three consecutive dots."""
    return text.replace("…", "...")


def _dumb_text(text: str) -> str:
    """Convert all smart characters in text to their dumb equivalents."""
    return _dumb_ellipses(_dumb_dashes(_dumb_guillemets(_dumb_quotes(text))))


def dumb_text(text: str) -> str:
    """Convert all smart characters in text to their dumb equivalents.

    Leaves the contents of fenced (```` ``` ````) and inline (`` ` ``) code
    blocks unchanged.
    """
    return _apply_outside_code(text, _dumb_text)


# ===================================================================================
#   Make dumb text smart.
# ===================================================================================


def _smart_quotes(text: str) -> str:
    """Convert straight quotes in text to curly quotes."""
    opener = r"(?P<opener>^|\s|[\(\[\{<])"
    text = re.sub(rf'{opener}"', r"\g<opener>“", text)
    text = re.sub(rf"{opener}'", r"\g<opener>‘", text)
    while '‘"' in text or "“'" in text:
        text = text.replace('‘"', "‘“")
        text = text.replace("“'", "“‘")
    text = text.replace('"', "”")
    return text.replace("'", "’")


def _smart_guillemets(text: str) -> str:
    """Convert guillemets to a plain-text equivalent."""
    return text.replace("<<", "«").replace('"', "»")


def _smart_dashes(text: str) -> str:
    """Convert hyphens to en and em dashes."""
    text = text.replace("---", _EM_DASH)
    return text.replace("--", _EN_DASH)


def _smart_ellipses(text: str) -> str:
    """Convert three consecutive dots to a single ellipsis character."""
    return text.replace("...", "…")


def _smart_text(text: str) -> str:
    """Convert all dumb characters in text to their smart equivalents."""
    return _smart_ellipses(_smart_guillemets(_smart_dashes(_smart_quotes(text))))


def smart_text(text: str) -> str:
    """Convert all dumb characters in text to their smart equivalents.

    Leaves the contents of fenced (```` ``` ````) and inline (`` ` ``) code
    blocks unchanged.
    """
    return _apply_outside_code(text, _smart_text)
