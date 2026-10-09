# M0-T126 — G2 self-check record (orchestrator-recorded; never satisfies an independent gate)

Recorded 2026-08-31. G2 documents the PRODUCER's own self-checks, as returned through the
agent channel across the three verbatim-captured returns, and notes their independent
corroboration; the independent verdicts live in G3/G4 (delta PASS at 2d46fb0) and the DCV
record (18/18 SATISFIED) — this record does not substitute for them.

## Producer self-checks as returned (returns 1-3, captured verbatim)

| Self-check | Producer claim (final, return 3) | Corroboration |
|---|---|---|
| Full supervisor suite excl. golden | 2990 passed, 2 skipped (654.84s), exit 0 | G4 delta reproduced 2990/2 at 2d46fb0 |
| 8 defect packs combined | 401 passed | Orchestrator reproduced 401 at integration; G4 delta reproduced 401 with exact per-pack counts; DCV reproduced 401 |
| Fast golden subset | 27 passed | G4 delta reproduced 27 passed / 15 deselected at 2d46fb0 |
| modularity_check --check | failures 0 (cli 2953/2953, claude_runner 1383/1383 net-zero; loop 2034/2088) | Orchestrator, G3 delta, G4 delta, DCV each reproduced 0 failures |
| Command-doc tooth | exit 0, 12 commands, 0 failures | Orchestrator, G3 delta, G4 delta, DCV each reproduced 12/0 |
| ruff on touched files | All checks passed | Orchestrator reproduced (touched-file set); G4 delta reproduced |
| Reports pure ASCII | 0 non-ASCII bytes in both | G4 delta reproduced 0 non-ASCII bytes |
| Scope containment | all changed files inside allowed_paths | G3 (both passes) verified via git diff --name-only |
| Worktree guard | isolated-worktree check PASSED both producer contexts | Return-1/3 headers; orchestrator confirmed both worktree paths outside the primary checkout |

## Honesty notes on the record

1. The first return DISCLOSED an incomplete correction set (12/17) rather than claiming
   completion; the orchestrator refused it and enforced the R385 continuation. The second
   return's per-pack counts were later found stale by G4 (measured on a transient worktree)
   and were corrected at the remediation identity — the drift is documented in the G4 report,
   the ledger progress history, and observation 4 of the DCV record.
2. The producer's static-analysis rebuttal (three orchestrator-flagged names alleged
   undefined) was independently CONFIRMED correct by G4 (observation O3: valid module-level
   forward references, executed by passing tests).
3. Property-3 softness (the reserved-turn demand cannot hard-block a tool call under the
   --max-turns streaming model) is disclosed by the producer in design-record section 8 and
   return 3 — verified honest by G3 delta, G4 delta (O4), and the DCV (R378 row).

Verdict recorded: PASS (self-check class; administrative record by the orchestrator).
