# M5-T034 G3 code review (verbatim reviewer return; code-reviewer, read-only, pinned 22724f02)

Saved verbatim by the orchestrator per the report-preservation rule.

---

# GATE REPORT — G3 Senior Code Review — M5-T034

**Task:** B7 wide-street wiring module + B4 input bounds + evaluator/route seam
**Reviewed SHA (pinned):** 22724f02171826cac711270b67309327bb540e7c (`git rev-parse HEAD` = match)
**Material identity:** ae478563 (`git diff fd9c644c..ae478563`, 9 files, +1940/-19). Production source at ae478563 is byte-identical through HEAD; the interim commits (54e1da7a seam, 22724f02 evidence, plus D-069/M5-T033 work) touch no `services/api` source.
**Reviewer:** code-reviewer (read-only)
**Verdict: PASS** (informational/low observations only; no blocking defects)

## Scope of verification
Read at frozen identity: `wide_street_wiring.py`, `integration.py` (fold + dataclass + serialization), `wide_street_buffer_engine.py` (bounds), `rule_evaluation.py` (provider seam), the two rule.json files, and all three test suites. Consumer sweep via Grep. Local pytest is UNVERIFIED (thin client: Python 3.11 vs `requires-python>=3.12`, `app` not installed) — the api CI job on the pushed head is the executable authority (seam commit records CI green at ae478563; orchestrator to confirm at HEAD).

## Findings

1. **Decision logic (wide_street_wiring.py:288-500) — CORRECT.** Routing keys off `PolicyDecision.decision_state`, never `routed_to` (verified: step 2 line 333-337; test `test_routing_is_keyed_off_decision_state_not_routed_to` uses a deliberately-inconsistent decision). Every non-{wide,narrow}, engine `WideStreetBufferEngineError` (incl. new `InputBoundsError`), unattested EC-5, and no-wide-segments-vs-wide-policy contradiction → professional review with `far_row=none`; a guessed wide is never emitted (steps 1,2,4,4b,4c). Narrow-all → standard row. Dataclasses `frozen=True`, no defaults. Own module per M4-T021 ruling — consumes policy + engine read-only. Severity: none (pass).

2. **integration.py fold (471-536, 755-789) — additive-only PROVEN.** New dataclass fields `wide_street_far_row/governing_far/determination` (154-156) are deliberately EXCLUDED from `as_dict()`/`export()` (158-182), so serialization is byte-identical when no determination is supplied; test `test_m5t034_determination_ignored_for_non_conditional_district_r5` asserts `with_det.export() == without_det.export()`. Exactly-one-applicable-trace guard at 766-767; FAR values read only from the applied rule's own `standard_far_by_district`/`wide_street_far_by_district` params (769-776, dict shape confirmed dsl.py:263) — no invented value. Coverage escalation via `cov.most_severe(...)` (787-789). Disjoint applicability verified: flat `r6_r12_residential_far.rule.json` in_set EXCLUDES bare R6/R7-1/R7-2/R8; conditional rule covers exactly those four. Severity: none (pass).

3. **Engine input bounds (wide_street_buffer_engine.py:216-248, 336-345, 641-722, 751-831) — CORRECT.** Typed `InputBoundsError(error_type="input_bounds_exceeded")`, subclass of `WideStreetBufferEngineError` (caught by wiring). Placement before expensive ops: lot-extent after `_lot_shapely` and before segment loop (752); segment-count before loop (816); per-path vertex count BEFORE `_segment_linework` construction (828); linework-extent before `.buffer()` (830). Non-finite rejected free (`_extent_within_bound`: `abs(±inf)<=bound` and any NaN compare are False). Guards only raise on out-of-bound input → previously-valid results unaltered. Tests cover at-bound (computes) and beyond-bound (raises) for all three, plus a large-in-bound coordinate not geofenced, plus CRS-gate-wins ordering. Severity: none (pass).

