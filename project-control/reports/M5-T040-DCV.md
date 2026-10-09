# M5-T040 — directive-compliance verification (verbatim verifier return; transport entity-decoding only)

Saved by the orchestrator from the directive-compliance-verifier agent return, 2026-09-18
(seq-118 wave, frozen head b4865d1c). Nothing added or removed beyond decoding transport
HTML entities.

---

All evidence reproduced. Validator exits 0 (registry integrity intact at the frozen head). Here is my verdict.

---

# Directive-Compliance Verification — M5-T040 (D-001 regime)

**Frozen head:** `b4865d1c` on `candidate/D-024-mrl-option-b` · materials `987930a2` + `751a1826`
**Verifier:** directive-compliance-verifier (read-only; producer ≠ verifier)
**Verdict: PASS** (all five cited requirements SATISFIED on reproduced primary evidence)

## Applicability (self-confirmed on the LOADED registry)
`DirectiveRegistry(Path('project-control/directives')).load().evaluate_task_refs(M5-T040.json)` →
`ok:True, applicable_ids == cited_ids == ['D-045-R002','D-045-R008','D-045-R009','D-066-R001','D-073-R006']`, `missing_ids:[]`, `invalid_refs:[]`. Applicable == cited exactly.

**Frozen-head identity:** current HEAD `7b7e7faf` = `b4865d1c` + one control-plane-only commit (`git show 7b7e7faf --name-only` = `state.json`, `tasks/M5-T040.json`). `b4865d1c` itself touched only `reports/M5-T040-ci-evidence.md` + `evidence-map.json`. Material source frozen since `751a1826` (`git log 751a1826..HEAD -- <material source>` empty). `751a1826..4d8847c6` and `4d8847c6..b4865d1c` both empty over `apps/ services/ packages/` — so CI run 35407153078 (headSha `4d8847c6`) speaks for the frozen-head material identity.

## Per-requirement verdicts

| Req ID | Class | Verdict | Primary evidence I personally reproduced |
|---|---|---|---|
| **D-045-R002** | obligation | **PASS** | Named-street exceptions leg wired fail-closed in `services/api/app/rules/wide_street_wiring.py`: `build_named_street_override_status` (L363-487) — MATCHED_OVERRIDE returns override provenance (snapshot_sha256/section_anchor/provision_id/verbatim row) with reason "the alternate/named-street width is NOT applied numerically and the wide-street FAR is withheld — professional review required" (L425-450); INDETERMINATE / not-fully-resolved / empty-list → unresolved refusal (L403-413, 451-476); all-NOT_MATCHED clears only via `_fully_resolved_typed_inputs` (L335-360) re-establishing typed inputs independently of the matcher's coercing short-circuit; `_elevated_exceptions_checked` (L269-290) returns False on any match/unimplemented-but-applicable exception. Truth-table tests in `tests/rules/test_wide_street_wiring.py` (L681-917, oracle+wiring assertions incl. malformed-input defenses). **Reproduced: 98 passed** (matcher+wiring); **475 passed** (consumer suites); CI 35407153078 success @ `4d8847c6` (api/web/web-e2e all green). |
| **D-045-R008** | sequencing | **PASS** | `git show 987930a2 --name-only` + `git show 751a1826 --name-only`: union = 11 files, every one ∈ `allowed_paths` (M5-T040.json L32-48). No `*.rule.json` (`git diff --name-only -- "*.rule.json"` empty). Contract files byte-untouched — `integration.py`, `response.py`, `schema*`, `*.gen.ts` in neither material commit. One bounded increment (the ZR 12-10 named-street exceptions leg), not a monolithic all-districts task; M5-T023/T024 and D-043 walkthrough untouched (not in diff). |
| **D-045-R009** | prohibition | **PASS** | `git show 987930a2 751a1826 -- <source>` added-line grep for `published\|verified\|compliant\|compliance` → the ONLY hit is `draft_label: "DRAFT — not a verified legal determination"` (a preservation/negative assertion, not a claim). DRAFT/not-verified assertions survive in display tests: `development-limits.test.tsx` L541/L564/L425; `report-view.test.tsx` L114 (`"DRAFT - not a Verified determination (D-045-R009)"`). Alternate-width provisions kept professional_review_required-class (`wide_street_wiring.py` L430-432). |
| **D-066-R001** | obligation | **PASS** | Packet `M5-T040.json` L12 carries the CODE-GRAPH NAVIGATION BLOCK (regenerated at seam HEAD 198c24f8) naming the wiring consumers with exact anchors — `integration.py:56,514-520`, `api/v1/rule_evaluation.py:74`, `spatial/wide_street_live_provider.py:100`, suites `test_rule_evaluation_api/test_rules_integration/test_wide_street_wiring` — and instructs "`python tools/code_graph/query.py --no-regen impact <path>` BEFORE broad sweeps; graph is ADVISORY — verify every material conclusion in source." Producer report L5 references it. `tests/api` + `test_rules_integration` ∈ allowed_paths (L37-38), **475 passed reproduced** + CI green. Modularity crossing disclosed: `modularity_check --check` → 443 files, **0 failures, exit 0**, warning `wide_street_wiring.py - above the warning threshold`; producer report L67-69 + commit 751a1826 disclose the cohesion signal. |
| **D-073-R006** | obligation | **PASS** | Records-vs-allowances distinction gated on `determination_state`, no reference-value-as-result. `DevelopmentLimits.tsx` `WideStreetResult` (L62-96): "gate the ENTIRE presentation on determination_state" (L65-69); not-within → heading "Governing floor-area ratio", never "Wide-street conditional FAR" (L70-78); review → higher FAR withheld (L82); PLUTO reference rendered as a SEPARATE concept "Residential FAR · city record"/"PLUTO reference" (L115-119, testid `development-reference-far`) vs "Evaluated residential FAR" showing "Not calculated" when unsupported (L122-124). `CalculationEvidence.tsx` L12-19,42-47: review label + withheld FAR gate on `determination_state`, never a null-FAR heuristic. `ReportView.tsx` L72 renders the shared `DevelopmentLimits` → structural screen/report parity. Tests: `report-view.test.tsx` L170-227 (conservative not-within captioned "Governing floor-area ratio" on both screen AND report), L142-165 (review label gates on determination_state); web proves in CI (web+web-e2e green @ 4d8847c6). |

