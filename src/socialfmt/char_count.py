"""Measure strings as they will probably be measured on X, Discord, LinkedIn.

This may not be exact, because I have no way to test it. But I've spot tested it, and
this seems to accurately see how platforms will measure strings for the purpose of
character limits. For example, it counts 𝑖 as 2 characters, and 𝐴 as 3 characters,
which is what X/Twitter does.

:author: Shay Hill
:created: 2026-05-12
"""

import re
import itertools as it

import string

# This regex matches any whitespace or punctuation character, which are the only
# characters we'll use as breakpoints for splitting text.
re_splitable = re.compile(f"[{re.escape(string.whitespace + string.punctuation)}]")


def count_chars(text: str) -> int:
    """The string length as counted by X/Twitter, Discord, LinkedIn, etc."""
    utf16_encoded = text.encode("utf-16le")
    return len(utf16_encoded) // 2


def split_at_chars(text: str, max_chars: int) -> tuple[str, str]:
    """Find the highest character index that splits the text at or before max_chars."""
    def _maybe_valid_split(i: int) -> bool:
        return i <= max_chars
    def _is_valid_split(i: int) -> bool:
        return count_chars(text[:i]) <= max_chars
    split_idxs = (x.span()[0] for x in re_splitable.finditer(text[:max_chars]))
    split_idxs = it.takewhile(_maybe_valid_split, split_idxs)
    split_idx = next(filter(_is_valid_split, reversed(list(split_idxs))), None)
    if split_idx is None:
        msg = f"Cannot split at or before {max_chars} characters: {text[:max_chars]!r}"
        raise ValueError(msg)
    return text[split_idx+1:], text[:split_idx+1]

# def split_at_chars(text: str, max_chars: int) -> tuple[str, str]:
#     """Split the text into two parts, the first of which is at most max_chars."""
#     idx = split_idx_at_chars(text, max_chars)
#     return text[:idx], text[idx:]


print(split_at_chars("sdfa asdf asfd  asdff ff   asdfdf S fs  fDF", 20))
