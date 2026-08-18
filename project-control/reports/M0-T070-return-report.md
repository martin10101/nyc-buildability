# SUPERVISOR_REPAIR_PR_READY — M0-T070 return report (D-014-R038 committed copy)

Returned by the orchestrator on 2026-08-18 after implementation and gates; this file is the
durable copy of the in-session return message required by D-014 ("return: SUPERVISOR_REPAIR_PR_READY").

1. **Reconciled task ID:** `M0-T070` (M0-T063..M0-T069 were already allocated by D-013; no ID reused).

2. **Branch and worktree:** `task/M0-T070-supervisor-authority-repair`, worktree
   `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t070`, stacked on `control/context-intelligence-init`
   at `de2f224a7db16405edfc0e2f2f0902f5164819a0` (origin/main was `5c71fe0e…` at capture).

3. **Exact files changed** (implementation, commit `6aae5857`):
   - `tools/agent_supervisor/policy.py` (+ canonical field constants, closed profile, fail-closed validator)
   - `tools/agent_supervisor/cli.py` (+ `production_task_authority`; `_run_loop` rewire; `cmd_status` read-time reconciliation; imports)
   - `tools/agent_supervisor/broker.py` (`revoke_all` durably resolves ask rows)
   - `tools/agent_supervisor/durable_state.py` (+ `DurableJournal.resolve_ask`, UPDATE-only)
   - `tools/agent_supervisor/schemas/task_packet_commands.schema.json` (new)
   - `tools/agent_supervisor/fixtures/m0_t063_documented_test_command.json` (new)
   - `tools/test_agent_supervisor_command_authority.py` (new, 29 tests)
   Control plane: D-014 capture (39 reqs), M0-T070 packet + gates G0/G2/G3/G5 + reports
   (incident evidence, before/after evidence, producer report, G3/G5/DCV reports, evidence map,
   this return report), `directives/index.json`, `state.json`.

4. **Root cause confirmed (both defects, from source, before any fix):**
   - **A:** production `_run_loop` (pre-fix `cli.py:2487`) built `TaskAuthority.from_packet` without
     `documented_test_commands` (kwarg-only, default `()`); the S4.1 documented-test AUTO tier was
     unreachable in production → all three A1 Bash requests `ASK:undocumented_command` (audit seq 4-6).
     `M0-T063.json` had no command-authority field at all.
   - **B:** `broker.revoke_all` flipped `approval/*` records to REVOKED but no code path ever updated
     `queued_asks`; `cmd_status` read unanswered rows unconditionally → the live A1 journal shows all
     3 asks unanswered while all 3 approvals are REVOKED (revoke_all revoked=3, state PREFLIGHT).

5. **Before/after test evidence** (bounded fixtures; the real A1 run was NOT repeated):
   - BEFORE (kept executable as `test_the_pre_fix_construction_reproduces_the_a1_failure`):
     intended command `python tools/test_repo_fingerprint.py` → **ASK:undocumented_command**.
   - AFTER (production constructor): → **AUTO:documented_test_command**; all 13 altered/injected
     variants remain ASK/HARD_DENY. Revoke lifecycle: pending→open; revoke-all→revoked durably;
     pending-approvals 0; status shows zero open asks, pre-fix journals labeled revoked history
     read-only. Measurements: validator ≈0.31 ms/call, classification ≈3.7 ms/call; no provider
     tokens involved. Full detail: `M0-T070-before-after-evidence.md`.

6. **Commit SHA and PR URL:**
   - Implementation head (reviewed): `6aae5857fdcdf55f5197e542013bdc81f8035d14`
   - Control-plane records: `bcc0962` (+ this return-report commit)
   - PR: https://github.com/martin10101/nyc-buildability/pull/222 (base `control/context-intelligence-init`; OPEN, not merged)

