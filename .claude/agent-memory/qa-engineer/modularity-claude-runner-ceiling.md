---
name: modularity-claude-runner-ceiling
description: On any agent_supervisor task gate, independently run modularity_check.py --check; claude_runner.py has a no-headroom 1410 exception ceiling that growth tasks trip while claiming exit 0
metadata:
  type: feedback
---

On every G4 gate for a task that touches `tools/agent_supervisor/`, independently run
`python tools/modularity_check.py --check` (exit code matters) — never trust the producer
report / G2 self-check "modularity exit 0" line.

**Why:** `tools/agent_supervisor/claude_runner.py` carries a FILE exception in
`tools/modularity_exceptions.json` with `max_lines: 1410`, `baseline_sloc: 1400` — a
deliberately NO-HEADROOM ceiling granted under M0-T130 whose own recorded reason says
"Narrow ceiling 1410 (no growth headroom); a module split is the recorded follow-up on the
NEXT substantial growth." Any task that adds even ~20-30 SLOC to claude_runner.py trips
`FAIL exception_exceeded ... grew past its reviewed exception ceiling (1410); renew through
review` and `--check` exits 1 (fail-closed, and CI-failing per CLAUDE.md principle 16).
This bit M0-T133 (D-024 Amendment 37): it grew claude_runner.py to 1432 SLOC while the
producer report AND G2 self-check both claimed "modularity exit 0". The producer's
`allowed_paths` did not include modularity_exceptions.json, so the ceiling could not be
renewed in-scope — meaning growth of claude_runner.py past 1410 is simply not admissible
without a scope expansion + reviewed exception bump, or without keeping the file <=1410
(e.g. push new orchestration into the extracted module instead of run_unit).

**How to apply:** Run the check yourself at the frozen SHA and read the output, not just
the exit code. If claude_runner.py (or any file with an exceptions.json entry) shows
`exception_exceeded`, that is a reproducible FAIL of a required gate teeth regardless of how
green the tests are — surface it as a blocking finding, don't PASS. The fix is either a
module split / footprint reduction, or an owner/G3-reviewed renewal of the exception
ceiling (which needs the exceptions file added to the task's allowed_paths).