No VIOLATED / UNVERIFIABLE result. Every requirement judged on reproduced primary evidence, not the producer's matrix (the report self-labels PARTIAL; I reproduced all suites and diffs independently).

## Conditional restamp PRE-AUTHORIZATION (later head <H>)
My PASS verdict at `b4865d1c` carries to a later head `<H>` for recording DCV `verification.json` (reviewed_sha=`<H>`) WITHOUT re-running per-requirement evidence, **iff ALL FIVE conditions hold at the record state** (M5-T041 five-condition pattern):

1. `git diff --name-only b4865d1c..<H> -- apps/ services/ packages/` is **empty** (product dirs unchanged).
2. The 11 allowed_paths material files are **byte-identical (LF-normalized)** between `b4865d1c` and `<H>`.
3. `M5-T040.json` `directive_refs` + `allowed_paths` unchanged, and evidence-map `material_commits` (`987930a2`, `751a1826`) unchanged.
4. `git diff --name-only b4865d1c..<H>` touches **only `project-control/**`**.
5. `python tools/validate_directive_compliance.py --check` exits **0** at the record state.

Any condition failing voids this pre-authorization; a fresh evidence pass is required.

## Exact read-only commands run
- `git rev-parse HEAD` / `--abbrev-ref HEAD` / `git log --oneline -8`
- `DirectiveRegistry(Path('project-control/directives')).load().evaluate_task_refs(<M5-T040.json>)`
- `git show 987930a2 --name-only` ; `git show 751a1826 --name-only` ; `git show 7b7e7faf --name-only` ; `git show b4865d1c --name-only`
- `git diff --name-only 987930a2^..751a1826 -- services/api/app/rules/integration.py services/api/app/rules/response.py "…schema*" "…*.gen.ts"` ; `-- "*.rule.json"`
- `git log --oneline 751a1826..HEAD -- <material source files>` ; `wc -l <material source>`
- `git show 987930a2 751a1826 -- services/api/app apps/web/src/components | grep '^+' | grep -iE 'published|verified|compliant|compliance'`
- `git diff --name-only 751a1826..4d8847c6 -- apps/ services/ packages/` ; `4d8847c6..b4865d1c -- apps/ services/ packages/`
- `cd services/api && python -m pytest tests/rules/test_named_street_override.py tests/rules/test_wide_street_wiring.py -q` → 98 passed
- `cd services/api && python -m pytest tests/api tests/rules/test_rules_integration.py -q` → 475 passed
- `cd services/api && python -m pytest tests/spatial/test_wide_street_live_provider.py -q` → 38 passed
- `cd services/api && python -m ruff check .` → All checks passed
- `python tools/modularity_check.py --check` → 443 files, 0 failures, exit 0
- `python tools/validate_directive_compliance.py --check` → exit 0
- `gh run view 35407153078` (+ `--json headSha,conclusion,status,headBranch`) → success @ `4d8847c6`
- Read: `M5-T040.json`, three `requirements.json`, `M5-T040-ci-evidence.md`, `M5-T040-evidence-map.json`, `M5-T040-producer-report.md`, `wide_street_wiring.py` (L260-500), `DevelopmentLimits.tsx` (L60-134); Grep across `wide_street_wiring.py`, `test_wide_street_wiring.py`, `CalculationEvidence.tsx`, `ReportView.tsx`, `development-limits.test.tsx`, `report-view.test.tsx`.

**RETURN TO ORCHESTRATOR: PASS** — record D-045-R002, D-045-R008, D-045-R009, D-066-R001, D-073-R006 as SATISFIED at reviewed_sha `b4865d1c` (restamp to `<H>` per the five conditions above). I performed no writes.
