# M0-T012 — G4 integration and regression evidence (orchestrator-captured)

- **Task:** M0-T012 CI SHA-pinning
- **Date:** 2026-07-17
- **Merge commit:** `99cca33` (no-ff merge of `task/M0-T012-sha-pinning` @ `e5f6ea4`); ledger commit `99202ce` (CI ran at this head)

## CI evidence on main

| Workflow | Run | Commit | Result |
| --- | --- | --- | --- |
| CI (5 jobs, all running on the pinned SHAs) | [29563636434](https://github.com/martin10101/nyc-buildability/actions/runs/29563636434) | `99202ce` | completed / **success** |
| secret-scan | [29563636433](https://github.com/martin10101/nyc-buildability/actions/runs/29563636433) | `99202ce` | completed / **success** |

Command: `gh run list --commit 99202ce2cdb9b0a66cc33ce77a7e33fd15ddb725 --json name,status,conclusion` → both `completed/success`.

## G4 checklist

- Full suite green on the integrated tree, executed entirely through the newly pinned actions (the strongest possible regression proof for this change class).
- Branch-side proof also green pre-merge (runs 29554930113 / 29554930067 at `e5f6ea4`).
- No contract, migration, or application-code surface touched (G3 verified every hunk).
- Low-storage: KB-scale text edits only; worktree removed at acceptance.

## Result

**G4 PASS.** Supply-chain debt (G5 M0-T005-R1 residual, M2-T001 G5 F1) closed: zero mutable action tags remain in CI workflows. Informational notes from G3 (stale packet inventory of 11 vs 12 refs; generate-lockfile.yml `contents: write` disposition; jobs-vs-checks phrasing) recorded for the backlog.
