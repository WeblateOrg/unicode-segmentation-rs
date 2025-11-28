// Copyright © Michal Čihař <michal@weblate.org>
//
// SPDX-License-Identifier: MIT

#[pyo3::pymodule(gil_used = false)]
mod unicode_segmentation_rs {
    use pyo3::prelude::*;
    use unicode_segmentation::UnicodeSegmentation;
    use unicode_width::UnicodeWidthStr;

    /// Split a string into grapheme clusters.
    #[pyfunction]
    fn graphemes(text: &str, is_extended: bool) -> PyResult<Vec<String>> {
        Ok(text.graphemes(is_extended).map(|s| s.to_string()).collect())
    }

    /// Split a string into grapheme cluster indices
    #[pyfunction]
    fn grapheme_indices(text: &str, is_extended: bool) -> PyResult<Vec<(usize, String)>> {
        Ok(text
            .grapheme_indices(is_extended)
            .map(|(i, s)| (i, s.to_string()))
            .collect())
    }

    /// Split a string at word boundaries (includes punctuation and whitespace).
    #[pyfunction]
    fn split_word_bounds(text: &str) -> PyResult<Vec<String>> {
        Ok(text.split_word_bounds().map(|s| s.to_string()).collect())
    }

    /// Split a string at word boundaries with indices.
    #[pyfunction]
    fn split_word_bound_indices(text: &str) -> PyResult<Vec<(usize, String)>> {
        Ok(text
            .split_word_bound_indices()
            .map(|(i, s)| (i, s.to_string()))
            .collect())
    }

    /// Get Unicode words from a string (excludes punctuation and whitespace).
    #[pyfunction]
    fn unicode_words(text: &str) -> PyResult<Vec<String>> {
        Ok(text.unicode_words().map(|s| s.to_string()).collect())
    }

    /// Split a string at word boundaries (includes punctuation and whitespace).
    #[pyfunction]
    fn unicode_sentences(text: &str) -> PyResult<Vec<String>> {
        Ok(text.unicode_sentences().map(|s| s.to_string()).collect())
    }

    /// Get the display width of a string (as it would appear in a terminal)
    #[pyfunction]
    fn text_width(text: &str) -> PyResult<usize> {
        Ok(UnicodeWidthStr::width(text))
    }
}
