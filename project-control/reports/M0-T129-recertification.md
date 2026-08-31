# M0-T129 - R247 recertification at the Amendment-25 final frozen identity (D-024-R406)

Executed by the orchestrator (`orchestrator-recert-runner`) 2026-08-31 in the PRIMARY control
checkout. ONE recertification at ONE identity; re-triggered by the M0-T128 supervisor change.

## 1. The final frozen identity (post-wiring)

| Anchor | Value |
|---|---|
| Material commit (supervisor content) | `de18f27` (M0-T128 wiring + remediation; accepted at `8011b6d`) |
| `tools/agent_supervisor` tree | `b392100930bd4213cab90eb02aafa6d0d568f849` (moved from `46722aa1...` by the wiring: cli.py +12/-7, next_task.py +549) |
| Golden pack blob | `deeca07b` - UNCHANGED from the Amendment-22 certification (no golden edit in the wiring window) |
| Provider CLI | Claude Code **2.1.251 UNDRIFTED** - supervisor-native `sha256_head+size` digest `d6f6c29a8ac6b3cf...` reproduced this session; 217,360,032 B; no admission event, no repin |
| Codex CLI | codex-cli **0.146.0** unchanged |

## 2. Suite evidence at the frozen identity

| Run | Result |
|---|---|
| Golden certification pack, single process | **42 passed, 0 failed in 51.32s** (sub-minute, consistent with the resolved timing baseline) |
| WHOLE supervisor suite - all 70 files INCLUDING golden, one process | **3,035 passed, 2 skipped, 0 failed** (666.93s orchestrator reproduction; producer and G4 delta each measured the identical figure) |
| cross-task pack (the new wiring coverage) | **45 passed** (reproduced independently by the orchestrator, G3 delta, G4 delta, and the DCV) |

**Baseline reconciliation (freeze rule):** 2,990 (M0-T127 certification) + 35 (M0-T128 first
pass: ten-family cross-task coverage) + 10 (remediation round: mode-confinement, real-_run_loop
journey, verbatim dispatch-branch, sub-codes) = **3,035**. No test removed; no existing test
file modified in the window (verified by name-only diffs at both gate waves).

## 3. Controller binding, doctor, preservation

* `record-manifest` from the ctl24 root: **125 files**, new digest `841ed11c622aa416...`
  binding THIS post-wiring tree (prior manifest hash `793082af...` recorded pre-overwrite for
  provenance); round-trip verification passed; `verify-controller` PASS ("including the
  external config.toml binding").
* `doctor` (full, non-live): **overall PASS**; config OS-ACL PROTECTED; model selection
  accepted; journal integrity ok. `doctor --live` not re-run (R403 caution; the executable
  identity is byte-identical to the admitted control-response evidence).
* **Preservation (R401) verified at G0 and again at report time:** journal
  `current_state=PAUSED_RECOVERY`, transitions **22**, audit **53**, effects/outbox/inbox
  **0**; `wt-m0t107` clean at `796e18f`. No restart, no clear-recovery, no journal edit, no
  repin, no PR #241 action, no live launch in the window.

## 4. Tooling teeth

`modularity_check --check` failures 0; `supervisor_command_doc_check.py` exit 0 (12 commands,
0 drift - the two new flags carry certified defaults and every previously presented command
remains valid); ruff clean on all wiring-touched files; registry validator EXIT=0 at this
content (Amendment-25 rows registered); CI green on the pushed chain. Both commissioning
commands presented in `M0-T129-commissioning-protocol.md` were dry-run validated this session
against `build_parser()` + the pinned-flag set + `dispatch_inputs_missing` (both OK - the
R408 duty made mechanical; the queue-file path is an owner-created input the eligibility
engine validates at run time).

## 5. Verdict

R247 recertification: **PASS at the one final frozen identity** (material `de18f27`, supervisor
tree `b3921009...`). Any supervisor/operator-channel change after this point re-invalidates
certification and re-triggers R247. Carried non-blocking observations: next_task.py
review_signal (split advisable on next growth); the cmd_start entry gauntlet is exercised only
at golden/live altitude (honestly disclosed); eligible-status set is the narrow documented
{claimed}.
