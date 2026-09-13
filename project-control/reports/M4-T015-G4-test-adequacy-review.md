# G4 GATE REPORT — M4-T015 (D-045 B2 DCM Street-Width Connector + fail-closed width classifier)

> Orchestrator note: reviewer return saved VERBATIM from the agent-return channel
> (transport entity-decoding only). Reviewer: qa-engineer. Recorded by the
> orchestrator per ADR-005. The cohesion justification recorded inside this review
> discharges the modularity review_signal policy obligation for
> services/api/app/connectors/dcm_street_centerline_arcgis.py.

I have completed all review work. Here is my full G4 gate report.

---

**Reviewer:** qa-engineer (independent; not the producer — producer was backend-engineer)
**Gate:** G4 (test adequacy / integration)
**Reviewed SHA (frozen):** `b3e66078ee50cbf1a8de89d0b85cdd2dfe50dffb` (material commit `8538c272`, 34 files)
**Review context:** isolated worktree `agent-ac40a0fae05cd94f3`, `git fetch` + `git reset --hard b3e66078…` (worktree-only, per anchor). Primary checkout untouched.
**Mode:** read-only. No repository implementation files edited; no `project_control.py`/git write commands run. (Only memory notes written under `.claude/agent-memory/qa-engineer/`.)

## Commands I ran (verbatim outputs), at the frozen SHA

| Command (from `services/api`, `PYTHONPATH='.'` where needed) | Result |
|---|---|
| `python -m pytest tests/connectors -q` | **619 passed** in 4.06s |
| `python -m pytest tests/connectors/test_dcm_street_centerline_arcgis.py test_dcm_street_width_classifier.py -q` | **131 passed** in 0.17s |
| `pytest … --collect-only` (per file) | connector **49** tests / classifier **82** tests (=131) |
| `python tools/modularity_check.py --check` (repo root) | `selected 401 files; failures 0; warnings 17` — **EXIT 0** |
| `python -m ruff check .` (ruff **0.13.0**) | `All checks passed!` — **EXIT 0** |

619 passed and modularity EXIT 0 match the orchestrator's capture. Sandbox is Python 3.11.9; the code uses no 3.12-only syntax (`from __future__ import annotations`; `from datetime import UTC` is 3.11+), so this run is representative. CI on 3.12 for `8538c272` is orchestrator-captured evidence (in flight). [Orchestrator capture: the CI run at 8538c272 concluded SUCCESS — all jobs green, api job included.]

## Per-mandate findings

