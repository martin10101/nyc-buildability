"""M5-T179: the appendix scope note (page 7) and printed context maps.

D-094 R137 (owner review 2026-10-14): page 7 still lists 'Context maps' under
'Not yet in this report' even when the report prints its maps. The builder already
computes ``maps_present`` (true when the surroundings' maps rendered) and passes it
to page 1; this proves it now also reaches the appendix scope note, so 'Context
maps' is dropped from the exclusions exactly when the report shows them, and nothing
else changes.

Every expected name is READ from ``coverage.coverage_groups`` (the source of truth),
never retyped. The scenarios run through ``build_report_html`` so the builder's
pass-through is exercised (S4: reverting it makes S1 fail).
"""

from __future__ import annotations

import html as _html
import json
from pathlib import Path

import pytest

from app.drawings.report import build_report_html, coverage

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)
_WINDOW_PACK = (
    Path(__file__).resolve().parents[2] / "fixtures" / "benchmark_215_16_northern_window"
)
_LANE_E = {"LANE_E_ENABLED": "1"}


def _load(name: str) -> dict:
    return json.loads((_FIXTURES / f"{name}.json").read_text("utf-8"))


def benchmark() -> dict:
    return _load("recorded_215_16_northern_journey")


def _benchmark_map_context() -> dict:
    """The recorded 215-16 Northern WINDOW map document (as test_report_pages.py
    builds it): its subject outline matches the benchmark lot, so the maps render."""
    from app.api.v1.report_context import recorded_pack_provider

    doc = recorded_pack_provider(_WINDOW_PACK)("4073340070", "q3")
    assert doc is not None
    return doc


def _scope_note_names(html: str) -> list[str]:
    """The ordered names listed under 'Not yet in this report:' in the appendix
    scope note (page 7), read straight from the rendered report HTML."""
    section = html[html.index('id="assumptions-open-items"'):]
    section = section[: section.index("</section>")]
    marker = "<strong>Not yet in this report:</strong> "
    start = section.index(marker) + len(marker)
    inner = section[start: section.index("</p>", start)]
    return [_html.unescape(part) for part in inner.split("; ")]


# =========================================================================== S1
def test_s1_scope_note_drops_context_maps_when_maps_are_printed() -> None:
    doc = benchmark()
    html = build_report_html(doc, map_context=_benchmark_map_context(), env=_LANE_E)
    names = _scope_note_names(html)

    # the builder reported maps_present True to the appendix: 'Context maps' is gone.
    assert "Context maps" not in names
    # the scope note names exactly the 'Not yet' coverage group for maps_present True,
    # in the same order and words (source of truth, not retyped).
    expected = dict(coverage.coverage_groups(doc, maps_present=True))["Not yet"]
    assert "Context maps" not in expected
    assert names == expected

    # every other listed name stays, in the same order: the only difference from the
    # no-maps note is the removal of 'Context maps' at the end.
    no_maps_names = _scope_note_names(build_report_html(doc))
    assert "Context maps" in no_maps_names
    assert names == [n for n in no_maps_names if n != "Context maps"]


# =========================================================================== S2
@pytest.mark.parametrize("fixture", sorted(p.stem for p in _FIXTURES.glob("*.json")))
def test_s2_scope_note_keeps_context_maps_without_a_map_context(fixture: str) -> None:
    doc = _load(fixture)
    html = build_report_html(doc)
    names = _scope_note_names(html)
    # no map context -> maps_present defaults False -> 'Context maps' still excluded,
    # exactly as at the claim head (byte-identity of the whole report proven in the
    # producer report by a script over every valid fixture).
    assert "Context maps" in names
    assert names == dict(coverage.coverage_groups(doc, maps_present=False))["Not yet"]


# =========================================================================== S3
def test_s3_benchmark_scope_note_difference_is_only_context_maps() -> None:
    doc = benchmark()
    without = _scope_note_names(build_report_html(doc))
    with_maps = _scope_note_names(
        build_report_html(doc, map_context=_benchmark_map_context(), env=_LANE_E)
    )
    removed = [n for n in without if n not in with_maps]
    added = [n for n in with_maps if n not in without]
    assert removed == ["Context maps"]
    assert added == []
