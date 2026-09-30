# Memory index

- [Reviewed SHA via git refs](reviewed-sha-via-git-refs.md) — confirm a shared-checkout's reviewed SHA by reading `.git` pointer → `worktrees/<x>/HEAD` → `refs/heads/<branch>` when the git guard blocks git commands
- [AST source-scan soundness](ast-source-scan-soundness.md) — holes in `functional_text` identifier-extraction scans: `exec(`/`eval(` paren tokens are dead checks, import-only forms evade, corroborate one-way by direct read + grep
