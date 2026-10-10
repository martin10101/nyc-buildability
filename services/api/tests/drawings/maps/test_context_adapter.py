"""The map-context adapter validates the optional 1.1.0 layers fail-closed
(M5-T155): a malformed window, a non-finite or out-of-range coordinate, an open
or degenerate ring, or a street with fewer than two points raises
:class:`MapInputError`; a 1.0.0 document loads with the new members absent."""

from __future__ import annotations

import copy

import pytest

from app.drawings.maps.adapter import load_map_context
from app.drawings.maps.errors import MapInputError
from app.drawings.maps.model import (
    ContextWindow,
    LayerUnavailable,
    StreetLayer,
    TaxLotLayer,
)

from .context_support import benchmark_document, legacy_1_0_0_document


def _ctx(doc):
    return load_map_context(doc)


def test_valid_1_1_0_document_populates_the_new_layers():
    ctx = _ctx(benchmark_document())
    assert isinstance(ctx.context_window, ContextWindow)
    assert isinstance(ctx.tax_lots, TaxLotLayer)
    assert isinstance(ctx.streets, StreetLayer)
    # the subject is never counted as a neighbour
    assert all(lot.bbl != "4073340070" for lot in ctx.tax_lots.lots)
    # a plain-number width becomes a number; the window is finite and non-empty
    northern = next(s for s in ctx.streets.streets if s.name == "Northern Boulevard")
    assert northern.mapped_width_ft == 100.0 and northern.width_text == "100"
    assert ctx.streets.window.xmax > ctx.streets.window.xmin


def test_a_1_0_0_document_loads_with_the_new_members_absent():
    ctx = _ctx(legacy_1_0_0_document())
    assert ctx.context_window is None
    assert ctx.tax_lots is None
    assert ctx.streets is None


def test_mapped_width_is_none_for_non_numeric_width_text():
    doc = benchmark_document()
    doc["map_context"]["streets"]["entries"][0]["width_text"] = "60-75"
    doc["map_context"]["streets"]["entries"][0]["mapped_width_ft"] = None
    ctx = _ctx(doc)
    first = ctx.streets.streets[0]
    assert first.width_text == "60-75" and first.mapped_width_ft is None


def test_not_available_layers_become_layer_unavailable():
    doc = benchmark_document()
    for layer in ("tax_lots", "streets"):
        doc["map_context"][layer] = {
            "status": "not_available", "reason": "down", "reason_kind": "source_unavailable"}
    ctx = _ctx(doc)
    assert isinstance(ctx.tax_lots, LayerUnavailable)
    assert isinstance(ctx.streets, LayerUnavailable)


def test_empty_window_is_refused():
    doc = benchmark_document()
    win = doc["map_context"]["context_window"]
    win["xmax"] = win["xmin"]  # zero width
    with pytest.raises(MapInputError):
        _ctx(doc)


def test_non_finite_coordinate_in_a_tax_lot_is_refused():
    doc = benchmark_document()
    doc["map_context"]["tax_lots"]["entries"][0]["outline"][0][0][0] = float("inf")
    with pytest.raises(MapInputError):
        _ctx(doc)


def test_a_street_path_with_one_point_is_refused():
    doc = benchmark_document()
    doc["map_context"]["streets"]["entries"][0]["paths"] = [[[1048700.0, 216200.0]]]
    with pytest.raises(MapInputError):
        _ctx(doc)


def test_an_open_tax_lot_ring_is_refused():
    doc = benchmark_document()
    ring = doc["map_context"]["tax_lots"]["entries"][0]["outline"][0]
    ring[-1] = [ring[-1][0] + 5.0, ring[-1][1]]  # break closure
    with pytest.raises(MapInputError):
        _ctx(doc)


def test_out_of_range_window_coordinate_is_refused():
    doc = copy.deepcopy(benchmark_document())
    doc["map_context"]["context_window"]["xmax"] = 1.0e9  # beyond MAX_ABS_COORD_FT
    with pytest.raises(MapInputError):
        _ctx(doc)
