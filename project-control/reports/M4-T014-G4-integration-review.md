# G4 GATE REPORT — M4-T014 (R3/R4 height/setback draft families)

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent qa-engineer agent. Recorded at the
> pre-rework identity; the (g)-provenance rework (G3 supplemental ruling) touches snapshot NOTES
> and two reports, so a G4 delta attestation follows the rework capture.

## VERDICT: PASS (no blocking corrections; 3 advisories, none blocking)

- **Gate:** G4 (integration / regression), independent reviewer (qa-engineer role), read-only.
- **Task:** M4-T014 — R3/R4-series height/setback draft rule families (D-045 A1 wave 1b).
- **Material commit reviewed:** `c8d94f38`. CI authority run **34740497612** at head `6fc8a878` (18/18 green).
- **Reproduction environment:** frozen source extracted from `c8d94f38` to an isolated scratch tree; Python 3.11.9 / pytest 8.4.2. No git writes.

All six G4 scope items and all six acceptance scenarios (S1–S6) are satisfied at the frozen candidate, independently reproduced where feasible.

---

## Item 1 — REGRESSION (PASS)

`git diff --name-status c6aca328..c8d94f38 -- services/api` returns exactly **7 files, all `A` (added), 0 modified, 0 deleted**:
- 3 rulesets: `services/api/app/rules/rulesets/{r3_r4_pitched_height,r3_2_r4_flat_height,r4b_height}.rule.json`
- 3 bundle snapshots: `services/api/app/_zr_snapshots/v1/{zr-23-42,zr-23-421-r3-r4,zr-23-422-r3-r4}.snapshot.json`
- 1 test file: `services/api/tests/rules/test_r3_r4_height.py`

- **Engine/evaluator untouched (forbidden):** no `engine*`, `evaluator*`, `dsl.py`, `registry.py`, `models.py`, `coverage.py`, `snapshots.py`, `lifecycle.py`, or `schemas/` change in the diff. Confirms S2's "DSL schema unchanged" and S6's "engine untouched."
- **No existing test edited:** the `services/api/tests/rules` diff shows only the new `test_r3_r4_height.py`.
- **Full suite count independently reproduced: 458 passed** (`PYTHONPATH=. python -m pytest tests/rules -q` at frozen source) — matches the claim, with zero pre-existing test broken. (An initial run showed 457/1-fail solely because my first extraction omitted `packages/contracts/schemas`, which `test_rules_engine.py::test_coverage_and_completeness_match_canonical_contract` reads; after extracting it, 458 passed.)

## Item 2 — SUITE INTEGRITY (PASS)

