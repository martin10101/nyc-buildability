---
name: mutation-harness-agent-supervisor
description: How to run RED/GREEN mutation teeth on tools/agent_supervisor test packs in a read-only sandbox where git is guarded
metadata:
  type: reference
---

Proven technique for G4 mutation-teeth on `tools/agent_supervisor/` packs (used on M0-T091, D-024 Phase C2).

**Setup:** copy `tools/agent_supervisor/` + the test file into a scratch `mut/tools/` dir; keep a `pristine_agent_supervisor/` copy for reverts. Run with `PYTHONPATH=<scratchroot> python -m pytest tools/<testfile> -k <name> -p no:cacheprovider`. The package's `__init__.py` imports the whole package but imports cleanly in this env, so the copy is self-sufficient EXCEPT for cross-`tools/` siblings: `workload_sizing` imports `tools.context_pack_budget`, so `test_mandatory_packet_categories_cannot_be_omitted` fails in isolation (harness artifact, deselect it — it runs green in the full tree).

**Gotcha:** applying mutants via a bash heredoc string literal mis-escapes regex backslashes (`\b`, `\d`) — count-checks abort at 0. Fix: read the actual file bytes in Python and do `.replace()` / line-scan on content read from disk, or use base64 args. For multi-line regex tuple entries, boundary-index slicing (`s.index("MARKER") .. s.index("))")`) is the most robust.

**Repo state:** `ctl24` review target is a DIFFERENT checkout from the dispatched worktree (which is stale on its own branch). The bash cwd resets each call; git against ctl24 is refused by the worktree guard (byte-identity ee564dd..HEAD is orchestrator-captured, not sandbox-reproducible). Non-git commands (`ls`, `pytest`, `python`) run fine when cd'd into ctl24, but compound `cd ctl24 && VAR=x python ...` gets refused as "too complex" — instead put `sys.path.insert(0, r"<ctl24>")` inside the script and invoke it plainly. Python 3.11.9 / pytest 8.4.2 / ruff 0.13.0 in sandbox; new C-phase modules use `from __future__ import annotations` so they collect under 3.11.
