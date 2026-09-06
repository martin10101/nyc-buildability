# D-032 Amendment 3 — monitor to breaker, then converge (owner, 2026-09-06)

- **Captured:** 2026-09-06 (UTC), session_01WBbzN5Rx17CBSjky5uKmnY, channel: owner terminal prompt.
- **Amends:** source-001.md (the live-activation campaign; run persistent-local-04 in flight).
- **Base identity at capture:** worktree `ctl24`, branch `candidate/D-024-mrl-option-b`,
  HEAD `f3139c5b9c36fc779175b753c3a84de1db3ada6c`.

## Verbatim owner text

```
continue monitoring until the breaker trips, then run the convergence
```

## Capture context (recorder's note, not owner text)

Given in direct reply to the orchestrator's report on closure run **persistent-local-04**
(task M2-T020): three consecutive live gpt-6-astra REVISE verdicts (audit seq 53, 66, 78) all
demanding supervisor-collected, digest-bound contents of the untracked deliverables
(`services/api/app/spatial/live_provider.py`, `services/api/tests/spatial/test_live_provider.py`,
`project-control/reports/M2-T020-producer-report.md`), the M2-T020 task contract, and
broker-captured pytest transcripts — evidence the certified controller's packet builder
(`tools/agent_supervisor/loop.py::_collect` → `evidence.build_packet`, certified subtree
`520a4904fffe4da70c4c967dbfe5727f443b715e`) is not wired to collect. "The breaker" =
the run's durable `consecutive_revision_loops=4` circuit breaker. "The convergence" =
the mandatory `/deficit-convergence` method (CLAUDE.md rule 18) applied to this
packet-collection gap.
