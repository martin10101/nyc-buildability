# M5-T033 AS-7 — audited graph-guided vs prior-packet comparison (D-066-R003)

Orchestrator-captured 2026-09-17 from the supervisor journal (`transitions` table,
runtime 9aca7075; read-only query). Advisory observation, NOT a controlled benchmark —
limits stated below. No savings claim is made (D-059-R006 discipline).

## Per-unit wall time (journal MIN→MAX committed_at_utc per run_id)

| Unit | Runs | Wall time | Review cycles | Outcome |
|---|---|---|---|---|
| M5-T032 (prior packet, NO graph block; web) | persistent-local-auto 04:00→05:48 (~108 min) + persistent-local-36 05:56→07:09 (~73 min) | **~181 min over two runs** | 4 REVISE rounds total across both | breaker end; orchestrator seam completed the task (ACCEPTED) |
| M5-T033 (graph-guided packet; api) | persistent-local-37 07:42→08:41 | **~59 min in one run** | 4 cycles (3 REVISE + terminal) | breaker end; build complete at post-rework-3, orchestrator seam |

## Context tokens

- Run 37 recorded `provider_session_continuity.context_tokens = 118271` at cycle 4
  (worker claude-opus-4-8). No comparable per-run figure survives for runs auto/36 in the
  journal's current state (the key stores last-value only) — the token half of the
  comparison is therefore one-sided and UNVERIFIABLE for the baseline; recorded as such
  rather than estimated.

## Codex reviewer statement on the graph (D-066-R002)

Recorded in the producer report §6 and the worker's rework-3 commit message: the reviewer
used the packet's navigation block and called it "useful navigation, accuracy unverified
from this packet" — i.e., the graph aided blast-radius orientation but the reviewer
(correctly) did not treat it as verified truth.

## Limits (why this is advisory only)

1. Different task types (web feature build vs api diagnosis+tests) and different defect
   surfaces — wall times are not like-for-like.
2. Both units ended via the same `consecutive_revision_loops` breaker at 4; review-round
   count, not navigation, dominated both durations.
3. M5-T032's first run includes launch/recovery overhead from the relaunch drill.
4. One observation per arm; no variance estimate.

Honest reading: the graph-guided unit finished its build in a single run at roughly a
third of the prior unit's total wall time, and the reviewer found the navigation useful —
directionally positive for D-066, proving nothing on its own.
