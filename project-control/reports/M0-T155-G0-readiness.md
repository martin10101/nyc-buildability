# G0 Readiness — M0-T155 (D-037: reviewer proportionality)

**Recorder:** orchestrator (G0 administrative readiness), 2026-09-07.

- **Packet:** `project-control/tasks/M0-T155.json` — objective (add proportionality/blocking-threshold
  rule to `prompts/codex_review.md`: REVISE only when it names a failing gate or written acceptance
  criterion; minor non-blockers → recorded advisory + COMPLETE), real tracked allowed_paths
  (codex_review.md, codex_reviewer.py, test_agent_supervisor_reviewer.py, the producer report),
  four documented commands, gates G0/G2/G3/G5, roster (code-reviewer, security-reviewer,
  directive-compliance-verifier), the DL-2 envelope + Bash-tool notes.
- **Directive:** D-037 (cites D-037:ALL); the objective distinguisher (name the failing
  check/criterion or it is a note) is recorded in the packet notes.
- **Safety:** freeze-rule task; weakens NO real gate (correctness/safety/contract/tests/modularity/
  security/dependency-security stay blocking); HALT_UNSAFE/STOP_FOR_OWNER/read-only discipline and
  the consecutive-revision breaker unchanged. Recertify before the running controller uses the new prompt.
- **Order:** staged to run when the current loop task (M0-T153) parks; no interrupt of in-flight work.

G0 outcome: **PASS** — ready to claim for the loop.
