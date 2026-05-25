"""Measure strings as they will probably be measured on X, Discord, LinkedIn.

This may not be exact, because I have no way to test it. But I've spot tested it, and
this seems to accurately see how platforms will measure strings for the purpose of
character limits. For example, it counts 𝑖 as 2 characters, and 𝐴 as 3 characters,
which is what X/Twitter does.

:author: Shay Hill
:created: 2026-05-12
"""

import itertools as it
import re
import string

# This regex matches any whitespace or punctuation character, which are the only
# characters we'll use as breakpoints for splitting text.
re_splitable = re.compile(f"[{re.escape(string.whitespace + string.punctuation)}]")


def count_chars(text: str) -> int:
    """Return string length as counted by X/Twitter, Discord, LinkedIn, etc."""
    utf16_encoded = text.encode("utf-16le")
    return len(utf16_encoded) // 2


def split_at_chars(text: str, max_chars: int) -> tuple[str, str]:
    """Split text afterw the highest word/punctuation break at or before max_chars.

    Returns ``(head, rest)`` where ``head`` is the chunk up to and including the
    split character (``count_chars(head) <= max_chars``) and ``rest`` is
    everything after it.
    """

    def _maybe_valid_split(i: int) -> bool:
        """Check if the split at index i fits without checking utf16_endoded len."""
        return i <= max_chars

    def _is_valid_split(i: int) -> bool:
        """Verify the split at index i fits by checking the utf16_encoded len."""
        return count_chars(text[:i]) <= max_chars

    split_idxs = (x.span()[1] for x in re_splitable.finditer(text[:max_chars]))
    split_idxs_tw = it.takewhile(_maybe_valid_split, split_idxs)
    split_idx = next(filter(_is_valid_split, reversed(list(split_idxs_tw))), None)
    if split_idx is None:
        msg = f"Cannot split at or before {max_chars} characters: {text[:max_chars]!r}"
        raise ValueError(msg)
    return text[:split_idx], text[split_idx:]
