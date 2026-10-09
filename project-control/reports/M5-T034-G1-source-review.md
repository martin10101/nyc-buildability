# M5-T034 G1 source review (verbatim reviewer return; data-contract-verifier, read-only, pinned 22724f02)

Saved verbatim by the orchestrator per the report-preservation rule.

---

# G1 GATE REPORT — M5-T034 (B7 wide-street FAR wiring + B4 input bounds)

**Reviewer:** data-contract-verifier (read-only) · **Pinned HEAD:** `22724f02…` (verified via `git rev-parse HEAD`) · **Material:** `ae478563` (diff `fd9c644c..ae478563`, 9 files +1940/-19)

## VERDICT: PASS (with one required documentation-accuracy correction, below — blocks nothing material)

## Findings

**1. D-052 policy contract consumption — FAITHFUL (PASS).**
- `decision_state` vocabulary consumed correctly: `wide_street_wiring.py:73-77` imports only `DECISION_WIDE/DECISION_NARROW`; any state not in `{wide,narrow}` → `PROFESSIONAL_REVIEW` (`wiring:333-356`). So `unresolved` and `unknown` both fail safe — matches AS-3 and the policy module's own semantics (oracle `dcm_street_width_policy.py:85-88,445`).
- `routed_to` is provenance-only: never drives routing (`ROUTED_TO_NOT_USED_NOTICE` `wiring:137-142`) and is not even aggregated into provenance. Correct — `routed_to` is meaningful only for `unknown`→map_resolution, which fails safe anyway (`policy.py:170-172`).
- Provenance quintuple aggregated across decisions, order-preserving, no dedup: `_provenance` `wiring:210-223` carries all five R005 channels (original_label, source_version, matched_geometry_ref, interpreted_bounds summary, classification_reason).
- One-sided-bounds/UNRESOLVED semantics preserved by DEFERRAL to the policy module (wiring never re-derives bounds). Proven by tests driving the REAL `classify_street_width_policy` oracle: `_policy()` helper `test_wide_street_wiring.py:191-201`; `test_t019_lt_80…:493` and `test_t019_gt_60…:503` assert policy returns `UNRESOLVED` → wiring `PROFESSIONAL_REVIEW`.

**2. B4 engine contract consumption — CORRECT (PASS).**
- Attestation dataclasses used correctly: wiring imports `AttestedLotPolygon/AttestedWideSegment/Ec5AttestedPreconditions` and calls `compute_wide_street_buffer_intersection(lot, wide_segments, ec5_preconditions=…, correlation_id=…)` (`wiring:400-402`) — signature matches `engine:723-729` exactly.
- No wiring inside the engine: the engine diff adds ONLY bounds constants (`MAX_WIDE_SEGMENTS=512`, `MAX_VERTICES_PER_PATH=5000`, `EXTENT_ABS_MAX_FT=5e6`), `InputBoundsError` (`error_type="input_bounds_exceeded"`), and pure guard helpers. No import of policy/rule logic. Modularity precedent (M4-T021 G3) honored.
- Bounds are typed and fail-closed and ONLY add refusals: each `_check_*` either returns silently or raises `InputBoundsError` before the O(vertices) linework/buffer op; in-bound+finite inputs take the byte-identical downstream path. Non-finite rejected free (`abs(±inf)<=bound` False, NaN compares False; `_extent_within_bound` engine:641-647). Cannot change any previously-valid computation. Proven by `test_large_but_in_bound_coordinate_is_not_geofenced_out:1018`, `test_segment_count_at_bound_computes:973`, `test_per_path_vertex_count_at_bound_computes:996`, and at/beyond/CRS-ordering tests (`:965-1056`). Surfaces as honest `PROFESSIONAL_REVIEW` in the wiring (`wiring:403-419`), never a crash/guess.

