"""Standing text-budget and benchmark-wording tests for the report (M5-T165).

These own the report's standing budget (S7) and the benchmark-text assertions
moved here from test_report_pages.py:378 (now the rear-yard open check). The caps
are the figures fixed at this task's G0 and the contract's text budget
(ARCHITECT_PRESENTATION_CONTRACT.md, "Change 2026-10-11", "Checks"):

* page 1 (decision summary) visible words <= 200 (G0; the before set was 327/330);
* total report visible words <= 2,448 (the before set at main b4704161 / base);
* page 1 adds no sentence of eight or more words that appears elsewhere;
* the repeat count (sentences of eight or more words printed twice or more) stays
  at or below the before set (3 distinct, 7 printings) and falls.

Every expected string is quoted from the contract or the records, never a program run.
"""

from __future__ import annotations

import html as _html
import json
import re
from collections import Counter
from pathlib import Path

from app.drawings.report import build_report_html, constraint_text, readers, zoning_lot_item

_FIXTURES = (
    Path(__file__).resolve().parents[5]
    / "packages" / "contracts" / "fixtures" / "valid" / "results"
)

# --- budget caps (G0 for page 1; the contract before set for the total and repeats) -------
PAGE_ONE_WORD_CAP = 200
TOTAL_WORD_CAP = 2448
REPEAT_DISTINCT_CAP = 3   # before set: 3 sentences of 8+ words printed 2+ times
REPEAT_PRINTING_CAP = 7   # before set: 7 printings of those sentences

_SECTION_IDS = (
    "decision-summary", "site-and-context", "option-comparison",
    "scenario-B", "assumptions-open-items", "calculations-evidence",
)


def benchmark() -> dict:
    return json.loads((_FIXTURES / "recorded_215_16_northern_journey.json").read_text("utf-8"))


def visible_text(markup: str) -> str:
    markup = re.sub(r"<style.*?</style>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<script.*?</script>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<[^>]+>", " ", markup)
    return _html.unescape(markup)


def _section_bounds(html: str) -> list[tuple[str, int, int]]:
    positions = sorted((html.index(f'id="{sid}"'), sid) for sid in _SECTION_IDS)
    out = []
    for i, (start, sid) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(html)
        out.append((sid, start, end))
    return out


def _word_count(markup: str) -> int:
    return len(visible_text(markup).split())


def _long_sentences(text: str, min_words: int = 8) -> list[str]:
    flat = " ".join(visible_text(text).split())
    parts = re.split(r"(?<=[.!?])\s+", flat)
    return [" ".join(p.split()) for p in parts if len(p.split()) >= min_words]


# =========================================================================== S7
def test_s7_page_one_section_is_within_the_word_cap() -> None:
    html = build_report_html(benchmark())
    for sid, start, end in _section_bounds(html):
        if sid == "decision-summary":
            words = _word_count(html[start:end])
            assert words <= PAGE_ONE_WORD_CAP, f"page 1 has {words} words (cap {PAGE_ONE_WORD_CAP})"
            return
    raise AssertionError("decision-summary section not found")


def test_s7_total_report_is_within_the_word_cap() -> None:
    html = build_report_html(benchmark())
    total = _word_count(html)
    assert total <= TOTAL_WORD_CAP, f"report has {total} words (cap {TOTAL_WORD_CAP})"


def test_s7_page_one_adds_no_eight_word_sentence_found_elsewhere() -> None:
    html = build_report_html(benchmark())
    page_one = html[html.index('id="decision-summary"'):html.index('id="site-and-context"')]
    rest = html[html.index('id="site-and-context"'):]
    rest_text = " ".join(visible_text(rest).split())
    for sentence in _long_sentences(page_one):
        assert sentence not in rest_text, f"page-1 sentence repeated elsewhere: {sentence[:70]!r}"


