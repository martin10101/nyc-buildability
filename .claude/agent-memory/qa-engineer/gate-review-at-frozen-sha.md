---
name: gate-review-at-frozen-sha
description: How to run an independent G4 gate at a frozen deliverable SHA when the reviewer worktree lags that SHA (read-only, no checkout)
metadata:
  type: feedback
---

When dispatched as a read-only gate reviewer, the isolated worktree HEAD often does NOT match the
frozen deliverable/live-HEAD SHA the packet pins (it lags at an older accepted merge). You cannot
`git checkout` (mutates worktree state) and must not edit repo files.

**Rule:** export the frozen tree into the OS temp dir and run everything there.

**Why:** the deliverable files literally do not exist in the stale worktree; running tests against
the worktree tests the wrong code (or ImportErrors). `git archive <SHA> | tar -x -C <temp>` is a pure
read (no repo-state mutation) and reconstructs the exact reviewed tree.

**How to apply:**
- Export: `git archive --format=tar <live-HEAD-SHA> | tar -x -C <tempdir>` (from the worktree; object DB has the SHA even if not checked out).
- This repo has NO pytest.ini/pyproject/conftest and `tools/` is a namespace package (no `__init__.py`).
  So imports like `from tools.agent_supervisor import ...` need the export ROOT as cwd. Run
  `cd <tempdir> && python -m pytest tools/<pack>.py` — `python -m` prepends cwd to sys.path. Do NOT
  run from the worktree cwd or the stale worktree `tools/` shadows the import.
- Content-identity proof: `git show <SHA>:<path> | tr -d '\r' | sha256sum` vs `tr -d '\r' < <tempfile> | sha256sum`.
  The archive extracts CRLF on Windows while `git show` emits LF, so ALWAYS CRLF-normalize before comparing
  or the hashes differ spuriously (content is identical).
- Mutation-proof checks: mutate the TEMP copy (outside the repo), run the named test, restore from a `.bak`.
  Never touch repo files.
- `tools/modularity_check.py --check` shells out to `git ls-files`, so it FAILS in the non-git temp export
  (exit 128) — verify the modularity claim by direct file-size/responsibility inspection instead.
- Skip hygiene: live rows gate on `shutil.which("claude")`; claude 2.1.247 IS installed on the owner box
  (cp1252 locale, PYTHONUTF8 unset), so version-drift live tooths actually RUN (not skip) here.
