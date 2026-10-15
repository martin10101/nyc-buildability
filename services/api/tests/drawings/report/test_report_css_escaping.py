"""Hardening (DB-277): ``layout._css_string`` neutralizes a ``</style>`` breakout.

The running identity (header) and footer are written literally into the
``<style>@page{content:"..."}`` block. Before this guard ``_css_string`` escaped
only backslash, quote and newlines, so a header/footer value containing
``</style>`` would close the ``<style>`` element and inject markup. The guard
also neutralizes ``<``/``>`` as the CSS hex escapes ``\\3C ``/``\\3E `` (which
render as ``<``/``>`` in the content string), so every value WITHOUT angle
brackets - every run-identity value: address, "Results revision N", "computed
YYYY-MM-DD" - produces byte-identical CSS.

One test per input state: a breakout value (header and footer), a normal value
(byte-identical no-op), and the existing backslash/quote/newline escapes
preserved. The mutation proof (revert the ``<`` replace -> raw ``</style>``
reappears) is recorded in the producer report.
"""

from __future__ import annotations

import re

from app.drawings.report import layout

# The CSS hex escapes the guard emits for the two angle brackets.
_LT = "\\3C "  # '<'
_GT = "\\3E "  # '>'


def test_breakout_value_cannot_close_the_style_element_header() -> None:
    """A ``</style>`` payload in the HEADER is neutralized: no raw ``</style>``
    (or ``<script>``) survives and the ``<`` renders as the ``\\3C `` hex escape."""
    payload = "</style><script>alert(1)</script>"
    css = layout.report_css(payload, "footer")
    assert "</style>" not in css
    assert "<script>" not in css
    assert "</script>" not in css
    assert _LT in css
    assert _GT in css


def test_breakout_value_cannot_close_the_style_element_footer() -> None:
    """The same guard covers the FOOTER margin box."""
    payload = "</style><script>alert(1)</script>"
    css = layout.report_css("header", payload)
    assert "</style>" not in css
    assert "<script>" not in css


def test_css_string_encodes_each_angle_bracket() -> None:
    """``_css_string`` turns ``</style>`` into its CSS hex-escaped form."""
    assert layout._css_string("</style>") == "\\3C /style\\3E "
    assert layout._css_string("a < b > c") == "a \\3C  b \\3E  c"


def test_normal_run_identity_value_is_byte_identical() -> None:
    """A value with no angle brackets is unchanged - the two new replaces are a
    no-op, so the produced CSS is byte-identical to the pre-guard output."""
    header = "Results revision 3"
    footer = "123 Main St, Brooklyn · computed 2026-10-15"
    # _css_string returns the value verbatim (nothing to escape).
    assert layout._css_string(header) == header
    assert layout._css_string(footer) == footer
    css = layout.report_css(header, footer)
    assert header in css
    assert footer in css
    # No hex escape is emitted for a value that has no angle brackets, and the
    # stylesheet itself carries no literal '<'/'>' to encode.
    assert _LT not in css
    assert _GT not in css


def test_evidence_column_list_item_breaks_a_long_commit() -> None:
    """DB-277/S10: the run-identity column prints the 40-character deployed commit
    as an unbroken token in a ``ul`` inside ``div.evidence-column``. Without a break
    rule it overflows the narrow flex column and Chromium shrinks the whole document
    to fit (8 pages instead of 10). The stylesheet lets a list item break anywhere."""
    css = layout.report_css("H", "F")
    assert re.search(r"\.evidence-column li\s*\{[^}]*overflow-wrap:\s*anywhere", css)


def test_existing_backslash_quote_newline_escapes_preserved() -> None:
    """The guard is additive: backslash, double quote and newline escaping (and
    their ordering - the angle-bracket replaces run AFTER the backslash doubling,
    so the ``\\3C `` backslash is not doubled) still hold."""
    assert layout._css_string("a\\b") == "a\\\\b"
    assert layout._css_string('say "hi"') == 'say \\"hi\\"'
    assert layout._css_string("line1\nline2\r\n") == "line1 line2  "
    # A value mixing a backslash and an angle bracket keeps a single '\3C '.
    assert layout._css_string("\\<") == "\\\\\\3C "
