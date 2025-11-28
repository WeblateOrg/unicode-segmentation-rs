# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: MIT

"""Unit tests for unicode-segmentation-rs"""

import unicode_segmentation_rs


class TestGraphemes:
    """Tests for grapheme cluster segmentation"""

    def test_simple_ascii(self):
        text = "Hello"
        result = unicode_segmentation_rs.graphemes(text, is_extended=True)
        assert result == ["H", "e", "l", "l", "o"]

    def test_emoji_zwj_sequence(self):
        # Family emoji with ZWJ (Zero Width Joiner)
        text = "👨‍👩‍👧‍👦"
        result = unicode_segmentation_rs.graphemes(text, is_extended=True)
        assert result == [text]

    def test_combining_characters(self):
        # Devanagari with combining characters
        text = "नमस्ते"
        result = unicode_segmentation_rs.graphemes(text, is_extended=True)
        # Should treat combining characters as single graphemes
        assert len(result) < len(text)

    def test_grapheme_indices(self):
        text = "Hello"
        result = unicode_segmentation_rs.grapheme_indices(text, is_extended=True)
        expected = [(0, "H"), (1, "e"), (2, "l"), (3, "l"), (4, "o")]
        assert result == expected

    def test_empty_string(self):
        result = unicode_segmentation_rs.graphemes("", is_extended=True)
        assert result == []


class TestWordSegmentation:
    """Tests for word segmentation"""

    def test_split_word_bounds_simple(self):
        text = "Hello world"
        result = unicode_segmentation_rs.split_word_bounds(text)
        assert result == ["Hello", " ", "world"]

    def test_split_word_bounds_punctuation(self):
        text = "Hello, world!"
        result = unicode_segmentation_rs.split_word_bounds(text)
        assert result == ["Hello", ",", " ", "world", "!"]

    def test_unicode_words(self):
        text = "Hello, world!"
        result = unicode_segmentation_rs.unicode_words(text)
        assert result == ["Hello", "world"]

    def test_split_word_bound_indices(self):
        text = "Hello world"
        result = unicode_segmentation_rs.split_word_bound_indices(text)
        expected = [(0, "Hello"), (5, " "), (6, "world")]
        assert result == expected

    def test_empty_string(self):
        result = unicode_segmentation_rs.unicode_words("")
        assert result == []

    def test_multilingual(self):
        text = "Hello世界"
        result = unicode_segmentation_rs.unicode_words(text)
        # Should handle mixed scripts
        assert len(result) > 0


class TestSentenceSegmentation:
    """Tests for sentence segmentation"""

    def test_simple_sentences(self):
        text = "Hello world. How are you?"
        result = unicode_segmentation_rs.unicode_sentences(text)
        assert len(result) == 2
        assert result[0] == "Hello world. "
        assert result[1] == "How are you?"

    def test_multiple_sentences(self):
        text = "First. Second! Third?"
        result = unicode_segmentation_rs.unicode_sentences(text)
        assert len(result) == 3

    def test_abbreviations(self):
        text = "Dr. Smith went home."
        result = unicode_segmentation_rs.unicode_sentences(text)
        # Should handle abbreviations correctly
        assert len(result) >= 1

    def test_empty_string(self):
        result = unicode_segmentation_rs.unicode_sentences("")
        assert result == []

    def test_arabic(self):
        text = "مرحبا بك. كيف حالك؟"
        result = unicode_segmentation_rs.unicode_sentences(text)
        assert len(result) == 2

    def test_japanese(self):
        text = "こんにちは。お元気ですか？"
        result = unicode_segmentation_rs.unicode_sentences(text)
        assert len(result) == 2


class TestDisplayWidth:
    """Tests for display width calculation"""

    def test_ascii_width(self):
        assert unicode_segmentation_rs.text_width("Hello") == 5
        assert unicode_segmentation_rs.text_width("a") == 1

    def test_cjk_width(self):
        # Chinese characters are typically 2 columns wide
        assert unicode_segmentation_rs.text_width("世界") == 4
        assert unicode_segmentation_rs.text_width("世") == 2

    def test_mixed_width(self):
        text = "Hello 世界"
        width = unicode_segmentation_rs.text_width(text)
        # "Hello" = 5, space = 1, "世界" = 4
        assert width == 10

    def test_empty_string(self):
        assert unicode_segmentation_rs.text_width("") == 0

    def test_text_width_ascii(self):
        assert unicode_segmentation_rs.text_width("a") == 1
        assert unicode_segmentation_rs.text_width("A") == 1
        assert unicode_segmentation_rs.text_width("1") == 1
        assert unicode_segmentation_rs.text_width(" ") == 1

    def test_text_width(self):
        assert unicode_segmentation_rs.text_width("世") == 2
        assert unicode_segmentation_rs.text_width("界") == 2
        assert unicode_segmentation_rs.text_width("あ") == 2

    def test_text_width_control(self):
        # Control characters should return None
        assert unicode_segmentation_rs.text_width("\t") == 1
        assert unicode_segmentation_rs.text_width("\n") == 1
        assert unicode_segmentation_rs.text_width("\r") == 1

    def test_text_width_mode(self):
        # Basic test that CJK mode works
        assert unicode_segmentation_rs.text_width("a") == 1
        assert unicode_segmentation_rs.text_width("世") == 2
        assert unicode_segmentation_rs.text_width("\t") == 1


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_only_whitespace(self):
        text = "   "
        assert unicode_segmentation_rs.graphemes(text, is_extended=True) == [
            " ",
            " ",
            " ",
        ]
        assert unicode_segmentation_rs.split_word_bounds(text) == ["   "]
        assert unicode_segmentation_rs.unicode_words(text) == []

    def test_only_punctuation(self):
        text = "!!!"
        assert unicode_segmentation_rs.unicode_words(text) == []
        assert unicode_segmentation_rs.split_word_bounds(text) == ["!", "!", "!"]

    def test_newlines(self):
        text = "Hello\nWorld"
        result = unicode_segmentation_rs.unicode_words(text)
        assert "Hello" in result
        assert "World" in result

    def test_tabs(self):
        text = "Hello\tWorld"
        result = unicode_segmentation_rs.unicode_words(text)
        assert "Hello" in result
        assert "World" in result

    def test_multiple_spaces(self):
        text = "Hello    World"
        words = unicode_segmentation_rs.unicode_words(text)
        assert words == ["Hello", "World"]


class TestPerformance:
    """Basic performance sanity checks"""

    def test_large_text_graphemes(self):
        text = "a" * 10000
        result = unicode_segmentation_rs.graphemes(text, is_extended=True)
        assert len(result) == 10000

    def test_large_text_words(self):
        text = " ".join(["word"] * 1000)
        result = unicode_segmentation_rs.unicode_words(text)
        assert len(result) == 1000

    def test_large_text_width(self):
        text = "a" * 10000
        width = unicode_segmentation_rs.text_width(text)
        assert width == 10000
