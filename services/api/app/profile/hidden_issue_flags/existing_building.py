"""The §8a existing-building hidden-issue group (queue item B-09, first slice; plan L-11).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 8a, "Existing building" row. Five
items, each a flag / opportunity / "Check needed" (never a guess):

1. **Larger than today's rules** (section 5b). Reuses the existing zoning floor area
   (B-05, ``app.profile.existing_floor_area``) and, when the engine supplies today's
   as-of-right allowance, compares the two. The comparison is arithmetic on two given
   numbers; this module computes no allowance (that is the engine, Lane A) and never reads
   DOF/PLUTO building area (B-05 admits no such input). When either number is missing it is
   "Check needed", not a silent default.
2. **Non-conforming use.** Whether a use is non-conforming is a legal determination against
   the district's currently permitted uses (the engine, Lane A), read together with the
   certificate of occupancy's legal use (item 3). No Lane B source establishes it, so it is
   "Check needed" and never guessed here.
3. **Legal use and occupancy on the certificate of occupancy.** No certificate dataset has
   a legal-use/occupancy column (B-05 ``inputs``: the certificate datasets only show that a
   job received a certificate), and no certificate-document importer exists yet, so this is
   "Check needed" - refined when the existing-floor-area result already references a
   certificate of occupancy.
4. **Rent-regulated apartments.** No DHCR or HPD rent-regulation source is connected, so it
   is "Check needed".
5. **Harassment-certification requirements.** Whether a Certification of No Harassment
   applies depends on the building's location in an HPD program area (a map-based source)
   and HPD records, none connected, so it is "Check needed".

B-06 (``app.profile.data_versions``) is reused for item 1: when the existing-floor-area
fact's source is "Out of date", the flag carries that exception label.

This slice builds the flag layer and the "Check needed" fallback for one group (the
reconciliation's stated gap). The other three §8a groups - zoning-lot history (flag only,
plan P-2), map-based rules, and site shape and street - are later B-09 slices.

Pure, deterministic code: no I/O, no clock, no legal logic.
"""

from __future__ import annotations

import re

from app.profile.data_versions import DataVersionReport
from app.profile.existing_floor_area import BASIS_CERTIFICATE, ExistingFloorAreaResult
from app.profile.hidden_issue_flags.allowance import AsOfRightAllowance
from app.profile.hidden_issue_flags.model import (
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    STATUS_NOT_FLAGGED,
    FlagGroup,
    HiddenIssueFlag,
)

__all__ = ["GROUP_ID", "GROUP_TITLE", "existing_building_group"]

GROUP_ID = "existing_building"
GROUP_TITLE = "Existing building"

_BBL = re.compile(r"^[1-5][0-9]{9}$")

# Plan section 5b, verbatim (the flag a competitor missed on its own sample lot, plan line
# 261): shown when the existing building exceeds today's as-of-right allowance.
_LARGER_FLAG = ("The existing building is larger than today's zoning allows; demolition "
                "would reduce floor area.")


def _area(value: int | float) -> str:
    return f"{value:,} sq ft"


def _co_reference(efa: ExistingFloorAreaResult | None) -> str | None:
    """A certificate of occupancy already referenced by the floor-area result, or None.

    Reused from B-05 so item 3 can say a certificate is on record without a new source:
    either the floor-area figure was read from a certificate, or a DOB filing's completion
    was a certificate of occupancy."""
    if efa is None:
        return None
    if efa.basis == BASIS_CERTIFICATE:
        source = efa.fact.get("source") or {}
        return source.get("document_ref")
    completion = efa.completion or {}
    if completion.get("kind") == "certificate_of_occupancy":
        return completion.get("document_ref") or (
            f"certificate for job {completion.get('job')}" if completion.get("job") else None)
    return None


