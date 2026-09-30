---
name: reviewer-worktree-git-plumbing
description: How a worktree-isolated reviewer verifies a frozen SHA in this repo — ctl24 shares the object DB, so git plumbing against any commit works from the agent worktree
metadata:
  type: reference
---

When dispatched as a read-only gate reviewer in an isolated agent worktree
(`.../nyc-development-feasibility-claude-pack/.claude/worktrees/agent-*`), the
main review checkout `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` is a LINKED
WORKTREE of the same repo (`ctl24/.git` is a file: `gitdir: .../nyc-development-feasibility-claude-pack/.git/worktrees/ctl24`).

Consequences for verifying a frozen reviewed SHA:
- The object database is SHARED. From the agent worktree, `git -C <my-worktree>
  rev-parse|show|cat-file|ls-tree|diff <frozen-sha>` resolves any committed blob,
  including the packet's material commit — no clone or fetch needed.
- The Bash guard REFUSES `cd`-into-ctl24 and command-substitution/`sed`/pipe
  chains ("too complex to verify it stays inside the worktree"). Use plain
  single `git -C "<agent-worktree-abs-path>" <verb>` calls, one per invocation.
- Read ctl24's checked-out ref directly: `.../.git/worktrees/ctl24/HEAD`, then
  `rev-parse` it. It is usually the SUBMIT-SEAM commit (one past the material
  commit); `git diff --stat <material> <seam>` confirms the seam changed only
  ledger/report files, so ctl24 working-tree copies of the material files equal
  the frozen identity and can be Read directly with line numbers.
- To read strictly-frozen content regardless of working-tree drift, use
  `git show <sha>:<path>`.

**How to apply:** at gate start, resolve the material SHA, `show --stat` it to
confirm the file count, `diff --stat material seam` to prove material files are
byte-stable, then Read ctl24 paths for line-numbered review. Verify forbidden/HELD
files are absent from the diff (not just "producer says untouched").
