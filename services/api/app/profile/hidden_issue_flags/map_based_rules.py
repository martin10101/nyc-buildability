"""The §8a map-based-rules hidden-issue group (queue item B-09, slice 3; plan L-11).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 8a, "Map-based rules" row (typical
source: DCP and LPC data, FEMA maps). Nine items, each a flag / "Check needed" / "No flag"
(never a guess):

1. **Special districts and overlays.**
2. **Inclusionary-housing areas.**
3. **Lots split by a district line.**
4. **Lots within about 20 ft of a district line** (the city's zoning map is not lot-precise).
5. **Flood zones and flood-resilience height rules.**
6. **Waterfront and coastal-zone rules.**
7. **Transit easements near stations.**
8. **Airport height limits.**
9. **Landmarks and historic districts.**

Every flag comes from a source ALREADY recorded in the repository. The recorded source is
the PLUTO row (queue item B-01, version-pinned by B-06), read through the one shared reader
``app.profile.site_facts.read_pluto_value`` so one PLUTO column is read the one way, with the
same trust rules the site facts use (an identity conflict, a duplicate, a connector drift
signal, a data conflict or a named conflict makes a value unusable). PLUTO carries these
map-based columns with provenance: ``overlay1``/``overlay2`` (commercial overlays),
``spdist1``-``spdist3`` (special districts), ``mih_opt1``-``mih_opt4`` (Mandatory
Inclusionary Housing option flags), ``splitzone`` (lot split by a district line),
``firm07_flag``/``pfirm15_flag`` (FEMA floodplain flags) and ``landmark``/``histdist``
(landmark / historic district). An item whose source is not recorded in this repository
(inclusionary-housing designated areas beyond the PLUTO flag, lot-vs-boundary proximity,
waterfront/coastal, transit easements, airport height) is "Check needed" naming the missing
source, never a guess (lane prompt B).

**Data only, never the law.** Where an item maps the lot into a regulated area, this layer
only reports that the lot is mapped that way and that a rule check is needed; it never
decides what the special district, overlay, inclusionary-housing area, flood-resilience
rule, landmark designation, etc. REQUIRES. That is a Zoning-Resolution / legal determination
for the rule engine (Lane A) and a qualified reviewer at G6 (platform principle 1; lane
prompt B). No code's meaning is guessed: a PLUTO code is surfaced verbatim, never decoded.

**SODA omit-null (never a silent clear).** SODA omits a null field per record, so an absent
categorical column means "none OR unknown" and is "Check needed" naming the source to
confirm, never a silent "no issue" (D-051: no silent default direction) - the same rule
B-10's transit/parking status uses. The one exception is ``splitzone``, a boolean PLUTO
serves explicitly as ``true``/``false``: ``false`` is a real recorded "not split" and is
"No flag". A ``false`` ``splitzone`` does NOT mean the lot is not NEAR a district line
(item 4); the two are different questions and item 4 stays "Check needed".

The transit/parking ZONE (queue item B-10, ``app.profile.transit_parking``) is a different
map layer from a transit EASEMENT near a station (item 7). B-10 surfaces the zone once per
study (check C-8); whether it should ALSO appear as a §8a map-based flag is B-10's open owner
question (b), not decided here. This group can CONSUME B-10's status as an opt-in extra flag
only when the caller supplies it (``transit_parking``); it is off by default, so the default
result is exactly the nine §8a items and this layer does not decide that owner question.

There is no site_fact or results contract slot for the flag layer yet, so a flag is a plain
record; wiring it into the study and a contract is a Lane C request (as B-06/B-09/B-10 did).
Each flag carries its PLUTO ``source``, so ``app.profile.data_versions`` (B-06) pins it
("Out of date" / "Version unknown") with no extra wiring.

Pure, deterministic code: no I/O, no clock, no legal logic.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from app.profile.hidden_issue_flags.model import (
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    STATUS_NOT_FLAGGED,
    FlagGroup,
    HiddenIssueFlag,
)
from app.profile.site_facts import read_pluto_value
from app.profile.transit_parking import (
    STATUS_RECORDED as TRANSIT_STATUS_RECORDED,
)
from app.profile.transit_parking import (
    TransitParkingStatus,
)

__all__ = ["GROUP_ID", "GROUP_TITLE", "map_based_rules_group"]

GROUP_ID = "map_based_rules"
GROUP_TITLE = "Map-based rules"

_BBL = re.compile(r"^[1-5][0-9]{9}$")

# The legal boundary this data layer never crosses (platform principle 1; lane prompt B):
# the map layer is reported; what it REQUIRES under the Zoning Resolution is a rule check.
_RULE_CHECK = (
    "What this requires under the Zoning Resolution is a rule check (the engine, Lane A) "
    "confirmed by a qualified reviewer at G6; this data layer only reports that the lot is "
    "mapped this way and never decides the rule."
)
# Why an absent categorical PLUTO column is "Check needed", not a silent "no issue".
_OMIT_NULL = (
    "SODA omits null fields, so an absent column means none OR unknown here, never a silent "
    "\"no issue\"; a reviewer confirms it on the source, and it is never guessed"
)
# When no profile is supplied the PLUTO-backed items cannot be read.
_NO_PROFILE = (
    "No property profile was supplied, so the recorded PLUTO value for this item could not "
    "be read; a reviewer must check it."
)


def _read(profile: Mapping[str, Any] | None, column: str) -> tuple[Any, dict | None, str | None]:
    """One recorded PLUTO column, or (None, None, reason) when no profile was supplied."""
    if profile is None:
        return None, None, _NO_PROFILE
    return read_pluto_value(profile, column)


def _evidence(label: str, source: dict | None) -> tuple[Mapping, ...]:
    return ({"label": label, "source": source},)


def _check_needed(
    item_id: str, title: str, typical: str, reason: str, *, evidence: tuple[Mapping, ...] = ()
) -> HiddenIssueFlag:
    return HiddenIssueFlag(
        f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_CHECK_NEEDED, reason, typical, evidence
    )


def _special_districts_and_overlays(profile: Mapping[str, Any] | None) -> HiddenIssueFlag:
    item_id = "special_districts_and_overlays"
    title = "Special districts and overlays"
    typical = (
        "PLUTO overlay1-2 (commercial overlays) and spdist1-3 (special districts), recorded; "
        "DCP zoning map special-district and commercial-overlay layers"
    )
    mapped: list[str] = []
    evidence: list[Mapping] = []
    problems: list[str] = []
    for label_fmt, column in (
        ("commercial overlay {} (PLUTO {})", "overlay1"),
        ("commercial overlay {} (PLUTO {})", "overlay2"),
        ("special district {} (PLUTO {})", "spdist1"),
        ("special district {} (PLUTO {})", "spdist2"),
        ("special district {} (PLUTO {})", "spdist3"),
    ):
        value, source, problem = _read(profile, column)
        if problem is not None and profile is not None and value is None and (
            "has no" not in problem
        ):
            # Present but untrusted (conflict/drift/duplicate): keep it visible, never surfaced.
            problems.append(problem)
        if value is not None:
            mapped.append(label_fmt.format(value, column))
            evidence.append({"label": label_fmt.format(value, column), "source": source})
    if mapped:
        detail = (
            f"The lot is mapped with: {'; '.join(mapped)}. {_RULE_CHECK}"
        )
        if problems:
            detail += f" (Also check: {' '.join(problems)})"
        return HiddenIssueFlag(
            f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
            tuple(evidence),
        )
    if problems:
        return _check_needed(
            item_id, title, typical,
            f"A recorded PLUTO special-district / overlay value could not be used: "
            f"{' '.join(problems)} A reviewer must confirm it on the DCP zoning map.",
        )
    reason = (
        f"PLUTO records no special district or commercial overlay for this lot ({_OMIT_NULL}). "
        f"Confirm on the DCP zoning map (NYZD special-district and NYCO overlay layers)."
        if profile is not None else _NO_PROFILE
    )
    return _check_needed(item_id, title, typical, reason)


def _inclusionary_housing(profile: Mapping[str, Any] | None) -> HiddenIssueFlag:
    item_id = "inclusionary_housing"
    title = "Inclusionary-housing areas"
    typical = (
        "DCP Mandatory / Voluntary Inclusionary Housing Designated Areas; "
        "PLUTO mih_opt1-4 (recorded when present)"
    )
    for column in ("mih_opt1", "mih_opt2", "mih_opt3", "mih_opt4"):
        value, source, problem = _read(profile, column)
        if problem is None and value:
            detail = (
                f"PLUTO records a Mandatory Inclusionary Housing option flag for this lot "
                f"(PLUTO {column}). {_RULE_CHECK}"
            )
            return HiddenIssueFlag(
                f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
                _evidence(f"PLUTO {column}", source),
            )
    reason = (
        "PLUTO records no Mandatory Inclusionary Housing option flag (mih_opt) for this lot "
        f"({_OMIT_NULL}). Whether the lot is in an Inclusionary Housing Designated Area "
        "(mandatory or voluntary) must be checked on the DCP Inclusionary Housing data."
        if profile is not None else _NO_PROFILE
    )
    return _check_needed(item_id, title, typical, reason)


def _split_by_district_line(profile: Mapping[str, Any] | None) -> HiddenIssueFlag:
    item_id = "split_by_district_line"
    title = "Lot split by a district line"
    typical = "PLUTO splitzone (recorded); DCP zoning map district boundaries"
    value, source, problem = _read(profile, "splitzone")
    if problem is None and isinstance(value, bool):
        if value:
            detail = (
                "PLUTO records this lot as split by a zoning-district boundary "
                f"(splitzone true). Which district's rules apply to which part is a check. "
                f"{_RULE_CHECK}"
            )
            return HiddenIssueFlag(
                f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
                _evidence("PLUTO splitzone", source),
            )
        detail = (
            "PLUTO records this lot as not split by a zoning-district boundary "
            "(splitzone false). This is a recorded value, not an absent one; it does not say "
            "the lot is away from a district line (see \"within about 20 ft of a district "
            "line\")."
        )
        return HiddenIssueFlag(
            f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_NOT_FLAGGED, detail, typical,
            _evidence("PLUTO splitzone", source),
        )
    reason = (
        problem or f"PLUTO splitzone is {value!r}, not a usable true/false value."
    ) if profile is not None else _NO_PROFILE
    return _check_needed(item_id, title, typical, f"{reason} A reviewer must check it.")


def _near_district_line() -> HiddenIssueFlag:
    return _check_needed(
        "near_district_line",
        "Lot within about 20 ft of a district line",
        "DCP zoning map district boundaries (NYZD / NYCO); a lot-vs-boundary proximity "
        "analysis (the platform spatial substrate)",
        "No recorded data field answers this. The city's zoning map is not lot-precise, so "
        "whether the lot is within about 20 ft of a district line needs a lot-vs-boundary "
        "proximity check against the DCP zoning-map boundaries. The platform's spatial "
        "substrate computes this (near-boundary), but this data layer runs no geometry, so a "
        "reviewer must check it; it is never guessed.",
    )


def _flood(profile: Mapping[str, Any] | None) -> HiddenIssueFlag:
    item_id = "flood"
    title = "Flood zones and flood-resilience height rules"
    typical = (
        "FEMA Flood Insurance Rate Maps (FIRM 2007 / Preliminary FIRM 2015); "
        "PLUTO firm07_flag / pfirm15_flag (recorded when present)"
    )
    for column in ("firm07_flag", "pfirm15_flag"):
        value, source, problem = _read(profile, column)
        if problem is None and value not in (None, 0, 0.0, False):
            detail = (
                "PLUTO records this lot in a FEMA flood-insurance-rate-map floodplain "
                f"(PLUTO {column}). The flood zone letter (for example A, AE, X, VE) comes "
                "from the FEMA map, and the flood-resilience height rules (ZR Appendix G) are "
                f"a rule check. {_RULE_CHECK}"
            )
            return HiddenIssueFlag(
                f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
                _evidence(f"PLUTO {column}", source),
            )
    reason = (
        "PLUTO records no FEMA floodplain flag (firm07_flag / pfirm15_flag) for this lot "
        f"({_OMIT_NULL}), and no FEMA flood-map source is connected to confirm the flood "
        "zone letter. A reviewer must check the FEMA Flood Insurance Rate Map."
        if profile is not None else _NO_PROFILE
    )
    return _check_needed(item_id, title, typical, reason)


def _waterfront_coastal() -> HiddenIssueFlag:
    return _check_needed(
        "waterfront_coastal",
        "Waterfront and coastal-zone rules",
        "DCP Waterfront Revitalization Program area; NYS Coastal Zone Boundary",
        "No DCP Waterfront or Coastal Zone Boundary source is connected, so whether the lot "
        "is on the waterfront or in the coastal zone (which brings extra rules) must be "
        "checked; it is never guessed.",
    )


def _transit_easements() -> HiddenIssueFlag:
    return _check_needed(
        "transit_easements",
        "Transit easements near stations",
        "MTA / NYCT transit easements; DCP zoning map transit-easement notations "
        "(ZR 13-10 / 37-40)",
        "No transit-easement source is connected. Whether a transit easement crosses the lot "
        "near a subway station (a different map layer from the transit/parking ZONE, which "
        "B-10 surfaces separately) must be checked; it is never guessed.",
    )


def _airport_height() -> HiddenIssueFlag:
    return _check_needed(
        "airport_height",
        "Airport height limits",
        "FAA Part 77 obstruction surfaces; airport approach-surface limits",
        "No airport-height source is connected. Whether an FAA Part 77 obstruction surface or "
        "an airport approach-surface limit applies to the lot must be checked; it is never "
        "guessed.",
    )


def _landmarks_historic(profile: Mapping[str, Any] | None) -> HiddenIssueFlag:
    item_id = "landmarks_historic"
    title = "Landmarks and historic districts"
    typical = (
        "LPC Individual Landmarks and Historic Districts; "
        "PLUTO landmark / histdist (recorded when present)"
    )
    mapped: list[str] = []
    evidence: list[Mapping] = []
    for label_fmt, column in (
        ("landmark {!r} (PLUTO {})", "landmark"),
        ("historic district {!r} (PLUTO {})", "histdist"),
    ):
        value, source, problem = _read(profile, column)
        if problem is None and value is not None:
            mapped.append(label_fmt.format(value, column))
            evidence.append({"label": label_fmt.format(value, column), "source": source})
    if mapped:
        detail = (
            f"PLUTO records this lot as: {'; '.join(mapped)}. Landmarks Preservation "
            f"Commission jurisdiction and what it requires is a determination. {_RULE_CHECK}"
        )
        return HiddenIssueFlag(
            f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
            tuple(evidence),
        )
    reason = (
        "PLUTO records no landmark or historic-district value for this lot "
        f"({_OMIT_NULL}), and no LPC source is connected. Whether the lot is an individual "
        "landmark or in a historic district must be checked on the LPC data."
        if profile is not None else _NO_PROFILE
    )
    return _check_needed(item_id, title, typical, reason)


def _transit_parking_zone(status: TransitParkingStatus) -> HiddenIssueFlag:
    """OPT-IN extra flag (pending B-10 owner question b): the lot's transit/parking ZONE.

    Surfaces B-10's already-recorded status verbatim; it makes no new decision. The
    parking OUTCOME stays a rule-engine / G6 determination, as B-10 states.
    """
    item_id = "transit_parking_zone"
    title = "Transit/parking zone"
    typical = "PLUTO transitzone (DCP Transit Zones classification); queue item B-10"
    source = status.source
    if status.status == TRANSIT_STATUS_RECORDED and status.transit_zone is not None:
        detail = (
            f"The lot's transit/parking zone is {status.transit_zone!r} (queue item B-10, "
            "one source applied to every option, check C-8). What it means for parking is a "
            "rule-engine / G6 determination this data layer never makes."
        )
        return HiddenIssueFlag(
            f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
            _evidence("PLUTO transitzone (B-10)", source),
        )
    return _check_needed(
        item_id, title, typical,
        "The transit/parking zone is not available from PLUTO for this lot "
        f"(B-10: {status.missing_source}). A reviewer must check it.",
        evidence=_evidence("PLUTO transitzone (B-10)", source),
    )


def map_based_rules_group(
    bbl: str,
    *,
    profile: Mapping[str, Any] | None = None,
    transit_parking: TransitParkingStatus | None = None,
) -> FlagGroup:
    """The §8a map-based-rules flag group for tax lot ``bbl`` (items in the module doc).

    Each of the nine §8a items is a ``flag`` (the recorded PLUTO value maps the lot into a
    regulated area; what it requires is a rule check), ``not_flagged`` (``splitzone`` recorded
    false - a real "not split"), or ``check_needed`` (the source is not recorded / not
    connected, or an absent categorical PLUTO column, which under SODA omit-null means none or
    unknown). Nothing is guessed and no rule is decided.

    Args:
        bbl: the tax lot (10-digit BBL).
        profile: a document from ``app.profile.builder.build_property_profile`` for this lot,
            read (never changed) for its recorded PLUTO map-based columns. None means no
            profile was supplied, so the PLUTO-backed items are "Check needed".
        transit_parking: the B-10 transit/parking status for this lot. When supplied, an
            OPT-IN tenth flag surfaces the lot's transit/parking ZONE (B-10, check C-8).
            Off by default: whether the zone should appear as a §8a map-based flag (vs
            study-level only) is B-10's open owner question (b), not decided here.

    Raises:
        ValueError: ``bbl`` is not a 10-digit BBL, ``profile`` is not a mapping, the profile's
            ``identity.bbl`` disagrees with ``bbl``, or ``transit_parking`` is of the wrong type.
    """
    if not isinstance(bbl, str) or not _BBL.match(bbl):
        raise ValueError(f"bbl must be a 10-digit BBL, got {bbl!r}")
    if profile is not None:
        if not isinstance(profile, Mapping):
            raise ValueError("profile must be a built property-profile mapping or None")
        identity = profile.get("identity")
        profile_bbl = identity.get("bbl") if isinstance(identity, Mapping) else None
        if profile_bbl != bbl:
            raise ValueError(
                f"profile identity.bbl {profile_bbl!r} does not match bbl {bbl!r}; "
                "the flag group must describe one lot"
            )
    if transit_parking is not None and not isinstance(transit_parking, TransitParkingStatus):
        raise ValueError("transit_parking must be a TransitParkingStatus or None")

    flags: list[HiddenIssueFlag] = [
        _special_districts_and_overlays(profile),
        _inclusionary_housing(profile),
        _split_by_district_line(profile),
        _near_district_line(),
        _flood(profile),
        _waterfront_coastal(),
        _transit_easements(),
        _airport_height(),
        _landmarks_historic(profile),
    ]
    if transit_parking is not None:
        flags.append(_transit_parking_zone(transit_parking))
    return FlagGroup(GROUP_ID, GROUP_TITLE, bbl, tuple(flags))
