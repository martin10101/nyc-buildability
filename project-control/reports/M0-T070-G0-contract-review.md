# M0-T070 — G0 contract readiness review

- Task: M0-T070 — Supervisor corrective repair (defect A: packet documented-test-command
  authority wiring; defect B: revoke-all/status open_asks reconciliation) under D-014.
- Reviewed at: 2026-08-18, branch `task/M0-T070-supervisor-authority-repair`, base
  `de2f224a7db16405edfc0e2f2f0902f5164819a0` (tip of `control/context-intelligence-init`;
  origin/main `5c71fe0e08c8717cc20ac232d8bd0d8a328525e1`).

## Contract completeness

- Objective names both source-confirmed defects with exact production sites
  (`cli.py:_run_loop` / `TaskAuthority.from_packet`; `broker.revoke_all` /
  `DurableJournal.open_asks` / `cmd_status`) and binds the twelve owner acceptance
  behaviors AS-1..AS-12 verbatim into `acceptance_scenarios`.
- Directive regime: `directive_refs = D-001:ALL; D-014:ALL`. The resolver
  (`DirectiveRegistry.evaluate_task_refs`) returns `ok: true` for the packet's
  allowed_paths — no other directive's requirements become applicable (no selective
  citation).
- Qualifying evidence (supervisor-freeze §2/§3) is cited in the packet objective:
  a reproduced defect + inability to complete an authorized product task
  (run_M0_T063_A1, controller 0.4.0-phase4: 3 × `ASK:undocumented_command`, exit 1,
  PAUSED_RECOVERY, no checkpoint, no Codex review; A1 worktree clean at de2f224;
  post-revoke-all journal shows 3 unanswered `queued_asks` rows while all 3 approval
  records are `REVOKED`).
- Scope is bounded: 4 supervisor production files, 1 new schema, 1 new replay-corpus
  fixture, 1 new test module, 3 report files. Forbidden paths exclude the A1
  implementation surface (`tools/repo_*.py`), CI config, and app/service trees
  (D-014 prohibitions 4, 8).
- Gate profile G0/G2/G3/G5 matches the supervisor-freeze defect lane; reviewers
  (code-reviewer, security-reviewer, directive-compliance-verifier) are all distinct
  from the producer (orchestrator).
- Rollback: deletion/reversion of only `task/M0-T070-supervisor-authority-repair`
  and `wt-m0t070` before merge (D-014-R037); no runtime state is touched.

## Preconditions verified

- M0-T063..M0-T069 remain allocated and untouched; next free ID M0-T070 confirmed
  by ledger scan (no reference anywhere in project-control/, docs/, tools/).
- D-014 captured (39 requirements) and registry-valid apart from the expected
  `affected_task M0-T070 not found in ledger` ordering error, resolved by this
  contract.
- The live A1 runtime SQLite database is out of scope for all writes; the status-side
  reconciliation requirement (AS-8) is explicitly read-time so the existing journal
  reports correctly without mutation (D-014 prohibition 3).

## Verdict

G0 PASS — contract is complete, bounded, in-regime, and executable.
