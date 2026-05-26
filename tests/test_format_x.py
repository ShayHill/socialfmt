"""Test markdown -> X formatting.

:author: Shay Hill
:created: 2026-05-24
"""

import pytest

from socialfmt import maps
from socialfmt.format_x import reformat_markdown_for_x


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
        assert (
            reformat_markdown_for_x("> **hello**") == maps.to_bold_italic("hello")
        )


class TestSmartTextPostProcessing:
    """The final output runs through dumb_text + smart_text."""

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

class TestNewlinesPreserved:
    """Treat single newlines as hard breaks, not spaces."""
    result = reformat_markdown_for_x("color red\ncolor green\ncolor blue")
    assert result == "color red\ncolor green\ncolor blue"
