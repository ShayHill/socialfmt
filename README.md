# socialfmt

Format text for social media platforms that strip away rich formatting.

X (Twitter), Discord, LinkedIn, and similar platforms accept plain Unicode but not Markdown. `socialfmt` turns Markdown into Unicode-styled text that *looks* formatted (bold, italic, monospace, etc.), counts characters the way those platforms count them, and splits long posts into properly-sized threads.

## Modules

### `socialfmt.format_x`

- `reformat_markdown_for_x(text)` — convert a Markdown string into a single
  X-ready post:

  - Markdown emphasis becomes Unicode-styled glyphs (`*italic*` → 𝑖𝑡𝑎𝑙𝑖𝑐)
  - Blockquotes render in italic
  - Lists get bullet/number prefixes
  - Inline / fenced code is rendered in monospace
  - Symbols are "smartened" - Straight quotes, double hyphens, and `...` are replace with unicode typographic equivalents.
  - Raises `ValueError` when the input contains `||...||` spoiler markup, which X does not support.

### `socialfmt.char_count`

- `count_chars(text)` — return the length of a string the way X / Discord /
  LinkedIn count it (UTF-16 code units, so an emoji or math-italic letter
  counts as 2).
- `split_at_chars(text, max_chars)` — split a string into `(head, rest)` at
  the latest word/punctuation boundary that keeps `head` within `max_chars`.

### `socialfmt.thread_break_text`

- `break_into_thread(text, max_chars, footer_template="\n\n{}/{}", *, par_break_dots=False)` — Split a long string into a list of posts, each at most `max_chars` including the page footer. Breaks preferentially at paragraph, then sentence, then comma, then word boundaries. Returns the original string unchanged if it already fits.
