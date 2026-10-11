"""M5-T162: the report's legal apartment limit open item and the 'Legal unit
limits' coverage line follow the results document (after M5-T157 made the
standard-residence limit a Conditional ceiling).

One test per input state (benchmark; all withheld; none withheld; only one
withheld; a malformed/absent allowance block) plus the S5 guard. Every expected
reason and resolver is read from the document, never retyped from a program run;
the composed effect and coverage note follow the packet's scenarios S1-S5.
"""

from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

from app.drawings.report import build_report_html, coverage, readers

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)

_STANDARD = "legal_unit_limit_standard"
_AFFORDABLE = "legal_unit_limit_qualifying_affordable"
_SENIOR = "legal_unit_limit_qualifying_senior"

_EFFECT_NONE = "No legal apartment limit is shown."
_COVERAGE_WITHHELD = "the legal unit limit is withheld"


def benchmark() -> dict:
    return json.loads(
        (_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8")
    )


def _fa_states(doc: dict) -> dict:
    return doc["answers"]["floor_area_allowance"]["value_states"]


def _visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<script.*?</script>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def _legal_item(doc: dict) -> dict | None:
    for item in readers.open_items(doc):
        if item["category"] == "legal_unit_limit":
            return item
    return None


def _coverage_f(doc: dict) -> dict:
    for entry in coverage.coverage_entries(doc):
        if entry["name"] == "Legal unit limits":
            return entry
    raise AssertionError("no 'Legal unit limits' coverage entry")


# --------------------------------------------------------------------------- S1
def test_s1_benchmark_standard_shown_affordable_and_senior_withheld() -> None:
    doc = benchmark()
    affordable = _fa_states(doc)[_AFFORDABLE]
    senior = _fa_states(doc)[_SENIOR]

    item = _legal_item(doc)
    assert item is not None
    assert item["title"] == "Legal apartment limit"
    assert item["effect"] == (
        "The legal apartment limit is shown as a conditional ceiling for standard residences; "
        "it is not known for qualifying affordable housing or qualifying senior housing."
    )
    # the reason row keeps EACH withheld limit's own reason, labelled by program.
    assert "Qualifying affordable housing: " in item["reason"]
    assert "Qualifying senior housing: " in item["reason"]
    assert affordable["reason"] in item["reason"]
    assert senior["reason"] in item["reason"]
    # the resolver names each (they differ): both are kept, labelled by program.
    assert affordable["resolved_by"] in item["resolves"]
    assert senior["resolved_by"] in item["resolves"]
    # the derivation number is NOT repeated in the effect/reason text.
    assert "29" not in item["effect"]


# --------------------------------------------------------------------------- S2
def test_s2_every_limit_withheld_says_none_shown() -> None:
    doc = benchmark()
    # make the standard limit withheld too: no legal dwelling-unit limit is shown.
    _fa_states(doc)[_STANDARD] = {
        "way": "withheld",
        "label": "Legal dwelling-unit limit, standard residences",
        "reason": "The standard-residence limit is not known in this synthetic state.",
        "gap_kind": "work_owed",
        "resolved_by": "Working the standard-residence limit and checking it against an example.",
        "zr_sections": ["ZR 23-52"],
    }
    assert readers.shown_legal_unit_limit_programs(doc) == []
    item = _legal_item(doc)
    assert item is not None
    assert item["effect"] == _EFFECT_NONE
    assert _coverage_f(doc)["state"] == coverage.NOT_YET


# --------------------------------------------------------------------------- S3
def test_s3_no_withheld_means_no_open_item() -> None:
    doc = benchmark()
    states = _fa_states(doc)
    del states[_AFFORDABLE]
    del states[_SENIOR]
    assert readers.shown_legal_unit_limit_programs(doc) == ["standard residences"]
    assert _legal_item(doc) is None
    # a shown limit still reads 'Partly' in the coverage list (S4), not 'Not yet'.
    assert _coverage_f(doc)["state"] == coverage.PARTLY


# ----------------------------------------------------------------------- one withheld
def test_only_one_withheld_names_the_single_program() -> None:
    doc = benchmark()
    states = _fa_states(doc)
    affordable = dict(states[_AFFORDABLE])
    del states[_SENIOR]
    item = _legal_item(doc)
    assert item is not None
    assert item["effect"] == (
        "The legal apartment limit is shown as a conditional ceiling for standard residences; "
        "it is not known for qualifying affordable housing."
    )
    assert "qualifying senior housing" not in item["effect"]
    assert item["reason"] == f"Qualifying affordable housing: {affordable['reason']}"
    assert item["resolves"] == f"Qualifying affordable housing: {affordable['resolved_by']}"


# ----------------------------------------------------------------- malformed/absent block
def test_malformed_or_absent_allowance_block_is_not_shown() -> None:
    doc = benchmark()
    # a malformed answer block (not a mapping) must read as NOT shown and give no open item,
    # without a truthiness test on the optional block.
    doc["answers"]["floor_area_allowance"] = "malformed"
    assert readers.shown_legal_unit_limit_programs(doc) == []
    assert _legal_item(doc) is None
    assert _coverage_f(doc)["state"] == coverage.NOT_YET

    absent = benchmark()
    del absent["answers"]["floor_area_allowance"]
    assert readers.shown_legal_unit_limit_programs(absent) == []
    assert _legal_item(absent) is None


# --------------------------------------------------------------------------- S4
def test_s4_coverage_partly_names_the_shown_limit_as_conditional() -> None:
    doc = benchmark()
    entry = _coverage_f(doc)
    assert entry["state"] == coverage.PARTLY
    assert entry["note"] == (
        "the limit for standard residences is shown as a conditional ceiling"
    )
    assert _COVERAGE_WITHHELD not in entry["note"]


# --------------------------------------------------------------------------- S5 guard
def test_s5_guard_no_denial_while_a_limit_is_shown() -> None:
    doc = benchmark()
    assert readers.shown_legal_unit_limit_programs(doc)  # a limit is shown
    html = build_report_html(doc)
    text = _visible_text(html)
    assert _EFFECT_NONE not in text
    assert _COVERAGE_WITHHELD not in text
    # on the decision summary (most important open items) and the open-items page alike.
    decision = _visible_text(
        html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    )
    open_items_page = _visible_text(
        html[html.index('id="assumptions-open-items"'):html.index('id="calculations-evidence"')]
    )
    for slice_text in (decision, open_items_page):
        assert _EFFECT_NONE not in slice_text
        assert _COVERAGE_WITHHELD not in slice_text
