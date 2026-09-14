# Delta re-attestation — M4-T021 rework at head `432ed8f3` (G4 / qa-engineer)

> Saved VERBATIM by the orchestrator from the same qa-engineer agent that produced the original
> M4-T021 G4 FAIL report, resumed with its full context (2026-09-14; transport entity-decoding
> only). Reviewer ≠ producer.
>
> **Orchestrator disposition of NB-5 (recorded here, not silently):** the reviewer graded NB-5
> non-blocking but advised correcting it before final acceptance. The orchestrator ruled it
> BLOCKING for acceptance and corrected it immediately at the source, because it is the same
> defect class as G3-F2 (a false statement embedded in permanent code) and it concerns the
> module's legal-attestation semantics specifically — the most sensitive claim in the file.
> Correction applied as a tagged `[ORCH-CORRECTED per M4-T021-G4-delta NB-5]` docstring edit,
> superseded text preserved rather than deleted; behavior-neutral (792 connectors still pass,
> ruff clean). Both reviewers were asked for an identity-carry attestation on that edit.

**Content identity:** `git cat-file -t 432ed8f3` → `commit`. Material commit `c48bfd80` (parent `f8ada299`, confirmed via `git rev-parse c48bfd80^` and `git merge-base --is-ancestor`). `git diff --stat f8ada299 432ed8f3` restricted to `services/api/tests/connectors/` + `services/api/app/connectors/` → only the two allowed files changed (190/44 and 305/… line delta) — scope clean, same as before. Extracted fresh via `git archive 432ed8f3` into scratchpad; ran the same three commands: `pytest tests/connectors/test_wide_street_buffer_engine.py -q` → **40 passed**; `pytest tests/connectors -q` → **792 passed**; `ruff check .` → **All checks passed!** All match the claims.

## 1. F1 (provenance) — **CONFIRMED RESOLVED**

Read the full module. `SegmentContribution.segment_source_retrieved_at`/`.segment_source_raw_digest` (`:410-411`) and `WideStreetBufferResult.lot_source_retrieved_at`/`.lot_source_raw_digest` (`:461-462`) now exist and are populated by direct source read at all three return sites: `STATUS_PRECONDITIONS_NOT_ATTESTED` (`:659-660`), `STATUS_NO_WIDE_SEGMENTS_PROVIDED` (`:683-684`), `STATUS_COMPUTED` (`:733-734`, and per-segment `:705-706`). Segment-level fields correctly have nothing to carry in the two non-computed branches because those branches never construct a `SegmentContribution` (`segment_contributions=()`) — not a gap, a structural non-applicability.

The 5 new tests are genuinely non-tautological: they assert `contribution.segment_source_retrieved_at == segment.source_retrieved_at` against the **already-constructed input fixture's own attribute**, not a duplicated literal or the function's own prior output — confirmed by reading each of the 5 bodies. One test (`..._explicit_none_provenance_when_genuinely_unavailable`) specifically exercises the "may be None but never omitted" edge via `dataclasses.replace`. The lot-provenance passthrough is independently tested in all three branches by name (`..._when_computed`, `..._when_empty_wide_segments`, `..._when_preconditions_not_attested`). F1 is resolved both structurally and by test coverage.

## 2. New EC-5 value gate — **adequately tested, both directions, full truth table**

`_ec5_precondition_failures` (`:523-543`) independently re-checks each boolean field; the gate at `:628-661` returns typed `STATUS_PRECONDITIONS_NOT_ATTESTED` before any segment is touched, correctly ordered after lot CRS/geometry validation but before the EC-6 empty check. Coverage: `test_ec5_affirmative_attestation_computes_normally` (both True → `STATUS_COMPUTED`), plus refusal tests for named-false/alt-true, named-true/alt-false, and both-false — that's all 4 boolean combinations, with per-field message-isolation asserted (only the failing field is named) and gate-precedes-EC-6 ordering explicitly pinned (`test_ec5_gate_refuses_even_with_an_empty_wide_segment_set`). This is genuinely stronger than the retired test it replaces. Minor, non-blocking observation: no test pins "EC-5 refusal wins over a segment-level CRS error" the way `test_crs_gate_runs_before_geometry_is_ever_interpreted` pins lot-CRS-before-geometry — control flow makes this unreachable by construction (identical to why the empty-segment ordering test was needed and added), so I don't consider it a real gap, just a defensive test a future pass could add.

