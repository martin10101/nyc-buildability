# M5-T033 G4 QA review (verbatim reviewer return; qa-engineer, read-only, pinned 62dd97cb)

Saved verbatim by the orchestrator per the report-preservation rule. (The reviewer landed in
a worktree whose HEAD lacked the material and correctly verified everything via git plumbing
at the pinned SHA rather than trusting its working tree.)

---

**VERDICT: PASS**

## G4 QA Gate Report — M5-T033

**Reviewer:** qa-engineer (read-only) · **Reviewed at pinned SHA:** `62dd97cb` (material `00be16d3`, ancestor-verified) · **Method:** worktree HEAD (`d8b3899f`) is NOT an ancestor of the pinned SHA, so every artifact was read via `git show 62dd97cb:<path>` — working-tree files were not trusted. Executable authority = orchestrator-captured CI green + 654 focused tests passed at `00be16d3`.

### AS-by-AS coverage

| AS | Evidence | Verdict |
|----|----------|---------|
| AS-1 (flag-unset → uniform absent, every BBL) | `test_live_provider.py::test_m5t033_flag_off_absent_for_every_bbl_zero_calls_no_log` (parametrized both D-059 BBLs: asserts `None` + zero ztldb/lot/layer calls + zero fail-safe log lines); route `test_rule_evaluation_api.py::test_m5t033_flag_off_uniform_absent_zero_connector_calls` (200, `spatial_intersection_absent`, `professional_review_required`, district None, evaluations [], zero calls); evaluator `test_rules_integration.py::test_m5t033_absent_substrate_uniform_spatial_intersection_absent` (both BBLs) | COVERED |
| AS-2 (flag-on + injected failure → typed per-parcel fail-safe, distinct) | `test_live_provider.py::test_m5t033_flag_on_connector_failure_absent_but_calls_and_logs` (both BBLs: `None` BUT `ztldb_calls==[(bbl,CID)]`, exactly 1 `connector_error` line, canary text absent); route `test_m5t033_flag_on_connector_failure_same_reason_but_connector_consulted` (200 not 500, same reason, connector consulted w/ matching X-Correlation-ID, 1 log line, canary not in log or body) | COVERED |
| AS-3 (both parcels exercised; no test claims runtime confirmed) | Parcels `3052960043`/`3022647515` parametrized at provider + evaluator; counterexample `test_m5t033_shared_connector_failure_is_uniform_absent_flag_on` exercises both + control `1008350041`; docstrings state "asserts nothing about the live runtime" | COVERED |
| AS-4 (one causal account; owner check is sole remaining confirmation; no M4-T020/B4-fixes-it claim) | Report §1 (default provider → None; two branches marked NON-EXHAUSTIVE; uniformity/latency "suggestive not decisive") + §2 (both readings, exact expected observations); "M4-T020 / B4 does NOT fix this" in §1 + checklist §6b | COVERED |
| AS-5 (checklist names both flags w/ defaults, location, post-restart probe; content preserved) | Checklist §6a names `LIVE_SPATIAL_PROVIDER_ENABLED` + `INTERNAL_SCENARIO_ENABLED` (absent=disabled, nycdf-api→Environment) + §6b two post-restart probes; diff is pure insertion (`@@ -248,6 +248,127`) + 3 additive reference rows, **0 deletions** | COVERED |
| AS-6 (ruff + python checks; api CI green at seam) | Seam evidence: CI success at `00be16d3`; orchestrator local `654 passed in 19.64s`. Producer §4 honestly flags its own from-worktree-root `No module named 'app'` collection artifact (thin-client); authority is the orchestrator-captured run — correct ADR-005 posture | COVERED (orchestrator-captured) |
| AS-7 (orchestrator-captured D-066-R003 comparison + Codex D-066-R002 graph statement) | `M5-T033-graph-comparison.md`: ~59min/1run vs ~181min/2runs, advisory with 4 stated limits, token half marked UNVERIFIABLE for baseline (no savings claim); Codex "useful navigation, accuracy unverified" on record | COVERED |

### Findings
- **No AS gap.** Every scenario maps to a concrete test or committed evidence artifact; every named test exists at the pinned SHA and its assertions meet or exceed the report's claims. No test asserts less than the report states.
- **Regression risk to the 654-test suite: nil.** The three production source edits (`live_provider.py`, `rule_evaluation.py`, `integration.py`) are **comment-only** (verified in the `00be16d3` diff — no code path/signature/token change). All three test-file changes are **additive appends** (135/19/121 insertions, **0 deletions**) — no pre-existing test modified or removed. Helper signatures (`_profile(bbl=...)`, `RecordingFetchers(ztldb=...)`, `RecordingLiveFetchers(label=/ztldb=)`) and referenced symbols all exist at the SHA and are compatible.
- **Provenance/rigor is strong.** Report and checklist consistently separate reproduced code behavior from the pending owner-only runtime check; the security-relevant "canary detail never leaks to log or response" is asserted in tests. The evidence-map covers D-059-R004 and D-066 R001–R004 (full directive re-derivation is the directive-compliance-verifier's gate, not this G4 pass).
- **Minor (non-blocking):** AS-2's route-level test injects the connector failure at the ztldb fetcher only; the "any connector" breadth is carried by the pre-existing `test_s3_any_connector_failure_yields_absent_substrate`. Adequate — noted for completeness, not a defect.

### Verdict
**PASS.** All AS-1..AS-7 have genuine, reproducible coverage at the pinned SHA; no under-assertion; no regression exposure. Executable authority (CI green + 654 passed at `00be16d3`) stands.
