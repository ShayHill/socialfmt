"""Test markdown -> X formatting.

:author: Shay Hill
:created: 2026-05-24
"""

from pathlib import Path

import pytest

from socialfmt import maps
from socialfmt.format_x import main, reformat_markdown_for_x


class TestRejectSpoilerTags:
    """``reformat_markdown_for_x`` raises ``ValueError`` on ``||`` outside code."""

    def test_plain_spoiler_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = reformat_markdown_for_x("hello ||secret|| world")

    def test_bare_double_pipe_still_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = reformat_markdown_for_x("a||b")

    def test_single_pipe_is_allowed(self):
        # A single ``|`` is not a spoiler marker.
        assert reformat_markdown_for_x("a | b") == "a | b"

    def test_pipe_inside_inline_code_allowed(self):
        # Must not raise.
        _ = reformat_markdown_for_x("see `a || b` here")

    def test_pipe_inside_fenced_code_allowed(self):
        # Must not raise.
        _ = reformat_markdown_for_x("before\n```\nx || y\n```\nafter")

    def test_pipe_after_code_still_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = reformat_markdown_for_x("`code` then ||spoiler||")

    def test_pipe_before_code_still_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = reformat_markdown_for_x("||spoiler|| then `code`")

    def test_pipe_straddling_code_block_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = reformat_markdown_for_x("a||\n```\nb\n```\n||c")


class TestSpanFormatting:
    """Inline spans render as unicode-styled characters."""

    def test_plain_text(self):
        assert reformat_markdown_for_x("hello world") == "hello world"

    def test_italic(self):
        assert reformat_markdown_for_x("*hello*") == maps.to_italic("hello")

    def test_bold(self):
        assert reformat_markdown_for_x("**hello**") == maps.to_bold("hello")

    def test_bold_italic(self):
        assert reformat_markdown_for_x("***hello***") == maps.to_bold_italic("hello")

    def test_inline_code(self):
        assert reformat_markdown_for_x("`hello`") == maps.to_mono("hello")


class TestBlockquote:
    """``> `` blockquotes render as italic."""

    def test_blockquote_is_italic(self):
        assert reformat_markdown_for_x("> hello") == maps.to_italic("hello")

    def test_bold_inside_blockquote_is_bold_italic(self):
        assert reformat_markdown_for_x("> **hello**") == maps.to_bold_italic("hello")


class TestLists:
    """Unordered lists render with bullet markers."""

    @pytest.mark.parametrize("leader", ["*", "-"])
    def test_unordered_list_markers(self, leader: str):
        assert reformat_markdown_for_x(f"{leader} item") == "\u2022 item"


class TestSmartTextFormatting:
    """Non-code text runs through dumb_text + smart_text."""

    def test_single_quotes_become_curly(self):
        result = reformat_markdown_for_x("She said 'hi'.")
        assert "‘hi’" in result

    def test_double_quotes_become_curly(self):
        result = reformat_markdown_for_x('She said "hi".')
        assert "“hi”" in result

    def test_double_hyphen_becomes_en_dash(self):
        result = reformat_markdown_for_x("pages 3--5")
        assert "3–5" in result

    def test_triple_hyphen_becomes_em_dash(self):
        result = reformat_markdown_for_x("wait---now")
        assert "wait—now" in result

    def test_triple_dot_becomes_ellipsis(self):
        result = reformat_markdown_for_x("wait...")
        assert "…" in result


class TestCodeSymbolsPreserved:
    """Code punctuation is not converted to smart typography."""

    def test_inline_code_symbols(self):
        content = "'quoted' -- --- ..."
        assert reformat_markdown_for_x(f"`{content}`") == maps.to_mono(content)

    def test_fenced_code_symbols(self):
        content = "quoted -- --- ..."
        text = f"```\n{content}\n```"
        assert reformat_markdown_for_x(text) == maps.to_mono(content)


class TestNewlinesPreserved:
    """Treat single newlines as hard breaks, not spaces."""

    result = reformat_markdown_for_x("color red\ncolor green\ncolor blue")
    assert result == "color red\ncolor green\ncolor blue"


def test_main_writes_x_suffixed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The script writes reformatted text beside its input file."""
    input_path = tmp_path / "post.md"
    _ = input_path.write_text("**hello**", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["format_x", str(input_path)])

    main()

    assert (tmp_path / "post_x.md").read_text(encoding="utf-8") == maps.to_bold("hello")
