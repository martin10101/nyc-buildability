# M2-T015 — G0 readiness (administrative)

Recorded by the orchestrator 2026-08-08, at main `d2b6e87` (post PR #189).

- **Release authority:** D-010 source-023 (owner SUPERVISED-AUTO activation decision, typed
  2026-08-08; R214–R235 captured, validator green). R219 releases M2-T015 as supervised-auto
  product proof #1; the R133/R143/R153/R167/R196/R213 product-proof holds are discharged by the
  owner-typed decision line. Directive refs to stamp at claim: `D-010:ALL` (resolver-applicable
  set = 29 D-010 rows; no other directive derives a non-empty applicable set for this task).
- **Dependency:** M2-T014 ACCEPTED; its two hard-input outputs exist on main:
  `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md`, `docs/research/survey-document-sources-2026-07.md`.
- **Other inputs present:** `packages/contracts/schemas/v1/` (contract conventions + M2-T010
  generation tooling), `services/api/app/connectors/mappluto_geometry_arcgis.py` (read-only
  domain models for the tax-lot cross-check), `docs/SECRETS_POLICY.md`,
  `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`.
- **Execution mode (R222/R227):** FIRST supervised-auto product proof. The producer of record is
  the supervised worker (claude CLI launched by `tools/agent_supervisor` in `--mode supervised`),
  operating in worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015` on branch
  `task/M2-T015-survey-ingestion`, bounded by the task packet's `allowed_paths`/`forbidden_paths`
  through `TaskAuthority`. Reviews, gates (G0/G1/G2/G3/G4/G5 per packet), approval/park/resume
  protections, fail-closed mechanisms, and the normal PR lifecycle operate as designed. The
  orchestrator operates the supervisor (Tier A, ADR-006); Tier D / Section 20 items still stop
  for the owner.
- **Unit plan (contract-first, per the packet's own split guidance):** unit 1 = acceptance-scenario
  pack + survey-evidence contract (`survey_evidence.schema.json` + `SURVEY_EVIDENCE_CONTRACT.md`)
  + architecture/threat-model documents; implementation and fixture units follow in later
  supervised units. Kept as ONE ledger task executed in bounded supervised units; the supervisor's
  checkpoint reviews keep each increment reviewable. The orchestrator retains G0 discretion to
  split at fresh IDs if a diff becomes unreviewable.
- **Parser dependencies / disk budget:** unit 1 admits NO new dependency. Any later parser
  dependency (PDF/CAD/OCR/image) goes through `/dependency-security` (D-009: advisory-free,
  exact-pinned, 7-day age gate, G5 provenance review) and the low-storage policy (heavy native
  deps may be CI/Render-only). This is the packet's named G0 disk-budget duty; it binds every
  later unit.
- **Holds honored:** B-001 (no production storage provisioning of any kind; the architecture doc
  must design for it and mark it deferred — G3 verifies that honesty); no real client documents
  (synthetic/redacted fixtures only); AI output never promoted to canonical geometry (fail-closed
  doctrine); M0-T047 age gate untouched (R233); LIMITED-AUTO not authorized (R231).
- **Stop conditions (packet, verbatim):** need for production credentials; any real client
  document; any AI output promoted to canonical geometry; any parser that cannot be sandboxed or
  disk-budgeted.

READY.