def test_s7_repeat_count_stays_at_or_below_the_before_set() -> None:
    html = build_report_html(benchmark())
    counts = Counter(_long_sentences(html))
    repeated = {s: n for s, n in counts.items() if n >= 2}
    distinct = len(repeated)
    printings = sum(repeated.values())
    assert distinct <= REPEAT_DISTINCT_CAP, f"{distinct} distinct repeated: {list(repeated)}"
    assert printings <= REPEAT_PRINTING_CAP, f"{printings} total printings: {repeated}"


# ================================================= moved benchmark-text assertion (was :378)
def test_benchmark_rear_yard_reads_as_the_applied_conditional_result() -> None:
    # Was test_benchmark_rear_yard_reads_as_the_open_check. M5-T167 (scope correction 2,
    # R039/R136): the regenerated benchmark now carries the engine's 1.5.0 rear_yard block,
    # so the page-8 appendix rear-yard open item reads the APPLIED ZR 23-344 result, not the
    # "not yet checked" open check. The expected result is the reference case's not-known /
    # Conditional real-lot answer (docs/reference-cases/R6B/short-block-rear-yard.md,
    # real-lot-z1/z2): labelled Conditional, naming ZR 23-344(b) and (c)(3) with the section
    # linked, the conditions named, never an unconditional "no rear yard".
    html = build_report_html(benchmark())
    appendix = html[
        html.index('id="assumptions-open-items"'):html.index('id="calculations-evidence"')
    ]
    # the rear-yard open item is numbered by the reader; locate its row (not program wording).
    number = {it["category"]: it["number"] for it in readers.open_items(benchmark())}["rear_yard"]
    row = appendix[appendix.index(f'id="issue-{number}"'):]
    row = row[:row.index("</tr>")]
    row_text = visible_text(row)
    # the applied conditional reading, no longer the open check; the old wording is gone.
    assert "rear yard is not known beyond the corner area" not in row_text
    assert constraint_text.REAR_YARD_OPEN_CHECK not in visible_text(appendix)
    assert "is not yet checked" not in row_text
    # names the short-block rule (b) and the adjoining-side-line rule (c)(3).
    assert "23-344(b)" in row_text and "23-344(c)(3)" in row_text
    # labelled Conditional (the engine's combined way), not the 1.4.0 open-check label.
    assert 'class="label-chip">Conditional</span>' in row
    # the conditions that settle it are named (the adjoining lots' lot lines).
    assert "lot lines" in row_text
    # never an unconditional "no rear yard".
    low = row_text.lower()
    assert "no rear yard" not in low or "no rear yard is required within 100 feet" in low
    # ZR 23-344 is linked to its captured official text where the reading is shown (pages 1/3).
    assert 'href="https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-344"' in html


# ===================================== M5-T167 round 4 (R136): page 6 agrees with page 8 (1.5.0)
def test_round4_benchmark_page_6_drops_the_rear_yard_pre_check_line() -> None:
    """Round 4 (R136): on the 1.5.0 benchmark (the engine applied ZR 23-344) the building method's
    "what was not checked" list on page 6 no longer carries the corner-lot pre-check line "The rear
    yard beyond the corner" - the reading is shown at the lot level (page 8 reads the conditional
    result, test_benchmark_rear_yard_reads_as_the_applied_conditional_result). So page 6 and page 8
    agree. The companion 1.4.0 render (page 6 KEEPS the line, page 8 shows the open check) is in
    tests/scenario/three_answers/test_three_answers_three_way_emit.py."""
    doc = benchmark()
    assert doc["contract_version"] == "1.5.0"  # the regenerated benchmark applied ZR 23-344
    html = build_report_html(doc)
    # page 6 (the building option / "scenario-B" section) drops the pre-check line everywhere.
    assert "The rear yard beyond the corner" not in visible_text(html)
    # the building alternatives' stored not_checked lists carry only the three base items.
    for alt in doc.get("building_alternatives", []):
        assert "The rear yard beyond the corner" not in alt["not_checked"]
    # page 8 is NOT the "not yet checked" open check (it reads the applied conditional result).
    appendix = html[
        html.index('id="assumptions-open-items"'):html.index('id="calculations-evidence"')
    ]
    assert constraint_text.REAR_YARD_OPEN_CHECK not in visible_text(appendix)


