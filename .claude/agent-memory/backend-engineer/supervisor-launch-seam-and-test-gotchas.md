---
name: supervisor-launch-seam-and-test-gotchas
description: agent_supervisor launch/resume chokepoint facts + non-obvious test/lint/fixture gotchas learned building the M0-T123 launch seam
metadata:
  type: project
---

Learned building the M0-T123 launch-seam (D-024 Amendment 19). Stable facts about
`tools/agent_supervisor/**` and its test harness.

**Provider-contact chokepoint.** The ONLY worker-dispatch `subprocess.Popen` is in
`claude_runner.ClaudeRunner.run_unit`. Rotation/resume never launch separately — the loop rebinds
`self.runner` (`with_model`/`with_resume`) and the next `run_cycle` dispatches through `run_unit`
(loop.py ~1487). `probe_model_launch` also builds argv+Popens but is a non-worker availability probe
(no permission broker, no resume, no checkpoint contract). So a single guard before that one Popen
covers every worker launch.

**Rotation ceiling was reactive-only (the M0-T123 defect).** `rotation_pending` is a durable journal
flag set post-unit by `_flag_rotation_if_needed` (loop.py, compares `run_result.context_tokens` >=
400k) and acted on ONLY between cycles (loop.py ~2587) or on the FORWARD_PROMPT resume. The ordinary
`IDLE→PREFLIGHT→first-cycle` `run()` path had no pre-first-dispatch ceiling seam, so a start after a
halt that had crossed 400k dispatched a unit on the over-ceiling session. The 400k ceiling lives in
`rotation.RotationThresholds.context_rotation_threshold` — import it, never re-hardcode.

**Worktree-isolation guards must compare against the PACKET's declared worktree, not "worktree !=
checkout".** Golden-run + cli-start tests (`test_agent_supervisor_golden_run.py`,
`test_agent_supervisor_loop.py` CliStartTests) run controller and worker in the SAME tmp checkout and
the packet declares `worktree == str(checkout)` (single-checkout mode). A guard that refuses
`worktree == checkout` breaks ~9 of them. The real defect signal is `cwd != packet.worktree` (packet
declared `wt-m0t107`, launch bound to `…/ctl24`). `cli._run_loop` gets `--worktree` (defaults to
`repo`→`checkout`) and the packet's own `worktree` field separately.

**Committed-fixture hygiene is enforced.** `test_agent_supervisor_subagent_telemetry.py::
test_all_committed_fixtures_free_of_home_prefixes` fails any `tools/agent_supervisor/fixtures/*.json`
containing `C:\Users\<name>` / `/home/` / `/Users/` prefixes. Mask home prefixes to `[HOME]` (and
project slugs `C--Users-MLFLL-…` too); keep only the load-bearing path tail.

**CI ruff only lints `services/api`** (`.github/workflows/ci.yml` job `api`, `working-directory:
services/api`, `ruff check .`), NOT `tools/`. So pre-existing `tools/` F401s (e.g. `loop.py`
owner_touch imports) are not a CI gate — but keep NEW files clean anyway. Local ruff is 0.13.0
matching CI.

See also [[env-producer-sandbox-no-exec]] (this session had full python+read access to the live
runtime dir and `~/.claude/projects` transcripts, read-only), [[socrata-pluto-gotchas]].
