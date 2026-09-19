"""ZR 12-10 named-street override matcher — compatibility facade (M5-T049; DB-030f).

The implementation was split for cohesion (DB-030f cohesion ruling) into two
focused modules, with this file preserved as the original public import surface:

* :mod:`app.rules.named_street_override_table` — the typed override-table DATA
  model (:class:`MatchStatus`, the query / provenance / result dataclasses, the
  internal :class:`_Row` record, :data:`SNAPSHOT_ID`, :data:`BOUNDARY_OPEN_QUESTION`,
  and :class:`NamedStreetOverrideError`) AND the pure normalization / source-anchoring
  helpers (:func:`_collapse`, :func:`_normalize_cd`, :func:`_normalize_district`,
  :func:`_word_bounded`, :func:`_anchored_in`, :func:`_bounded_repr`) that produce and
  compare the model's normalized values.
* :mod:`app.rules.named_street_override_matching` — the stateful
  :class:`NamedStreetOverrideMatcher` segment engine and the default-snapshot
  loader :func:`load_default_matcher`.

The two modules form a one-directional import chain (matching -> table). This
facade re-exports every name the original module exposed — the public matcher API
AND the internal helpers consumers already import (``_normalize_cd`` is used by
:mod:`app.rules.named_street_override_status`) — so every existing consumer and the
M5-T039/T040 acceptance suite import byte-identically. PURE extraction — zero
behavior change; the moved code is unchanged and the unchanged suites are the
byte-identity proof.

The full source-boundary rationale (snapshot-pinned matching, fail-closed
tri-state, the DB-023a metadata-bypass closure and complete-span binding, and the
C5-3/C6-4/C6-6 alternate-width refusal) is documented on the two implementation
modules and their methods. This is not legal advice. Everything here is DRAFT
pending qualified-human (G6) approval (D-045-R009).
"""

from __future__ import annotations

from app.rules.named_street_override_matching import (
    NamedStreetOverrideMatcher,
    load_default_matcher,
)
from app.rules.named_street_override_table import (
    BOUNDARY_OPEN_QUESTION,
    SNAPSHOT_ID,
    AlternateWidthResult,
    MatchResult,
    MatchStatus,
    NamedStreetOverrideError,
    OverrideProvenance,
    OverrideQuery,
    _anchored_in,
    _bounded_repr,
    _collapse,
    _normalize_cd,
    _normalize_district,
    _Row,
    _word_bounded,
)

# Every re-exported name is listed in __all__ so the compatibility surface is
# explicit and F401-clean. This preserves the ORIGINAL public import surface AND
# the internal helpers existing consumers already import through this module
# (``_normalize_cd`` is imported by app.rules.named_street_override_status; the
# other helpers/_Row are kept for the same import-path compatibility).
__all__ = [
    "BOUNDARY_OPEN_QUESTION",
    "SNAPSHOT_ID",
    "AlternateWidthResult",
    "MatchResult",
    "MatchStatus",
    "NamedStreetOverrideError",
    "NamedStreetOverrideMatcher",
    "OverrideProvenance",
    "OverrideQuery",
    "load_default_matcher",
    "_Row",
    "_anchored_in",
    "_bounded_repr",
    "_collapse",
    "_normalize_cd",
    "_normalize_district",
    "_word_bounded",
]
