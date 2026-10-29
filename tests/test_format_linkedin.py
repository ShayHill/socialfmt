"""Test Markdown -> LinkedIn formatting.

:author: Shay Hill
:created: 2026-10-29
"""

from pathlib import Path

import pytest

from socialfmt import maps
from socialfmt.format_linkedin import cli, main, reformat_markdown_for_linkedin


def test_reformat_markdown_for_linkedin() -> None:
    """LinkedIn formatting uses the shared Unicode renderer."""
    assert reformat_markdown_for_linkedin("**hello**") == maps.to_bold("hello")


def test_main_returns_a_list_when_threading_is_allowed() -> None:
    """Threaded output is a list even when its body fits in one post."""
    assert main("hello", allow_thread=True) == ["hello"]


def test_cli_writes_linkedin_suffixed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The script writes a ``*_li`` sibling file."""
    input_path = tmp_path / "post.md"
    _ = input_path.write_text("**hello**", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["format_linkedin", str(input_path)])

    cli()

    assert (tmp_path / "post_li.md").read_text(encoding="utf-8") == maps.to_bold(
        "hello"
    )
