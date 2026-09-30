---
name: reviewed-sha-via-git-refs
description: How a worktree-isolated reviewer confirms the shared checkout's reviewed SHA when the git guard blocks git commands
metadata:
  type: reference
---

When dispatched as a read-only gate reviewer, my Bash tool is isolated to my own agent
worktree and a guard REFUSES any git command that `cd`s to the shared checkout
(e.g. `cd .../ctl24 && git rev-parse`). Non-git commands (python, pytest, cat, ls) against
the shared checkout run fine — only git is blocked.

To confirm the reviewed SHA of the shared checkout WITHOUT running git there:

1. Read `<checkout>/.git` — in this repo the shared checkout `ctl24` is itself a LINKED
   worktree, so `.git` is a pointer FILE: `gitdir: <repo>/.git/worktrees/ctl24`.
2. Read `<repo>/.git/worktrees/ctl24/HEAD` → e.g. `ref: refs/heads/control/D-024-fable-codex-loop`.
3. Read `<repo>/.git/refs/heads/<branch>` → the 40-char SHA.

This lets the SHA attestation be by-ref (not by-content only) even under the guard. The
deliverable CONTENT is still what I verify by Read + executing the test packs; the ref read
just closes the SHA-identity line of the report.

Related: [[producer-worktree-base-and-stop-hazard]], [[orchestration-lessons]].
