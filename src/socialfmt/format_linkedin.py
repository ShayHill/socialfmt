"""Format Markdown text for LinkedIn.

:author: Shay Hill
:created: 2026-10-29
"""

from typing import Literal, overload

from socialfmt.format_social import enforce_max_chars, format_file, reformat_markdown

_MAX_CHARS = 3000


@overloaddef reformat_markdown_for_linkedin(
    body: str, *, allow_thread: Literal[False]
) -> str: ...


@overload
def reformat_markdown_for_linkedin(
    body: str, *, allow_thread: Literal[True]
) -> list[str]: ...


def reformat_markdown_for_linkedin(
    body: str, *, allow_thread: bool = False
) -> str | list[str]:
    """Format markdown for LinkedIn, optionally splitting it into a thread."""
    body = reformat_markdown(body)
    return enforce_max_chars(
        body, _MAX_CHARS, allow_thread=allow_thread, content_name="LinkedIn post"
    )


def cli() -> None:
    """Reformat a Markdown file for LinkedIn and write a ``*_li`` sibling file."""
    format_file("_li", reformat_markdown_for_linkedin)


if __name__ == "__main__":
    cli()
