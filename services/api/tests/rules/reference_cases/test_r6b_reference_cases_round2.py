"""Round-2 acceptance tests for the R6B reference cases (M4-T030, review F2 and F3).

F2 - one current expected answer per question: a row kept as the historical record
of what an earlier pair of readers could settle carries ``superseded_by``; the
loader does not hand it out as current, and the checker validates the links.

F3 - sentences that are time-true: no case file states in the present tense that a
text is "not captured" / "uncaptured" / "the repository does not hold"; such wording
survives only in change-log sentences that describe a rewording.

Deterministic and engine-free; nothing here imports the rule or scenario engine.
"""
from __future__ import annotations

import copy
import pathlib
import sys

import pytest

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_lib as lib  # noqa: E402
import r6b_reference_cases_step_p3 as step_p3  # noqa: E402

# Every superseded row and the current row(s) that hold its question's answer.
SUPERSEDED = [
    ("step-p1-worked", "interior-40x100-rear-yard",
     ["step-p3-worked#interior-40x100-rear-yard"]),
    ("step-p1-worked", "through-40x200-rear-yard",
     ["step-p3-worked#through-40x200-rear-yard-equivalent"]),
    ("step-p1-worked", "special-density-real-lot",
     ["step-p3-worked#manhattan-core", "step-p3-worked#special-downtown-brooklyn-district"]),
    ("step-p1-worked", "corner-150x100-rear-yard",
     ["step-p3-worked#corner-150x100-rear-yard-beyond-corner"]),
    ("corner-reach", "real-lot-rear-yard",
     ["step-p3-worked#real-lot-rear-yard-beyond-corner"]),
    ("corner-reach", "C3-rear-yard",
     ["step-p3-worked#corner-150x100-rear-yard-beyond-corner"]),
    ("real-lot", "L12", ["step-p3-worked#real-lot-rear-yard-beyond-corner"]),
    ("overlay-reading", "section-35-633",
     ["step-p3-worked#zr-23-436-paragraphs", "step-p3-worked#zr-35-633-paragraphs"]),
    ("overlay-reading", "floor-area-ratio", ["step-p4-worked#floor-area-ratio"]),
    ("overlay-reading", "lot-coverage", ["step-p4-worked#lot-coverage"]),
    ("overlay-reading", "rear-yard", ["step-p4-worked#rear-yard"]),
]

FORBIDDEN_PRESENT_TENSE = (
    "does not hold", "is not captured", "are not captured", "not captured", "uncaptured",
)


def test_superseded_links_validate_clean():
    assert step_p3.superseded_by_errors(lib.load_case, lib.CASE_IDS) == []


def test_superseded_rows_are_refused_by_the_loader_and_name_the_current_row():
    for case_id, row_id, targets in SUPERSEDED:
        with pytest.raises(lib.RowSuperseded) as exc:
            lib.load_row(case_id, row_id)
        message = str(exc.value)
        for target in targets:
            assert target in message, f"{case_id}/{row_id}: loader did not name {target}"
        # read on purpose: the historical row is returned and still carries its link
        historical = lib.load_row(case_id, row_id, allow_superseded=True)
        assert historical["superseded_by"] == targets
        assert historical["kind"] in lib.EXPECTED_KINDS


def test_current_rows_are_not_superseded():
    # a target row must not itself be superseded (checked by the checker, confirmed here)
    for _case_id, _row_id, targets in SUPERSEDED:
        for target in targets:
            tcase, trow = target.split("#", 1)
            row = lib.find_row_or_none(tcase, trow)
            assert row is not None, target
            assert not row.get("superseded_by"), f"{target} is itself superseded"


def test_a_superseded_by_pointing_nowhere_is_refused():
    cases = copy.deepcopy(lib.load_all())
    cases["real-lot"]["rows"][0]["superseded_by"] = ["step-p3-worked#no-such-row"]
    errs = step_p3.superseded_by_errors(lambda cid: cases[cid], lib.CASE_IDS)
    assert errs and any("does not exist" in m for m in errs), errs


def test_a_target_that_is_itself_superseded_is_refused():
    cases = copy.deepcopy(lib.load_all())
    cases["real-lot"]["rows"][0]["superseded_by"] = ["step-p1-worked#interior-40x100-rear-yard"]
    errs = step_p3.superseded_by_errors(lambda cid: cases[cid], lib.CASE_IDS)
    assert errs and any("itself superseded" in m for m in errs), errs


def test_a_row_that_supersedes_itself_is_refused():
    cases = copy.deepcopy(lib.load_all())
    for row in cases["real-lot"]["rows"]:
        if row["row_id"] == "L1":
            row["superseded_by"] = ["real-lot#L1"]
    errs = step_p3.superseded_by_errors(lambda cid: cases[cid], lib.CASE_IDS)
    assert errs and any("cannot supersede itself" in m for m in errs), errs


def test_present_tense_not_captured_wording_only_in_change_log():
    """F3: no case file says a text 'is not captured' / 'uncaptured' / 'the
    repository does not hold' in the present tense outside a change-log entry."""
    violations: list[tuple[str, str, str]] = []

    def walk(node, path, case_id):
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, path + [str(key)], case_id)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, path + [str(i)], case_id)
        elif isinstance(node, str):
            low = node.lower()
            if any(p in low for p in FORBIDDEN_PRESENT_TENSE) and "change_log" not in path:
                violations.append((case_id, "/".join(path), node[:90]))

    for case_id in lib.CASE_IDS:
        walk(lib.load_case(case_id), [], case_id)
    assert violations == [], violations
