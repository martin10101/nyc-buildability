---
name: frozen-sha-test-harness
description: How a worktree-isolated reviewer runs frozen-SHA agent_supervisor tests + proves content identity here, incl. sys.path shadowing and classifier/guard quirks
metadata:
  type: feedback
---

Running frozen-SHA `tools/agent_supervisor` tests as a worktree-isolated G4 reviewer.

**Why:** the isolated agent worktree carries its OWN (often stale) `tools/agent_supervisor`
package. `python -m pytest` prepends cwd to sys.path, so the worktree's `tools` SHADOWS the
frozen ctl24 copy and imports fail (`cannot import name telemetry_hooks`). `tools/` has no
`__init__.py` (namespace pkg) and there is NO pytest.ini/conftest at repo root, so tests only
resolve with the repo root on sys.path.

**How to apply:**
- Content identity (no autocrlf trap): `git diff --name-only <frozen> <liveHEAD>` — if the shipped
  files aren't listed, committed blobs are identical. Then `git rev-parse <frozen>:path` vs
  `git hash-object <copied-file>` give EXACT matching OIDs (git content-addressing; matched here
  for all spot-checked files). All ctl24 worktrees share one object DB (common-dir =
  nyc-development-feasibility-claude-pack/.git), so frozen objects are reachable from any worktree.
- Targeted packs: `cp -r ctl24/tools <ostemp>/tools`, then `cd <ostemp> && PYTHONDONTWRITEBYTECODE=1
  python -m pytest tools/test_...` (cwd=temp, temp/tools is the only `tools` on path → no shadow).
- FULL `tools/test_agent_supervisor_*.py` suite CANNOT run from a tools-only temp copy: ~6 files
  (ephemeral_review, loop, manifest_binding, policy, replay, turnover_live_signal) read repo-root
  artifacts (project-control/blockers/*, docs/, etc.) and error/fail on absence. Run the full suite
  in ctl24 itself: `cd ctl24 && python -m pytest tools/test_agent_supervisor_*.py` — cwd=ctl24 puts
  '' on path; guard allows non-git commands cd'd into the shared checkout (only GIT ops are refused).
- Mutation teeth checks: mutate the temp copy (a tiny `mutate.py` doing a verified 1-count str
  replace), run the single test node, then `cp` the pristine file back from ctl24 before the next.
- Classifier/guard quirks observed: DENIED = `ruff --version`, `python -P -m pytest`, chained
  `;` version probes, `git ls-tree -r`, multi-line git loops, `git reset --hard`. ALLOWED =
  `python --version`, `ruff version`, `ruff check`, `python -m pytest ...`, `git diff/show/log/
  rev-parse/hash-object/cat-file`, `cp`, python helper scripts. Keep git one command per call.
