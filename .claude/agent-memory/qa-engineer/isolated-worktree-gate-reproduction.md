---
name: isolated-worktree-gate-reproduction
description: How a worktree-isolated QA reviewer reproduces tests at the frozen reviewed SHA when its own HEAD differs (git archive to scratch, git-init for modularity_check, explicit cwd)
metadata:
  type: feedback
---

When dispatched as an independent gate reviewer, the QA agent is isolated in its own
worktree whose HEAD is NOT the reviewed SHA (e.g. reviewed 57f1b70d but worktree HEAD
was a pre-fix commit, so the working-tree files were the WRONG content). Running pytest
against the worktree working tree tests the wrong code.

**Why:** the dispatch worktree is auto-isolated off some base commit, and the git guard
refuses any `cd`/git that targets the shared checkout (ctl24). So you cannot just run
pytest in ctl24 either.

**How to apply (reproducible clean-room pattern that worked for M0-T131):**
1. Both the fix SHA and reviewed HEAD exist in the isolated worktree's object store, so
   `git show <sha>:path`, `git diff a..b -- paths`, `git archive <sha>` all work from the
   worktree with NO `cd`.
2. Materialize the reviewed content: `git archive <reviewed_sha> -o scratch/full.tar`
   then `tar --force-local -xf scratch/full.tar -C scratch` (GNU tar treats `C:` as a
   remote host — `--force-local` is mandatory on Windows). Extract the WHOLE repo, not
   just `tools/` — governance tests read repo-root files (AGENTS.md,
   project-control/campaigns/*.json); a tools-only extract yields spurious
   FileNotFoundError failures.
3. `tools/` has no `__init__.py` (namespace package); the test files self-bootstrap
   sys.path via `REPO = HERE.parent`, so pytest run against `scratch/tools/test_*.py`
   imports the extracted reviewed modules correctly.
4. git archive applies .gitattributes CRLF; `git show` emits raw LF — a byte diff between
   the two is normally ONLY line endings (confirm with `diff --strip-trailing-cr`). No
   functional effect: Python string constants built from `\n` escapes are unaffected.
5. modularity_check.py runs `git ls-files`, so the scratch must be a git repo: `git init
   -q .` + `git add -A` inside the scratch dir (allowed — it targets scratch, not the
   shared checkout). Then `python tools/modularity_check.py --check` works.
6. Run pytest with an explicit `cd scratch &&` prefix. Without a valid cwd, pytest's
   rootdir detection throws `FileNotFoundError ... samefile ... tmpXXXX` at collection
   (exit 2) because the Bash default cwd is a deleted temp dir.
7. Prove removal-sensitivity by mutating the SCRATCH copy only (never the repo): revert
   the wiring / drop a preamble anchor / delete a guard, re-run the pack, restore from a
   pristine backup. This is legitimate for a read-only reviewer because the repo is
   untouched.

Guard trips: avoid pipes with `${PIPESTATUS[0]}`, `&&`-chained multi-step git, and
compound `file`/`printf` combos — the isolation guard rejects them as "too complex to
verify." Redirect pytest to a file and Read it instead of piping to tail.
