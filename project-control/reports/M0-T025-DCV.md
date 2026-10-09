# M0-T025 — Directive-Compliance Verification (DCV) report

**Directive regime:** D-001. **Task:** M0-T025 (governance; control-plane hardening, LOW-1 path containment). **Packet:** `project-control/tasks/M0-T025.json`. **Cited refs:** `[{D-002: ALL}]`. **Submitted:** `awaiting_gate`, reviewed_sha `56db6a17`, evidence-map claims EMPTY applicable set. **Candidate diff:** `20f7651c`. **Branch HEAD at review:** `75f060d8`. **Verifier:** directive-compliance-verifier (≠ producer `supervised-loop-fable-worker`; ≠ orchestrator). Read-only; no writes, git, gh, or control CLI performed.

## 1. Applicability reproduced (primary evidence)

Command (verbatim from task):
`python -c "... reg.evaluate_task_refs(json.load('project-control/tasks/M0-T025.json')) ..."`

Reproduced output:
```
{"ok": true, "applicable_ids": [], "cited_ids": [], "missing_ids": [],
 "invalid_refs": [], "unresolved": [], "reasons": []}
```
**ok=true, applicable_ids=[]** confirmed.

**WHY the D-002 rows are inert (conjunction semantics).** `Registry._applicability_matches` (tools/directive_registry.py:568-595) applies conjunction over the four dimensions: for every NON-EMPTY dimension the task must match; the first non-empty dimension that excludes the task short-circuits to non-match (returns `False, None`). M0-T025 has `task_id=M0-T025`, `task_type=governance`, `milestone_id=M0`. Every one of D-002's 69 requirement rows carries a NON-EMPTY `applicability.task_ids` — `["M0-T024"]` (R001–R035, R040–R044, R061–R069 governance rows), `["M3-T001","M4-T007","M2-T017"]` (R036–R039, R051–R060 producer rows), or `["M0-T024-POSTMERGE"]` (R030, R045–R050 post-merge rows) — and **none contains `M0-T025`**. So the `if tids and task.get("task_id") not in tids: return False` check fires for every row, regardless of the fact that `task_type=governance` and `milestone=M0` would otherwise match. `D-002:ALL` therefore expands (evaluate_task_refs:696-700 intersects the directive's requirement_ids with the *applicable* set) to **zero** cited ids. Empty applicable set ⇒ `ok=true` with all sets empty. This matches the evidence-map note and the D-032/D-033 empty-set precedent.

## 2. Selective-citation exposure — NONE (independent cross-directive scan)

I did not rely on `evaluate_task_refs` alone. I re-implemented the conjunction matcher independently and swept **all 3623 requirement rows across all 32 active directives (D-001…D-034)** against M0-T025's `task_id`/`task_type`/`milestone_id`/`allowed_paths`:
```
total requirement rows scanned: 3623
rows matching M0-T025 (independent conjunction impl): []
```
Corroborating detail:
- **No row names M0-T025 in `task_ids`.** D-004 mentions `M0-T025` only in prohibition *text* (R022/R053/R183/R222/R260/R263/R306/R325/R397/R492, R422) whose *applicability* is bound to OTHER tasks (M0-T027/M0-T028/M0-T029/D-004-PHASE0…). Those forbid other tasks from touching M0-T025; they do not bind M0-T025 itself, and M0-T025 does not cite D-004.
- **No path-based row binds.** Every active requirement with a non-empty `applicability.paths` also has a non-empty `task_ids` that excludes M0-T025 (e.g. D-004 report/settings/hooks rows → M0-T027/M0-T028; D-007/agent_supervisor → M0-T036; D-009 → M0-T019). The only path row with empty `task_ids` (D-010-R297, path `C:/Program Files/SupervisorConfig/config.toml`) does not intersect M0-T025's four `tools/` + `project-control/reports/` paths. Even broad prefixes (`project-control/`, `project-control/reports/`) that WOULD intersect the report path all carry excluding `task_ids`.
- **No governance-typed wildcard row** (empty `task_ids` + `task_type=governance`) exists.
- `missing_ids=[]` in the reproduced output confirms there is no applicable-but-uncited requirement; the accept-time selective-citation guard has nothing to fire on.
- Sanity: `covers_governance(M0-T025) = True` — D-002's manifest scope (`task_types:["governance"]`) covers this governance packet, so the citation `D-002:ALL` is the correct/adequate governance citation (s19 claim-time guard satisfied). `D-002 is_active=True, errors=[]`.

