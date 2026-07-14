# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: Apache-2.0

"""Test that all code examples in README.md work correctly"""

import unicode_segmentation_rs


class TestReadmeBasicUsage:
    """Tests for basic usage section of README"""

    def test_grapheme_clusters(self):
        """Test grapheme cluster example from README"""
        text = "Hello 👨‍👩‍👧‍👦 World"
        clusters = unicode_segmentation_rs.graphemes(text, is_extended=True)
        # Verify it works
        assert isinstance(clusters, list)
        assert len(clusters) > 0

    def test_grapheme_indices(self):
        """Test grapheme indices example from README"""
        text = "Hello 👨‍👩‍👧‍👦 World"
        indices = unicode_segmentation_rs.grapheme_indices(text, is_extended=True)
        # Verify it works
        assert isinstance(indices, list)
        assert len(indices) > 0
        assert isinstance(indices[0], tuple)

    def test_word_boundaries(self):
        """Test word boundaries example from README"""
        text = "Hello, world!"
        words = unicode_segmentation_rs.split_word_bounds(text)
        assert words == ["Hello", ",", " ", "world", "!"]

    def test_unicode_words(self):
        """Test unicode words example from README"""
        text = "Hello, world!"
        words = unicode_segmentation_rs.unicode_words(text)
        assert words == ["Hello", "world"]

    def test_word_indices(self):
        """Test word indices example from README"""
        text = "Hello, world!"
        indices = unicode_segmentation_rs.split_word_bound_indices(text)
        assert isinstance(indices, list)
        assert len(indices) > 0

    def test_sentence_segmentation(self):
        """Test sentence segmentation example from README"""
        text = "Hello world. How are you? I'm fine."
        sentences = unicode_segmentation_rs.unicode_sentences(text)
        assert isinstance(sentences, list)
        assert len(sentences) == 3

    def test_line_breaks(self):
        """Test line-break examples from README"""
        text = "你好世界"
        breaks = unicode_segmentation_rs.line_breaks(text)
        assert breaks == [(3, False), (6, False), (9, False), (12, True)]
        assert unicode_segmentation_rs.line_break_units(text) == [
            "你",
            "好",
            "世",
            "界",
        ]

    def test_display_width(self):
        """Test display width example from README"""
        text = "Hello 世界"
        width = unicode_segmentation_rs.text_width(text)
        assert width == 10  # Hello=5, space=1, 世=2, 界=2

    def test_character_width(self):
        """Test character width examples from README"""
        assert unicode_segmentation_rs.text_width("A") == 1
        assert unicode_segmentation_rs.text_width("世") == 2
        assert unicode_segmentation_rs.text_width("\t") == 1


class TestReadmeGraphemeExamples:
    """Tests for grapheme cluster segmentation examples section"""

    def test_complex_emojis_combining_chars(self):
        """Test complex emoji and combining characters example"""
        text = "Hello 👨‍👩‍👧‍👦 नमस्ते"
        graphemes = unicode_segmentation_rs.graphemes(text, is_extended=True)
        assert isinstance(graphemes, list)
        assert len(graphemes) > 0
        assert len(graphemes) < len(text)  # Should be fewer graphemes than chars

    def test_grapheme_indices_complex(self):
        """Test grapheme indices with complex text"""
        text = "Hello 👨‍👩‍👧‍👦 नमस्ते"
        indices = unicode_segmentation_rs.grapheme_indices(text, is_extended=True)
        assert isinstance(indices, list)
        for idx, cluster in indices:
            assert isinstance(idx, int)
            assert isinstance(cluster, str)


