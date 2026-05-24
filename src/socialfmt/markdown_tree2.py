"""Parse markdown into a tree of nodes.

:author: Shay Hill
:created: 2026-05-19
"""

from __future__ import annotations

import itertools as it
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Self
from uuid import uuid4
from collections.abc import Iterator, Iterable
from typing import TypeVar


class InvalidMarkdownError(ValueError):
    pass


# any of these, preceeded by at least one \n, will be identified as a
# paragraph--provided they are not in a code block.
_PAR_DELIMITERS = (
    r"(?:>\s+)-\s+",  # ul in quote
    r"(?:>\s+)\d+\.\s+",  # ol in quote
    r">\s+",  # quote
    r"#\s+",  # heading
    r"-\s+",  # ul
    r"\d+\.\s+",  # ol
    r"\n\s*",  # double newline
)

_NEWLINE = r"(?:\s*\n\s*)"

_T = TypeVar("_T")


def _chunkify_or_raise(items: Iterable[_T], n: int = 1) -> Iterable[tuple[_T, ...]]:
    """Yield iterable items n at a time."""
    iter_items = iter(items)
    while True:
        chunk = tuple(it.islice(iter_items, n))
        if len(chunk) == 0:
            return
        if len(chunk) == n:
            yield chunk
        else:
            msg = f"number of items not evenly divisible by {n}"
            raise ValueError(msg)


def _mask_code_blocks(text: str) -> str:
    """Replace spans starting and beginning with ``` with zeros.

    This is to hide markdown-delimiter characters in pre elements like ``` and `
    while maintaining the character count.
    """
    delims = list(re.finditer("```", text))
    if len(delims) % 2:
        msg = "Open '```' block without close"
        raise InvalidMarkdownError(msg, f"found {len(delims)}")
    while delims:
        end = delims.pop().end()
        start = delims.pop().start()
        text = text[:start] + "0" * (end - start) + text[end:]
    return text


def _split_pars(text: str) -> Iterator[tuple[str, str]]:
    """Split text spans into (par delim, par text), (par delim, par text), ..."""
    masked_text = _mask_code_blocks(text)
    par_delims = (f"{_NEWLINE}+{x}" for x in _PAR_DELIMITERS)
    par_break = f"({'|'.join(par_delims)})"
    dtdtdt = re.split(par_break, f"\n\n{masked_text}\n\n")[1:-2]
    dtdtdt[0] = dtdtdt[0][2:]
    cursor = 0
    for d, t in _chunkify_or_raise(dtdtdt, 2):
        cursor += len(d)
        yield d, text[cursor : cursor + len(t)]
        cursor += len(t)
    return


text = "**This is bold and *italic*** te**xt**\n\n**an**```d `co**no recurse**de` and``` ||spoiler||"
for dt in _split_pars(text):
    print(dt)