## 3. quad_segs 8→16 + end-cap fixture — **independently reproduced, claim confirmed correct**

I did **not** take the producer's numbers on faith. Ran my own standalone shapely probes (not the module under test):
- End-cap distance from `(248.0,-64.0)` to lot corner `(200,0)`: exactly `80.0` (48-64-80 triangle) — confirmed.
- End-cap intersection area: `382.9260890749891` at `quad_segs=16`, `373.6219486597519` at `quad_segs=8` — **matches the claim to all significant figures**, independently computed.
- Flat-cap probe on identical linework: `intersects=False`, `area=0.0` at both settings — confirms the entire end-cap-fixture overlap is exclusively the rounded-cap contribution, not the straight sides, exactly as the test's own comment claims.
- **The specific claim I was asked to check independently** — "no existing S1–S4 expected value changed" — I verified by computing all of S1-within (10000.0), S1-beyond (0.0), S4-tangent (0.0, `LineString`, `intersects=True`), and S3-union (17500.0, with 10000.0/10000.0 per-segment) at both `quad_segs=8` and `quad_segs=16`: **identical in every case**. This is expected given those fixtures' segments all use long y-ranges (±1000) keeping endpoints far from the lot, so only straight buffer sides ever reach it — the producer's stated reasoning is correct, not just asserted. The test-file diff also confirms the only change to those three pre-existing tests is a search-and-replace of hardcoded `quad_segs=8` → `BUFFER_QUAD_SEGS` in `test_line_probe_matches_the_hand_derived_expected_values`, nothing else — full diff of removed (`-`) lines shows no other body was touched.

## Earlier PASS dimensions — carry forward

Full diff of both files against the prior reviewed head confirms all S1/S2(CRS+geometry+malformed-attestation)/S3/S4/determinism/no-reprojection-guard/tautology/isolation/scope test bodies are byte-identical to what I already verified PASS on `2231227a`, except the deliberate, verified-safe `quad_segs` substitution above. Count reconciles exactly: 29 − 1 (retired `..._pass_through_unmodified_regardless_of_value`) + 12 new (5 provenance + 2 end-cap + 5 EC-5-gate) = 40. 792 = 752 + 40, confirmed by my own run, not just cited.

## New non-blocking finding (incidental, found during verification)

**NB-5:** `Ec5AttestedPreconditions`'s own class docstring (`wide_street_buffer_engine.py:310-328`, specifically "*This module does NOT gate computation on the attested values*") was **not updated** by the rework and now directly contradicts the corrected module-level docstring and the actual gating behavior at `:628-661`. The rework's producer report (line 483) claims "dataclass docstrings updated to describe the new fields and their per-branch guarantees" — true for `SegmentContribution`/`WideStreetBufferResult`, but this one was missed. Purely a documentation defect (docstrings are inert at runtime; no test could or should assert prose), not a behavior or test-adequacy defect — does not block this confirmation, but should be corrected before G6/final acceptance given this is legal-attestation-input documentation.

## Verdict

**CONFIRMED.** F1 is genuinely resolved (code + non-tautological tests, all three branches). The new EC-5 gate is adequately tested in both directions with full truth-table coverage. The quad_segs correction and end-cap fixture are independently reproduced by me and correct; the "no existing value changed" claim is independently verified true, not merely trusted. All previously-PASS dimensions carry forward unchanged. One new non-blocking documentation finding (NB-5) noted for the record, not gating this delta re-review.
