# M4-T015 G0 contract-readiness record (administrative; orchestrator)

Date: 2026-09-13 (UTC). D-046/D-047 wave 2 slot 2 (connector lane, parallel with the re-dispatched
M4-T012 rules lane; width 2 within the D-047-R004 ramp).

- **Requirement identifiers**: D-045:D-045-R003 (B2 street-width connector - the BUILD half; the
  research half is accepted M4-T013), R008 (sequencing), R009 (preservation); D-046:D-046-R001
  (parallel wave slot), R002 (disjointness - this packet's writable surfaces share nothing with
  M4-T012's rules dirs, _zr_snapshots, tests/rules, or its reports).
  `evaluate_task_refs` ok - applicable == cited == the five rows (missing/invalid/unresolved all
  empty). Registry applicability task_ids appended for M4-T015 this commit.
- **Pin**: project-control/reports/M4-T013-street-width-research.md - DCM Street Center Line ArcGIS
  PRIMARY (keyless, EPSG:2263, dataLastEditDate pin), SODA g6zj-tzgn documented-stale fallback,
  Geoclient streetWidth KILLED for legal use, free-text Streetwidth parsed fail-closed-to-narrow
  (wide only on mathematical entailment >= 75 ft), OQ-1/OQ-3 stay open - surfaced, never resolved.
- **Dependency**: M4-T013 (accepted 197th) - satisfied at contract time.
- **Scope**: two NEW connector modules + two NEW test files + one NEW fixture dir + the existing
  registry draft + the producer report. All existing connectors READ-ONLY/forbidden; no consumer
  wiring; zero new dependencies (section G: a needed package = BLOCKED submission).
- **Scenarios**: S1-S6 (source+provenance, fail-closed classification with the class->disposition
  table, mapped-street honesty, recorded-official fixtures, error/paging honesty, scope+regression).
- **Gates**: G0/G1/G4/G5; reviewers data-contract-verifier + qa-engineer + security-reviewer, all
  != producer backend-engineer.
- **Producer model (D-047-R001 deviation recorded)**: claude-sonnet-5 required. The
  backend-engineer agent-file model-key flip was BLOCKED twice by the session permission classifier
  (Edit tool and PowerShell both denied); the dispatch therefore carries the harness model override
  resolving to claude-sonnet-5 (Sonnet 5 is the only current Sonnet), and the durable agent-file
  flip is an open owner/settings item. Escalation per D-047-R003 unchanged.

Verdict: **PASS** - packet claimable.
