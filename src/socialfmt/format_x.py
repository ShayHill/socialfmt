"""Format markdown text for X.

- Emphasized text for blockquotes.
- Raise a ValueError for `||`, which might be a failed attempt at spoiler tags.

:author: Shay Hill
:created: 2026-05-22
"""

from collections.abc import Callable, Iterator
from typing import cast

from mistletoe.block_token import Document as MistletoeDocument
from mistletoe.token import Token

from socialfmt import maps
from socialfmt.format_symbols import CODE_RE, dumb_text, smart_text


def _reject_spoiler_tags(text: str) -> None:
    """Raise ``ValueError`` if ``||`` appears outside a code block."""
    last_end = 0
    for match in CODE_RE.finditer(text):
        if "||" in text[last_end : match.start()]:
            break
        last_end = match.end()
    else:
        if "||" not in text[last_end:]:
            return
    msg = "spoiler tags (||...||) are not supported on X"
    raise ValueError(msg)


# These node names will never contribute to span styles.
_IGNORE_FOR_SPAN_STYLES = {"Document", "Paragraph", "RawText"}


def _no_fmt(text: str) -> str:
    return text


_FMT2FORMATTER: dict[str | tuple[str, ...], Callable[[str], str]] = {
    ("CodeFence",): maps.to_mono,
    ("Emphasis", "Strong"): maps.to_bold_italic,
    ("Emphasis",): maps.to_italic,
    ("InlineCode",): maps.to_mono,
    ("Quote", "Emphasis"): maps.to_normal,
    ("Quote", "Emphasis", "Strong"): maps.to_bold,
    ("Quote", "Strong"): maps.to_bold_italic,
    ("Quote", "Strong", "Emphasis"): maps.to_bold,
    ("Quote",): maps.to_italic,
    ("Strikethrough",): maps.to_strikethrough,
    ("Strong", "Emphasis"): maps.to_bold_italic,
    ("Strong",): maps.to_bold,
    (): _no_fmt,
}

# For debugging purposes, keep track of what formats return what simplified formats.
fmt2simplified_fmt: dict[tuple[str, ...], tuple[str, ...]] = {}


def __simplify_to_known_fmt(fmt: tuple[str, ...]) -> tuple[str, ...]:
    """Find a key to a formatter in _FMT2FORMATTER."""
    if fmt in _FMT2FORMATTER:
        return fmt
    return __simplify_to_known_fmt(fmt[1:])


def _simplify_to_known_fmt(fmt: tuple[str, ...]) -> tuple[str, ...]:
    """Find a key to a formatter in _FMT2FORMATTER. Keep a record."""
    found = __simplify_to_known_fmt(fmt)
    if found != fmt:
        fmt2simplified_fmt[fmt] = found
    return found


def _find_formatter(fmt: tuple[str, ...]) -> Callable[[str], str]:
    """Find a text formatter function given inherited styles."""
    return _FMT2FORMATTER[_simplify_to_known_fmt(fmt)]


def _get_nested_styles(node: Token | None) -> tuple[str, ...]:
    """Return all node span formats from root down."""
    if node is None:
        return ()
    pref = _get_nested_styles(node.parent)
    name = node.__class__.__name__
    if name in _IGNORE_FOR_SPAN_STYLES:
        return pref
    return (*pref, name)


def _reformat_ast_to_unicode_styles(
    node: Token, nested_formats: tuple[str, ...] = ()
) -> Iterator[str]:
    """Yield reformatted text given the ast root node."""
    name = node.__class__.__name__
    if name == "ListItem":
        leader = cast("str", getattr(node, "leader", ""))
        yield "• " if leader == "*" else f"{leader} "
    style = _get_nested_styles(node)
    if name == "RawText":
        content = cast("str", getattr(node, "content", None))
        formatter = _find_formatter(style)
        yield formatter(content)
    for child in cast("list[Token] | None", getattr(node, "children", None)) or []:
        yield from _reformat_ast_to_unicode_styles(child, nested_formats)
    if name == "List":
        yield "\n"
    elif name == "LineBreak":
        yield "\n"
    elif name == "Paragraph":
        yield "\n"
        if "ListItem" not in style:
            yield "\n"


def reformat_markdown_for_x(text: str) -> str:
    """Emulate markdown formatting with unicode characters."""
    _reject_spoiler_tags(text)
    document = MistletoeDocument(text)
    md_formatted = "".join(_reformat_ast_to_unicode_styles(document)).strip()
    return smart_text(dumb_text(md_formatted))

