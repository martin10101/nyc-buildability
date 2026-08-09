# M2-T015 — G2 self-check (orchestrator)

Recorded by the orchestrator 2026-08-09 at main `1b3af35`. Producer self-check preceding the independent
G1/G3/G5 + DCV gates (all PASS).

## Reproduced self-check evidence
- **Ruff:** `cd services/api && python -m ruff check .` (pinned ruff 0.13.0) → **All checks passed, exit 0**
  (whole tree; the earlier 37 violations cleared).
- **Tests:** full documents suite 939 passed / 1 skipped; full api suite **2025 passed** — authoritative on
  the **api CI job (Python 3.12)**, SUCCESS (captured `M2-T015-CI-evidence.md`); locally corroborated on 3.11
  (939 documents via the runtime-identical non-generic `_match_unit` form; 367 on the 3.11-importable subset).
- **Contract:** `validate_contracts.py` exit 0 (10 schemas, survey_evidence fixtures both directions).
- **Fixture pack:** 14/14 MANIFEST sha256 digests verified; 12 objective categories covered.
- **Deterministic + fail-closed:** isolation gate fail-closed reproduced; cross-check `overrides_survey=False`;
  no-AI-authority promotion; provenance on every fact.

## Honest limitation
Shipped `units.py::_match_unit` uses PEP 695 (correct for `requires-python>=3.12` / CI 3.12); the local
sandbox has only 3.11, so full-suite pytest rests on the orchestrator-captured 3.12 CI evidence (evidence-
capture division of labor). Deferred (lawful, documented): OCR/raster extraction, rotation-normalization,
distance/bearing normalization, boundary/area reconstruction + tax-lot AREA cross-check. Self-check PASS.
