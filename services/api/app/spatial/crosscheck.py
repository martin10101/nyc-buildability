"""ZTLDB cross-check (advisory 2.5).

Foundational asymmetry (both officially documented): the zoning-features layers
are officially NOT for lot-level determination, while ZTLDB is DCP's official
per-lot assignment product - but ZTLDB has NO percentages and a suspected stale
vintage. Therefore:

* ZTLDB is the authority for the district SET and ORDER.
* Our geometry is the only source of PERCENTAGES.
* Neither alone yields a confident assignment, and (owner amendment invariant 9)
  NOTHING here is ever labelled ``Verified`` or "confirmed assignment". The
  strongest state is ``agreement``; ZTLDB agreement on a geometrically uncertain
  lot upgrades the DISPLAYED result to ``conditional`` at most (owner choice C2),
  because ZTLDB derives from the same +/-20 ft geometry chain - shared lineage
  is corroboration, not independent confirmation.
"""

from __future__ import annotations

from .models import (
    LOT_SINGLE_DISTRICT_CONFIDENT,
    LOT_SPLIT_LOT_CONFIDENT,
    XCHK_AGREEMENT,
    XCHK_ORDERING_DISAGREEMENT,
    XCHK_SET_CONFLICT,
    XCHK_ZTLDB_ABSENT,
    CrossCheckOutcome,
)


def _norm(label: str) -> str:
    return " ".join(str(label).strip().upper().split())


def _vintage(district_vintage: str | None, ztldb_vintage: str | None) -> tuple[bool, str]:
    """Compare the district-layer source vintage against the ZTLDB row vintage
    (OQ-3). Only claim a skew when BOTH are known and differ; otherwise say so
    honestly rather than guessing."""
    if district_vintage is None or ztldb_vintage is None:
        return False, "vintage_comparison_unavailable"
    if str(district_vintage) == str(ztldb_vintage):
        return False, "match"
    return True, "differ"


def crosscheck_ztldb(
    *,
    geometric_ordered: list,  # [{"label", "share_point"}] confident base districts, share desc
    geometric_probable_label: str | None,  # max-share base label even when uncertain
    lot_overall_class: str,
    ztldb_assignment: dict | None,
    ztldb_status: str | None,  # "ok" | "no_record" | None
    ztldb_dataset_version: str | None = None,
    ztldb_source_vintage: str | None = None,
    district_source_vintage: str | None = None,
) -> CrossCheckOutcome:
    geom_labels = [str(d["label"]) for d in geometric_ordered]
    geom_norm = [_norm(x) for x in geom_labels]

    entries = (ztldb_assignment or {}).get("zoning_districts", []) if ztldb_assignment else []
    ztldb_labels = [str(e.get("value", "")) for e in entries if e.get("value")]
    ztldb_norm = [_norm(x) for x in ztldb_labels]

    possible_vintage_skew, vintage_comparison = _vintage(
        district_source_vintage, ztldb_source_vintage
    )

    ordered_ztldb = [{"position": i + 1, "label": lbl} for i, lbl in enumerate(ztldb_labels)]
    ordered_geom = [dict(d) for d in geometric_ordered]

    def _outcome(outcome: str, display_upgrade: str, notes: list) -> CrossCheckOutcome:
        return CrossCheckOutcome(
            outcome=outcome,
            ztldb_ordered_districts=ordered_ztldb,
            geometric_ordered_districts=ordered_geom,
            possible_vintage_skew=possible_vintage_skew,
            ztldb_dataset_version=ztldb_dataset_version,
            display_upgrade=display_upgrade,
            vintage_comparison=vintage_comparison,
            notes=notes,
        )

    if ztldb_status == "no_record" or not ztldb_norm:
        return _outcome(
            XCHK_ZTLDB_ABSENT,
            "none",
            [
                "ZTLDB has no zoning_district_1 assignment for this lot; a "
                "geometry-only result is capped at conditional in review."
            ],
        )

    geom_confident = lot_overall_class in (
        LOT_SINGLE_DISTRICT_CONFIDENT,
        LOT_SPLIT_LOT_CONFIDENT,
    )
    set_equal = bool(geom_norm) and set(geom_norm) == set(ztldb_norm)
    order_equal = geom_norm == ztldb_norm

    if geom_confident and set_equal and order_equal:
        return _outcome(
            XCHK_AGREEMENT,
            "none",
            ["geometric set+order match ZTLDB; not a Verified determination (M4+G6 only)"],
        )
    if geom_confident and set_equal and not order_equal:
        return _outcome(
            XCHK_ORDERING_DISAGREEMENT,
            "conditional",
            [
                "same district set, different order vs ZTLDB (plausible when point "
                "shares are close or vintages differ); conditional, not confident."
            ],
        )
    if geom_confident and not set_equal:
        note = ["geometric district set differs from ZTLDB; never pick a winner - data_conflict."]
        if possible_vintage_skew:
            note.append("nyzd vs ZTLDB vintages differ (possible_vintage_skew).")
        return _outcome(XCHK_SET_CONFLICT, "none", note)

    # Geometry is uncertain (boundary_uncertain / sliver_ambiguous) or found no
    # confident district. C2: ZTLDB corroboration of the probable side upgrades
    # the DISPLAYED result to conditional at most; underlying uncertainty stays.
    probable = _norm(geometric_probable_label) if geometric_probable_label else None
    if probable and probable in ztldb_norm:
        return _outcome(
            XCHK_AGREEMENT,
            "conditional",
            [
                "geometrically uncertain; ZTLDB corroborates the probable side. "
                "Conditional at most - shared +/-20 ft lineage means agreement is "
                "corroboration, not independent confirmation (C2)."
            ],
        )
    note = [
        "geometric uncertainty not corroborated by ZTLDB (set/side mismatch); "
        "data_conflict, professional review required."
    ]
    if possible_vintage_skew:
        note.append("nyzd vs ZTLDB vintages differ (possible_vintage_skew).")
    return _outcome(XCHK_SET_CONFLICT, "none", note)
