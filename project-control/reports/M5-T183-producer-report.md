# M5-T183 producer report — area-illustration drawing kernel (both states)

Builder: backend-engineer. Claim head: `dc3a2276653ee17542ba626bcd925a065963f62b`
(`task/wave26-envelope-constraints`). Worktree:
`/root/project/nyc-buildability/.claude/worktrees/wf_41dbdf50-89f-2`.

## What changed (only the packet's allowed paths)

- `services/api/app/drawings/kit/area_allocation.py` — new leaf kit kernel
  `draw_area_allocation(allocation, *, placement=None, caption=True) -> Drawing | Unavailable`.
  Imports only the kit's own `model`, `presentation_tokens` and `svg` helpers — nothing from
  `drawings/report` or `drawings/maps` (layering). Two states:
  - NOT fitted (`fitted is False`) → a proportional horizontal bar split by the apartment share,
    beside the building diagram, no zone inside any outline.
  - FITTED (`fitted is True` AND `placement.status == "placed"` with an outline) → two zones inside
    `outline[0]`, split by ONE vertical division placed so the area to its left equals the share
    (Sutherland–Hodgman half-plane clip + deterministic bisection; truthful for any simple outline,
    exact for the 82×82 fixture ring). No bar.
  - FITTED without a placed outline → `Unavailable` (`not_placed`); never a bar mislabelled fitted.
  Labels/caption are the `presentation_tokens.WORDING` strings verbatim (em dash, no trailing
  period). ONE stated percentage `round(share*100)` printed from the block. Both zones carry ONE
  neutral fill and are told apart by hatch (two local `<pattern>` families at 45°/135°, mirroring
  `kit/hatches.py`; the shared style table carries no apartment/other kind and is not this task's to
  edit). Every label 9.5 pt (`TYPE["drawing-label"]["print_pt_preferred"]`, ≥ 8.5 pt — never the
  8.0 pt `TYPOGRAPHY.label_pt` nor the 7.5 pt scale-bar size). Fail-closed on a missing/garbled
  block, a non-finite or out-of-range share, an inconsistent split, or a fitted-without-outline.
- `services/api/tests/drawings/kit/test_area_allocation_drawing.py` — new dedicated test (28 tests):
  renders the two committed synthetic 1.5.0 fixtures reading ONLY their `area_allocation` and
  `placement` blocks, pins two byte-stable snapshots, and drives every state and refusal from small
  literal blocks (S1–S9).
- `services/api/tests/drawings/kit/snapshots/synthetic_placed_building_contract_1_5_0.area_allocation.svg`
  — new snapshot (fitted, zones, share 0.70).
- `services/api/tests/drawings/kit/snapshots/synthetic_rear_yard_constraints_contract_1_5_0.area_allocation.svg`
  — new snapshot (not fitted, bar, share 0.65).
- `project-control/reports/M5-T183-producer-report.md` — this report.

No report wiring, no `kit/__init__.py` export, no website, no benchmark edit, no section legal lines,
no engine/schema/register/evidence-record edit (those are Part B / M5-T174 / M5-T172).

## Three rules for result-deciding code

1. **No default stands for a fact.** Every optional fact is tested explicitly; no truthiness test
   stands in for a value. The explicit tests (all in `_validate` / `_placed_ring` /
   `draw_area_allocation`):
   - `isinstance(allocation, Mapping)` (not truthiness) → else `Unavailable`.
   - `label`/`measure`/`conversion_statement` compared byte-equal to the schema consts → else
     `Unavailable` (garbled). The block's OWN values are printed; the consts are used only to refuse,
     never to substitute.
   - `share`: `_finite_number(share)` (int/float, not bool, `math.isfinite`) and range `0.60–0.75` →
     else `Unavailable`.
   - `apartment/other/total`: each `_finite_number`; `total > 0`; `|apartment+other−total| ≤ 0.01`;
     `|apartment/total − share| ≤ 0.005` → else `Unavailable`.
   - `fitted is True` / `fitted is False` explicitly; anything else (missing/non-bool) →
     `Unavailable` (never treated as False).
   - `placement`: `isinstance(placement, Mapping)` AND `status == "placed"` AND an outline that is a
     non-empty, non-string sequence whose `[0]` is a ring of ≥ 3 points → else, for a fitted block,
     `Unavailable`.
2. **One test per input state** (table below).
3. **Returned texts are user texts.** The `Unavailable.reason` strings are plain words with no
   record/task ids, no field names, no "reference case"/"the caller". A dedicated test
   (`test_s8_reasons_are_plain_words_no_internal_names`) asserts the reasons carry none of
   `area_allocation`, `fitted`, `sqft`, `placement`, `outline`, `/`, `_`.

