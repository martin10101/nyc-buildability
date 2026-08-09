---
name: tooling-lock-byte-identity-crlf
description: On this Windows repo, byte-identity checks of committed lockfiles (requirements.txt) fail spuriously because core.autocrlf=true makes the working tree CRLF while the git blob and Linux CI are LF - compare against the git blob, not the working-tree file
metadata:
  type: project
---

When verifying that a committed lockfile (e.g. `services/api/requirements.txt`) is byte-identical to a fresh regeneration, do NOT diff the **working-tree** copy on this Windows checkout: `core.autocrlf=true` (confirmed 2026-07-20, M0-T020) rewrites the file to **CRLF** on checkout, while the **git blob** and any Linux CI runner see **LF**. A `uv pip compile`/`pip-compile` regeneration on Windows emits **LF**, so a naive `cmp`/`diff` reports "DIFFERS" with a byte delta of exactly one `\r` per line (e.g. 851 lines → 851-byte difference), which is a pure line-ending artifact, NOT a resolver difference.

**Why:** `git ls-files --eol -- <file>` on this repo returns `i/lf w/crlf attr/` (index=LF, worktree=CRLF, no `.gitattributes` override). The M0-T018 `api-lock-verify` CI job passes because it runs on Linux where both sides are LF.

**How to apply:** for any lock byte-identity proof, compare the regen against the canonical blob:
`git show HEAD:services/api/requirements.txt > blob.txt` then sha256/`cmp` the regen vs `blob.txt`. If they still differ, normalize both with CRLF→LF and re-compare to isolate whether the residual is a genuine resolver change. Report the git-blob sha256 as the authoritative result. This also confirmed uv 0.11.28 and 0.11.29 produce byte-identical resolver output for the production lock (only the pinned-uv version string in docs/CI differs). Related: [[tooling-worktree-write-isolation]], [[tooling-grep-glob-gotcha]].
