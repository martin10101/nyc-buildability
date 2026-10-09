# M0-T107 — G0 readiness (administrative; recorded at the claim seam)

Task: M0-T107 (unit J: generic Claude Code plugin portability plan; Amendment-3 packet,
post-golden-run, non-blocking). Recorded by: orchestrator (fable-orchestrator-session),
2026-08-29, campaign seq 28. Supervisor-freeze note: planning-only unit — the packet
produces a PLAN document; qualifying-evidence citation for supervisor-adjacent control
commits stays `D-024-R###` per the freeze rule.

1. **Why now:** M0-T107 is the campaign's only remaining non-owner-gated unit and is
   selected as the FIRST BOUNDED TASK PACKET for the R595-authorized limited-auto loop
   (Amendment 9 R255: Codex selects bounded tasks from the durable campaign record — the
   seq-28 record names M0-T107 as NEXT after the activation act).
2. **Dependencies:** M0-T096 `accepted` (the only dependency). Bootstrap Gate 0 re-verified
   this seam (cwd = ctl24 root; clean tree; local == origin; CI 20/20 at `bbb932a`).
3. **Packet integrity:** directive_refs `D-024:ALL`; `evaluate_task_refs` ok=true,
   **7 applicable ids** (R179, R220, R221, R223, R224, R227, R228), no
   missing/invalid/unresolved.
4. **Isolation:** producer worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107` on task
   branch `task/M0-T107-plugin-portability`, created from the current campaign head — the
   loop's Fable producer works there, never in the primary checkout.
5. **Loop context:** this claim stages the packet for supervised-by-supervisor execution
   under the certified policies (bounded unit, checkpoint evidence, independent review);
   the packet confers authority to the runner via `--task-packet`. Planning-only scope:
   the unit writes a portability PLAN (no plugin implementation, no dependency admission,
   no `.claude/hooks` changes).

Verdict: **PASS** (administrative readiness; independent review at the unit's gates).
