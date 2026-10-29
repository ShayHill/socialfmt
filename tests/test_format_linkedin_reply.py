"""Test Markdown -> LinkedIn reply formatting.

:author: Shay Hill
:created: 2026-10-29
"""

from socialfmt.format_linkedin_reply import MAX_CHARS, main


def test_main_returns_a_list_when_threading_is_allowed() -> None:
    """Threaded output is a list even when its body fits in one reply."""
    assert main("hello", allow_thread=True) == ["hello"]


def test_main_rejects_an_overlong_reply() -> None:
    """Non-threaded output must fit LinkedIn's reply character limit."""
    body = "word " * (MAX_CHARS // 4)
    try:
        _ = main(body)
    except ValueError:
        return
    msg = "expected an overlong reply to raise ValueError"
    raise AssertionError(msg)