def _larger_than_today(
    efa: ExistingFloorAreaResult | None,
    allowance: AsOfRightAllowance | None,
    out_of_date: dict[str, str],
) -> HiddenIssueFlag:
    item_id = f"{GROUP_ID}.larger_than_today"
    title = "Existing building larger than today's rules"
    typical = ("DOB filing or certificate of occupancy (existing zoning floor area, M2-07); "
               "the engine's as-of-right allowance")

    def build(status: str, detail: str, *, evidence=(), fact_refs=(), exception=None):
        return HiddenIssueFlag(item_id, GROUP_ID, title, status, detail, typical,
                               tuple(evidence), tuple(fact_refs), exception)

    # B-05 forbids DOF/PLUTO building area as an input, so a known value here is always a
    # zoning floor area for this tax lot (scope kept as B-05 established it, never widened).
    known = efa is not None and efa.fact.get("value") is not None
    if not known:
        if efa is None:
            why = ("No existing-floor-area result was supplied. It comes from a DOB filing "
                   "or certificate of occupancy, or a stated assumption, and never from "
                   "DOF/PLUTO building area.")
            return build(STATUS_CHECK_NEEDED,
                         "Existing zoning floor area is not available, so it cannot be "
                         f"compared with today's as-of-right allowance. {why}")
        why = efa.reason or "Existing zoning floor area is unknown."
        return build(
            STATUS_CHECK_NEEDED,
            "Existing zoning floor area is not available, so it cannot be compared with "
            f"today's as-of-right allowance. {why}",
            fact_refs=_fact_ids(efa),
            exception=_exception(efa, out_of_date),
        )

    existing = efa.fact["value"]
    existing_evidence = {
        "label": f"Existing zoning floor area ({efa.basis_label})",
        "source": efa.fact.get("source"),
    }
    fact_refs = _fact_ids(efa)
    exception = _exception(efa, out_of_date)

    if allowance is None:
        return build(
            STATUS_CHECK_NEEDED,
            f"The existing zoning floor area is {_area(existing)} ({efa.basis_label}), but "
            "today's as-of-right zoning floor-area allowance was not supplied, so whether "
            "the building is larger than today's rules cannot be determined here. The "
            "allowance is the engine's.",
            evidence=[existing_evidence], fact_refs=fact_refs, exception=exception,
        )

    allowed = allowance.value_sq_ft
    evidence = [existing_evidence, {"label": "Today's as-of-right allowance",
                                    "source": dict(allowance.source)}]
    if existing > allowed:
        detail = (f"{_LARGER_FLAG} Existing {_area(existing)} ({efa.basis_label}) exceeds "
                  f"today's as-of-right {_area(allowed)}.")
        return build(STATUS_FLAG, detail, evidence=evidence, fact_refs=fact_refs,
                     exception=exception)
    detail = (f"The existing building ({_area(existing)}, {efa.basis_label}) is within "
              f"today's as-of-right allowance ({_area(allowed)}).")
    return build(STATUS_NOT_FLAGGED, detail, evidence=evidence, fact_refs=fact_refs,
                 exception=exception)


def _non_conforming_use() -> HiddenIssueFlag:
    return HiddenIssueFlag(
        f"{GROUP_ID}.non_conforming_use", GROUP_ID, "Non-conforming use",
        STATUS_CHECK_NEEDED,
        "Whether the use is non-conforming (and so loses its protection after major "
        "damage) is a determination against the district's currently permitted uses (the "
        "engine) read with the certificate of occupancy's legal use. No source establishes "
        "it, so a reviewer must check it; it is never guessed.",
        "DOB filings/certificate of occupancy (legal use); zoning use rules (engine)",
    )


