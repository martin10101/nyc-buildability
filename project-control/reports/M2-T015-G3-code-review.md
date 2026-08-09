# Gate Report

- Gate ID: G3 (human-style walkthrough)
- Task ID: M2-T015 (units 3k + 3l — secure survey ingestion/extraction/verification pipeline)
- Reviewer: code-reviewer (independent, read-only)
- Result: **FAIL** (single blocking defect: SB-S9 ruff/CI; no functional/correctness defects)
- Clean worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015` at frozen SHA `897e7df6c29753008a14fbb4c1457752e19ed2e0`.

> Saved verbatim by the orchestrator (report-preservation; transport entity-decoding only).

## Acceptance criteria reviewed
The 9 scenarios SB-S1..SB-S9 in `project-control/tasks/M2-T015.json` and the producer map `docs/M2-T015-SB-COVERAGE-MATRIX.md`, verified against actual source and tests (not taken on faith).

## Steps independently executed
1. `cd services/api && python -m pytest tests/documents/ -q` → **925 passed, 1 skipped in ~1.5s**. The 1 skip is `tests/documents/test_gate.py:308` "host forbids symlink creation" — environmental, benign.
2. Focus suites: `pytest tests/documents/test_survey_pipeline.py test_crosscheck.py test_vector_pdf_decoder.py test_extraction_routing.py -q` → **131 passed**.
3. Read the seam/mechanism source: `routing.py`, `survey_pipeline.py`, `vector_pdf_decoder.py`, `crosscheck.py`, `checks/__init__.py`, `checks/metadata.py`, and the four focus test files.
4. Reproduced the CI `api`-job lint step: `cd services/api && ruff check .` (ci.yml line 211, working-directory `services/api`) → **exit 1, 37 errors**.
5. Confirmed branch state: `git cat-file -e origin/main:services/api/app/documents/correction_history.py` → ABSENT on origin/main; `git rev-list --count origin/main..HEAD` → 27. The entire documents module is new on this branch and has never passed a green full-repo CI at this SHA.

Caveat: local ruff **0.9.9**; CI pins **ruff==0.13.0** (`requirements-tools.lock:379`). The E501/F401 findings are version-independent and reproduce under 0.13.0.

## Per-scenario walkthrough (input / expected / actual / evidence)
- **SB-S1** (digitally-authored → auto_extracted): 2 facts (scale+BBL), every fact `PromotionAllowed`, both checks pass, gated `processing→auto_extracted`. Matches. Concrete `VectorPdfDecoder` carried for the digitally-authored routes (`routing.py:370-373 _CONCRETE_DECODERS`), handed out at `begin_extraction_job:401`, invoked at `survey_pipeline.py:653`. Spy test proves decoder reached.
- **SB-S2** (routing; boundary): unsupported `docx` → `ExtractionNotStarted(unsupported_format)`; raster `tiff` → `DecoderUnavailable` (no decode); DXF/DWG deferred. Matches (`TestFormatRoutingMatrix`, closed matrix, all 8 enum members).
- **SB-S3** (deterministic checks; pass+fail; visible): decode refusal + empty + failed check all route to `needs_review` and RECORDED. The four required checks each have passing+failing fixtures at check-unit level (`test_checks_boundary.py`, `test_checks_area.py`). Honest-scope note verified: boundary/area reconstruction is a later unit; the pipeline wires `scale_consistency` + `address_bbl_match` — disclosed, not hidden.
- **SB-S4** (tax-lot cross-check, 3l): verified end-to-end. `_tax_lot_crosscheck` (survey_pipeline.py:574-600) reads the resolved BBL fact, defers to `tax_lot_bbl_crosscheck`; result recorded ONLY on `ExtractionCompleted.tax_lot_crosscheck`; routing coupling `auto_extract = auto_extract and crosscheck_clean` — can only pull toward review. Divergent → FAIL + `needs_review` (sole cause); match → promotion preserved; no reference → byte-identical to 3k. Facts byte-identical across none/match/divergent. Non-promotable, kept out of `check_results` and every fact's `validation_results`. Imports no state/storage.
- **SB-S5** (fail-closed AI/confidence): facts carry `confidence=1.0`, promotion rests solely on resolved validators. Matches.
- **SB-S6** (isolation fail-closed): isolation-disabled → `isolation_unavailable`, spy decoder proves `decode` NEVER called (`calls == []`). `begin_extraction_job` consults `require_isolation()` first, no bypass parameter. Decoder never raises (refusal-as-value).
- **SB-S7** (wrong-address): `WRONG_BBL_PDF` fails `address_bbl_match` → `needs_review` via raw (non-gated) `transition`, typed `NeedsReviewRouting` recorded + `fail` check on the BBL fact. Matches.
- **SB-S8** (contract validation): assembled facts validate against schema via real jsonschema engine + `$ref` registry. Matches.
- **SB-S9** (full-repo CI green): **FAILS at this SHA.** `cd services/api && ruff check .` exits 1 with 37 violations.

Gated vs non-gated transition discipline correct and asserted (`TestGatedTransitionWiring`: gated only for `processing→auto_extracted`, raw only for `processing→needs_review`).

## Ruling on the 3l `unevaluable → needs_review` question (asked to judge)
**CORRECT fail-closed behavior, not over-eager.** The cross-check can only demote toward review; outcome always RECORDED as typed `CheckUnevaluable` with a reason; facts never mutated. The "no BBL fact" case actually CLOSES a fail-open gap (a survey with no address/BBL skips `address_bbl_match`, so without the cross-check it would auto-extract with zero property-identity verification despite the caller supplying a tax-lot reference). Demoting to review is doctrine-aligned ("if material values cannot be independently validated, fail closed and produce a visible unresolved condition"). Malformed-reference sub-case demotes for an operator-supplied-reference defect, but the recorded reason names the true cause — non-misleading. Sound; would not change it.

## Non-blocking notes
(a) `_tax_lot_crosscheck` and `address_bbl_match` both consume only `bbl_facts[0]`; consistent, any divergence routes to review. (b) On decode-refusal early return, a supplied `tax_lot_reference` is not recorded — harmless (already routed to needs_review with refusal recorded); worth a one-line note if the outcome's `tax_lot_crosscheck` field is consumed as "was a reference provided." (c) PDF fixture helpers duplicated across two test modules — test-only.

## Defects
**D1 (blocking SB-S9) — `ruff check .` fails; CI `api` job would be RED at `897e7df`.** The dispatch's "ruff CI-equivalent clean (only UP038)" is accurate ONLY for the 3k/3l delta files. CI runs `ruff check .` over all of `services/api`, which exits 1 with 37 violations in earlier-unit files of the same M2-T015 module: 15× E501 (version-independent line-width; e.g. `correction_history.py:1`=106, `geometry_validation.py:1`=104, `units.py:1`=103, `test_correction_history.py:205`=110), 1× F401 (`pdf_objects.py:72` unused `LexedToken`), plus 7× UP007, 4× I001, 3× B010, 2× B009, 2× B905, 2× UP017, 1× UP047 — all stable rules 0.13.0 still enforces. Files ABSENT from origin/main (27 commits ahead); SB-S9's "full repository CI green" not established. **No functional/correctness defects found in the 3k/3l pipeline, decoder, or SB-S4 cross-check.**

## Required rework
1. Bring the full `services/api` tree to a clean `ruff check .` under pinned ruff 0.13.0: `ruff check . --fix` clears the 21 auto-fixable; manually wrap the 15 E501 lines to ≤100; re-verify `ruff check .` exits 0 and `pytest -q` stays green.
2. Re-establish SB-S9 with an orchestrator-captured CI run at the new SHA (both push/PR events).

## Reviewer conclusion
The 3k/3l implementation — routing/isolation seam, refusal-as-value `VectorPdfDecoder`, the route→isolate→decode→assemble→check→promote flow with correct gated/non-gated edge discipline, and the SB-S4 context-only tax-lot cross-check (incl. the `unevaluable→needs_review` rule, ruled correct) — is sound, doctrine-faithful, and well-tested (925 pass / 1 skip). However, **SB-S9 (full repository CI green) is reproducibly not met**: `ruff check .` exits 1 at the reviewed SHA with version-independent violations. Verdict: **FAIL** — mechanical lint rework then re-capture CI; the pipeline logic needs no functional changes.

---

## G3 Re-review — at merged main HEAD `1b3af35` (post-rework): VERDICT PASS

Same independent code-reviewer. Prior FAIL was **solely** the SB-S9 ruff failure (no functional defects; 3l
`unevaluable→needs_review` ruled correct). Resolved:
- `cd services/api && ruff check .` under CI-pinned **ruff 0.13.0** → **All checks passed, exit 0** (the prior 37
  cleared), independently reproduced.
- `git diff 897e7df 1b3af35 -- services/api/app/documents/` = 7 files, +21/−23, **lint-only**; the 8
  routing/decode/assemble/check/cross-check/promote/state pipeline files are **byte-identical (zero diff)** — so
  the functional walkthrough carries over verbatim. Each lint hunk analyzed behavior-preserving (UP017 `UTC`
  alias, B905 `strict=False` default, B009 attr-access, F401 unused import, UP007 `X|Y`, E501 docstrings, UP047
  PEP 695 same generic semantics). New material (fixture pack, matrix, fixture test) is additive.
- Stored CI evidence verified (`M2-T015-CI-evidence.md`): api job 3.12 SUCCESS — ruff clean + 2025 passed
  (documents subset 939). Local pytest not runnable (PEP 695 needs 3.12; 3.11 sandbox) → evidence-capture
  division of labor; NOT a BLOCKED condition.

**Verdict: G3 PASS at `1b3af35`.** No defects, no rework.
