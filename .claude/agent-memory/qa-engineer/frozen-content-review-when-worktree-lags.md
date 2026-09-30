---
name: frozen-content-review-when-worktree-lags
description: How a read-only reviewer isolated in a lagging worktree runs tests at frozen content in ctl24
metadata:
  type: feedback
---

When dispatched as a read-only gate reviewer, your isolated worktree is often pinned to an
OLD commit (e.g. reviewing M0-T090 frozen at e8b21d1 while the worktree sits at an M0-T077
merge) and therefore does NOT contain the deliverable files. Do not try `git checkout`/`fetch`
to move it.

**Why:** the git-isolation guard refuses any git command that targets the shared checkout
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, and a reviewer must not run git write commands.
But the shared `ctl24` checkout already holds the frozen deliverable content when the task says
"later commits control-plane only" (the `tools/**` source is unchanged since the frozen SHA).

**How to apply:** Read deliverables directly from `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/...`
and run tests/probes with `cd C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 && python -m pytest ...`
(non-git commands with cwd=ctl24 are allowed; only `git`/`gh`/`project_control.py` are blocked).
Corroborate you are on frozen content by reproducing the producer's exact test counts. For
in-memory mutation teeth, monkeypatch module globals/methods via `python -c` (writes nothing to
the repo). The heavy directive-compliance pack (~40 min composite) is slow — a narrow
`-k registry` slice ran in ~82s; verify the rest via orchestrator-captured stored evidence
rather than re-running the composite. Sandbox is Python 3.11.9; the tools/agent_supervisor
modules avoid PEP 695 generics so 3.11 collects them fine (unlike services/api PEP 695 code).
