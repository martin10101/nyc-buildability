"""Web/PDF parity golden for the fitted two-zone split (M5-T202 part B2a; D-094 R088/R091/R096).

The website's fitted branch (apps/web/src/lib/architect/area-allocation.ts) ports the
kernel's ``_poly_area``/``_clip_x``/``_division_x`` so the two surfaces split the placed
footprint identically. This test writes the golden FROM the kit code (never by hand): it
reads the benchmark's own ``area_allocation.share`` and ``placement.outline`` from the
recorded fixture, de-duplicates the ring exactly as :func:`_placed_ring` does, and records
the kernel's footprint area, division x and apartment fraction. The web parity test
(area-allocation.test.ts) reads the SAME golden and asserts its TypeScript port reproduces
these values within 1e-6; editing one golden number reddens both surfaces.

Regenerate after a kernel change with ``UPDATE_GOLDEN=1`` (the golden stays the kit output).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.drawings.kit.area_allocation import (
    _clip_x,
    _division_x,
    _placed_ring,
    _poly_area,
    draw_area_allocation,
)
from app.drawings.kit.model import Unavailable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FIXTURES = REPO / "packages" / "contracts" / "fixtures" / "valid" / "results"
GOLDEN = REPO / "apps" / "web" / "src" / "test-support" / "report-parity-area-zones.json"
WEB_SELECTOR = REPO / "apps" / "web" / "src" / "lib" / "architect" / "area-allocation.ts"
BENCHMARK = "recorded_215_16_northern_journey"


def _benchmark_blocks() -> tuple[dict, dict]:
    """ONLY the first worked building's ``area_allocation`` and ``placement`` blocks."""
    doc = json.loads((FIXTURES / f"{BENCHMARK}.json").read_text(encoding="utf-8"))
    alt = doc["building_alternatives"][0]
    return alt["area_allocation"], alt["placement"]


def _compute_golden() -> dict:
    allocation, placement = _benchmark_blocks()
    share = float(allocation["share"])
    ring = _placed_ring(placement)
    assert isinstance(ring, list), "the benchmark footprint must be a drawable ring"
    total = _poly_area(ring)
    c = _division_x(ring, share)
    apartment_fraction = _poly_area(_clip_x(ring, c, keep_left=True)) / total
    return {
        "benchmark": {
            "fixture": BENCHMARK,
            "share": share,
            "ring": [[x, y] for (x, y) in ring],
            "footprint_area": total,
            "division_x": c,
            "apartment_fraction": apartment_fraction,
        }
    }


def test_web_parity_area_zones_golden_matches_kernel() -> None:
    computed = _compute_golden()
    if os.environ.get("UPDATE_GOLDEN") == "1":
        GOLDEN.write_text(json.dumps(computed, indent=2) + "\n", encoding="utf-8")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert golden == computed, (
        "golden drifted from the kit code; regenerate with UPDATE_GOLDEN=1:\n"
        + json.dumps(computed, indent=2)
    )


def _valid_fitted_allocation() -> dict:
    allocation, _ = _benchmark_blocks()
    return dict(allocation)


def test_outline_refusal_reasons_are_byte_equal_to_the_web_selector() -> None:
    """Every reason the kernel refuses a fitted footprint with must appear verbatim in the web
    selector, so the two surfaces explain a refusal in the same words (S2; D-094 R096). The
    reasons are READ from the kernel (never hand-typed), then matched against the TS source."""
    reasons: dict[str, str] = {}

    # the four placed-outline refusals (F1/F2/F3), read from the kernel.
    for name, outline in (
        ("too_many", [[[0.0, float(i)] for i in range(1001)]]),
        ("not_points", [[[0.0, 0.0], [10.0, 0.0], [10.0], [0.0, 10.0]]]),
        ("out_of_range", [[[0.0, 0.0], [10.0, 0.0], [10.0, float("nan")], [0.0, 10.0]]]),
        ("no_area", [[[0.0, 0.0], [40.0, 0.0], [80.0, 0.0], [0.0, 0.0]]]),
    ):
        result = _placed_ring({"status": "placed", "outline": outline})
        assert isinstance(result, Unavailable), name
        reasons[name] = result.reason

    # the not-placed refusal, read from the public entry point with a valid fitted block.
    not_placed = draw_area_allocation(_valid_fitted_allocation(), placement={"status": "withheld"})
    assert isinstance(not_placed, Unavailable)
    reasons["not_placed"] = not_placed.reason

    # distinct reasons, and each appears as a verbatim string literal in the web selector.
    assert len(set(reasons.values())) == 5, reasons
    source = WEB_SELECTOR.read_text(encoding="utf-8")
    for name, reason in reasons.items():
        assert f'"{reason}"' in source, f"web selector missing the {name} reason: {reason!r}"


def test_benchmark_golden_is_the_fitted_60_percent_split() -> None:
    """The benchmark is the share-0.60 / 100.76 x 66.66 footprint the audit cites."""
    allocation, placement = _benchmark_blocks()
    assert allocation["share"] == 0.6
    assert allocation["apartment_area_sqft"] == 12090.0
    assert allocation["other_area_sqft"] == 8060.0
    assert allocation["total_sqft"] == 20150.0
    assert allocation["fitted"] is True
    ring = _placed_ring(placement)
    assert isinstance(ring, list)
    xs = [p[0] for p in ring]
    ys = [p[1] for p in ring]
    assert max(xs) - min(xs) == 100.76
    assert max(ys) - min(ys) == 66.66
    # the division sits at share * width and the apartment zone is 60% of the footprint.
    c = _division_x(ring, 0.6)
    assert abs(c - 0.6 * 100.76) <= 1e-6
    frac = _poly_area(_clip_x(ring, c, keep_left=True)) / _poly_area(ring)
    assert abs(frac - 0.6) <= 1e-6
