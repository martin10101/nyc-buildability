---
name: frozen-tree-review-method
description: How to review a pinned-SHA supervisor task read-only via git archive, and which test failures are expected export artifacts vs real regressions
metadata:
  type: feedback
---

Reviewing an agent_supervisor unit (D-024 M0-T10x) at a frozen SHA when the worktree lags:
export read-only with `git archive <deliverable_sha> | tar -x -C <tmp>` (the object store in the
worktree has the frozen commits even when the branch is elsewhere). Run tests with
`python -m pytest` from the export root — `tools` resolves as a PEP 420 namespace package (no
`tools/__init__.py`; cwd on sys.path via `python -m`).

**Why:** the export has NO `.git`, so a handful of `RealRepo*` smoke tests fail with
`not_a_repo` / `git ls-files failed (128)` — these are EXPECTED export artifacts, not regressions.
Seen at M0-T106: full `tools/` suite = 2830 passed / 5 failed / 5 skipped; all 5 failures were
`test_repo_fingerprint`, `test_modularity_check::RealRepoTests`, `test_repo_index_baseline/incremental`,
`test_context_integration::Proof7` — every one a `.git`-absence failure, none in agent_supervisor.

**How to apply:** when the full supervisor suite shows a few failures, grep the failure reasons for
`not_a_repo`/`git ls-files` before flagging a regression. Also: whole-REPO collection on the
sandbox's Python 3.11 shows ~15 PEP 695 SyntaxError collection errors in `services/api` (repo
targets 3.12) — pre-existing/out-of-scope for any tools/ unit. Producers labeling a "whole-tree
collect" number usually mean the `tools/` subtree (e.g. M0-T106 "2,720" = tools/ 2,840 minus the
120-test `test_directive_compliance.py`), not the whole repo. `modularity_check` needs `.git`
too — verify file SLOC against thresholds warn=600/justify=750/hard=1000 manually instead.

Worktree-isolation guard: if a compound extraction command is REFUSED, RESPECT the refusal —
do not engineer a command split to slip past a safety guard (that is a guard-evasion pattern and
is prohibited; the orchestrator removed an earlier note here that did exactly that). Legitimate
read-only alternatives that need no evasion: read individual files with `git show <sha>:<path>`,
run the specific test file you need directly, or ask the orchestrator to capture the evidence.
If a guard is genuinely a false positive for a legitimate read-only action, surface it to the
owner rather than working around it.
