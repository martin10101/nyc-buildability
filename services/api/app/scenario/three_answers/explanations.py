"""C-11 explanation audit and the guarded status strip (task A-05; competitor-review
check C-11; directive D-090).

Competitor-review check C-11 requires that explanations such as "another floor would exceed
the height limit" appear ONLY when computed as true - no template sentence that survives when
its condition is false. This module carries the mechanised audit of EVERY sentence the
three-answer generator can emit, and owns the one piece of generator wiring the audit found
untrue: the status-strip measurement chip.

Two classes of emitted text:

* ``computed_true`` - emitted only when a condition computed from the inputs holds; a flip
  test proves it disappears or changes when the condition is false.
* ``fixed_scope`` - a standing statement about what this slice does NOT yet compute. It is
  always true because the slice never computes that family; it is listed with that reason.

C-11 AUDIT (sentence -> class -> guard / why always true):

Status strip (engine):
  1  measurement chip "Approximate measurements" / "Survey measurements" -- computed_true:
     ``site_measurement_status_chip`` reads the site rank; a survey is never flagged
     approximate (THIS WAS THE DEFECT: the chip was fixed text before A-05).
  2  "Preliminary zoning results" -- fixed_scope: the owner's overall label for the preliminary
     results (D-090-R641); each result keeps its own settled/conditional/not-known state.
  3  "Lots you selected" -- fixed_scope: results always rest on the caller-selected lots.
  4  "Zoning engine not enabled" (lane-off strip) -- computed_true: only when the flag is off.
  5  lane-off gap reasons ("...Lane A... is not enabled...") -- computed_true: flag off only.

Document body (engine ``_assemble_document``):
  6  ``lot_selection_statement`` -- fixed_scope: this slice never verifies the zoning lot.
  7  ``remaining_floor_area`` reason (D-090-R038) -- fixed_scope: the slot never states a
     number in this slice.
  8  ``best_combination`` reason ("add-on model is not built in this slice") -- fixed_scope:
     the add-on model (M1-25) is not in this slice.
  9  ``existing_building`` reason ("keep / partial / full rebuild...") -- fixed_scope: the
     existing-building paths (M2-08) are not in this slice.
  10 ``completeness_line`` text + ``not_yet_covered`` -- fixed_scope: named families unbuilt.

Answers (answers.py):
  11 answer value labels ("Maximum residential FAR (standard)" ...) -- computed_true: emitted
     beside a computed value; absent when the answer is not_available.
  12 allowance / envelope not_available reason (``RuleGap``) -- computed_true: only when a
     rule produced no usable value.

Building option (building_option.py):
  13 ``shortfall.reasons[].text`` -- computed_true: only when ``comp.shortfall_sf > 0`` (else
     ``shortfall`` is ``{"status": "none"}``).
  14 gap "The building option needs the floor-area allowance..." -- computed_true: input
     missing only.
  15 gap "No floor fits under the H ft height limit..." -- computed_true: no floor fits only.

Geometry (geometry.py):
  16 yards reason "No rear yard is required within 100 ft of the corner..." -- computed_true:
     only when ``rear_yard_required is False``.
  17 yards not_available "The rear-yard requirement... is not resolved." -- computed_true:
     only when the waiver did not resolve.
  18 setback not_available "Setback lines need the ZR 23-433 setback depths..." -- fixed_scope:
     ZR 23-433 setbacks are not encoded in this slice.
  19 envelope not_available "...needs the height limit and lot coverage." -- computed_true:
     height or coverage missing only.
  20 floor_plates not_available "Floor plates need the building option." -- computed_true:
     building option unavailable only.

Unit estimate (dwelling_units.py):
  21 ``formula`` ("20,150 / 680 = 29.63") -- computed_true: built from the computed allowance
     and the rule's own factor.
  22 ``rounding_rule`` ("rounds up only at .75 or more") -- fixed_scope: the ZR 23-52(b)
     rounding rule the estimate is computed under.
  23 not_available reason (``RuleGap``) -- computed_true: allowance or rule unavailable only.

Inputs (inputs.py):
  24 floor-to-floor assumption label -- computed_true: built from the actual value in effect.
  25 measurement labels ("Survey (entered)", "City records", ...) -- computed_true: keyed by
     the measurement rank actually carried.

Only entry #1 was a C-11 defect before task A-05: the status strip carried the fixed text
"Approximate measurements" regardless of the site measurement rank, so a survey-measured lot
was wrongly flagged approximate. It is now computed from the rank below. Every other
``computed_true`` sentence was already guarded by its emitting module; every ``fixed_scope``
sentence is a standing statement about an unbuilt family and is listed above with the reason
it is always true.
"""

from __future__ import annotations

# Site measurement ranks precise enough that "Approximate measurements" would be untrue. Only
# a survey is a precise measurement in this slice; city records, tax-map and assumed values are
# all approximate. Keyed to ``inputs.DEFAULT_SITE_MEASUREMENT_RANK`` and its sibling ranks.
_PRECISE_SITE_RANKS = frozenset({"survey_entered"})

APPROXIMATE_MEASUREMENTS_CHIP = "Approximate measurements"
SURVEY_MEASUREMENTS_CHIP = "Survey measurements"


def site_measurement_status_chip(site_measurement_rank: str) -> dict:
    """The status-strip measurement chip, computed from the site measurement rank (C-11).

    A precise survey must NOT be flagged "Approximate measurements"; every other rank (city
    records, approximate tax map, entered, assumed) is approximate, so the chip is true."""
    if site_measurement_rank in _PRECISE_SITE_RANKS:
        return {"text": SURVEY_MEASUREMENTS_CHIP}
    return {"text": APPROXIMATE_MEASUREMENTS_CHIP}


def build_status_strip(site_measurement_rank: str) -> list[dict]:
    """The on-path status strip: a fixed "Preliminary zoning results" label (the owner's overall
    label, D-090-R641; each result keeps its own state), the rank-computed measurement chip
    (C-11), and a fixed "Lots you selected" label."""
    return [
        {"text": "Preliminary zoning results"},
        site_measurement_status_chip(site_measurement_rank),
        {"text": "Lots you selected"},
    ]
