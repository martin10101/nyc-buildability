# M0-T013 — G0 definition-of-ready (orchestrator, 2026-07-17)

- **Task:** Expansion-agent ADR-005 conformance (5 agent files + rule item 13/11)
- **Origin:** owner decision 2026-07-17 approving disposition A with programmatic enforcement; G5 corrections 1-5 (project-control/reports/M0-T010-G5-agent-governance-review.md) route here; B-007 closes at this task's acceptance.

| G0 item | Status |
| --- | --- |
| Objective unambiguous | YES — G5 corrections 1-5 are verbatim, per-file, with named roster baseline files |
| Dependencies | M0-T010 (G3+G5 PASS recorded; branch merged to LOCAL main only — the pack files this task edits exist locally; per owner sequence remote main receives ONE final HEAD after this task's gates) |
| File scope exclusive | YES — 5 agent files + 1 rule file + own producer report; enforcement layer (hook/settings/counter-notice/blocker) explicitly forbidden (orchestrator-only); no other open task touches these paths |
| Inputs/outputs | Defined in packet |
| Acceptance scenarios | S1–S6 in packet |
| Source documentation | G5 report + conformant roster agent files on main |
| Credentials | none |
| Gates | G0 (this), G2 (producer self-check), G3 (code-reviewer), G5 re-check (security-reviewer — REQUIRED: edits active execution surfaces) |
| Execution/disk | text-only, KB-scale, worktree .claude/worktrees/M0-T013 on branch task/M0-T013-agent-conformance from local post-merge main; 16.7 GB free (>= 10 GB owner threshold); cleanup = worktree/branch removal at acceptance |
| Storage routing | git only; no datasets, no installs; heavy work N/A |

## Result

**G0 PASS** — producer cloud-architect may claim. Constraint restated: raw-pack commits
d25d2b2/c0769ae are preserved history; conformance edits are new commits; nothing pushes
to remote main until G2+G3+G5 pass and the orchestrator assembles the single final HEAD
(owner git sequence).
