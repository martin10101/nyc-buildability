# D-011 — Amendment 003 (owner, 2026-08-11, session 16)

- Channel: owner_typed_instruction (continuation of the same reconciliation / open-Codex exchange)
- Recorded: 2026-08-11
- Frozen baseline: origin/main = 7cc1fed7ea66df8abe952e48bfea2451469f93ac (unchanged from source-001)
- Integration branch/worktree at capture: control/session15-acceptance (PR #220), HEAD 65adc7c, worktree .claude/worktrees/session15-acc
- Model in session: claude-opus-4-8 (owner set /model claude-opus-4-8 at session start)
- Append-only amendment to D-011; does NOT edit source-001.md or source-002-amendment.md.

## Verbatim owner text

Continue the NYC Buildability build (session 16). First run
`python tools/project_control.py status` and read `docs/SESSION_HANDOFF.md` on branch
control/session15-acceptance (PR #220) — the live integration branch off main 7cc1fed;
do control-plane work in its worktree .claude/worktrees/session15-acc.

State: M0-T055 ACCEPTED (real identity). M2-T016 verified 77/77 (accept is mechanical).
M0-T053 verified sound but order-blocked. M0-T057 guard built, BOTH reviews PASS.

Do these IN THIS FIXED ORDER (D-010-R283), using the accept-mechanics recipe in the handoff
(work in the #220 worktree, DO NOT commit until after accept, reviewed_sha==HEAD; I authorize
each accept — do NOT add the broad accept allowlist, D-011 R003):
1. Accept M2-T016: write its 77-row D-010 verification.json row from the independent DCV,
   record gates G0/G2/G3/G4/G5, re-submit at identity ac3d45cb, then accept.
2. Accept M0-T053: re-run its DCV at the new HEAD (R283 flips to PASS), record G0/G2/G3/G5, accept.
3. Land M0-T057 guard (reviews already PASS): record gates G0/G2/G3, accept; then drain the
   now-inert M0-T055 grandfather entry from validator c17.
4. Only then begin the supervisor safety fixes P1, P2, P3, P6 (frozen-lane, each its own gate
   wave) — the real remaining work before M0-T056 / R595.

Holds: M0-T056 not started, R595 not activated, no accept allowlist. Merge #219 (nanoid) when
convenient to green the security check on #218/#220. Codex model-fallback already resolved.go till the point where we can lunch codex absult no blocking on my end

## Interpretation notes (for the resolver; not owner words)

- This amendment adds an explicit EXECUTION plan (fixed order + per-accept authorization + a
  continuation authorization) on top of the D-011 corrections already captured in source-001/-002.
  It does NOT lift any hold. The source-001 prohibitions (no M0-T056, no R595 activation, no broad
  accept allowlist) and D-011-R019 remain in force; "go till ... launch codex ... no blocking on my
  end" is standing continuation authorization to work the chain autonomously up to the R595 flip,
  not authorization to actuate. "lunch codex" = launch Codex; "absult" = absolutely (owner typos
  preserved verbatim above).
- "I authorize each accept" = explicit owner authorization for the three in-chain accepts
  (M2-T016, M0-T053, M0-T057). The broad accept allowlist stays prohibited (reaffirms D-011-R003).
- "Codex model-fallback already resolved" = owner-recorded resolution of the D-011-R018 concern:
  Codex already attempts its main model first each session and only falls back on unavailability
  (non-sticky); no supervisor code change is owed for R018 on the Codex side.
- The accepts themselves are gated independently by the D-010 verification machinery on each task's
  own directive_refs (D-010:ALL); D-011 remains a NON-LEDGER governance sentinel (D-011-CORRECTION /
  governance) and does not rebind directive_refs onto those packets (two-lane principle).