4. **Route provider seam (rule_evaluation.py:120-166, 197-203, 317-328) — CORRECT.** `get_wide_street_determination_provider` default `_default_wide_street_determination` returns None (server-side FastAPI `Depends`, never request-body). Default path skips the fold, so `wide_street_wiring` (and shapely) is never imported at request time; `WideStreetDetermination` imported only under `TYPE_CHECKING`, lazy import inside `select_conditional_far_row` (integration.py 501-509). None default → byte-identical prior behavior. Severity: none (pass).

5. **Test quality (three suites) — STRONG.** Wiring suite drives the REAL D-052 policy module and REAL buffer-engine parse surfaces as oracles (no mocked decision logic); AS-3/AS-2/AS-4/AS-5/AS-6 blocks each assert the claimed behavior. Ten evaluator-seam tests assert governing_far 3.0/2.2/7.2 from the rule's own params and coverage escalation. Engine bound tests deterministic, offline. All network-free. Severity: none (pass).

6. **Consumer sweep — CLEAN.** `compute_wide_street_buffer_intersection` called only by the wiring (wide_street_wiring.py:400), so the new `InputBoundsError` surfaces only there. `evaluate_property` other callers (scenario_analysis.py:529, evidence.py:512, scenario.py:271) pass no determination — keyword-only default None leaves them unaffected. No known-red consumer left silent.

### Informational (non-blocking, for the follow-up)
- **INFO-A (integration.py 843 SLOC; wide_street_buffer_engine.py 890 SLOC):** both sit in the modularity "justify" band (>750, <1000 hard). `modularity_check --check` passes (failures 0); growth is cohesive (fold belongs with `evaluate_property`; bounds belong with the engine entry point). Future growth should split with a facade.
- **INFO-B (contract scope):** the wide-street outcome (far_row/governing_far/provenance) is intentionally NOT serialized into rule_evaluation v1.0.0; only coverage escalation reaches the client. So even a WITHIN determination leaves the serialized `max_residential_far` at the conservative value — fail-safe and disclosed (dataclass note 150-153), awaiting a future additive contract bump. No overstatement risk.
- **INFO-C (seam not yet live):** the provider default is None and no test exercises a real determination through the full `/rule-evaluation` endpoint (producer §6.1). The seam is unit/integration-tested and safe-by-default; live data-source wiring is a disclosed future task.

## Deviation ruling (producer report §3.3 — packet output "rule.json updated to consume the real determination")

**RULING: SOUND — the chosen design is correct and superior to the literal wording; accept as an intentional, well-justified deviation.**

The producer made the rule.json changes documentation-only (description/parameter-note/limitations prose) and consumes the determination at the evaluator seam (`evaluate_property` → `select_conditional_far_row`), reading the rule's existing `standard_far_by_district`/`wide_street_far_by_district` params as the single FAR source. This is the right engineering choice:
- The deterministic DSL evaluator resolves refs only from const/input/param/param_select/step and has no external wide-street-determination primitive. Making the rule.json literally "consume" a geometry-derived determination would require inventing a new DSL input fed by server-side geometry — blurring the "deterministic code calculates / geometry is server-side" boundary (CLAUDE.md P1/P6) and breaking the rule's byte-reproducibility.
- A wide-street determination is inherently a server-side geometry+policy computation, not a table lookup the DSL can express. Selecting the row server-side keeps the DSL pure while the rule.json remains the authoritative source of both FAR values (no invented value).
- The conservative default is preserved (DSL still returns the LOWER value; the higher value applies only on an affirmative WITHIN, never on uncertainty).
- Task output #4's substance ("the determination reaches evaluation server-side") is satisfied via `evaluate_property`.

The producer flagged this honestly and did not claim the literal output line was met. Recommend the orchestrator record it as an accepted design deviation with this rationale.

## Verdict
**PASS.** No blocking defects across the six review dimensions. Deviation is sound. Byte-identity, fail-safe direction (D-051), provenance quintuple, DRAFT/needs_review discipline (D-045-R009), and the "never a guessed wide" invariant all hold in source and are pinned by deterministic, offline tests. PASS is conditioned on the orchestrator confirming the api CI job is green at the pushed head (I could not run pytest locally; this is a sandbox limitation, not a BLOCKED condition). INFO-A/B/C are follow-up notes, not gate blockers.
