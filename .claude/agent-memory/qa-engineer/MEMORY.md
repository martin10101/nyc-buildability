# Memory index

- [Cross-worktree gate mechanics](cross-worktree-gate-mechanics.md) — how to run a G4 QA gate from an isolated worktree when the reviewed code is in the ctl24 shared checkout (git guard blocks ctl24-targeted git; read blobs by SHA from own worktree, run pytest with cwd=ctl24, verify content via pure-Python blob hashing, watch CRLF)
