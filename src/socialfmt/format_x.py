"""Format Markdown text for X.

:author: Shay Hill
:created: 2026-05-22
"""

from typing import Literal, overload

from socialfmt.char_count import get_and_mark_one_url, put_back_url
from socialfmt.format_social import enforce_max_chars, format_file, reformat_markdown

_MAX_CHARS = 280


@overload
def reformat_markdown_for_x(body: str, *, allow_thread: Literal[False]) -> str: ...


@overload
def reformat_markdown_for_x(body: str, *, allow_thread: Literal[True]) -> list[str]: ...


@overload
def reformat_markdown_for_x(body: str, *, allow_thread: bool) -> str | list[str]: ...


def reformat_markdown_for_x(
    body: str, *, allow_thread: bool = False
) -> str | list[str]:
    """Format a tweet for X, optionally splitting it into a thread."""
    body = reformat_markdown(body)
    body, url = get_and_mark_one_url(body)
    formatted = enforce_max_chars(
        body, _MAX_CHARS, allow_thread=allow_thread, content_name="tweet"
    )
    if isinstance(formatted, list):
        first, *rest = formatted
        return [put_back_url(first, url), *rest]
    return put_back_url(formatted, url)


def cli() -> None:
    """Reformat a Markdown file for X and write a sibling ``*_x`` file."""
    format_file("_x", reformat_markdown_for_x)


if __name__ == "__main__":
    cli()
