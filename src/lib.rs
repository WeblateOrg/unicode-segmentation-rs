// Copyright © Michal Čihař <michal@weblate.org>
//
// SPDX-License-Identifier: MIT

#[pyo3::pymodule(gil_used = false)]
mod unicode_segmentation_rs {
    use pyo3::prelude::*;
    use unicode_segmentation::UnicodeSegmentation;
    use unicode_width::UnicodeWidthStr;

    // Constants for PO file wrapping behavior
    // These match gettext's behavior for line breaking
    // po_line_break_chars = {"/", "}", ")", ">", "-"}
    const PO_LINE_BREAK_CHARS: &[char] = &['/', '}', ')', '>', '-'];

    // po_mergeable_chars = po_line_break_chars | {" ", "\t"}
    const PO_MERGEABLE_CHARS: &[char] = &['/', '}', ')', '>', '-', ' ', '\t'];

    // po_open_parenthesis_chars = {"{", "("}
    const PO_OPEN_PARENTHESIS_CHARS: &[char] = &['{', '('];

    // po_punctuation = set(punctuation)
    // Python's string.punctuation
    const PO_PUNCTUATION: &[char] = &[
        '!', '"', '#', '$', '%', '&', '\'', '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<',
        '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~',
    ];

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

    /// Wrap text for gettext PO files
    ///
    /// This implementation follows gettext's wrapping behavior:
    /// - Never breaks escape sequences (\\n, \\", etc.)
    /// - Prefers breaking after spaces
    /// - Handles CJK characters with proper width calculation
    /// - Breaks long words only when necessary
    #[pyfunction]
    fn gettext_wrap(text: &str, width: usize) -> PyResult<Vec<String>> {
        if text.is_empty() || width == 0 {
            return if text.is_empty() {
                Ok(vec![])
            } else {
                Ok(vec![text.to_string()])
            };
        }

        // Split text into chunks at word boundaries
        let chunks = split_po_chunks(text);

        // Wrap chunks into lines
        Ok(wrap_po_chunks(&chunks, width))
    }

    /// Split text into chunks using word boundaries with PO-specific rules
    fn split_po_chunks(text: &str) -> Vec<String> {
        let mut chunks: Vec<String> = Vec::new();
        let mut last_char: Option<char> = None;
        let mut second_last_char: Option<char> = None;
        let mut second_fallback: Option<char>;
        let mut last_chunk = String::new();

        for chunk in text.split_word_bounds() {
            let chunk_str = chunk.to_string();
            let should_merge = last_char.is_some()
                && (second_last_char.is_none()
                    || last_char.unwrap() != '\\'
                    || second_last_char.unwrap() != '\\')
                && (is_mergeable(&chunk_str)
                    || (!is_open_parenthesis(&chunk_str.chars().next().unwrap())
                        && !is_line_break(&last_char.unwrap())
                        && (is_punctuation(&last_char.unwrap())
                            || (is_punctuation(&chunk_str.chars().next().unwrap())
                                && !last_char.unwrap().is_whitespace()))));

            if !should_merge {
                if !last_chunk.is_empty() {
                    chunks.push(last_chunk.clone())
                }
                last_chunk.clear();
                second_fallback = None;
            } else {
                second_fallback = Some(last_char.unwrap());
            }
            last_chunk.push_str(chunk);

            // Update last_char and second_last_char
            let chars: Vec<char> = chunk.chars().collect();
            if chars.len() >= 2 {
                let len = chars.len();
                last_char = Some(chars[len - 2]);
                second_last_char = Some(chars[len - 1]);
            } else {
                second_last_char = second_fallback;
                last_char = Some(chars[0]);
            }
        }
        if !last_chunk.is_empty() {
            chunks.push(last_chunk.clone())
        }

        chunks
    }

    /// Wrap chunks into lines respecting the width limit
    fn wrap_po_chunks(chunks: &Vec<String>, width: usize) -> Vec<String> {
        let mut lines = Vec::new();
        let mut current_line = String::new();
        let mut current_width = 0;

        for chunk in chunks {
            let chunk_width: usize = chunk.width();

            if current_width + chunk_width <= width {
                current_line.push_str(chunk.as_str());
                current_width += chunk_width;
            } else {
                if !current_line.is_empty() {
                    lines.push(current_line.clone());
                    current_line.clear();
                    current_width = 0;
                }
                current_line.push_str(chunk.as_str());
                current_width += chunk_width;
            }
        }

        if !current_line.is_empty() {
            lines.push(current_line.clone());
        }

        lines
    }

    /// Check if a string contains only mergeable characters
    fn is_mergeable(s: &str) -> bool {
        s.chars().all(|c| PO_MERGEABLE_CHARS.contains(&c))
    }

    /// Check if a string starts with an open parenthesis character
    fn is_open_parenthesis(c: &char) -> bool {
        PO_OPEN_PARENTHESIS_CHARS.contains(&c)
    }

    /// Check if a string contains line break characters
    fn is_line_break(c: &char) -> bool {
        PO_LINE_BREAK_CHARS.contains(&c)
    }

    /// Check if a string contains punctuation characters
    fn is_punctuation(c: &char) -> bool {
        PO_PUNCTUATION.contains(&c)
    }
}
