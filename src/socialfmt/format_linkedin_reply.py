"""Format Markdown text for LinkedIn.

:author: Shay Hill
:created: 2026-10-29
"""

from typing import Literal, overload

from socialfmt.format_social import enforce_max_chars, format_file, reformat_markdown

_MAX_CHARS = 1250


@overload
def reformat_markdown_for_linkedin_reply(
    body: str, *, allow_thread: Literal[False]
) -> str: ...


@overload
def reformat_markdown_for_linkedin_reply(
    body: str, *, allow_thread: Literal[True]
) -> list[str]: ...


@overload
def reformat_markdown_for_linkedin_reply(
    body: str, *, allow_thread: bool
) -> str | list[str]: ...


def reformat_markdown_for_linkedin_reply(
    body: str, *, allow_thread: bool = False
) -> str | list[str]:
    """Format a LinkedIn reply, optionally splitting it into a thread."""
    body = reformat_markdown(body)
    return enforce_max_chars(
        body, _MAX_CHARS, allow_thread=allow_thread, content_name="LinkedIn reply"
    )


def cli() -> None:
    """Reformat a Markdown file as a LinkedIn reply. Write an ``*_li`` sibling file."""
    format_file("_li", reformat_markdown_for_linkedin_reply)


if __name__ == "__main__":
    cli()
