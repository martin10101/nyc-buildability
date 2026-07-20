# M2-T008 — G0 Definition-of-Ready record

- **Task:** M2-T008 — ZTLDB lot-level zoning connector (SODA fdkv-4t4z)
- **Recorded by:** orchestrator (G0 is administrative per the hardened CLI gate classes)
- **Date:** 2026-07-20
- **Owner authorization:** owner approval 2026-07-17 (NEXT CONNECTOR WAVE), strict order M2-T007 → M2-T008 → M2-T009. M2-T007 was accepted (33rd, CP-0028) before this dispatch, satisfying the owner's serialization requirement.

## Owner-required pre-dispatch revalidation (against main `81da9c3`)

- Dependencies all accepted: M2-T007 (accepted this session, CP-0028), M2-T004, M1-T003, M1-T009.
- Cross-check inputs now exist on main: `services/api/tests/fixtures/zoning_features/**` (32 fixtures + MANIFEST) and the accepted PLUTO fixtures.
- No contract drift: contract 1.3.0 stands; the packet's STOP condition on any version bump remains valid (M2-T010 precondition unchanged).
- No file-scope drift: the packet's allowed paths do not overlap any in-flight work (0 claimed tasks).
- M2-T007 review carry-forwards folded into the dispatch brief (not packet changes):
  1. G5 O4 — widen the fixture/manifest secret-scan needle set (add bearer/password/secret needles).
  2. G3/G4 O6 — reuse the two-staleness test quartet pattern (fresh-old-source, cache-hit, LKG, both client paths).
  3. G4 O1 — do NOT duplicate the hardened transport: reuse `pluto_soda` public exports read-only exactly as M2-T007 did; the shared-transport extraction refactor remains a documented maintenance consideration to be contracted separately (not fragmented into this task, per the owner's consolidation instruction).
  4. G5 O1 — correlation_id shape-bounding stays a future HTTP-boundary concern; internal-caller posture unchanged.

## G0 checklist (docs/GATES_AND_CHECKPOINTS.md)

1. **Objective unambiguous** — PASS. Packet objective enumerates the six owner safeguards (schema authority with 16-column inventory, query safety/SoQL-injection prevention, pagination and ordering, domain semantics incl. split-lot ordering + slash-tie + PARK caveat + open ZD1, source-freshness guard separate from transport staleness, PLUTO + M2-T007 cross-check as typed conflicts).
2. **Dependencies accepted** — PASS (see revalidation above); CI is fixture-driven, no mocks needed.
3. **File scope exclusive** — PASS. New connector + new fixture dir `services/api/tests/fixtures/ztldb/` + bounded profile cross-check integration; no other task active. Existing connectors read-only by packet rule.
4. **Inputs and outputs defined** — PASS (packet `inputs`/`outputs`).
5. **Acceptance scenarios exist** — PASS. ZT-S1..ZT-S17 in the packet, covering the research §6 ZT-F1..F12 pack plus all owner negative cases (blank omitted key, explicit null, split lot, slash tie, PARK, open ZD1 value, stale source, fresh-retrieval-of-stale-source, PLUTO disagreement, M2-T007 disagreement, empty result, malformed record, metadata drift, rate limit, timeout, budget exhaustion, deterministic digests).
6. **Source documentation available** — PASS. G1-corrected research doc (ZTLDB sections), official data-dictionary findings, registry draft `docs/research/source-registry-drafts/ztldb.json`.
7. **Credentials** — PASS. None required: SODA works tokenless; the optional `SOCRATA_APP_TOKEN` is environment-sourced, never committed, never logged (M2-T004 discipline). No blocker.
8. **Required gates assigned** — PASS. G0/G1/G2/G3/G4; roster data-contract-verifier (G1) + code-reviewer (G3/G4); producer backend-engineer (∉ roster). No G5: no new outbound-request pattern — the SODA origin-allowlist/token discipline was G5-reviewed at the framework level (M1-T005) and follows the M2-T004-reviewed pluto pattern; the M2-T007 G5 review covered the new ArcGIS surface. If the producer's design introduces any new security surface beyond the pluto SODA pattern, the orchestrator adds a G5 review before acceptance.
9. **Execution location and disk usage** — PASS. Owner-PC thin-client checkout (source + KB-scale JSON fixtures only; ≥4 GB free preserved); full CI in GitHub Actions; producer fixture capture via bounded KB-scale SODA GETs with disclosed timestamps; no dataset downloads (857k-row full sync explicitly out of scope).
10. **Cleanup and durable routing** — PASS. Durable artifacts are git-committed fixtures/reports only; no persistence (B-001 stands).

## Verdict

**G0 PASS** — ready; claim by backend-engineer follows in this control PR; worktree `.claude/worktrees/M2-T008`, branch `task/M2-T008-ztldb-connector` created from main after merge.
