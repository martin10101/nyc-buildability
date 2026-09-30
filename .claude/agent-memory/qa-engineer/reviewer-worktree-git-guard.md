---
name: reviewer-worktree-git-guard
description: How an isolated reviewer agent verifies a task branch it cannot git-read — diff base-vs-review dirs, gh with --repo, CI as authoritative web evidence
metadata:
  type: feedback
---

When dispatched as a read-only gate reviewer, the agent is isolated in its OWN worktree
(e.g. `.claude/worktrees/agent-<hash>`) sitting at the branch POINT-OF-DIVERGENCE (a base
commit like the pre-task main HEAD), while the review CONTENT lives in a different shared
checkout (e.g. `wt-m0t064`) that has the task branch checked out.

**Why:** the dispatch harness's git-guard refuses ANY `git`/`gh` invocation that redirects to
the shared checkout — both `cd <shared> && git …` AND `git -C <shared> …` are blocked ("must
target its own worktree"). It also refuses compound/looped shell it "cannot verify stays
inside the worktree" (break loops into separate plain commands).

**How to apply:**
- Non-git commands (pytest, `diff`, `wc`, `grep`, reading files) DO run against the shared
  review path — use them freely. `cd <shared>/services/api && python -m pytest …` works.
- To substitute for `git diff` (confirm "zero existing-test mods" / additive-only): run
  `diff -rq <own-worktree>/<subtree> <review-worktree>/<subtree>` and per-file `diff` — the
  own worktree at the branch base gives you the "before" side. New files show as "Only in";
  modified files show unified hunks you can confirm are purely additive.
- `gh` is NOT blocked when it does not redirect git to the shared checkout: `gh pr checks
  <n> --repo <owner>/<repo>` and `gh pr view` work read-only. Find the repo from
  `<primary>/.git/config` remote origin (worktree `.git` is a file: `gitdir: …`). Repo here
  is `martin10101/nyc-buildability` (NOT the folder name).
- CI (`gh pr checks`) is the AUTHORITATIVE evidence for thin-client web tests you cannot run
  (vitest/Playwright): the `web-e2e` and `web` jobs green at the PR head close the "web tests
  written but not executed" (N2) producer limitation. Verify the PR headRefOid matches the
  reviewed identity first (content commits + a trailing control-plane-only commit is normal).