- **No suite-weakening markers:** case-insensitive search of `test_r3_r4_height.py` for `.skip/.only/.xfail/skipif/pytest.skip/TODO/FIXME/quarantine` = **no matches**.
- **90-case reconciliation:** hand-count of parametrization (AS-1 pitched 7×3=21, NC-1 8+7+5, AS-3 3+3, NC-3 3+3, NC-7 4, NC-8 5, plus singletons) = **90**, and `pytest test_r3_r4_height.py` collected & passed exactly **90**.
- **Family-membership auto-coverage mechanism verified (producer disclosure 4):** `RuleRegistry.load()` (`services/api/app/rules/registry.py`) globs **all** `*.rule.json`, raises on duplicate `rule_id`, and indexes by `family`; it is the fixture in effectively every rules test, so a malformed/duplicate new file breaks the whole suite. The **unedited pilot** `test_r5_height_setback.py::test_as6_every_family_rule_file_validates_via_dsl_loader` iterates `_RULESET_DIR.glob("*.rule.json")` — it validated the 3 new files at runtime with no pilot edit. Using the **distinct** family `residential_height_setback_r3_r4` (vs the pilot's `residential_height_setback`) keeps the pilot's exact-set assertion `sorted(fc["rule_ids"]) == sorted(_FAMILY_RULE_IDS)` green. This is genuine auto-discovery, not a bespoke hook.

## Item 3 — ACCEPTANCE SCENARIOS S1–S6 (all PASS)

- **S1 per-variant + provenance:** `test_as1_pitched_confident_wall_and_ridge_separate` (per-variant scoped 25/35), `test_as1_flat_r3_2_r4_confident_building_height_only`, `test_as1_r4b_confident_building_height_only`; provenance via `test_as2_pitched_dimensions_trace_to_snapshot_provenance` (`export()` fails closed without provenance; asserts section/quote/`last_amended`/`snapshot_id`+digest) and `test_as2_every_recorded_citation_digest_matches_snapshot`.
- **S2 typed min/max separation:** pitched emits TWO separate typed constraints (`max_perimeter_wall_height=25.0`, `max_building_height=35.0`), flat/R4B emit ONLY `max_building_height` with `assert "max_base_height" not in res.outputs` (no invented base/setback split). Units `"feet"` explicit in ruleset outputs; DSL schema unchanged (Item 1). The source states only maxima; the two distinct pitched maxima are correctly kept separate.
- **S3 fail-closed gaps:** `test_nc4_*` (building_type unavailable → PRR, no value, `COMPLETENESS_MISSING_CRITICAL`), `test_nc1_*` (out-of-enumeration → `NOT_APPLICABLE`), `test_nc8_pitched_setback_is_documented_limitation_not_numeric` (23-421 sloping-plane setback never numeric).
- **S4 negative controls + mutation binding:** cross-variant (`test_nc1_*`, incl. pitched `NOT_APPLICABLE` for R5A/R4B/R1/R2/R5/R5B/R5D/R3), cross-SECTION (`test_nc2_r4_flat_value_never_leaks_into_pitched_constraint`, `test_nc2_r4b_25_never_merges_with_r3_2_r4_35`), effective-date discipline (`test_as3_before_amendment_not_effective` at 2024-12-04 vs `test_as3_on_amendment_date_effective` at 2024-12-05). **Mutation judgement:** every numeric cap is asserted as a **hardcoded literal** in the test (`res.outputs == {"max_perimeter_wall_height": 25.0, "max_building_height": 35.0}`, etc.), never read from the ruleset — so a value drift in a `parameters[].value` fails the test. Not vacuous. The digest test reads recorded digests but independently recomputes `sha256(verbatim_excerpt)`, so it too binds real content.
- **S5 draft posture/language:** `test_as5_every_family_rule_is_needs_review_and_verified_ineligible` (status `needs_review`, `qualified_human_approval: pending`), `test_as5_family_coverage_is_conditional_never_verified`, `test_as5_no_buildable_or_compliance_language_in_rulesets`. All three rulesets carry `status: needs_review`; D-045-R009 preserved (G6 remains the only path past `needs_review`).
- **S6 regression/determinism:** 458 reproduced; engine untouched; `test_as4_determinism_byte_identical` passes; `sync_zr_snapshots.py --check` EXIT 0 (reproduced); modularity EXIT 0; CI api job green at frozen head.

## Item 4 — SNAPSHOT INTEGRITY (PASS)

- **Canonical vs bundle byte-identical:** the 3 new files have identical git blob SHAs in `docs/research/zr-snapshots/v1/` and `services/api/app/_zr_snapshots/v1/` (`zr-23-42` = `7d23f0ba…`, `zr-23-421-r3-r4` = `0d87c2c6…`, `zr-23-422-r3-r4` = `a3129b08…`). Identical blob SHA = byte-identical.
- **Sync `--check` covers all 10:** independently ran `sync_zr_snapshots.py --check` → EXIT 0, "byte-identical to the canonical source (**10 file(s)**)" (7 prior + 3 new). Guarded in-suite by `test_zr_snapshot_bundle.py` (`bundled == canonical` membership + byte-identity + subprocess `--check`), which globs all files and thus auto-covers the 3 new ones.
- **Ruleset digests match actual snapshots:** independently recomputed `sha256(verbatim_excerpt)` for all three snapshots — each equals its stored `content_digest_sha256` AND the value referenced in the consuming rulesets' `citations[].content_digest_sha256` (`68e4d147…`, `0268089074…`, `3fea4ca5…`). The 23-422 snapshot's excerpt genuinely contains BOTH the R3-2/R4 (35 ft) and R4B (25 ft) statements its two consumers quote.

## Item 5 — DETERMINISM / FLAKE RISK (PASS)

Pure deterministic evaluation over committed JSON data + snapshots; **no AI call, no network at test time** (the `curl` capture was one-time at source-capture; snapshots are committed, hash-guarded data). No wall-clock dependence — effective-date behavior is driven only by the explicit `as_of_date` fixtures. The one subprocess (bundle-guard `sync --check`) is deterministic. `test_as4` and the byte-identical exports confirm run-to-run stability. Nothing in the diff can flake CI.

## Item 6 — CI EVIDENCE CONSISTENCY (PASS)

- **Source identity verified:** `git diff --stat c8d94f38..6fc8a878 -- services/api docs/research/zr-snapshots` is **empty** — the green run at `6fc8a878` covers the exact frozen M4-T014 source. The 4 intervening commits (`7226db90`, `a085454b`, `0f71681b`, `6fc8a878`) are control-plane records + `docs/ARCHITECT_REVIEW_QUESTIONS.md` edits only, confirming the orchestrator's "later commits are control-plane/questions-doc only."
- **Counts reconcile:** evidence's "90 new / 458 total, sync EXIT 0, modularity EXIT 0" all independently reproduced.
- **Run lineage:** the two peer-cancelled runs are consistent with the branch's two questions-doc commits (a peer appending owner ZR research). I cannot re-query GitHub run IDs/cancellation without `gh`; the load-bearing fact — byte-identical source at the surviving green head — is git-verified, so this is not a gap.

---

## Advisories (none blocking; for the orchestrator / G6 / directive-compliance-verifier)

- **ADV-1 (deferred to G6, not a G4 defect):** all three snapshots carry `raw_html_verified: false` / `extraction_status: extracted_draft` (producer disclosure 1). Correct for a `needs_review` DRAFT; the numeric caps, enumeration, and building-type condition must be confirmed by a qualified zoning professional at G6 before any publish/Verified. Every rule is `needs_review`, so this is properly gated.
- **ADV-2 (disclosed, fail-closed):** the `building_type` axis values `attached`/`other` are an engineered representation of §23-422's negative definition ("residences not subject to §23-421"), not source-named building types (disclosure 2). Because no canonical `property_profile` field supplies building type, all three rules fail closed to `professional_review_required` in practice; flagged for G6.
- **ADV-3 (test robustness, optional):** `test_as5_no_buildable_or_compliance_language_in_rulesets` bans the space form `"buildable envelope"`, but the rulesets use the hyphenated `"buildable-envelope"` inside disclaimers ("not a buildable-envelope result"). The intent (no buildable-envelope *label*) is met and the disclaimers are appropriate, but the grep would not catch a hyphenated *affirmative* label; consider adding the hyphen form and `"buildable"` to the banned list in a future increment.

## Informational (not defects)

- The material commit `c8d94f38` also touched `project-control/state.json` (+2) and `project-control/tasks/M4-T014.json` (+16), which are in the packet's `forbidden_paths`. These are orchestrator lifecycle edits bundled into the integration commit (the producer report states work was left uncommitted in the worktree); not a producer scope violation.
- The write to canonical `docs/research/zr-snapshots/v1/` sits outside the literal `allowed_paths` bundle path but was pre-approved by the orchestrator packet correction (progress_log at 50%), is required by the established sync guard, and is not in `forbidden_paths` (disclosure 3) — already reconciled. This is an in-regime scope note for the `directive-compliance-verifier`, whose separate DCV pass (D-045 R001/R008/R009, D-046 R001/R002) is out of this G4 scope.

## Requested action
Record **G4 = PASS** for M4-T014 at material commit `c8d94f38` / CI head `6fc8a878`. No rework required for this gate.