class TestReadmeWordExamples:
    """Tests for word segmentation examples section"""

    def test_word_bounds_with_punctuation(self):
        """Test word boundaries with punctuation"""
        text = "Hello, world! How are you?"
        bounds = unicode_segmentation_rs.split_word_bounds(text)
        assert isinstance(bounds, list)
        assert len(bounds) > 0

    def test_unicode_words_extraction(self):
        """Test unicode words extraction"""
        text = "Hello, world! How are you?"
        words = unicode_segmentation_rs.unicode_words(text)
        assert isinstance(words, list)
        assert "Hello" in words
        assert "world" in words

    def test_word_boundary_indices(self):
        """Test word boundary indices"""
        text = "Hello, world! How are you?"
        indices = unicode_segmentation_rs.split_word_bound_indices(text)
        assert isinstance(indices, list)
        for idx, word in indices:
            assert isinstance(idx, int)
            assert isinstance(word, str)


class TestReadmeSentenceExamples:
    """Tests for sentence segmentation examples section"""

    def test_sentence_segmentation_multiple(self):
        """Test sentence segmentation with multiple sentences"""
        text = "Hello world. How are you? I'm fine, thanks! What about you?"
        sentences = unicode_segmentation_rs.unicode_sentences(text)
        assert isinstance(sentences, list)
        assert len(sentences) >= 3


class TestReadmeLineBreakExamples:
    """Tests for line-break segmentation examples"""

    def test_legal_break_units(self):
        text = "Hello 世界"
        assert unicode_segmentation_rs.line_break_units(text) == [
            "Hello ",
            "世",
            "界",
        ]

    def test_soft_hyphen_is_preserved(self):
        text = "foo\u00adbar"
        assert unicode_segmentation_rs.line_break_units(text) == [
            "foo\u00ad",
            "bar",
        ]


class TestReadmeMultilingualExamples:
    """Tests for multilingual examples section"""

    def test_arabic_sentences(self):
        """Test Arabic sentence segmentation"""
        arabic = "مرحبا بك. كيف حالك؟"
        sentences = unicode_segmentation_rs.unicode_sentences(arabic)
        assert isinstance(sentences, list)
        assert len(sentences) > 0

    def test_japanese_sentences(self):
        """Test Japanese sentence segmentation"""
        japanese = "こんにちは。お元気ですか？"
        sentences = unicode_segmentation_rs.unicode_sentences(japanese)
        assert isinstance(sentences, list)
        assert len(sentences) > 0

    def test_mixed_language_words(self):
        """Test mixed language word segmentation"""
        mixed = "Hello世界! This is a test文章."
        words = unicode_segmentation_rs.unicode_words(mixed)
        assert isinstance(words, list)
        assert len(words) > 0


class TestReadmeDisplayWidthExamples:
    """Tests for display width calculation examples section"""

    def test_various_text_widths(self):
        """Test width calculation for various texts"""
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
            assert isinstance(width, int)

    def test_character_widths_various(self):
        """Test character width for various characters"""
        chars = ["a", "A", "1", " ", "世", "界", "あ", "🎉", "\t", "\n"]
        for c in chars:
            w = unicode_segmentation_rs.text_width(c)
            assert isinstance(w, int)


class TestReadmeGettextWrapExamples:
    """Tests for gettext PO file wrapping examples section"""

    def test_basic_gettext_wrap(self):
        """Test basic gettext wrapping"""
        text = "This is a long translation string that needs to be wrapped appropriately for a gettext PO file"
        lines = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert isinstance(lines, list)
        assert len(lines) > 0

    def test_gettext_wrap_cjk(self):
        """Test gettext wrapping with CJK characters"""
        text = "This translation contains 中文字符 (Chinese characters) and should wrap correctly"
        lines = unicode_segmentation_rs.gettext_wrap(text, 40)
        assert isinstance(lines, list)
        assert len(lines) > 0
        for line in lines:
            width = unicode_segmentation_rs.text_width(line)
            assert isinstance(width, int)

    def test_gettext_wrap_escape_sequences(self):
        """Test gettext wrapping preserves escape sequences"""
        text = "This has\\nline breaks\\tand tabs"
        lines = unicode_segmentation_rs.gettext_wrap(text, 20)
        assert isinstance(lines, list)
        # Verify escape sequences are preserved
        full_text = "".join(lines)
        assert "\\n" in full_text or "\\t" in full_text
