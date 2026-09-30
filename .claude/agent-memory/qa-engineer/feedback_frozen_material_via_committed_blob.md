---
name: frozen-material-via-committed-blob
description: As a worktree-isolated reviewer, verify frozen review material via committed blob hashes, never working-tree diffs (your worktree may be parked at an old ancestor commit)
metadata:
  type: feedback
---

When running a G4/quality gate as a worktree-isolated reviewer, verify the frozen material
by COMMITTED CONTENT IDENTITY, not by working-tree state.

**Why:** The reviewer's own dispatched worktree can be parked at a DIFFERENT (often older,
ancestor) commit than the branch HEAD under review. In the M0-T157 review my worktree HEAD
(d8b3899f) was an ancestor of the branch submit HEAD (b405d350); its working-tree copy of the
target file was the pre-fix version, so `git diff <frozen-sha> -- <file>` against my working
tree showed a large misleading diff that had nothing to do with the change under review.

**How to apply:**
- Run git from your OWN worktree dir (worktrees share the object DB, so any commit/blob is
  reachable). A `cd` into the shared/primary checkout before `git` is refused by the
  worktree-isolation guard; targeting the shared checkout is unnecessary anyway.
- Prove material stability with committed blobs, not the working tree:
  `git rev-parse <frozen-sha>:path` == `git rev-parse <branchHEAD-sha>:path`, and confirm no
  intervening commit touched it with `git log <frozen>..<HEAD> -- path`. Beware `A..B` is empty
  when B is an ANCESTOR of A — check ancestry (`git merge-base --is-ancestor`) before trusting it.
- Confirm the shared/primary checkout holds the authoritative material by hashing its working
  file: `git hash-object <shared-checkout>/path` should equal the frozen blob. RUN the tests in
  that checkout (it has fixed source + the real registry), not in your parked worktree.
- `gh run view <id> --json ...` was permitted for a read-only reviewer here; use it to
  corroborate CI conclusion + headSha, then confirm the fix blob is present at that headSha and
  that the relevant CI job actually executes the test (grep the workflow, e.g. ci.yml).

Related: [[probe-separator-deleting-normalizations]].
