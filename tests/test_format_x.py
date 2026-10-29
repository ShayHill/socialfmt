"""Test markdown -> X formatting.

:author: Shay Hill
:created: 2026-05-24
"""

from pathlib import Path

import pytest

from socialfmt import maps
from socialfmt.format_x import _MAX_CHARS, cli, reformat_markdown_for_x


class TestRejectSpoilerTags:
    """``reformat_markdown_for_x`` raises ``ValueError`` on ``||`` outside code."""

    def test_plain_spoiler_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = _MAX_CHARS("hello ||secret|| world")

    def test_bare_double_pipe_still_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = _MAX_CHARS("a||b")

    def test_single_pipe_is_allowed(self):
        # A single ``|`` is not a spoiler marker.
        assert _MAX_CHARS("a | b") == "a | b"

    def test_pipe_inside_inline_code_allowed(self):
        # Must not raise.
        _ = _MAX_CHARS("see `a || b` here")

    def test_pipe_inside_fenced_code_allowed(self):
        # Must not raise.
        _ = _MAX_CHARS("before\n```\nx || y\n```\nafter")

    def test_pipe_after_code_still_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = _MAX_CHARS("`code` then ||spoiler||")

    def test_pipe_before_code_still_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = _MAX_CHARS("||spoiler|| then `code`")

    def test_pipe_straddling_code_block_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = _MAX_CHARS("a||\n```\nb\n```\n||c")


class TestSpanFormatting:
    """Inline spans render as unicode-styled characters."""

    def test_plain_text(self):
        assert _MAX_CHARS("hello world") == "hello world"

    def test_italic(self):
        assert _MAX_CHARS("*hello*") == maps.to_italic("hello")

    def test_bold(self):
        assert _MAX_CHARS("**hello**") == maps.to_bold("hello")

    def test_bold_italic(self):
        assert _MAX_CHARS("***hello***") == maps.to_bold_italic("hello")

    def test_inline_code(self):
        assert _MAX_CHARS("`hello`") == maps.to_mono("hello")


class TestBlockquote:
    """``> `` blockquotes render as italic."""

    def test_blockquote_is_italic(self):
        assert _MAX_CHARS("> hello") == maps.to_italic("hello")

    def test_bold_inside_blockquote_is_bold_italic(self):
        assert _MAX_CHARS("> **hello**") == maps.to_bold_italic("hello")


class TestLists:
    """Unordered lists render with bullet markers."""

    @pytest.mark.parametrize("leader", ["*", "-"])
    def test_unordered_list_markers(self, leader: str):
        assert _MAX_CHARS(f"{leader} item") == "\u2022 item"


class TestSmartTextFormatting:
    """Non-code text runs through dumb_text + smart_text."""

    def test_single_quotes_become_curly(self):
        result = _MAX_CHARS("She said 'hi'.")
        assert "‘hi’" in result

    def test_double_quotes_become_curly(self):
        result = _MAX_CHARS('She said "hi".')
        assert "“hi”" in result

    def test_double_hyphen_becomes_en_dash(self):
        result = _MAX_CHARS("pages 3--5")
        assert "3–5" in result

    def test_triple_hyphen_becomes_em_dash(self):
        result = _MAX_CHARS("wait---now")
        assert "wait—now" in result

    def test_triple_dot_becomes_ellipsis(self):
        result = _MAX_CHARS("wait...")
        assert "…" in result


class TestCodeSymbolsPreserved:
    """Code punctuation is not converted to smart typography."""

    def test_inline_code_symbols(self):
        content = "'quoted' -- --- ..."
        assert _MAX_CHARS(f"`{content}`") == maps.to_mono(content)

    def test_fenced_code_symbols(self):
        content = "quoted -- --- ..."
        text = f"```\n{content}\n```"
        assert _MAX_CHARS(text) == maps.to_mono(content)


class TestNewlinesPreserved:
    """Treat single newlines as hard breaks, not spaces."""

    result = _MAX_CHARS("color red\ncolor green\ncolor blue")
    assert result == "color red\ncolor green\ncolor blue"


def test_main_returns_a_list_when_threading_is_allowed() -> None:
    """Threaded output is a list even when its body fits in one post."""
    assert reformat_markdown_for_x("hello", allow_thread=True) == ["hello"]


def test_main_rejects_an_overlong_tweet() -> None:
    """Non-threaded output must fit X's character limit."""
    with pytest.raises(ValueError, match="tweet longer"):
        _ = reformat_markdown_for_x("word " * 100)


def test_main_counts_a_leading_url_as_twenty_three_characters() -> None:
    """X measures a leading URL by its shortened, fixed-length representation."""
    url = "https://example.com/" + "a" * 300

    assert reformat_markdown_for_x(url) == url


def test_cli_writes_x_suffixed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The script writes reformatted text beside its input file."""
    input_path = tmp_path / "post.md"
    _ = input_path.write_text("**hello**", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["format_x", str(input_path)])

    cli()

    assert (tmp_path / "post_x.md").read_text(encoding="utf-8") == maps.to_bold("hello")


def test_cli_writes_threaded_posts_with_separators(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The thread flag writes posts into one sibling file with separators."""
    input_path = tmp_path / "post.md"
    body = "word " * 100
    _ = input_path.write_text(body, encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["format_x", "--allow_thread", str(input_path)])

    cli()

    expected = "\n\n---\n\n".join(reformat_markdown_for_x(body, allow_thread=True))
    assert (tmp_path / "post_x.md").read_text(encoding="utf-8") == expected
