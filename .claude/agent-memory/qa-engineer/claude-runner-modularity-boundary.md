---
name: claude-runner-modularity-boundary
description: G3/G4 reviews of tools/agent_supervisor/claude_runner.py MUST independently run modularity_check; the file sits at its material-growth limit and small edits trip a FAIL that producers have misreported as PASS
metadata:
  type: feedback
---

For any change to `tools/agent_supervisor/claude_runner.py`, independently run
`python tools/modularity_check.py --check` (EXIT code is authoritative) before trusting a producer's
"modularity PASS" line.

**Why:** As of 2026-08-31 (M0-T130 G4), the modularity baseline records claude_runner.py at **1258 SLOC**;
material-growth limit = 1258 + max(50, int(1258*0.10)) = **1383**. The file already sat EXACTLY at 1383
(parent 81d5a9ba). M0-T130 (20bfa449) added 17 SLOC -> 1400 > 1383 -> `FAIL baseline_growth` (exit 1).
The producer report claimed "modularity_check --check: PASS (0 failures); +~45 SLOC" — false; the effective
SLOC delta over the parent is +17, not +45, and the check fails.

**How to apply:** claude_runner.py is a grandfathered oversized file living on its growth boundary. Any
supervisor-defect-lane edit that adds even ~20 SLOC will trip modularity FAIL, and the fix is NOT achievable
within a packet whose allowed_paths exclude `tools/modularity_baseline.json` and `tools/modularity_exceptions.json`.
Remedy requires an authorized action: a reviewed path-exact exception, an approved baseline regeneration
(D-017-R110), OR (modularity-preferred) extracting the new logic into a focused module. Flag as blocking.
SLOC counting (source_lines): non-blank, non-`#`-prefixed physical lines; deterministic across Python 3.11/3.12,
so a local run reproduces CI. See [[m2t015-python312-and-gate-lessons]] for the ruff-version caveat (does NOT
apply to modularity_check, which is pure-Python).
