# M0-T121 — G0 readiness (orchestrator, administrative)

Recorded 2026-08-30 at HEAD `ef0d476` (capture commit for Amendments 16/17; local == origin;
validator EXIT=0). VERDICT: **PASS — ready to claim and dispatch.**

1. **Authority:** owner authorization verbatim in `source-016-amendment.md` (rows
   D-024-R302..R317) + the live-journey addendum `source-017-amendment.md` (R318..R322).
   Qualifying evidence per the supervisor-freeze rule §2/§3: **reproduced defect** —
   the owner-typed certified cycle-2 start refused pre-dispatch (exit 13 `stale_state`,
   `illegal transition HALTED -> HALTED`), root-caused to the `owner_explicit_restart`
   edge (state_machine.py:399) having zero call sites
   (`project-control/reports/M0-T107-cycle2-start-refusal.md`); authorized by D-024-R302.
2. **Packet completeness:** objective, business reason, inputs, outputs, 8 acceptance
   scenarios (AS-1..AS-8 covering the R312 matrix + R309 red/green reachability + R311
   fail-closed preconditions + R313 exactly-once/audit), allowed_paths (14 entries:
   production seams state_machine/cli/recovery + focused module `restart_channel.py` +
   docs + 6 test files + 2 report files), forbidden paths (control plane except own
   reports; the live runtime dir — the preserved journal is NEVER touched), gates
   G0/G2/G3/G4/G5, 4-reviewer roster.
3. **Directive binding:** in-regime `D-024:ALL` (regime 1.0); resolver dry-run ok=true —
   applicable = cited = 15 rows (R302–R314, R318, R319), missing none, invalid none.
   Registry validator EXIT=0 after the R302–R322 append (c14 digests restamped).
4. **Dependency/order:** no upstream dependency; M0-T122 (recert) depends on this task.
   The R315 hold (no R276 rerun / no cycle-2 handover before certification) is recorded
   on M0-T122.
5. **Environment:** worktree isolation required (producer resets its OWN worktree to
   `ef0d476`); the live supervisor runtime dir is out of scope for all producers; suite
   runs under the sandbox interpreter as in prior supervisor tasks.
