---
name: pep695-ruff-vs-py311-sandbox
description: services/api targets py312 (ruff UP047 wants PEP 695); a py311-only sandbox can't parse it — prove pytest on the bounded-TypeVar form, then re-apply PEP 695 for ruff
metadata:
  type: feedback
---

`services/api` sets `requires-python >=3.12` and ruff `target-version = "py312"` (pyproject.toml),
and CI's `api` job runs Python 3.12 (every `setup-python` in `.github/workflows/ci.yml` pins
`python-version: "3.12"`). Ruff 0.13.0 (pinned in `requirements-tools.lock`, `select=[E,F,I,UP,B]`,
line-length 100) therefore raises **UP047** on a bounded `TypeVar` generic function and wants PEP 695
type-parameter syntax (`def f[T: Bound](...)`). Ruff 0.13.0 also raises **UP049** if the PEP 695
param name is private — so name it `UnitT`, not `_UnitT` (no leading underscore).

**Why:** the producer sandbox on a given session may have ONLY a working Python 3.11 (the local
3.12/3.13 install can be a gutted dir with no `python.exe` — see [[env-producer-sandbox-no-exec]]).
Python 3.11 cannot *parse* PEP 695 function-type-parameter syntax, so once you apply the UP047 fix,
any module importing `units.py` (the whole documents pipeline) fails collection on 3.11 with
`SyntaxError: expected '('`. `# noqa` is prohibited by the task, and UP047 has no non-PEP-695 fix.

**How to apply:** ruff parses independently of the runtime, so `python -m ruff check .` verifies exit
0 on 3.11 against the shipped PEP 695 code. For pytest, do the temp-revert dance: (1) temporarily
restore the semantically-identical bounded-`TypeVar` form (`_UnitT = TypeVar("_UnitT",
bound=enum.Enum)` + `from typing import TypeVar` + `def _match_unit(unit_enum: type[_UnitT], ...)`),
(2) run `python -m pytest tests/documents/ -q` to prove green, (3) re-apply the PEP 695 form as the
shipped state and re-run `ruff check .` for exit 0. On CI (3.12) both hold together. Report this as a
producer-sandbox limitation (authoritative 3.12 pytest is an orchestrator/CI capture), never a code
defect. The two forms are the identical generic function; ruff's UP047 treats them as the same upgrade.
