---
name: reviewer-sandbox-python-311-artifact
description: Reviewer sandbox runs Python 3.11 while the repo targets 3.12 - a whole-api-suite run red-herrings on PEP 695 syntax in app/documents/units.py; never report it as a producer regression
metadata:
  type: project
---

The QA-reviewer sandbox interpreter is **Python 3.11.9**, but repo source uses PEP 695
generic-function syntax (`def _match_unit[UnitT: enum.Enum](...)` in
`services/api/app/documents/units.py`). Running the WHOLE api suite from `services/api`
therefore produces:

- `python -m pytest -q` -> `Interrupted: 15 errors during collection` (all `tests/documents/*`)
- `python -m pytest -q --ignore=tests/documents` -> `3099 passed, 1 failed`, the single failure
  being `tests/contracts/test_contract_serializers.py::test_serializer_imported_exactly_at_the_profile_write_boundary`
  (it `ast.parse`s `units.py`).

**Why:** the version skew is environmental, not a defect. `units.py` last changed in M2-T015,
long before any current packet, so attributing these to the task under review would be a false
FAIL. CI runs 3.12 and is the authoritative green.

**How to apply:** when broadening regression evidence beyond a packet's documented test commands,
run `--ignore=tests/documents` and state the skew explicitly in the gate report's limitations
section. Confirm `python --version` before treating any collection error as a producer regression.
Related: [[feedback_probe_separator_deleting_normalizations]].
