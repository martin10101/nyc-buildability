# M0-T127 - G2 self-check record (orchestrator-recorded; never satisfies an independent gate)

Recorded 2026-08-31. The producer for this task IS the orchestrator (`orchestrator-recert-runner`
per the M0-T119 precedent), so G2 documents the orchestrator's own recert execution self-checks,
and the independent verdicts carry the weight: G3 and G4 each reproduced the load-bearing numbers
as PRIMARY evidence (both PASS with zero blocking findings), and the DCV verifies the 22-row set.

| Self-check | Orchestrator execution | Independent corroboration |
|---|---|---|
| Golden pack 42/42 | canonical single-process 52.20s + 5-shard corroboration + probe | G3 reproduced 42/42 in 14.81s; G4 in 16.16s |
| Whole suite | 2,990 passed / 2 skipped / 0 failed (449.11s) | G4 reproduced 2,990/2/0 (220.63s) + collection reconciliations |
| Timing-anomaly resolution | recorded from T119 precedent + own measurements | G4 (the original outlier's author) formally accepts; four datapoints cluster sub-minute |
| Manifest / verify-controller / doctor | 125 files a43f133b bound; verified; doctor overall PASS ACL PROTECTED | G4 independently re-ran verify-controller (EXIT 0); doctor readback internally consistent (reviewers correctly declined to open the live journal) |
| CLI identity | supervisor-native d6f6c29a... reproduced; codex 0.146.0 | G3 reproduced the exact digest/size/kind |
| Preservation before/after | 53/22/0, wt-m0t107 clean 796e18f | G3 verified incl. runtime mtimes untouched; G4 verified the preserved copies + worktree |
| Commissioning commands | dry-run validated pre-presentation (both OK) | G3 and G4 each re-validated independently; neither executed them |
| Tooling | modularity 0 failures; tooth 12/0; validator EXIT=0; CI 20/20 | G3/G4 reproduced modularity + tooth; CI conclusion API-read |

Honesty notes: the whole-suite "excl. golden" mislabel from the M0-T126 era was caught by the
orchestrator at recert, root-caused and exactly reconciled by G4 (true excl-golden = 2,948);
the orchestrator's initial Get-FileHash CLI check used the wrong digest scheme and was corrected
to the supervisor-native scheme before any drift conclusion was drawn; the golden sharding plan
was executed transparently and then superseded by the canonical single-process run once the
timing anomaly resolved.

Verdict recorded: PASS (self-check class; administrative record by the orchestrator).
