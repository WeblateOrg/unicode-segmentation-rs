// Copyright © Michal Čihař <michal@weblate.org>
//
// SPDX-License-Identifier: Apache-2.0

#[pyo3::pymodule(gil_used = false)]
mod unicode_segmentation_rs {
    use pyo3::prelude::*;
    use pyo3::types::PyList;
    use unicode_linebreak::{BreakOpportunity, linebreaks as unicode_linebreaks};
    use unicode_segmentation::{UWordBoundIndices, UnicodeSegmentation};
    use unicode_width::UnicodeWidthStr;

    /// Split a string into grapheme clusters.
    #[pyfunction]
    fn graphemes<'py>(
        py: Python<'py>,
        text: &str,
        is_extended: bool,
    ) -> PyResult<Bound<'py, PyList>> {
        PyList::new(py, text.graphemes(is_extended))
    }

    /// Split a string into grapheme cluster indices
    #[pyfunction]
    fn grapheme_indices<'py>(
        py: Python<'py>,
        text: &str,
        is_extended: bool,
    ) -> PyResult<Bound<'py, PyList>> {
        PyList::new(py, text.grapheme_indices(is_extended))
    }

    /// Split a string at word boundaries (includes punctuation and whitespace).
    #[pyfunction]
    fn split_word_bounds<'py>(py: Python<'py>, text: &str) -> PyResult<Bound<'py, PyList>> {
        PyList::new(py, text.split_word_bounds())
    }

    /// Split a string at word boundaries with indices.
    #[pyfunction]
    fn split_word_bound_indices<'py>(py: Python<'py>, text: &str) -> PyResult<Bound<'py, PyList>> {
        PyList::new(py, text.split_word_bound_indices())
    }

    /// Get Unicode words from a string (excludes punctuation and whitespace).
    #[pyfunction]
    fn unicode_words<'py>(py: Python<'py>, text: &str) -> PyResult<Bound<'py, PyList>> {
        PyList::new(py, text.unicode_words())
    }

    /// Split a string at word boundaries (includes punctuation and whitespace).
    #[pyfunction]
    fn unicode_sentences<'py>(py: Python<'py>, text: &str) -> PyResult<Bound<'py, PyList>> {
        let mut sentences = text.unicode_sentences();
        PyList::new(py, std::iter::from_fn(move || sentences.next()))
    }

    /// Get Unicode line-break opportunities as UTF-8 byte offsets.
    #[pyfunction]
    fn line_breaks<'py>(py: Python<'py>, text: &str) -> PyResult<Bound<'py, PyList>> {
        if text.is_empty() {
            return Ok(PyList::empty(py));
        }

        PyList::new(
            py,
            unicode_linebreaks(text)
                .map(|(offset, opportunity)| (offset, opportunity == BreakOpportunity::Mandatory)),
        )
    }

    /// Split a string at every Unicode line-break opportunity.
    #[pyfunction]
    fn line_break_units<'py>(py: Python<'py>, text: &str) -> PyResult<Bound<'py, PyList>> {
        let mut previous_offset = 0;

        PyList::new(
            py,
            unicode_linebreaks(text).filter_map(|(offset, _)| {
                if offset == previous_offset {
                    None
                } else {
                    let unit = &text[previous_offset..offset];
                    previous_offset = offset;
                    Some(unit)
                }
            }),
        )
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
    fn gettext_wrap<'py>(
        py: Python<'py>,
        text: &str,
        width: usize,
    ) -> PyResult<Bound<'py, PyList>> {
        if text.is_empty() || width == 0 {
            return if text.is_empty() {
                Ok(PyList::empty(py))
            } else {
                PyList::new(py, [text])
            };
        }

        PyList::new(py, wrap_po_chunks(PoChunks::new(text), width))
    }

    /// Iterator over borrowed chunks split using word boundaries and PO-specific rules.
    struct PoChunks<'a> {
        text: &'a str,
        word_bounds: UWordBoundIndices<'a>,
        chunk_start: Option<usize>,
        last_char: Option<char>,
        second_last_char: Option<char>,
    }

    impl<'a> PoChunks<'a> {
        fn new(text: &'a str) -> Self {
            Self {
                text,
                word_bounds: text.split_word_bound_indices(),
                chunk_start: None,
                last_char: None,
                second_last_char: None,
            }
        }

        /// Add a word-boundary segment and return the completed chunk's byte range, if any.
        fn add_segment(
            &mut self,
            segment_start: usize,
            segment: &str,
        ) -> Option<std::ops::Range<usize>> {
            let first_char = segment.chars().next().unwrap();
            let should_merge = self.last_char.is_some_and(|last_char| {
                (self.second_last_char.is_none()
                    || !matches!(last_char, '\\' | 'n')
                    || self.second_last_char != Some('\\'))
                    && (is_mergeable(segment)
                        || (!is_open_parenthesis(&first_char)
                            && !is_line_break(&last_char)
                            && (is_punctuation(&last_char)
                                || (is_punctuation(&first_char) && !last_char.is_whitespace()))))
            });

            let completed = if should_merge {
                if self.chunk_start.is_none() {
                    self.chunk_start = Some(segment_start);
                }
                None
            } else {
                self.chunk_start
                    .replace(segment_start)
                    .map(|start| start..segment_start)
            };

            let second_fallback = if should_merge { self.last_char } else { None };
            let mut chars = segment.chars().rev();
            let final_char = chars.next().unwrap();
            if let Some(penultimate_char) = chars.next() {
                self.last_char = Some(penultimate_char);
                self.second_last_char = Some(final_char);
            } else {
                self.last_char = Some(final_char);
                self.second_last_char = second_fallback;
            }

            completed
        }
    }

    impl<'a> Iterator for PoChunks<'a> {
        type Item = &'a str;

        fn next(&mut self) -> Option<Self::Item> {
            while let Some((segment_start, segment)) = self.word_bounds.next() {
                // Keep an escape sequence in the chunk before it, then emit that chunk.
                if self.last_char == Some('\\') && segment.len() > 1 {
                    let first_char_len = segment.chars().next().unwrap().len_utf8();
                    let segment_end = segment_start + first_char_len;
                    let completed_start = self.chunk_start.take().unwrap_or(segment_start);
                    let remainder = &segment[first_char_len..];

                    if !remainder.is_empty() {
                        let pending = self.add_segment(segment_end, remainder);
                        debug_assert!(
                            pending.is_none(),
                            "an emitted escape sequence should leave no pending chunk"
                        );
                    }

                    return Some(&self.text[completed_start..segment_end]);
                }

                if let Some(completed) = self.add_segment(segment_start, segment) {
                    return Some(&self.text[completed]);
                }
            }

            self.chunk_start
                .take()
                .map(|start| &self.text[start..self.text.len()])
        }
    }

    /// Iterator that wraps borrowed chunks into owned lines respecting the width limit.
    struct WrappedLines<'a, I>
    where
        I: Iterator<Item = &'a str>,
    {
        chunks: I,
        width: usize,
        current_line: String,
        current_width: usize,
        emit_current: bool,
    }

    impl<'a, I> Iterator for WrappedLines<'a, I>
    where
        I: Iterator<Item = &'a str>,
    {
        type Item = String;

        fn next(&mut self) -> Option<Self::Item> {
            if self.emit_current {
                self.emit_current = false;
                self.current_width = 0;
                return Some(std::mem::take(&mut self.current_line));
            }

            for chunk in self.chunks.by_ref() {
                let chunk_width = chunk.width();

                if self.current_width + chunk_width > self.width && !self.current_line.is_empty() {
                    let completed = std::mem::take(&mut self.current_line);
                    self.current_line.push_str(chunk);
                    self.current_width = chunk_width;
                    self.emit_current = chunk.ends_with("\\n");
                    return Some(completed);
                }

                self.current_line.push_str(chunk);
                self.current_width += chunk_width;

                // Force break on \n
                if chunk.ends_with("\\n") {
                    self.current_width = 0;
                    return Some(std::mem::take(&mut self.current_line));
                }
            }

            self.current_width = 0;
            (!self.current_line.is_empty()).then(|| std::mem::take(&mut self.current_line))
        }
    }

    fn wrap_po_chunks<'a, C>(chunks: C, width: usize) -> WrappedLines<'a, C::IntoIter>
    where
        C: IntoIterator<Item = &'a str>,
    {
        WrappedLines {
            chunks: chunks.into_iter(),
            width,
            current_line: String::new(),
            current_width: 0,
            emit_current: false,
        }
    }

    /// Check if a string contains only mergeable characters
    #[inline]
    fn is_mergeable(s: &str) -> bool {
        s.len() == 1
            && matches!(
                &s.chars().next().unwrap(),
                '/' | '}' | ')' | '>' | '-' | ' ' | '\t'
            )
    }

    /// Check if a string starts with an open parenthesis character
    #[inline]
    fn is_open_parenthesis(c: &char) -> bool {
        matches!(c, '{' | '(')
    }

    /// Check if a string should trigger line break
    #[inline]
    fn is_line_break(c: &char) -> bool {
        matches!(c, '/' | '}' | ')' | '>' | '-')
    }

    /// Check if a string contains punctuation characters
    #[inline]
    fn is_punctuation(c: &char) -> bool {
        matches!(
            c,
            '!' | '"'
                | '#'
                | '$'
                | '%'
                | '&'
                | '\''
                | '('
                | ')'
                | '*'
                | '+'
                | ','
                | '-'
                | '.'
                | '/'
                | ':'
                | ';'
                | '<'
                | '='
                | '>'
                | '?'
                | '@'
                | '['
                | '\\'
                | ']'
                | '^'
                | '_'
                | '`'
                | '{'
                | '|'
                | '}'
                | '~'
        )
    }

    #[cfg(test)]
    mod tests {
        use std::cell::Cell;

        use super::wrap_po_chunks;

        #[test]
        fn wrapped_lines_are_produced_incrementally() {
            let consumed = Cell::new(0);
            let chunks = ["first ", "second ", "third ", "fourth"]
                .into_iter()
                .inspect(|_| consumed.set(consumed.get() + 1));
            let mut lines = wrap_po_chunks(chunks, 7);

            assert_eq!(lines.next().as_deref(), Some("first "));
            assert_eq!(consumed.get(), 2);
            assert_eq!(lines.collect::<Vec<_>>(), ["second ", "third ", "fourth"]);
            assert_eq!(consumed.get(), 4);
        }

        #[test]
        fn wrapped_lines_preserve_edge_cases() {
            assert_eq!(
                wrap_po_chunks(["first ", "\\n", "last"], 6).collect::<Vec<_>>(),
                ["first ", "\\n", "last"]
            );
            assert!(
                wrap_po_chunks(std::iter::empty(), 10)
                    .collect::<Vec<_>>()
                    .is_empty()
            );
            assert_eq!(
                wrap_po_chunks(["unwrapped"], 0).collect::<Vec<_>>(),
                ["unwrapped"]
            );
        }
    }
}
