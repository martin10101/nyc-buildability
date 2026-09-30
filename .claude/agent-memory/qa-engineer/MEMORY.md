# Memory index

- [Isolated-worktree gate reproduction](isolated-worktree-gate-reproduction.md) — how to reproduce tests at the frozen reviewed SHA when the reviewer's own worktree HEAD differs: git archive whole repo to scratch, --force-local tar, git-init scratch for modularity_check, explicit cwd for pytest, mutate scratch-only for removal-sensitivity
