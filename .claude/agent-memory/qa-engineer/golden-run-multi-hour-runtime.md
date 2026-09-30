---
name: golden-run-multi-hour-runtime
description: tools/test_agent_supervisor_golden_run.py takes ~3+ hours wall time — budget hours, do not kill as hung
metadata:
  type: project
---

`python -m pytest tools/test_agent_supervisor_golden_run.py -q` runs ~3h13m wall
(42 passed, exit 0, measured 2026-08-30 on the M0-T125 G4 gate). It exercises real
subprocess launches / grace-window / watchdog timers, so multi-hour runtime is
EXPECTED, not a hang.

**Why:** a future QA reviewer timing this pack against a normal test budget (minutes)
will wrongly conclude it hung and kill it, losing the run.

**How to apply:** run golden_run in the background (Bash run_in_background) at the start
of a supervisor gate; keep verifying other claims while it runs; only judge it complete
on the recorded exit code. The fast sibling packs are quick: launch_seam ~59s (64 tests),
bounded_mode ~12s (91 tests). See [[d024-live-loop-evidence-artifacts]].
