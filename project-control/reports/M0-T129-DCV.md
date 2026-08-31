# M0-T129 - DCV verification report (independent directive-compliance-verifier, read-only) - VERBATIM agent return (transport entity-decoding only)

Orchestrator capture note: returned 2026-08-31. VERDICT: ALL 7 rows (R401/R402/R403/R406/
R407/R408/R409) SATISFIED at material de18f27, tip 4b4583d. The DCV reproduced the read-only
core itself (golden 42/42 in 46.15s - the fourth sub-minute datapoint; validator EXIT=0;
anchors; both command validations; the fact-6 grep; the LIVE journal final re-check) and
recorded the honest correction chain (pre-fix G4 PASS + C1/N1/N2 fixes + dual delta-ack
CONFIRMED). Includes the complete Amendment-22/24/25 window DCV summary: T126 18/18, T127
22/22 + delta rows, T128 6/6, T129 7/7 - the controller is DCV-certified at frozen material
de18f27 with the seven-fact live journey remaining the owner's decision.

---VERBATIM-BEGIN---
The delta-acks confirm the honest chain: both G3 and G4 verified their PASS stands at the corrected protocol text; the corrected protocol is stable from 1d4ecea through HEAD and equals the submit reviewed_sha. Both reviewers independently grep-confirmed the fact-6 correction (matching my own M0-T128/de18f27 grep). I now have complete coverage. Here is my DCV record.

---

# DCV REPORT - Task M0-T129 (D-024 Amendment 25 terminal; rows R401/R402/R403/R406/R407/R408/R409)

## VERDICT: **PASS** - ALL 7 applicable requirement rows SATISFIED

**Reviewed identity:** material `de18f27` (report-only window). Branch tip HEAD = `4b4583d`. Content identity: `git diff de18f27 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` **EMPTY** (T129 changed only reports; supervisor tree unchanged since the M0-T128 wiring). Submit `reviewed_sha 012be56`; the corrected commissioning protocol is byte-stable `1d4ecea..HEAD` and `012be56..HEAD` (empty diffs). Producer = `orchestrator-recert-runner` != every independent reviewer (code-reviewer/qa-engineer/DCV). Exactly ONE recert commit (`e4ab79c`).

## Row-by-row verdicts

| Req | Verdict | Primary evidence reproduced |
|---|---|---|
| **R401** (journal/evidence untouched) | SATISFIED | LIVE re-check (final): journal `PAUSED_RECOVERY`, transitions **22**, effects/outbox/inbox **0**, audit **53**; `wt-m0t107` clean at `796e18f`. Report-only window (allowed_paths = 3 report files); no supervisor code touched. |
| **R402** (gates/fail-closed/budget/audit/isolation/exactly-once maintained) | SATISFIED | Recert battery: golden **42/42** reproduced (46.15s); NO supervisor-path change in the window (empty diff de18f27..HEAD); `next_task` 18 + `cross_task` 45 reproduced (exactly-once/eligibility machinery intact); `modularity_check --check` 0 failures; validator EXIT=0. Full-suite 3035/2/0 + doctor PASS are orchestrator-captured (three independent measurements on file; Disc. 3). All M0-T128 owner-gate/exactly-once wiring unchanged (identity stable). |
| **R403** (window holds) | SATISFIED | PR #241 **OPEN**, updatedAt 2026-08-20 (untouched). No clear-recovery/loop start/live commissioning - the unchanged journal (PAUSED_RECOVERY/22/53) is the proof. |
| **R406** (R247 recert ONCE + gates + DCV) | SATISFIED | ONE recert (`e4ab79c`) at final frozen `de18f27`. Anchors verified by `git rev-parse`: supervisor tree = `b392100930bd4213cab90eb02aafa6d0d568f849`, golden blob = `deeca07bf2b6...` (unchanged); tree@HEAD == tree@de18f27 (unmoved). Validator EXIT=0 (reproduced); golden 42/42 (reproduced). Gates G0/G3/G4 PASS recorded (G2 self-check + this DCV = closing steps). |
| **R407** (stop-and-present preflight + seven-fact protocol) | SATISFIED | `M0-T129-commissioning-protocol.md` opens "THE WIRING WINDOW STOPS HERE"; s2 complete preflight (8 rows); s1 seven-fact table maps all seven R393 facts to live mechanisms incl. cross-task selection (fact 6) + multiple successive tasks (fact 7) with no owner touch. **Fact-6 citation is code-accurate** (my independent grep at de18f27: `run_task_queue` live at cli.py:3069 + `evaluate_eligibility` + `is_advanced`; `select_next_packet` = ZERO production callers, correctly labeled simulation-only). The C1 correction is genuine. |
| **R408** (mechanically validate every presented command) | SATISFIED | I independently parse-validated BOTH commands via the real `cli.build_parser()` + `command_docs.validate_command`: `clear-recovery` -> `ok=True, code=ok`; `start --max-tasks 3 --packet-queue ...` -> `ok=True, code=ok` (all pinned flags present + `dispatch_inputs_missing` empty). Three prior independent validations (producer/G3/G4) corroborated. |
| **R409** (orchestrator never executes) | SATISFIED | Protocol s4 "OWNER-TYPED ONLY - R409"; header "the orchestrator never executes any command below (R409)". Journal unchanged (PAUSED_RECOVERY/22/53) proves no clear-recovery/start ran; validations were parse-only. Activation pkg restates R409 + owner-only live journey (R393/R394). |

