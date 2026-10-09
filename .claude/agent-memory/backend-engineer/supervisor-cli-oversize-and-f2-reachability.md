---
name: supervisor-cli-oversize-and-f2-reachability
description: tools/agent_supervisor/cli.py is grandfathered-oversized with tiny headroom — new operator commands go in a focused module via register_*_verbs; the F-2 class = unreachable owner recovery edges caught by a mechanical TRANSITIONS reachability test
metadata:
  type: project
---

Two stable facts for `tools/agent_supervisor` work (learned M0-T121, 2026-08-30).

**cli.py is grandfathered-oversized — do NOT add inline handlers.** `modularity_check.py`
`baseline_growth` fails closed when a grandfathered file grows past baseline + max(50, 10%).
For `cli.py` that limit was 2953 SLOC and HEAD was already 2927 (only ~26 SLOC headroom;
docstrings COUNT toward SLOC, `#`-comments and blanks do not).
**Why:** adding ~90 SLOC of command handlers to cli.py fails the gate.
**How to apply:** put the substance in a focused module and expose ONE `register_<x>_verbs(sub,
add_common)` that `build_parser` calls next to `register_operator_verbs` /
`register_codex_channel_verbs` / `register_telegram_verbs`; keep cli.py to an import + the register
call (~2 SLOC). Handler+argparse both live in the focused module (see
`operator_channel_cli.py` and `restart_channel.py`). Cross-module import is safe:
`operator_channel_cli` exposes `open_runtime`/`emit_payload` and imports neither cli nor the new
module, so a focused module may import them without a cycle.

**The F-2 defect class = an owner recovery edge the S7 table defines but no code fires.** Fixed
instances: `PAUSED_RECOVERY->PREFLIGHT` (`clear-recovery`), held-prompt `WAIT_FOR_OWNER->FORWARD_PROMPT`
(`resume-pending-prompt`), `HALTED->IDLE` + `EMERGENCY_STOPPED->IDLE` (`owner_explicit_restart`,
M0-T121 `owner-restart` / `acknowledge-emergency-stop`), and `WAIT_FOR_OWNER->PREFLIGHT`
(`owner_answer_validated`, `resume-after-answer`, discovered by the sweep).
**Why:** after a blocking/terminal stop, `recover_boot` classifies but never applies a transition,
and `assert_can_act()` fails closed for every `BLOCKING_STATES` member — so an unreached edge strands
the run (owner-typed start refuses `illegal_transition X->X (trigger 'act')`, exit 13).
**How to apply:** the mechanical operator-recovery trigger set = edges whose source is in
`BLOCKING_STATES | TERMINAL_STATES`, whose target is NOT, and whose trigger starts with `owner_`. A
removal-sensitive reachability test derives that set from `TRANSITIONS` and asserts each has a
registered CLI call site (resolve constant NAMES to values, strip docstrings, walk within
cli+focused-module). Each operator-recovery surface must be fail-closed: refuse under the durable
emergency-stop FLAG (direct to `stop --clear`), from any non-source state, and while open asks /
pending effects / surviving children / provider-identity drift / non-SAFE_CHECKPOINT recovery exist;
hold the single-instance lock across check+transition (exactly-once); clear no flag, reset no budget,
dispatch nothing; append a durable audited owner-recovery event. Live provider-CLI drift can't be
probed in a non-live command — rely on the recorded SAFE_CHECKPOINT (which includes the
`cli_capability_manifest` revalidation) and let the next `start` preflight re-probe
`recovery_probes.probe_cli_capability_manifest` live. Any supervisor edit re-triggers the R247
frozen-identity recertification.
