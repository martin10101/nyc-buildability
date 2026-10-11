"""The special density area read from the city's record (ZR 12-10; task M5-T157, DB-231).

One test per input state of the pure fold rule. Expected decisions come from the ZR 12-10
definitions and the PLUTO community-district coding (fixture F08), never from a program run; the
law digests are checked against the committed snapshots so the module's cited capture cannot drift.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.scenario.three_answers.special_density_geography import (
    MANHATTAN_CORE,
    SPECIAL_DENSITY_AREAS,
    SPECIAL_DOWNTOWN_BROOKLYN_DISTRICT,
    SpecialDensityArea,
    SpecialDensityInputs,
    decide_special_density,
)

_SNAPSHOTS = Path(__file__).resolve().parents[3] / "app" / "_zr_snapshots" / "v1"


def _inputs(
    *,
    cd: int | None = None,
    borocode: int | None = None,
    tokens: tuple[str, ...] = (),
    all_read: bool = True,
) -> SpecialDensityInputs:
    return SpecialDensityInputs(
        community_district=cd,
        borough_code=borocode,
        special_district_tokens=tokens,
        all_special_district_columns_read=all_read,
    )


def _area(**kw) -> SpecialDensityArea:
    return decide_special_density(_inputs(**kw)).area


IN = SpecialDensityArea.IN_SPECIAL_DENSITY_AREA
NOT_IN = SpecialDensityArea.NOT_IN_SPECIAL_DENSITY_AREA
NOT_KNOWN = SpecialDensityArea.NOT_KNOWN


# --------------------------------------------------------------------------- Manhattan Core IN
def test_cd_101_manhattan_core_is_in() -> None:
    # Manhattan Community District 1 (code 101), borough code 1: in the Manhattan Core (ZR 12-10).
    assert _area(cd=101, borocode=1) is IN


def test_cd_108_manhattan_core_is_in() -> None:
    # Manhattan Community District 8 (code 108), the top of the Manhattan Core range.
    assert _area(cd=108, borocode=1) is IN


def test_manhattan_core_is_in_even_when_special_district_columns_not_read() -> None:
    # "Manhattan cd 105 spdist not read = IN": a Manhattan Core community district alone is enough;
    # the special-district columns being unread does not withhold the IN signal.
    assert _area(cd=105, borocode=1, tokens=(), all_read=False) is IN


def test_manhattan_core_is_in_when_borough_code_not_read() -> None:
    # Either IN signal alone is enough; a Manhattan Core code with no borough code is still IN (not
    # a contradiction - the borough code is simply not read).
    assert _area(cd=103, borocode=None) is IN


# --------------------------------------------------------------------------- Manhattan not-core
def test_cd_109_manhattan_outside_core_is_not_in() -> None:
    # Manhattan Community District 9 (code 109): a recognised community district outside 1-8, and no
    # special district recorded, so not in a special density area.
    assert _area(cd=109, borocode=1) is NOT_IN


def test_cd_112_manhattan_outside_core_is_not_in() -> None:
    # Manhattan Community District 12 (code 112): outside the Manhattan Core; not in one.
    assert _area(cd=112, borocode=1) is NOT_IN


def test_marble_hill_cd_207_is_not_in() -> None:
    # Marble Hill (legally Manhattan, borough code 1) is numbered in community districts 207/208
    # (serviced by the Bronx), which are not Manhattan Community Districts 1-8: not in the core.
    assert _area(cd=207, borocode=1) is NOT_IN


def test_queens_benchmark_cd_411_is_not_in() -> None:
    # The 215-16 Northern benchmark: Queens community district 11 (code 411), borough code 4, no
    # special district. Not in a special density area (step-p3 manhattan-core / downtown-brooklyn).
    assert _area(cd=411, borocode=4) is NOT_IN


# --------------------------------------------------------------------------- Downtown Brooklyn IN
def test_special_district_db_token_is_in() -> None:
    # A recorded "DB" special purpose district: the Special Downtown Brooklyn District (ZR 12-10).
    assert _area(cd=302, borocode=3, tokens=("DB",)) is IN


def test_special_district_db_token_overrides_an_unknown_community_district() -> None:
    # Either IN signal alone is enough: "DB" recorded means IN even when the community district is
    # not usable for the Manhattan Core test.
    assert _area(cd=None, borocode=None, tokens=("DB",)) is IN


def test_split_special_district_value_xx_slash_db_is_in() -> None:
    # A split value such as "XX/DB" (the caller splits on "/") carries the "DB" token, so IN.
    assert _area(cd=302, borocode=3, tokens=("XX", "DB")) is IN


def test_brooklyn_without_db_is_not_in() -> None:
    # A Brooklyn lot (community district 302), every special-district column read with no "DB":
    # outside the Manhattan Core and not the Special Downtown Brooklyn District, so not in one.
    assert _area(cd=302, borocode=3, tokens=()) is NOT_IN


def test_brooklyn_with_a_non_db_special_district_is_not_in() -> None:
    # A Brooklyn lot in some other special purpose district (not "DB"): still not a special density
    # area (the Special Downtown Brooklyn District is the only Brooklyn special density area).
    assert _area(cd=302, borocode=3, tokens=("MX",)) is NOT_IN


# --------------------------------------------------------------------------- NOT KNOWN states
def test_special_district_columns_not_read_is_not_known() -> None:
    # The lot is outside the Manhattan Core, but a special-district column was not read: "none DB"
    # cannot be trusted, so not known (a column that was not read is never read as "no").
    assert _area(cd=411, borocode=4, tokens=(), all_read=False) is NOT_KNOWN


def test_community_district_served_empty_is_not_known() -> None:
    # The community district was not read (served empty), so the Manhattan Core question cannot be
    # answered and no "DB" is recorded: not known.
    assert _area(cd=None, borocode=4, tokens=()) is NOT_KNOWN


def test_cd_164_joint_interest_area_is_not_known() -> None:
    # Code 164 is Central Park, a joint interest area, not a community district (F08), so the
    # Manhattan Core question cannot be answered from it: not known.
    assert _area(cd=164, borocode=1) is NOT_KNOWN


def test_contradiction_cd_105_borocode_3_is_not_known() -> None:
    # A Manhattan Core code (105) with a Brooklyn borough code (3) is a contradiction in the record:
    # not known, never read as in one.
    assert _area(cd=105, borocode=3) is NOT_KNOWN


def test_unrecognised_cd_value_is_not_known() -> None:
    # A value that is not a recognised community-district code (e.g. 999) cannot answer it.
    assert _area(cd=999, borocode=None) is NOT_KNOWN


def test_nothing_read_is_not_known() -> None:
    # No community district, no borough code, no special district read: not known.
    assert _area(cd=None, borocode=None, tokens=(), all_read=False) is NOT_KNOWN


# --------------------------------------------------------------------------- the law digests pin
@pytest.mark.parametrize(
    "capture",
    [SPECIAL_DENSITY_AREAS, MANHATTAN_CORE, SPECIAL_DOWNTOWN_BROOKLYN_DISTRICT],
)
def test_each_law_capture_digest_matches_the_committed_snapshot(capture) -> None:
    snapshot = json.loads(
        (_SNAPSHOTS / f"{capture.capture_snapshot_id}.snapshot.json").read_text("utf-8")
    )
    assert capture.capture_content_digest == snapshot["content_digest_sha256"]
    assert capture.captured_words == snapshot["verbatim_excerpt"]
