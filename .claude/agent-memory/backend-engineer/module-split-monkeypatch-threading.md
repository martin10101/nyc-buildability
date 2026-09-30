---
name: module-split-monkeypatch-threading
description: How to split a production module whose tests monkeypatch its globals (in-process mutant seam) without breaking them or creating an import cycle; plus modularity_check scope and the drawings 3.11 shim
metadata:
  type: feedback
---

Splitting a module whose test suite installs in-process mutants by `monkeypatch.setattr(mod, "X", ...)`
on module-level constants/functions (the "resolved from this module's globals at call time" seam —
e.g. `services/api/app/drawings/sheet_reader.py`, M5-T094).

**Rule:** keep the FACADE as the single authoritative patch surface and THREAD the patched values into
the extracted modules at the public-entry call time (read the facade globals inside `read_sheet`, pass
them into the coordinator/decoder as instance attributes/limits). The extracted modules then read
`self._interp.<hook>` / `self.<limit>`, never their own globals. Patching the facade still bites, and
there is NO facade↔impl runtime import cycle.

- **Why:** the forbidden 37-test file rebinds `sheet_reader._flatten_cubic`, `_concat_matrix`,
  `_decode_stream`, `_catalog_pages_root`, and every `MAX_*` and asserts behaviour changes. If the
  extracted code read its OWN module globals, the facade patch would not reach it. If the extracted
  module imported the facade at runtime to read them, that's a cycle. Threading captures the facade
  global at `read_sheet` entry (after the patch is set) → both problems solved.
- **How to apply:** any future split of these profile readers (the C1 packet grows `sheet_objects`).
  Keep bound-embedding refusal detail strings using the THREADED value (`f"over {limits.max_...}"`),
  or a patched-low budget case will diverge from the pre-split golden. Prove byte-identical with a
  serialized+sha256 corpus captured from the PRE-split module BEFORE editing (see [[env-producer-sandbox-no-exec]]).
- A parameter annotation that must reference a class moved to the facade → use a
  `if TYPE_CHECKING: from app.drawings.sheet_reader import _SheetInterpreter` back-ref; type-only, no
  runtime cycle, ruff-clean.

**modularity_check.py scope (verified M5-T094):** `--check` enforces SLOC (WARN 600 / JUSTIFY 750 /
HARD 1000) and reports symbol counts — it does NOT detect import cycles. "Acyclic imports" in an
acceptance scenario is a reviewer/design check, not machine-enforced. A NEW file >600 SLOC emits a
`review_signal` warning (not a failure); a baseline-absent file only FAILS above HARD 1000. Test files
(`test_*`) are excluded from the census.

**drawings/extraction tests on local 3.11:** raw `pytest` fails at collection — `app/documents/
extraction/__init__.py` transitively imports PEP 695 syntax (`def _match_unit[UnitT: enum.Enum]`,
3.12-only). Run via a bare-package shim that registers `app`, `app.documents`,
`app.documents.extraction`, `app.drawings` as `types.ModuleType` with `__path__` set (skips the heavy
`__init__`) so the 3.11-safe strict-reader leaves load. The dispatch-referenced
`scratchpad/run_sheet_tests_ctl24.py` did NOT exist in-repo; author it fresh in scratch each time.
