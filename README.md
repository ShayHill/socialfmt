# socialfmt

Format text for social media platforms that strip away rich formatting.

X (Twitter), Discord, LinkedIn, and similar platforms accept plain Unicode but not Markdown. `socialfmt` turns Markdown into Unicode-styled text that *looks* formatted (bold, italic, monospace, etc.), counts characters the way those platforms count them, and splits long posts into properly-sized threads.

## Modules

### `socialfmt.format_x`

- `reformat_markdown_for_x(text, *, allow_thread=False)` — convert a Markdown
  string into an X-ready post. Returns a string up to 280 UTF-16 code units, or
  raises `ValueError` when it is too long. With `allow_thread=True`, returns a
  list of one or more threaded posts.

  - Markdown emphasis becomes Unicode-styled glyphs (`*italic*` → 𝑖𝑡𝑎𝑙𝑖𝑐)
  - Blockquotes render in italic
  - Lists get bullet prefixes
  - Inline / fenced code is rendered in monospace
  - Symbols outside code are "smartened": straight quotes, double hyphens, and
    `...` are replaced with Unicode typographic equivalents.
  - Raises `ValueError` for `||` spoiler markup outside inline and fenced code.

### `socialfmt.format_linkedin`

- `reformat_markdown_for_linkedin(text, *, allow_thread=False)` — convert a
  Markdown string into a LinkedIn-ready post using the same Unicode formatting
  as X. Returns a string up to 3,000 UTF-16 code units, or raises `ValueError`
  when it is too long. With `allow_thread=True`, returns a list of one or more
  threaded posts.

### `socialfmt.format_linkedin_reply`

- `reformat_markdown_for_linkedin_reply(text, *, allow_thread=False)` — convert
  a Markdown string into a LinkedIn reply. Returns a string up to 1,250 UTF-16
  code units, or raises `ValueError` when it is too long. With
  `allow_thread=True`, returns a list of one or more threaded replies.

### Command Line

- Run a platform module with an input path, for example
  `python -m socialfmt.format_x post.md`. It writes a sibling file with the
  platform suffix (`_x` for X and `_li` for LinkedIn).
- Pass `--allow_thread` to split over-limit content. The sibling file contains
  posts separated by a Markdown horizontal rule (`---`).

### `socialfmt.char_count`

- `count_chars(text)` — return the length of a string the way X / Discord /
  LinkedIn count it (UTF-16 code units, so an emoji or math-italic letter
  counts as 2).
- `split_at_chars(text, max_chars)` — split a string into `(head, rest)` at
  the latest word/punctuation boundary that keeps `head` within `max_chars`.

### `socialfmt.thread_break_text`

- `break_into_thread(text, max_chars, footer_template="\n\n{}/{}", *, par_break_dots=False)` — Split a long string into a list of posts, each at most `max_chars` including the page footer. Breaks preferentially at paragraph, then sentence, then comma, then word boundaries. Returns the original string unchanged if it already fits.
