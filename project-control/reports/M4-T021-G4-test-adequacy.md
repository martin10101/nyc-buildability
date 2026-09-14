# Gate Report

> Saved VERBATIM by the orchestrator from the qa-engineer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.
> Verdict FAIL — recorded as FAIL; see the orchestrator's consolidated rework record for the
> ruling on the G3/G4 disagreement about EC-5 (this report's NB-2 vs the G3 report's F1).

- Gate ID: G4
- Task ID: M4-T021
- Reviewer: qa-engineer (independent, read-only)
- Producer: backend-engineer (orchestrator-dispatched, unnamed spawn, D-060 deviation record)
- Result: **FAIL**
- Clean environment/worktree used: Landed in an isolated worktree (`.claude/worktrees/agent-ad06102843dab8205`, live HEAD `d8b3899f`, ≠ pinned `2231227a`). Verified `2231227a` exists in this worktree's history (`git cat-file -t 2231227a` → `commit`). Read pinned content via `git show 2231227a:<path>` and executed against a `git archive 2231227a` extraction into scratchpad (`…/scratchpad/m4t021review`), per the reviewer's explicit isolated-worktree instruction. Two additional disposable mutation-probe copies were made in scratchpad for non-vacuity testing; nothing in the actual worktree/repo was modified, no git/gh state-changing command was run.

## Content-identity check