7. **Gate results** (all at reviewed head `6aae5857`):
   - G0 contract PASS (orchestrator, administrative)
   - G2 self-check PASS (orchestrator; never counts as independent review)
   - G3 code review **PASS** (independent code-reviewer; F1 LOW non-blocking, F2-F4 INFO)
   - G5 security review **PASS** (independent security-reviewer; 0 blocking, SEC-INFO-1..3)
   - Directive-compliance verification **PASS** (independent verifier; 27/30 PASS,
     R014/R015/R038 pending-external return-cycle acts, recorded in D-014 `verification.json`)
   - Suites: supervisor 1557 passed / 2 skipped / 0 failed (freeze baseline ≥1165 re-established);
     project-control + directive-compliance 155 passed; registry `--check` VALID.

8. **Remaining risks:**
   - **Wildcard-in-program-token latitude (G3 F1 / G5 SEC-INFO-1, non-blocking):** a documented
     shape like `py* tools/test.py` is accepted by the closed profile and fnmatch-broadens the
     executable within one token. Bounded (≤16 entries, single segment, no metacharacters, exact
     token count) and inherited from the pre-existing grant-shape matcher. Suggested follow-up
     task: forbid `*`/`?` in the program token and rename the related test.
   - **Replay parity (G5 SEC-INFO-2):** `replay.build_authority` does not run the validator
     (offline reconstruction only; no live authority). Optional parity follow-up.
   - **Prohibition-7 literal reading (DCV discrepancy 1, disclosed):** one `git stash push/pop`
     pair (read-only lint comparison) left three no-op `reset: moving to HEAD` reflog entries in
     wt-m0t070; HEAD never moved off base, nothing was cleaned, rewritten, or force-pushed. If the
     owner reads "do not use git reset" as covering stash internals, this is the one deviation to
     adjudicate; the evidence map was corrected to describe it accurately.
   - **A1 packet still lacks the field:** by design (prohibition 4) `M0-T063.json` was not
     modified; a future authorized A1 run needs its `documented_test_commands` added first.
   - **Pending-external rows:** D-014 R014/R015/R038 verify at the accept cycle (push/PR now
     exist; stop-before-merge holds; this file is the committed return copy).
   - G0 report wording nit (DCV discrepancy 3): "replay-corpus fixture" should read
     "bounded fixture under tools/agent_supervisor/fixtures/"; the recorded gate artifact is left
     unedited, corrected here.

9. **Exact owner-controlled merge and controller-update commands** (this session performs none of them):
   ```bash
   # (a) Merge the repair PR into the control branch (after required checks):
   gh pr merge 222 --merge

   # (b) Then merge the control branch (D-013 bootstrap + this repair) to main,
   #     e.g. by opening/merging its PR:
   gh pr create --base main --head control/context-intelligence-init \
       --title "control: D-013 bootstrap + M0-T070 supervisor repair"
   # ... review/checks ... then: gh pr merge <that PR#> --merge

   # (c) Controller update (R595-gated, S13.1 manual process; supervisor stays SHADOW-ONLY):
   #     1. Ensure no supervised run is active.
   #     2. Back up C:\SupervisorController (keep for rollback).
   #     3. Copy the MERGED tools\agent_supervisor\ tree over C:\SupervisorController.
   #     4. Regenerate + record the controller manifest so the new schema file is covered:
   python -m tools.agent_supervisor doctor --config <config.toml> --model-selection <model_selection.toml>
   #        (generate/record controller_manifest.json per the S13.1 procedure in tools/agent_supervisor/README.md)
   #     5. Restart explicitly. Rollback = restore the backed-up controller directory.

   # (d) Before any future authorized A1 run: add to project-control/tasks/M0-T063.json:
   #     "documented_test_commands": [
   #       "python tools/test_repo_fingerprint.py",
   #       "python tools/test_repo_index_cache.py",
   #       "python tools/test_repo_index_baseline.py",
   #       "python -m pytest tools/test_repo_fingerprint.py tools/test_repo_index_cache.py tools/test_repo_index_baseline.py -q"
   #     ]
   ```

**A1 was not restarted.** The A1 worktree remains clean at `de2f224`; its runtime journal and
audit log are byte-for-byte intact; runtime state remains PREFLIGHT.
