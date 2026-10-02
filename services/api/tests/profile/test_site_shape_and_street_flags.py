"""§8a site-shape-and-street hidden-issue flags (queue item B-09, slice 4; plan L-11).

Offline and deterministic. The recorded 215-16 Northern Blvd pack (queue item B-01) is
replayed through the real connectors and B-03 site-geometry code (the way slice 3 replays
the pack); SYNTHETIC ``SiteGeometry`` rows - clearly labelled, never presented as official
data - exercise the through-lot flag, a street-center-line crossing, and an unknown lot type.
No live call is made. Every claim in the module docstring and docs/lanes/status/B.md is
checked here.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.connectors.pluto_soda import SOURCE_ID as PLUTO_SOURCE_ID
from app.profile.builder import build_property_profile
from app.profile.hidden_issue_flags import (
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    STATUS_NOT_FLAGGED,
    STATUS_OPPORTUNITY,
    FlagGroup,
    HiddenIssueFlag,
    site_shape_and_street_group,
)
from app.profile.hidden_issue_flags.site_shape_and_street import GROUP_ID, GROUP_TITLE
from app.spatial.site_geometry import (
    LABEL_TAX_MAP,
    LABEL_UNKNOWN,
    CityRecordValues,
    LotType,
    SiteGeometry,
    SourcedValue,
    derive_site_geometry_from_sources,
)
from app.spatial.site_geometry.results import (
    LOT_TYPE_CORNER,
    LOT_TYPE_INTERIOR,
    LOT_TYPE_THROUGH,
    LOT_TYPE_UNKNOWN,
    STATUS_COMPLETE,
)
from tests.spatial._northern_replay import (
    BBL,
    DCM_ENVELOPE,
    replay_dcm_page,
    replay_lot_geometry,
    replay_pluto,
)

_CLOCK = lambda: datetime(2026, 9, 30, 6, 20, tzinfo=UTC)  # noqa: E731

# The six §8a site-shape-and-street items, in plan order.
EXPECTED_ITEMS = (
    "site_shape_and_street.mapped_streets_or_widening",
    "site_shape_and_street.shallow_or_irregular",
    "site_shape_and_street.through_lot",
    "site_shape_and_street.street_wall_lineup",
    "site_shape_and_street.sloping_site",
    "site_shape_and_street.neighbors_lot_line_windows",
)

# Items that are a rule determination / survey / City Map check: ALWAYS "Check needed",
# whatever the geometry shows (this layer never decides a rule).
ALWAYS_CHECK_NEEDED = (
    "site_shape_and_street.shallow_or_irregular",
    "site_shape_and_street.street_wall_lineup",
    "site_shape_and_street.sloping_site",
    "site_shape_and_street.neighbors_lot_line_windows",
)


def benchmark_geometry() -> SiteGeometry:
    """The recorded 215-16 Northern Blvd lot through the real connectors + B-03 code."""
    return derive_site_geometry_from_sources(
        replay_lot_geometry(), [replay_dcm_page()], envelope=DCM_ENVELOPE,
        pluto_result=replay_pluto(),
    )


def benchmark_profile() -> dict:
    return build_property_profile(replay_pluto(), clock=_CLOCK)


def by_id(group: FlagGroup) -> dict[str, HiddenIssueFlag]:
    return {flag.item_id: flag for flag in group.flags}


# --- SYNTHETIC helpers (never official data) --------------------------------


def synthetic_geometry(
    *,
    kind: str = LOT_TYPE_INTERIOR,
    crossings: tuple[str, ...] = (),
    lot_depth: SourcedValue | None = None,
    reason: str | None = None,
) -> SiteGeometry:
    """A SYNTHETIC ``SiteGeometry`` built to exercise this module's reads (not official)."""
    unknown_ft = SourcedValue(None, "ft", LABEL_UNKNOWN, "SYNTHETIC", "synthetic unknown")
    unknown_area = SourcedValue(None, "sq ft", LABEL_UNKNOWN, "SYNTHETIC", "synthetic unknown")
    label = LABEL_UNKNOWN if kind == LOT_TYPE_UNKNOWN else LABEL_TAX_MAP
    streets = {
        LOT_TYPE_INTERIOR: ("A Street",),
        LOT_TYPE_CORNER: ("A Street", "B Street"),
        LOT_TYPE_THROUGH: ("A Street", "B Street"),
        LOT_TYPE_UNKNOWN: (),
    }[kind]
    lot_type = LotType(kind, label, "SYNTHETIC geometric test (not official data)", reason,
                       streets)
    return SiteGeometry(
        status=STATUS_COMPLETE,
        refusal_reason=None,
        lot_area=unknown_area,
        city_records=CityRecordValues(unknown_area, unknown_ft, unknown_ft),
        area_check=None,
        frontages=(),
        lot_type=lot_type,
        lot_depth=lot_depth if lot_depth is not None else unknown_ft,
        edges=(),
        street_crossings=tuple(crossings),
        notes=(),
        parameters={"method_version": "SYNTHETIC"},
        provenance={"method_version": "SYNTHETIC", "streets": {"source": "SYNTHETIC"}},
    )


