<a href="https://weblate.org/"><img alt="Weblate" src="https://s.weblate.org/cdn/Logo-Darktext-borders.png" height="80px" /></a>

**Weblate is libre software web-based continuous localization system,
used by over 2500 libre projects and companies in more than 165 countries.**

# unicode-segmentation-rs

Python bindings for the Rust [unicode-segmentation](https://docs.rs/unicode-segmentation/), [unicode-linebreak](https://docs.rs/unicode-linebreak/), and [unicode-width](https://docs.rs/unicode-width/) crates, providing Unicode text segmentation and width calculation according to Unicode standards.

## Features

- **Grapheme Cluster Segmentation**: Split text into user-perceived characters
- **Word Segmentation**: Split text into words according to Unicode rules
- **Sentence Segmentation**: Split text into sentences
- **Line-Break Segmentation**: Find legal wrapping opportunities according to Unicode Standard Annex #14
- **Display Width Calculation**: Get the display width of text (for terminal/monospace display)
- **Gettext PO Wrapping**: Wrap text for gettext PO files with proper handling of escape sequences and CJK characters

## Installation

### From PyPI

```bash
uv pip install unicode-segmentation-rs
```

### From source

```bash
# Install maturin
pip install maturin

# Build and install the package
maturin develop --release
```

## Usage

```python
import unicode_segmentation_rs

# Grapheme clusters (user-perceived characters)
text = "Hello 👨‍👩‍👧‍👦 World"
clusters = unicode_segmentation_rs.graphemes(text, is_extended=True)
print(
    clusters
)  # ['H', 'e', 'l', 'l', 'o', ' ', '👨‍👩‍👧‍👦', ' ', 'W', 'o', 'r', 'l', 'd']

# Get grapheme clusters with their byte indices
indices = unicode_segmentation_rs.grapheme_indices(text, is_extended=True)
print(indices)  # [(0, 'H'), (1, 'e'), ...]

# Word boundaries (includes punctuation and whitespace)
text = "Hello, world!"
words = unicode_segmentation_rs.split_word_bounds(text)
print(words)  # ['Hello', ',', ' ', 'world', '!']

# Unicode words (excludes punctuation and whitespace)
words = unicode_segmentation_rs.unicode_words(text)
print(words)  # ['Hello', 'world']

# Word indices
indices = unicode_segmentation_rs.split_word_bound_indices(text)
print(indices)  # [(0, 'Hello'), (5, ','), ...]

# Sentence segmentation
text = "Hello world. How are you? I'm fine."
sentences = unicode_segmentation_rs.unicode_sentences(text)
print(sentences)  # ['Hello world. ', 'How are you? ', "I'm fine."]

# Line-break opportunities use UTF-8 byte offsets
text = "你好世界"
breaks = unicode_segmentation_rs.line_breaks(text)
print(breaks)  # [(3, False), (6, False), (9, False), (12, True)]
units = unicode_segmentation_rs.line_break_units(text)
print(units)  # ['你', '好', '世', '界']

# Display width calculation
text = "Hello 世界"
width = unicode_segmentation_rs.text_width(text)
print(width)  # 10 (Hello=5, space=1, 世=2, 界=2, but depends on terminal)

# Character width
print(unicode_segmentation_rs.text_width("A"))  # 1
print(unicode_segmentation_rs.text_width("世"))  # 2
print(unicode_segmentation_rs.text_width("\t"))  # 1
```

## Examples

### Grapheme Cluster Segmentation

```python
import unicode_segmentation_rs

# Complex emojis and combining characters
text = "Hello 👨‍👩‍👧‍👦 नमस्ते"
print(f"Text: {text}")
print(f"Graphemes: {unicode_segmentation_rs.graphemes(text, is_extended=True)}")
print(
    f"Length (graphemes): {len(unicode_segmentation_rs.graphemes(text, is_extended=True))}"
)
print(f"Length (chars): {len(text)}")

# With indices
print("Grapheme indices:")
for idx, cluster in unicode_segmentation_rs.grapheme_indices(text, is_extended=True):
    print(f"  {idx:3d}: {cluster!r}")
```

### Word Segmentation

```python
text = "Hello, world! How are you?"
print(f"Text: {text}")
print(f"Word bounds: {unicode_segmentation_rs.split_word_bounds(text)}")
print(f"Unicode words: {unicode_segmentation_rs.unicode_words(text)}")

# With indices
print("Word boundary indices:")
for idx, word in unicode_segmentation_rs.split_word_bound_indices(text):
    print(f"  {idx:3d}: {word!r}")
```

### Sentence Segmentation

```python
text = "Hello world. How are you? I'm fine, thanks! What about you?"
print(f"Text: {text}")
sentences = unicode_segmentation_rs.unicode_sentences(text)
print("Sentences:")
for i, sentence in enumerate(sentences, 1):
    print(f"  {i}. {sentence!r}")
```

### Line-Break Segmentation

```python
# Find legal wrapping opportunities without measuring or reformatting text
text = "Hello 世界"
print(unicode_segmentation_rs.line_breaks(text))
print(unicode_segmentation_rs.line_break_units(text))  # ['Hello ', '世', '界']

# A soft hyphen is preserved in the unit before its discretionary break
text = "foo\u00adbar"
print(unicode_segmentation_rs.line_break_units(text))  # ['foo\u00ad', 'bar']
```

Line-break segmentation reports opportunities only. The caller remains responsible for measuring widths, trimming whitespace for display, and rendering a visible hyphen when selecting a soft-hyphen break.

The underlying `unicode-linebreak` crate treats complex-context (`SA`) characters as ordinary alphabetic characters rather than performing dictionary-based segmentation. Consequently, scripts such as Thai, Lao, and Khmer do not receive language-specific word break opportunities.

### Multilingual Examples

```python
# Arabic
arabic = "مرحبا بك. كيف حالك؟"
print(f"Arabic: {arabic}")
print(f"Sentences: {unicode_segmentation_rs.unicode_sentences(arabic)}")

# Japanese
japanese = "こんにちは。お元気ですか？"
print(f"Japanese: {japanese}")
print(f"Sentences: {unicode_segmentation_rs.unicode_sentences(japanese)}")

# Mixed languages
mixed = "Hello世界! This is a test文章."
print(f"Mixed: {mixed}")
print(f"Words: {unicode_segmentation_rs.unicode_words(mixed)}")
```

### Display Width Calculation

```python
examples = [
    "Hello",
    "世界",
    "Hello 世界",
    "こんにちは",
    "🎉🎊",
    "Tab\there",
]

for text in examples:
    width = unicode_segmentation_rs.text_width(text)
    print(f"Text: {text!r:20} Width: {width:2} Chars: {len(text):2}")

# Character widths
chars = ["a", "A", "1", " ", "世", "界", "あ", "🎉", "\t", "\n"]
for c in chars:
    w = unicode_segmentation_rs.text_width(c)
    print(f"  {c!r:6} width: {w:2}")
```

### Gettext PO File Wrapping

```python
# Wrap text for PO files (default width is 77 characters)
text = "This is a long translation string that needs to be wrapped appropriately for a gettext PO file"
lines = unicode_segmentation_rs.gettext_wrap(text, 77)
for i, line in enumerate(lines, 1):
    print(f"Line {i}: {line}")

# Wrapping with CJK characters
text = (
    "This translation contains 中文字符 (Chinese characters) and should wrap correctly"
)
lines = unicode_segmentation_rs.gettext_wrap(text, 40)
for line in lines:
    width = unicode_segmentation_rs.text_width(line)
    print(f"[{width:2d} cols] {line}")

# Escape sequences are preserved
text = "This has\\nline breaks\\tand tabs"
lines = unicode_segmentation_rs.gettext_wrap(text, 20)
print(lines)
```

## API Reference

Functions returning lists materialize the complete result. Applications processing very large or
untrusted text should enforce an input-size limit appropriate for their environment.

### `graphemes(text: str, is_extended: bool) -> list[str]`

Split a string into grapheme clusters. Set `is_extended=True` for extended grapheme clusters (recommended).

### `grapheme_indices(text: str, is_extended: bool) -> list[tuple[int, str]]`

Split a string into grapheme clusters with their byte indices.

### `split_word_bounds(text: str) -> list[str]`

Split a string at word boundaries (includes punctuation and whitespace).

### `split_word_bound_indices(text: str) -> list[tuple[int, str]]`

Split a string at word boundaries with byte indices.

### `unicode_words(text: str) -> list[str]`

Get Unicode words from a string (excludes punctuation and whitespace).

### `unicode_sentences(text: str) -> list[str]`

Split a string into sentences according to Unicode rules.

### `line_breaks(text: str) -> list[tuple[int, bool]]`

Return every allowed or mandatory Unicode line-break opportunity as `(utf8_byte_offset, mandatory)`. The boolean is `True` only for mandatory breaks. Non-empty input includes the mandatory end-of-text opportunity.

### `line_break_units(text: str) -> list[str]`

Split a string at every allowed or mandatory Unicode line-break opportunity. Every input code point is preserved exactly, and the mandatory end-of-text opportunity does not add an empty unit.

### `text_width(text: str) -> int`

Get the display width of a string in columns (as it would appear in a terminal). East Asian characters typically take 2 columns.

### `gettext_wrap(text: str, width: int) -> list[str]`

Wrap text for gettext PO files. This function follows gettext's wrapping behavior:

- Never breaks escape sequences (`\n`, `\"`, etc.)
- Prefers breaking after spaces
- Handles CJK characters with proper width calculation
- Breaks long words only when necessary

## Building for Distribution

```bash
# Build wheel
maturin build --release

# Build and publish to PyPI
maturin publish
```

## Running Tests

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest tests/
```

## License

This project is licensed under the Apache License 2.0.
