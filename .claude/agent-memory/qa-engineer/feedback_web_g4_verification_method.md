---
name: web-g4-verification-method
description: Reusable method for an independent G4 QA gate on a thin-client, CI-only web task (apps/web) when the reviewer worktree is pinned to an unrelated base commit
metadata:
  type: feedback
---

Running an independent G4 on a web task (apps/web) here: web suites are NOT locally
executable (no node_modules, npm prohibited), and the reviewer's isolated worktree is
frequently pinned to an UNRELATED base (e.g. reviewing M5-T018 while my worktree HEAD was
an old M0-T077 merge). So the on-disk working tree is the wrong code — do NOT read the live
files or run repo-tree tools directly against your worktree.

**Why:** the git-isolation guard refuses git ops that target the shared checkout, and the
shared checkout (ctl24) may have advanced PAST the frozen SHA, so neither is safe to trust
for a frozen-identity review.

**How to apply — the method that worked:**
1. The frozen commits are reachable in the worktree object store (shared with the pack repo).
   Verify with `git cat-file -t <sha>`. Extract every artifact and source file at the frozen
   code SHA with `git show <sha>:path > scratchpad/...` (simple single commands — the guard
   rejects compound/redirect-heavy git lines).
2. Frozen-identity integrity: `git diff --stat <report-commit> <HEAD>` must show ONLY
   control-plane files (reports, evidence maps, state.json, task json) — no production
   allowed_paths. Then `git diff <frozen-code-sha> <CI-head-sha> -- <prod paths>` must be
   EMPTY (CI tested byte-identical code to what you review).
3. Red->green soundness: `git diff --stat <red-head> <green-head> -- apps/web` must equal
   exactly the task's production+test files, and `git diff --stat <red> <green>
   ':(exclude)apps/web' ':(exclude)project-control'` must be empty (no confounding
   packages/services change). That proves the web-side delta is only this task's material.
4. "No weakening" (S5): confirm previously-red suites are NOT in the producer diff at all
   (untouched), and that any shared test-fixture file edit is purely additive (`git diff ...
   -- fixtures.ts | grep '^-'` empty). The fix is then provably the validator change alone.
5. Modularity: you can't run `--check` against the frozen tree (worktree is the wrong base;
   reconstructing the whole tree is disproportionate). Instead import the FROZEN
   tools/modularity_check.py and call its own `source_lines()` / `top_level_symbols()` on the
   extracted files, then apply run_check's real threshold logic by reading it: WARN_SLOC=600,
   HARD_SLOC=1000, files not in modularity_baseline.json only fail if >HARD or warn if >WARN;
   material growth (max(50,10%)) only FAILS grandfathered files that ARE in the baseline.
6. Validator negative-test validity: check the emitted problem-string format in
   scenario-contract-checks.ts (`Problems.add` pushes `"{path}: {message}"`), so
   `startsWith("path:")` assertions are only valid if the check actually emits that path.