- `git cat-file -t 2231227a` → `commit` (exists in this worktree's ancestry).
- `2231227a` is the control-plane integration commit (evidence-map + task/report JSON + `state.json`, 4 files, 58 lines) — **not** the material change itself.
- Material producer commit `7dc56112` (parent of `2231227a`) carries the actual diff: `wide_street_buffer_engine.py` +632/-1, `test_wide_street_buffer_engine.py` +662/-1, matching the producer report's claimed line counts exactly (`wc -l` on the extraction: 632 / 662).
- Direct parent of `7dc56112` is `b2983c74` (verified via `git rev-parse 7dc56112^`) — confirmed as the correct pre-B4 baseline for the regression diff.
- At `b2983c74`, both new files were 1-line placeholders (`git show b2983c74:<path>`) — confirms this is genuinely new work, not a rewrite of prior accepted content.

## Acceptance criteria reviewed

Task packet `project-control/tasks/M4-T021.json` scenarios S1–S5 (read at pinned content), contract items 1–6, and the required producer-report tradeoff sections (EC-2, EC-4, EC-5).

## Steps independently executed

1. `python -m pytest tests/connectors/test_wide_street_buffer_engine.py -q` (extraction root `…/m4t021review/services/api`) → **29 passed in 0.62s**. Matches claim.
2. `python -m pytest tests/connectors -q` → **781 passed in 6.77s**. Matches claim.
3. `python -m ruff check .` (from `services/api`) → **All checks passed!** Matches claim.
4. Baseline reconciliation: extracted `b2983c74` (`services/api` only) and ran `pytest tests/connectors -q` → **751 passed, 1 error** (752 collected). The 1 error is `FileNotFoundError` for `packages/contracts/schemas/...` — an artifact of extracting `services/api` in isolation from `packages/`, not a real failure (the same test passes cleanly inside the full-repo extraction at the pinned head). Collected-count reconciles to 752, matching the producer's "752 previously-accepted" claim.
5. `git diff --stat b2983c74 2231227a -- services/api/tests/connectors/ services/api/app/connectors/` → **only** the two new files changed (662/1 and 632/1 line diffs). No accepted test or connector file modified.
6. `git diff --stat b2983c74 2231227a` (whole repo) → exactly the 3 `allowed_paths` files plus expected orchestrator ledger/evidence bookkeeping (`state.json`, `tasks/M4-T021.json`, `reports/M4-T021.json`, `reports/M4-T021-evidence-map.json`) — no producer scope violation.
7. `grep -c '^def test_'` and `pytest --collect-only` on the new test file → **29** test functions, reconciling exactly to the claimed count, with no skips/xfails hiding.
8. Structural code trace: read `wide_street_buffer_engine.py` in full (633 lines) and confirmed `disposition`/`width_classification`/`Streetwidth` never appear in executable code — only inside docstrings/notice-string prose.
9. **Non-vacuity mutation test of the guard test** (`test_module_never_reimplements_transport_or_reprojection`), per the reviewer's explicit instruction:
   - Probe 1: added `BOUNDARY_TOLERANCE_FT` to the existing `mappluto_geometry_arcgis` import in a scratch copy → guard test **FAILED** (`AssertionError: assert 'BOUNDARY_TOLERANCE_FT' not in {...}`) — the import-allowlist/name-scan half is genuinely non-vacuous.
   - Probe 2: added a bare literal `_MUTATION_PROBE_LITERAL = 0.3048` (no import, simulating hand-rolled reprojection math) in a second scratch copy → guard test **FAILED** (`AssertionError: 0.3048 ... contained here`) — the forbidden-token-scan half is *independently* non-vacuous (not redundant with the import check).
10. Hand-derived (not code-derived) verification of three fixture geometries:
    - S1 within-100ft: vertical segment at x=−50, buffer → x∈[−150,50]; intersect with lot x∈[0,200] → rectangle 50×200 = **10000 sq ft**. Matches test.
    - S3 corner-lot union: vertical contributes 10000, horizontal contributes 10000, SW-corner overlap 50×50=2500; union = 10000+10000−2500 = **17500 sq ft**, strictly between 0 and 40000. Matches test.
    - S4 tangency: segment at x=−100, buffer edge lands exactly at x=0 (lot's west edge) → boundary-only touch, zero-area `LineString`, `intersects=True`. Matches test.
11. Confirmed offline isolation: grepped `dcm_street_centerline_geometry.py` / `mappluto_geometry_arcgis.py` / `wide_street_buffer_engine.py` for `requests.`/`socket.`/`urlopen`/`httpx.` — none found in the code paths the fixtures exercise (`DcmTransport` is a plain frozen dataclass constructed directly with synthetic bytes; `parse_segment_geometry_page`/`analyze_lot_geometry` take in-memory data, no transport default). `default_fetch`/`urllib_transport` only appear as *default parameters of other, unused functions* — never invoked by any test in this file.
12. Confirmed no fixture mutation risk: `EC5_CHECKED` is a frozen dataclass (mutation raises `FrozenInstanceError`); `SQUARE_LOT_RINGS` is read-only across ~15 reuses; `analyze_lot_geometry`'s internal list operations build fresh output collections (`.append` onto locally-scoped `holes`/`exteriors`/`repairs`/`structural` lists), never mutate the input `rings` in place — corroborated empirically by every test that reuses `SQUARE_LOT_RINGS` consistently reporting lot area 40000.0.
13. Order-independence spot check: ran two tests in reverse declaration order (`test_corner_lot_...` before `test_segment_within_100ft_...`) — both passed. (No `pytest-randomly` plugin available in this environment for a full shuffle; module-level fixtures are immutable/re-read-only, so this is a reasonable, not exhaustive, confirmation.)
14. Did **not** run `python tools/modularity_check.py --check` (outside the explicit "MAY run" list for this review) — relying on the producer's reported `0 failures` as inspected-not-independently-reproduced; not part of my assigned test-adequacy scope, and `code-reviewer` is the named second reviewer for this task.

## Expected versus actual — coverage tables (S1–S4)

**S1 wide_only_buffer_membership**

| Requirement | Test(s) | Verdict |
|---|---|---|
| Segment within 100ft → intersects true, non-empty area>0 | `test_segment_within_100ft_intersects_true_with_nonempty_area` | PASS (10000 sq ft hand-verified) |
| Segment beyond 100ft → false, empty portion | `test_segment_beyond_100ft_intersects_false_with_empty_portion` | PASS |
| Only caller-supplied segments participate; module never re-classifies | `test_only_caller_supplied_segments_participate_never_reclassified` (narrow-labelled 40ft segment produces identical geometric result) + structural: no `Streetwidth`/`disposition` token in executable code + AST-scan forbids importing classifier/policy modules | PASS, structurally proven, not just behaviorally asserted |
| Per-segment identity visible | `test_per_segment_identity_is_visible` | PASS |

**S2 crs_and_input_fail_closed**

| Requirement | Test(s) | Verdict |
|---|---|---|
| Missing/mismatched lot CRS | `test_missing_lot_crs_is_typed_wrong_crs`, `test_mismatched_lot_crs_is_typed_wrong_crs` | PASS |
| Missing/mismatched segment CRS | `test_missing_segment_crs_is_typed_wrong_crs`, `test_mismatched_segment_crs_is_typed_wrong_crs` | PASS |
| CRS gate precedes geometry interpretation | `test_crs_gate_runs_before_geometry_is_ever_interpreted`, confirmed structurally (`_require_crs` precedes `_lot_shapely` in source) | PASS |
| Degenerate/invalid lot & segment geometry | `test_invalid_lot_geometry_is_typed_invalid_geometry`, `test_invalid_segment_geometry_is_typed_invalid_geometry` | PASS |
| Missing/malformed EC-5 attestation | `test_missing_ec5_preconditions_is_a_construction_error`, `test_malformed_ec5_preconditions_type_is_typed_error`, `test_malformed_ec5_preconditions_non_bool_field_is_typed_error`, 3× no-default dataclass tests | PASS |
| No-reprojection path (non-vacuous) | `test_module_never_reimplements_transport_or_reprojection` | PASS, **confirmed genuinely non-vacuous by two independent mutation probes** (see step 9 above) |

**S3 portions_split_corner_lot**

| Requirement | Test(s) | Verdict |
|---|---|---|
| Union-before-intersect aggregate correct | `test_corner_lot_union_before_intersect_and_per_segment_visibility` | PASS (17500 hand-derived) |
| Sub-area strictly between 0 and lot area | same test, `0.0 < aggregate_area_sq_ft < lot_area_sq_ft` | PASS |
| Per-segment contributions individually visible | same test, `by_id[21]`/`by_id[22]` | PASS |
| Non-wide frontage excluded by construction | `test_non_wide_frontage_never_included_by_construction` | PASS |

**S4 tangency_and_empty_honesty**

| Requirement | Test(s) | Verdict |
|---|---|---|
| Exact-100ft tangency, no silent tolerance | `test_exact_tangency_is_the_unmodified_geos_predicate_result` | PASS, hand-verified (area 0.0, `LineString`), no `pytest.approx`/tolerance constant used |
| Empty wide-segment set typed, not a default | `test_empty_wide_segment_set_is_typed_never_a_default` | PASS, asserts `status == STATUS_NO_WIDE_SEGMENTS_PROVIDED` and all aggregate fields `is None` |
| EC-2 notice always present | `test_ec2_under_claim_notice_always_present` | PASS |
| EC-5 attestation passthrough (design choice) | `test_ec5_preconditions_pass_through_unmodified_regardless_of_value` | PASS — pins the disclosed "does not gate on attested value" design choice; ruled an acceptable, contract-literal reading (packet text requires the caller "cannot silently skip" supplying the attestation, not that computation be blocked on its value) — logged NB-2 below |

**Determinism (S5)**: `test_shapely_and_geos_versions_are_pinned_for_determinism` hardcodes literal string comparisons (`"2.0.7"`, `"3.11.4"`) against both the test-local shapely import and the module's own pinned constants; the production module additionally asserts at **import time** (lines 623–632), meaning even test *collection* fails on drift — stricter than the cited precedent. Non-tautological: literal comparison, not a self-check.

## Tautology + isolation verdicts

- **Tautology: PASS.** No test derives its expected value by calling `compute_wide_street_buffer_intersection` and comparing against another call's output. All numeric expectations are literal constants I independently hand-derived (10000, 40000, 17500, 0.0) or cross-checked via the suite's own separate `test_line_probe_matches_the_hand_derived_expected_values`, which recomputes the S1/S4 facts via **direct shapely calls that never touch the module under test** — a genuine independent path, not a snapshot of the implementation's own output.
- **Isolation: PASS.** Fully offline (confirmed no network call path in any code the fixtures exercise); fixtures are immutable (frozen dataclass) or empirically read-only across ~15 reuses; spot-checked order-independence (two tests run out of declaration order, both passed) — not exhaustively fuzzed, but no plausible shared-mutable-state vector exists given the frozen/read-only fixture design.

## Regression/security/provenance findings

**F1 (BLOCKING) — provenance passthrough on results is dropped, contradicting the packet's own contract, and is untestable as a result.**

The task packet's contract item 5 requires: *"every result carries the inputs' provenance (retrieval identities, raw digests, CRS stamps, classifier basis passthrough)"* and the packet's `outputs` field names `"provenance passthrough"` as a required output-module characteristic. `AttestedWideSegment.source_retrieved_at`/`.source_raw_digest` and `AttestedLotPolygon.source_retrieved_at`/`.source_raw_digest` are declared as required (no-default) **input** fields (`wide_street_buffer_engine.py:334-335`, `358-359`), but neither `SegmentContribution` (`:366-376`) nor `WideStreetBufferResult` (`:378-411`) carries a `source_retrieved_at` or `source_raw_digest` field at all — I confirmed via full read of both dataclasses and a `grep` for those two identifiers across the whole module: they appear **only** in docstrings and the two input dataclass field declarations, never read or copied anywhere inside `compute_wide_street_buffer_intersection` (`:521-613`). Only `classification_basis` and `lot_identity` are actually threaded through to the result — the CRS stamp and citation are also carried, but retrieval identity and raw digest are silently dropped between validation and result construction.

This is a real implementation gap (deterministic-code correctness, not a legal/AI-boundary question), not merely a documentation nit: a downstream consumer (B7 rule wiring, or a future audit) receiving a `WideStreetBufferResult` has **no way to trace which raw DCM/MapPLUTO fetch produced a given buffer/intersection area** — only an opaque `classification_basis` string and a `lot_identity` label, neither of which is a retrieval timestamp or content digest. This directly conflicts with CLAUDE.md's permanent principle #2 ("every material fact... must retain provenance") for a module whose entire stated purpose is producing a provenance-carrying geometry fact for a future rule.

Critically for **test adequacy**: because the fields don't exist on the output, **no test could have caught this** — there is no assertable surface for "the result carries `source_retrieved_at`/`source_raw_digest`." The producer report's own Item 5 evidence claim ("carried through unmodified into the result") is worded ambiguously enough to read as accurate only if narrowly parsed to mean "classification_basis and lot_identity specifically" — but the packet text it's citing explicitly says "retrieval identities, raw digests" too, and no evidence or test backs that part of the claim. Unlike the EC-5 attestation design choice (section 5 of the producer report), this gap is **not** disclosed anywhere in the producer report's "Limitations and honest disclosure" section (section 9).

Remedy (either is acceptable, subject to reviewer/producer discussion): (a) add `segment_source_retrieved_at`/`segment_source_raw_digest` to `SegmentContribution` and `lot_source_retrieved_at`/`lot_source_raw_digest` to `WideStreetBufferResult`, thread them through both the empty-set and computed branches, and add a test asserting their presence/passthrough; or (b) explicitly disclose in the producer report, mirroring the EC-5 pattern, that retrieval-identity/raw-digest passthrough was deliberately scoped out of the result (with rationale), subject to reviewer agreement — in which case this becomes an NB rather than an F.

## Non-blocking notes

- **NB-1 (disclosed, judged acceptable):** No dedicated multipolygon/holes lot fixture. Judged **non-blocking**: I read `_lot_shapely` (`:490-515`) and the full `compute_wide_street_buffer_intersection` body and confirmed the module treats the lot as an opaque `shapely.BaseGeometry` — it never inspects ring count, exterior/hole structure, or geometry subtype; `.intersects`/`.intersection`/`.area` are polymorphic GEOS operations that behave identically for `Polygon` and `MultiPolygon`/polygon-with-holes. The one place a multipolygon-specific bug could hide is inside the *accepted, forbidden-path, out-of-scope* `canonical_to_shapely`/`analyze_lot_geometry` (M2-T009), which already claims generic Multi/hole support and is not this task's surface to re-test. Honestly and specifically disclosed in producer report §9 (not buried). Not required by any of S1–S5's literal text. Acceptable as a documented limitation, not a defect of this module's own test suite — but worth a follow-up fixture in a later B-series task given zoning lots do sometimes span irregular/multi-part parcels.
- **NB-2 (design choice, ratified):** EC-5 "does not gate computation on attested values" — disclosed explicitly by the producer (report §5) as open to reviewer disagreement, pinned by a real test (`test_ec5_preconditions_pass_through_unmodified_regardless_of_value`) that would fail if a future change silently started gating on it. I rule this an acceptable, contract-literal reading (the packet requires non-omission, not value-gating) and it is adequately test-pinned either way.
- **NB-3:** `quad_segs=8` arc-approximation resolution disclosed (producer report §9) as matching shapely's default but not independently derived from an official source; no test exercises an end-cap-proximate scenario where this parameter would matter. Low materiality (straight-buffer edges away from segment endpoints are exact regardless of this parameter) — acceptable as disclosed.
- **NB-4:** `python tools/modularity_check.py --check` was not independently reproduced by me (outside my allowed-command list for this review); relying on the producer's reported `0 failures` — flag for `code-reviewer`, the task's other named reviewer, or for the orchestrator to independently confirm before acceptance.

## Count + regression audit

- Claimed 29 new tests: **confirmed exactly 29** (`grep -c '^def test_'` and `pytest --collect-only` agree, no skips/xfails).
- Claimed 781 = 752 + 29: **confirmed** — full suite at pinned head passes 781; baseline at the direct parent commit `b2983c74` collects 752 (751 pass + 1 environment-artifact error from partial extraction, not a real failure).
- No accepted test or connector file modified: **confirmed** via `git diff --stat b2983c74 2231227a` restricted to `services/api/tests/connectors/` and `services/api/app/connectors/` — only the two new files appear in the diff.
- Scope: **confirmed** — whole-repo diff between the same two commits touches exactly the 3 `allowed_paths` files plus expected orchestrator ledger/evidence bookkeeping files, nothing else.

## Evidence paths

- Task packet (pinned): `project-control/tasks/M4-T021.json` (read via `git show 2231227a:...`)
- Producer report (pinned): `project-control/reports/M4-T021-producer-report.md`
- Module under test (pinned): `services/api/app/connectors/wide_street_buffer_engine.py`
- Test file (pinned): `services/api/tests/connectors/test_wide_street_buffer_engine.py`
- Precedent AST-scan pattern: `services/api/tests/connectors/test_dcm_street_centerline_geometry.py:233-268`
- Reviewer working extraction: scratchpad `m4t021review` (full `git archive 2231227a`), `m4t021base` (`services/api` at `b2983c74`), `m4t021mutate`/`m4t021mutate2` (disposable non-vacuity probes)

## What I executed vs. inspected

- **Executed** against the pinned-head extraction: the module's own 29-test file, the full 781-test connectors suite, `ruff check .`, plus my own `-k`-filtered re-runs, the reverse-order pair, and both guard-test mutation probes.
- **Executed** against the pre-B4 baseline extraction: full connectors suite (752-collected reconciliation).
- **Inspected only** (read source, did not independently re-execute as a separate tool): `modularity_check.py` output (relied on producer's reported number); the accepted `analyze_lot_geometry`/`canonical_to_shapely`/`parse_segment_geometry_page` internals (out of this task's scope, `forbidden_paths`), confirmed only by grep for mutation/network-call red flags.

## Required rework

1. Resolve F1: either thread `source_retrieved_at`/`source_raw_digest` from both `AttestedWideSegment`/`AttestedLotPolygon` into `SegmentContribution`/`WideStreetBufferResult` with a covering test, or add an explicit, disclosed producer-report limitation (mirroring the EC-5 pattern) narrowing contract item 5's "retrieval identities, raw digests" language, for reviewer ratification.
2. Resubmit for G4 re-review at the corrected head; NB-1 through NB-4 do not block re-submission but should be carried forward (NB-1 as a follow-up-task candidate, NB-4 for `code-reviewer`/orchestrator to independently confirm).

## Reviewer conclusion

Test *design* quality is high: non-vacuous structural guards (proven by mutation, not merely inspected), hand-derived rather than snapshotted expected values, exact-not-approximate tangency assertions, literal (non-tautological) determinism pins, and honest disclosure discipline for the two genuine judgment calls (EC-5 gating, multipolygon fixture gap) that the producer did flag. However, the suite has a real, non-obvious blind spot precisely because the implementation drops a contractually-required provenance field before it ever reaches an assertable output — no amount of additional test-writing skill inside the existing dataclass shape could have covered it. That is a genuine defect in the code under test, surfaced by a test-adequacy review, not a nitpick. **Verdict: FAIL**, on F1 alone; all other reviewed dimensions are PASS.
