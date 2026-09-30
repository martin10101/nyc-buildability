"""Pure classifier for the DCM Street Center Line free-text ``Streetwidth``
field (task M4-T015, D-045-R003 B2; pinned research
``project-control/reports/M4-T013-street-width-research.md`` sections 4/E7).

THE CENTRAL RULE (the packet's own words, never loosened): a segment
classifies ``wide`` ONLY where the raw text MATHEMATICALLY ENTAILS a width
of 75 ft or more (ZR 12-10: "A wide street is a street that is 75 feet or
more in width"):

- a clean numeral or decimal value >= 75;
- a hyphenated range whose BOTH endpoints are >= 75;
- a one-sided inequality (``>N`` / ``>=N``) whose bound N is >= 75 (the true
  width is at least as large as N, so it is at least 75 too).

Every other observed shape in the free-text domain - cutoff-straddling
ranges, one-sided inequalities below 75, approximations/hedges/prose, the
labelled non-answers ("Width Irregular", "varies", "n/a", "Unknown",
"Unknown but <75", "Unknown but >75", "Regular but unknown."), and anything
unrecognized or empty - fails closed to :data:`DISPOSITION_NARROW_FAIL_CLOSED`.
A confidently-narrow value (a clean number below 75, a range or inequality
whose entire possible range sits below 75) ALSO disposes narrow, but is
marked ``review_required=False`` because there is no genuine ambiguity to
review; every other narrow disposition carries ``review_required=True`` so a
human/legal reviewer can see exactly which raw values were conservatively
assumed narrow without certainty.

OQ-3 (the research's open question: the ZR-grounded fail-closed policy for
each ambiguity class) stays OPEN. This module never resolves it - it only
types the class and fails closed. In particular "Unknown but <75" and
"Unknown but >75" are BOTH treated as ambiguous (never granted wide, and
never trusted as confidently narrow either) because the hedge itself is
prose, not a mathematical entailment.

Deterministic, side-effect-free, network-free code. No AI, no legal
interpretation - this module answers "what does the text say", never
"what should the rule do about it".
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "AMBIGUITY_CLASS_DISPOSITIONS",
    "WIDE_THRESHOLD_FT",
    "DISPOSITION_WIDE",
    "DISPOSITION_NARROW_FAIL_CLOSED",
    "WidthClassification",
    "classify_street_width",
]

# ZR 12-10: "A wide street is a street that is 75 feet or more in width."
WIDE_THRESHOLD_FT = 75.0

DISPOSITION_WIDE = "wide"
DISPOSITION_NARROW_FAIL_CLOSED = "narrow_fail_closed"

_NUMBER = r"-?\d+(?:\.\d+)?"
_CLEAN_NUMERIC_RE = re.compile(rf"^\s*({_NUMBER})\s*$")
_RANGE_RE = re.compile(rf"^\s*({_NUMBER})\s*-\s*({_NUMBER})\s*$")
_INEQUALITY_RE = re.compile(rf"^\s*(>=|<=|>|<)\s*({_NUMBER})\s*$")

# Hedged-unknown patterns checked BEFORE the bare "Unknown" pattern (E7:
# "Unknown but <75" (38) / "Unknown but >75" (17)). Optional trailing
# "ft"/"feet"/"." tolerated; never widened beyond the observed shape.
_HEDGED_BELOW_RE = re.compile(
    r"^\s*unknown\s+but\s*<\s*75\s*(?:ft\.?|feet)?\.?\s*$", re.IGNORECASE
)
_HEDGED_ABOVE_RE = re.compile(
    r"^\s*unknown\s+but\s*>\s*75\s*(?:ft\.?|feet)?\.?\s*$", re.IGNORECASE
)
_BARE_UNKNOWN_RE = re.compile(r"^\s*unknown\s*$", re.IGNORECASE)
_NOT_APPLICABLE_RE = re.compile(r"^\s*n\s*/\s*a\.?\s*$", re.IGNORECASE)
_WIDTH_IRREGULAR_RE = re.compile(r"^\s*width\s+irregular\s*$", re.IGNORECASE)
_VARIES_RE = re.compile(r"^\s*varies\s*$", re.IGNORECASE)
_REGULAR_BUT_UNKNOWN_RE = re.compile(
    r"^\s*regular\s+but\s+unknown\.?\s*$", re.IGNORECASE
)

# Substring markers (not anchored: they can appear anywhere in a longer
# prose value, e.g. "Probably between 80 - 90"). ANY marker present makes
# the whole value approximate/hedged - never a mathematical entailment,
# regardless of what number follows (E7: "~80" and "Probably between 80 -
# 90" are both ambiguous even though the numbers alone would read >= 75).
_APPROX_MARKERS = ("~", "around", "more or less", "approx", "probably")


@dataclass(frozen=True)
class WidthClassification:
    """Typed classification of one raw DCM ``Streetwidth`` value.

    ``raw_text`` is preserved VERBATIM (including ``None`` for a missing
    value) - never normalized away, so provenance is never lost.
    ``ambiguity_class`` is a stable machine-readable code (see
    :data:`AMBIGUITY_CLASS_DISPOSITIONS` for the complete class table).
    ``disposition`` is exactly :data:`DISPOSITION_WIDE` or
    :data:`DISPOSITION_NARROW_FAIL_CLOSED` - never a third value.
    ``review_required`` is True whenever the disposition rests on an
    ambiguous, hedged, irregular, or unrecognized value rather than a
    mathematically confident read (clean numbers/ranges/inequalities that
    are unambiguously below 75 are narrow with ``review_required=False``).
    ``basis`` is a short, non-legal, human-readable explanation of the
    parse - never a legal or ZR conclusion.
    """

    raw_text: str | None
    ambiguity_class: str
    disposition: str
    review_required: bool
    basis: str


def _classification(
    raw_text: str | None,
    ambiguity_class: str,
    disposition: str,
    review_required: bool,
    basis: str,
) -> WidthClassification:
    return WidthClassification(
        raw_text=raw_text,
        ambiguity_class=ambiguity_class,
        disposition=disposition,
        review_required=review_required,
        basis=basis,
    )


def _parse_number(text: str) -> float | None:
    try:
        return float(text)
    except ValueError:  # pragma: no cover - regexes only ever pass numerics
        return None


def classify_street_width(raw_value: object) -> WidthClassification:
    """Classify one raw DCM ``Streetwidth`` value. Never raises: every input
    - including ``None``, empty strings, and any unrecognized text - always
    yields a typed :class:`WidthClassification` (fail-closed by
    construction, never an exception on messy source data)."""
    if raw_value is None:
        return _classification(
            None, "empty_or_missing", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "Streetwidth value is missing (None); no width information to "
            "act on, so the segment fails closed to narrow.",
        )
    if not isinstance(raw_value, str):
        return _classification(
            repr(raw_value), "unexpected_type", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "Streetwidth value was not a string as documented (STRING(50)); "
            "treated as unrecognized and failed closed (schema drift signal).",
        )

    text = raw_value.strip()
    if text == "":
        return _classification(
            raw_value, "empty_or_missing", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "Streetwidth value is an empty string; no width information to "
            "act on, so the segment fails closed to narrow.",
        )

    lowered = text.lower()

    # 1. Approximation/hedge markers take priority over every other shape:
    # even a numerically-high approximation is never a mathematical
    # entailment (E7: "~80", "Probably between 80 - 90").
    if any(marker in lowered for marker in _APPROX_MARKERS):
        return _classification(
            raw_value, "approximate_or_hedged_value_ambiguous",
            DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value carries an approximation/hedge marker (~, around, more "
            "or less, approx, probably); never treated as a clean numeral "
            "regardless of the number(s) present.",
        )

    # 2. Hedged unknowns (checked before the bare "Unknown" pattern).
    if _HEDGED_BELOW_RE.match(text):
        return _classification(
            raw_value, "unknown_hedged_below_75", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value hedges 'Unknown but <75'; the hedge is prose, not a "
            "mathematical entailment, so OQ-3 stays open and the segment "
            "fails closed to narrow with a review flag.",
        )
    if _HEDGED_ABOVE_RE.match(text):
        return _classification(
            raw_value, "unknown_hedged_above_75", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value hedges 'Unknown but >75'; wide is NEVER granted on a "
            "hedge alone, so the segment fails closed to narrow with a "
            "review flag despite the suggestive text.",
        )

    # 3. Labelled non-answers (checked before the bare "Unknown" pattern
    # where a phrase also contains the word "unknown").
    if _REGULAR_BUT_UNKNOWN_RE.match(text):
        return _classification(
            raw_value, "regular_but_unknown", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value is the labelled non-answer 'Regular but unknown.'; no "
            "width to act on.",
        )
    if _BARE_UNKNOWN_RE.match(text):
        return _classification(
            raw_value, "unknown_no_qualifier", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value is the bare label 'Unknown'; no width to act on.",
        )
    if _NOT_APPLICABLE_RE.match(text):
        return _classification(
            raw_value, "not_applicable_n_a", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value is the labelled non-answer 'n/a'; no width to act on.",
        )
    if _WIDTH_IRREGULAR_RE.match(text):
        return _classification(
            raw_value, "width_irregular", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value is the labelled non-answer 'Width Irregular'; no single "
            "width to act on.",
        )
    if _VARIES_RE.match(text):
        return _classification(
            raw_value, "varies", DISPOSITION_NARROW_FAIL_CLOSED, True,
            "value is the labelled non-answer 'varies'/'Varies'; no single "
            "width to act on.",
        )

    # 4. Clean numeral or decimal.
    clean_match = _CLEAN_NUMERIC_RE.match(text)
    if clean_match:
        value = _parse_number(clean_match.group(1))
        if value is not None and value < 0:
            return _classification(
                raw_value, "negative_value_unexpected", DISPOSITION_NARROW_FAIL_CLOSED, True,
                "value parses as a negative number, which is physically "
                "meaningless for a street width; treated as a data-quality "
                "anomaly and failed closed (never guessed).",
            )
        if value is not None and value >= WIDE_THRESHOLD_FT:
            return _classification(
                raw_value, "clean_numeric_ge_75", DISPOSITION_WIDE, False,
                f"clean numeral/decimal {value:g} >= {WIDE_THRESHOLD_FT:g} ft "
                "- mathematically entails wide.",
            )
        return _classification(
            raw_value, "clean_numeric_lt_75", DISPOSITION_NARROW_FAIL_CLOSED, False,
            f"clean numeral/decimal {value:g} < {WIDE_THRESHOLD_FT:g} ft - "
            "confidently narrow, no ambiguity to review.",
        )

    # 5. Hyphenated range "N1-N2".
    range_match = _RANGE_RE.match(text)
    if range_match:
        lo = _parse_number(range_match.group(1))
        hi = _parse_number(range_match.group(2))
        if lo is None or hi is None:  # pragma: no cover - regex guarantees numerics
            return _classification(
                raw_value, "unrecognized_free_text_ambiguous",
                DISPOSITION_NARROW_FAIL_CLOSED, True,
                "range endpoints could not be parsed as numbers; failed "
                "closed (never guessed).",
            )
        if lo < 0 or hi < 0:
            return _classification(
                raw_value, "negative_value_unexpected", DISPOSITION_NARROW_FAIL_CLOSED, True,
                "range contains a negative endpoint, which is physically "
                "meaningless for a street width; failed closed.",
            )
        if lo > hi:
            return _classification(
                raw_value, "range_order_unexpected", DISPOSITION_NARROW_FAIL_CLOSED, True,
                f"range endpoints are out of the expected ascending order "
                f"({lo:g} > {hi:g}); never assumed which bound is intended, "
                "failed closed.",
            )
        if lo >= WIDE_THRESHOLD_FT and hi >= WIDE_THRESHOLD_FT:
            return _classification(
                raw_value, "range_both_endpoints_ge_75", DISPOSITION_WIDE, False,
                f"range {lo:g}-{hi:g}: BOTH endpoints >= "
                f"{WIDE_THRESHOLD_FT:g} ft - mathematically entails wide.",
            )
        if hi < WIDE_THRESHOLD_FT:
            return _classification(
                raw_value, "range_both_endpoints_lt_75", DISPOSITION_NARROW_FAIL_CLOSED, False,
                f"range {lo:g}-{hi:g}: the upper endpoint is < "
                f"{WIDE_THRESHOLD_FT:g} ft, so the entire range is below "
                "the threshold - confidently narrow.",
            )
        return _classification(
            raw_value, "range_straddles_cutoff", DISPOSITION_NARROW_FAIL_CLOSED, True,
            f"range {lo:g}-{hi:g} straddles the {WIDE_THRESHOLD_FT:g} ft "
            "cutoff (lower endpoint below, upper at or above); no single "
            "width is entailed, failed closed with a review flag.",
        )

    # 6. One-sided inequality ">N" / ">=N" / "<N" / "<=N". The ZR concept is
    # "75 ft or more"; ">=75" and ">75" both entail width >= 75. For an
    # upper bound, "<75" (strict) excludes exactly 75 so is confidently
    # narrow, while "<=75" INCLUDES exactly 75 (which is itself wide) and
    # is therefore ambiguous - the strict/non-strict distinction matters at
    # exactly the threshold.
    ineq_match = _INEQUALITY_RE.match(text)
    if ineq_match:
        operator, number_text = ineq_match.groups()
        bound = _parse_number(number_text)
        if bound is not None and bound < 0:
            return _classification(
                raw_value, "negative_value_unexpected", DISPOSITION_NARROW_FAIL_CLOSED, True,
                "inequality bound is negative, which is physically "
                "meaningless for a street width; failed closed.",
            )
        if operator in (">", ">="):
            if bound is not None and bound >= WIDE_THRESHOLD_FT:
                return _classification(
                    raw_value, "gt_inequality_ge_75", DISPOSITION_WIDE, False,
                    f"inequality '{operator}{bound:g}': the true width is at "
                    f"least {bound:g} ft, which is >= {WIDE_THRESHOLD_FT:g} "
                    "ft - mathematically entails wide.",
                )
            return _classification(
                raw_value, "gt_inequality_below_75_ambiguous", DISPOSITION_NARROW_FAIL_CLOSED, True,
                f"inequality '{operator}{bound:g}': the true width could be "
                f"anywhere above {bound:g} ft, including at or above "
                f"{WIDE_THRESHOLD_FT:g} ft - ambiguous, failed closed with "
                "a review flag.",
            )
        # operator in ("<", "<=")
        strict = operator == "<"
        if bound is not None and (
            (strict and bound <= WIDE_THRESHOLD_FT)
            or (not strict and bound < WIDE_THRESHOLD_FT)
        ):
            klass = (
                "lt_inequality_at_or_below_75_confident_narrow"
                if strict
                else "le_inequality_below_75_confident_narrow"
            )
            return _classification(
                raw_value, klass, DISPOSITION_NARROW_FAIL_CLOSED, False,
                f"inequality '{operator}{bound:g}': the true width is "
                f"strictly below {WIDE_THRESHOLD_FT:g} ft - confidently "
                "narrow, no ambiguity to review.",
            )
        klass = (
            "lt_inequality_above_75_ambiguous"
            if strict
            else "le_inequality_at_or_above_75_ambiguous"
        )
        return _classification(
            raw_value, klass, DISPOSITION_NARROW_FAIL_CLOSED, True,
            f"inequality '{operator}{bound:g}': the true width could be at "
            f"or above {WIDE_THRESHOLD_FT:g} ft - ambiguous, failed closed "
            "with a review flag.",
        )

    # 7. Catch-all: any other unrecognized free text (never guessed).
    return _classification(
        raw_value, "unrecognized_free_text_ambiguous", DISPOSITION_NARROW_FAIL_CLOSED, True,
        "raw value did not match any known DCM Streetwidth class; "
        "conservatively treated as ambiguous per the fail-closed policy "
        "(never guessed).",
    )


# Complete class -> disposition table (for documentation/tests; mirrors the
# table recorded in the M4-T015 producer report). Kept as a plain tuple of
# (ambiguity_class, disposition, review_required_when_reached) so the test
# suite can assert exhaustiveness against this single source of truth.
AMBIGUITY_CLASS_DISPOSITIONS: tuple[tuple[str, str, bool], ...] = (
    ("clean_numeric_ge_75", DISPOSITION_WIDE, False),
    ("clean_numeric_lt_75", DISPOSITION_NARROW_FAIL_CLOSED, False),
    ("range_both_endpoints_ge_75", DISPOSITION_WIDE, False),
    ("range_both_endpoints_lt_75", DISPOSITION_NARROW_FAIL_CLOSED, False),
    ("range_straddles_cutoff", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("range_order_unexpected", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("gt_inequality_ge_75", DISPOSITION_WIDE, False),
    ("gt_inequality_below_75_ambiguous", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("lt_inequality_at_or_below_75_confident_narrow", DISPOSITION_NARROW_FAIL_CLOSED, False),
    ("lt_inequality_above_75_ambiguous", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("le_inequality_below_75_confident_narrow", DISPOSITION_NARROW_FAIL_CLOSED, False),
    ("le_inequality_at_or_above_75_ambiguous", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("approximate_or_hedged_value_ambiguous", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("width_irregular", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("varies", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("not_applicable_n_a", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("unknown_no_qualifier", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("unknown_hedged_below_75", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("unknown_hedged_above_75", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("regular_but_unknown", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("empty_or_missing", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("unexpected_type", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("negative_value_unexpected", DISPOSITION_NARROW_FAIL_CLOSED, True),
    ("unrecognized_free_text_ambiguous", DISPOSITION_NARROW_FAIL_CLOSED, True),
)