def profile_with_zonedist(value: object, *, conflict_status: str = "none") -> dict:
    """A SYNTHETIC minimal profile recording one PLUTO zonedist1 (never official data)."""
    return {
        "identity": {"bbl": BBL},
        "provenance": [
            {
                "source_id": PLUTO_SOURCE_ID,
                "bbl": BBL,
                "original_field_name": "zonedist1",
                "normalized_value": value,
                "conflict_status": conflict_status,
                "dataset_version": "26v2",
                "retrieved_at": "2026-09-30T06:20:00Z",
                "request_url": (
                    "https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=" + BBL),
                "provenance_id": "pluto-64uk-42ks-26v2-" + BBL + "-zonedist1",
            }
        ],
    }


# ---------------------------------------------------------------------------
# Shape and order
# ---------------------------------------------------------------------------


def test_group_identity_and_six_items_in_plan_order() -> None:
    group = site_shape_and_street_group(BBL, site_geometry=benchmark_geometry())
    assert isinstance(group, FlagGroup)
    assert group.group_id == GROUP_ID == "site_shape_and_street"
    assert group.title == GROUP_TITLE == "Site shape and street"
    assert group.lot_bbl == BBL == "4073340070"
    assert tuple(f.item_id for f in group.flags) == EXPECTED_ITEMS
    assert all(f.group == GROUP_ID for f in group.flags)
    # Plan §8a: site shape and street is Phase 1 for flags.
    assert all(f.phase == "1" for f in group.flags)
    # Opportunity never applies to this group; only flag / check_needed / not_flagged.
    assert {f.status for f in group.flags} <= {
        STATUS_FLAG, STATUS_CHECK_NEEDED, STATUS_NOT_FLAGGED}
    assert STATUS_OPPORTUNITY not in {f.status for f in group.flags}


def test_no_geometry_and_no_profile_makes_every_item_check_needed() -> None:
    group = site_shape_and_street_group(BBL)
    assert tuple(f.item_id for f in group.flags) == EXPECTED_ITEMS
    # Nothing to read: every item is an honest "Check needed", never a guess.
    assert all(f.status == STATUS_CHECK_NEEDED for f in group.flags)
    assert all(f.needs_check for f in group.flags)


def test_rule_determinations_stay_check_needed_even_with_full_geometry() -> None:
    # A through lot with a street crossing still never flips items 2/4/5/6 to a flag:
    # those are rule / survey / City Map checks this layer never decides.
    geom = synthetic_geometry(kind=LOT_TYPE_THROUGH, crossings=("A Street",))
    flags = by_id(site_shape_and_street_group(BBL, site_geometry=geom,
                                              profile=profile_with_zonedist("R7B")))
    for item_id in ALWAYS_CHECK_NEEDED:
        assert flags[item_id].status == STATUS_CHECK_NEEDED


def test_never_decides_the_rule_wording_is_present() -> None:
    flags = by_id(site_shape_and_street_group(BBL, site_geometry=benchmark_geometry(),
                                              profile=benchmark_profile()))
    # Each flag either names the rule check or says a reviewer/survey must check it.
    for flag in flags.values():
        text = flag.detail.lower()
        assert ("rule check" in text or "never decides the rule" in text
                or "never guessed" in text or "reviewer" in text or "rule" in text)


# ---------------------------------------------------------------------------
# Item 1 - mapped-but-unbuilt streets or widening lines crossing the lot
# ---------------------------------------------------------------------------


def test_item1_flags_a_center_line_running_through_the_lot() -> None:
    geom = synthetic_geometry(kind=LOT_TYPE_INTERIOR, crossings=("Old Mapped Street",))
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=geom))[
        "site_shape_and_street.mapped_streets_or_widening"]
    assert flag.status == STATUS_FLAG
    assert "Old Mapped Street" in flag.detail
    assert "runs through the lot" in flag.detail
    assert "City Map" in flag.detail
    # The B-03 street provenance rides along as evidence.
    assert flag.evidence and "Old Mapped Street" in flag.evidence[0]["label"]


