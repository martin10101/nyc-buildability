# M0-T073 directive-compliance verification — verbatim reviewer return (round 1)

Preserved verbatim by the orchestrator (report-preservation rule; transport
entity-decoding only). Verifier: independent directive-compliance-verifier
subagent, read-only, at frozen HEAD `6bfc60a`. Producer ≠ verifier.

---

## Verdict summary — M0-T073 @ frozen HEAD `6bfc60a` (branch `task/M0-T073-modularity-enforcement`)

**Applicable D-017 rows re-derived from `requirements.json`: exactly 9 (R105–R113)** — confirmed by resolver, not by the producer's map:
```
$ python -c "...json.load(requirements.json); [r for r in rows if 'M0-T073' in r['applicability']['task_ids']]"
TOTAL 123 SELECTED 9   → D-017-R105 … D-017-R113
```

| Req ID | Verdict | Evidence (re-derived at 6bfc60a) |
|---|---|---|
| **D-017-R105** | **PASS** | Permanence is structural, not narrative: 5 committed artifacts (`CLAUDE.md` p16, `AGENTS.md` §Modularity, `.claude/rules/code-architecture.md`, `docs/CODE_MODULARITY_POLICY.md`, `tools/modularity_check.py`+baseline+exceptions) plus an unconditional CI job — none depends on session state or initiative scope; policy §preamble states "permanent repository law, not initiative-scoped". |
| **D-017-R106** | **PASS** | All 7 item-1 bullets located verbatim-in-substance in CLAUDE.md principle 16 (bullet map below); `python tools/context_budget_check.py` → `PASS`, eager total 2920 tok vs 6000 budget. |
| **D-017-R107** | **PASS** | `AGENTS.md` §"Modularity (permanent)" names all 5 finding classes explicitly: responsibility mixing, excessive module growth, giant functions, hidden coupling, giant generic utility modules — framed as "treat as FINDINGS". |
| **D-017-R108** | **PASS** | Frontmatter `services/**/*.py`, `tools/**/*.py`, `packages/**/*.py`, `apps/web/src/**/*.ts`, `apps/web/src/**/*.tsx` covers Python+TS+TSX production roots (matches `git ls-files` layout); all 10 mandated behaviors present (map below); format identical to sibling path rules and confirmed non-eager by the budget checker. |
| **D-017-R109** | **PASS** | All 12 item-4 contents map to §§1–12 of `docs/CODE_MODULARITY_POLICY.md` (map below); all six boundary-example domains (Python, TS, React, API, storage, rule-engine) present in §5. |
| **D-017-R110** | **PASS** | All 12 behaviors verified in code and, where testable, by execution. Determinism proven by byte-compare: two `--check --json` runs are md5-identical (`bc3801ec…`). Real-repo run: 240 files, 0 failures, 4 symbol-ceiling warnings, exit 0. |
| **D-017-R111** | **PASS** | All 7 questions present, numbered (1)–(7), in `.claude/skills/start-controlled-task/SKILL.md` step 3; `.claude/skills/run-quality-gate/SKILL.md` instructs checking them "against the ACTUAL diff". |
| **D-017-R112** | **PASS** | 4/4 channels: `ci.yml` `on: {push: None, pull_request: None}` — no path/branch filter, `modularity` job has no `needs`/`if` → runs on every source PR; CLAUDE.md is eager-loaded (budget checker lists it); AGENTS.md is root; path rule frontmatter matches the working convention. |
| **D-017-R113** | **PASS** | All 7 proofs have named, individually passing tests; `pytest -v` → 17/17 PASSED including `RealRepoTests::test_committed_check_passes` and `test_committed_baseline_integrity`. |

**Overall D-017 verdict: PASS (9/9).**
**D-001 process: PASS with one required correction** — see Finding 1.

---

### R106 — seven mandated statements → CLAUDE.md principle 16
1. clear responsibilities / stable module boundaries → "design production code around clear responsibilities and stable module boundaries" ✓
2. no unrelated domain+storage+serialization+I/O+CLI/API+presentation in one file → "never put unrelated domain logic, storage, serialization, external I/O, CLI/API wiring, and presentation in one large file" ✓
3. inspect size/responsibilities/dependencies before growing → present verbatim ✓
4. prefer focused modules, explicit interfaces, focused tests → ✓
5. preserve public imports through compatibility facades when splitting → ✓
6. new oversized files + unjustified growth prohibited by policy **and CI** → "prohibited by the modularity policy and fail CI" ✓
7. read `docs/CODE_MODULARITY_POLICY.md` + the path-scoped rule when creating/expanding/decomposing → names both the policy and `.claude/rules/code-architecture.md` ✓

