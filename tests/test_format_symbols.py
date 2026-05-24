"""Test smart/dumb typographical substitution.

:author: Shay Hill
:created: 2026-05-24
"""

from socialfmt.format_symbols import dumb_text, smart_text


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

    def test_ellipsis(self):
        assert smart_text("and so on...") == "and so on…"

    def test_opening_guillemet(self):
        assert smart_text("<<hello") == "«hello"

    def test_empty(self):
        assert smart_text("") == ""


class TestDumbText:
    """Convert smart text back to plain text."""

    def test_double_quotes(self):
        assert dumb_text("He said “hi” to her.") == 'He said "hi" to her.'

    def test_single_quotes(self):
        assert dumb_text("Let’s ‘go’.") == "Let's 'go'."

    def test_en_dash(self):
        assert dumb_text("pages 3–5") == "pages 3--5"

    def test_em_dash(self):
        assert dumb_text("wait—really?") == "wait---really?"

    def test_ellipsis(self):
        assert dumb_text("and so on…") == "and so on..."

    def test_guillemets(self):
        assert dumb_text("«hello»") == "<<hello>>"

    def test_empty(self):
        assert dumb_text("") == ""


class TestCodeBlocksPreserved:
    """Content inside code blocks is left unchanged."""

    def test_inline_code_preserves_single_quotes(self):
        text = "Run `echo 'hi'` now."
        assert smart_text(text) == "Run `echo 'hi'` now."

    def test_inline_code_preserves_double_dashes(self):
        text = "Pass `--flag` here."
        assert smart_text(text) == "Pass `--flag` here."

    def test_inline_code_preserves_triple_dots(self):
        text = "Returns `foo(...)` always."
        assert smart_text(text) == "Returns `foo(...)` always."

    def test_text_outside_inline_code_still_converted(self):
        text = "Say 'hi' then `code 'here'` then 'bye'."
        assert smart_text(text) == "Say ‘hi’ then `code 'here'` then ‘bye’."

    def test_fenced_code_block_preserved(self):
        text = "before -- text\n```\ncode -- 'kept'\n```\nafter -- text"
        expect = "before – text\n```\ncode -- 'kept'\n```\nafter – text"
        assert smart_text(text) == expect

    def test_fenced_code_block_with_language_tag(self):
        text = "```py\nprint('hi -- there')\n```"
        assert smart_text(text) == text

    def test_multi_backtick_span_preserved(self):
        text = "use ``code with `tick` inside`` here"
        assert smart_text(text) == "use ``code with `tick` inside`` here"

    def test_dumb_text_preserves_code_blocks(self):
        text = "before — “smart” ``code — “raw”`` after — “smart”"
        expect = 'before --- "smart" ``code — “raw”`` after --- "smart"'
        assert dumb_text(text) == expect

    def test_code_block_at_start(self):
        text = "`x'y` then 'go'"
        assert smart_text(text) == "`x'y` then ‘go’"

    def test_code_block_at_end(self):
        text = "'go' then `x'y`"
        assert smart_text(text) == "‘go’ then `x'y`"

    def test_multiple_inline_spans(self):
        text = "'a' `b'c` 'd' `e'f` 'g'"
        assert smart_text(text) == "‘a’ `b'c` ‘d’ `e'f` ‘g’"


class TestUnmatchedBackticks:
    """A stray backtick is not a code span and should not block conversion."""

    def test_lone_backtick_does_not_block_conversion(self):
        assert smart_text("it's a ` lonely tick") == "it’s a ` lonely tick"


class TestRoundtrip:
    """``dumb_text`` inverts ``smart_text`` for quote/dash/ellipsis input."""

    def test_quotes_dashes_ellipses(self):
        dumb = "He said 'hi' -- then 'bye'..."
        assert dumb_text(smart_text(dumb)) == dumb

    def test_with_inline_code(self):
        dumb = "Run `echo 'hi' -- now` and 'wait'..."
        assert dumb_text(smart_text(dumb)) == dumb

    def test_with_fenced_code(self):
        dumb = "before -- text\n```py\nx = 'kept' -- always\n```\nafter -- text"
        assert dumb_text(smart_text(dumb)) == dumb
