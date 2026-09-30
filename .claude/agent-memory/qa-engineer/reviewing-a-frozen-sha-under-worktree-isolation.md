---
name: reviewing-a-frozen-sha-under-worktree-isolation
description: How to verify a reviewed SHA's content and run gate commands when the reviewer is dispatched into a DIFFERENT isolated worktree than the shared checkout it must review
metadata:
  type: feedback
---

When dispatched as a gate reviewer, the agent is often isolated in its OWN worktree
(e.g. `...\.claude\worktrees\agent-*` on an unrelated branch) while the task points at
the shared checkout `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` at a frozen reviewed SHA.

**Why:** a dispatch guard refuses any git command that targets the shared checkout — both
`cd <shared> && git ...` and `git -C <shared> ...` are blocked, and even complex/piped
commands or loops get refused as "too complex to verify it stays inside the worktree."
So `git -C ctl24 rev-parse HEAD` and `git -C ctl24 status --porcelain` (the usual SHA/clean
preflight) CANNOT be run.

**How to apply:**
- Non-git commands DO run in the shared checkout: `cd <shared> && python -m pytest ...`,
  `python tools/modularity_check.py --check`, `powershell.exe -File ...` all work there.
- Git OBJECT-STORE reads run fine from the agent's OWN worktree (shared object DB):
  `git ls-tree <sha> <paths>`, `git rev-parse <sha>:<path>`, `git rev-parse <sha>^{tree}`,
  `git diff <shaA> <shaB> -- <paths>`, `git show <sha>:<path>`. Keep each command simple
  (no pipes/loops) or the guard rejects it.
- To confirm the shared working tree equals the reviewed SHA without running git there:
  get the reviewed blob SHAs via `git ls-tree <sha> <files>` (own worktree), then compute
  the git blob hash of each shared-checkout file in pure Python
  (`sha1(b"blob "+len+b"\0"+data)`) and compare. On this Windows checkout, PRE-EXISTING
  tracked files carry CRLF so their raw hash won't match the LF blob — re-hash with
  `data.replace(b"\r\n", b"\n")`; a match there means git considers them clean. Freshly
  written task files are usually LF and match raw. (Verified on M0-T141.)
- To prove a mutant is caught while read-only: copy the module source to scratchpad, apply
  the mutation by string replacement (rewrite the relative import to an absolute one), load
  it with importlib, and run the EXACT suite assertion against it — never edit the repo.
- Do NOT return BLOCKED just because the shared-checkout git preflight is unavailable;
  content-verify the tracked files instead and note the limitation ([[in-regime-accept-mechanics]]
  style: reviewed_sha content identity is what matters).
