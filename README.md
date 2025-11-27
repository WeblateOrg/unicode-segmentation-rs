# unicode-segmentation-rs

Python bindings for the Rust [unicode-segmentation](https://docs.rs/unicode-segmentation/) and [unicode-width](https://docs.rs/unicode-width/) crates, providing Unicode text segmentation and width calculation according to Unicode standards.

## Features

- **Grapheme Cluster Segmentation**: Split text into user-perceived characters
- **Word Segmentation**: Split text into words according to Unicode rules
- **Sentence Segmentation**: Split text into sentences
- **Display Width Calculation**: Get the display width of text (for terminal/monospace display)

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
clusters = unicode_segmentation_py.graphemes(text, is_extended=True)
print(clusters)  # ['H', 'e', 'l', 'l', 'o', ' ', '👨‍👩‍👧‍👦', ' ', 'W', 'o', 'r', 'l', 'd']

# Get grapheme clusters with their byte indices
indices = unicode_segmentation_py.grapheme_indices(text, is_extended=True)
print(indices)  # [(0, 'H'), (1, 'e'), ...]

# Word boundaries (includes punctuation and whitespace)
text = "Hello, world!"
words = unicode_segmentation_py.split_word_bounds(text)
print(words)  # ['Hello', ',', ' ', 'world', '!']

# Unicode words (excludes punctuation and whitespace)
words = unicode_segmentation_py.unicode_words(text)
print(words)  # ['Hello', 'world']

# Word indices
indices = unicode_segmentation_py.split_word_bound_indices(text)
print(indices)  # [(0, 'Hello'), (5, ','), ...]

# Sentence segmentation
text = "Hello world. How are you? I'm fine."
sentences = unicode_segmentation_py.unicode_sentences(text)
print(sentences)  # ['Hello world. ', 'How are you? ', "I'm fine."]

# Display width calculation
text = "Hello 世界"
width = unicode_segmentation_py.text_width(text)
print(width)  # 10 (Hello=5, space=1, 世=2, 界=2, but depends on terminal)

# Character width
print(unicode_segmentation_py.text_width('A'))    # Some(1)
print(unicode_segmentation_py.text_width('世'))   # Some(2)
print(unicode_segmentation_py.text_width('\t'))   # None (control character)
```

## Examples

### Grapheme Cluster Segmentation

```python
import unicode_segmentation_rs

# Complex emojis and combining characters
text = "Hello 👨‍👩‍👧‍👦 नमस्ते"
print(f"Text: {text}")
print(f"Graphemes: {unicode_segmentation_py.graphemes(text, is_extended=True)}")
print(f"Length (graphemes): {len(unicode_segmentation_py.graphemes(text, is_extended=True))}")
print(f"Length (chars): {len(text)}")

# With indices
print("Grapheme indices:")
for idx, cluster in unicode_segmentation_py.grapheme_indices(text, is_extended=True):
    print(f"  {idx:3d}: {cluster!r}")
```

### Word Segmentation

```python
text = "Hello, world! How are you?"
print(f"Text: {text}")
print(f"Word bounds: {unicode_segmentation_py.split_word_bounds(text)}")
print(f"Unicode words: {unicode_segmentation_py.unicode_words(text)}")

# With indices
print("Word boundary indices:")
for idx, word in unicode_segmentation_py.split_word_bound_indices(text):
    print(f"  {idx:3d}: {word!r}")
```

### Sentence Segmentation

```python
text = "Hello world. How are you? I'm fine, thanks! What about you?"
print(f"Text: {text}")
sentences = unicode_segmentation_py.unicode_sentences(text)
print("Sentences:")
for i, sentence in enumerate(sentences, 1):
    print(f"  {i}. {sentence!r}")
```

### Multilingual Examples

```python
# Arabic
arabic = "مرحبا بك. كيف حالك؟"
print(f"Arabic: {arabic}")
print(f"Sentences: {unicode_segmentation_py.unicode_sentences(arabic)}")

# Japanese
japanese = "こんにちは。お元気ですか？"
print(f"Japanese: {japanese}")
print(f"Sentences: {unicode_segmentation_py.unicode_sentences(japanese)}")

# Mixed languages
mixed = "Hello世界! This is a test文章."
print(f"Mixed: {mixed}")
print(f"Words: {unicode_segmentation_py.unicode_words(mixed)}")
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
    width = unicode_segmentation_py.text_width(text)
    width_cjk = unicode_segmentation_py.text_width_cjk(text)
    print(f"Text: {text!r:20} Width: {width:2} CJK: {width_cjk:2} Chars: {len(text):2}")

# Character widths
chars = ['a', 'A', '1', ' ', '世', '界', 'あ', '🎉', '\t', '\n']
for c in chars:
    w = unicode_segmentation_py.text_width(c)
    w_cjk = unicode_segmentation_py.text_width_cjk(c)
    w_str = str(w) if w is not None else "None"
    w_cjk_str = str(w_cjk) if w_cjk is not None else "None"
    print(f"  {c!r:6} width: {w_str:4} cjk: {w_cjk_str:4}")
```

## API Reference

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

### `text_width(text: str) -> int`

Get the display width of a string in columns (as it would appear in a terminal). East Asian characters typically take 2 columns.

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

This project follows the same license as the underlying unicode-segmentation crate.
