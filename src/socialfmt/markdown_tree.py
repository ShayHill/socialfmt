"""Parse Discord-style markdown into a tree of nodes.

:author: Shay Hill
:created: 2026-05-12
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


_PAR = str(int(uuid4()))
_QUOTE = str(int(uuid4()))
_UL = str(int(uuid4()))
_OL = str(int(uuid4()))

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


class InvalidMarkdownError(ValueError):
    pass


def _mask_spans(delim: str, text: str) -> str:
    """Replace spans starting and beginning with ``delim`` with zeros.

    This is to hide markdown-delimiter characters in pre elements like ``` and `
    while maintaining the character count.
    """
    delims = list(re.finditer(delim, text))
    if len(delims) % 2:
        msg = f"Open '{delim}' block without close"
        raise InvalidMarkdownError(msg, f"found {len(delims)}")
    while delims:
        end = delims.pop().end()
        start = delims.pop().start()
        text = text[:start] + "0" * (end - start) + text[end:]
    return text

def _mask_pattern(pattern: str, text: str) -> str:
    """Replace any pattern matches with zeros."""
    for match in re.finditer(pattern, text):
#         breakpoint()


# def validate_markdown_par(text: str) -> list[str]:
#     """Raise an InvalidMarkdownError for any nested or unclosed spans."""
#     text = _mask_spans("`", text)
#     text = _mask_pattern(


def validate_markdown_text(text: str) -> None:
    """Raise a value error for any nested markdown tags.

    **~~text~~** is valid.
    **~~text**~~ is invalid.
    """
    if not text.strip():
        return
    if match := re.search("````", text):
        msg = "Cannot parse more than three consecutive '`'."
        raise InvalidMarkdownError(msg, match)
    if match := re.match(r"\*\*\*\*", text):
        msg = "Cannot parse more than three consecutive '`'."
        raise InvalidMarkdownError(msg, match)
    if match := re.match("____", text):
        msg = "Cannot parse more than three consecutive '_'."
        raise InvalidMarkdownError(msg, match)
    masked_text = _mask_spans("```", text)
    par_delims = (r"(?:>\s+)-\s+", r">\s+", r"#\s+", r"\d+\.\s+", "\n")
    par_delims = (f"{_NEWLINE}+{x}" for x in par_delims)
    par_break = f"({'|'.join(par_delims)})"
    dpdpdp = re.split(par_break, f"\n\n{masked_text}\n\n")[1:-2]
    dpdpdp[0] = dpdpdp[0][2:]
    for i, (_, par) in enumerate(_chunkify_or_raise(dpdpdp, 2)):
        _ = validate_markdown_par(par)

        # delim_ = {"> ": _QUOTE, "- ": _UL}.get(delim.lstrip(), _PAR)
        # start = max(len("".join(dpdpdp[:i*2])) - 2, 0)
        # par_w_leading_delimiter = "".join(dpdpdp[:i*2+2][2:])
        # end = len(par_w_leading_delimiter)
        # # placeholder = f"{delim_}"
        # # text = text[:start] + placeholder + text[end:]
        # breakpoint()
        # # dpdpdp[i*2+1] = f"{delim_}{dpdpdp[i*2+1]}{delim_}

    _
    # for delim, par in _chunkify_or_raise(re.split(par_break, f"\n\n {text} \n\n"), 2):

    breakpoint()
    # for placeholder in placeholder_map:
    #     par_delims.
    # # par_delims = "\n*\n- |\n*\n\* |\n*\n> |\n*\n\n"
    # pars = re.split(par_delims, text)
    # breakpoint()
    return True, ""


# validate_markdown("ff")
validate_markdown_text("```pre```asdf\n\nSDf\n>  e`a`s\n\n\n\n* df\n  >    - ```asdfasdf```")


class Fmt(Enum):
    """Formatting type for a parsed markdown node."""

    BOLD = "bold"
    BOLD_ITALIC = "bold_italic"
    CODE = "code"
    CODE_BLOCK = "code_block"
    DOCUMENT = "document"
    ITALIC = "italic"
    PARAGRAPH = "paragraph"
    PLAIN = "plain"
    QUOTE = "quote"
    SPOILER = "spoiler"
    STRIKETHROUGH = "strikethrough"
    UNDERLINE = "underline"


_DELIMITERS: list[tuple[str, Fmt]] = [
    ("```", Fmt.CODE_BLOCK),
    ("\n\n", Fmt.PARAGRAPH),
    ("> ", Fmt.QUOTE),
    ("**", Fmt.BOLD),
    ("*", Fmt.ITALIC),
    ("__", Fmt.UNDERLINE),
    ("~~", Fmt.STRIKETHROUGH),
    ("||", Fmt.SPOILER),
    ("`", Fmt.CODE),
]

_DELIM2FMT: dict[str, Fmt] = dict(_DELIMITERS)
_FMT2DELIM: dict[Fmt, str] = {v: k for k, v in _DELIM2FMT.items()}


def _prioritize_delims(node: Node) -> re.Pattern[str]:
    """Prioritize delimiters such that currently open Fmts are matched first."""
    if node.fmt in _NO_RECURSE:
        return re.compile(re.escape(_FMT2DELIM[node.fmt]))
    delims = [_FMT2DELIM[fmt] for fmt in reversed(node.fmts)]
    delims.extend([x for x in _DELIM2FMT if x not in delims])
    return re.compile("|".join(re.escape(d) for d in delims))


def _take_block(node: Node, text: str) -> tuple[Node, str]:
    """Open a new block and add the text as content or return the text to the queue."""
    if node.fmt == Fmt.DOCUMENT:
        text = "\n\n" + text
    match = _prioritize_delims(node).search(text)
    if match is None:
        if node.fmts:
            msg = "Reached end of text with unclosed formatting: "
            msg += ", ".join(x.value for x in node.fmts)
            raise ValueError(msg)
        _ = node.append(Fmt.PLAIN, text)
        return node, ""
    if match.start() > 0:
        _ = node.append(Fmt.PLAIN, text[: match.start()])
        return node, text[match.start() :]
    next_fmt = _DELIM2FMT[match.group(0)]
    if node.fmts and next_fmt == node.fmts[-1]:
        # closing
        if node.parent is None:
            msg = "Warning: found closing delimiter with no open formatting: "
            msg += next_fmt.value
            raise ValueError(msg)
        if next_fmt in node.fmts[:-1]:
            msg = "Warning: found closing delimiter for format that is not innermost: "
            msg += next_fmt.value
            raise ValueError(msg)
        # print(f"Closing {next_fmt.value} at {match.start()} with open formats: ")
        return node.parent, text[match.end() :]
    # print(f"Opening {next_fmt.value} at {match.start()} with open formats: ")
    return node.append(next_fmt, ""), text[match.end() :]


# TODO: autoclose QUOTE
# TODO: bullets


@dataclass
class Node:
    """A node in the markdown parse tree."""

    fmt: Fmt = Fmt.DOCUMENT
    content: str = ""
    parent: Node | None = None
    children: list[Node] = field(  # pyright: ignore[reportUnknownVariableType]
        init=False, default_factory=list
    )

    def append(self, fmt: Fmt, content: str = "") -> Self:
        """Append a child node with the given format and content."""
        child = type(self)(fmt, content, self)
        self.children.append(child)
        return child

    @property
    def fmts(self) -> tuple[Fmt, ...]:
        """The hierarchy of formats applied to this node."""
        fmts = self.parent.fmts if self.parent is not None else ()
        if self.fmt in _FMT2DELIM.keys():
            return (*fmts, self.fmt)
        return fmts


# def build_tree(text: str) -> Node:
#     """Parse the input text into a tree of nodes."""
#     text = text.strip('\n')
#     text = re.sub(r"\n\s*\* ", "\n\n* "
#     text = re.sub(r"\n{3,}", "\n\n", text)
#     text = f"{text}\n\n"
#     node = Node()
#     if not text.strip():
#         return node
#     while text:
#         print(text.replace("\n", "\\n"))
#         node, text = _take_block(node, text)
#     assert node.fmt == Fmt.DOCUMENT
#     return node


# _BLOCK_DELIMITERS: list[tuple[str, Fmt]] = [


_NO_RECURSE: frozenset[Fmt] = frozenset({Fmt.CODE, Fmt.CODE_BLOCK})

_OPEN_RE = re.compile("|".join(re.escape(d) for d, _ in _DELIMITERS))


text = "**This is bold and *italic*** te**xt**\n\n**an**d `co**no recurse**de` and ||spoiler||"


def print_node(node: Node, indent: int = 0) -> None:
    TAB = "  "
    if node.fmt == Fmt.PLAIN:
        # print(f"{TAB * indent}{node.content}")
        print(f"{node.content} {node.fmts}")
    # else:
    #     print(f"{TAB * indent}{node.fmt.value}:")
    for child in node.children:
        print_node(child, indent + 1)
    # if node.fmt != Fmt.PLAIN:
    #     print(f"{TAB * indent}END {node.fmt.value}")


aaa = build_tree(text)
print_node(aaa)
print("done")
