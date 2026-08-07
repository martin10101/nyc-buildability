# M0-T038 G3 code review — verdict preserved verbatim

**Reviewer:** code-reviewer (independent, read-only). **Recorded by:** orchestrator (producer ≠ reviewer).
**Reviewed:** HEAD `361dee9` (content commit `25ed364`, identity `16d327e1…`, base `aa5eec3`).
**Result: FAIL — one BLOCKING defect (D1), rework trivial.**

---

# Gate Report

- Gate ID: G3
- Task ID: M0-T038 ("Preserve post-merge SESSION_HANDOFF update via dedicated PR", D-010-R098)
- Reviewer: code-reviewer (independent, read-only)
- Producer: orchestrator
- Result: **FAIL**
- Clean environment/worktree used: `C:\Users\MLFLL\Downloads\nyc-zoning\orch`, branch `task/M0-T038-handoff-preserve`, HEAD `361dee9`, reviewed content commit `25ed364`, base `origin/main aa5eec3`. All git/gh reproductions run from that worktree.

## Acceptance criteria reviewed

- **AS-1 (scope + fidelity):** branch diff vs main touches only `docs/SESSION_HANDOFF.md` plus M0-T038 control records; handoff change equals the preserved post-merge update with no unrelated content mixed in.
- **AS-2 (factual accuracy):** every factual claim in the added lines reproduces against primary evidence (`gh pr view 154` state/mergedAt/mergeCommit; required-check conclusions on `57ccb44`; tree byte-identity `57ccb44^{tree} == 4f8c1d2^{tree}`).

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R098 (preserve the verified/accurate update via a dedicated bounded task + normal PR; not discarded, not mixed with unrelated work) | 25ed364 / 361dee9 | **FAIL** | Preservation, dedicated-task, and no-unrelated-work aspects PASS (see AS-1). But R098 requires the update be **accurate** ("verified against merged repository state"); the delivered `main` merge-commit SHA is malformed and does not resolve (Defect D1) — so the "verified accurate" clause is contradicted by the deliverable. |
| D-010-R107 (begin the first dependency-valid bounded task automatically; no routine-approval stop) | 361dee9 | PASS (process; partial-scope) | Task file `created_at 2026-08-07T01:32:33Z`, autonomous `progress_log` with no owner-approval stop; `M0-T038-g0-readiness.md` present. The evidence-map's "PRs #155/#156/#157 merged autonomously" sub-claim is outside this deliverable's diff and outside allowed_paths — not independently re-derived here; it is not central to AS-1/AS-2 and does not affect this gate's verdict. Full R107 sign-off is the directive-compliance-verifier's pass. |

## Steps independently executed (reproducible)

```
# SCOPE
git diff aa5eec3..25ed364 --name-only
  docs/SESSION_HANDOFF.md
  project-control/gates/M0-T038-G0.json
  project-control/reports/M0-T038-evidence-map.json
  project-control/reports/M0-T038-g0-readiness.md
  project-control/reports/M0-T038-producer-report.md
  project-control/state.json
  project-control/tasks/M0-T038.json
git diff aa5eec3..361dee9 --name-only   # adds only: project-control/reports/M0-T038.json
# per-commit attribution: 796cd00 = deliverable + producer report + evidence-map + g0-readiness;
#   25ed364 = G0 gate/state/task; 361dee9 = submit (report snapshot/state/task)

# CONTENT FIDELITY
git diff aa5eec3..25ed364 --numstat -- docs/SESSION_HANDOFF.md   -> 11  5
git diff ... | grep -c "^@@"                                     -> 1   (single hunk, CURRENT STATE block only)

# AS-2 FACTS
gh pr view 154 --json state,mergedAt,mergeCommit
  {"state":"MERGED","mergedAt":"2026-08-07T00:06:56Z",
   "mergeCommit":{"oid":"cec785f97ac1037fb..." [full 40-hex merge SHA]}}
git rev-parse 57ccb44^{tree} 4f8c1d2^{tree}
  67e97dda1ea8067ed73a8e1000ca662a736fbe93 (both)
gh api .../commits/57ccb44/check-runs --jq '.total_count'                 -> 16
gh api .../commits/57ccb44/check-runs --jq 'group conclusions'           -> [{"success":16}]

# MERGE-SHA EXACT-TOKEN CHECK (from the committed blob, not transcription)
git show 25ed364:docs/SESSION_HANDOFF.md | grep -oE 'main` = `[0-9a-f]+`'
  -> the written token is 39 hex chars (missing the 9th digit "7")
git rev-parse <written 39-char token>
  fatal: ambiguous argument ... unknown revision           # does NOT resolve
git rev-parse cec785f  -> the real 40-char merge commit