def _legal_use_and_occupancy(efa: ExistingFloorAreaResult | None) -> HiddenIssueFlag:
    co_ref = _co_reference(efa)
    note = (f" A certificate of occupancy is already referenced for the floor area "
            f"({co_ref}); its legal use and occupancy were not transcribed from the "
            "document." if co_ref else "")
    return HiddenIssueFlag(
        f"{GROUP_ID}.legal_use_and_occupancy", GROUP_ID,
        "Legal use and occupancy on the certificate of occupancy",
        STATUS_CHECK_NEEDED,
        "No certificate-of-occupancy dataset carries a legal-use or occupancy column, and "
        "no certificate-document importer is connected, so the legal use and occupancy must "
        f"be read from the certificate itself.{note}",
        "DOB certificate of occupancy (document)",
    )


def _rent_regulated() -> HiddenIssueFlag:
    return HiddenIssueFlag(
        f"{GROUP_ID}.rent_regulated_apartments", GROUP_ID, "Rent-regulated apartments",
        STATUS_CHECK_NEEDED,
        "No DHCR or HPD rent-regulation source is connected, so whether the building has "
        "rent-regulated apartments cannot be determined from the data on record and is "
        "never guessed.",
        "DHCR and HPD data",
    )


def _harassment_certification() -> HiddenIssueFlag:
    return HiddenIssueFlag(
        f"{GROUP_ID}.harassment_certification", GROUP_ID,
        "Harassment-certification requirements",
        STATUS_CHECK_NEEDED,
        "Whether a Certification of No Harassment applies depends on the building's location "
        "in an HPD program area (a map-based source) and HPD records, neither connected, so "
        "a reviewer must check it.",
        "HPD Certification of No Harassment program (map-based) and HPD data",
    )


def _fact_ids(efa: ExistingFloorAreaResult | None) -> tuple[str, ...]:
    if efa is None:
        return ()
    fact_id = efa.fact.get("fact_id")
    return (fact_id,) if isinstance(fact_id, str) else ()


def _exception(efa: ExistingFloorAreaResult | None, out_of_date: dict[str, str]) -> str | None:
    for fact_id in _fact_ids(efa):
        if fact_id in out_of_date:
            return out_of_date[fact_id]
    return None


def existing_building_group(
    bbl: str,
    *,
    existing_floor_area: ExistingFloorAreaResult | None = None,
    as_of_right_allowance: AsOfRightAllowance | None = None,
    data_versions: DataVersionReport | None = None,
) -> FlagGroup:
    """The §8a existing-building flag group for tax lot ``bbl`` (items in the module doc).

    Args:
        bbl: the tax lot (10-digit BBL).
        existing_floor_area: the B-05 existing zoning floor-area result for the lot, or
            None when it was not resolved.
        as_of_right_allowance: today's as-of-right zoning floor-area allowance from the
            engine (Lane A), or None when the engine has not supplied it. This module never
            computes it.
        data_versions: the B-06 data-version report, used to mark a flag "Out of date" when
            the floor-area fact's source is behind, or None.

    Raises:
        ValueError: ``bbl`` is not a 10-digit BBL, or an input is of the wrong type.
    """
    if not isinstance(bbl, str) or not _BBL.match(bbl):
        raise ValueError(f"bbl must be a 10-digit BBL, got {bbl!r}")
    if existing_floor_area is not None and not isinstance(
        existing_floor_area, ExistingFloorAreaResult
    ):
        raise ValueError("existing_floor_area must be an ExistingFloorAreaResult or None")
    if as_of_right_allowance is not None and not isinstance(
        as_of_right_allowance, AsOfRightAllowance
    ):
        raise ValueError("as_of_right_allowance must be an AsOfRightAllowance or None")
    if data_versions is not None and not isinstance(data_versions, DataVersionReport):
        raise ValueError("data_versions must be a DataVersionReport or None")

    out_of_date = data_versions.fact_exception_labels() if data_versions is not None else {}

    flags = (
        _larger_than_today(existing_floor_area, as_of_right_allowance, out_of_date),
        _non_conforming_use(),
        _legal_use_and_occupancy(existing_floor_area),
        _rent_regulated(),
        _harassment_certification(),
    )
    return FlagGroup(GROUP_ID, GROUP_TITLE, bbl, flags)
