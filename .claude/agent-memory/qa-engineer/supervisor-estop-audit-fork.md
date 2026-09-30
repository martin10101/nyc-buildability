---
name: supervisor-estop-audit-fork
description: Emergency-stop in tools/agent_supervisor forks the audit hash-chain (duplicate sequence) because the estop command writes concurrently with the loop; verify_chain()/recovery-status truthfully report audit_chain_ok:false. By design, not a defect.
metadata:
  type: project
---

When reviewing agent_supervisor emergency-stop (S16.3 / R6) evidence, expect the
estop-run `audit.jsonl` to FAIL `AuditLog.verify_chain()` with
`duplicate_sequence` (e.g. two records at seq 12/13 sharing the same
`prev_digest` = the prior record's digest — a fork, not a clean linear chain).

**Why:** the `emergency-stop` command runs as a SEPARATE, concurrent process that
force-writes `emergency_stop_set` + `remote_approvals_revoked` while the main
supervised loop is still writing its own final records (codex decision → HALT_UNSAFE
→ HALTED). Both opened the append-only log at the same head and appended in
parallel. This is inherent to a kill-path that must not depend on the loop it is
halting. The system surfaces it HONESTLY: `recovery-status` JSON carries
`"audit_chain_ok": false`, and the controller refuses to append onto an
unverifiable chain (so after an estop the log is verify-closed until an explicit
operator repair — acceptable because estop is terminal and recovery re-runs
preflight, never auto-resumes).

**How to apply:** do NOT treat the estop-run chain fork as a blocking defect by
itself. Confirm instead that (1) the estop's SAFETY claims are independently
evidenced (HALTED state, child-tree termination by PID, autostart refused,
recovery report, zero unaccounted children/pending effects), and (2) the evidence
transparently shows `audit_chain_ok:false` rather than hiding it. Contrast with the
ROTATION relaunch path, which is SEQUENTIAL (old process ends, successor continues)
and therefore keeps ONE clean verify-passing chain across the rotation — that one
MUST verify clean. Coverage gap worth flagging: no test locks the estop
concurrent-writer audit shape or the post-estop verify-closed consequence.
Discovered during M0-T045 G4 review (frozen SHA f29decc, main-run 37-event chain
verified clean; estop-run forked).
