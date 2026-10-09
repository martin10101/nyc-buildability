# M0-T148 G2 self-check (orchestrator-recorded, evidence independently re-run)

Frozen candidate: task commit `53d642a1`, merged HEAD `7772626e`
(`candidate/D-024-mrl-option-b`). Producer: backend-engineer (wt-m0t148).
Every number below was re-executed by the orchestrator, not copied from the
producer report.

## Re-run evidence (orchestrator, wt-m0t148 @ 53d642a1)

| Check | Command | Result |
|---|---|---|
| Focused suites | `python -m pytest tools/test_agent_supervisor_reviewer.py tools/test_agent_supervisor_loop.py -q` | **243 passed** in 43.52s |
| Lint | `python -m ruff check` (6 changed files) | All checks passed |
| Modularity | `python tools/modularity_check.py --check` | failures 0 (12 pre-existing warnings) |
| Scope | `git status --porcelain=v1 -uall` | exactly the 6 allowed paths + producer report; nothing else |

## S6 reproduction closure (orchestrator, repaired builder vs. wt-m2t020)

The identical offline reproduction from the convergence record §3, re-run through
the repaired `collect_completeness` + `build_packet` path against the real
M2-T020 worker worktree:

- Sections: `claude_checkpoint, command_transcripts, directive_refs, git,
  project_control, task_packet, untracked_content` (was 4 sections).
- Untracked deliverable content probes: **9/9 present** (was 0/9) for
  live_provider.py, test_live_provider.py, and the producer report.
- Task contract (M2-T020.json title) present: True (was False).
- Both documented pytest commands executed by the collector; transcripts carry
  digest/ok/truncated/value.
- Packet 95,707 bytes — inside DEFAULT_PACKET_BYTES 262,144; no PacketResult.stop.

## Producer-report cross-check

Producer's claimed numbers (117+126=243 focused, ruff clean, modularity 0
failures, adversarial 93 + ephemeral/mrl/repair 190 regression) are consistent
with the re-run where re-run; full-suite regression at the merged HEAD runs
separately and is recorded with the gate wave.

Result: **PASS** (G2 self-check; never a substitute for the independent G3/G5).
