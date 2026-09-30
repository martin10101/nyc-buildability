---
name: env-python311-full-suite
description: services/api gate runs in this sandbox use Python 3.11, which cannot collect the PEP-695 tests/documents tree or one contracts ast.parse test — env limitation, not a defect
metadata:
  type: feedback
---

When running a services/api QA gate in this sandbox, `python --version` is 3.11
but the repo declares `requires-python >=3.12` and uses PEP 695 generics
(e.g. `def _match_unit[UnitT: enum.Enum](` in `app/documents/units.py`).

Consequences observed (2026-09-06, M2-T020 gate at bc106d8d):
- `python -m pytest services/api/tests` fails with ~15 COLLECTION errors under
  `tests/documents/**` (SyntaxError on the 3.12 generic syntax).
- One additional FAIL: `tests/contracts/test_contract_serializers.py::
  test_serializer_imported_exactly_at_the_profile_write_boundary` — it
  `ast.parse()`s every source file and chokes on the same `units.py` line.

**Why:** the sandbox interpreter is 3.11; CI runs 3.12 where these collect/parse
fine. These failures are NOT attributable to the task under review as long as the
task did not touch `app/documents/**` or introduce the failing syntax.

**How to apply:** for a services/api gate, run the task-scoped dirs
(`tests/spatial tests/api` etc.) which collect cleanly, plus
`tests -q --ignore=tests/documents` for a broad regression sweep; attribute any
residual `units.py` PEP-695 failures to the interpreter version (verify the task
diff did not touch `app/documents/**`), and request 3.12 CI evidence rather than
returning BLOCKED. Set `PYTHONPATH=<...>/services/api` so `app` imports (there is
no conftest adding it). See also [[m2t015-python312-and-gate-lessons]].
