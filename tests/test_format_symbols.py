"""Test smart/dumb typographical substitution.

:author: Shay Hill
:created: 2026-05-24
"""

# pyright: reportPrivateUsage=false

import pytest

from socialfmt.format_symbols import _DumbText, smart_text


class TestSmartText:
    """Convert plain text to typographically smart text."""

    def test_double_quotes(self):
        assert smart_text('He said "hi" to her.') == "He said “hi” to her."

    def test_single_quotes(self):
        assert smart_text("Let's 'go'.") == "Let’s ‘go’."

    def test_nested_quotes(self):
        assert smart_text("\"'hello'\"") == "“‘hello’”"

    def test_apostrophe_inside_quoted_phrase(self):
        assert smart_text('He said "Don\'t" loud.') == "He said “Don’t” loud."

    def test_en_dash(self):
        assert smart_text("pages 3--5") == "pages 3–5"

    def test_em_dash(self):
        assert smart_text("wait---really?") == "wait—really?"

    def test_long_dash_run(self):
        assert smart_text("wait----really?") == "wait----really?"

    def test_ellipsis(self):
        assert smart_text("and so on...") == "and so on…"

    def test_opening_guillemet(self):
        assert smart_text("<<hello") == "«hello"

    def test_empty(self):
        assert smart_text("") == ""

    def test_spoiler_tag_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = smart_text("hello ||secret||")

    def test_spoiler_tag_in_markdown_code_raises(self):
        with pytest.raises(ValueError, match="spoiler"):
            _ = smart_text("`hello ||secret||`")


class TestDumbText:
    """Convert smart text back to plain text."""

    def test_double_quotes(self):
        assert _DumbText.apply("He said “hi” to her.") == 'He said "hi" to her.'

    def test_single_quotes(self):
        assert _DumbText.apply("Let’s ‘go’.") == "Let's 'go'."

    def test_en_dash(self):
        assert _DumbText.apply("pages 3–5") == "pages 3--5"

    def test_em_dash(self):
        assert _DumbText.apply("wait—really?") == "wait---really?"

    def test_ellipsis(self):
        assert _DumbText.apply("and so on…") == "and so on..."

    def test_guillemets(self):
        assert _DumbText.apply("«hello»") == "<<hello>>"

    def test_empty(self):
        assert _DumbText.apply("") == ""


class TestMarkdownDelimiters:
    """Markdown delimiters do not change symbol formatting behavior."""

    def test_inline_code_delimiters(self):
        text = "Run `echo 'hi' -- ...` now."
        assert smart_text(text) == "Run `echo ‘hi’ – …` now."

    def test_fenced_code_delimiters(self):
        text = "```\ncode -- 'kept'\n```"
        assert smart_text(text) == "```\ncode – ‘kept’\n```"


class TestRoundtrip:
    """``_DumbText.apply`` inverts ``smart_text`` for quote/dash/ellipsis input."""

    def test_quotes_dashes_ellipses(self):
        dumb = "He said 'hi' -- then 'bye'..."
        assert _DumbText.apply(smart_text(dumb)) == dumb

    def test_with_inline_code(self):
        dumb = "Run `echo 'hi' -- now` and 'wait'..."
        assert _DumbText.apply(smart_text(dumb)) == dumb

    def test_with_fenced_code(self):
        dumb = "before -- text\n```py\nx = 'kept' -- always\n```\nafter -- text"
        assert _DumbText.apply(smart_text(dumb)) == dumb
