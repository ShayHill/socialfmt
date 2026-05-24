"""Test character counting and splitting.

:author: Shay Hill
:created: 2026-05-24
"""

import pytest

from socialfmt.char_count import count_chars, split_at_chars


class TestCountChars:
    """Count strings as UTF-16 code units."""

    def test_empty(self):
        assert count_chars("") == 0

    def test_ascii(self):
        assert count_chars("hello") == 5

    def test_ascii_with_spaces(self):
        assert count_chars("hello world") == 11

    def test_bmp_accented(self):
        assert count_chars("café") == 4

    def test_bmp_cyrillic(self):
        assert count_chars("привет") == 6

    def test_math_italic_is_two_code_units(self):
        # U+1D456 MATHEMATICAL ITALIC SMALL I is outside the BMP and so
        # encodes as a UTF-16 surrogate pair (2 code units).
        assert count_chars("𝑖") == 2

    def test_emoji_is_two_code_units(self):
        # U+1F600 GRINNING FACE is outside the BMP.
        assert count_chars("😀") == 2

    def test_flag_is_four_code_units(self):
        # 🇺🇸 is two regional-indicator codepoints, each a surrogate pair.
        assert count_chars("🇺🇸") == 4

    def test_mixed_bmp_and_supplementary(self):
        assert count_chars("a😀b") == 4

    def test_newline(self):
        assert count_chars("a\nb") == 3


class TestSplitAtChars:
    """Split a string at whitespace or punctuation, no later than max_chars.

    The function returns ``(rest, head)`` — the first element is what
    remains after the split, the second is the chunk up to and including
    the split character.
    """

    def test_splits_at_latest_space(self):
        rest, head = split_at_chars("hello world foo", 12)
        assert head == "hello world "
        assert rest == "foo"

    def test_splits_at_punctuation(self):
        rest, head = split_at_chars("hello,world,foo", 12)
        assert head == "hello,world,"
        assert rest == "foo"

    def test_picks_highest_valid_breakpoint(self):
        rest, head = split_at_chars("a b c d e f g h i", 8)
        assert head == "a b c d "
        assert rest == "e f g h i"

    def test_concatenation_recovers_original(self):
        original = "the quick brown fox jumps over the lazy dog"
        rest, head = split_at_chars(original, 20)
        assert head + rest == original

    def test_head_fits_within_max_chars(self):
        rest, head = split_at_chars("the quick brown fox jumps", 20)
        del rest
        assert count_chars(head) <= 20

    def test_raises_when_no_breakpoint_available(self):
        with pytest.raises(ValueError):
            _ = split_at_chars("nowhitespaceavailable", 5)

    def test_raises_when_leading_chunk_has_no_breakpoint(self):
        # A space exists, but only past max_chars — must still raise.
        with pytest.raises(ValueError):
            _ = split_at_chars("abcdefghij klmnop", 5)