def test_item1_check_needed_names_the_city_map_when_no_crossing() -> None:
    # Geometry present, no crossing: NOT a silent clear (D-051) - widening lines and
    # adjacent paper streets are City Map features this layer does not read.
    geom = synthetic_geometry(kind=LOT_TYPE_INTERIOR, crossings=())
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=geom))[
        "site_shape_and_street.mapped_streets_or_widening"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "City Map" in flag.detail
    assert "does not clear the item" in flag.detail


def test_item1_check_needed_when_no_geometry() -> None:
    flag = by_id(site_shape_and_street_group(BBL))[
        "site_shape_and_street.mapped_streets_or_widening"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "City Map" in flag.detail


# ---------------------------------------------------------------------------
# Item 2 - shallow or irregular lot (yard relief) - always a rule check
# ---------------------------------------------------------------------------


def test_item2_is_a_rule_check_and_carries_a_known_depth_as_context() -> None:
    depth = SourcedValue(42.0, "ft", LABEL_TAX_MAP, "outline")
    geom = synthetic_geometry(kind=LOT_TYPE_INTERIOR, lot_depth=depth)
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=geom))[
        "site_shape_and_street.shallow_or_irregular"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "yard relief" in flag.detail
    assert "rule check" in flag.detail
    # The recorded depth is carried as context, never a decision.
    assert "42 ft" in flag.detail
    assert "survey" in flag.detail.lower()


def test_item2_without_geometry_names_the_survey_and_rule() -> None:
    flag = by_id(site_shape_and_street_group(BBL))[
        "site_shape_and_street.shallow_or_irregular"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "survey" in flag.detail.lower()
    assert "yard relief" in flag.detail


# ---------------------------------------------------------------------------
# Item 3 - through lot (the one item a recorded value answers)
# ---------------------------------------------------------------------------


def test_item3_flags_a_geometric_through_lot() -> None:
    geom = synthetic_geometry(kind=LOT_TYPE_THROUGH)
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=geom))[
        "site_shape_and_street.through_lot"]
    assert flag.status == STATUS_FLAG
    assert "through lot" in flag.detail
    assert "not a Zoning Resolution determination" in flag.detail
    assert flag.evidence and "through" in flag.evidence[0]["label"]


@pytest.mark.parametrize("kind", [LOT_TYPE_CORNER, LOT_TYPE_INTERIOR])
def test_item3_no_flag_for_a_known_non_through_lot(kind: str) -> None:
    geom = synthetic_geometry(kind=kind)
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=geom))[
        "site_shape_and_street.through_lot"]
    assert flag.status == STATUS_NOT_FLAGGED
    assert f"{kind} lot" in flag.detail
    assert "not a through lot" in flag.detail
    # A recorded "not a through lot", never the absence of data.
    assert "not an absent one" in flag.detail