## Input-state table (input, state, outcome, test that pins it)

| input | state | outcome | test |
|---|---|---|---|
| `allocation` | `None` / not a Mapping | Unavailable (missing_input) | `test_s8_unavailable_paths` |
| `allocation` | `{}` / label/measure/conversion not the const | Unavailable (schema_invalid) | `test_s8_unavailable_paths`, `_reasons_are_plain_words` |
| `share` | missing / non-number / NaN | Unavailable (schema_invalid) | `test_s8_unavailable_paths` |
| `share` | < 0.60 or > 0.75 | Unavailable (schema_invalid) | `test_s8_unavailable_paths` |
| `apartment+other` | ≠ total (> 0.01) | Unavailable (inconsistent) | `test_s3_inconsistent_split` |
| `apartment/total` | ≠ share (> 0.005) | Unavailable (inconsistent) | `test_s3_inconsistent_split` |
| `fitted` | not a bool (missing/"yes") | Unavailable (schema_invalid) | `test_s8_unavailable_paths` |
| `fitted=False` | (any placement) | **bar**, no zone/footprint/division | `test_s1_unfitted_draws_a_bar_no_zone` |
| `fitted=True` + placement placed + outline | | **zones** inside outline[0], 1 division, no bar | `test_s1_fitted_with_outline_draws_zones_no_bar` |
| `fitted=True`, placement None / withheld / no outline | | Unavailable (not_placed) | `test_s1_fitted_without_outline_is_unavailable_never_a_bar` |
| `share` ∈ {0.60,0.65,0.70,0.75} | bar / zones | drawn apartment ratio = share ± 0.5% | `test_s3_bar_proportion…`, `test_s3_zone_proportion…` |
| `share` 0.65 vs 0.70 | zones | drawn ratio moves with share | `test_s3_changing_only_the_share_moves_the_drawn_ratio` |
| committed fixtures | | drawn ratio = apartment/total = share | `test_s3_fixture_fraction_equals_apartment_over_total` |
| `share` ∈ {0.60,0.65,0.70} | | percentage = `round(share*100)` (not hardcoded) | `test_s4_percentage_is_round_share_times_100_not_hardcoded` |
| either state | | exactly 6 texts; one number (the percentage); 1 division line | `test_s5_only_the_expected_texts_and_one_number`, `test_s5_fitted_has_exactly_one_line…` |
| either state | | measure + exact conversion statement carried; ZFA never equated | `test_s6_carries_measure_and_exact_conversion_statement` |
| either state | | every label ≥ 8.5 pt; zones told apart by hatch not colour | `test_s7_every_label_is_at_least_8_5_pt`, `test_s7_zones_told_apart_by_hatch_not_colour` |
| labels/caption | | byte-equal to the WORDING tokens, em dash, no period, one caption | `test_s2_labels_and_caption_are_the_tokens_verbatim` |
| caption=False | | no caption element (report frame) | `test_s2_caption_can_be_omitted_for_the_report_frame` |
| same input / reordered keys | | byte-identical SVG | `test_s9_same_input_and_reordered_keys_give_identical_svg` |
| the two committed fixtures | | byte-stable snapshot | `test_matches_approved_snapshot` |

## Checks (direct exit codes; lanes venv, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`)

1. `cd services/api && python -m ruff check app/drawings/kit/area_allocation.py tests/drawings/kit/test_area_allocation_drawing.py`
   → **All checks passed!  exit 0**.
2. `cd services/api && python -m ruff check .` (the api CI job's first step)
   → **All checks passed!  exit 0**.
3. `cd services/api && python -m pytest -q tests/drawings/kit/test_area_allocation_drawing.py`
   → **28 passed in 0.32s  exit 0** (the folder of my tests; single file, no lock needed).
4. `cd services/api && UPDATE_DRAWING_SNAPSHOTS=1 python -m pytest -q …test_area_allocation_drawing.py`
   → regenerated the two snapshots, **28 passed  exit 0**; the SVG diff reviewed like code and
   rasterised (below).
5. `flock …/heavy-run.lock python -m pytest -q tests/drawings/kit` (whole kit folder, >1 file)
   → **NOT COMPLETED — lock-contended.** Several concurrent helpers (other worktrees) held/queued
   `heavy-run.lock`; my queued run never acquired it, so I released the slot rather than block. This
   is extra diligence beyond the packet's required checks (the "folder of my tests" is my single
   file, check 3 above, which passed 28/28). The existing snapshot harness is undisturbed by
   construction: `RENDERERS` in `test_snapshots.py` is a hardcoded `{site_plan, massing}` dict (the
   new kernel is not auto-enrolled), and the two new `*.area_allocation.svg` snapshots do not match
   its `{stem}.{site_plan|massing}.svg` glob. The independent check and CI run the full api suite.
