# M0-T124 — G2 self-check (orchestrator)

Recorded 2026-08-30 at control head `3cb9e31`. VERDICT: **PASS.** As with M0-T122, the
orchestrator is the producer of record; every claim below is an executed-command output
from this session, and all judgment defers to the independent G3/G4/G5 wave + DCV.

| # | Claim | Source (this session) |
|---|---|---|
| 1 | Whole suite 2,889 / 2 / 0 at the final identity | TWO independent full runs: orchestrator (625.3 s, exit 0) + the G4 reviewer's own regression run (attestation on file) |
| 2 | Anchors: material `16e1b3b`, tree `a72a53b8…`, golden `c54fd0d2` (unchanged since T119), launch-seam `1a77b904` | `git log -1 -- tools/agent_supervisor/` + `git rev-parse HEAD:<path>` outputs |
| 3 | CLI digest `d6f6c29a…` exact, size 217,360,032 — no admission event | `executable_identity()` executed live |
| 4 | Drift tooth green | explicit pytest `-k version_matches_catalog` → 1 passed |
| 5 | Manifest 121 files digest `47293127…`, config bound, round-trip verified | `record-manifest` output verbatim |
| 6 | verify-controller PASS; doctor overall PASS (PAUSED_RECOVERY preserved: transitions 18, audit 43 verified; OS-ACL PROTECTED) | both commands executed, outputs quoted |
| 7 | CI 20/20 at `a71bd65`; the certification tip re-runs the same checks | DCV-confirmed check-runs poll |
| 8 | The R347 package presents but does not execute | recert §4 is text; the journal readback (row 6) is unchanged from the post-cycle-2 preserved state — proof nothing ran |
| 9 | Correct recovery surface named | the journal is at PAUSED_RECOVERY (S14 stop), so §4 names `clear-recovery` (the documented PAUSED_RECOVERY→PREFLIGHT exit), NOT `owner-restart` (the HALTED surface) — reviewers should confirm this distinction |
| 10 | R316 consumption + R345 prohibitions restated | recert §3/§4; nothing in either deliverable authorizes or requests a start |

Scope: deliverables exactly the two allowed_paths files; no code changed; resolver 5 rows ok.