## 3. Content identity + reviewed_sha (primary evidence)

- Submission record `project-control/reports/M0-T025.json` carries `content_manifest_sha256 = 598fc256…2036d09`, `reviewed_sha = 56db6a17…`, `applicable_requirements = []`. Evidence map `project-control/reports/M0-T025-evidence-map.json` is `schema evidence_map/v1`, `requirements {}`, with the empty-set note.
- The four allowed-path blobs are **byte-identical** across submit `56db6a17`, candidate `20f7651c`, and HEAD `75f060d8`:
  - `tools/directive_registry.py` = `e1168304…`
  - `tools/validate_directive_compliance.py` = `d649b6fe…`
  - `tools/test_directive_compliance.py` = `940ad7dd…`
  - `project-control/reports/M0-T025-producer-report.md` = `805ddc84…`
- `directive_registry.frozen_git_identity(<4 paths>)` reproduces the manifest identity `598fc256…2036d09` at all three SHAs; the HEAD stamp with `require_clean=True` returns `err=None` (working tree clean for these paths, HEAD=75f060d8). **Reproduced identity == submitted content_manifest_sha256.**

## 4. Directive-registry append-only law (primary evidence)

`git show --stat 20f7651c` = exactly 4 files, all inside `allowed_paths`:
```
project-control/reports/M0-T025-producer-report.md | 177 +
tools/directive_registry.py                        |  72
tools/test_directive_compliance.py                 | 112
tools/validate_directive_compliance.py             |  11
4 files changed, 339 insertions(+), 33 deletions(-)
```
**No** committed `source-*.md`, `manifest.json`, `requirements.json`, or `verification.json` under `project-control/directives/**` is touched. Append-only registry law intact. Forbidden paths (product/runtime, `.claude/**`, `.github/**`, D-002 registry sources, other tasks) untouched.

## 5. Registry integrity + change-does-not-break-law + prohibited-action state

- `python tools/validate_directive_compliance.py --check` → **exit 0** (real 30-directive registry validates clean through the new containment guard; repository-level AS-2 no-regression proof, reproduced by me).
- `pytest -k "guard_accepts or guard_rejects"` → **2 passed** (resolve_contained_ref accepts plain/nested relative refs; rejects traversal/absolute/malformed) — reproduced by me. The heavy fixture-copy tests (`test_real_registry_valid`, AS-1/AS-2 full-registry-copy cases) exceed my 5-min sandbox cap because each copies the 7.7 MB / 265-file registry (documented slow characteristic, not a defect). The full `tools/test_directive_compliance.py` suite (~27 min, producer-documented 126 passed pre-rider) remains the **orchestrator's mandatory gate-wave step before acceptance** per the packet note — request that captured evidence at accept-time; it is not a directive-compliance gating item.
- Prohibited-action evidence: M0-T025 `status=awaiting_gate` (progress 85), present in `state.json active_tasks`, **absent from `accepted_tasks`**; no blocker references M0-T025; nothing merged/accepted/deployed. PR #241 untouched (out of scope).
- No existing `(D-002, M0-T025)` row in `D-002/verification.json` (present rows: M0-T024, M3-T001, M4-T007, M2-T017). `accept()` fail-closes when a cited active directive lacks a task_verification row, so the orchestrator MUST add the empty-set row below before acceptance (D-032/D-033 precedent).

## Exact attested verification row (record verbatim into `project-control/directives/D-002-activate-control-system-first-wave/verification.json` → `task_verifications[]`)

