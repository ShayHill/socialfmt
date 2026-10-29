"""Format Markdown text for X.

:author: Shay Hill
:created: 2026-05-22
"""

from typing import Literal, overload

from socialfmt.format_social import enforce_max_chars, format_file, reformat_markdown

_MAX_CHARS = 280


@overload
def reformat_markdown_for_x(body: str, *, allow_thread: Literal[False]) -> str: ...


@overload
def reformat_markdown_for_x(body: str, *, allow_thread: Literal[True]) -> list[str]: ...


def reformat_markdown_for_x(
    body: str, *, allow_thread: bool = False
) -> str | list[str]:
    """Format a tweet for X, optionally splitting it into a thread."""
    body = reformat_markdown(body)
    return enforce_max_chars(
        body, _MAX_CHARS, allow_thread=allow_thread, content_name="tweet"
    )


def cli() -> None:
    """Reformat a Markdown file for X and write a sibling ``*_x`` file."""
    format_file("_x", reformat_markdown_for_x)


if __name__ == "__main__":
    cli()
