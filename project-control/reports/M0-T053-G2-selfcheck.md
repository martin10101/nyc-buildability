# M0-T053 — G2 producer self-check — VERDICT: PASS

Recorded by `orchestrator` (role self_check). Producer evidence, independently reproduced by the G3
code-reviewer and G5 security-reviewer at the reviewed material `a387331` (byte-identical to the accept-head
material identity `e6746f68`).

## Deliverables → evidence
- **C2 child-accounting wiring**: `ClaudeRunner` gains an optional journal; `run_unit` records the launched
  child right after `container.adopt(pid)` and settles after the `finally`; `cli._run_loop` passes
  `journal=journal` — the single keyword that makes `recover_boot`'s surviving-child fail-closed LIVE in
  production instead of inert (a surviving recorded child forces UNSAFE_OR_DRIFTED refusal on resume).
- **C1 containment gate**: new `containment_precondition()`; `cmd_start` evaluates it and refuses as the LAST
  gate before a spawn, auditing `containment_gate_refused`, with NO flag/env/config override (unbypassable);
  an undeterminable containment kind refuses with kind `unknown` (fail-closed).

## Test evidence (reproduced by BOTH independent reviewers)
- Full supervisor suite: **1493 passed / 2 skipped**, run twice — re-establishes the M0-T039 freeze baseline
  (bar ≥1165, 0 failures; pre-change baseline 1481/2). **+12 tests** added.
- Non-vacuity proven by five guard mutations, each reverted (gate-always-permits → 2 fail; delete record call
  → 4; delete clear call → 3; never-settle → 1; swallow unwritable-journal → 2).
- `ruff 0.13.0` on changed files: 5 pre-existing F401 only (no new lint).
- CI `supervisor-bridge (pytest tools/test_agent_supervisor_*.py)` green.

## Verdict
The scoped C1+C2 corrections are implemented, fail-closed, and covered. **PASS** (self_check; independent
confirmation is G3 code-review PASS unconditional + G5 security PASS).
