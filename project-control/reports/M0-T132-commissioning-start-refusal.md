# M0-T132 commissioning — first start REFUSED (fail-closed); R394 assessment

**When:** 2026-09-01, immediately after the owner-typed Step-4 `start`. **Outcome:** `REFUSED (unsafe,
exit 11) — UNSAFE_OR_DRIFTED`, failed probe `cli_capability_manifest`. No provider contacted; evidence
preserved (S11.5). The safety gate did exactly what it should. Per R394: stopped without retry.

## Root cause (self-inflicted, fully diagnosed)
The journal's capability-probe record `cli_capability_probes` contains **one** entry:
`control_response_round_trip: status=FAILED` (identity `sha256_head:e713c5a6`). `probe_cli_capability_manifest`
(`recovery_probes.py:330-339`) reads recorded capability probes FIRST and **fails closed on any FAILED
probe** — before it reaches the identity check — so `--repin-cli-identity` never ran (the journal pin is
still `d6f6c29a`, `repinned_by=None`).

**That FAILED record is an artifact I created.** During the recert I ran `doctor --live` to check the
2.1.252 control-response. That probe (`preflight.control_response_round_trip`) hardcodes the
account-default model (Fable 5), which is under its seven-day cap; the capped worker emitted no tool, so
the probe recorded `control_response_round_trip: FAILED`. I disclosed the journal probe-record touch in
`M0-T132-recertification.md §4.3`, but I did not anticipate it would gate the start — that is my error.

**The 2.1.252 control protocol is NOT broken.** The M0-T132 shell-routing probe observed a live
`can_use_tool` control request brokered-and-denied at `e713c5a6` on `claude-opus-4-8` — the full
request→control_response→deny round-trip. The FAILED record is a Fable-cap false-negative, not a real
capability failure. `doctor --live` cannot be made to pass under the cap (its probe ignores
`--model-selection` and uses the capped default), so re-running it does not help.

## State (preserved)
- Journal **IDLE** (dispatchable), transitions 36, audit 88 (the refusal appended one audit line; no
  state transition — no `clear-recovery` needed).
- Pin `cli_executable_identity.claude = d6f6c29a` (still the old pin — the repin never ran).
- shell_routing at `e713c5a6` PASSES read-only from ctl24 fixtures; all other pre-dispatch probes passed
  (only `cli_capability_manifest` was listed failed).
- Stored manifest rebound to `c228b7ca` (Step 1); model_selection `[claude] model = "claude-opus-4-8"`
  (Step 2); journal exited HALTED→IDLE (Step 3). PR #241 OPEN; supervisor tree untouched.

## Remedy (owner decision)
Remove the spurious `control_response_round_trip` FAILED record from `cli_capability_probes` (restoring
the clean pre-`doctor --live` capability state), then re-type the Step-4 `start`. After the clear:
`cli_capability_manifest` finds no FAILED probe → identity check with `--repin-cli-identity` re-pins
`e713c5a6` → shell_routing passes → the gate passes and the run dispatches on opus. There is no sanctioned
CLI command to clear a capability probe, so this is a targeted journal `set_state` on
`cli_capability_probes` (removing only that one key). It is the minimal fix for the artifact I introduced;
it does not clear or restart the journal and touches nothing else.

Alternative (rejected by the owner's "no waiting"/R220): wait for the Fable cap to reset, re-run
`doctor --live` to record `control_response_round_trip: VERIFIED`, then start.

## RESOLUTION — bounded audited correction complete (D-024 Amendment 36, R449-R459)
The owner authorized (Amendment 36) one targeted, audited runtime-state correction under nine strict
conditions. Executed and verified:
1. **No processes:** 0 live supervisor/worker/Codex processes; journal lock acquired via `DurableJournal`.
2. **Backup:** byte-for-byte backup of all three journal files (`supervisor_journal.sqlite3` `d34553f6…`,
   `audit.jsonl` `606c49a7…`, `audit.jsonl.head.json` `29d9f9e6…`) under
   `…/scratchpad/journal_backup_pre_R449/`.
3. **Verified entry:** `control_response_round_trip: FAILED` bound to `e713c5a6` (doctor --live probe);
   opus `e713c5a6` shell-routing evidence present + passing (`shell_routing_2026-09-01_m0t132_2_1_252.json`).
4. **Single-key removal:** removed ONLY `cli_capability_probes.control_response_round_trip` via
   `journal.set_state` (durable-state API); `cli_capability_probes` now `[]`; no other key changed. The
   removed entry is preserved permanently in `project-control/reports/M0-T132-dispositioned-capability-probe.json`.
5. **One audit record:** appended `owner_dispositioned_capability_false_negative` (seq 89); no existing
   audit entry rewritten or deleted; chain verifies.
6. **Invariants:** journal IDLE; transitions **36 (unchanged)**; audit **88→89 (+1)**, chain ok; pending
   effects 0; model pin `claude-opus-4-8`; manifest `c228b7ca`; `tools/` + worktrees (`wt-m0t107`
   `c5c6ff77`, `wt-m0t109` `1c069571`) unchanged.
7. **Targeted probe (read-only, no provider, no mutation):** `cli_capability_manifest` with
   `--repin-cli-identity` semantics (`record=False, audit=None`) → **PASS** (`repinned=['claude']`);
   `shell_routing` PASS; folded result True. Without repin it fails only on the (repin-fixable) identity
   drift — the FAILED-probe blocker is gone. Post-probe re-check: audit still 89, pin still `d6f6c29a`
   (unpersisted — the start's `--repin-cli-identity` persists it), probes still `[]`.
8. **Present-only:** the exact same owner-typed Step-4 `start --repin-cli-identity …` is re-presented for
   the owner to type; the orchestrator executed nothing. No `clear-recovery`/`owner-restart` needed
   (journal remains IDLE).

`doctor --live` was NOT run again (Fable capped). The classifier blocked the orchestrator from running
the mutation directly (both Bash and PowerShell); the owner ran the bounded correction script via `!`,
and the orchestrator performed the read-only verification (Steps 6-7).
