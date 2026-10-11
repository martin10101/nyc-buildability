"""M5-T159 (D-094 R027): the report's evidence-page law links go to the EXACT
Zoning Resolution section URL from the repository's own captures - never the
homepage, never a guessed URL. Scenarios S1-S6 of the packet.

Expected URLs are read from the law-capture files (the snapshot ``request_url``)
and from whatever sections the fixture actually makes the page render - NOT from
hard-coded counts or URL strings. Other wave-23 tasks (M5-T157, M5-T158) change
the shared benchmark fixture, so nothing here may depend on how many values it
shows. The evidence page is built through the real report builder; its hrefs are
parsed from the output.
"""

from __future__ import annotations

import json
import re
from collections import Counter
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

# Local parsers (independent of the module under test) so the oracle never derives
# its expectations from law_links / sources.
_PAGE_RE = re.compile(r"\d{1,3}-\d{1,4}")


def _benchmark() -> dict:
    return json.loads(_FIXTURE.read_text("utf-8"))


def _capture_request_url(snapshot_id: str) -> str:
    """The ``source.request_url`` recorded by one capture file."""
    data = json.loads((_CAPTURE_DIR / f"{snapshot_id}.snapshot.json").read_text("utf-8"))
    return data["source"]["request_url"]


def _evidence_html(results: dict) -> str:
    html = build_report_html(results)
    return html[html.index('id="calculations-evidence"'):]


def _law_hrefs(evidence: str) -> list[str]:
    return re.findall(r'<a href="([^"]+)"', evidence)


def _last_segment(url: str) -> str:
    return url.split("#", 1)[0].rstrip("/").rsplit("/", 1)[-1]


def _visible_of(citation: object) -> str:
    """The visible section text, sub-paragraph kept (e.g. ``"ZR 23-52(b)"`` ->
    ``"23-52(b)"``)."""
    text = str(citation or "").strip()
    return text[2:].strip() if text.upper().startswith("ZR") else text


def _page_of(visible: str) -> str:
    """The bare section page of a visible number (sub-paragraph dropped)."""
    match = _PAGE_RE.match(visible)
    return match.group(0) if match else ""


def _rendered_citations(results: dict) -> list[str]:
    """Every section citation the evidence page actually renders, in document order:
    the two figure blocks' non-withheld values - exactly what the page iterates."""
    citations: list[str] = []
    for block in ("floor_area_allowance", "permitted_envelope"):
        for row in readers.present_values(readers.answer_block(results, block)):
            citations.extend(row.get("zr_sections", []))
    return citations


def _capture_section_url(page: str) -> str | None:
    """INDEPENDENT oracle: scan the capture files and return the official
    section-PAGE URL a capture records for ``page`` (its own ``request_url`` on the
    official host, ending at that section), or ``None`` when no capture records one -
    in which case the section must print as plain text. No URL is typed here."""
    if not page:
        return None
    for path in sorted(_CAPTURE_DIR.glob("*.snapshot.json")):
        url = json.loads(path.read_text("utf-8")).get("source", {}).get("request_url", "")
        if (
            url.startswith(_HOST + "/article-")
            and "?" not in url
            and "@" not in url
            and _last_segment(url) == page
        ):
            return url
    return None


# ----------------------------------------------------------------- S1
def test_s1_every_rendered_section_links_to_its_capture_or_prints_plain() -> None:
    """S1: every law href is the exact captured section URL whose last path segment
    equals the cited section; a section with no capture prints as plain text; no href
    is the homepage. Derived from the fixture + captures, independent of counts."""
    results = _benchmark()
    evidence = _evidence_html(results)
    citations = _rendered_citations(results)
    assert citations, "the benchmark evidence page must cite at least one section"

    expected_links: list[str] = []
    for citation in citations:
        visible = _visible_of(citation)
        page = _page_of(visible)
        url = _capture_section_url(page)
        label = (f'New York City Zoning Resolution, Section '
                 f'<span class="nowrap">{visible}</span>')
        if url:
            assert url != _HOMEPAGE
            assert _last_segment(url) == page          # last path segment == section
            assert f'<a href="{url}">{label}</a>' in evidence  # exactly this link form
            expected_links.append(url)
        else:
            assert label in evidence                   # printed ...
            assert f'{label}</a>' not in evidence       # ... as plain text, no link

    hrefs = _law_hrefs(evidence)
    assert _HOMEPAGE not in hrefs
    # No extra or missing links: the hrefs are exactly the valid captured sections.
    assert Counter(hrefs) == Counter(expected_links)


def test_s1_known_sections_link_or_print_plain_from_captures() -> None:
    """The specific sections the orchestrator named: 23-22, 23-52 (incl. from
    23-52(b)) and 23-432 link to their section pages; 11-25 (captured only on the
    wrong host) is plain text. Every expected URL is read from the capture files."""
    evidence = _evidence_html(_benchmark())
    for page, visible in (("23-22", "23-22"), ("23-52", "23-52"),
                          ("23-52", "23-52(b)"), ("23-432", "23-432")):
        url = _capture_section_url(page)
        assert url is not None and _last_segment(url) == page
        label = (f'New York City Zoning Resolution, Section '
                 f'<span class="nowrap">{visible}</span>')
        assert f'<a href="{url}">{label}</a>' in evidence

    assert _capture_section_url("11-25") is None  # only a wrong-host capture exists
    assert '<span class="nowrap">11-25</span>' in evidence
    assert '11-25</span></a>' not in evidence     # plain text, never linked


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
    """S6: only the link targets change - every rendered section's visible label is
    intact and the hrefs are exactly the captured section URLs, never the homepage.
    Derived from the fixture + captures, so it survives later fixture changes."""
    results = _benchmark()
    evidence = _evidence_html(results)
    citations = _rendered_citations(results)

    # Visible labels intact (no figure, label or other text moved).
    for citation in citations:
        assert (f'New York City Zoning Resolution, Section '
                f'<span class="nowrap">{_visible_of(citation)}</span>') in evidence

    pages = {_page_of(_visible_of(citation)) for citation in citations}
    expected = {url for url in (_capture_section_url(page) for page in pages) if url}
    hrefs = set(_law_hrefs(evidence))
    assert hrefs == expected
    assert _HOMEPAGE not in hrefs
    assert expected, "at least one rendered section must link to a captured URL"


def test_s6_homepage_constant_is_gone_from_page_evidence() -> None:
    assert not hasattr(page_evidence, "_LAW_URL")