# =========================================================================== S13
def test_s13_moved_effect_texts_keep_their_1_4_0_output_except_the_rear_yard() -> None:
    # The constraint effect texts moved from readers.py to constraint_text.py keep their
    # 1.4.0 output byte-for-byte, EXCEPT lot_area (GIS label fix, S18) and rear_yard (the open
    # check, S19). These are the unchanged ones.
    assert constraint_text.effect_for("coverage") == "The square-foot coverage figure is withheld."
    assert constraint_text.effect_for("placement") == (
        "Where the building sits on the lot is not worked out."
    )
    assert constraint_text.effect_for("setback") == "The setback above the base is not worked out."
    assert constraint_text.effect_for("street_wall") == "The street wall is not checked."
    assert constraint_text.effect_for("parking") == (
        "Parking, loading and bicycle requirements are not checked."
    )
    # the zoning-lot structural effect moved to zoning_lot_item, also unchanged.
    assert zoning_lot_item.ZONING_LOT_EFFECT == (
        "The floor area, the apartment limit and the building option are worked for this tax "
        "lot alone; recorded documents may name it with another lot."
    )
    # an unknown category invents no text.
    assert constraint_text.effect_for("made_up_category") == ""


# =========================================================================== M5-T170 S10
def test_m5t170_page_8_shows_the_applied_envelope_readings() -> None:
    # On the regenerated 1.5.0 benchmark the page-8 appendix shows the engine's applied envelope
    # readings for the setback, street wall and side yard - NOT "not checked" / "not worked out" -
    # so page 8 agrees with the page-3 constraints table and page 6 (which drops "The street
    # wall"). This pins readers._apply_envelope_open_items (M5-T170).
    items = {it["category"]: it for it in readers.open_items(benchmark())}
    for category in ("setback", "street_wall", "side_yard"):
        assert category in items, f"page 8 must list the {category} reading"
        effect = items[category]["effect"].lower()
        assert "not checked" not in effect, category
        assert "not worked out" not in effect, category
        assert "not yet" not in effect, category
    assert "setback above the base" in items["setback"]["effect"].lower()
    assert "street wall" in items["street_wall"]["effect"].lower()
    assert "side yard" in items["side_yard"]["effect"].lower()
    # the "The street wall" not-checked line is gone from the worked building (page 6 / 8 agree).
    for building in readers.worked_buildings(benchmark()):
        assert "The street wall" not in (building.get("not_checked") or [])


def test_m5t170_page_8_side_yard_effect_follows_the_row_state() -> None:
    # G4 advisory 3: the page-8 side-yard effect follows the row state (like the setback branch),
    # so a detached building without the overlay (state=applies, two 5-ft yards) cannot contradict
    # page 3. The shipped benchmark side yard is not_applicable, so its print is unchanged.
    applies = readers._envelope_open_effect("side_yard", {"state": "applies"})
    not_applicable = readers._envelope_open_effect("side_yard", {"state": "not_applicable"})
    assert "two side yards" in applies.lower()
    assert "23-335(a)" in applies
    assert "no side yard is required" in not_applicable.lower()
    assert applies != not_applicable  # the effect is NOT state-invariant


# =========================================================================== S17
def test_s17_long_apartment_estimate_sentence_prints_once() -> None:
    doc = benchmark()
    text = " ".join(visible_text(build_report_html(doc)).split()).lower()
    estimate = readers.apartment_estimate_text(doc["building_alternatives"][0]["capacity_estimate"])
    assert estimate is not None
    assert text.count(estimate.lower()) == 1
