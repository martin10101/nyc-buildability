# M0-T038 producer report — post-merge SESSION_HANDOFF update preserved

**Task:** M0-T038 (D-010-R098). **Producer:** orchestrator. **Branch:** task/M0-T038-handoff-preserve (base origin/main `aa5eec3f`).

## What changed

Exactly one deliverable file: `docs/SESSION_HANDOFF.md`. The change is the byte-preserved
uncommitted post-merge update found in the primary checkout during D-010 Phase 0
reconciliation (11 insertions, 5 deletions in the CURRENT STATE block): it records that
M0-T036 was merged to main via PR #154, the merge SHA, the trigger-commit mechanics used
during the 2026-08-06 GitHub Actions outage, the 16/16 green checks, and that the R595
supervised rehearsal remains the mandatory blocking pre-activation prerequisite. No other
content was mixed in (D-010-R098: "do not mix it into unrelated work").

## Evidence — every factual claim in the added lines reproduced (AS-2)

| Claim in the handoff update | Primary evidence (reproduced this session) |
|---|---|
| PR #154 MERGED 2026-08-07T00:06:56Z | `gh pr view 154 --json state,mergedAt,mergeCommit` → `MERGED`, `2026-08-07T00:06:56Z`, `cec785f97ac1037df1fb2e1b114260eb106b7de0` |
| `main` = `cec785f9…` via merge-commit method | `git log origin/main` prior to D-010 work: `cec785f Merge pull request #154 …` (merge commit, branch not deleted — `origin/task/M0-T036-supervisor-bridge` still exists) |
| Merged head `57ccb44` content-empty trigger commit, tree `67e97dda`, byte-identical to `4f8c1d2` | `git rev-parse 57ccb44^{tree} 4f8c1d2^{tree}` → both `67e97dda1ea8067ed73a8e1000ca662a736fbe93` |
| 8 required checks pass on `57ccb44` (16/16 green incl. non-required) | `gh api …/commits/57ccb44/check-runs` → 16 check-runs, all `success`; the 8 required contexts (ruleset query) are among them |
| SHADOW-ONLY; nothing activated; R595 mandatory blocking prerequisite (R619) | `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md` (on main) states R595 as MANDATORY BLOCKING before any activation; no activation record exists in the ledger |
| accepted count 56 | `python tools/project_control.py status` → `"accepted": 56` (before D-010 wave-1 tasks were added to backlog) |

## Self-check (G2 input)

- `git diff origin/main -- docs/SESSION_HANDOFF.md` shows only the CURRENT STATE block
  update (11+/5−); diff reviewed line-by-line against the Phase 0 capture — identical.
- The handoff's historical sections (including the now-outdated "Reviewers still run
  claude-opus-4-8 (Fable out)" note) are preserved as written by the prior session — this
  task PRESERVES the record (R098); refreshing the handoff for the current session state is
  end-of-session work, deliberately out of scope here.
- No governance path touched; no scope beyond allowed_paths.

## Requirement mapping

- **D-010-R098** (preserve the update via dedicated bounded task + normal PR): this task/PR.
- **D-010-R107** (begin the first dependency-valid bounded task automatically; no routine
  approval stops): M0-T038 was started immediately after the D-010 capture + task
  architecture merged, without owner prompting.

## Rework note (G3 D1)

The prior session's uncommitted update carried the PR #154 merge SHA with a missing 9th hex
digit (39 chars, non-resolving). G3 (code-reviewer) caught it as BLOCKING D1. Corrected in
this rework commit to the full 40-char merge SHA taken programmatically from `git rev-parse`
(no manual transcription); token verified to resolve to the PR #154 merge commit. This is a
preserve-with-correction under D-010-R098's accuracy clause ('verify it against the actual
merged repository state'); every other byte of the preserved update is unchanged. N2 applied:
packet allowed_paths now enumerate the evidence-map and G0-readiness lifecycle artifacts.
