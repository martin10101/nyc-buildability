"""The §8a site-shape-and-street hidden-issue group (queue item B-09, slice 4; plan L-11).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 8a, "Site shape and street" row
(typical source: City Map, tax map, survey). This is the last §8a group. Six items, each a
flag / "No flag" / "Check needed" (never a guess, never an opportunity):

1. **Mapped-but-unbuilt streets or widening lines crossing the lot.**
2. **Shallow or irregular lot (yard relief).**
3. **Through lot.**
4. **Line-up with neighboring street walls (R6B, R7B, R8B).**
5. **Sloping site.**
6. **Neighbors' lot-line windows.**

What this group can read, and what it never decides
----------------------------------------------------

The only recorded facts this group reads are the single-lot (or combined, B-07) site
geometry ``app.spatial.site_geometry.SiteGeometry`` (queue item B-03), carried in as an
input, and - for item 4's context only - the recorded PLUTO zoning district through the
shared reader ``app.profile.site_facts.read_pluto_value``. B-03 is itself a geometric test
on the tax-map outline and the City Map (DCP Digital City Map / DCM) street center lines;
it is explicitly **not a Zoning Resolution determination** (``site_geometry.lot_type``).

**Data only, never the law.** Whether a rule applies here - shallow-lot or irregular-lot
yard relief, through-lot yard rules, the street-wall line-up rules of the contextual
districts (R6B / R7B / R8B) - and what it requires is a determination for the rule engine
(Lane A) confirmed by a qualified reviewer at G6 (platform principle 1; lane prompt B). This
layer only reports the recorded geometric facts and never decides a rule. No code or meaning
is guessed.

Flag direction, item by item
----------------------------

* Item 3 (through lot) is the one item a recorded value can answer: B-03 classifies the lot
  geometrically as ``through`` (flag), ``corner`` / ``interior`` (a real recorded "not a
  through lot" -> "No flag"), or ``unknown`` ("Check needed" with B-03's reason). Mirrors the
  recorded true / false / absent split ``map_based_rules`` uses for ``splitzone``.
* Item 1 (mapped-but-unbuilt streets / widening lines) flags when B-03 reports a mapped City
  Map street center line running *through* the lot interior (``street_crossings``); otherwise
  "Check needed" naming the City Map. The absence of a crossing is **never** a silent clear
  (D-051): street-widening lines, and mapped-but-unbuilt (paper) streets adjacent to the lot,
  are City Map features this layer does not read, and the City Map (Admin Code section 25-101:
  the adopted City Map is conclusive) is the authoritative source.
* Items 2, 4, 5 and 6 have no recorded value that this layer may read into a flag: shallow /
  irregular yard relief and the street-wall line-up are rule determinations; a sloping site
  needs a topographic / field survey; a neighbor's lot-line window needs a field survey or
  the neighbor's DOB records; none is connected. Each is "Check needed" naming the missing
  source, never guessed. Item 2 carries the recorded depth from B-03 as context when it is
  available, and item 4 carries the recorded PLUTO zoning district as context.

There is no site_fact or results contract slot for the flag layer yet, so a flag is a plain
record; wiring it into the study and a contract is a Lane C request (as the earlier B-09
slices did). A flag that carries a B-03 value keeps its provenance in ``evidence``.

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
from app.spatial.site_geometry import SiteGeometry
from app.spatial.site_geometry.results import (
    LOT_TYPE_CORNER,
    LOT_TYPE_INTERIOR,
    LOT_TYPE_THROUGH,
)

__all__ = ["GROUP_ID", "GROUP_TITLE", "site_shape_and_street_group"]

GROUP_ID = "site_shape_and_street"
GROUP_TITLE = "Site shape and street"

_BBL = re.compile(r"^[1-5][0-9]{9}$")

# The legal boundary this data layer never crosses (platform principle 1; lane prompt B):
# the recorded facts are reported; what any rule requires is a rule check. Mirrors the
# rule-check sentence the other §8a slices use (map_based_rules._RULE_CHECK).
_RULE_CHECK = (
    "What the rule requires is a determination for the engine (Lane A) confirmed by a "
    "qualified reviewer at G6; this data layer reports the recorded facts and never decides "
    "the rule."
)
# The authoritative City Map source (named in full so item 1's "Check needed" names it).
_CITY_MAP = (
    "the City Map (the adopted City Map is conclusive, Admin Code section 25-101; DCP "
    "Digital City Map / DCM street center lines)"
)
# When no B-03 site geometry is supplied the geometry-backed items cannot be read.
_NO_GEOMETRY = (
    "No site geometry (queue item B-03) was supplied, so the lot's recorded shape and street "
    "frontage could not be read; a reviewer must check it."
)


def _evidence(label: str, source: object) -> tuple[Mapping, ...]:
    return ({"label": label, "source": source},)


def _check_needed(
    item_id: str, title: str, typical: str, reason: str, *, evidence: tuple[Mapping, ...] = ()
) -> HiddenIssueFlag:
    return HiddenIssueFlag(
        f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_CHECK_NEEDED, reason, typical, evidence
    )


def _streets_source(geometry: SiteGeometry) -> object:
    """The B-03 street provenance (City Map / DCM), or the whole provenance as a fallback."""
    provenance = geometry.provenance if isinstance(geometry.provenance, Mapping) else {}
    streets = provenance.get("streets")
    return streets if streets is not None else dict(provenance)


def _mapped_streets_or_widening(geometry: SiteGeometry | None) -> HiddenIssueFlag:
    item_id = "mapped_streets_or_widening"
    title = "Mapped-but-unbuilt streets or widening lines crossing the lot"
    typical = (
        f"{_CITY_MAP}; a street-widening line and a mapped-but-unbuilt (paper) street are "
        "City Map features not carried in the street center-line data"
    )
    if geometry is not None and geometry.street_crossings:
        crossing = ", ".join(geometry.street_crossings)
        detail = (
            f"A mapped City Map street center line runs through the lot (B-03 geometry; "
            f"street key(s): {crossing}). Confirm on the City Map whether it is a "
            "mapped-but-unbuilt (paper) street, a street-widening line, or a built mapped "
            f"street. {_RULE_CHECK}"
        )
        return HiddenIssueFlag(
            f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
            _evidence(f"mapped street center line crossing the lot ({crossing})",
                      _streets_source(geometry)),
        )
    if geometry is None:
        return _check_needed(item_id, title, typical,
                             f"{_NO_GEOMETRY} Mapped-but-unbuilt streets and street-widening "
                             f"lines come from {_CITY_MAP}.")
    # Geometry present, no center line crosses the lot: NOT a clear (D-051). The City Map
    # still carries street-widening lines and adjacent paper streets this layer never reads.
    return _check_needed(
        item_id, title, typical,
        "B-03 found no street center line crossing the lot interior, but this does not "
        "clear the item: street-widening lines and mapped-but-unbuilt (paper) streets "
        f"adjacent to the lot are {_CITY_MAP} features this layer does not read, so a "
        "reviewer must check the City Map; it is never guessed.",
    )


def _depth_context(geometry: SiteGeometry) -> str:
    """One plain sentence of the lot's recorded depth, or "" when none is measured."""
    if geometry.lot_depth.known:
        return (f" The lot's measured depth is about {geometry.lot_depth.value:g} ft "
                f"({geometry.lot_depth.label}).")
    measured = [
        f"{f.depth.mean.value:g} ft from {f.street_key}"
        for f in geometry.frontages
        if f.depth is not None and f.depth.mean.known and f.depth.mean.value is not None
    ]
    if measured:
        return (f" The depth measured from each street is about {'; '.join(measured)} "
                "(approximate - tax map).")
    return ""