## Discrepancies / observations (all NON-BLOCKING)

1. **G2 self-check gate not yet recorded.** `required_gates=[G0,G2,G3,G4]`; G0/G3/G4 PASS on file (G3 `reviewed_sha 1d4ecea` = corrections-applied; G4 `012be56` = delta-ack/corrected text; both content-identical to `de18f27`). No `M0-T129-G2.json` yet - G2 self-check + this DCV are the orchestrator-recorded closing steps before `accept()` (CLI-enforced). Normal in-flight state, not a producer defect.
2. **Honest correction chain (recorded, not a defect).** G4's first PASS (`3477f89`) was on the PRE-FIX protocol text (`9e60d05`); the C1/N1/N2 report-only corrections were then applied (`1d4ecea`) and BOTH G3 and G4 re-confirmed PASS at the corrected text via `M0-T129-gate-delta-acks.md` (`012be56`). The corrected protocol is stable `1d4ecea..HEAD` and equals the submit reviewed_sha. All prior reports preserved; chain is honest.
3. **Orchestrator-captured recert items (not read-only-reproducible).** record-manifest 125-files digest `841ed11c`, verify-controller PASS, doctor PASS, full-suite 3035/2/0 (long run), CI green - require write/provider/network access. I reproduced the read-only core (golden 42/42, validator EXIT=0, anchors, cross_task 45, next_task 18, both command validations, LIVE journal); the rest are orchestrator-captured per the evidence-capture division of labor, corroborated by G3/G4. Not a defect.
4. **Carried non-blocking (from M0-T128, disclosed):** next_task.py modularity review_signal; cmd_start entry gauntlet exercised only at golden/live altitude; eligible-status narrow `{claimed}`. Honestly disclosed in the recert s5; non-blocking.

## Exact commands run (read-only)

- `git rev-parse HEAD` (`4b4583d`); `git diff de18f27 HEAD -- tools/ .github/ docs/CONTROLLER_UPDATE_RUNBOOK.md` (empty); `git diff 1d4ecea HEAD -- ...commissioning-protocol.md` (empty); `git diff 012be56 HEAD -- ...commissioning-protocol.md` (empty); `git merge-base --is-ancestor` (4b4583d/012be56/e4ab79c -> HEAD yes); `git rev-parse de18f27:tools/agent_supervisor` (`b3921009`) / `...golden_run.py` (`deeca07b`); `git log --grep="recertification PASS" -i` (one recert).
- `python -m pytest tools/test_agent_supervisor_golden_run.py -q` -> **42 passed** (46.15s).
- `grep -rn select_next_packet|run_task_queue tools/agent_supervisor/*.py` (fact-6: select_next_packet zero prod callers; run_task_queue @ cli.py:3069).
- `python tools/validate_directive_compliance.py --check` -> exit 0.
- `command_docs.validate_command(<cmd>, cli.build_parser())` on both commissioning commands -> both `ok=True, code=ok`.
- Read-only sqlite (`mode=ro&immutable=1`): PAUSED_RECOVERY/22/0; `wc -l audit.jsonl`=53; `git -C wt-m0t107 status` clean; `gh pr view 241` -> OPEN/2026-08-20.
- `Read` of recert, commissioning-protocol, evidence-map, G3/G4/delta-acks reports, activation package seventh refresh, gate records.

No writes outside my agent-memory scope; no `project_control.py`/git-write/`gh`-write/supervisor-write verb; live journal opened read-only only.

**Recommendation to orchestrator:** record this DCV as **PASS** for the 7-row set (R401/R402/R403/R406/R407/R408/R409) into `verification.json`; then record the pending **G2** self-check before `accept()`. This completes the Amendment-25 window's DCV record.

## Amendment-22/24/25 window - complete DCV summary
- **M0-T126:** PASS (18/18) - seven-property durable checkpoint + 17 corrections at `2d46fb0`.
- **M0-T127 r1:** PASS (22/22); **r2/r3 (Amdt-24):** R397/R398/R399 PASS after the `owner_decision`->`decision` fix + G3/G4 delta PASS.
- **M0-T128 (Amdt-25 wiring):** PASS (6/6) - live cross-task selection + exactly-once advancement behind the owner gate at `de18f27`.
- **M0-T129 (Amdt-25 terminal):** PASS (7/7) - ONE recert at `de18f27`, seven-fact owner-executed commissioning protocol (code-accurate fact-6), all commands validated + never executed, journal/PR #241 preserved.

The controller is DCV-certified at frozen material `de18f27`; the seven-fact live commissioning journey remains the owner's decision (R393/R394), with every command owner-typed only and never executed by the orchestrator.
---VERBATIM-END---
