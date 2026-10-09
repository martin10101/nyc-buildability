"""One canonical claim-class word list and one separator-collapsing screen shared
by every CAD/3D writer (task M5-T102, D-087 PKT-A; DB-059 (b), (c); DB-053 (c)).

D-083 (R001/R002) bars affirmative regulatory/approval claims from every product
surface: a proposed drawing, blueprint sheet, or 3D mesh must NEVER be labelled
``permitted``, ``approved``, ``maximum allowed building``, ``as of right`` and the
like. Before this module the three writers each carried their own copy of the word
list and their own matcher: the PDF writer collapsed separator runs (so
``As_of_right`` / ``MAXIMUM  ALLOWED`` were caught) while the DXF and GLB writers
did a raw upper-case substring match that those separator variants slipped past
(DB-059 (b)), and the GLB copy of the list had drifted with no guard (DB-059 (c)).

This module is the single source of truth:

* :data:`CLAIM_CLASS_WORDS` is the ONLY literal word list. Each writer imports it;
  ``dxf_writer.CLAIM_CLASS_WORDS`` is kept as an identity-equal compatibility alias
  (it is imported by ``pdf_sheet_writer`` and by tests).
* :func:`claim_key` is the ONLY matching key: it upper-cases and collapses every
  run of non-alphanumeric characters to a single space, so all separator variants
  normalise to the same canonical form.
* :func:`contains_claim_word` is the ONE screen every writer calls. Callers that
  print an ASCII-sanitised form (the PDF sheet writer) pass BOTH the raw and the
  printed form, so a word hidden behind a non-ASCII separator that prints as ``?``
  is still caught.

The word list's CONTENT is unchanged from the accepted writers; this packet only
moves where it lives and how each writer matches it. Deterministic, stdlib only,
no I/O, no network; nothing here draws a legal conclusion.
"""

from __future__ import annotations

import re

__all__ = [
    "CLAIM_CLASS_WORDS",
    "claim_key",
    "contains_claim_word",
]

#: Claim-class words barred from ANY caller-supplied name or title-block string
#: and from a writer's own emitted strings (D-083 R001/R002). Deliberately EXCLUDES
#: honest negations such as "NOT A CITY RECORD" - only affirmative legal/approval
#: claims are barred. This is the single canonical list; the writers alias it.
CLAIM_CLASS_WORDS: tuple[str, ...] = (
    "PERMITTED",
    "APPROVED",
    "CERTIFIED",
    "COMPLIANT",
    "LAWFUL",
    "LEGAL",
    "ENTITLEMENT",
    "GUARANTEED",
    "MAXIMUM ALLOWED",
    "AS OF RIGHT",
    "AS-OF-RIGHT",
)

#: Every run of non-alphanumeric characters (spaces, underscores, hyphens, dots,
#: tabs, the ``?`` an ASCII-sanitiser emits for a non-ASCII byte, ...) collapses to
#: ONE space after upper-casing, so ``As_of_right`` / ``MAXIMUM  ALLOWED`` /
#: ``as-of-right`` all match the same canonical word.
_SEPARATOR_RUN = re.compile(r"[^A-Z0-9]+")


def claim_key(text: str) -> str:
    """Return the separator-insensitive, upper-cased matching key for ``text``.

    Upper-cases, then collapses every run of non-alphanumeric characters to a
    single space. This is the ONLY normalisation the writers use; keeping it here
    means no writer keeps its own matcher (AS-1).
    """
    return _SEPARATOR_RUN.sub(" ", text.upper())


def contains_claim_word(*texts: str) -> str | None:
    """Return the first canonical claim word found in any of ``texts``, else None.

    Matching is separator-insensitive and case-insensitive: both the text and the
    canonical word are reduced with :func:`claim_key` before a substring test, so
    ``As_of_right`` matches ``AS OF RIGHT`` and ``AS-OF-RIGHT`` alike. Words are
    tested in :data:`CLAIM_CLASS_WORDS` order, so the returned word is stable.

    Pass every form a value can take on the page in one call (the PDF sheet writer
    passes the raw value AND its ASCII-sanitised printed form); a match in ANY of
    them is a refusal.
    """
    keys = [claim_key(text) for text in texts]
    for word in CLAIM_CLASS_WORDS:
        barred = claim_key(word)
        if any(barred in key for key in keys):
            return word
    return None
