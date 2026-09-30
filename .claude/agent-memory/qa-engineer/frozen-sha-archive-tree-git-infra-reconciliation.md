---
name: frozen-sha-archive-tree-git-infra-reconciliation
description: Reviewing a frozen SHA via `git archive | tar -x` gives a no-.git tree; exactly 5 RealRepo tests FAIL + 2 os_acl tests SKIP as env artifacts — reconcile, don't FAIL the gate
metadata:
  type: feedback
---

When a worktree-isolated read-only reviewer cannot `git checkout` the frozen review SHA
(git-write blocked by the guard), the faithful move is to extract the frozen tree into a
TEMP dir with `git archive <sha> | tar -x -C <tmp>`. Verify content identity by comparing
LF-normalized sha256 (`git show <sha>:path | tr -d '\r' | sha256sum` vs the extracted file)
— `git archive` re-applies CRLF on Windows so raw sha differs but LF-normalized matches.

**Why:** the archive tree has NO `.git`. Running the full `tools/` pytest suite there
produces git-infrastructure false-failures that are NOT product defects. On the ctl24
agent-supervisor suite (M0-T099, 2026-08-26) the delta vs a real checkout was exactly:
- 5 FAIL (all "RealRepo" smoke tests needing the ambient checkout to be a git work tree):
  `test_context_integration.py::Proof7EntryPoint.test_entry_point_invokes_integrated_compiler`
  (`--diff-base HEAD` unresolvable), `test_modularity_check.py::RealRepoTests.test_committed_check_passes`
  (`git ls-files` exit 128), `test_repo_fingerprint.py::RealRepoSmoke.test_runs_on_this_repo_and_reconciles`,
  `test_repo_index_baseline.py::RealRepoBaselineSmoke.test_runs_on_this_repo`,
  `test_repo_index_incremental.py::RealRepoSmoke.test_parity_on_this_repo` (all FingerprintError
  "not_a_repo").
- 2 EXTRA skips that would RUN+pass in a git tree: `test_agent_supervisor_os_acl.py:787` and `:1033`
  ("defective blob unreachable: not a git repository").

**How to apply:** archive-tree run of 2468 passed / 5 failed / 5 skipped reconciles EXACTLY to a
git-backed 2475 passed / 3 skipped / 0 failed: +5 (RealRepo failures pass) +2 (os_acl skips run)
= 2475 passed; 5−2 = 3 skipped; 5−5 = 0 failed; total 2478 both ways. Confirm each failure's
traceback names a git/.git/rev-parse/ls-files cause AND the test id is OUTSIDE the task's diff,
then classify ADVISORY (reviewer-env), not blocking. The 3 real env-conditional skips
(process.py:448 POSIX-only, policy.py:449 symlink WinError 1314, repo_fingerprint.py:148 symlinks
unavailable) appear in BOTH environments and have compensating coverage (Windows Job Objects test;
`mklink /J` junction-escape test). Targeted packs + mutation teeth run fine in the archive tree
(they don't touch `.git`). `git-dependent` RealRepo packs are also SLOW on Windows (temp-repo
subprocess spawns) — the full suite took ~17 min; budget for it or background it.
