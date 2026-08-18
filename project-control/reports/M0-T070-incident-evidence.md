# M0-T070 — Incident evidence: run_M0_T063_A1 fail-closed stop (D-014)

Qualifying evidence for the supervisor defect lane (supervisor-freeze §2/§3): a
**reproduced defect** and **inability to complete an authorized product task**.
All facts below were read from the live runtime evidence **read-only**
(`audit.jsonl` is an append-only file; the SQLite journal was opened with
`mode=ro&immutable=1` and never mutated — D-014 prohibition 3).

## Run identity

- run_id: `run_M0_T063_A1` — D-013 Unit A1, ledger task M0-T063
- controller: `0.4.0-phase4`
- checkout: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t063`
  (branch `task/M0-T063-context-index-a1`, clean at
  `de2f224a7db16405edfc0e2f2f0902f5164819a0`)
- runtime dir: `%LOCALAPPDATA%/NYCBuildabilitySupervisor/1854a2a4ff3baf3d…`
  (`audit.jsonl` 9,367 bytes; `supervisor_journal.sqlite3` 73,728 bytes)

## Audit chain (verbatim sequence)

| seq | event | fact |
|---|---|---|
| 1 | `start_command` | operator start, journal at IDLE → PREFLIGHT |
| 2 | `preflight_pass` | preflight succeeded |
| 4 | `approval_deferred` | `ASK:undocumented_command`, Bash, task M0-T063, request `85d454e2-39e0-4e4a-b1c7-6d1de898a7cb`, 2026-08-18T05:18:49Z |
| 5 | `approval_deferred` | `ASK:undocumented_command`, Bash, request `0446ed2c-f7ad-4bfc-a493-e569bb91a491`, 05:20:33Z |
| 6 | `approval_deferred` | `ASK:undocumented_command`, Bash, request `7a3d51cb-9a85-443a-b75e-9fa5d65046c3`, 05:20:39Z |
| — | `claude_process_started` → `unsafe_condition` → `no_valid_checkpoint` | worker exited rc 1 with no structured checkpoint; state → PAUSED_RECOVERY; no Codex review occurred |
| — | `approvals_revoked` | `REVOKE_ALL` (S13.10), revoked=3, 05:30:44Z |
| — | `owner_cleared_pause` | owner clear-recovery; current state `PREFLIGHT` |

Every deferral carries the identical policy reason, verbatim:

> "the command is not an enumerated read-only git command and is not a
> packet-documented test command" (`policy_rule: S4.3/unclassified_command`)

Command text is redacted by design in the audit records (digests only:
`5ef70649…`, `755769c5…`, `573267a9…`).

## Journal state after revoke-all (the defect-B display bug, live)

Read-only query of `supervisor_journal.sqlite3`:

- `queued_asks`: 3 rows (`ask_85d454e2…`, `ask_0446ed2c…`, `ask_7a3d51cb…`),
  **all with `answered_at_utc = ''`** — i.e. still "open" to `open_asks()`.
- approval records `approval/85d454e2…`, `approval/0446ed2c…`,
  `approval/7a3d51cb…`: **all `status: REVOKED`**, `revoked_reason:
  "operator revoke-all"`.
- `state_kv.revoke_all`: `{"at_utc": "2026-08-18T05:30:44.984Z", "revoked": 3}`
- `current_state`: `PREFLIGHT`

So `pending-approvals` correctly reports 0, while `status` misleadingly lists
the three revoked requests under `open_asks` — exactly the owner's report.

## Root causes (source-confirmed before any fix)

**Defect A — packet commands never reach production authority.**
- `policy.py` `TaskAuthority.from_packet` accepts `documented_test_commands`
  only as a keyword argument, default `()` (pre-fix lines 883–915); it reads
  no packet field.
- Production `_run_loop` (pre-fix `cli.py:2487–2489`) called `from_packet`
  **without** that argument, so `_auto_test_command` (S4.1) iterated an empty
  tuple in every production run — the documented-test AUTO tier was
  unreachable, and every task test command classified ASK.
- The replay path (`replay.py:258–264`) **does** pass the commands, which is
  why shadow replay never surfaced the gap.
- `M0-T063.json` additionally carried no command-authority field at all
  (no canonical field existed to carry one).

**Defect B — revoked requests stay displayed as open.**
- `broker.py revoke_all` (pre-fix lines 665–689) flips `approval/*` records to
  `REVOKED` but touches nothing else.
- `queued_asks` rows are inserted (`broker.defer`, `loop.py` rotation/model
  stops) and **no code path in the package ever updated the table** — grep
  for `UPDATE queued_asks` returned nothing pre-fix.
- `cmd_status` read `journal.open_asks()` = `queued_asks WHERE
  answered_at_utc = ''` unconditionally, so revoked requests remained
  presented as open actionable questions forever.

## Repaired by

Ledger task M0-T070 (this task), directive D-014, branch
`task/M0-T070-supervisor-authority-repair`. The live A1 journal above is left
byte-for-byte intact; the repaired `status` reconciles it read-only and labels
the three revoked asks as non-actionable revoked history.