**1. Coverage.** S1–S6 each have executable, reproducible proof. Every packet output is exercised: both modules (imported and called), both test files (run green), the 26-fixture set (`test_manifest_matches_fixture_bytes_on_disk` asserts on-disk set == manifest set both directions + sha256 + byte-count per fixture, plus per-class classification tests), the registry draft (`self_declared_source_id` present and matches the connector's `SOURCE_ID = "nyc-dcp-dcm-street-centerline-arcgis"`; deep contract belongs to G1). The classifier defines **24** typed classes in `AMBIGUITY_CLASS_DISPOSITIONS`; I confirmed each of the 24 has a binding test that pins its `ambiguity_class` (adversarial spot-checks of the producer-report table vs code vs tests all consistent — `gt_inequality_ge_75`→wide/False, `range_straddles_cutoff`→narrow/True, `le_inequality_at_or_above_75_ambiguous`→"<=75", `negative_value_unexpected`→"-10", `unexpected_type`→non-string, all match). PASS.

**2. Binding / mutation adequacy.** Strong.
- **75-ft threshold:** bound on both sides — `"75"`→wide and `"74.99"`→narrow, plus `test_wide_threshold_is_75` asserts `WIDE_THRESHOLD_FT == 75.0`. Any threshold-constant mutation fails a test.
- **both-endpoints range rule:** `"75-90"`/`"75-100"`→wide, `"60-75"`/`"74-75.3"`→straddle-narrow-review, `"50-60"`/`"10-74.9"`→confident-narrow. A mutation to "either endpoint ≥75" flips `"60-75"` to wide and fails the straddle assertions.
- **strict ≥75 inequality:** `">75"`/`">=75"`→wide vs `">60"`/`">50"`→ambiguous; `"<75"`/`"<=74"`→confident-narrow vs `"<=75"`/`"<80"`→ambiguous. The strict-vs-non-strict distinction at exactly 75 is asserted on both sides.
- **mapped-street override:** all four triggers bound (below), and it never over-fires (a wide mapped street with no flags stays wide; an already-narrow segment + a flag is unchanged, `override_reason=None`). PASS.

**3. Fail-closed branches.** Every ambiguous class asserts `narrow_fail_closed` + typed class + `review_required=True`. Paper/record/former/unmapped override tested **with wide-looking width text** (`paper_street_override_wide` Feat_Type=Mapped_St+Paper_ST=Y+raw"80"; former raw"100"; unmapped raw"80") → raw classifier=WIDE but `effective_disposition`=narrow with `override_reason` citing the trigger; the raw read is preserved in `width_classification`. HTTP-200 error object → `UpstreamError` (`arcgis_error_code==400`). Two-page fixtures (disjoint OBJECTIDs 7,10,11,18,68 / 71,72,74,85,98) prove offset advance + merge + termination; duplicate-page, repeated-object-ids, zero-progress, and page-budget pathologies each raise typed `PagingPathologyError`. Network failure → typed `UpstreamError`. PASS.

**4. Offline discipline.** All 131 tests run with zero network via the injected `fetch` seam serving recorded bytes; no test invokes `default_fetch` (the live path). Fixtures are loaded byte-verbatim; the manifest self-consistency test enforces byte identity. The single synthetic fixture (`provider_error_http200_synthetic.json`) is marked `"synthetic": true` with `url: null` and is used only in the error-shape test. PASS.

**5. Regression + lint.** 619 passed (no regressions in any pre-existing connector test), modularity EXIT 0, ruff 0.13.0 EXIT 0 — all reproduced by me. PASS.

**6. Producer disclosures.** `empty_or_missing` has no live fixture (I confirmed the disclosure rationale) and is bound by `test_none_is_empty_or_missing` + `test_empty_string_is_empty_or_missing` (class + disposition + review). 3.11 collected fine (reproduced). No test-only dead code: both modules are cohesive single-responsibility units; `default_fetch` is the production live seam (legitimately not exercised offline). PASS.

## Findings

**BLOCKING:** none.

**ADVISORY-1 (producer report accuracy — modularity, most material).** Producer report §9 states the verbatim output as `selected 399 files; … warnings 16` and "neither new module appears in the warning list." At the reviewed SHA the actual output is `selected 401 files; failures 0; warnings 17`, and `services/api/app/connectors/dcm_street_centerline_arcgis.py` **is** listed: `review_signal: above the justification threshold; record a cohesion justification in review`. `tools/modularity_check.py` is unchanged pre-task (`git log` newest = `5487b84a`), so the §9 claim is inaccurate at the reviewed candidate, not stale-by-tool-change. The check still EXITS 0. **I record the required cohesion justification in this review** (below), which discharges the policy obligation; combined with EXIT 0 and a genuinely cohesive module, this is not a FAIL. Recommend the orchestrator have §9 corrected.

> **Cohesion justification (recorded in review):** `dcm_street_centerline_arcgis.py` (959 lines) is one responsibility — the DCM Street Center Line ArcGIS connector: provenance constants, typed error taxonomy, injection-proof URL construction, a single-attempt no-retry transport seam, response parsing, layer-metadata validation, the per-segment typed envelope, and the paged entry point. The separable pure logic (free-text width classification) is already extracted to its own module (`dcm_street_width_classifier.py`, 390 lines). No unrelated domain logic, persistence, serialization-for-storage, or presentation is mixed in; no consumer wiring. Size is driven by exhaustive typed error handling and docstrings, not responsibility mixing or dead code. This mirrors the accepted M5-T020/M2-T009 precedent (`mappluto_geometry_arcgis.py`, itself in the warning list).

**ADVISORY-2 (report accuracy — test split).** §2/§9 state the 131 new tests split 46/85; `--collect-only` shows **49/82**. Total 131 is correct; per-file counts should be corrected.

**ADVISORY-3 (class-count wording).** The evidence map and commit message say "23 typed ambiguity classes"; the code and the producer-report table both have **24**. The authoritative artifact (report table) matches the code; correct the non-code "23" references.

**ADVISORY-4 (record-trigger isolation).** The record fixture (Woodvale 16549) sets both `Feat_Type=Not_mapped` and `Record_ST=Y`, so it does not isolate the record trigger the way the paper fixture isolates paper. The `"Record_ST" in override_reason` assertion + branch ordering still bind single-mutation removal of the record check, so this is adequate; a `Record_ST=Y` + `Feat_Type=Mapped_St` fixture would be strictly stronger.

**ADVISORY-5 (network-failure no-retry).** `test_network_failure_is_a_typed_upstream_error_no_retry` proves the typed error propagates but does not assert a single fetch call, so a retry-then-give-up would also pass. No-retry is structurally sound in `default_fetch` (one `urlopen`) and implicitly bound on the query path by the sequenced-fetcher tests (a retry would exhaust/misalign the fixture sequence). A call-count assertion would make it explicit.

**ADVISORY-6 (lt/le confident-narrow).** `test_lt_or_le_inequality_confident_narrow` asserts `ambiguity_class in (lt_…, le_…)` rather than the exact class per input; the ambiguous side is individually pinned and disposition/review are pinned on both, so this is minor.

## Scope / integration

Material commit `8538c272` touches exactly 34 files, **all within `allowed_paths`** (2 new modules, 2 new test files, 26 fixtures incl. MANIFEST, the registry draft, the producer report; plus the orchestrator-assembled evidence-map). No `rules/**`, `api/**`, `scenario/**`, `profile/**`, `spatial/**`, `config.py`, Geoclient/MapPLUTO/other connectors, or `requirements*/pyproject/package.json` touched — no consumer wiring and zero new dependencies (S6 confirmed). Registry SODA record correctly stays `PLAN ONLY` / non-final.

## Verdict

All six acceptance scenarios reproduce green with strong binding, fail-closed correctness, full offline discipline, clean regression, and clean lint. The only issues are documentation-accuracy discrepancies in the producer report (none affect the code, the acceptance criteria, or any reproducible result) plus minor test-robustness advisories; the modularity `review_signal` is discharged by the cohesion justification recorded above on a genuinely cohesive module.

**VERDICT: PASS**

Recommendations to the orchestrator (do not block): have the producer correct report §2/§9 (modularity = 17 warnings with the connector listed; per-file test split 49/82; class count 24), and carry the cohesion justification above into the gate record.