def _shallow_or_irregular(geometry: SiteGeometry | None) -> HiddenIssueFlag:
    item_id = "shallow_or_irregular"
    title = "Shallow or irregular lot (yard relief)"
    typical = (
        "The tax-map outline (approximate shape, B-03) and a field survey (the authoritative "
        "shape); the shallow-lot / irregular-lot yard rules (the engine)"
    )
    reason = (
        "Whether the lot is shallow or irregular enough to qualify for yard relief is a rule "
        "check: the yard rules set the depth threshold and the irregular-lot test, not this "
        f"data layer. {_RULE_CHECK}"
    )
    evidence: tuple[Mapping, ...] = ()
    if geometry is not None:
        reason += _depth_context(geometry)
        evidence = _evidence("Lot depth and outline (B-03)", dict(geometry.provenance))
    reason += (" A field survey gives the authoritative shape; it is never guessed.")
    return _check_needed(item_id, title, typical, reason, evidence=evidence)


def _through_lot(geometry: SiteGeometry | None) -> HiddenIssueFlag:
    item_id = "through_lot"
    title = "Through lot"
    typical = (
        "The tax-map outline and City Map street center lines (geometric lot type, B-03); "
        "the Zoning Resolution through-lot definition (reviewer)"
    )
    if geometry is None:
        return _check_needed(item_id, title, typical, _NO_GEOMETRY)
    lot_type = geometry.lot_type
    basis_evidence = _evidence(f"Geometric lot type: {lot_type.kind} (B-03)",
                               {"basis": lot_type.basis, "streets": list(lot_type.streets)})
    if lot_type.kind == LOT_TYPE_THROUGH:
        detail = (
            "B-03 classifies the lot geometrically as a through lot (it fronts two streets on "
            "opposite sides that do not meet at a corner). A through lot takes a front and a "
            "rear yard toward both streets. This is a geometric test on the tax-map outline, "
            f"not a Zoning Resolution determination. {_RULE_CHECK}"
        )
        return HiddenIssueFlag(
            f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_FLAG, detail, typical,
            basis_evidence,
        )
    if lot_type.kind in (LOT_TYPE_CORNER, LOT_TYPE_INTERIOR):
        detail = (
            f"B-03 classifies the lot geometrically as a {lot_type.kind} lot, not a through "
            "lot. This is a recorded geometric result, not an absent one; the Zoning "
            "Resolution lot-type determination is the reviewer's."
        )
        return HiddenIssueFlag(
            f"{GROUP_ID}.{item_id}", GROUP_ID, title, STATUS_NOT_FLAGGED, detail, typical,
            basis_evidence,
        )
    # Unknown: B-03 could not state the type (its reason names why).
    why = lot_type.reason or "The geometric lot type could not be determined."
    return _check_needed(
        item_id, title, typical,
        f"The geometric lot type could not be determined, so whether the lot is a through "
        f"lot must be checked on the tax map / City Map; it is never guessed. {why}",
    )