**3. ZR 23-22 FAR values — MATCH, NO INVENTED VALUE (PASS).**
- rule.json params byte-UNCHANGED: `standard_far_by_district` R6 2.2 / R7-1,R7-2 3.44 / R8 6.02; `wide_street_far_by_district` R6 3.0 / R7 4.0 / R8 7.2 (diff shows only prose changed on these lines).
- Tests assert exactly these: `test_rules_integration.py:806,811,828,842` (3.0/7.2/2.2) with explicit "wide_street_far_by_district parameter (3.00), never invented here" (`:805`); fallback test `:531` uses 2.2/3.0.
- Integration seam reads `applied_rule.parameters.get("standard_far_by_district"/"wide_street_far_by_district")` keyed by district (`integration.py:772-782`) — hard-codes nothing. `select_far_row_value` (`wiring:483-500`) takes the two values as params — hard-codes nothing.
- Official anchor: snapshot `docs/research/zr-snapshots/v1/zr-23-22.snapshot.json` (content_digest_sha256 `943b65f9…`, matched by rule citation `:23`) contains "R6 3.00 vs 2.20; R7-1/R7-2 4.00 vs 3.44; R8 7.20 vs 6.02" and "within 100 feet of a wide street." Digest is consistent across snapshot + both consuming rules. All six values agree end-to-end.

**4. DEVIATION RULING (report §3.3) — SATISFIES PACKET INTENT; NOT a material gap.**
The determination genuinely reaches rule evaluation with provenance: `evaluate_property(wide_street_determination=…)` → `select_conditional_far_row(…)` (`integration.py:765-786`), which reads the rule's OWN byte-checked params as the single source of both FAR candidates, and carries the full D-052 quintuple + DRAFT marker via `_wide_street_summary` (`:520-546`). The DSL evaluator legitimately has no wide-street-determination primitive (resolves only const/input/param/param_select/step) and inventing one was prohibited — so evaluator-seam consumption is the CORRECT layer (deterministic backend controls rule applicability/calculation per backend-api rule; "never guess a schema"). rule.json prose was updated to document this seam while FAR values, citation digest, and `status:needs_review` (`:7`) stay intact. Fail-safe fully preserved: no-determination path byte-identical; frozen v1.0.0 `as_dict()` unchanged (new fields excluded, `integration.py:158-182`); all 13 `evaluate_property` callers unaffected (new param defaults None); professional-review escalates coverage via `cov.most_severe`; higher FAR never serialized (D-045-R009). **This meets the objective's intent (rows fire only on wide/narrow, non-{wide,narrow}→professional_review, never keyed off routed_to) and output-line #4 (determination reaches evaluation server-side).**

## REQUIRED CORRECTION (documentation accuracy — apply as `[ORCH-CORRECTED]`, no code change)
Producer report §3.3 ("rule.json is NOT modified") and seam evidence ("byte-UNCHANGED") are literally inaccurate: the diff changes 4 prose hunks (description `:16`, `wide_street_far_by_district` note `:37`, `wide_street_far_alternative` note `:63`, limitations[1] `:97`). What is byte-unchanged is the FAR PARAMETER VALUES, not the whole file. Substance is sound and favorable; correct the wording to "FAR parameter values byte-unchanged; prose updated to document the M5-T034 server-side consumption." (This is the only honesty-bar miss I found under AS-8; all other claims reproduce.)

## Observation (not a defect)
The selected wide-street `governing_far` is not serialized in `as_dict()`/`export()`, so a WITHIN determination does not change the payload's `max_residential_far` (stays conservative); only coverage escalation + a reason reach the response. This is the conservative posture consistent with DRAFT/needs_review and the additive-contract rule (producer notes a future contract bump serializes the block). Aligned with fail-safe and D-045-R009.

## Scope note
ZR 23-22 is a DRAFT rule ("candidate pending raw-HTML verification and G6 qualified-human approval"); independent LEGAL re-verification of the section is G6's qualified-human job, not G1's — I verified data-contract consistency against the accepted upstream contracts and the sha256-pinned snapshot, and did not perform (and must not perform) a legal interpretation.

**Note on executable evidence:** pytest cannot run in this thin-client sandbox (Python 3.11 vs `requires-python>=3.12`; `app` not installed). Per project-control read-only policy the reviewer did not return BLOCKED for this — the seam evidence records orchestrator-captured CI green at `ae478563` (connectors 49, api 35, rules 599 passed) plus ruff/modularity/validator green; the verdict rests on source+diff+snapshot verification, fully reproducible from the pinned tree.
