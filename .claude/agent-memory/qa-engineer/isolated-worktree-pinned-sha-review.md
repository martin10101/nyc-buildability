---
name: isolated-worktree-pinned-sha-review
description: How to run a G4/gate review at a pinned SHA when landed in an isolated worktree whose own HEAD is unrelated to the review target
metadata:
  type: feedback
---

When a reviewer prompt pins a review SHA (e.g. "verify HEAD == <sha>") but the agent lands in an
isolated worktree whose own `git rev-parse HEAD` is a completely different, unrelated commit, do NOT
try to `cd` into the shared/primary checkout — the harness blocks that for worktree-isolated agents.

**How to apply:** the pinned SHA is almost always still reachable from the isolated worktree's own
`.git` (all worktrees share one object store). Confirm with `git cat-file -t <sha>` (expect `commit`)
and `git worktree list` (shows which real checkout, if any, sits at that SHA). Then:
1. Read individual files with `git show <sha>:<path>` for spot checks.
2. For anything that needs to actually EXECUTE (pytest, ruff, a tool that shells out to
   `git ls-files`), extract the whole tree with `git archive <sha> | tar -x -C <scratchpad-dir>` and
   run commands inside that extraction. This gives a real, executable copy without ever touching the
   shared/primary checkout.
3. If a tool depends on `git ls-files` (e.g. this repo's `tools/modularity_check.py`), the plain
   archive extraction has no `.git` and the tool fails closed with a git error. Fix: `git init` +
   `git add -A` INSIDE the scratch extraction only (a throwaway, fully-isolated repo scoped to the
   scratchpad) so the tool's `git ls-files` call resolves. This never touches the real repository's
   git state — it's a disposable repo that only exists to satisfy one tool's dependency.
4. For a RED-on-old audit, don't just trust the producer's narrated pass/fail counts: independently
   `git show <base-sha>:<file>` the pre-fix production files into a SEPARATE scratch copy (keep the
   FIXED test files), rerun the targeted tests there, and reconcile pass/fail per individual test name
   — not just the aggregate count. A coincidental pass on old code (e.g. an assertion whose expected
   value happens to equal the pre-fix hardcoded default) is legitimate and should be reported as such,
   not treated as a red flag, as long as the paired test that WOULD catch the defect does fail on old
   code.
5. To prove a grep/source-scan regression test is non-vacuous (not just checking it exists), mutate a
   SEPARATE scratch copy of the fixed tree (inject the literal string the test forbids into an
   unrelated-looking declaration) and rerun just that one test — it should fail and correctly name the
   mutated file.

See also [[m5t028-g4-test-adequacy-review]] for a worked example of this whole method end-to-end.