def _street_wall_lineup(profile: Mapping[str, Any] | None) -> HiddenIssueFlag:
    item_id = "street_wall_lineup"
    title = "Line-up with neighboring street walls (R6B, R7B, R8B)"
    typical = (
        "PLUTO zoning district (recorded); the street-wall / line-up rules (the engine); the "
        "neighboring buildings' street-wall positions (a field survey / DOB records)"
    )
    reason = (
        "Whether street-wall line-up rules apply to this lot and what they require is a rule "
        "check; the plan flags the contextual districts R6B, R7B and R8B. "
    )
    evidence: tuple[Mapping, ...] = ()
    if profile is not None:
        value, source, _problem = read_pluto_value(profile, "zonedist1")
        if value is not None:
            reason += f"PLUTO records the zoning district as {value!r}. "
            evidence = _evidence("PLUTO zonedist1", source)
    reason += (
        f"{_RULE_CHECK} The neighboring buildings' street-wall positions are not on record "
        "here; a field survey or DOB records must supply them. It is never guessed."
    )
    return _check_needed(item_id, title, typical, reason, evidence=evidence)


def _sloping_site() -> HiddenIssueFlag:
    return _check_needed(
        "sloping_site",
        "Sloping site",
        "A field survey / topographic survey (ground elevations); no connected source",
        "No ground-elevation or topographic source is connected, so whether the site slopes "
        "(which can change the base plane, how height is measured and yard regrading) must be "
        "checked on a field or topographic survey; it is never guessed.",
    )


def _neighbors_lot_line_windows() -> HiddenIssueFlag:
    return _check_needed(
        "neighbors_lot_line_windows",
        "Neighbors' lot-line windows",
        "A field survey / site observation of the neighboring buildings; the neighbors' DOB "
        "records; no connected source",
        "No source records the neighboring buildings' lot-line windows, so whether any legal "
        "lot-line windows face this lot (which can restrict building to the lot line) must be "
        f"checked by a field survey or the neighbors' DOB records; it is never guessed. "
        f"{_RULE_CHECK}",
    )


def site_shape_and_street_group(
    bbl: str,
    *,
    site_geometry: SiteGeometry | None = None,
    profile: Mapping[str, Any] | None = None,
) -> FlagGroup:
    """The §8a site-shape-and-street flag group for tax lot ``bbl`` (items in the module doc).

    Each of the six §8a items is a ``flag`` (a recorded geometric value shows the condition),
    ``not_flagged`` (B-03 records a known non-through lot type - a real "not a through lot"),
    or ``check_needed`` (the source is a rule determination, a survey, or the City Map, none
    read here, or the geometry is unknown / not supplied). Nothing is guessed and no rule is
    decided.

    Args:
        bbl: the tax lot (10-digit BBL).
        site_geometry: the B-03 single-lot (or B-07 combined) ``SiteGeometry`` for the lot,
            read (never changed) for its lot type, street crossings and depth. None means it
            was not supplied, so the geometry-backed items are "Check needed".
        profile: a built property profile, read only for item 4's recorded zoning-district
            context (PLUTO ``zonedist1``) through the shared trusted reader. None means that
            context is omitted; the item stays "Check needed" either way.

    Raises:
        ValueError: ``bbl`` is not a 10-digit BBL, an input is of the wrong type, or the
            profile's ``identity.bbl`` disagrees with ``bbl``.
    """
    if not isinstance(bbl, str) or not _BBL.match(bbl):
        raise ValueError(f"bbl must be a 10-digit BBL, got {bbl!r}")
    if site_geometry is not None and not isinstance(site_geometry, SiteGeometry):
        raise ValueError("site_geometry must be a SiteGeometry or None")
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

    flags = (
        _mapped_streets_or_widening(site_geometry),
        _shallow_or_irregular(site_geometry),
        _through_lot(site_geometry),
        _street_wall_lineup(profile),
        _sloping_site(),
        _neighbors_lot_line_windows(),
    )
    return FlagGroup(GROUP_ID, GROUP_TITLE, bbl, flags)
