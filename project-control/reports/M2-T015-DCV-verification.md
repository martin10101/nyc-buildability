# GATE REPORT — M2-T015 (Directive-Compliance / DCV)

**Task:** M2-T015 — Secure survey ingestion, extraction, and deterministic verification (Packet B)
**Reviewed SHA (frozen):** `897e7df6c29753008a14fbb4c1457752e19ed2e0`
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015` (merge-base with main `d2b6e87`)
**Verdict: FAIL (for acceptance at `897e7df`)** — reproducible required-CI-check failure + missing named deliverables.

> Saved verbatim by the orchestrator (report-preservation; transport entity-decoding only). NOTE: the DCV
> derived **29** applicable requirements from the STALE worktree D-010 registry (merge-base d2b6e87);
> main's current registry derives **97** for M2-T015. The blocking defects below are registry-version-
> independent. A re-verification against main's 97 at the reworked green SHA is required before acceptance.

## Reproduced evidence (independent runs)

| Check | Command | Result |
|---|---|---|
| Documents test suite | `cd services/api && python -m pytest tests/documents/ -q` | **925 passed, 1 skipped** (skip = `test_gate.py:308` host forbids symlink) |
| Contract validation | `python .github/scripts/validate_contracts.py` | **exit 0**, 10 schemas |
| TS generator test | `pytest packages/contracts/scripts/tests/test_generate_survey_evidence_ts.py -q` | **5 passed** |
| Scenario tests SB-S3/S4/S5/S6/S7 | targeted `pytest -v` | **60 passed** |
| **CI-equivalent ruff** | `cd services/api && ruff check .` (ruff **0.13.0** pinned; `select=[E,F,I,UP,B]`, line-length 100) | **exit 1 — 37 errors, ALL in M2-T015's own new files** |

## Blocking defect #1 — CI is NOT green (SB-S9 fails); the "ruff clean" claim is false
CI runs the `api` job as `ruff check .` (working-directory `services/api`) before pytest; ruff exits 1, so SB-S9 ("full repository CI green on both events") is not met. Statistics: 15 E501, 7 UP007, 4 I001, 3 B010, 2 B009, 2 B905, 2 UP017, 1 F401, 1 UP047. None is UP038. All 37 in files created by this task (`app/documents/**` + `tests/documents/**`), which do not exist on `main`. `pyproject.toml` has no exclude/per-file-ignores.

## Blocking defect #2 — named deliverables absent + producer report stale
- `docs/SURVEY_FIXTURE_MATRIX.md` — a **named output, a named `allowed_path`, and part of the objective FIXTURES clause** — is **absent**. What exists is `docs/M2-T015-SB-COVERAGE-MATRIX.md` (not in `allowed_paths`).
- The required **"committed synthetic fixture pack with MANIFEST digests (build_fixture_pack.py pattern)"** is **absent** — no MANIFEST, no `build_fixture_pack`, no committed fixture files under `services/api/tests/documents/` (fixtures are built programmatically in-code).
- `project-control/reports/M2-T015-producer-report.md` documents **only through Unit 2**, while commits run through **unit 3l** — the AOS §6 return packet is incomplete/stale.

## Positive findings (reproduced)
- **Diff is scope-clean for prohibitions:** `git diff --name-only d2b6e87..HEAD` touches no `config.toml`, ACL, supervisor, `.claude/`, or `project-control/` (except its own report). Fully additive (18785 insertions, 2 deletions in the M2-T010 generator).
- **Contract substance real:** `survey_evidence.schema.json` requires all provenance fields with `additionalProperties:false`.
- **Fail-closed / no-override proven:** cross-check `overrides_survey=False`, read-only, non-promotable; confidence promotes nothing; wrong-address → `needs_review`.

## Per-requirement verdict (29 applicable at the stale registry)
25 SATISFIED (several dispatch-scope/upstream: R121/R123/R214/R215/R220), **2 VIOLATED (R227, R234)**, **2 UNVERIFIABLE from the frozen worktree (R221, R224 — dispatch-scope activation records on `main`)**.
- **R227** (obligation): mechanism real (supervisor commits, 925 tests, real contract) BUT the task's own code **fails the required CI ruff check (37 errors)** so "normal PR lifecycle operating as designed" is not demonstrated, and authorized bounded work is **incomplete** (missing `SURVEY_FIXTURE_MATRIX.md` + fixture-pack MANIFEST).
- **R234** (obligation): "do not claim something passed unless evidence proves it" + "preserve required gates" — the **"ruff clean" claim is contradicted** by reproduced evidence and the required CI gate is **not green**.
- **R221/R224** (evidence/obligation): activation-record durability lives on `main`; UNVERIFIABLE from the frozen worktree — orchestrator confirms on main.

## Deferred vs defect
- **Genuinely deferred / lawful:** AREA tax-lot cross-check awaits lot-area geometry reconstruction (later unit); B-001 production storage/tenant-isolation/retention designed-but-deferred.
- **Defects, not lawful deferrals (blocking):** (1) reproducible **ruff CI failure** — SB-S9 unmet; (2) **missing named deliverables** (`SURVEY_FIXTURE_MATRIX.md`, fixture-pack MANIFEST); (3) **stale producer report**.

## Recommendation
**FAIL.** Do not accept `897e7df`. Required to clear (subsequent unit/SHA, then re-review): (1) `cd services/api && ruff check .` exit 0 at the reviewed SHA; (2) deliver `docs/SURVEY_FIXTURE_MATRIX.md` + committed synthetic fixture pack with MANIFEST digests, or an explicit owner-approved scope reduction; (3) bring the producer report current through the final unit; (4) orchestrator confirms R221/R224 activation records on `main`; (5) [orchestrator] re-verify against main's current 97-requirement set. Test/contract substance (925 pass, contract exit 0, provenance schema, fail-closed/no-override) is otherwise sound and reproducible.

---

## DCV RE-VERIFICATION — at merged main HEAD `1b3af35` (post-rework): VERDICT PASS (97/97)

Same independent directive-compliance-verifier, at the PRIMARY checkout (current registry). Applicable set
re-derived **97** (0 unresolved) — the correct authoritative set (pass-1 used the stale 29-req worktree registry).

**All three prior FAIL findings independently reproduced as RESOLVED:**
1. SB-S9 ruff — `cd services/api && python -m ruff check .` (pinned 0.13.0) → **All checks passed, exit 0** (37→0).
2. Named deliverables — `docs/SURVEY_FIXTURE_MATRIX.md` present; fixture pack `services/api/tests/documents/fixtures/survey_documents/` (build_fixture_pack.py + SVY01..SVY14 + MANIFEST.json + test_survey_fixture_pack.py); **14/14 sha256 digests + byte-sizes recomputed → MATCH**; MANIFEST covers all 12 objective categories.
3. Producer report current through unit 3l + rework.

**Independently reproduced at `1b3af35`:** ruff exit 0; `validate_contracts.py` exit 0 (10 schemas); TS drift `--check` up-to-date + generator test 5 passed; 14/14 fixture digests; **367 pytest passed / 1 skipped** on the 3.11-importable documents test files (those not importing the PEP-695 `units.py`); activation records R221/R224 (`doctor-pre-activation.json` PROTECTED/shadow, `start-*-output.json` supervised/limited-auto-off); ledger (M0-T054 accepted, M0-T052 accepted-untouched, M0-T053 backlog). Full `pytest -q` (2025) / documents (939) rest on the orchestrator-captured 3.12 CI evidence (`M2-T015-CI-evidence.md`, api job SUCCESS) per the evidence-capture division of labor (PEP-695 needs 3.12; sandbox is 3.11).

**Per-requirement verdict: all 97 PASS** — hardening/completion (R249, R252–R280 taxonomy/units/geometry/correction-history/promotion/fixtures/contract-pipeline/coverage/isolation/scope), prohibitions/holds by diff-negative (R217/R218/R223/R229/R231/R234/R240/R242/R243/R280/R341/R232), product-proof & self-sufficiency (R227/R228/R235/R248/R283/R284/R299), activation preconditions now VERIFIED on main (R219–R226), dispatch/turnover control-plane (R121/R123/R133/R143/R153/R167/R172/R196/R213–R216/R236–R251/R285–R295/R298/R302/R303/R304/R317/R318/R343/R281/R282).

**Tally: 97/97 PASS · 0 VIOLATED · 0 UNVERIFIABLE.** Non-blocking observations: allowed-path deviations all in-scope (`.gitattributes` binary-marks the fixture pack; `SB-COVERAGE-MATRIX.md` is the R272 matrix and `SURVEY_FIXTURE_MATRIX.md` is ALSO present; `generate_ts_types.py` is the M2-T010 generator); one non-required red check `web-dependency-security` (nanoid age-gate, Tier-A-unaffected).

**Recommendation: PASS — accept M2-T015 at `1b3af35`.**
