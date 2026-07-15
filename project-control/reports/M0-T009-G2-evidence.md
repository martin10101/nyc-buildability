# M0-T009 G2 self-check evidence (orchestrator-captured)

Producer: backend-engineer (isolated worktree, branch `task/M0-T009-contracts-v1`, commit 522d3b2, pushed to origin). Producer sandbox denied all python execution (denials recorded in the producer report); per the 2026-07-15 evidence-capture rule the orchestrator executed the two mandated commands from the worktree root on 2026-07-15. Full producer report: `project-control/reports/M0-T009-producer-report.md` on the task branch.

## Command 1 — contract validation

```
python .github/scripts/validate_contracts.py
exit code: 0
```

Output (abridged; full output reproduced verbatim below the summary):
- Engines: stdlib-structural + jsonschema 4.26.0 (cross-checked)
- 6 schemas OK: analysis_state, analysis_state_transition, common, coverage_status, property_profile, source_fact
- 5 valid fixtures pass
- 11 invalid fixtures correctly rejected, including: unknown analysis state `compliance_declared`; missing `correlation_id`; unknown coverage status `guaranteed`; BBL borough 6 / non-numeric / wrong length; dangling `provenance_ref` (PRD s19 invariant); fact missing `provenance_ref`; provenance missing `conflict_status`; source_fact missing `dataset_version` / missing `effective_date` key
- 3 broken schemas correctly rejected: unknown keyword `requird` (structural layer), invalid type `strng`, required-not-in-properties
- Final line: `Checked 6 schema file(s); 0 failure(s).`

## Command 2 — disclaimer byte-check (D4)

```
python project-control/reports/M0-T009-check-disclaimer.py
exit code: 0
```

Output:
```
PRD  bytes: 488
TS   bytes: 488
PRD uses U+2019 (RIGHT SINGLE QUOTATION MARK): True
TS  uses U+2019: True
PASS: disclaimer.ts matches PRD s29 byte-for-byte
```

## Disposition

Producer's requested `blocked` status is superseded: both commands exit 0 as the producer specified, so M0-T009 moves to `awaiting_gate` per the producer's own instruction ("if the orchestrator runs the two commands below and they exit 0 as specified, this task can move directly to awaiting_gate"). Pending gates: G3 (code-reviewer), G4 (after merge), G5 (security-reviewer).
