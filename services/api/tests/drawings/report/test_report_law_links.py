"""M5-T159 (D-094 R027): the report's evidence-page law links go to the EXACT
Zoning Resolution section URL from the repository's own captures - never the
homepage, never a guessed URL. Scenarios S1-S6 of the packet.

Expected URLs are read from the law-capture files (the snapshot ``request_url``),
NOT from a program run. The evidence page is built through the real report builder
on the committed benchmark results fixture; its hrefs are parsed from the output.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from app.drawings.report import build_report_html, law_links, page_evidence, readers, sources

_REPO = Path(__file__).resolve().parents[5]
_FIXTURE = (
    _REPO / "packages" / "contracts" / "fixtures" / "valid" / "results"
    / "recorded_215_16_northern_journey.json"
)
# The captures the snapshot loader resolves by default (byte-identical to the docs
# copy, kept in sync by sync_zr_snapshots.py). Expected URLs are read from here.
_CAPTURE_DIR = _REPO / "services" / "api" / "app" / "_zr_snapshots" / "v1"
_HOMEPAGE = "https://zoningresolution.planning.nyc.gov/"
_HOST = "https://zoningresolution.planning.nyc.gov"


def _benchmark() -> dict:
    return json.loads(_FIXTURE.read_text("utf-8"))


def _capture_request_url(snapshot_id: str) -> str:
    """The ``source.request_url`` recorded by a capture file - the expected link."""
    data = json.loads((_CAPTURE_DIR / f"{snapshot_id}.snapshot.json").read_text("utf-8"))
    return data["source"]["request_url"]


def _evidence_html(results: dict) -> str:
    html = build_report_html(results)
    return html[html.index('id="calculations-evidence"'):]


def _law_hrefs(evidence: str) -> list[str]:
    return re.findall(r'<a href="([^"]+)"', evidence)


def _last_segment(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/").rsplit("/", 1)[-1]


def _rendered_pages(results: dict, block_name: str) -> list[str]:
    """The section pages the evidence page actually renders for a block (only the
    non-withheld values are shown - exactly what the page iterates)."""
    pages: list[str] = []
    for row in readers.present_values(readers.answer_block(results, block_name)):
        for section in row.get("zr_sections", []):
            pages.append(sources.zr_section_page_number(section))
    return pages


# ----------------------------------------------------------------- S1
def test_s1_every_href_is_the_exact_section_and_never_the_homepage() -> None:
    results = _benchmark()
    evidence = _evidence_html(results)
    hrefs = _law_hrefs(evidence)

    # The pages the page renders (benchmark: 23-22 x4, 23-432 x6).
    rendered = _rendered_pages(results, "floor_area_allowance") + _rendered_pages(
        results, "permitted_envelope")
    assert rendered, "the benchmark evidence page must cite at least one section"
    assert len(hrefs) == len(rendered)

    expected_by_page = {
        "23-22": _capture_request_url("zr-23-22"),
        "23-432": _capture_request_url("zr-23-432"),
    }
    for href in hrefs:
        assert href != _HOMEPAGE
        # every href is an official article/chapter/section URL ...
        assert href.startswith(_HOST + "/article-")
        page = _last_segment(href)
        # ... whose last path segment equals a cited section number ...
        assert page in rendered
        # ... and equals the URL the capture itself records.
        assert href == expected_by_page[page]


def test_s1_index_never_maps_a_section_to_the_homepage() -> None:
    for cited in ("ZR 23-22", "ZR 23-432", "ZR 23-52", "ZR 12-10", "ZR 23-344"):
        url = law_links.section_url(cited)
        assert url is not None and url != _HOMEPAGE


# ----------------------------------------------------------------- S2
def test_s2_subparagraph_links_to_the_section_page_and_keeps_its_text() -> None:
    expected = _capture_request_url("zr-23-52")
    # The link target drops the sub-paragraph; the visible label keeps it.
    assert law_links.section_url("ZR 23-52(b)") == expected
    assert _last_segment(expected) == "23-52"
    assert sources.zr_section_number("ZR 23-52(b)") == "23-52(b)"

    # Rendered through the real builder: a present value citing 23-52(b).
    results = _benchmark()
    results["answers"]["floor_area_allowance"]["values"][0]["zr_sections"] = ["ZR 23-52(b)"]
    evidence = _evidence_html(results)
    assert f'<a href="{expected}">' in evidence
    assert '23-52(b)</span></a>' in evidence  # the anchor wraps the sub-paragraph text


# ----------------------------------------------------------------- S3
def test_s3_section_with_no_capture_prints_as_plain_text() -> None:
    assert law_links.section_url("ZR 99-99") is None  # no capture, no guessed URL

    results = _benchmark()
    results["answers"]["floor_area_allowance"]["values"][0]["zr_sections"] = ["ZR 99-99"]
    evidence = _evidence_html(results)
    # The label still prints ...
    assert '<span class="nowrap">99-99</span>' in evidence
    # ... but it is NOT wrapped in an anchor (a linked section ends '</span></a>').
    assert '99-99</span></a>' not in evidence
    # and no href points at the uncaptured section.
    assert not any("99-99" in href for href in _law_hrefs(evidence))


# ----------------------------------------------------------------- S4
@pytest.mark.parametrize(
    "url",
    [
        "http://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52",  # not https
        "https://evil.example.com/article-ii/chapter-3/23-52",                  # wrong host
        "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52?x=1",  # query
        "https://zoningresolution.planning.nyc.gov:8443/article-ii/chapter-3/23-52",  # port
        "https://u:p@zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52",   # creds
        "https://zoningresolution.planning.nyc.gov/",                           # homepage
        "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52\\x",  # backslash
        "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23 52",  # space
        "https://zr.planning.nyc.gov/entityprint/pdf/node/18075",              # wrong host + path
        "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52#foo",  # bad anchor
    ],
)
def test_s4_allowlist_rejects_disallowed_urls(url: str) -> None:
    assert law_links.official_zoning_text_url(url) is None


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52",
            "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52",
        ),
        (
            "https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10",
            "https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10",
        ),
        (  # a valid anchor is preserved in canonical form
            "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52#23-52",
            "https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-52#23-52",
        ),
    ],
)
def test_s4_allowlist_accepts_official_section_urls(url: str, expected: str) -> None:
    assert law_links.official_zoning_text_url(url) == expected


def test_s4_every_rendered_href_passes_the_allowlist() -> None:
    evidence = _evidence_html(_benchmark())
    hrefs = _law_hrefs(evidence)
    assert hrefs
    for href in hrefs:
        assert law_links.official_zoning_text_url(href) == href


# ----------------------------------------------------------------- S5
def test_s5_twelve_ten_links_to_the_section_with_an_anchor_only_if_captured() -> None:
    expected = _capture_request_url("zr-12-10")
    assert law_links.section_url("ZR 12-10") == expected
    assert _last_segment(expected) == "12-10"

    # No 12-10 capture records an anchor, so no anchor is added.
    for path in _CAPTURE_DIR.glob("zr-12-10*.snapshot.json"):
        data = json.loads(path.read_text("utf-8"))
        if sources.zr_section_page_number(data.get("section_number", "")) == "12-10":
            assert "#" not in data["source"]["request_url"]
    assert "#" not in law_links.section_url("ZR 12-10")

    # Rendered through the real builder: a present value citing 12-10.
    results = _benchmark()
    results["answers"]["permitted_envelope"]["values"][0]["zr_sections"] = ["ZR 12-10"]
    evidence = _evidence_html(results)
    assert f'<a href="{expected}">' in evidence


# ----------------------------------------------------------------- S6
def test_s6_only_link_targets_change_labels_and_text_stay() -> None:
    evidence = _evidence_html(_benchmark())
    # The visible law labels are unchanged (same wording as before this task) ...
    assert ('New York City Zoning Resolution, Section '
            '<span class="nowrap">23-22</span>') in evidence
    assert ('New York City Zoning Resolution, Section '
            '<span class="nowrap">23-432</span>') in evidence
    # ... only the href targets moved off the homepage onto the exact sections.
    hrefs = _law_hrefs(evidence)
    assert len(hrefs) == 10  # 23-22 x4 + 23-432 x6, as the planner measured
    assert _HOMEPAGE not in hrefs
    assert set(hrefs) == {
        _capture_request_url("zr-23-22"),
        _capture_request_url("zr-23-432"),
    }


def test_s6_homepage_constant_is_gone_from_page_evidence() -> None:
    assert not hasattr(page_evidence, "_LAW_URL")
