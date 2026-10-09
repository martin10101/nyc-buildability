"""Competitor-error guard checks, Lane E outputs side (D-090 source-025, R147-R150).

PENDING tests for the two Lane-E E-items from the 215-16 Northern competitor review
(``docs/COMPETITOR_REVIEW_ENVELOPE_215-16_NORTHERN_2026-09-28.md``; guards table
``docs/plans/COMPETITOR_ERROR_GUARDS_2026-10-04.md``) whose feature is not built:

- E13 (elevator / core statements match the drawings; C-5): there is no
  elevator / building-core producer yet, so nothing can disagree with a drawing.
- E18 (no copy-paste options with mismatched heights / floors; C-5, C-6): no
  multi-option report is produced over the Northern path yet.

Both are the queued E-06 consistency sweep over a rendered multi-page report, which
depends on the unbuilt report builder (E-04). Each stays skipped so CI is green and
the intent is executable once the feature lands. Recorded 215-16 Northern data would
feed them; see the docstrings for the assertion to come.
"""

from __future__ import annotations

import pytest

# --- E13: elevator / core statements match the drawings (C-5) - NOT BUILT YET (E-06) ----


@pytest.mark.skip(reason="NOT BUILT YET: E-06 (C-5) - no elevator/building-core producer "
                         "(M5 scenario engine) and no report to sweep; nothing to compare yet.")
def test_e13_elevator_and_core_statements_match_the_drawings() -> None:
    """E13: when a building-core / elevator producer and the E-06 consistency sweep
    exist, a report that states 'walk-up (no elevator)' must not draw an elevator or
    an elevator bulkhead anywhere (the competitor's every-scenario contradiction).
    Assertion to come, on the recorded 215-16 Northern report:

        sweep = consistency_sweep(render_report(northern_results))
        assert sweep.elevator_statement_matches_drawings is True
    """
    pytest.fail("E-06 not built: no elevator/core statement or sweep exists")


# --- E18: no copy-paste options with mismatched heights/floors (C-5, C-6) - E-06 --------


@pytest.mark.skip(reason="NOT BUILT YET: E-06 (C-5, C-6) - no multi-option report is "
                         "produced over the Northern path, so no cross-option sweep runs.")
def test_e18_no_copy_paste_options_with_mismatched_heights_or_floors() -> None:
    """E18: when multiple options reach a rendered report and the E-06 sweep runs,
    no two options may draw the same building while stating different heights or
    floor counts (the competitor's scenario 1 = 4 floors / 45 ft vs scenarios 2-3 =
    3 floors / 38 ft for the same building). Assertion to come:

        sweep = consistency_sweep(render_report(northern_multi_option_results))
        assert sweep.no_option_shows_conflicting_height_or_floor_count is True
    """
    pytest.fail("E-06 not built: no multi-option report or cross-page sweep exists")
