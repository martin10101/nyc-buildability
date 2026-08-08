# M2-T015 — routing & coverage map (D-010 source-025; R281)

Orchestrator, 2026-08-08, base `1eb29fb`. Built after inspecting (R250): the M2-T015 packet +
acceptance scenarios SB-S1..S9, Unit-1 contract (`survey_evidence.schema.json` + fixtures,
`cabe128`), Unit-2 architecture/threat model (`a059b50`), and Unit-3a code
(`services/api/app/documents/{state,models,errors,limits}.py` + 44 tests, `7802c62`).

## Routing decisions (summary)

- **All eight hardening areas stay INSIDE M2-T015** (R277). None is lawfully forbidden by the
  packet or blocked by an external capability at the code level.
- **No v2 wire contract** (R253/R255/R258/R270): every taxonomy/unit/geometry/correction/promotion
  rule is enforced in **deterministic application validators** over the existing open v1
  `survey_evidence` schema. The v1 wire field stays byte-compatible; unknown/ambiguous inputs
  yield typed `unsupported_*`/`unresolved` results, never silent acceptance. A breaking v2 would
  be an owner-return stop (R284) and is not currently justified.
- **One deferred item — production DEPLOYMENT only, not code:** real parser decoding of untrusted
  bytes requires a verified Landlock+seccomp isolation boundary. That boundary is provable on the
  Linux CI substrate (where the end-to-end real-extraction path runs, satisfying R274) but **not**
  on the owner's Windows host, where the capability probe fails closed and production parsing
  stays DISABLED (R275). Production-substrate enablement on Render is gated by the existing
  **B-001** hold plus the recorded deployment blocker below (a hold, not a hardening-area
  follow-up).

## Remaining bounded M2-T015 units (indicative; split further to fit the supervised-run window, R251)

| Unit | Scope | Primary code paths | Test paths |
|---|---|---|---|
| **3b** | S1 upload gate: MIME/content sniff vs declared extension, size cap, SHA-256 of exact original bytes, safe temp-path (T07/T11) | `services/api/app/documents/gate.py` | `services/api/tests/documents/test_gate.py` |
| **3c** | Storage abstraction + temp-dir CI fake + immutable-originals + abandoned-job scavenging (B-001-honest, no prod binding) | `documents/storage.py`, `documents/scavenge.py` | `test_storage.py`, `test_scavenge.py` |
| **3d** | H1 fact-type taxonomy + H2 normalized-value/unit typing (application validators) | `documents/taxonomy.py`, `documents/units.py` | `test_taxonomy.py`, `test_units.py` |
| **3e** | H3 cross-field geometry validation + H4 correction-history integrity | `documents/geometry_validation.py`, `documents/correction_history.py` | `test_geometry_validation.py`, `test_correction_history.py` |
| **3f** | H5 material-evidence promotion gate wired into `processing→auto_extracted` and professional-confirmation (no AI trigger/veto) | `documents/promotion.py`, `documents/state.py` (integration) | `test_promotion.py` |
| **3g** | SB-S3 deterministic checks: boundary closure, area-vs-stated, segment sums, contradictory dimensions, scale, north/orientation, elevation, address/BBL match | `documents/checks/*.py` | `test_checks.py` |
| **3h** | SB-S4 tax-lot/MapPLUTO typed comparison (read-only domain models; never overrides a licensed survey) | `documents/crosscheck.py` | `test_crosscheck.py` |
| **3i** | SB-S1/S2 extraction pipeline + format routing + parser-isolation capability gate (Landlock/seccomp, fail-closed, parsing disabled where unprovable) + SB-S7 wrong-address routing | `documents/extraction/*.py`, `documents/isolation.py` | `test_extraction.py`, `test_isolation.py` |
| **3j** | H6 adversarial fixture matrix + H7 contract-pipeline reconciliation + `survey_evidence.ts` generation (or lawful-exclusion record) + SB-S8 | `packages/contracts/fixtures/{valid,invalid}/survey_evidence/**`, `packages/contracts/generated/survey_evidence.ts`, `packages/contracts/scripts/**` | contract drift + `test_gen` |
| **3k** | R274 end-to-end clean synthetic supported path through the REAL implementation (in CI where isolation is provable) + SB-S1..S9 coverage matrix (R272) + SB-S9 full CI/regression | `test_e2e_survey_ingestion.py`, `docs/M2-T015-SB-COVERAGE-MATRIX.md` | e2e + full suite |

## Requirement → routing table (R281 columns 1-6)

