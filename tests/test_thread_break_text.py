"""Test breaking text into thread-sized segments.

:author: Shay Hill
:created: 2026-05-24
"""

import pytest

from socialfmt.char_count import count_chars
from socialfmt.thread_break_text import break_into_thread, split_at_next_word


def _strip_footer(post: str, page: int, total: int, template: str = "\n\n{}/{}") -> str:
    """Remove the per-post footer so just the body can be compared."""
    footer = template.format(page, total)
    assert post.endswith(footer), f"post {post!r} does not end with footer {footer!r}"
    return post[: -len(footer)]


class TestSplitAtNextWord:
    """``split_at_next_word`` returns ``(left.strip(), right.lstrip())``."""

    def test_break_at_word_boundary(self):
        assert split_at_next_word("hello world foo", 5) == ("hello", "world foo")

    def test_break_one_past_boundary_snaps_back(self):
        # start=6 should still find the space at index 5 (search begins at start-1).
        assert split_at_next_word("hello world foo", 6) == ("hello", "world foo")

    def test_newline_is_a_word_boundary(self):
        assert split_at_next_word("hello\nworld", 3) == ("hello", "world")

    def test_no_word_boundary_returns_whole_text(self):
        # No space at or after start - 1 → next_word_break = len(text).
        assert split_at_next_word("nospaces", 3) == ("nospaces", "")


class TestBreakIntoThreadShortText:
    """Text shorter than ``max_chars`` is returned as a string, not a list."""

    def test_short_text_returns_string(self):
        assert break_into_thread("hello world", 100) == "hello world"

    def test_leading_and_trailing_whitespace_stripped(self):
        assert break_into_thread("  hello world  ", 100) == "hello world"

    def test_text_exactly_at_max_chars(self):
        text = "a" * 50
        assert break_into_thread(text, 50) == text


class TestBreakIntoThreadMultiPost:
    """Text longer than ``max_chars`` is broken into a list of posts."""

    @staticmethod
    def _make_text(words: int) -> str:
        return " ".join(f"word{i}" for i in range(words))

    def test_returns_list_when_text_overflows(self):
        result = break_into_thread(self._make_text(50), 60)
        assert isinstance(result, list)

    def test_each_post_within_max_chars(self):
        max_chars = 60
        result = break_into_thread(self._make_text(50), max_chars)
        assert isinstance(result, list)
        for post in result:
            assert count_chars(post) <= max_chars

    def test_posts_in_original_order(self):
        text = self._make_text(50)
        result = break_into_thread(text, 60)
        assert isinstance(result, list)
        # The body of the first post should be a prefix of the input.
        first_body = _strip_footer(result[0], 1, len(result)).strip()
        assert text.startswith(first_body)

    def test_posts_reconstruct_input(self):
        text = self._make_text(50)
        result = break_into_thread(text, 60)
        assert isinstance(result, list)
        bodies = [
            _strip_footer(post, i + 1, len(result)).strip()
            for i, post in enumerate(result)
        ]
        assert " ".join(bodies) == text

    def test_footers_count_up(self):
        result = break_into_thread(self._make_text(50), 60)
        assert isinstance(result, list)
        n = len(result)
        for i, post in enumerate(result):
            assert post.endswith(f"\n\n{i + 1}/{n}")


class TestBreakIntoThreadBreakpointPreference:
    """Splits prefer paragraph > sentence > comma > word."""

    def test_splits_at_paragraph_when_possible(self):
        text = "First paragraph here.\n\nSecond paragraph here, also nontrivial."
        result = break_into_thread(text, 35)
        assert isinstance(result, list)
        body = _strip_footer(result[0], 1, len(result)).strip()
        assert body == "First paragraph here."

    def test_splits_at_sentence_when_no_paragraph_break(self):
        text = "First sentence here. Second sentence here, also nontrivial."
        result = break_into_thread(text, 35)
        assert isinstance(result, list)
        body = _strip_footer(result[0], 1, len(result)).strip()
        assert body == "First sentence here."

    def test_par_break_dots_adds_dot_after_paragraph_split(self):
        text = "First paragraph here.\n\nSecond paragraph here, also nontrivial."
        result = break_into_thread(text, 35, par_break_dots=True)
        assert isinstance(result, list)
        body = _strip_footer(result[1], 2, len(result))
        assert body.startswith(".\n")


class TestBreakIntoThreadFooterTemplate:
    """Custom and empty footer templates."""

    def test_empty_footer(self):
        text = "a b c d e f g h i j k l m n o p q r s t"
        result = break_into_thread(text, 12, footer_template="")
        assert isinstance(result, list)
        for post in result:
            assert count_chars(post) <= 12

    def test_single_placeholder_footer(self):
        text = " ".join(f"word{i}" for i in range(30))
        result = break_into_thread(text, 40, footer_template=" [{}]")
        assert isinstance(result, list)
        for i, post in enumerate(result):
            assert post.endswith(f" [{i + 1}]")

    def test_too_many_placeholders_raises(self):
        text = " ".join(f"word{i}" for i in range(30))
        with pytest.raises(ValueError):
            _ = break_into_thread(text, 20, footer_template="\n{}/{}/{}")


class TestBreakIntoThreadEdgeCases:
    """Error and boundary behavior."""

    def test_max_chars_too_small_for_footer_reserve_raises(self):
        # Default footer reserve dominates at very small max_chars.
        with pytest.raises(ValueError):
            _ = break_into_thread("the quick brown fox jumps over", 3)

    def test_unbreakable_long_word_raises(self):
        # A single word longer than max_chars has no word boundary at all.
        with pytest.raises(ValueError):
            _ = break_into_thread("a" * 100, 30)