### R108 — ten mandated behaviors → rule file items
inspect-first (1) · identify boundary (2) · no convenient-file appending (2) · separate the six responsibility classes (3) · focused tests for extracted behavior (4) · preserve public interfaces (4) · avoid circular deps (4) · no `utils.py`/`helpers.py`/`common.ts` dumping grounds (5) · report cohesion when crossing a threshold (6) · run the checker before checkpoint (7). **10/10.** File is 35 lines — compact, depth deferred to policy as mandated.

### R109 — twelve policy contents → sections
cohesion rules §2 · boundary examples (Py/TS/React/API/storage/rule-engine) §5 · soft+hard thresholds §3 · function/class complexity §4 · interface preservation §6.3 · circular-dep prevention §6.4 · tests-before-extraction §6.1 · exclusions (generated/schemas/migrations/fixtures/data-driven) §9 · reviewed-exception process §8 · safe large-file refactoring §6 · anti-over-fragmentation §11 · measured & enforced §10+§12. **12/12.**

### R110 — twelve checker behaviors, each re-derived
| # | Behavior | Where / how verified |
|---|---|---|
| 1 | handwritten production only | `INCLUDE_RULES` + `selected_files()` from `git ls-files` |
| 2 | excludes generated/vendored/lock/schema/migration/fixture | `EXCLUDED_SEGMENTS` (+ `_is_test_file`); `test_4` passes with 3 oversized excluded files → `selected_files: 0` |
| 3 | new file > hard threshold fails w/o exception | `new_oversized`; `test_2` exit 1 |
| 4 | grandfathered file material growth fails | `baseline_growth`, `max(50, 10%)`; `test_3` exit 1, `test_3b` in-limit passes |
| 5 | reports > warning threshold | `review_signal` warning; `test_warnings_do_not_fail…` |
| 6 | top-level symbols where reliable | `PY_SYMBOL` (reliable) / `TS_SYMBOL` labelled "(approximate count)"; live run emitted 4 such warnings |
| 7 | versioned reviewed baseline | `modularity_baseline.json` v1, 23 entries, `thresholds` recorded |
| 8 | baseline not casually regenerated | SHA-256 `baseline_digest` integrity + `--approval-id` gated + carry-forward `min(recorded, current)`; `test_7` proves refusal, carry-forward at 1400 (not 1500), and digest-mismatch fail |
| 9 | deterministic output | **byte-identical** repeat runs (md5 `bc3801ec1f814c4256aa76af7d7ac1ba` twice); sorted selection/warnings |
| 10 | explicit expiring path-exact exceptions w/ owner+reason+review evidence | `load_exceptions()` requires all four fields, rejects globs/dirs/unknown targets/duplicates; `test_5/6/6b/6c` |
| 11 | line count never proof architecture is bad | module docstring + JSON payload `note` field + policy §1 |
| 12 | passing count never excuses mixing/coupling | same `note` + policy §1 + AGENTS.md + rule file closing line |

### R113 — seven proofs → passing tests
`test_1_normal_focused_module_passes` · `test_2_new_unjustifiably_oversized_module_fails` · `test_3_growth_of_grandfathered_oversized_file_fails` · `test_4_excluded_generated_file_does_not_fail` · `test_5_valid_exception_is_narrow_and_temporary` · `test_6_expired` + `test_6b_broadened` + `test_6c_incorrectly_targeted` · `test_7_regeneration_cannot_silently_erase_debt`. All PASSED.

---

## D-001 process compliance

| Item | Result |
|---|---|
| Regime stamp on packet | PASS — `directive_regime_version: "1.0"`, `directive_regime_entered_at` present |
| Directive refs | PASS — `[{D-001: ALL}, {D-017: ALL}]` |
| G0 recorded | PASS (result PASS, `reviewed_sha 57b80c2`, report `M0-T073-G0-readiness.md`) — **but uncommitted, see Finding 1** |
| G2 recorded | PASS (result PASS, role `self_check`, `reviewed_sha 86ede7f`) — **but uncommitted, see Finding 1** |
| Producer report | PASS — `project-control/reports/M0-T073-producer-report.md`, committed |
| Evidence map | PASS — `project-control/reports/M0-T073-evidence-map.json`, committed, `reviewed_sha ad3408d` |
| `reviewed_sha` present | PASS — in evidence map and both gate records |
| No `project-control/directives/` changes | **PASS** — `git diff 57b80c2..HEAD --stat` lists 15 files, none under `directives/` |
| Registry integrity | PASS — `validate_directive_compliance.py` → "directive registry OK: 17 directive(s), 17 active" |
| Producer ≠ verifier | PASS — `verification.json` M0-T073 entry is still a PENDING stub (`verifier: ""`), i.e. not self-verified |

