---
name: reviewing-shared-checkout-from-isolated-worktree
description: How a G4 reviewer in an isolated worktree verifies a material commit that lives in the shared ctl24 checkout
metadata:
  type: feedback
---

When dispatched as a read-only gate reviewer while isolated in a `.claude/worktrees/<id>`
worktree, the material files under review usually live in the SHARED checkout
(`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`), and the isolated worktree HEAD is often an
old base that does NOT contain the material commit.

**Why:** the harness worktree-isolation guard refuses any `git` command that targets the
shared checkout, and refuses "too complex" bash (heredocs, multi-`&&` pipelines, inline
`python - <<PY`). So git-diff-against-the-frozen-SHA is not available to you.

**How to apply:**
- The Read tool reads shared-checkout absolute paths fine. Plain `ls`/`python <scriptfile>`
  referencing ctl24 absolute paths also run.
- Confirm you are at the frozen content identity by RECOMPUTING the producer report's
  LF-normalized `sha256[:16]` per file (write a script to the scratchpad, run
  `python <scratchpad>\digests.py`) and matching all of them. Byte match == you are
  reviewing the frozen reviewed content even though you cannot `git checkout` it.
- Regression suites DO run: `cd <ctl24>/services/api && python -m pytest tests/rules -q`
  (from services/api cwd — repo-root collection fails `No module named app`). ruff + full
  suites reproduce locally offline.
- To exercise a branch with a standalone probe script, set
  `PYTHONPATH=<ctl24>/services/api` (pytest adds it via conftest; a bare `python script.py`
  does not). Put temp rulesets in the scratchpad, never in ctl24.
- Never `git`, never edit ctl24, never run the control CLI — return the report + verdict.
