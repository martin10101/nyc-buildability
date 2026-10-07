# M5-T127 producer report — the lot-reach measurements

Producer: geospatial-engineer (isolated worktree). Scope: the work order's Part 0 first new
file. Base/contract head reset to `cc30ab1884cdb6541c41f0d759ebe198f91a6f46`.

Files written (only the three allowed paths):
- `services/api/app/spatial/lot_reach.py` (replaces the seeded placeholder) — 240 lines.
- `services/api/tests/spatial/test_lot_reach.py` (replaces the seeded placeholder).
- `project-control/reports/M5-T127-producer-report.md` (this file).

## The interface

One pure, deterministic function and its result record. No I/O, no flag, no law, no caller.

```
measure_lot_reach(outline: PreparedOutline | None, geometry: SiteGeometry) -> LotReach
```

Inputs — what single-lot site geometry already derives, read only:
- `outline`: the prepared tax-map outline in EPSG:2263 feet (`app.spatial.site_geometry.outline`);
  `None` when the lot outline was refused.
- `geometry`: the derived `SiteGeometry` — its confirmed `frontages` and the corner relation
  in `lot_type.relations`.

Result record `LotReach`:
- `street_lines: tuple[StreetLineReach, ...]` — one per street frontage. `StreetLineReach` =
  `street_key`, `street_name`, `reach` (a `SourcedValue` in ft: the farthest perpendicular
  distance of any point of the outline from that frontage's street line).
- `corner: CornerReach` — always present. `CornerReach` = `first_street`, `second_street`,
  `angle` (`SourcedValue` in degrees, carried from the site-geometry corner relation),
  `corner_point` (`(x, y)` in EPSG:2263 feet where the two street lines cross, else `None`),
  `reach` (`SourcedValue` in ft: the farthest straight-line distance of any point of the
  outline from `corner_point`).

Every value is a site_geometry `SourcedValue`: a tax-map measurement
(`LABEL_TAX_MAP`, rounded to 0.01 ft) with its basis in plain words, or unknown (`value` is
`None`, `LABEL_UNKNOWN`) with a plain reason — never a zero, never a default.

## Each measurement beside its reference value

Expected numbers are PARSED in the test from the corner-reach reference case rows through the
loader `r6b_reference_cases_lib.load_row(...)` — never retyped, never read back from the module.
Tolerance: **0.01 ft** for every reach; both the reference row and the module quote feet to two
decimals, so 0.01 ft is the shared rounding unit, and a reach taken along the wrong axis or from
the wrong corner is wrong by whole feet (see the mutation proof). Angle tolerance for the made-up
rectangles: **0.1 degrees** (the 90-degree corner is a property of the right-angle rectangle
built in the test, not a reference reach value).

Measured values (observed in the self-check; all within tolerance):

| Case (row) | reach from street A / Northern | reach from street B / 215 Place | farthest from corner |
|---|---|---|---|
| real lot (`real-lot-reach`) | Northern 99.97 ft (ref 99.97) | 215 Place 103.93 ft (ref 103.93) | 144.60 ft (ref 144.60) |
| C1 40×100 (`C1-reach`) | A 100.00 ft (ref 100.00) | B 40.00 ft (ref 40.00) | 107.70 ft (ref 107.70) |
| C2 60×80 (`C2-reach`) | A 80.00 ft (ref 80.00) | B 60.00 ft (ref 60.00) | 100.00 ft (ref 100.00) |
| C3 150×100 (`C3-reach`) | A 100.00 ft (ref 100.00) | B 150.00 ft (ref 150.00) | 180.28 ft (ref 180.28) |

Real-lot corner angle = 89.7° (carried from the site-geometry corner relation, which the
benchmark pins at 89.7°); made-up rectangles = 90.0°. The reference reach rows state no angle
number, so no angle is asserted against a reference number: the real lot asserts the module
carries the relation's angle, the rectangles assert the constructed right angle.

Measured values match the reference to 0.01 ft (observed difference 0.00 ft on every row). No row
differed by more than the tolerance; nothing was adjusted.

## When each value is unknown (S3)

Verified by tests, each leaving the value `None` with a plain reason and `LABEL_UNKNOWN`, never a
zero or default:
- **No / refused outline** (`outline is None` or `geometry.status == refused`): `street_lines`
  is empty; the corner angle, point and reach are all unknown with the refusal reason.
- **Uncertain frontage**: that street's reach is unknown ("the frontage on X is not confirmed,
  so its street line is not settled").
- **Frontage that is not straight** (bends beyond the site-geometry `SINGLE_STREET_MAX_BEND_DEG`
  = 15°): that street's reach is unknown ("not straight … no single street line to measure from").
- **Interior lot (one confirmed street)**: the one reach is given; the corner is unknown ("only
  … has a confirmed, straight frontage, so there is no corner point").
- **Through lot (two opposite streets)**: both reaches are given; the corner is unknown ("… front
  the lot but do not meet at a corner").
- **More than two confirmed streets**: the corner is unknown ("more than two streets front the
  lot, so no single corner point is measured").

## Measurements only, no law (S4)

A test reads the module source and asserts it contains no `100`/`135` constant and no `coverage`
or `yard`, and imports nothing from `app.rules` / `app.scenario`. A second test walks every `.py`
under `services/api/app` and asserts nothing imports `lot_reach` yet.

## Modularity answers (code-architecture.md / CODE_MODULARITY_POLICY.md)

1. Owning responsibility: the reach of a lot from its street lines and its corner — a measurement.
2. Module boundary: a new file `services/api/app/spatial/lot_reach.py`, beside the
   `site_geometry` package it consumes read-only.
3. Size: 240 lines — well under the 600-line warning threshold; `modularity_check --check` lists
   no signal for it.
4. Nothing extracted or moved; no existing file changed; no new package.
5. Public interface: one function `measure_lot_reach` and the result record `LotReach` (with the
   nested `StreetLineReach` and `CornerReach`), exported via `__all__`.
6. Focused test: `services/api/tests/spatial/test_lot_reach.py` (scenarios S1–S5).
7. No persistence, serialization, external I/O, API/CLI wiring or presentation in the module.

## Checks — each with its DIRECT exit code

Run with `/root/project/lanes-runtime/venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, pytest
`-p no:cacheprovider`, from `services/api` (d from the repo root). The full api suite was NOT run
(the orchestrator runs it once at the wave's final candidate).

- (a) `python -m ruff check .` → **EXIT 0** ("All checks passed!"). One E501 on a comment line
  was fixed, then clean.
- (b) `python -m pytest -q -p no:cacheprovider tests/spatial/test_lot_reach.py` → **EXIT 0**
  (12 passed).
- (c) `python -m pytest -q -p no:cacheprovider tests/spatial tests/rules/reference_cases` →
  **EXIT 0** (447 passed in 11.91s).
- (d) `python3 tools/modularity_check.py --check` → **EXIT 0** (716 files; failures 0; 29 warnings,
  none for `lot_reach.py`). `python3 scripts/lanes/check_lane_paths.py --coverage` → **EXIT 0**
  ("LANE COVERAGE PASS: 8920 file(s), each owned by exactly one lane.").
- (e) Mutation proof (temporary copy outside the repository,
  `scratchpad/mutant/services/api/app/spatial/lot_reach.py`): `_farthest_perpendicular` changed to
  take the distance along the wrong (along-street) axis, then the real test file run against the
  injected mutant → **EXIT 1**: 7 reach assertions failed and each named its row, e.g.
  `real-lot-reach: reach from the Northern Boulevard street line -- measured 104.47, reference
  99.97` and the `C1/C2/C3-reach` rows; the unknown-stays-unknown and no-law tests still passed.
  The committed module is unchanged.

## Doubt / notes

- The angle is carried from the site-geometry corner relation (the task's listed input "the
  relation between two frontage streets"); the corner point and both reaches are measured fresh
  from the prepared outline. The reference reach rows carry no angle number, so the angle is not
  checked against a reference number.
- The reference case labels the real lot's corner vertex "P2"; `prepare_outline` re-orients and
  re-indexes the ring, so the same geometric corner is the prepared outline's vertex 3. The
  measured corner reach (144.60 ft) matches the reference, so the labels differ but the geometry
  agrees.
