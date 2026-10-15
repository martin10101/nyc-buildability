"""Page-1 rear-yard title strip uses a WORD BOUNDARY (DB-263 A3; S6).

The page-1 'What is still uncertain' rear-yard line reads the engine's OWN combined
row text. When that text begins with the row title ('Rear yard'), the title is
stripped so the line does not read 'Rear yard Rear yard'. The strip now fires ONLY at
a word boundary - the character after the title is ':' , whitespace, or the end of the
text - so a title that is a bare PREFIX of a longer word is never mis-stripped.

This is DB-263's own page-1 home. The benchmark 1.5.0 'Rear yard Rear yard'-absent
behaviour (S7) stays asserted in test_report_page_one.py (M5-T170's file, a read-only
consumer this task does not edit).
"""

from __future__ import annotations

import re

from app.drawings.report.page_decision_summary import _uncertainty_line


def _line_html(title: str, text: str) -> str:
    """Render the page-1 rear-yard uncertainty line from a CONSTRUCTED combined row
    (its own text), exactly as the real engine's combined row reaches the line."""
    row = {"number": "1", "title": title, "category": "rear_yard",
           "status_label": "Open check"}
    results = {"rear_yard": {"combined": {"text": text, "way": "conditional",
                                          "zr_sections": ["ZR 23-344"]}}}
    return str(_uncertainty_line(row, results))


def _combined_body(html: str) -> str:
    """The text printed in the combined-row span (the first bare ``<span>`` - the
    label chip carries a class, so ``<span>`` with no attributes is the body span)."""
    match = re.search(r"<span>(.*?)</span>", html, re.S)
    assert match is not None, f"no body span in {html!r}"
    return match.group(1)


def test_s6_title_followed_by_a_space_is_stripped() -> None:
    # The existing 'Rear yard Rear yard ...' outcome (S16): the char after 'Rear yard'
    # is a space -> boundary -> the leading title is still stripped.
    html = _line_html("Rear yard", "Rear yard Rear yard is conditional under ZR 23-344(b).")
    assert _combined_body(html) == "Rear yard is conditional under ZR 23-344(b)."


def test_s6_title_followed_by_a_colon_is_stripped() -> None:
    html = _line_html("Rear yard", "Rear yard: conditional under ZR 23-344(b).")
    assert _combined_body(html) == "conditional under ZR 23-344(b)."


def test_s6_title_equal_to_the_whole_text_is_stripped_to_empty() -> None:
    html = _line_html("Rear yard", "Rear yard")
    assert _combined_body(html) == ""


def test_s6_title_as_a_bare_prefix_of_a_longer_word_is_not_stripped() -> None:
    # 'Rear yard' is a bare prefix of 'Rear yardage'; the char after the title is 'a'
    # (not a boundary), so the title is NOT stripped. Mutation: revert to plain
    # startswith -> the body is mis-stripped to 'age rules ...' and this test fails.
    text = "Rear yardage rules are conditional under ZR 23-344(b)."
    html = _line_html("Rear yard", text)
    assert _combined_body(html) == text


def test_s6_text_that_does_not_begin_with_the_title_is_untouched() -> None:
    text = "A conditional rear-yard reading applies under ZR 23-344(b)."
    html = _line_html("Rear yard", text)
    assert _combined_body(html) == text
