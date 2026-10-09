# M0-T109 commissioning preparation + full section-2 preflight (D-024-R410..R416)

Orchestrator, 2026-08-31, session `session_01SfXcRw7emzdojCDJmKxNTM`. Authority: owner
directive 2026-08-31 (Amendment 26, `source-026-amendment.md`) naming **M0-T109 the SOLE
commissioning successor** — the owner's exercise of campaign seq-54 NEXT branch (1). The
orchestrator prepared the successor under the normal Tier A control process, wrote the
one-entry queue, and re-ran the COMPLETE `M0-T129-commissioning-protocol.md` section-2
preflight. **No section-4 command was executed (R414/R409).**

## 1. Preparation record (R410/R411)

| Item | Value |
|---|---|
| Amendment-26 capture | `e1ad02d` (rows R410-R416; verification skeleton; validator EXIT=0) |
| G0 readiness | PASS, `M0-T109-G0-readiness.md`, reviewed_sha `e1ad02d0efa3...` |
| Claim | `claimed` by `supervisor-loop-fable-producer`, refs `D-024:ALL` (evaluate_task_refs ok; applicable = exactly R410-R416) |
| Isolated worktree | `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t109`, new branch `task/M0-T109-guard-hardening`, base `6d2e816` (guard/test content == accepted material `de18f27`), `status --porcelain` empty |
| Queue file | `C:/Users/MLFLL/Downloads/nyc-zoning/commissioning-queue.json` (the exact path the presented Step-2 command names), sha256 `11eaa5a7b006ac7d1e1edd9b29574727c9a4bd27fa63ed4e70671fcd36fe2f8e` |
| Queued packet digest | `371bed1a8b29fb6f024e16c316d6924ba23c8b966f4d632d4077a4f66b5eb26b` (raw-bytes sha256 of `project-control/tasks/M0-T109.json` in its final claimed state; the packet must not be edited again before the journey or the live engine reads it `stale_packet`) |

Queue file content (verbatim):

```json
{
  "tasks": [
    {
      "task_id": "M0-T109",
      "packet_path": "C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/tasks/M0-T109.json",
      "worktree": "C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t109",
      "branch": "task/M0-T109-guard-hardening",
      "repo": "C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t109"
    }
  ]
}
```

`repo` is the worktree itself — the protocol-allowed single-checkout shape, so evidence
and the Codex reviewer bind to the WORKER'S tree, never the control checkout.
**Section-3 per-successor prerequisites verified through the REAL production engine**
(`load_task_queue` + `evaluate_eligibility`, pure read-only calls, no journal write):
1 entry parsed; verdict **ELIGIBLE** ("M0-T109 is eligible for supervised execution") —
packet parses, ids match, status `claimed`, zero blockers, no owner-gate field, sole
dependency M0-T108 `accepted`, worktree exists / is not the primary checkout / binds via
`enforce_launch_bindings`, digest fresh. Preparing the successor changed NO supervisor
file (no R247 re-trigger).

## 2. Complete section-2 preflight (all 8 rows)

| # | Row | Result |
|---|---|---|
| 1 | tree clean; HEAD == origin tip; CI green at tip | **PASS** — verified at the pushed seq-55 tip (control-plane landing chain from `6d2e816`); CI conclusions recorded live post-push in the session report; material identity unchanged by these control-plane commits (`de18f27`) |
| 2 | `HEAD:tools/agent_supervisor` | **PASS** — `b392100930bd4213cab90eb02aafa6d0d568f849` (unchanged) |
| 3 | CLI identities | **PASS** — claude.exe 2.1.251, supervisor-native `sha256_head+size` digest `d6f6c29a8ac6b3cf...`, 217,360,032 B (UNDRIFTED); codex-cli 0.146.0 |
| 4 | `verify-controller` | **PASS** — "controller verified, including the external config.toml binding" (manifest `841ed11c...`, 125 files) |
| 5 | `doctor` (full, non-live) | **PASS** — overall PASS; config OS-ACL PROTECTED; journal integrity ok; readback `PAUSED_RECOVERY`, transitions 22, audit 53, pending effects 0, surviving children 0 |
| 6 | `supervisor_command_doc_check.py` | **PASS** — 12 commands checked, 0 failures, exit 0 |
| 7 | `wt-m0t107` | **PASS** — clean at `796e18f`, branch `task/M0-T107-plugin-portability` (untouched, R413) |
| 8 | queue exists/parses; every successor meets section 3 | **PASS** — see section 1 (real-engine ELIGIBLE verdict) |

**R408 refresh (mechanical command validation, this session):** both section-4 commands
were re-validated against the live CLI contract — `build_parser()` parses Step 1
(`clear-recovery`) and Step 2 (`start --mode limited-auto --owner-enable-bounded-auto ...
--max-cycles 3 --max-tasks 3 --packet-queue ...`) exactly as presented;
`dispatch_inputs_missing` is EMPTY for Step 2. **Neither command was executed.**

**Preservation (R413) re-verified after preparation:** M0-T107 packet untouched;
`wt-m0t107` clean `796e18f`; journal `PAUSED_RECOVERY` / transitions 22 / audit 53 /
effects 0; PR #241 untouched.

## 3. Seven-fact sufficiency of the ONE-task queue (R415) — explicit answer

**YES — a one-task queue is sufficient to prove all seven R393 facts.** No fact requires
an M0-T109-to-second-task advancement, so the R416 stop-condition is NOT triggered and no
second queue entry is proposed. Mechanism mapping at the certified identity:

| Fact | Proof with the one-entry queue |
|---|---|
| 1-5 | Proven within the first task exactly as certified: over-ceiling shed, fresh Fable 5 worker in `wt-m0t107`, validated checkpoint to Codex, independent Codex review, and the audited exactly-once `task_advancement/M0-T107` CAS record (advance-BEFORE-select) |
| 6 | "Next bounded task is selected" — the driver's between-task seam + `evaluate_eligibility` over the M0-T109 entry, then the `cross_task_dispatch` audit row (successor=true) and launch in `wt-m0t109` |
| 7 | Proof surface is ">= 2 tasks dispatched in one journey, zero owner interventions between" — M0-T107 + M0-T109 = 2 dispatched tasks. Fact 5's advancement duty binds M0-T107 specifically; no fact demands that the SECOND task also advance or that a THIRD be selected |

This matches the protocol's own section-4 statement: "A conservative first journey MAY
use `--max-tasks 2` with a one-entry queue - facts 1-7 are still all exercised (one
cross-task selection)". Journey-end behaviour with the PRESENTED command
(`--max-tasks 3`) and this one-entry queue: after M0-T109's run the ordered list is
exhausted and the journey lands `queue_exhausted` — an honest, visible stop reason in
the driver's `task_queue` result, not a failure. The presented command therefore remains
valid AS WRITTEN; the owner MAY optionally type `--max-tasks 2` for the conservative
shape, but no edit is required. (Second-selection exercise — `--max-tasks 3` with a
two-entry queue — remains available as a later owner choice; identifying candidates for
it was NOT needed because no fact requires it.)

## 4. What remains owner-only

Exactly the two section-4 commands, typed personally by the owner (Step 1
`clear-recovery` — which ends the R374-era preservation by owner decision — then Step 2
the limited-auto start). Any live failure: R394 — stop without retry, preserve
byte-for-byte, one consolidated assessment. Standing gates untouched: never merge
PR #241; autostart, C1 canary, Telegram live send, natural-event graduation, OS-ACL,
production, credentials, payments, legal — all owner-only and closed.
