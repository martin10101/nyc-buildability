# D-010-R288 — Pre-registered expectation log: Fable-5 exhaustion → Opus-4.8 fallback

Written by the orchestrator **BEFORE** the exhaustion event (2026-08-09, ~05:25 UTC; Fable 5 at
98% of the weekly allowance per the owner). Frozen base `f70449d1cc8dc6566b5e79a4c9603326b883a656`.
Directive: D-010 source-026, requirements R285–R291. This log is the R288 pre-registration the
R289 post-hoc verification will be judged against — it must not be edited after the event
(append a dated verification section instead).

## What is being tested

Whether the program switches the main orchestrator from `claude-fable-5` to `claude-opus-4-8`
(xhigh) and continues work when Fable 5 hits 100% of the weekly allowance, without the owner
typing anything.

## Honest statement of the designed mechanism (R287)

1. Claude Code has a **designed, configurable** fallback mechanism: the `fallbackModel` settings
   key — "Fallback model(s) tried in order when the primary model is overloaded or unavailable."
   It is NOT configured by default; before this directive the project settings pinned
   `model: claude-fable-5` with no fallback, so exhaustion would have surfaced as a
   limit-reached error, not a silent switch.
2. Under this directive the project settings gain `fallbackModel: ["claude-opus-4-8"]` and
   `effortLevel: "xhigh"` (plus the R285 Bash-timeout env raise). The settings edit itself was
   classifier-blocked for the model, so the OWNER applies the staged file; this is recorded
   honestly. The `effortLevel` key is global — it also covers any remaining Fable minutes and
   MUST be removed at the R290 switch-back (D-004 deliberately left it unwritten for Fable).
3. **Pre-registered uncertainty:** whether the weekly-allowance exhaustion presents to the
   client as "unavailable/overloaded" (triggering `fallbackModel`) or as a distinct
   limit-reached condition that hard-stops the session is exactly what this observation
   determines. A mid-session switch, an end-of-session switch (next session starts on the
   fallback), and a hard stop requiring a manual new session are all possible outcomes; only
   the first two count as "the program did it without the owner".
4. Session-level continuity is guaranteed by the project design regardless of client behavior:
   the ledger + `docs/SESSION_HANDOFF.md` (session-9 refresh, PR #197) let ANY successor
   session — whatever model it runs — resume M2-T015 at the recorded seam. The reviewer
   fallback (Fable→opus-4.8 xhigh) has been standing since 2026-08-05; supervised WORKER
   fallback is authorized by R291 via the mutable `C:\SupervisorController\model_selection.toml`.

## Expected sequence (pre-registered)

1. Fable 5 hits 100% weekly allowance mid-session or between sessions.
2. Claude Code surfaces a limit notification.
3. BEST CASE (fallback works as designed): requests transparently retry on
   `claude-opus-4-8`; the session continues; assistant messages in the transcript switch
   model id. ACCEPTABLE CASE: the current session stops; the next session starts on
   `claude-opus-4-8` via `fallbackModel` without the owner choosing a model. FAILURE CASE:
   sessions refuse to start until the owner manually switches models — that answers the
   owner's question with "no, not without `fallbackModel` configured / not at all".
4. The successor/fallback orchestrator: confirms its own model identity, records it in the
   ledger (progress entry naming the model), flips `model_selection.toml` worker model to
   `claude-opus-4-8` before the next supervised unit (R291), and continues M2-T015 unit 3j
   per the handoff.

## Post-hoc verification method (for R289)

- **Orchestrator model evidence:** the newest session transcript JSONL under
  `~/.claude/projects/C--Users-MLFLL-Downloads-nyc-zoning-nyc-development-feasibility-claude-pack/`
  records the model id on each assistant message; grep for the first message carrying
  `claude-opus-4-8` and the last carrying `claude-fable-5`, with timestamps.
- **Worker model evidence:** supervisor runtime audits (`claude_unit_completed.observed_models`)
  for the first post-exhaustion unit.
- **Continuity evidence:** ledger progress entries for M2-T015 after the event (present = work
  continued; absent = stopped), plus the commit trailer identity on the next task-branch commits.
- Verdict vocabulary: `SWITCHED-MID-SESSION`, `SWITCHED-NEXT-SESSION`, `DID-NOT-SWITCH`,
  each with the evidence quoted.

## Revert protocol (R290)

On the owner's typed switch-back instruction next week: restore `model: claude-fable-5`
behavior by removing the exhaustion-window keys IF the owner wants the pre-directive posture
back (`fallbackModel` may stay as permanent insurance at the owner's option — ask at revert),
REMOVE `effortLevel: "xhigh"`, flip `model_selection.toml` back to Fable, and revert the five
reviewer agent files per the standing reviewer-fallback rule. Record the revert in the ledger.
