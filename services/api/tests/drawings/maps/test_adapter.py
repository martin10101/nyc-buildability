"""The map-context adapter fails closed (task E-07, plan section 5c).

A context that is malformed, carries an unsupported CRS, or whose geometry
cannot be drawn truthfully raises :class:`MapInputError`; nothing partial is
drawn. A layer the data marks ``not_available`` is not an error - the map
returns :class:`Unavailable` with the data's own reason. The maps draw nothing
while the Lane E flag is off.
"""

from __future__ import annotations

import copy

import pytest

from app.drawings.maps import (
    DrawingKitDisabled,
    MapInputError,
    Unavailable,
    load_map_context,
    render_location_map,
    render_zoning_map,
)

from .maps_support import ENV_ON, FIXTURES, load

BASE = load(FIXTURES / "synthetic_midblock_split_lot.json")


def _doc() -> dict:
    return copy.deepcopy(BASE)


def test_flag_off_draws_nothing():
    with pytest.raises(DrawingKitDisabled):
        render_zoning_map(_doc())
    with pytest.raises(DrawingKitDisabled):
        render_location_map(_doc(), env={})


def test_valid_context_loads():
    context = load_map_context(_doc())
    assert context.crs == "EPSG:2263"
    assert context.subject_lot.bbl == "1000477501"
    assert len(context.zoning.districts) == 2
    assert context.zoning.use_limitation.text.startswith("These features are not intended")


@pytest.mark.parametrize("crs", ["local_feet", "EPSG:4326", "4326", "", None])
def test_unsupported_crs_fails_closed(crs):
    doc = _doc()
    doc["map_context"]["crs"] = crs
    with pytest.raises(MapInputError) as exc:
        load_map_context(doc)
    assert exc.value.code == "unsupported_crs"


def test_open_ring_fails_closed():
    doc = _doc()
    doc["map_context"]["subject_lot"]["outline"][0][-1] = [987180, 200161]  # not closed
    with pytest.raises(MapInputError) as exc:
        load_map_context(doc)
    assert exc.value.code == "ring_not_closed"


def test_coordinate_out_of_range_fails_closed():
    doc = _doc()
    doc["map_context"]["zoning_districts"]["entries"][0]["outline"][0][0] = [1e9, 200000]
    with pytest.raises(MapInputError) as exc:
        load_map_context(doc)
    assert exc.value.code == "coordinate_out_of_range"


def test_self_crossing_ring_fails_closed():
    doc = _doc()
    # A bow-tie: swap two vertices so the outline crosses itself.
    doc["map_context"]["subject_lot"]["outline"][0] = [
        [987180, 200160], [987260, 200260], [987260, 200160], [987180, 200260], [987180, 200160]
    ]
    with pytest.raises(MapInputError) as exc:
        load_map_context(doc)
    assert exc.value.code == "ring_not_simple"


def test_too_many_features_fails_closed():
    doc = _doc()
    one = doc["map_context"]["building_footprints"]["entries"][0]
    doc["map_context"]["building_footprints"]["entries"] = [copy.deepcopy(one) for _ in range(2001)]
    with pytest.raises(MapInputError) as exc:
        load_map_context(doc)
    assert exc.value.code == "too_many_features"


def test_control_character_in_label_fails_closed():
    doc = _doc()
    doc["map_context"]["zoning_districts"]["entries"][0]["zonedist"] = "R6\x07"
    with pytest.raises(MapInputError) as exc:
        load_map_context(doc)
    assert exc.value.code == "invalid_text"


def test_missing_measurement_block_fails_closed():
    doc = _doc()
    del doc["map_context"]["measurement"]
    with pytest.raises(MapInputError) as exc:
        load_map_context(doc)
    assert exc.value.code == "missing_block"


def test_buildings_not_available_returns_unavailable():
    doc = load(FIXTURES / "synthetic_buildings_unavailable.json")
    result = render_location_map(doc, env=ENV_ON)
    assert isinstance(result, Unavailable)
    assert result.drawing == "location_map"
    assert result.reason.startswith("Building footprints could not be retrieved")
    assert result.reason_kind == "source_unavailable"
    # the other map still draws
    from app.drawings.maps import Drawing

    assert isinstance(render_zoning_map(doc, env=ENV_ON), Drawing)


def test_zoning_not_available_returns_unavailable():
    doc = load(FIXTURES / "synthetic_zoning_unavailable.json")
    result = render_zoning_map(doc, env=ENV_ON)
    assert isinstance(result, Unavailable)
    assert result.drawing == "zoning_map"
    assert result.reason.startswith("Zoning-district features could not be retrieved")
