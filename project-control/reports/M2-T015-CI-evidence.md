# M2-T015 — Orchestrator-captured CI evidence (SB-S9 / G4)

Captured by the orchestrator because the shipped `units.py::_match_unit` uses **PEP 695** type-parameter
syntax (correct for the project's `requires-python >=3.12` / ruff `target-version=py312`), which the
review/dev sandboxes (Python **3.11** only; the local 3.12/3.13 interpreter is absent) cannot parse. CI's
`api` job runs **Python 3.12** and is the authoritative pytest+ruff runner. Reviewers on 3.11 verify this
stored evidence per the evidence-capture division of labor.

## Authoritative run
- **Commit:** `408513b` (task/M2-T015-survey-ingestion head), merged to main as `1b3af35` (PR #213).
- **Workflow run:** 31326826299 · **api job:** 93278422472 · **conclusion: SUCCESS**.
- **Runner:** ubuntu-latest, `actions/setup-python` **python-version "3.12"**; tooling from the hash-pinned
  `requirements-tools.lock` (ruff==0.13.0), runtime from `requirements.txt`, app `pip install --no-deps .`.

## Results (verbatim from the api job log)
```
Run ruff check .
All checks passed!
...
2025 passed, 1 warning in 10.42s
```
- **Ruff 0.13.0 `ruff check .` (whole services/api tree): exit 0 — All checks passed.** (The earlier 37
  violations, incl. UP047 → PEP 695 and the 15 E501, are cleared.)
- **Full `pytest -q` api suite: 2025 passed, 1 warning.** (The `tests/documents/` subset is 939 passed / 1
  skipped.)

## Local corroboration (Python 3.11, this session)
- `cd services/api && python -m ruff check .` (pinned ruff **0.13.0**) → **All checks passed** on the shipped
  PEP 695 code (ruff parses independently of the runtime).
- `python -m pytest tests/documents/ -q` → **939 passed / 1 skipped**, reproduced on 3.11 with the
  **runtime-identical non-generic form** of `_match_unit` (Python generics are compile-time only; the shipped
  PEP 695 function body is byte-identical at runtime), then the clean PEP 695 form was restored for CI parity.
- `python .github/scripts/validate_contracts.py` → **exit 0** (10 schemas, incl. the new survey_evidence fixture).

## Conclusion
SB-S9 ("full repository CI green on both events") and the G4 integration/regression gate are satisfied at the
reviewed identity: required checks green (api ruff+pytest on 3.12, contracts, contracts-schema-bundle,
contracts-typegen, control-plane, web, web-e2e, credential-scan); the only red is the non-required
`web-dependency-security` (nanoid age-gate, eligible 2026-08-10; Tier-A-unaffected).
