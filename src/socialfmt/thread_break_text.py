"""Split long text into thread-sized segments with page markers.

* Break at double newline
* Failing that, break after the next word[1] after a sentence terminator
* Failing that, break after the next word[1] after a comma
* Failing that, break after the next word[1]
* Failing that, raise ValueError

[1] A word boundary is a space, newline, or end of string.

The implementation is a little brittle, because it depends on careful stripping to
* prevent invisible spaces and newlines from contributing to character count
* avoid losing word boundaries when text is split and rejoined.

Example:
input = "part_a part_b part_c"
-> ["part_a", "part_b ", "part_c"]
             |       ^ this space must be preserved
             ^ space intentionally discarded
-> head = "part_a"  |  tail = "part_b "  | todo = "part_c"
-> done = ["part_a"]  |  todo = tail + todo = ["part_b part_c"]

:author: Shay Hill
:created: 2026-04-01
"""

from socialfmt.char_count import count_chars, split_at_chars

# highest to lowest priority terminators. Lists are terminators of equal priority.
_TERMINATORS: list[list[str] | str] = [
    "\n\n",
    "\n",
    list(".?!:;"),
    ",",
    " ",
]


def _split_at_next_word(text: str, start: int) -> tuple[str, str]:
    """Find the next space in the text starting at the given index.

    :param text: The text to split
    :param start: The index to start searching for a space
    :return: A tuple of the text before the word break and the text after the word
        break. The break itself (spaces or newlines) is stripped. Any break characters
        would be between posts, and there is no difference in behavior between
        paragraphs between posts and sentences between posts.
    """
    word_boundaries = " \n"
    candidate_breaks = (text.find(x, start - 1) for x in word_boundaries)
    candidate_breaks = (x for x in candidate_breaks if x > -1)
    next_word_break = min(candidate_breaks, default=len(text))
    return text[:next_word_break].strip(), text[next_word_break:].lstrip()


def _rfind_terminator(text: str, terminator: list[str] | str) -> int:
    """Find the last occurrence of a terminator in text."""
    if isinstance(terminator, str):
        return text.rfind(terminator, 1)
    return max(text.rfind(y, 1) for y in terminator)


def _break_text(text: str) -> tuple[str, str]:
    """Break text into two parts.

    Break at par if at least half the text is captured.
    Break at sentence terminator if at least half the text is captured.
    Break at comma if at least half the text is captured.
    Break at word if at least half the text is captured.
    Break at any potential split point if all fail to capture at least half the text.
    Do not split in the middle of a word. Raise ValueError if no word boundary is found.
    """
    splits = [_rfind_terminator(text, x) for x in _TERMINATORS]
    splits = [x for x in splits if x > -1]
    for split in splits:
        part_a, part_b = _split_at_next_word(text, split)
        if len(part_b) < len(part_a):
            return part_a, part_b
    if splits:
        # A long word or some other condition prevents part_a from ever being longer
        # than part_b. This is a better choice than splitting a word.
        return _split_at_next_word(text, max(splits))
    msg = f"No word boundary found in '{text}'"
    raise ValueError(msg)


def break_into_thread(
    text: str,
    max_chars: int,
    footer_template: str = "\n\n{}/{}",
    *,
    par_break_dots: bool = False,
    _allow_chars_for_total_pages: int = 1,
) -> list[str] | str:
    """Split text into thread segments of at most max_chars each including markers.

    :param text: Full text to split
    :param max_chars: Maximum length per segment including thread markers. For free X,
        this is 280. For free Discord, this is 2000.
    :param footer_template: `str.format` template for the page marker after a blank
        line. Will have two `{}` placeholders for the current page number and the total
        number of pages. Include any desired leading newline characters.
    :param par_break_dots: Optionally add a dot at the top of a post that comes after a
        paragraph break. This is mainly for Discord, where subsequent posts with the
        same timestamp will appear closer together than subsequent paragraphs in one
        post.
    :param _allow_chars_for_total_pages: Reserved character width for the total page
        count in `page_count` (unknown until splitting finishes). This is meant for
        internal use. If the default value does not produce a satisfactory result (any
        post is too long), the value is automatically increased.
    """
    input_text = text
    text = text.strip()
    if count_chars(text) <= max_chars:
        return text
    parts: list[str] = []
    fields = footer_template.count("{}")
    if fields > 2:
        msg = "page_count_template must have at most two {} placeholders"
        raise ValueError(msg)
    while True:
        footer_chars = count_chars(footer_template) - fields * 2
        footer_chars += len(str(len(parts) + 1)) if fields else 0
        footer_chars += _allow_chars_for_total_pages if fields == 2 else 0
        max_body_chars = max_chars - footer_chars
        if max_body_chars <= 0:
            msg = "max_chars is too small for page marker reserve"
            raise ValueError(msg)

        if count_chars(text) <= max_body_chars:
            break
        head, text = split_at_chars(text, max_body_chars)
        next_part, tail = _break_text(head)
        if (
            head[len(next_part) : len(next_part) + 2] == "\n\n"
            and par_break_dots
            and tail.strip()
        ):
            tail = ".\n" + tail
        parts.append(next_part)
        text = (tail + text).strip()
    if text:
        parts.append(text.strip())
    len_parts = len(parts)
    candidate_posts = [
        part + footer_template.format(i + 1, len_parts) for i, part in enumerate(parts)
    ]
    if all(count_chars(post) <= max_chars for post in candidate_posts):
        return candidate_posts
    if fields == 2:
        return break_into_thread(
            input_text,
            max_chars,
            footer_template,
            par_break_dots=par_break_dots,
            _allow_chars_for_total_pages=_allow_chars_for_total_pages + 1,
        )
    msg = "Unexpected error. Failed to break into thread."
    raise ValueError(msg)