# ACCEPTED COUNT (project_control.py not run — reviewer read-only; derived from ledger)
grep -c '"status": "accepted"' project-control/tasks/*.json  -> 56 files (incl. M0-T036)
```

## Expected versus actual

| # | Check | Expected | Actual | Verdict |
|---|---|---|---|---|
| 1 | SCOPE (AS-1) | Only `docs/SESSION_HANDOFF.md` + M0-T038 control records; nothing unrelated; no forbidden paths | Exactly that. Deliverable + G0 gate + state/task ledger + producer-report + evidence-map + g0-readiness + report snapshot. No `project-control/directives/`, `apps/`, `services/`, `tools/`, `.claude/`, `.github/`. D-010-R098 "no unrelated work" satisfied. | PASS |
| 2 | CONTENT FIDELITY (AS-1) | Single CURRENT STATE update; historical sections verbatim; supersedes-note intact | Single hunk `@@ -10,11 +10,17 @@`, 11+/5−; only the M0-T036 bullet rewritten; top supersedes-note (lines 8–9) unchanged; no other section touched | PASS |
| 3a | PR #154 state/mergedAt | MERGED, 2026-08-07T00:06:56Z | MERGED, 2026-08-07T00:06:56Z | PASS |
| 3b | PR #154 mergeCommit vs added line | full 40-hex merge SHA | Real merge commit is 40 hex chars; **added line carries a 39-char token (missing digit "7" after `cec785f9`)** — does not reproduce, does not resolve | **FAIL (D1)** |
| 3c | tree byte-identity `57ccb44^{tree}==4f8c1d2^{tree}==67e97dda` | equal | both `67e97dda1ea8067ed73a8e1000ca662a736fbe93` | PASS |
| 3d | required checks on `57ccb44` / 16-green | all pass; 16/16 green | `total_count=16`, all 16 `success` | PASS (see N1 on the 8/8 split) |
| 3e | R595 blocking-prerequisite claim | matches `M0-T036-ACTIVATION-CHECKLIST.md` | Checklist line 11 "⛔ R595 supervised rehearsal — MANDATORY BLOCKING (…D-007-R619)"; handoff phrasing + citation match | PASS |
| 3f | accepted count 56 | 56 at write time; still holds with D-010 backlog uncounted | 56 task files `status: accepted` (incl. M0-T036); D-010 wave-1 tasks not accepted | PASS |
| 4 | WRITING QUALITY | consistent with file conventions | Consistent bolding/emoji/citation style; LF endings preserved; single logical block | PASS (aside from D1) |
| 5 | Secrets/credentials/PII | none | Added lines contain only public commit SHAs, dates, PR#, report path — no secrets/PII | PASS |

## Defects

- **D1 — BLOCKING (factual accuracy / AS-2 / D-010-R098).** `docs/SESSION_HANDOFF.md` line 16 states the `main` merge SHA as a 39-hex-char token missing the 9th digit "7" (after `cec785f9`). The authoritative merge commit for PR #154 is the 40-char SHA from `gh pr view 154 --json mergeCommit` / `git rev-parse cec785f`. `git rev-parse` on the written token returns "unknown revision" — it resolves to nothing. AS-2 requires the `mergeCommit` claim to reproduce against `gh pr view 154`; it does not. Fully reproducible (see Steps). Fix: insert `7` at position 9; re-verify with `git rev-parse` before resubmission.

- **N1 — NON-BLOCKING (observation).** The added line asserts "8 required checks" and "8 non-required" within the 16. All 16 check-runs are `success`, so the material claim holds; the exact 8/8 split was not re-derived from the ruleset. Immaterial because all 16 passed.

- **N2 — NON-BLOCKING (packet nit, not a producer fault).** The deliverable content commit `796cd00` also wrote `M0-T038-evidence-map.json` and `M0-T038-g0-readiness.md` — legitimate M0-T038 control records sanctioned by the review checklist, but not enumerated in the packet's `allowed_paths`. No unrelated work and no forbidden path was touched. Consider widening `allowed_paths` to cover the standard lifecycle artifacts on the rework packet.

## Required rework

1. Correct the merge-commit SHA in `docs/SESSION_HANDOFF.md` line 16 to the full 40-char merge SHA (Defect D1). Re-verify with `git rev-parse` that the written token resolves to the PR #154 merge commit before resubmission.
2. (Optional, N2) On the rework packet, enumerate `M0-T038-evidence-map.json` and `M0-T038-g0-readiness.md` under `allowed_paths` so scope matches the lifecycle artifacts actually produced.

## Reviewer conclusion

**FAIL.** Scope (AS-1), content fidelity, historical-section preservation, the supersedes-note, the merge date/state, tree byte-identity (`67e97dda`), 16/16 green checks, the R595 blocking-prerequisite citation, the accepted-count-56 claim, writing quality, and secrets/PII all pass. The gate fails on one BLOCKING, fully reproducible factual-accuracy defect (D1): the deliverable records the PR #154 merge commit with a missing hex digit, so it does not resolve in git and does not match `gh pr view 154`. Because AS-2 requires every factual claim in the added lines to reproduce and this is the core provenance value the task exists to preserve, the task cannot be accepted until the SHA is corrected and re-verified. The fix is a single-character insertion, so rework is trivial.

---

*Orchestrator note (D1 provenance): the defective 39-char token originated in the PRIOR session's uncommitted update (the artifact this task preserves); the producer report's own evidence table carries the correct 40-char value. Rework = preserve-with-correction, documented in the rework commit.*