---

## Findings

**Finding 1 (required correction, process — not a D-017 row failure).** The G0 and G2 gate records are **untracked working-tree files**, not present at the frozen HEAD:
```
$ git status --porcelain
 M project-control/state.json
?? project-control/gates/M0-T073-G0.json
?? project-control/gates/M0-T073-G2.json
?? project-control/reports/M0-T073.json
$ git ls-files project-control/gates/ | grep T073   → (no output, exit 1)
$ git ls-files project-control/gates/ | wc -l        → 408   (M0-T070/T071 gates ARE tracked)
```
Commit `6bfc60a` is titled "M0-T073: record G2 self-check PASS" but contains no gate file — `git diff ad3408d..HEAD --stat` shows only `evidence-map.json` and `tasks/M0-T073.json`. Anyone verifying at the frozen content identity would not find the gate evidence. Repo convention (408 tracked gate records) is to commit them. `state.json` (modified) and `reports/M0-T073.json` are likewise uncommitted. **Orchestrator should commit the gate records + state before the next gate/accept.**

**Finding 2 (informational).** Producer report and evidence map claim `239 selected files`; re-derivation at HEAD gives **240**. Most likely the producer ran the checker before `git add` of `tools/modularity_check.py` (selection is `git ls-files`-based). Immaterial to any requirement, but the number in the committed evidence is not reproducible.

**Finding 3 (informational).** `.claude/hooks/*.py` and `.github/scripts/*.py` are handwritten Python outside both the path rule's frontmatter and the checker's `INCLUDE_RULES`. This is a documented, deliberate scope decision (policy §9 enumerates the measured roots), so it is not a R108/R110 failure — but it is the one place where "handwritten production source" was interpreted narrowly, and it should be an explicit review item if those trees grow.

**Finding 4 (cosmetic).** CLAUDE.md's routing paragraph still enumerates path-scoped rules as "(project-control, apps/web, services/api, geospatial data, legal/rules, deployment)" and was not extended to mention `code-architecture`. Non-binding narrative; the rule loads by frontmatter regardless.

**Non-finding checked and cleared.** The `M0-T073-initial-baseline` regeneration approval expires 2026-08-25, which could have been a time bomb; `load_exceptions()` deliberately makes an expired `baseline-regeneration` entry inert for `--check` (only `--regenerate-baseline` refuses it), proven by `test_7b`. `--check` will not start failing on 2026-08-26.

---

## Exact commands and output tails

```
$ git rev-parse HEAD                       → 6bfc60a7c44c3ec5671bd20f7f3eda368a7baab8
$ git diff 57b80c2..HEAD --stat            → 15 files changed, 1158 insertions(+), 69 deletions(-)   [no project-control/directives/**]

$ python tools/context_budget_check.py
  ---- eager total: 11870B  146L  ~2920 tok  (budget 6000 tok)
  PASS - automatic context budget within limits; no stale/duplicate/retired regressions.   EXIT=0

$ python tools/modularity_check.py --check --json > mc1.json; python ... > mc2.json; cmp mc1.json mc2.json
  EXIT1=0  EXIT2=0  BYTE-IDENTICAL
  bc3801ec1f814c4256aa76af7d7ac1ba  mc1.json
  bc3801ec1f814c4256aa76af7d7ac1ba  mc2.json
  "selected_files": 240, "failures": [], warnings: 4 × symbol_ceiling

$ python -m pytest tools/test_modularity_check.py -v
  17 passed in 3.49s   (all seven proof tests PASSED individually)

$ python tools/validate_directive_compliance.py
  directive registry OK: 17 directive(s), 17 active; source hashes, ID append-only,
  and producer/verifier separation verified.
```

**Files re-derived:** CLAUDE.md, AGENTS.md, .claude/rules/code-architecture.md, docs/CODE_MODULARITY_POLICY.md, tools/modularity_check.py, tools/modularity_baseline.json, tools/modularity_exceptions.json, tools/test_modularity_check.py, .github/workflows/ci.yml, .claude/skills/start-controlled-task/SKILL.md, .claude/skills/run-quality-gate/SKILL.md, project-control/tasks/M0-T073.json, project-control/gates/M0-T073-G0.json, project-control/gates/M0-T073-G2.json, project-control/reports/M0-T073-producer-report.md, project-control/reports/M0-T073-evidence-map.json, project-control/directives/D-017-a-to-z-completion-authorization/{requirements.json,source-002-amendment.md,verification.json}.
