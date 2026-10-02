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
  versions. The other three groups - zoning-lot history, map-based rules, and site shape
  and street - are later B-09 slices.

Library only: no route. Lane C wires the flag layer into the study and a contract; Lane D
renders it beside the affected results (plan section 5a, D-12).
"""

from app.profile.hidden_issue_flags.allowance import AsOfRightAllowance
from app.profile.hidden_issue_flags.existing_building import (
    GROUP_ID,
    GROUP_TITLE,
    existing_building_group,
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

__all__ = [
    "GROUP_ID",
    "GROUP_TITLE",
    "LABELS",
    "STATUSES",
    "STATUS_CHECK_NEEDED",
    "STATUS_FLAG",
    "STATUS_NOT_FLAGGED",
    "STATUS_OPPORTUNITY",
    "AsOfRightAllowance",
    "FlagGroup",
    "HiddenIssueFlag",
    "existing_building_group",
]