6. `python tools/modularity_check.py --check` → **exit 0** (no warning on `area_allocation.py`; only
   pre-existing warnings on other files).
7. `python scripts/lanes/check_lane_paths.py --coverage`
   → **LANE COVERAGE PASS: 10525 file(s), each owned by exactly one lane.  exit 0**.
8. Rasterised both standalone SVGs to PNG under `/tmp/claude-0/M5-T183/` with the installed
   Chromium (headless, a `file:` URL — no server, no ports, not a Playwright test) and looked at
   them: fitted = two hatched zones (45°/70% apartment left, 135°/30% other right) inside the
   footprint with one division; not fitted = a 65%/35% hatched bar; both carry the two token labels,
   the one percentage, the measure tag, the exact conversion statement and the one caption; all text
   reads inside the canvas at 9.5 pt; the two hatches are clearly distinct in greyscale.

## Mutation proofs (one per decisive boundary; applied, shown failing, reverted)

| # | boundary | mutation | failing test | result |
|---|---|---|---|---|
| M1 | state switch (S1/R094) | `if not fitted:` → `if True:` (always bar) | `test_s1_fitted_with_outline…`, `…without_outline…`, `test_s5_fitted…` | **3 failed** (`area_division` count 0 ≠ 1) exit 1 |
| M2 | share-driven proportion (S3) | `apartment_w = _BAR_W * share` → `* (1 - share)` | `test_s3_bar_proportion_equals_share…` | **1 failed** (fraction 0.40 ≠ 0.60) exit 1 |
| M3 | one stated percentage not hardcoded (S4) | `pct = round(share*100)` → `pct = 60` | `test_s4_percentage_is_round_share_times_100_not_hardcoded` | **1 failed** (`60%` ≠ `65%`) exit 1 |
| M4 | defensive share-consistency gate (S3/S8) | `… - share) > _SHARE_TOL:` → `> 9.0:` | `test_s3_inconsistent_split_is_unavailable` | **1 failed** (Drawing ≠ Unavailable) exit 1 |

After each: source restored from a byte-identical backup; `grep -c MUTANT` = 0; final ruff + 28/28
pass confirmed.

## D-093 research and verification

Part A draws a pre-computed split and changes no feasibility fact, rule applicability, calculation
input, result or certainty label, so it **revises no evidence record**. I opened the primary sources
the packet names:
- `docs/reference-cases/R6B/cases/placement-building-b.json` (SETTLED reading, two sealed AI readers;
  agreement is not proof): row `area-allocation` records the one stated **60 %** apartment-area share
  applied to the proposed building's residential floor area (12,090 / 20,150 = 0.60), with
  apartment + other = total and the per-storey figures summing to the plate; row `plate` /
  `physical-plate-not-checked` confirm the plate is zoning floor area per storey and the physical
  floor plate is **not checked**.
- `docs/research/evidence-records/NB-02-proposed-zfa-scope.json` (measure/scope; ZR 12-10 floor-area
  definition) — read, not revised.
- The two committed 1.5.0 fixtures carry the measure `residential_floor_area` and the fixed
  conversion statement; the kernel prints the block's own values and refuses a block whose measure or
  conversion statement is not the contract const. Gross/zoning/apartment areas are never equated
  (the one stated percentage is the only number; the conversion statement is carried verbatim).
- **R091 responsibility split (recorded so a reviewer does not flag a token mismatch):** the kernel
  is data-driven and prints `round(share*100)` (65 %/70 % on the synthetics). The design contract's
  real-report **60 %** is the engine emitting `share_low = 0.60` upstream
  (`preliminary_apartment_estimate.py`), outside this kernel.
- **DB-248 scope:** S3's apartment/total == share check here is a DEFENSIVE refusal only; the
  apartment/total == share WAY RULE (DB-248) stays owned by M5-T172 and is NOT recorded resolved by
  this task.

Every unresolved input stays unresolved: a missing/garbled block, a non-finite or out-of-range
share, an inconsistent split or a fitted-without-outline yields `Unavailable`, never a drawn guess.

## What I could not check / limitations

- **No full api suite** (the independent check runs it once; the brief forbids it here). Local
  coverage = ruff + my test file + the whole kit folder + modularity + lane-paths.
