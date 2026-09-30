---
name: reviewer-worktree-isolation-technique
description: How to review committed content authoritatively when the review agent is isolated in a stale worktree whose bash cwd differs from the Read tool's filesystem
metadata:
  type: feedback
---

When dispatched as a read-only gate reviewer in this repo, the harness may isolate the agent
in a git worktree (e.g. `.claude/worktrees/agent-XXX`) whose branch HEAD is an OLD base commit
(seen: d8b3899f, ~1255 files behind the candidate), while the **Read tool** resolves paths
against the real shared checkout (`ctl24`) holding the candidate content. So `Read` and `bash`
see DIFFERENT filesystems; a relative `sha256sum <path>` in bash can report "No such file" even
though Read just read it, and `git rev-parse HEAD` returns the stale base, not the reviewed SHA.

Rule: for a QA/gate review, treat `git show <sha>:<path>` (against the SHARED object DB) as the
ONLY authoritative content source — the frozen candidate SHA and the submit HEAD are both
reachable. Hash gate records with `git show <head>:<record> | sha256sum`.

**Why:** trusting the working tree gave contradictory results (dir `ls` found the gates dir but
`sha256sum` of a sibling file failed); only `git show` is stable and provably tied to the reviewed SHA.

**How to apply:** (1) Do NOT `cd` to the shared checkout — the worktree git guard refuses git that
leaves the isolated worktree, and refuses multi-line/compound git; run plain single git commands from
the worktree cwd. (2) Verify commits/ancestry with `git cat-file -t`, `git merge-base --is-ancestor`,
`git log --oneline`, `git diff --name-only A B`. (3) `git ls-remote origin <refpattern>` works for
AS-NEG remote checks (read-only, network OK). (4) In this repo's gate evidence, each index entry's
`record_sha256` == the sha256 of the committed gate-record JSON file (confirmed by 3 spot-checks on
M0-T136); gate_runner.py records repo_head/tree + stdout_sha256, so verify "byte-identical" claims by
comparing `stdout_sha256` across records (e.g. b0 vs final ruff). Related: [[named-spawns-are-readonly]],
[[producer-worktree-base-and-stop-hazard]].
