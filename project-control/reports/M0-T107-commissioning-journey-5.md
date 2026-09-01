# M0-T107 commissioning journey 5 — FIRST live limited-auto dispatch on the admitted 2.1.252 identity; stopped `no_valid_checkpoint` (R394 assessment)

**When:** 2026-09-01, the owner-typed Step-4 `start` (fresh `--run-id m0t107-commission-20260901`) after
the 2.1.252 admission + the Amendment-36 capability correction. **Milestone + honest stop.**

## Milestone — the loop dispatched a real cycle end-to-end
Every pre-dispatch gate PASSED on the admitted identity (the admission + correction held):
`PREFLIGHT -> START_CLAUDE` `preflight_pass` ("Manifest, journal, lock, config, models, and capabilities
all verified"), then `START_CLAUDE -> CLAUDE_RUNNING` — the bounded Claude worker launched on
**`claude-opus-4-8`** (observed_models `[claude-opus-4-8]`, model_mismatch false), session `6c0129cb…`,
job-object contained, ran ~136.5s, 98 events, returncode 0, no timeout, no malformed/noise/duplicate
lines. This is the first real supervised cycle — the whole admission + correction chain works.

## The stop (fail-closed, correct — S14)
`CLAUDE_RUNNING -> PAUSED_RECOVERY` on `unsafe_condition`, reason:
> `invalid_checkpoint: the checkpoint does not conform: missing_fields: ClaudeCheckpoint missing required fields: ['branch', 'current_sha', 'starting_sha', 'worktree']`

The worker emitted a checkpoint (checkpoint_contract_appended true; the S8.3 contract requires EXACTLY
one JSON object conforming to `claude_checkpoint.schema.json` with every required field), but it
**omitted the four git-state fields** `branch`, `current_sha`, `starting_sha`, `worktree`. The
supervisor is the source of `branch`/`worktree`/`current_sha` (interpolated into `claude_checkpoint.md`
and the worker is told to echo them), so these were available to the worker; it did not include them.
Per S14 a nonconforming checkpoint is failure, never success → the run paused for a human. Exit 11.

## Contributing observation (not the stop cause)
Mid-run the worker attempted one Bash command the broker could not classify
(`S4.3/unclassified_command`: "not an enumerated read-only git command and is not a packet-documented
test command"; rejected suggestion `addRules`) → correctly DENIED (`permission_decisions: ['deny']`).
The command broker behaved correctly; this denial is not the checkpoint failure but shows the worker
reached for an out-of-contract action.

## Assessment
This is a **worker checkpoint-conformance defect on the certified run** — opus-4-8 produced a checkpoint
missing required git-state fields it was given. It is AD-093-qualifying evidence (a failed acceptance
scenario / worker behavior on the certified loop). It is **not** a drift, identity, manifest, routing,
or safety-gate failure — every supervisor gate did exactly the right thing. It should NOT be retried
as-is (the same non-conforming checkpoint is expected); it needs a defect-lane investigation of WHY the
opus worker omitted the fields (contract/prompt clarity for opus vs the Fable-validated contract; or a
parse/emit mismatch), then a fix under the standard gates.

## Preservation (R394)
Journal **PAUSED_RECOVERY** (transitions 40, audit 104, chain ok); pending effects 0; owner touches
counted **1 of budget 2** (within budget); run `m0t107-commission-20260901` budget UNLIMITED, elapsed
136.5s; the exhausted prior run `run_33dfa57d54db` record intact. No provider re-contacted. Stored
manifest `c228b7ca`, model pin `claude-opus-4-8`, supervisor tree + worktrees unchanged, PR #241 OPEN.

## Owner decision needed
The unattended run cannot resolve `no_valid_checkpoint` without a human. Options: (A) authorize a
defect-lane task to investigate + fix the opus checkpoint-conformance (recommended; AD-093 evidence =
this journey); (B) direct a specific adjustment. Do NOT re-run the same start expecting a different
checkpoint. The journal rests at PAUSED_RECOVERY; a future resume after any fix is again a `clear-recovery`
(PAUSED_RECOVERY -> PREFLIGHT) then an owner-typed start with a fresh `--run-id`.
