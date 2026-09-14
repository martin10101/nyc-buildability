# M5-T028 Independent Directive-Compliance Verification (D-001) — DCV Report

> Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent return
> (2026-09-14; transport entity-decoding only, per the report-preservation rule).
> Verifier ≠ producer ≠ gate reviewers.
>
> **This report CLOSES D-059-R003 project-wide**, superseding the deliberately scope-limited
> ruling recorded in `M5-T027-dcv-verification.md`.

## Verification environment

`git rev-parse --show-toplevel` = `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (primary checkout, not a worktree). HEAD **moved twice** during my read-only review — from the pinned `f640805b` to `486862ec` to `f04b1d714ce6deaab76d9e44ff99923c98545184` — via six new commits, all `M4-T021` gate/delta-attestation bookkeeping (a disjoint task). I treated this as the anticipated "possibly one or two later control-plane-only commits" scenario and re-verified at the final live HEAD rather than stopping at the stale pin.

## 1. Restamp ruling

**General condition** (any accept-time head H): H is safe to restamp `reviewed_sha` at without re-gating iff (1) no commit between the gate-recorded heads (`f1955348`/`99f9b277`/`2e5f7528`/`d232ab0a`) and H touches any M5-T028 `allowed_paths` entry or its producer report; (2) `project_control._task_git_identity(reg_mod, task)` recomputed **live at H** (no `reviewed_sha` arg) reproduces the gate-recorded `content_manifest_sha256 = 1b1c4bab5cfe6f64d2db568e57eaaa1dcf208cfda7c86ce11c720e9ffd608648` with `error = None` (clean tree); (3) `allowed_paths`/`forbidden_paths`/`directive_refs` are byte-unchanged from gate-review time.

I verified this condition holds at **two successive live heads** that appeared during my own session:
- `486862ec…` — recompute required an exact-HEAD reviewed_sha (`frozen_git_identity` fails closed if `reviewed_sha != live HEAD`); HEAD had already advanced again by the time I ran it.
- `f04b1d714ce6…` (final, current) — `_task_git_identity` (live) returned `identity = 1b1c4bab…` (exact match), `resolved_sha = f04b1d714ce6…`, `error = None`.

All six intervening commits (`d9ac9596`, `fbd7b0ee`, `14af4e20`, `486862ec`, `275c166c`, `f04b1d71`) touch only `project-control/gates/M4-T021-*.json`, `project-control/reports/M4-T021-G{3,4}-delta-attestation.md`, `project-control/state.json`, `project-control/tasks/M4-T021.json`, and `services/api/app/connectors/wide_street_buffer_engine.py` (M4-T021's own disjoint file) — **zero** touch to any M5-T028 path, confirmed by direct `git diff --name-only` (empty). `project-control/tasks/M5-T028.json` is byte-identical across the entire range `f640805b..f04b1d71` (empty diff). The reviewer-roster correction (`88ad3a9f`, adding `security-reviewer`) is the **only** field-level change to the task packet anywhere in the reviewed history, and it touched `reviewer_agents`/`progress_percent`/`updated_at` only — `allowed_paths` and `directive_refs` are byte-unchanged across the full `f1955348..f04b1d71` span (confirmed via `git log -p` over that range).

**Ruling: acceptance may safely restamp `reviewed_sha` at the live HEAD at accept time** (currently `f04b1d714ce6deaab76d9e44ff99923c98545184`), condition holding.

## 2. Per-requirement verdicts

| Requirement | Verdict | Evidence I personally inspected | Note |
|---|---|---|---|
| **D-059-R003 — task-scope** | **PASS** | Read all 5 production diffs directly (`git show 7e7cd85e -- services/api/app/scenario/{derive,breakeven,comparison,ranking,sensitivity}.py`): every one of the 10 live emission sites now calls a per-call `_x_label(_cap_section_reference(scenario_document))`, reusing `builder._cap_citation_section` (the M5-T027 seam) via `derive._cap_section_reference`. Confirmed OLD code was unconditional via `git show <parent-of-7e7cd85e>:derive.py` — both old call sites (lines 263, 484) read the bare module constant with zero district-family branching. Ran `pytest services/api/tests/scenario -q` myself → **443 passed**; ran `-k d059` → **12 passed** (the new derivation tests, including the R6-R12 test which builds its document via the real `build_scenario(profile, rule_evaluation)` — the identical function the live route calls). | — |
| **D-059-R003 — DIRECTIVE-LEVEL (project-wide) closure** | **PASS — CLOSED** | (a) Every remaining `"23-21"` literal outside test files (`grep -rn "23-21" services/api --include="*.py" \| grep -v tests`) is either a parameterized alias `X_LABEL = _x_label("23-21")` or a code comment; I proved each alias is genuinely unreachable from the live path: `scenario_analysis.py`'s import block (lines 107-114) imports only `NOT_VERIFIED_DISCLAIMER, ThresholdResponseMetric, analyze_scenario_sensitivity, build_scenario, compare_scenario_assumption_sets, find_scenario_threshold, rank_scenario_assumption_sets` — none of the six `_LABEL`/`_METRIC_LABELS` constants; `_rebuild_scenario` (scenario_analysis.py:462-553) *always* builds `scenario_document` server-side via `build_scenario(profile, rule_evaluation)` and the request body is structurally forbidden (`FORBIDDEN_FACT_KEYS`, checked at every depth) from supplying/overriding it. I traced `builder.py:344` (`"cap_label": C.draft_cap_label(cap_section) if cap_value is not None else None`) and confirmed `draft_cap_label` always returns a non-`None` string — so whenever `derive.py`'s `cap_raw` (== `cap_value`) is non-`None`, `cap_label` is *already* a correctly-derived string, meaning `derive.py`'s own `else DRAFT_CAP_LABEL` fallback (line 525) requires a scenario-document state `builder.py` never produces. (b) Swept beyond the five modules: `grep -rn "23-21\|under ZR\|(ZR " services/api --include="*.py"` (non-test) found nothing else — `evidence.py:32`'s "ZR 23-21" is inside the module `"""docstring"""` (lines 1-64), never serialized into a response; `wide_street_buffer_engine.py`/`dcm_street_width_*.py`'s ZR 23-22/12-10 references are for the unrelated, genuinely-fixed "wide street" definition, not the FAR-cap family split. No sixth defective module found. (c) Confirmed on the live wiring, not merely tests, via the trace above. | Supersedes the M5-T027 DCV's explicit "remains OPEN project-wide until M5-T028 completes" ruling — that condition is now discharged. |
| **D-046-R001** (scale-up, ≤3 concurrent, disjoint) | **PASS** | Independently read `project-control/tasks/M4-T021.json` progress_log (claimed `2026-09-14T09:05:42Z`, rework `09:40:40Z`, in_progress `09:59:41Z`) against `M5-T028.json` progress_log (claimed `09:22:44Z`, G2 self-check content `reviewed_at 09:45:31Z`): M4-T021's producer was active throughout M5-T028's entire producer window — 2 concurrent writing producers, within the ≤3 ceiling. | Gate reports (G3/G4) deferred this to DCV as outside code-review scope; I verified it myself from primary task-packet timestamps, not from any gate's claim. |
| **D-046-R002** (disjointness mandatory) | **PASS** | Directly compared `allowed_paths`: M4-T021 = `{connectors/wide_street_buffer_engine.py, its test, its report}`; M5-T028 = `{derive,breakeven,comparison,ranking,sensitivity}.py + 5 tests + its report}` — zero overlap. `git show 7e7cd85e --stat` = exactly 11 files, all inside M5-T028's own `allowed_paths`, none of M4-T021's or M5-T027's (`constants.py`/`builder.py` — both `forbidden_paths` — untouched, confirmed). | — |

`DirectiveRegistry.load().evaluate_task_refs(task)` reproduced myself: `applicable_ids == cited_ids == ['D-046-R001', 'D-046-R002', 'D-059-R003']`, `missing_ids: []`, `unresolved: []`, `ok: True` — exactly the three IDs, nothing more/less. `python tools/validate_directive_compliance.py --check` exits 0 (ran twice, at two different live heads, both clean).

## 3. Material-identity statement

- `git diff 7e7cd85e8d1fb6dcf40cfde142931f720383f532 99f9b277efdae2cef9d94e2e9213402532f7841e -- <10 content/test files>` = 0 lines (byte-identical cherry-pick onto the integration head).
- `git diff 99f9b277… f04b1d714ce6…(current HEAD) -- <10 files + producer report>` = 0 lines for every file — content byte-stable through 12 intervening control-plane commits.
- Recomputed `project_control._task_git_identity` **live at current HEAD** = `1b1c4bab5cfe6f64d2db568e57eaaa1dcf208cfda7c86ce11c720e9ffd608648`, `error = None` — exact match to the value recorded in `M5-T028-G2.json`, `G3.json`, `G4.json`, `G5.json`.
- Self-checks reproduced directly by me (not trusted from reports): `pytest services/api/tests/scenario -q` → 443 passed; `pytest services/api/tests/scenario/test_scenario_contract.py -q` → 28 passed; `ruff check .` (from `services/api`) → All checks passed; `python tools/modularity_check.py --check` → 0 failures, 18 warnings (includes the pre-existing `breakeven.py` review-signal warning — file was already 784 lines, above the 750 "justify" threshold, before this task's +29 net lines; not a new crossing, not a failure).

## 4. Blocking discrepancies

**None.** One non-blocking item carried forward for visibility, not blocking acceptance: G4's advisory **NB-1** — the generic/no-cap-provenance fallback *text* is asserted by a dedicated test only for `derive.py`; the other four modules' identical fallback logic is confirmed correct by direct source read but lacks its own text-assertion test (recommend a small follow-up task, consistent with G4's own non-blocking disposition).

## Overall verdict: **PASS**

All three applicable requirement IDs (D-059-R003 in both its task-scope and directive-level senses, D-046-R001, D-046-R002) are SATISFIED on primary evidence I personally reproduced — not on the producer report, evidence map, or any gate report's narrative. D-059-R003 is now **closed project-wide**: this verification supersedes the M5-T027 DCV's explicit "remains OPEN project-wide" ruling. Restamp to the live head at accept time is safe under the stated, empirically-reverified condition.
