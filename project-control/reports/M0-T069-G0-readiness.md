# M0-T069 Unit F G0 readiness — promotion benchmark, runbook, status projection

Recorded by the orchestrator (G0 administrative). Branch
`task/M0-T069-benchmark-runbook`, stacked on accepted Unit E (M0-T068) merged
to main (merge commit cf65b78).

## Checks (6/6 PASS)
1. **Packet complete** — objective, gates G0/G3/G4/G5, reviewers, 13
   allowed_paths, 28 forbidden_paths, 6 acceptance scenarios (AS-1..AS-6),
   named output deliverables, documented_test_commands.
2. **Governing directive active** — D-013 (rows for Unit F: benchmark corpus +
   comparison method R054/R055/R056, honest reporting R057/R012/R053,
   promotion evidence R059, decision discipline R060, status projection
   R061/R062/R063, rollback documentation R071, fail closed R013) + D-001;
   validator run at claim.
3. **Dependencies accepted** — M0-T068 (Unit E) accepted and merged to main
   (PR #235, cf65b78); ALL prior units A1/A2/B/C/D/E are accepted and on
   main, so the benchmark compares the complete accepted pipeline; every
   consumed module is listed forbidden (import-only).
4. **Scope resolvable** — the reference side reuses the accepted A1 baseline
   harness (`capture_baseline`, UNMODIFIED full builder — R055's frozen
   reference discipline); the new side is the accepted A2
   `build_incremental`; both run at the SAME SHA over the SAME deterministic
   fixture snapshots, which removes the implementation-SHA confound (R056
   method, stated in the report). R059's evidence list maps to executable
   cases already proven unit-wise by the accepted A2/D suites and is
   re-proven end-to-end here. The status projection reads only authoritative
   control-plane files + git (R061) and stamps generating SHA + Unit C index
   digests.
5. **Modularity path** — two new focused modules + two test files, each well
   under the 600-SLOC warn line; no existing module grows.
6. **No concurrent overlap** — Unit F creates only new files plus its own
   reports and one new doc; no other open task touches these paths.

Conclusion: backlog → ready for claim by the orchestrator.
