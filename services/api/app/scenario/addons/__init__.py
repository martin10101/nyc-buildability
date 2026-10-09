"""Add-on model for the three-answer generator (task A-06, plan section 6 and section 5
'Best combination'; M1-25; directive D-090).

The catalogue is data (:mod:`catalogue`); the recalculation, gains and 'Best combination'
search are pure functions over the accepted Lane A rules (:mod:`recalculation`). Automatic
add-ons are always applied; optional switches start off and recalculate together; gains are
differences between recalculated outcomes, never summed; 'Best combination' is an exhaustive,
deterministic search over Groups A and B only, with every exclusion computed.

Public API:

- :func:`build_addon_results` - the three results-v1 slots (addon_gains, best_combination,
  completeness_line) for one option.
- :class:`AddOn`, :func:`build_catalogue`, :func:`conflicts` - the catalogue and its computed
  exclusions.
- :func:`base_values`, :func:`outcome_for_selection`, :func:`addon_gains`,
  :func:`best_combination`, :func:`completeness_line` - the recalculation primitives, for tests.
"""

from __future__ import annotations

from .catalogue import (
    GROUP_A,
    GROUP_B,
    GROUP_C,
    GROUP_D1,
    GROUP_D2,
    QUALIFYING_PROGRAMS,
    AddOn,
    build_catalogue,
    conflicting_input_keys,
    conflicts,
    is_available,
    optional_group_a_b,
    unavailable_reason,
)
from .recalculation import (
    BaseValues,
    SelectionOutcome,
    addon_gain_entry,
    addon_gains,
    base_values,
    best_combination,
    build_addon_results,
    completeness_line,
    effective_program,
    goal_value_sf,
    outcome_for_selection,
)

__all__ = [
    "GROUP_A",
    "GROUP_B",
    "GROUP_C",
    "GROUP_D1",
    "GROUP_D2",
    "QUALIFYING_PROGRAMS",
    "AddOn",
    "BaseValues",
    "SelectionOutcome",
    "addon_gain_entry",
    "addon_gains",
    "base_values",
    "best_combination",
    "build_addon_results",
    "build_catalogue",
    "completeness_line",
    "conflicting_input_keys",
    "conflicts",
    "effective_program",
    "goal_value_sf",
    "is_available",
    "optional_group_a_b",
    "outcome_for_selection",
    "unavailable_reason",
]
