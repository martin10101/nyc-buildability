# M0-T125 — G2 producer self-check (recorded by the orchestrator from the producer's return)

The survey producer's return carried its own self-checks, recorded here at the evidence
identity `915d73d` (return captured verbatim in the two deliverables + evidence map):

| Check | Result |
|---|---|
| Scope honored | PASS — read-only analysis; zero file writes by the spawn (write-guard denied by design); content returned via the agent channel; only the two allowed report files were created (by orchestrator capture) |
| Preservation honored | PASS — sqlite journal never opened; no supervisor subcommand executed (parser introspected by pure import); preserved artifacts read as plain files only |
| Deliverable completeness self-check | PASS — call graph A.1–A.5 spans start→recovery; all 94 transitions inventoried with per-edge surfaces; all CLI verbs enumerated; every owner-presented command reconciled; 17 defects across all ten mandated classes; six seeds dispositioned; checked-and-clean list records absence-of-findings as evidence |
| Honesty rules | PASS — every claim cited (file:line or artifact); UNVERIFIED items marked with reasons; the register REFUTED one of the orchestrator's own seeds (seed c) rather than confirming it — evidence of independent judgment |
| Size bounds | PASS — file 1 ≈ 272 lines, file 2 ≈ 256 lines (under the ~1200-line bound) |

Orchestrator note: the self-check stands on the producer's return; its material claims were
then independently verified by G3 (all 17 confirmed), G4 (19/19 live-evidence verified),
and the DCV (7/7 rows PASS) — the self-check is corroborated, not load-bearing alone.
