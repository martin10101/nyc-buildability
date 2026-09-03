# M0-T140 — Definitive return report (D-024 Amendment 47, R724)

Durable capture of the implementing session's return; the live final reply reproduces it. Last
line is exactly the required token.

1. **Reconciled (R716):** ledger + repository reconciled; the commissioning live evidence is
   captured durably in `project-control/reports/M0-T140-canary-execution-evidence.md`
   (canary-b5-02r3: worker COMPLETED on `claude-fable-5`, schema-valid Codex REVISE decision,
   owner deny close `operator_declined`, all ten R587 rows PASS from durable artifacts).
   Nothing already accepted was redone; no Claude or Codex was rerun.
2. **M0-T140 closed canonically (R717):** evidence + evidence-map submitted, independent
   G3/G4 + DCV wave, gates recorded, accepted through `tools/project_control.py` — never a
   hand edit.
3. **Live-proven production path recorded (R718):** exact `claude-fable-5` pin; Claude
   authentication + valid WorkerResult; restricted tool surface; bounded subagents +
   over-limit denial; Codex authentication + valid review decision; process-tree cleanup;
   immutable installation + manifest binding; raw PowerShell exit-code preservation
   (canary-execution evidence §3).
4. **GitHub boundary stated honestly (R719):** the supervised loop's own push/PR/CI/merge
   surface has ZERO live evidence and remains unproven (push_policy executes no push in this
   phase; audit anchor NOT ACTIVE; branch has no upstream). Ordinary human/orchestrator
   GitHub activity under ADR-006 Tier A remains separately proven by project history.
5. **Journey task selected (R720):** **M0-T107** — existing, claimed by the supervised-loop
   producer, dependency M0-T096 accepted, documentation-only deliverable
   (`docs/D024_PORTABILITY_PLAN.md` + `project-control/reports/M0-T107-portability-plan.md`),
   gates G0/G2/G3 — the lowest-risk genuinely ready task; not a canary, not infrastructure.
6. **One owner-run script prepared (R721):**
   `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1`
   (SHA-256 `1b636d591dffaba14e1e0cf578eb6f76c7fdbf9ee13291ca15a5ecf5d0e34a65`; PS 5.1 parse
   0 errors). It performs the canonical WAIT_FOR_OWNER exit (`resume-after-answer`), verifies
   the installed manifest (`-Phase verify-manifest`, no install) and the exact
   `claude-fable-5` pin (verify-only + doctor row), launches ONE real supervised journey on
   M0-T107 (`--max-cycles 1`: one Fable worker result + one Codex review; Explore-only
   subagents 2/2; bare-deny Bash; Write/Edit permitted solely for the task's two documented
   paths by prompt + review), performs no push/PR/merge/deployment, and prints a concise
   final status with evidence paths.
7. **Not executed; exactly one command (R722):**
   `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\run_first_supervised_journey.ps1"`
8. **No Tranche C, no new campaign (R723).** The single GitHub decision that remains
   owner-only, identified separately: **whether to authorize the first live supervisor-driven
   GitHub interaction** (a task-branch push and/or the R595-gated automation path with the
   Option-A audit-anchor activation, which requires controller credentials AND an explicit
   owner activation). Local supervised journeys need no GitHub authority; nothing proceeds on
   that surface without that one decision.

FIRST_REAL_SUPERVISED_RUN_READY
