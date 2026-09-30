---
name: supervisor-reachability-sweep-granularity
description: Supervisor CLI-reachability removal-sensitivity tests must key on (state_from,trigger) EDGES, not bare triggers; shared trigger owner_explicit_restart hides single-edge surface removal. M0-T121 ReachabilitySweep is the corrected edge-granular reference.
metadata:
  type: feedback
---

The `tools/agent_supervisor` reachability/removal-sensitivity tests (`test_agent_supervisor_restart_channel.py::ReachabilitySweep`) derive operator-recovery edges from the `TRANSITIONS` table and assert each has a registered CLI surface.

**The trap (and why edge-granularity is mandatory):** `owner_explicit_restart` backs TWO distinct edges — `HALTED->IDLE` (`owner-restart`) and `EMERGENCY_STOPPED->IDLE` (`acknowledge-emergency-stop`). A TRIGGER-level sweep stays GREEN when one of the two edges loses its sole command surface, because the sibling keeps the bare trigger reachable — so a defined recovery edge can go call-site-less undetected (this was the original M0-T121 defect the QA gate caught, empirically: dropping only `owner-restart` still left `owner_explicit_restart` reachable).

**The correct pattern (M0-T121 rework, control head 6432d2d):** `operator_recovery_edges()` returns `(state_from, trigger)` pairs; `reachable_literals()` collects ALL closure string literals (no trigger intersection); `edge_has_surface()` requires SOME single handler's AST-closure to name BOTH the source state AND the trigger (per-handler, not unioned). This works ONLY because the handlers hardcode `expected_from_state` while the shared helpers (`_locked`/`_fire_edge`/`evaluate_preconditions`/`_current_state`) take state+trigger as PARAMETERS and hardcode no source-state constant — so each handler's closure contributes only its one edge's state/trigger. Verified empirically: dropping only `owner-restart` uncovers ONLY `(HALTED, owner_explicit_restart)`, not the EMERGENCY sibling.

**How to apply:** When gating a "removal-sensitive reachability" claim against an EDGE-worded requirement (e.g. D-024-R309 "fails whenever a defined recovery edge has no command call site"), confirm the sweep keys on `(state_from, trigger)` pairs and that per-surface drop tests assert BOTH the dropped edge becomes uncovered AND its shared-trigger sibling stays covered. Also confirm functional `cmd_*` tests don't silently bypass registration — add a `build_parser()` registration assertion (M0-T121 `test_parser_registers_the_three_recovery_commands`). A soundness check: if dropping one handler spuriously uncovers a sibling edge, a shared helper is leaking a source-state constant into every closure.
