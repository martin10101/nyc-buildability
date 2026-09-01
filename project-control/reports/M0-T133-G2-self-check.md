# M0-T133 — G2 producer self-check (orchestrator-captured)

Producer: `orchestrator-defect-runner`. **G2 self-check; does not satisfy an independent gate.**

## Evidence (single final identity)
| Pack | Result |
|---|---|
| NEW `test_agent_supervisor_checkpoint_envelope.py` (all 8 owner scenarios, removal-sensitive) | **18 passed** |
| NEW `test_agent_supervisor_claude_runner_checkpoint.py` (loop-level: mode scope, git-unreadable, audit) | **6 passed** |
| Affected packs (runner, claude_runner_env, checkpoint_journey, loop, cross_task, recovery, recovery_probes, loop_turnover, start_reentry + the two new files) | **477 passed, 0 failed** |
| Golden certification pack | **42 passed** |
| WHOLE supervisor suite (`tools/test_agent_supervisor_*.py`) | **3,067 passed, 2 skipped, 0 failed** (3,069 collected) |

**Baseline reconciliation (freeze rule):** M0-T132 baseline 3,043 passed / 2 skipped (3,045 collected)
→ +24 new test nodes (18 checkpoint_envelope + 6 claude_runner_checkpoint) = **3,067 passed / 2 skipped**
(3,069 collected). No test removed, no unexplained drift, 0 failed.

## Teeth
- `ruff check` on the touched files (checkpoint_envelope.py, claude_runner.py, loop.py, both new tests): **All checks passed**.
- `modularity_check.py --check`: **exit 0** (the new `checkpoint_envelope.py` and the touched files are not flagged; warns are pre-existing untouched modules).
- `supervisor_command_doc_check.py`: **0 failures** (no CLI command surface changed).

## Removal-sensitivity anchor
`test_journey5_shape_enriched_validates_and_is_removal_sensitive`: the exact journey-5 opus checkpoint
shape (omitting the four git-state fields) FAILS closed on `missing required fields:
['branch','current_sha','starting_sha','worktree']` WITHOUT the enrichment, and validates WITH it —
so a mutant that drops the enrichment call is RED.

## Scope / preservation
- Writes confined to packet `allowed_paths` (new checkpoint_envelope.py; claude_runner.py; loop.py; the
  two new test files; reports). `models.py`/ClaudeCheckpoint schema untouched (the four fields stay
  required; the controller fills them). No `.claude/**`, no control CLIs, no journal writes.
- Journal PAUSED_RECOVERY (transitions 40, audit 104 unchanged), PR #241 OPEN, model pin
  `claude-opus-4-8`, manifest (pre-recert `c228b7ca`), worktrees — all preserved.