```json
{
  "directive_id": "D-002",
  "task_id": "M0-T025",
  "applicable_requirement_ids": [],
  "reviewed_sha": "75f060d83ce29cce2cdd48339f04e66bc8592a1c",
  "reviewed_manifest_sha256": "598fc256aeecfb33bfc3b2b5081f559d1f95f660c4ac08141709e547f2036d09",
  "producer": "supervised-loop-fable-worker",
  "verifier": "directive-compliance-verifier",
  "schema_version": "directive_verification/v2",
  "verified_at": "2026-09-07T00:00:00+00:00",
  "note": "EMPTY-SET verification. M0-T025 cites D-002:ALL, but the shared canonical resolver (directive_registry.evaluate_task_refs / derive_applicable) independently derives ZERO applicable D-002 requirements for this packet: every one of the 69 D-002 requirements carries a NON-EMPTY applicability.task_ids ('M0-T024' | 'M3-T001','M4-T007','M2-T017' | 'M0-T024-POSTMERGE') and none contains 'M0-T025', so _applicability_matches short-circuits to non-match even though task_type=governance and milestone=M0 would otherwise match. evaluate_task_refs returns ok=true with applicable_ids=[], cited_ids=[], missing_ids=[], invalid_refs=[], unresolved=[]. No selective citation: an independent conjunction sweep of all 3623 requirement rows across all 32 active directives (D-001..D-034) against M0-T025's task_id/task_type/milestone/allowed_paths (tools/directive_registry.py, tools/validate_directive_compliance.py, tools/test_directive_compliance.py, project-control/reports/M0-T025-producer-report.md) yields ZERO applicable requirements; D-004's textual 'do not touch M0-T025' prohibitions are applicability-bound to other tasks and are not cited by M0-T025. Row exists because accept() fail-closes when a cited active directive has no task_verification row (D-032/M0-T147..M2-T020, D-033/M0-T150 empty-set precedents). Verifier != producer. Material identity: reviewed_manifest_sha256 = 598fc256aeecfb33bfc3b2b5081f559d1f95f660c4ac08141709e547f2036d09, reproduced via directive_registry.frozen_git_identity over the four allowed_paths and byte-identical across submit 56db6a17, candidate 20f7651c, and HEAD 75f060d8 (require_clean=True at HEAD, err=None); the four blobs are e1168304 / d649b6fe / 940ad7dd / 805ddc84 at all three commits. Directive integrity reproduced: D-002 active, zero errors; validate_directive_compliance.py --check exit 0. Append-only law honored: git show --stat 20f7651c = exactly the four allowed_paths; no source-*.md/manifest.json/requirements.json/verification.json under project-control/directives/ touched. Prohibited-action evidence: status awaiting_gate, in active_tasks only, not accepted, no merge/deploy, no blocker references M0-T025, PR #241 untouched. Mechanical accept-time restamp convention applies: reviewed_manifest_sha256 stays 598fc256 while the four allowed_paths blobs are unchanged; the orchestrator re-stamps reviewed_sha to the actual accept-time HEAD (must be verified clean and byte-identical), else fail closed. The full tools/test_directive_compliance.py suite (~27 min) is the separate mandatory orchestrator gate-wave step.",
  "requirements": []
}
```

Note for the orchestrator: `verified_at` is a placeholder timestamp — set it to the actual recording time; if HEAD advances before accept, re-stamp `reviewed_sha` to the accept-time HEAD after confirming the four blobs are still `e1168304 / d649b6fe / 940ad7dd / 805ddc84` (identity stays `598fc256`).

## Verdict

Every item verified against primary repository evidence I reproduced myself (applicability re-derivation, independent 32-directive selective-citation sweep, blob-SHA identity across three commits, frozen_git_identity reproduction, `git show --stat`, `validate --check` exit 0, guard unit tests, state/blocker inspection). The empty applicable set is correct and non-selective; content identity is stable and matches the submission; the diff respects append-only registry law and packet scope; the task is unaccepted with no prohibited action taken. The only remaining action is the orchestrator recording the empty-set verification row above (and the mandatory full-suite gate-wave run).

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the directive-compliance-verifier agent-return channel (2026-09-07 gate wave; transport framing line removed, HTML entities decoded, content unaltered).*
