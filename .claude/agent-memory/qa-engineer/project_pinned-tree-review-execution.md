---
name: pinned-tree-review-execution
description: How a worktree-isolated G4 reviewer can EXECUTE suites at a pinned SHA (git archive to scratchpad), plus the sandbox guard traps hit on 2026-09-14
metadata:
  type: project
---

A reviewer isolated in an agent worktree (HEAD != review pin) can still execute the packet's
test commands at the pinned content: `git archive <pin> services/api packages/contracts > x.tar`
(from the OWN worktree — object store is shared), extract into the scratchpad, `cd services/api`,
`python -m pytest tests/connectors -q`. Verified 2026-09-14 on M4-T020 (39 + 752 passed, ruff
0.13.0 clean at pin 16272c05).

**Why:** the isolation guard hard-refuses `git -C <primary-checkout>` AND "too complex" compound
commands (including some python heredocs — write scripts via the Write tool instead), so neither
landing in ctl24 nor redirecting git is available; but blob/commit reads and `git archive` from
the own worktree work fine.

**How to apply:** traps hit: (1) `tests/connectors/test_pluto_soda.py` reads
`packages/contracts/schemas/v1/*.schema.json` from the REPO ROOT — archive `packages/contracts`
too or you get 751 passed + 1 bogus FileNotFoundError; (2) `tools/modularity_check.py` needs a
live git checkout (`git ls-files`) — not runnable on an extraction, defer to CI; (3) local
Python 3.11.9 collected and passed the full connectors suite despite the repo's >=3.12 pin
(PEP 695 surfaces live elsewhere) — disclose the interpreter deviation, CI stays authoritative;
(4) `| tail` eats `$?` — take exit codes directly; (5) local env already has shapely==2.0.7,
pytest 8.4.2, ruff 0.13.0, fastapi/jsonschema/httpx.