- **PNG rasteriser:** the repo has no `cairosvg`/`rsvg-convert`/`resvg`/PIL; its SVG rasteriser is
  Chromium (via `print-report-pdf.mjs`). I used the installed Playwright Chromium binary directly on
  a `file:` URL (no server, no ports, not a Playwright test) to produce the two PNGs for the
  visual-quality-reviewer. If a reviewer requires a non-browser rasteriser, that tool is not present
  in this environment.
- **Website + PDF same-state check (R096/R098 document-level)** is Part B + M5-T174 + M0-T195 and is
  NOT asserted here (correctly, per the plan/judge spec).
- The fitted-state division uses a vertical half-plane split solved by area. It is exact for the
  committed 82×82 ring and truthful (area-proportional) for any simple outline; it carries no
  positional meaning (the direction is fixed, so the snapshot is byte-stable).

## Nothing stopped / surprised

- No forbidden path needed to change; no plan claim was wrong at the claim head (the fixtures carry
  `area_allocation` and `placement` under `building_alternatives[0]`, share 0.65/0.70, the placed
  82×82 outline — all as the packet's `path_notes` state).
- One adjustment during review: the first canvas (340 pt wide) clipped the long conversion statement;
  I widened it to 468 pt (≤ 182 mm A4 drawing width) so every label reads on one line, regenerated
  the two snapshots, and re-looked at both PNGs.

---

## Round 2 — G5 F1/F2/F3 hardening (builder, round 2)

Round 2 closes the three REQUIRED corrections the G5 security review raised, as one cluster, in the
kernel and its test only (both in the packet's `allowed_paths`). The kernel's own contract is to fail
CLOSED: a document it cannot draw truthfully yields `Unavailable`, never a malformed drawing (a
literal `nan` in a path) and never an unhandled exception. All three findings concern hostile
`placement.outline` coordinates. The two valid synthetic fixtures still draw and both snapshots are
byte-identical (unchanged by this round — proven below).

### The three findings and what changed (all in `_placed_ring`)

- **F1 — non-finite / over-large outline coordinate drew a `nan` token.** `_placed_ring` now checks
  every outline coordinate with a new `_plausible_coord(value)` helper: a coordinate must be a finite
  number (`_finite_number`: `int`/`float`, not `bool`, `math.isfinite`) whose magnitude is
  `≤ _COORD_MAX` (new constant, `1.0e9`). This rejects `NaN`, `±inf`, a non-number, and a magnitude
  such as `1e308` whose shoelace/scaling products overflow to `inf`/`nan`. `_COORD_MAX = 1e9` keeps a
  plausible absolute projected coordinate (EPSG:2263 NY state-plane, about `1.1e6` ft for NYC) well
  inside the bound — verified a `(980000, 190000)`-based 82×82 ring still draws — while refusing an
  over-large magnitude. A malformed vertex shape (not a ≥2-length sequence) is refused the same way.
- **F2 — a zero-area outline raised `ZeroDivisionError`.** `_placed_ring` now refuses a ring whose
  `_poly_area(pts) ≤ 0.0` (a collinear ring, or a zero-width vertical spike) → `Unavailable`, so the
  `fraction = _poly_area(apartment_poly) / total` division is never reached with `total == 0`. I also
  proved (reproductions in `/tmp/claude-0/M5-T183-r2/`) that the G5's *empty-clip* `ValueError` from
  the svg helpers (`head, *rest = points` on an empty list) is reachable ONLY through the non-finite /
  overflow path: for any finite, plausible-magnitude, positive-area ring and a share in 0.60–0.75 the
  vertical half-plane clip always keeps both extreme vertices, so neither side is ever empty (I
  probed simple, thin-spike and self-intersecting shapes — all kept ≥3 points per side). F1 therefore
  removes the only route to that `ValueError`; F1 + the zero-area guard together give the
  "no `ZeroDivisionError`, no `ValueError` from the svg helpers" guarantee without dead code.
- **F3 — no vertex-count cap (enormous SVG / CPU).** `_placed_ring` now refuses a ring whose raw
  vertex count exceeds `_MAX_OUTLINE_VERTICES` (new constant, `1000`) BEFORE building points or
  running the O(n) bisection → `Unavailable`. A plausible footprint carries a handful of vertices.

All three refusals return a plain-words reason (no field/record names) via a small
`_outline_unavailable(reason)` helper with `reason_kind = "outline_invalid"`. `draw_area_allocation`
now returns the `Unavailable` from `_placed_ring` directly (structural "not placed" stays `None` →
the existing `not_placed` reason). The dead `_ring_points` helper was folded into `_placed_ring`.
The valid drawing path is untouched, so the two snapshots do not change.

### Round-2 input-state table (input, state, outcome, test that pins it)

| input | state | outcome | test |
|---|---|---|---|
| outline coord | `NaN` / `inf` / `-inf` | Unavailable (outline_invalid), no `nan` in reason | `test_f1_nonfinite_or_overlarge_outline_coord_is_unavailable[nan/inf/-inf]` |
| outline coord | `1e308` (overflow magnitude) | Unavailable (outline_invalid) | `test_f1_…[1e+308]` |
| outline ring | zero-area collinear (flat) | Unavailable (outline_invalid), no `ZeroDivisionError` | `test_f2_zero_area_collinear_ring_is_unavailable_no_zerodivision` |
| outline ring | zero-width vertical spike (clips to nothing) | Unavailable (outline_invalid) | `test_f2_zero_width_spike_clips_to_nothing_is_unavailable` |
| outline ring | `_MAX_OUTLINE_VERTICES + 1` (1001) vertices | Unavailable (outline_invalid); 1000 still draws | `test_f3_outline_above_the_vertex_cap_is_unavailable` |
| outline refusals | F1 / F2 reasons | plain words, none of `area_allocation/fitted/sqft/placement/outline/\|/\|_` | `test_f1_f2_outline_reasons_are_plain_words_no_internal_names` |
| valid fitted fixture | placed 82×82 ring | Drawing, no `nan` token; snapshot byte-identical | `test_valid_fitted_outline_still_draws_without_a_nan_token`, `test_matches_approved_snapshot` |

### Checks (direct exit codes; lanes venv, `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider`)

1. `cd services/api && python -m ruff check app/drawings/kit/area_allocation.py tests/drawings/kit/test_area_allocation_drawing.py` → **All checks passed!  exit 0**.
2. `cd services/api && python -m ruff check .` (api CI job's first step) → **All checks passed!  exit 0**.
3. `cd services/api && python -m pytest -q tests/drawings/kit/test_area_allocation_drawing.py` → **37 passed in 0.50s  exit 0** (28 round-1 + 9 round-2).
4. `flock …/heavy-run.lock python -m pytest -q tests/drawings/kit` (whole kit folder, >1 file) → **474 passed in 24.20s  exit 0**.
5. `python tools/modularity_check.py --check` → **exit 0** (`failures 0; warnings 33`; no new/area_allocation warning — the kernel is 527 SLOC, under the 600 warn line).
6. `python scripts/lanes/check_lane_paths.py --coverage` → **LANE COVERAGE PASS: 10556 file(s), each owned by exactly one lane.  exit 0**.
7. Did NOT run the full api suite (the independent check runs it once); never started a server or touched ports 3000/3001/8000; ran no Playwright.

### Mutation proofs (one per guard; applied, shown failing, reverted; `grep -c MUTANT` = 0 after)

| guard | mutation | failing test | result |
|---|---|---|---|
| F1 | `if not (_plausible_coord(vertex[0]) and _plausible_coord(vertex[1])):` → `if False:` | `test_f1_nonfinite_or_overlarge_outline_coord_is_unavailable` | **4 failed** (drew a `nan`-token SVG / `viewBox … nan`) exit 1 |
| F2 | `if _poly_area(pts) <= 0.0:` → `if False:` | `test_f2_zero_area_collinear_ring_…`, `…zero_width_spike_…` | **2 failed** (`ZeroDivisionError` at `_draw_zones` `fraction = _poly_area(apartment_poly) / total`) exit 1 |
| F3 | `if len(ring) > _MAX_OUTLINE_VERTICES:` → `if False:` | `test_f3_outline_above_the_vertex_cap_is_unavailable` | **1 failed** (the 1001-vertex ring drew) exit 1 |

After each mutation the source was restored from a byte-identical backup (restored sha256 ==
pre-mutation sha256); `grep -c MUTANT` = 0; the file test re-ran 37/37 and ruff passed.

### D-093 / limitations

This round adds fail-closed INPUT validation only; it changes no feasibility fact, rule
applicability, calculation input, result or certainty label, so it revises no evidence record. I read
`docs/research/evidence-records/NB-04-lot-dimensions-basis.json` (read only): it records the owner's
rule that an outline's area is a drawing measure, never a zoning figure — consistent with this kernel,
which uses the outline only to draw proportions. Limitation: the empty-clip `ValueError` branch is now
unreachable from any finite input (closed by F1), so the "spike that clips to nothing" state is
exercised as a zero-area (zero-width) spike through the F2 guard; I proved the unreachability by
reproduction rather than leaving a dead guard.
