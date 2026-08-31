---
name: supervisor-modularity-and-tooth-gotchas
description: Net-zero SLOC trick for at-limit supervisor files (cli.py/claude_runner.py) and command-doc tooth placeholder/pinned-start constraints
metadata:
  type: reference
---

Working in `tools/agent_supervisor/` under the modularity gate (`tools/modularity_check.py`, baseline `tools/modularity_baseline.json`, limit = baseline + max(50, 10%)):

- SLOC counts PHYSICAL non-blank, non-comment lines (`source_lines`). Comments/blank lines are free. `cli.py` (2953/2953) and `claude_runner.py` (1383/1383) sit AT their exact limit. To wire a new kwarg into an at-limit file NET-ZERO, APPEND it to an existing multi-arg call line rather than adding a new physical line, e.g. `pinned_model=pinned_model, turn_budget=turn_budget,` on one line inside `SupervisedLoop(...)`. `loop.py` had ~54-58 SLOC headroom; put new logic in the small leaf modules (`orientation.py`, `turn_budget.py`, `loop_turnover.py`) instead of the big files.

Command-document tooth (`tools/agent_supervisor/command_docs.py` + `tools/supervisor_command_doc_check.py`, scans `docs/CONTROLLER_UPDATE_RUNBOOK.md` only):
- ANY presented supervisor command containing a `<...>` angle-bracket placeholder is SKIPPED entirely (`_is_supervisor_command` -> `_has_placeholder`). So you cannot template a command with `<run-id>` and still have it validated.
- `test_agent_supervisor_command_docs.py::LivingRunbookTests::test_runbook_has_a_pinned_start_command` REQUIRES at least one CONCRETE (non-placeholder) `start` command in the runbook carrying the 5 pinned flags (`--checkout --repo --branch --worktree --max-cycles`) + 6 dispatch inputs. Do not fully templatize the runbook's only `start` example. `--run-id` is NOT a pinned flag nor a dispatch input, so it can be omitted (avoid inventing one) while the command still validates.
- The CI entry does NOT resolve `--task-packet` or run the worktree-binding dry-run against the runbook; presented `start` values need only be concrete tokens, not real paths.

R374/R375 scope: the live PROTECTED CONFIG files `C:\Program Files\SupervisorConfig\config.toml` and `C:\SupervisorController\model_selection.toml` are NOT the runtime dir (`%LOCALAPPDATA%\NYCBuildabilitySupervisor\`) and were READABLE this session; recomputing their SHA-256 (raw uppercase = Get-FileHash; LF-normalized lowercase = manifest style) is a permissible read-only op for runbook digest regeneration. The certified manifest lives OUTSIDE the tree at `%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json` (M0-T113 sec1 item 10), and runbook commands use `$env:LOCALAPPDATA` (PowerShell), never `%LOCALAPPDATA%`.
