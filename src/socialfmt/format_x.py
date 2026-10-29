"""Format markdown text for X.

- Emphasized text for blockquotes.
- Raise a ValueError for `||`, which might be a failed attempt at spoiler tags.

:author: Shay Hill
:created: 2026-05-22
"""

import argparse
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import cast

from mistletoe.block_token import Document as MistletoeDocument
from mistletoe.token import Token

from socialfmt import maps
from socialfmt.format_symbols import smart_text


def _no_fmt(text: str) -> str:
    return text


# These node names will never contribute to span styles.
_IGNORE_FOR_SPAN_STYLES = {"Document", "Paragraph", "RawText"}
_BULLET = "\u2022"


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
        yield f"{_BULLET} "
    style = _get_nested_styles(node)
    if name == "RawText":
        content = cast("str", getattr(node, "content", None))
        if "InlineCode" not in style and "CodeFence" not in style:
            content = smart_text(content)
        formatter = _find_formatter(style)
        yield formatter(content)
    for child in cast("list[Token] | None", getattr(node, "children", None)) or []:
        yield from _reformat_ast_to_unicode_styles(child, nested_formats)
    if name in {"List", "LineBreak"}:
        yield "\n"
    elif name == "Paragraph":
        yield "\n"
        if "ListItem" not in style:
            yield "\n"


def reformat_markdown_for_x(text: str) -> str:
    """Emulate markdown formatting with unicode characters."""
    document = MistletoeDocument(text)
    return "".join(_reformat_ast_to_unicode_styles(document)).strip()


def main() -> None:
    """Reformat a Markdown file for X and write a sibling ``*_x`` file."""
    parser = argparse.ArgumentParser()
    _ = parser.add_argument("input_path", type=Path)
    args = parser.parse_args()

    input_path = args.input_path
    output_path = input_path.with_stem(f"{input_path.stem}_x")
    output_path.write_text(
        reformat_markdown_for_x(input_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
