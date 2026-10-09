# M0-T107 cycle-2 start — REFUSED PRE-DISPATCH (stale_state, exit 13): the HALTED exit edge is unreachable

Recorded by the orchestrator 2026-08-30 (campaign seq 34 → 35). The owner executed the
Amendment-15 cycle-2 continuation exactly as supplied (`!` prefix, certified item-3 shape,
`--mode limited-auto --owner-enable-bounded-auto`, NO `--repin-cli-identity`, forward-slash
paths, all inputs named). Governing rows: D-024-R259 (stop and report the exact mismatch,
never improvise), D-024-R270 (no restart loop, no journal edits). **R300/R301 evaluated and
NOT triggered — this is not a counted stop** (see §3).

## 1. Verbatim outcome (owner-typed start, 2026-08-30)

```
mode:            limited-auto
classification:  SAFE_CHECKPOINT (safe_no_auto_resume)
next state:      PREFLIGHT
resume permitted:False
reason:          the last action has a verified after-effect and every invariant matches, but limited-auto was NOT already owner-enabled, so recovery does not resume by itself: it re-runs preflight and waits for an explicit operator start (S11.5). Recovery never enables or broadens limited-auto

NOT DISPATCHED. the loop refused to run: illegal_transition: illegal transition HALTED -> HALTED (trigger 'act'): no action is permitted while the supervisor is in HALTED
no provider was contacted.

REFUSED (stale_state, exit 13): illegal_transition
  mode: limited-auto
  source: loop
```

## 2. Root cause (primary evidence: code + journal; no producer claim involved)

The certified cycle-1 HALT_UNSAFE (exit 10) left the journal in `HALTED` — by design a
TERMINAL and BLOCKING state (`state_machine.py:92-104`). The state machine has always
defined the owner's exit edge — `HALTED → IDLE` on trigger `owner_explicit_restart`
(`state_machine.py:399`; sibling `EMERGENCY_STOPPED → IDLE` at `:397`) — but **that trigger
has ZERO call sites anywhere in the package**: it appears only in the transition table.
Concretely, on the owner's start:

1. `recover_boot` classified the at-rest journal SAFE_CHECKPOINT / `safe_no_auto_resume`
   and *recorded* "next state: PREFLIGHT … waits for an explicit operator start"
   (`recovery.py:349-357`), but `recover_boot` never applies any transition
   (`recovery.py:516-528`) — the journal stayed `HALTED`.
2. The explicit operator start then entered the loop, whose `assert_can_act()` fails closed
   for every `BLOCKING_STATES` member including `HALTED` (`state_machine.py:533-539`),
   surfacing through the typed-refusal path (`cli.py:3008`) as `stale_state` exit 13.
3. No documented operator surface can fire the exit edge: `clear-recovery` refuses any
   state that is not `PAUSED_RECOVERY` (`cli.py:1866-1871`), and `resume-pending-prompt`
   covers only `WAIT_FOR_OWNER`.

Net: **after ANY certified halt — including the designed-and-correct HALT_UNSAFE — no
documented surface can ever restart the loop.** The accept-time phrase "journal HALTED
(operator-startable)" (M0-T113 R299 readback; handoff seq 34 §5) is falsified live: the
restart intent exists in the transition table but was never wired. This is the third
instance of the F-2 defect class — "the edge the state machine always defined but no
command could reach" — previously fixed for `PAUSED_RECOVERY` (`clear-recovery`, V1.1 F-2)
and `WAIT_FOR_OWNER` (`resume-pending-prompt`, M0-T036), and cousin to the M0-T115
deny/approve ask-row omission. The `EMERGENCY_STOPPED → IDLE` edge (`:397`) is unreachable
for the same reason (latent sibling; `stop --clear` clears the durable flag, not the state).

## 3. Counted-stop determination (R300/R301 NOT triggered)

The refusal is PRE-DISPATCH: `dispatched: false`, "no provider was contacted", 0 provider
calls, no cycle entered, no S-series synchronous stop taken. The owner-touch budget remains
2/2 (S14 + S9 from cycle 1) — untouched. Cycle 2 never started, so this is not "cycle 2
produc[ing] another counted stop" (Amendment 15 s4); it is a restart-blocking seam defect
in the same category as the Amendment-11 addendum (M0-T115 seam). The R270 discipline was
applied: ONE owner attempt, no retry (the refusal is deterministic — no legal transition
exists), no journal edit, no improvisation.

## 4. State preservation (verified after the refusal)

`status` re-read live: state `HALTED`, mode none, journal ok, **transitions still 13 (no
state transition occurred)**, pending effects 0, queued questions 0, resolved history 3
(not actionable); audit chain ok, head sequence 31 → 33 (the refused start's own audited
`recover_boot` + refusal events — refusals are reports, and reports are audited). Worktree
`wt-m0t107` untouched; repository tree clean; HEAD unchanged at `2598103`.

## 5. Proposed disposition (owner decision at this seam)

A bounded AD-093 defect packet (supervisor-freeze §2 qualifying evidence: **reproduced
defect** — this report §1/§2; plus the falsified R299 "operator-startable" claim) to wire
the owner-explicit restart channel: an explicit, audited operator surface that fires
`HALTED → IDLE` on `owner_explicit_restart` (the `clear-recovery` pattern: refuses under a
durable emergency stop, refuses from any other state, clears no flags, dispatches nothing),
covering the `EMERGENCY_STOPPED` sibling edge by the same review, with removal-sensitive
regression tests and the H2 RepairRecord. Because the fix touches `tools/agent_supervisor/**`
it INVALIDATES the current certification and re-triggers the full R247 re-certification
window (M0-T115/T116 precedent) before the next certified start; the R276-pattern preflight
then re-runs and the cycle-2 start is re-attempted (still owner-typed, still WITHOUT
`--repin-cli-identity` — the CLI identity `d6f6c29a…` is pinned and undrifted). M0-T113
stays accepted and immutable; this is post-acceptance discovery handled as new work.
