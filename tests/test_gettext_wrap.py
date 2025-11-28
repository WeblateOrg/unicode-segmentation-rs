# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: MIT

"""Unit tests for gettext wrapping"""

import unicode_segmentation_rs


class TestGettextWrap:
    """Tests for gettext PO file wrapping"""

    def test_simple_wrap(self):
        text = "This is a simple test string"
        result = unicode_segmentation_rs.gettext_wrap(text, 20)
        assert result == ["This is a simple ", "test string"]

    def test_wrap_with_cjk(self):
        text = "Hello 世界 this is a test"
        result = unicode_segmentation_rs.gettext_wrap(text, 10)
        assert result == ["Hello 世", "界 this ", "is a ", "test"]

    def test_wrap_short_text(self):
        text = "Short"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == ["Short"]

    def test_wrap_empty_string(self):
        result = unicode_segmentation_rs.gettext_wrap("", 77)
        assert result == []

    def test_wrap_zero_width(self):
        text = "Test"
        result = unicode_segmentation_rs.gettext_wrap(text, 0)
        assert result == ["Test"]

    def test_wrap_with_punctuation(self):
        text = "Hello, world! How are you?"
        result = unicode_segmentation_rs.gettext_wrap(text, 15)
        assert result == ["Hello, world! ", "How are you?"]

    def test_wrap_with_escape_sequences(self):
        # Escape sequences should not be broken
        text = "This has \\n escape sequences \\t in it"
        result = unicode_segmentation_rs.gettext_wrap(text, 11)
        assert result == ["This has ", "\\n escape ", "sequences ", "\\t in it"]

    def test_wrap_long_word(self):
        # Long words that don't fit should still be included
        text = "Supercalifragilisticexpialidocious"
        result = unicode_segmentation_rs.gettext_wrap(text, 20)
        assert result == [text]

    def test_wrap_default_width(self):
        # Test with typical PO file width (77 characters)
        text = "This is a longer sentence that should wrap appropriately at the standard gettext width of seventy-seven characters"
        result = unicode_segmentation_rs.gettext_wrap(text, 77)
        assert result == [
            "This is a longer sentence that should wrap appropriately at the standard ",
            "gettext width of seventy-seven characters",
        ]
