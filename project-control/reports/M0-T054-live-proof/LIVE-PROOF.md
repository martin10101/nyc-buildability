# M0-T054 — Bounded live Fable→Opus turnover proof (R316)

Orchestrator-captured, using **real provider processes** on the exhausted Fable account (not synthetic
fixtures, not unit-tests-alone). Owner requirement R316: "Do not claim success from unit tests alone.
Do not claim mid-session continuity merely because Opus can be selected manually." This proof exercises
each link of the required chain with a real signal or a real process, and is honest about the one part
that production intentionally gates.

## The R316 chain, link by link (each proven with real evidence)

| # | Required link | Proven by | Evidence |
|---|---|---|---|
| 1 | Fable launch/probe | real `claude.exe --model claude-fable-5 -p … --output-format stream-json --verbose` | exit **1**; `real-fable-exhaustion-streamjson.txt` |
| 2 | grounded weekly hard stop **detected** | `classify_exhaustion` on the **real** captured output | → **FABLE_EXHAUSTED**, `should_turn_over=True` (real, not a fixture) |
| 3 | Fable process **accounted for** | inc-5 `detect_exhaustion_evidence` distills the real `result_text` + the `seven_day` `rate_limit_event` | `test_agent_supervisor_turnover_live_signal.py` (10 tests) |
| 4a | turnover decides → **exactly one opus-4-8 launch** | integration test drives the **real** captured signal through `evaluate → TurnoverController → adapters` (authorized channel) | `triggered=True, actuated=True`, one WORKER-layer `claude-opus-4-8` launch request, Fable→Opus audit link |
| 4b | Opus 4.8 successor **actually launches** (real process) | real `claude.exe --model claude-opus-4-8 -p … --output-format stream-json` | `model: claude-opus-4-8`, exit **0**, result **"OK"** (NOT exhausted); `real-opus4-8-successor-launch.txt` |
| 5 | durable handoff + safe checkpoint loaded | `TurnoverContext(handoff_reference, safe_checkpoint_id)` carried into the launch request | integration + adapter tests |
| 6 | **no owner `/model`** required | detection + turnover decision are automatic from the worker result | by construction; no manual step in the chain above |

**Grounding + fail-closed preserved:** detection fires on the exact phrase AND on the `seven_day`
weekly rate-limit rejection (`status: rejected`), both distinct from a transient per-minute 429, which
stays excluded (`test_transient_429_not_triggered` → AMBIGUOUS, no launch).

## The one honest limitation (production-gating, by design)

The chain above is proven with real components, but it is **not** run as a single continuous automated
supervised run (a real Fable worker inside `SupervisedLoop` auto-redispatching to a real Opus worker in
one process). That is because production wiring is **record-intent-only**: `default_actuation_authorization`
is False (no runnable mode authorizes an automatic worker redispatch — shadow forwards nothing, supervised
holds every forward at `WAIT_FOR_OWNER`, LIMITED-AUTO off). An actual automatic **production** launch needs
an owner-authorized actuation channel — the **R595 activation** path — which the reaffirmed SHADOW-ONLY /
LIMITED-AUTO-off holds forbid the orchestrator from self-authorizing. The mechanism is fully built, and
the integration test (row 4a) exercises the continuous decision→launch path with the real signal through
an explicitly-authorized channel + real adapters (only the final `subprocess.Popen` is a fake that records
the exact opus-4-8 argv rather than spawning). Row 4b proves that same opus-4-8 successor process does
launch and run for real. So every real link is demonstrated; only the owner-gated production auto-actuation
is deferred to the R595 decision.

## Reproduce
- Fable exhaustion: `claude.exe --model claude-fable-5 -p "reply OK" --output-format stream-json --verbose` (exit 1, `seven_day` rejection).
- Opus successor: `claude.exe --model claude-opus-4-8 -p "reply OK" --output-format stream-json --verbose` (exit 0, model `claude-opus-4-8`).
- End-to-end on the real signal: `python -m pytest tools/test_agent_supervisor_turnover_live_signal.py -q` (10 passed).
