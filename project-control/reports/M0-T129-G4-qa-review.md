# M0-T129 - G4 report (independent qa-engineer, read-only + read-only pytest) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31, reviewed at tip 9e60d05 (BEFORE the G3
C1/N1/N2 report-only fixes landed at 1d4ecea). VERDICT: PASS, no new defects - golden 42/42
in 41.42s (reviewer's own run), all recert numbers reproduced or corroborated, the seven-fact
proof surfaces grep-verified as real production artifacts (over_ceiling_session_shed
loop.py:1086; task_advancement key next_task.py:51; cross_task_dispatch next_task.py:866),
both commands parse-validated, queue format and prerequisites verified, consistency sweep
clean (no execute/autonomy/fewer-facts residuals), baseline 2990+35+10=3035 confirmed. A
delta-ack round on the three-line G3 fix follows before the gate stamps the final identity.

---VERBATIM-BEGIN---
All verification complete. Here is my G4 gate report.

---

# G4 (QA) Gate Report - M0-T129 (Amendment-25 terminal recert + seven-fact commissioning protocol)

**Task:** M0-T129 - single R247 recertification at the post-wiring frozen identity + the owner-executed seven-fact commissioning protocol (D-024-R406..R409). Report-only.
**Reviewed identity:** branch tip `9e60d05`; material `de18f27` (supervisor code verified stable: `git diff de18f27 HEAD -- tools/agent_supervisor/ tools/test_agent_supervisor_*.py` empty). Window change set (`de18f27..9e60d05`) touches **no supervisor code or test file** - report-only confirmed.
**Reviewer:** qa-engineer (independent, read-only + read-only pytest). Producer = `orchestrator-recert-runner`, so my own runs are primary. Live PAUSED_RECOVERY journal never opened (R401/R403); preservation counts from the preserved copy.

## VERDICT: PASS - all recert numbers reproduce; the seven-fact protocol's proof surfaces, commands, queue format, and preflight are real and accurate; the whole package is consistent. No new defects.

## (1) Reproduced-numbers table

| Claim | My reproduction | Result |
|---|---|---|
| Golden pack, single process | **42 passed, 0 failed, 41.42s** (sub-minute) | MATCH (recert cites 51.32s; both sub-minute) |
| cross_task pack | **45 passed** | MATCH |
| Whole suite, golden included | **3035 passed, 2 skipped, 0 failed** - my own measurement at byte-identical material `de18f27` during the M0-T128 delta gate (644.48s); referenced, not re-run (material diff empty) | MATCH |
| tree hash `tools/agent_supervisor` | **b392100930bd4213cab90eb02aafa6d0d568f849** | MATCH |
| golden blob unchanged | **deeca07b...** (git rev-parse) | MATCH (no golden edit) |
| modularity `--check` | **failures 0** (335 files, 11 warnings) | MATCH |
| command-doc tooth | **12 checked, 0 failures, exit 0** | MATCH |
| verify-controller (read-only re-run) | **EXIT 0, "controller verified, including the external config.toml binding"** | MATCH (corroborates recert s3) |
| preservation: audit 53 (preserved copy) / transcript 97 / wt-m0t107 clean `796e18f` | **53 / 97 / `796e18f...` clean** | MATCH |
| baseline 2990 + 35 + 10 = 3035; no test removed | arithmetic confirmed; no existing test file modified in either M0-T128 wave or the M0-T129 window | CONFIRMED |

Not independently recomputed (deliberately): the manifest digest `841ed11c` (would require `record-manifest`, which I must NOT run - but verify-controller PASS corroborates the binding) and the CLI executable_identity `d6f6c29a` (requires the provider-binary probe; R403 caution - unchanged from the M0-T127 recert). doctor readback (PAUSED_RECOVERY/22/53/0) not re-run against the live journal (R401); audit=53 corroborated from the preserved copy.

## (2) Protocol QA

**(a) Both s4 commands parse-validate** via `command_docs.validate_command(build_parser())`: Step 1 `clear-recovery` -> **ok**; Step 2 `start --max-cycles 3 --max-tasks 3 --packet-queue ...` -> **ok** (all five pinned flags present, `dispatch_inputs_missing` empty, new optional flags accepted). No execution.

**(b) Traced >=8 citations to source:** tree `b392100930...` (git rev-parse) - golden blob `deeca07b...` (git rev-parse) - golden 42 sub-minute (my run) - cross_task 45 (my run) - whole suite 3035/2/0 (my measurement at identical material) - audit 53 (preserved copy) - transcript 97 - wt-m0t107 `796e18f` clean - tooth 12/0 - modularity 0 - verify-controller PASS - baseline 2990+35+10=3035. All reproduce.

**(c) Preflight rows executable:** row 2 `git rev-parse HEAD:tools/agent_supervisor` == `b392100930...` executes and matches; row 6 `supervisor_command_doc_check.py` exit 0. Rows executable as written.

**(d) Seven-fact proof surfaces are REAL production artifacts** (grep-verified): fact 1 `over_ceiling_session_shed` -> loop.py:1086; fact 5 durable key `task_advancement/<id>` -> next_task.py:51 (`ADVANCEMENT_KEY_PREFIX`); fact 6 `cross_task_dispatch` -> next_task.py:866. All present in production code, not invented.

**(e) Queue format + prerequisites accurate:** `load_task_queue` (next_task.py) documents exactly the protocol s3 format `{"tasks":[{task_id,packet_path,worktree,branch,repo}]}`, fail-closed on malformed. The s3 per-successor prerequisites (packet parses; status `claimed`; deps `accepted`; no blockers/owner-gate; worktree exists, not primary, binds via launch seam; content unchanged) map exactly to the eleven fail-closed categories in `evaluate_eligibility` I verified at M0-T128.

**(f) ASCII:** recertification.md 0 non-ASCII; commissioning-protocol.md 0 non-ASCII.

## (3) Consistency sweep - clean

Across all three deliverables (recertification.md, commissioning-protocol.md, evidence-map.json) plus the M0-T096 activation-package refresh: **no** residual claim that the orchestrator will run anything (the protocol states "the orchestrator never executes any command below (R409)" and evidence-map R409 confirms "executed NO commissioning command; validations were parse-only"); **no** claim autonomy is already proven ("full autonomy is declarable ONLY after the owner-run live journey proves all seven R393 facts"); **no** claim that fewer than seven facts need the live journey ("all seven", "one command ... all seven facts"). The protocol correctly supersedes the Amendment-24 Stage-3 placeholder and preserves the R397/R403 holds until the owner personally types the commands.

## (4) Baseline reconciliation
2990 (M0-T127) + 35 (M0-T128 pass 1: ten-family cross-task) + 10 (M0-T128 remediation: mode-confinement 4 + real-`_run_loop` 1 + verbatim-dispatch 3 + sub-codes 2) = **3035**. No test removed; no existing test file modified in any wave (name-only diffs confirm only the new `cross_task` file among tests; M0-T129 touched zero test files).

## Non-blocking observations (carried, unchanged)
- next_task.py `review_signal` warning (split advisable on next growth) - below HARD 1000; not a failure.
- The `cmd_start` entry-to-dispatch gauntlet is exercised only at golden/live altitude (honestly disclosed; the real cli.py:3069 line + real `_run_loop` are separately covered per my M0-T128 delta PASS).
- M0-T096-activation-package.md (refreshed this window; not a "report" under duty 2f) retains typographic non-ASCII from earlier - pre-existing, command/hash-safe, flagged at M0-T127; candidate for normalization, not blocking.

**Requested gate result:** **PASS** at the terminal frozen identity (material `de18f27`, supervisor tree `b392100930...`, reviewed at tip `9e60d05`). All commands reproduce read-only. The package correctly stops-and-presents: the seven-fact live commissioning journey is a separate owner decision, and any live failure invokes R394.

Note for the orchestrator: reviewed via `git checkout --detach 9e60d05` in my own isolated worktree (clean tree restored first; my untracked memory index + a local memory edit set aside and re-applied). The orchestrator owns this worktree's post-review lifecycle.
---VERBATIM-END---
