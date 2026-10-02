"""§8a hidden-issue flag layer, group by group (queue item B-09; plan L-11, section 8a).

Plan ``docs/PRODUCT_PLAN_CURRENT_2026-09-28.md`` section 8a: hidden issues and
opportunities checked on every property, each "shown as a flag, an opportunity, or 'Check
needed' when the data is not available" - a missing source is always "Check needed", never
a guess.

- ``model``: the shared flag layer - :class:`HiddenIssueFlag` and :class:`FlagGroup`, and
  the status vocabulary (``flag`` / ``opportunity`` / ``check_needed`` / ``not_flagged``).
- ``allowance``: :class:`AsOfRightAllowance`, the engine's as-of-right allowance carried in
  as an input (this package computes no allowance and interprets no rule).
- ``existing_building``: the first group built, the §8a existing-building group
  (:func:`existing_building_group`), reusing B-05 existing floor area and B-06 data
  versions.
- ``zoning_lot_history``: the §8a zoning-lot-history group (:func:`zoning_lot_history_group`),
  flag only (plan P-2) - it reminds the architect what recorded sources (B-05 DOB zoning-lot
  mentions, recorded ACRIS index metadata) are on file to check, or says the source is not
  connected; it never verifies, concludes or computes anything.
- ``map_based_rules``: the §8a map-based-rules group (:func:`map_based_rules_group`), reading
  the recorded PLUTO map-based columns (overlays, special districts, split-zone, Mandatory
  Inclusionary Housing flags, flood flags, landmark / historic district) through the shared
  ``read_pluto_value`` reader; each item is a flag, "No flag" (``splitzone`` recorded false)
  or "Check needed" (unrecorded source / absent categorical column), never a decided rule.
  The remaining group - site shape and street - is a later B-09 slice.

Library only: no route. Lane C wires the flag layer into the study and a contract; Lane D
renders it beside the affected results (plan section 5a, D-12).
"""

from app.profile.hidden_issue_flags.allowance import AsOfRightAllowance
from app.profile.hidden_issue_flags.existing_building import (
    GROUP_ID,
    GROUP_TITLE,
    existing_building_group,
)
from app.profile.hidden_issue_flags.map_based_rules import (
    GROUP_ID as MAP_BASED_GROUP_ID,
)
from app.profile.hidden_issue_flags.map_based_rules import (
    GROUP_TITLE as MAP_BASED_GROUP_TITLE,
)
from app.profile.hidden_issue_flags.map_based_rules import (
    map_based_rules_group,
)
from app.profile.hidden_issue_flags.model import (
    LABELS,
    STATUS_CHECK_NEEDED,
    STATUS_FLAG,
    STATUS_NOT_FLAGGED,
    STATUS_OPPORTUNITY,
    STATUSES,
    FlagGroup,
    HiddenIssueFlag,
)
from app.profile.hidden_issue_flags.zoning_lot_history import (
    GROUP_ID as ZONING_LOT_GROUP_ID,
)
from app.profile.hidden_issue_flags.zoning_lot_history import (
    GROUP_TITLE as ZONING_LOT_GROUP_TITLE,
)
from app.profile.hidden_issue_flags.zoning_lot_history import (
    RECORD_KEYS,
    zoning_lot_history_group,
)

__all__ = [
    "GROUP_ID",
    "GROUP_TITLE",
    "LABELS",
    "MAP_BASED_GROUP_ID",
    "MAP_BASED_GROUP_TITLE",
    "RECORD_KEYS",
    "STATUSES",
    "STATUS_CHECK_NEEDED",
    "STATUS_FLAG",
    "STATUS_NOT_FLAGGED",
    "STATUS_OPPORTUNITY",
    "ZONING_LOT_GROUP_ID",
    "ZONING_LOT_GROUP_TITLE",
    "AsOfRightAllowance",
    "FlagGroup",
    "HiddenIssueFlag",
    "existing_building_group",
    "map_based_rules_group",
    "zoning_lot_history_group",
]