| Hardening area (reqs) | In M2-T015 / follow-up | Task · unit | Code / test paths | v2-vs-v1 compat | SB coverage |
|---|---|---|---|---|---|
| **H1 fact-type taxonomy** (R252-R255) | In M2-T015 | M2-T015 · 3d | `taxonomy.py` · `test_taxonomy.py` | **v1** app-validation; open wire field unchanged; typed `unsupported_fact_type`; no v2 | SB-S2, SB-S3, SB-S8 |
| **H2 normalized value + unit typing** (R256-R258) | In M2-T015 | M2-T015 · 3d | `units.py` · `test_units.py` | **v1** app-validation; ambiguous/missing/unsupported→typed unresolved; no v2 | SB-S3 |
| **H3 cross-field geometry validation** (R259-R260) | In M2-T015 | M2-T015 · 3e | `geometry_validation.py` · `test_geometry_validation.py` | **v1** app-validation (relationships JSON Schema can't prove) | SB-S3, SB-S5 |
| **H4 correction-history integrity** (R261-R262) | In M2-T015 | M2-T015 · 3e | `correction_history.py` · `test_correction_history.py` | **v1** app-validation; append-only/chain checks | SB-S3 (+ integrity) |
| **H5 material-evidence promotion gate** (R263-R266) | In M2-T015 | M2-T015 · 3f | `promotion.py`, `state.py` · `test_promotion.py` | **v1**; validation_results=[] stays a visible mid-state; promotion gated in app | SB-S3, SB-S5, SB-S7 |
| **H6 adversarial fixture matrix** (R267) | In M2-T015 | M2-T015 · 3j | `fixtures/{valid,invalid}/survey_evidence/**` | **v1** fixtures | SB-S3, SB-S6, SB-S7, SB-S8 |
| **H7 CI / type-gen / regression** (R268-R270) | In M2-T015 | M2-T015 · 3j, 3k | `generated/survey_evidence.ts`, `scripts/**`, drift checks | **v1** schema; generate TS or record lawful exclusion (R270) | SB-S8, SB-S9 |
| **H8 preserve architecture** (R271) | In M2-T015 (cross-cutting invariant) | M2-T015 · all units | all documents/** | n/a (invariant) | all SB |
| **S9 scope closure: SB coverage matrix** (R272-R273) | In M2-T015 | M2-T015 · 3k | `docs/M2-T015-SB-COVERAGE-MATRIX.md` | n/a | SB-S1..S9 |
| **S9: end-to-end real-path proof** (R274) | In M2-T015 (runs in Linux CI) | M2-T015 · 3k | `test_e2e_survey_ingestion.py` | n/a | SB-S1, SB-S3 |
| **S9: parser-isolation capability enforcement** (R275-R276) | In M2-T015 (code); prod deployment deferred | M2-T015 · 3i + **follow-up deployment blocker** | `isolation.py`, `extraction/**` · `test_isolation.py` | n/a | SB-S1, SB-S2, SB-S6 |

## SB-S1..S9 → unit coverage assignment (R281 column 6)

| Scenario | Covering unit(s) | Note |
|---|---|---|
| SB-S1 vector-PDF ingest via vector path, full evidence, checks pass | 3b, 3i, 3g, 3k | real extraction runs in CI (isolation provable); disabled fail-closed on Windows host |
| SB-S2 extraction-path routing / unapproved-format reject-or-defer | 3i | per M2-T014 format policy |
| SB-S3 deterministic verification (closure/area/segment/contradiction) passing+failing | 3g (+3d,3e) | each check with a passing and a failing fixture |
| SB-S4 tax-lot cross-check typed, never silently overrides survey | 3h | read-only MapPLUTO domain models |
| SB-S5 fail-closed AI boundary → needs_review, not canonical | 3f | AI cannot trigger/veto transitions |
| SB-S6 security pack (extension/oversize/page-pixel/decompression/malformed) | 3b, 3c, 3i | immutable originals, digests, no temp residue |
| SB-S7 wrong-address/BBL flagged, not ingested | 3i, 3f | routed to needs_review |
| SB-S8 contract validation + drift discipline | 3j | schema + generated artifact + fixtures |
| SB-S9 full repository CI green on both events | 3k | after every prior unit merged |

## Follow-up created (R278)

**FOLLOW-UP (deployment hold, not a hardening-area omission): production parser-isolation
substrate + storage provisioning.** Reason it cannot lawfully/technically complete inside
M2-T015: it requires (a) production credentials/provisioning (owner/Tier-D + B-001 hold) and (b)
proving Landlock+seccomp on the live Render substrate, which needs the deployed environment.
M2-T015 delivers the fail-closed capability-gated CODE and proves it in Linux CI; production
DECODING stays disabled until this clears. Tracked under existing **B-001** (production storage)
with the exact deployment blocker recorded in the Unit-3i/3k evidence. This preserves an honest
acceptance hold on *live production parsing* only — every other M2-T015 component completes.

## Holds & anti-detour honored (R242-R246, R280)

M0-T052 not reopened; no supervisor/controller/ACL/config/autonomy/infra cycle; M0-T053 stays
backlog (blocking only under the R244 conditions); M0-T047 untouched; no framework rewrite, no
speculative features, no scope deletion.
