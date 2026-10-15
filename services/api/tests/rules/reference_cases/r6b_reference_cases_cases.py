#!/usr/bin/env python3
"""Case-module dispatch + reading-digest aggregation for the R6B reference cases (M5-T186).

Pure stdlib. The step-P9, step-P10 and step-P11 case modules share the exact same two
public entries - ``case_errors(case_id, data)`` and ``reading_digest_errors()`` - so the
checker aggregates them here through ONE registry loop instead of a hard-coded call per
module. Extracting the dispatch gives the checker durable headroom under its 600-line cap
(CLAUDE.md principle 16; docs/CODE_MODULARITY_POLICY.md) without weakening the guard: a
later benchmark-options case adds ONE entry to :data:`CASE_MODULES` and nothing in the
checker. The step modules are re-exported here so the checker and its tests keep reaching
them as ``check.step_p9`` etc. (a thin compatibility facade). Nothing here imports the
checker, so there is no cycle.
"""
from __future__ import annotations

import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_step_p9 as step_p9  # noqa: E402
import r6b_reference_cases_step_p10 as step_p10  # noqa: E402
import r6b_reference_cases_step_p11 as step_p11  # noqa: E402

# The case modules that share the uniform (case_errors + reading_digest_errors) interface,
# in case order (step_p9 -> step_p10 -> step_p11). Each module no-ops for a case that is
# not its own, so the order only fixes the message order on a failure.
CASE_MODULES = (step_p9, step_p10, step_p11)


def case_errors(case_id: str, data: dict) -> list[str]:
    """Every uniform-interface case module's per-row/per-case guards, aggregated in order.
    Each module returns [] for a case that is not its own."""
    errs: list[str] = []
    for module in CASE_MODULES:
        errs += module.case_errors(case_id, data)
    return errs


def reading_digest_errors() -> list[str]:
    """Every uniform-interface case module's new reading files are present unchanged,
    aggregated in order (S1)."""
    errs: list[str] = []
    for module in CASE_MODULES:
        errs += module.reading_digest_errors()
    return errs
