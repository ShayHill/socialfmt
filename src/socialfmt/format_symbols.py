"""Replace straight quotes with curly & make other "smart" typographical substitutions.

Only call these functions outside code blocks.

:author: Shay Hill
:created: 2026-01-02
"""

import re

_EN_DASH = "\u2013"
_EM_DASH = "\u2014"
_LEFT_DOUBLE_QUOTE = "\u201c"
_RIGHT_DOUBLE_QUOTE = "\u201d"
_LEFT_SINGLE_QUOTE = "\u2018"
_RIGHT_SINGLE_QUOTE = "\u2019"
_LEFT_GUILLEMET = "\u00ab"
_RIGHT_GUILLEMET = "\u00bb"
_ELLIPSIS = "\u2026"


def _reject_spoiler_tags(text: str) -> None:
    """Raise ``ValueError`` if ``||`` appears in text."""
    if "||" in text:
        msg = "spoiler tags (||...||) are not supported"
        raise ValueError(msg)


# ===================================================================================
#   Make smart text dumb.
# ===================================================================================


class _DumbText:
    @staticmethod
    def _dumb_quotes(text: str) -> str:
        """Convert curly quotes in text to straight quotes."""
        text = text.replace(_LEFT_DOUBLE_QUOTE, '"').replace(_RIGHT_DOUBLE_QUOTE, '"')
        return text.replace(_LEFT_SINGLE_QUOTE, "'").replace(_RIGHT_SINGLE_QUOTE, "'")

    @staticmethod
    def _dumb_guillemets(text: str) -> str:
        """Convert angle quotes in text to straight quotes."""
        return text.replace(_LEFT_GUILLEMET, "<<").replace(_RIGHT_GUILLEMET, ">>")

    @staticmethod
    def _dumb_dashes(text: str) -> str:
        """Convert em and en dashes to hyphens."""
        return text.replace(_EN_DASH, "--").replace(_EM_DASH, "---")

    @staticmethod
    def _dumb_ellipses(text: str) -> str:
        """Convert ellipsis character to three consecutive dots."""
        return text.replace(_ELLIPSIS, "...")

    @classmethod
    def apply(cls, text: str) -> str:
        """Convert all smart characters in text to their dumb equivalents."""
        for name in (x for x in cls.__dict__ if x.startswith("_dumb_")):
            text = getattr(cls, name)(text)
        return text


# ===================================================================================
#   Make dumb text smart.
# ===================================================================================


class _SmartText:
    @staticmethod
    def _smart_quotes(text: str) -> str:
        """Convert straight quotes in text to curly quotes."""
        opener = r"(?P<opener>^|\s|[\(\[\{<])"
        text = re.sub(rf'{opener}"', rf"\g<opener>{_LEFT_DOUBLE_QUOTE}", text)
        text = re.sub(rf"{opener}'", rf"\g<opener>{_LEFT_SINGLE_QUOTE}", text)
        while _LEFT_SINGLE_QUOTE + '"' in text or _LEFT_DOUBLE_QUOTE + "'" in text:
            text = text.replace(
                _LEFT_SINGLE_QUOTE + '"', _LEFT_SINGLE_QUOTE + _LEFT_DOUBLE_QUOTE
            )
            text = text.replace(
                _LEFT_DOUBLE_QUOTE + "'", _LEFT_DOUBLE_QUOTE + _LEFT_SINGLE_QUOTE
            )
        text = text.replace('"', _RIGHT_DOUBLE_QUOTE)
        return text.replace("'", _RIGHT_SINGLE_QUOTE)

    @staticmethod
    def _smart_guillemets(text: str) -> str:
        """Convert guillemets to a plain-text equivalent."""
        return text.replace("<<", _LEFT_GUILLEMET).replace('"', _RIGHT_GUILLEMET)

    @staticmethod
    def _smart_dashes(text: str) -> str:
        """Convert hyphens to en and em dashes."""
        text = re.sub(r"(?<!-)---(?!-)", _EM_DASH, text)
        return re.sub(r"(?<!-)--(?!-)", _EN_DASH, text)

    @staticmethod
    def _smart_ellipses(text: str) -> str:
        """Convert three consecutive dots to a single ellipsis character."""
        return text.replace("...", _ELLIPSIS)

    @classmethod
    def apply(cls, text: str) -> str:
        """Convert all dumb characters in text to their smart equivalents."""
        for name in (x for x in cls.__dict__ if x.startswith("_smart_")):
            text = getattr(cls, name)(text)
        return text


def smart_text(text: str) -> str:
    """Convert all dumb characters in text to their smart equivalents."""
    _reject_spoiler_tags(text)
    return _SmartText.apply(_DumbText.apply(text))
