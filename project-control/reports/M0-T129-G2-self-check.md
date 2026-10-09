# M0-T129 - G2 self-check record (orchestrator-recorded; never satisfies an independent gate)

Recorded 2026-08-31. The producer IS the orchestrator (`orchestrator-recert-runner`), so G2
documents the orchestrator's recert execution self-checks; the independent weight lives in
G3/G4 (PASS + delta-ack CONFIRMED at the corrected text) and the DCV (7/7 SATISFIED).

| Self-check | Orchestrator execution | Independent corroboration |
|---|---|---|
| Golden pack | 42/42 in 51.32s | G3 41.27s, G4 41.42s, DCV 46.15s - four sub-minute runs |
| Whole suite | 3,035 / 2 / 0 (666.93s) | Producer + G4 measured identical; chain 2990+35+10 confirmed by G4/DCV |
| Manifest / verify / doctor | 125 files 841ed11c bound; verify PASS; doctor PASS ACL PROTECTED | G4 re-ran verify-controller read-only (EXIT 0); reviewers correctly left record-manifest/doctor orchestrator-captured |
| CLI identity | d6f6c29a supervisor-native; codex 0.146.0 | G3 reproduced exactly |
| Command validation (R408) | both commands parse-validated pre-presentation | Producer + G3 + G4 + DCV = four independent validations |
| Preservation | 53/22/0 at G0 and report time; wt-m0t107 clean | G3 + DCV live re-checks identical; G4 preserved-copy corroboration |
| ASCII | both reports 0 non-ASCII | G4 + delta-ack re-verified after the fixes |

Honesty notes: the G3 round caught a fact-6 mechanism citation slip (select_next_packet named
as live when the wired mechanism is the driver's inline eligibility iteration) - the exact
Amendment-24 accuracy class, in the orchestrator's own authored report; the three report-only
fixes were applied and BOTH reviewers re-confirmed at the corrected text (delta-acks captured).
The gate chain preserves the pre-fix G4 review and the correction history in full.

Verdict recorded: PASS (self-check class; administrative record by the orchestrator).
