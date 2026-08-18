# M0-T068 Unit E G0 readiness — bounded repository-intelligence views

Recorded by the orchestrator (G0 administrative). Branch
`task/M0-T068-repo-views`, stacked on accepted Unit D (M0-T067) merged to main
(merge commit 40b530f).

## Checks (6/6 PASS)
1. **Packet complete** — objective, gates G0/G3/G4/G5, reviewers, 8
   allowed_paths, 26 forbidden_paths, 6 acceptance scenarios (AS-1..AS-6),
   named output deliverables, documented_test_commands.
2. **Governing directive active** — D-013 (rows for Unit E: coverage modes
   R023, coverage-record minimum fields R024, ONE-compiler feeding R039/R042,
   deterministic/no-LLM R009, honest kinds R018, fail closed R013, nullable
   honesty R051) + D-001; validator run at claim.
3. **Dependencies accepted** — M0-T067 (Unit D) accepted and merged to main
   (PR #234, 40b530f); all consumed layers (A1/A2 index + telemetry, Unit C
   resolver, Unit D store) are accepted, on main, and listed forbidden
   (import-only).
4. **Scope resolvable** — Stage-0 inspection confirmed the A2 telemetry
   already carries every R024 field group (census with per-reason
   excluded/failed dicts, change_set classification, versions, fingerprints,
   dirty-state digest, source-manifest/export digests); Unit E adds ONE
   coverage-record builder + five bounded view builders + a typed
   question-retrieval layer and a CLI with a determinism self-proof. No new
   storage, no prompt assembly, no budget (the ONE compiler stays the only
   budget owner, R039).
5. **Modularity path** — two new focused modules (view builders; query+CLI)
   each well under the 600-SLOC warn line; no existing module grows.
6. **No concurrent overlap** — Unit E creates only new files plus its own
   reports and one new doc; no other open task touches these paths.

Conclusion: backlog → ready for claim by the orchestrator.
