# D-024 Amendment 36 — bounded owner-authorized runtime-state correction of the spurious control_response_round_trip FAILED capability entry (owner instruction 2026-09-01)

Captured: 2026-09-01 UTC by the orchestrator (Fable 5), verbatim, BEFORE acting.
Base identity at capture: HEAD `7006f855` (campaign seq 66). Amends: `source-001.md`.
Requirement IDs: D-024-R449..D-024-R459.

Reconciliation: after the owner-typed Step-4 commissioning `start` REFUSED fail-closed on
`cli_capability_manifest` (root cause: the orchestrator's earlier `doctor --live` recorded a
Fable-cap false-negative `control_response_round_trip: FAILED` under the account-default model,
which the capability gate reads before the identity re-pin), the owner authorizes ONE targeted,
audited runtime-state correction under nine strict conditions. This authorization is narrow: it
does NOT permit supervisor-source changes, broad testing, full R247 recertification, another
`doctor --live` run, or any unrelated journal modification. It sits within the commissioning phase
(post-M0-T132-acceptance) and does not reopen the accepted task.

Forward trace: "I authorize one targeted, audited runtime-state correction ... spurious Fable-cap
control_response_round_trip: FAILED" -> R449; "does not permit supervisor-source changes, broad
testing, full R247 recertification, another doctor --live run, or any unrelated journal
modification" -> R450; step 1 (no running processes; acquire lock) -> R451; step 2 (byte-for-byte
backup + SHA-256) -> R452; step 3 (verify the exact entry bound to e713c5a6 from the Fable-default
probe; opus e713c5a6 shell-routing evidence present+passing) -> R453; step 4 (preserve the failed
probe in evidence; remove ONLY that one entry via durable-state APIs, not a text editor; change no
other key) -> R454; step 5 (append ONE durable audit record of the owner disposition; rewrite/delete
nothing) -> R455; step 6 (post-verify invariants) -> R456; step 7 (run only cli_capability_manifest
+ related integrity; no provider; no unrelated suites) -> R457; step 8 (if pass, record + present the
same owner-typed Step-4 start with --repin-cli-identity, present-only) -> R458; step 9 (if any
invariant cannot be preserved, restore the byte-identical backup and stop without retry) + "Do not
run doctor --live again while Fable is capped" + "stop for my Step-4 command" -> R459.
Anchors: #authorization (R449), #prohibitions (R450), #preconditions (R451), #backup (R452),
#verify-entry (R453), #single-key-removal (R454), #audit-record (R455), #post-verify (R456),
#targeted-probe (R457), #present-start (R458), #rollback-and-stop (R459).

---VERBATIM-BEGIN---
I authorize one targeted, audited runtime-state correction of the spurious Fable-cap `control_response_round_trip: FAILED` capability entry. This authorization does not permit supervisor-source changes, broad testing, full R247 recertification, another doctor --live run, or any unrelated journal modification.

Perform the correction under these conditions:

1. Confirm no supervisor, Claude worker or Codex reviewer process is running, and acquire the normal controller/journal lock.
2. Create a byte-for-byte backup of the complete pre-repair runtime journal and record its SHA-256.
3. Verify that the exact active entry being dispositioned is `control_response_round_trip: FAILED`, bound to e713c5a6, produced by the Fable-default doctor --live probe, and that the approved Opus e713c5a6 shell-routing round-trip evidence is present and passing.
4. Preserve the failed Fable probe permanently in the audit/report evidence. Remove only that one false-negative entry from the active capability-probe gating cache using the existing durable-state APIs—not a text editor—and change no other key.
5. Append one explicit durable audit record stating that the owner dispositioned this exact record as a model-cap false-negative. Do not rewrite or delete any existing audit entry.
6. Verify afterward: journal remains IDLE; transition count is unchanged; audit chain grows only by the expected disposition record and verifies; pending asks/effects remain zero; model pin remains claude-opus-4-8; manifest remains c228b7ca; supervisor tree and worktrees remain unchanged.
7. Run only the targeted `cli_capability_manifest` pre-dispatch probe and directly related integrity checks. Do not contact a provider and do not run unrelated suites.
8. If the probe passes, record the bounded correction and present the exact same owner-typed Step-4 start command with `--repin-cli-identity`. Do not execute it yourself. No clear-recovery or owner-restart is needed because the journal remains IDLE.
9. If any invariant cannot be preserved, restore the byte-identical backup and stop without retry.

Do not run doctor --live again while Fable is capped. After completing this targeted repair, stop for my Step-4 command.
---VERBATIM-END---