def test_item3_check_needed_when_lot_type_unknown_carries_the_reason() -> None:
    geom = synthetic_geometry(kind=LOT_TYPE_UNKNOWN,
                              reason="The frontage on A Street is not straight.")
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=geom))[
        "site_shape_and_street.through_lot"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "The frontage on A Street is not straight." in flag.detail
    assert "never guessed" in flag.detail


def test_item3_check_needed_when_no_geometry() -> None:
    flag = by_id(site_shape_and_street_group(BBL))["site_shape_and_street.through_lot"]
    assert flag.status == STATUS_CHECK_NEEDED


# ---------------------------------------------------------------------------
# Item 4 - line-up with neighboring street walls (R6B, R7B, R8B)
# ---------------------------------------------------------------------------


def test_item4_is_check_needed_and_surfaces_the_recorded_district_as_context() -> None:
    flag = by_id(site_shape_and_street_group(
        BBL, profile=profile_with_zonedist("R7B")))[
        "site_shape_and_street.street_wall_lineup"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "'R7B'" in flag.detail
    assert "R6B, R7B and R8B" in flag.detail
    assert "field survey" in flag.detail
    assert flag.evidence and flag.evidence[0]["label"] == "PLUTO zonedist1"


def test_item4_omits_district_context_when_no_profile() -> None:
    flag = by_id(site_shape_and_street_group(BBL))[
        "site_shape_and_street.street_wall_lineup"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "PLUTO records the zoning district" not in flag.detail
    assert flag.evidence == ()


def test_item4_omits_district_context_for_an_untrusted_value() -> None:
    # A present-but-untrusted PLUTO value (the trust rules reject it) is never surfaced.
    flag = by_id(site_shape_and_street_group(
        BBL, profile=profile_with_zonedist("R6B", conflict_status="conflicting")))[
        "site_shape_and_street.street_wall_lineup"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "PLUTO records the zoning district" not in flag.detail
    assert flag.evidence == ()


# ---------------------------------------------------------------------------
# Items 5 and 6 - no connected source, always a check
# ---------------------------------------------------------------------------


def test_item5_sloping_site_is_always_check_needed() -> None:
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=benchmark_geometry()))[
        "site_shape_and_street.sloping_site"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "survey" in flag.detail.lower()
    assert "never guessed" in flag.detail


def test_item6_neighbors_lot_line_windows_is_always_check_needed() -> None:
    flag = by_id(site_shape_and_street_group(BBL, site_geometry=benchmark_geometry()))[
        "site_shape_and_street.neighbors_lot_line_windows"]
    assert flag.status == STATUS_CHECK_NEEDED
    assert "lot-line window" in flag.detail
    assert "field survey" in flag.detail


# ---------------------------------------------------------------------------
# Benchmark 215-16 Northern Blvd (BBL 4073340070) - recorded, replayed offline
# ---------------------------------------------------------------------------


def test_benchmark_215_16_northern() -> None:
    group = site_shape_and_street_group(
        BBL, site_geometry=benchmark_geometry(), profile=benchmark_profile())
    flags = by_id(group)

    # Item 1: no center line crosses this corner lot, so "Check needed" naming the City Map.
    item1 = flags["site_shape_and_street.mapped_streets_or_widening"]
    assert item1.status == STATUS_CHECK_NEEDED
    assert "City Map" in item1.detail

    # Item 2: shallow/irregular stays a rule check; the per-frontage depths ride as context.
    item2 = flags["site_shape_and_street.shallow_or_irregular"]
    assert item2.status == STATUS_CHECK_NEEDED
    assert "215 Place" in item2.detail
    assert "Northern Boulevard" in item2.detail

    # Item 3: the lot is geometrically a corner lot, so "No flag" for a through lot.
    item3 = flags["site_shape_and_street.through_lot"]
    assert item3.status == STATUS_NOT_FLAGGED
    assert "corner lot, not a through lot" in item3.detail

    # Item 4: the benchmark is R6B (a named contextual district); surfaced as context only.
    item4 = flags["site_shape_and_street.street_wall_lineup"]
    assert item4.status == STATUS_CHECK_NEEDED
    assert "'R6B'" in item4.detail

    # Items 5 and 6: no connected source.
    assert flags["site_shape_and_street.sloping_site"].status == STATUS_CHECK_NEEDED
    assert flags["site_shape_and_street.neighbors_lot_line_windows"].status == (
        STATUS_CHECK_NEEDED)


def test_benchmark_makes_no_live_call_through_the_recorded_pack() -> None:
    # The geometry and profile come only from the recorded pack (replay transport); building
    # the group touches no network. Re-deriving gives a byte-stable group.
    first = site_shape_and_street_group(BBL, site_geometry=benchmark_geometry())
    second = site_shape_and_street_group(BBL, site_geometry=benchmark_geometry())
    assert first.to_dict() == second.to_dict()


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("bad", ["", "40733400", "4073340070 ", "x073340070", "0073340070"])
def test_rejects_a_non_bbl(bad: str) -> None:
    with pytest.raises(ValueError, match="10-digit BBL"):
        site_shape_and_street_group(bad)


def test_rejects_a_wrong_type_site_geometry() -> None:
    with pytest.raises(ValueError, match="SiteGeometry"):
        site_shape_and_street_group(BBL, site_geometry={"not": "a geometry"})  # type: ignore[arg-type]


def test_rejects_a_wrong_type_profile() -> None:
    with pytest.raises(ValueError, match="property-profile mapping"):
        site_shape_and_street_group(BBL, profile=["not", "a", "mapping"])  # type: ignore[arg-type]


def test_rejects_a_profile_for_a_different_lot() -> None:
    other = {"identity": {"bbl": "4073340001"}, "provenance": []}
    with pytest.raises(ValueError, match="does not match bbl"):
        site_shape_and_street_group(BBL, profile=other)
