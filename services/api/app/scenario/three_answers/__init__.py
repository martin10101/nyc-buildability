"""Three-answer generator (task A-04, plan M1-14 / C-2 / C-11; directive D-090).

Library-only. From the benchmark-style inputs and the Lane A draft rule tables, it computes
the three SEPARATE answers - the floor-area allowance, the permitted envelope, and the
building option (floor stack, floor-by-floor table, computed shortfall reason) - the unit
estimate in one place, and ONE geometry block in feet, and emits a results-v1 document that
validates against the bundled ``results`` schema.

Everything runs behind ``LANE_A_ENABLED`` (off in production). No network, connector, or file
I/O; pure computation over the inputs plus the Lane A rule registry. Nothing is ever Verified:
every rule result is DRAFT and the document is marked ``draft`` (D-090-R010).

Public API:

- :func:`generate_results` - build and validate the results-v1 document for one option.
- :class:`ThreeAnswerInputs`, :class:`BuildingDefaults`, :class:`Assumption` - typed inputs.
- :class:`ThreeAnswersResult` - the document plus its stated, named assumptions.
- :func:`compute_building_option` / :class:`BuildingOptionComputation` - the pure floor-stack
  and shortfall math (feet), for direct testing.
- :func:`validate_results_document` / :class:`ResultsContractError` - strict schema validation.
"""

from __future__ import annotations

from .building_option import (
    BuildingOptionComputation,
    BuildingOptionResult,
    compute_building_option,
    shortfall_reason,
)
from .contract import ResultsContractError, validate_results_document
from .duplicates import (
    find_duplicate_options,
    merge_or_explain,
    option_identity_key,
)
from .engine import (
    CONTRACT_VERSION,
    LOT_SELECTION_STATEMENT,
    REMAINING_NOT_CONFIRMED_REASON,
    ThreeAnswersResult,
    generate_results,
)
from .explanations import build_status_strip, site_measurement_status_chip
from .inputs import (
    DEFAULT_FLOOR_TO_FLOOR_FT,
    Assumption,
    BuildingDefaults,
    ThreeAnswerInputs,
)

__all__ = [
    "CONTRACT_VERSION",
    "DEFAULT_FLOOR_TO_FLOOR_FT",
    "LOT_SELECTION_STATEMENT",
    "REMAINING_NOT_CONFIRMED_REASON",
    "Assumption",
    "BuildingDefaults",
    "BuildingOptionComputation",
    "BuildingOptionResult",
    "ResultsContractError",
    "ThreeAnswerInputs",
    "ThreeAnswersResult",
    "build_status_strip",
    "compute_building_option",
    "find_duplicate_options",
    "generate_results",
    "merge_or_explain",
    "option_identity_key",
    "shortfall_reason",
    "site_measurement_status_chip",
    "validate_results_document",
]
