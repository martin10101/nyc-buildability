---
name: reviewing-at-sha-outside-worktree
description: How to run a G4/read-only gate when the pinned reviewed SHA is not an ancestor of your isolated worktree HEAD
metadata:
  type: feedback
---

When a gate review is PINNED at a SHA that is NOT in your worktree (`git merge-base
--is-ancestor <sha> HEAD` returns NO, or the working-tree files lack the reviewed
changes), read every artifact via `git show <sha>:<path>` — never trust working-tree
files, they are a different branch.

**Why:** reviewer worktrees are isolated and frequently sit on a divergent
handoff/candidate branch; the material under review lives only in the task branch.
Running `pytest` in your worktree tests the OLD suite, not the reviewed content, and can
produce a misleading FAIL or PASS.

**How to apply (verification recipe that stands in for local execution):**
1. Extract the reviewed test/source files with `git show <sha>:<path>` (dump to /tmp).
2. Confirm every test the producer report NAMES actually exists at the SHA and its asserts
   match the report's claims (read the function body, not just the name).
3. Confirm the helper symbols/fixtures the new tests call exist at the SHA with compatible
   signatures (e.g. `_profile(bbl=...)`, `RecordingFetchers(ztldb=...)`).
4. Check the source diff with `git show <sha> --numstat -- <files>`: comment-only source
   changes + additive-only test changes (N insertions, 0 deletions) = nil regression risk.
5. Rely on the orchestrator-captured CI-green + focused-suite pass count as the executable
   authority (ADR-005 evidence-capture division: a reviewer verifies stored evidence when its
   sandbox cannot execute at the reviewed content — do NOT return BLOCKED for that reason).
