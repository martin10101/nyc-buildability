# Neighbours' existing floor area — method and recorded capture (B-11 slice 2)

Queue item **B-11 slice 2** (Lane B; plan section 11b "neighbours' unused floor area";
directive D-090, owner GO D-090-R087). Recorded 2026-10-03. This note states the neighbour-set
method, the source order used to capture each neighbour's existing zoning floor area, and the
recorded reading on the benchmark. It encodes no legal interpretation and produces no capacity.

## 1. What a "neighbour" is (documented method, not computed here)

A **neighbour** of the subject lot is a lot on the subject's **tax block** whose recorded
MapPLUTO EPSG:2263 outline **shares a lot line** with the subject's outline — a **touching lot**.

- The geometry test (do two recorded tax-lot outlines share a lot line) is **B-07's**, in
  `services/api/app/spatial/multi_lot_site/` (shared-line detection via `conform`), and is proven
  on the benchmark in `services/api/tests/spatial/test_multi_lot_site_benchmark_block_7334.py`
  (`test_both_lots_make_one_corner_site_with_the_shared_line_removed`): lots 1 and 70 share one
  **99.98 ft** lot line, their EPSG:2263 outline vertices coinciding exactly.
- B-11 slice 2 does **not** recompute geometry. The capture module
  (`app.profile.parity.neighbor_floor_area`) takes the neighbour set as a documented input and
  records the method verbatim in `NEIGHBOR_SET_METHOD`. Reusing B-07's accepted result (rather
  than a second geometry implementation) keeps one source of truth for "touching".

### Benchmark neighbour set

For the subject **215-16 Northern Boulevard (BBL 4073340070)**, block 7334, Queens, the recorded
fixtures (B-01 lot 70; B-07 lot 1 + the shared-line test) establish exactly one touching
neighbour: **tax lot 1 (BBL 4073340001, 215-10 Northern Boulevard)**.

**Bound / known gap.** The recorded fixtures cover only lots 1 and 70 of block 7334. A block-wide
neighbour set — every lot on the block that touches lot 70 — would need the whole block's MapPLUTO
geometry recorded, which is not in scope here and is an **open B-11 owner question** (does the
product want every touching lot on the block, or the recorded touching lots only?). Until then the
neighbour set is the recorded touching lots; it is never silently widened or guessed (D-051).

## 2. Source order for each neighbour's existing zoning floor area (B-05, reused verbatim)

Each neighbour's existing zoning floor area is captured with the **same** precedence the subject
uses (`app.profile.existing_floor_area.resolve_existing_zoning_floor_area`), no new order and no
new field:

1. a **certificate of occupancy** figure (read from the document), else
2. a **DOB job-filing** figure (DOB BIS `ic3t-wcy2` "Proposed Zoning Sqft" of a completed filing
   shown to describe one building), else
3. a **stated assumption** the architect enters, else
4. **not recorded** (value unknown; the existing-building paths and remaining floor area stay
   blocked).

**DOF / PLUTO building area (`BldgArea`) is never read as existing zoning floor area** — the
`ExistingFloorAreaEvidence` input type admits no building-area value, so there is no path in
(plan M2-07). It is shown elsewhere for reference only.

## 3. Recorded reading on the benchmark neighbour (lot 1)

Recorded pack: `services/api/tests/fixtures/benchmark_block_7334_neighbor_lot_1/` (captured
2026-10-03 UTC, byte-faithful, `MANIFEST.json` + `README.md` + `.gitattributes -text`). It closes
the gap the B-07 README named: "no query keyed on BBL 4073340001 was recorded … no certificates of
occupancy by BBL."

| Dataset | Query | Result |
|---|---|---|
| DOB BIS job filings `ic3t-wcy2` | `?bin__=4157401` (lot 1's building), PII-excluding `$select` | 22 rows; the only zoning-figure rows are job **421199072** (14,150 sq ft, "PERMIT ISSUED - ENTIRE JOB/WORK", **not signed off**) and job **421803891** (existing 9,100 → proposed **39,772** sq ft, "PLAN EXAM - DISAPPROVED"; text names "ONE (1) ZONING LOT AND (2) TAX LOTS (LOT #1 & #70)"). |
| DOB BIS CO `bs8b-p36w` | `?bbl=4073340001` | `[]` — no BIS certificate of occupancy. |
| DOB NOW CO `pkdm-hqz6` | `?bbl=4073340001` | `[]` — no DOB NOW certificate of occupancy. |

**Capture outcome:** lot 1 reads **Unknown — enter / not recorded**. 14,150 is set aside (work not
completed); 39,772 is set aside (disapproved, and its text mentions a zoning lot spanning tax lots
1 and 70, so the figure may cover the whole zoning lot, not this building); no certificate figure
and no stated assumption. Both set-aside figures keep their source. The zoning-lot mention is a
**reminder only** — a recorded filing does not verify a zoning lot (that stays "Check needed"), and
the text is never read for lot numbers. DOF/PLUTO building area (lot 1 `bldgarea` 8,409; lot 70
`bldgarea` 54,488) appears nowhere in the capture.

## 4. Boundaries (platform principles)

- DATA only. The unused-floor-area output for every neighbour stays the owner-settled "Remaining
  development capacity: Not confirmed" / "Needs verified zoning-lot boundaries and existing zoning
  floor area." (D-090-R038) — never a number, never a subtraction. The allowance and the
  subtraction are the rule engine's (Lane A), which is off.
- No field meaning is guessed (principle 3): the DOB columns and query shapes are the B-05 /
  B-01 recorded ones (`docs/research/dob-legacy-sources.md`, `docs/research/M1-T007-dob-now-sources.md`).
- Tests replay recorded fixtures only; no live calls in tests. Live calls were used once, here, to
  record the fixtures.
