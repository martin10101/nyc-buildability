# M4-T022 producer report — ready for independent review

Producer: official-source-researcher (`feedback_source_producer`). Worktree: `m4t022-validation`, supplied base `dd22b95`, task branch `task/M4-T022-validation`. Work performed 2026-09-15 UTC. This producer did not mutate git, the controller, application/backend code, rule files, dependencies or deployment settings. Task acceptance remains with the orchestrator and independent gates.

## What was checked

The fresh official expectation fixture was written at **2026-09-15T23:26:42.094961Z before implementation-table inspection**. It contains 49 source rows, 45 district identifiers and both FAR columns from current [ZR 23-21](https://zr.planning.nyc.gov/article-ii/chapter-3/23-21) and [ZR 23-22](https://zr.planning.nyc.gov/article-ii/chapter-3/23-22). Source text captures and SHA-256 identities are retained. Expected fixture digest: `a44bf5f5bd085d28913dd1c333940a4e9090fb6d7bdc25af48f2caf9a1d5cdb7`.

- **98/98 reference-value comparisons match.** This establishes the two general FAR tables' numeric transcription, not property eligibility.
- **90/90 draft-engine numeric outputs match** for 45 independently expected district cases, each using an explicitly supplied district and 2,500 sq ft input. The existing engine and default packaged snapshots executed in the locked API runtime; no alternate implementation calculated production outputs.
- **21 distinct real parcels** cover all five boroughs. **20/21** have matching district sets in the separate ZTLDB official dataset. Condominium billing BBL `1002737501` has no returned ZTLDB row and stays an explicit gap.
- **Five actual live browser records**, independently captured by the orchestrator, match the PLUTO residential-FAR references. All five return **no supported calculated cap**, with `spatial_intersection_absent`. These are source/display successes and calculation gaps. This producer did not rerun those browser actions. The copied raw browser baseline and derived observations preserve origin and timestamps.
- **17 audit tests pass**, including deliberate wrong R6A value, missing value, missing conditional alternative, duplicate rule ownership, wrong source section, wrong property identity, malformed numeric values, zero versus missing, changed source digest and a path outside the fixture directory.

The resulting audit has **368 passing checks and 80 explicit gap rows, no numerical mismatches**. These counts mix evidence layers and must not be used as a product completion percentage. The gap rows include repeated unobserved/uncalculated cases, not 80 independently diagnosed defects.

## Sources and parcel interpretation

`M4-T022-source-matrix.json` links the current official tables, table checks, footnote conditions and [PLUTO dictionary 26v2](https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf), pages 36–37 and 45–46. BuiltFAR is the rough recorded existing building-area ratio. ResidFAR is a district-based city reference; it does not establish project-specific permission. Bare R6, R7-1, R7-2, R8 and R9 use the dictionary's sky-exposure-plane meaning, so equality with a different general-table path is not required.

`M4-T022-real-parcels.json` and `M4-T022-coverage.md` contain the complete sample with request URL, source retrieval time, BBL, district sets and per-layer outcomes. The sample includes the reported 1279 37 Street / PLUTO 3622 13 Avenue BBL `3052960043`: BuiltFAR 2.61 and residential reference FAR 3.00 remain separate facts. The alias itself relies on the parent investigation; this producer's new PLUTO capture verifies the representative record, not a second independent GeoSearch alias resolution.

Primary-R-prefixed inventory alone omitted R11/R12. A subsequent bounded search across all four district columns found mixed assignments, so the initial absence hypothesis was rejected. Examples retained: `165 WEST 23 STREET` BBL `1007990008` has C6-3X plus M1-8A/R11; `501 8 AVENUE` BBL `1007590037` has M1-9A/R12 plus C6-4M and MSX/HY. These are real coverage contexts, not evidence that the simple R11/R12 rule governs the complete parcel. R10H appears in official records but is outside these general-table district rows; its current draft-rule refusal is recorded, not assigned an invented FAR.

One initial research query used `splitzone='Y'` and returned HTTP400. Current SODA responses revealed a boolean field. The corrected `splitzone=true` query succeeded. The failed request remains in evidence as a research-request gap rather than being counted as a passing application test.

## Executable verification

Exact commands and raw final output are in `tests/fixtures/residential_validation/verification_runs.json`; final engine results and content identities are in `M4-T022-test-results.json`.

| Command | Actual result |
|---|---|
| `python -m unittest tools.test_residential_validation -v` | Exit 0; 17 tests, OK |
| `python tools/residential_validation.py --check-fixtures` | Exit 0; 210 pass, 29 gap; 21 parcels; no citywide/legal certification |
| `PYTHONPATH=services/api /workspace/scratch/cfa2464c5c7f/feedback-test-venv/bin/python tools/residential_validation.py --check-fixtures --engine --full` | Exit 0; 368 pass, 80 gap; 90 actual draft numeric outputs |
| `python tools/modularity_check.py --check` | Exit 0; 435 selected files, 0 failures, 18 existing warnings outside these new files |

Initial scaffolding run failed with `ModuleNotFoundError` before the helper existed. This is scaffolding evidence only. Meaningful critical-regression mutation proof then replaced the numeric equality decision with unconditional pass. `python -m unittest tools.test_residential_validation.ResidentialAuditTests.test_wrong_r6a_reference_is_detected -v` failed, exit 1, `AssertionError: False is not true`. Restoring the equality decision made the same test pass, exit 0. The fixture mutation tests also prove wrong expected/source values cannot silently pass. Full final tests ran after the last helper edit.

Verification context: cloud Linux, isolated worktree, no new dependencies, parent-installed hash-pinned API runtime. Windows was not run. This offline stdlib helper is manually reusable; **the new test is not yet named by existing CI jobs**. No continuous automatic gate is claimed. Network requests were bounded (small projected records, at most four concurrent initial requests, 20–30 second timeout per request, no unbounded retry, no citywide parcel download). The production application was only read through the parent's browser work.

## Remaining development work exposed

1. Restore/complete the real-property spatial evidence path before claiming calculated allowances. The live cause needs its own backend investigation; this task does not modify it.
2. Connect and validate wide-street/100-foot/partial-lot eligibility. The FAR rule currently returns its conservative base while preserving the alternative. Exact-boundary geometry eligibility is **not established** here.
3. Implement qualifying-site/housing, UAP/MIH and special-district decisions with their required evidence. The R8 8.64 value retains its compound conditions.
4. Implement the first-row R1/R2/R3 per-unit 0.60 limit for lots at least 4,000 sq ft using per-unit inputs. Its limitation is preserved by current traces; it is not computed here.
5. Complete and verify height, yards, coverage, street wall and full building envelope in the normal property journey. This FAR audit does not certify them.
6. Resolve mixed/split/special and condominium identity gaps. Refusal safeguards are passing safeguards, not successful numerical coverage.
7. Add the bounded audit to an explicitly scoped CI job if automatic ongoing enforcement is desired.

No new architect benchmark sheet or repeated client confirmation was requested or used. Only a batched, genuinely unresolved legal decision would require qualified review; engineering checks proceed internally.

## Directive and reliability evidence

| Requirement | Producer evidence; independent verification pending |
|---|---|
| D-063-R003 | Fresh independent expected fixture, real engine run, negative and mutation evidence |
| D-063-R004 | R1–R12 table coverage and 21 real records across five boroughs, with mixed/special/split/condo contexts explicitly separated |
| D-063-R005 | Changes restricted to read-only audit, fixtures and named reports; production files unchanged |
| D-063-R006 | Per-layer outcomes, explicit gaps, no universal correctness or completed bulk claim |
| D-063-R007 | Internal tests performed without repeated architect questions or a new benchmark-sheet dependency |
| D-063-R008 | No git mutation; main and PR241 untouched by this producer |
| D-063-R009 | `legal_approval: false`; draft results remain needs_review/non-verified; no production approval claimed |
| D-063-R010 | No replacement application calculator, API/schema/database/credential/deployment mutation |

Engineering Reliability Standard §1: the parent live benchmark falsified the FAR-swap hypothesis; the repeated live mechanism is missing spatial evidence, while a presentation issue obscures the relevant reference. §3: source-derived acceptance checks and critical comparison mutation/revert evidence. §8: runtime context, frozen content identities, actual neighbor engine execution, typed missing/malformed cases, parent live journey and independent-review boundary. §10: exact scoped counts only; no speed, financial-value, citywide correctness or reliability improvement claim.
