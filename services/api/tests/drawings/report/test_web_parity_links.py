"""Web/PDF parity golden for the exact-section law links (M5-T206; D-094 R027/R246).

The website's law-link resolver (apps/web/src/lib/architect/zr-section-urls.ts) ports
the report's own ``law_links.section_url``/``_section_index`` and
``sources.zr_section_page_number`` so the two surfaces resolve every Zoning Resolution
citation to the SAME exact-section URL, and a citation with no captured section shows as
plain text on both (D-094 R027: a link resolves to its exact current section, never the
host homepage; R246: website and PDF agree, same source bases).

This test writes the golden FROM the server code (never by hand): the full
section-page -> URL index, and the ``zr_section_page_number`` / ``section_url`` output for
a pinned case table (the forms the report carries, plus blank/forbidden probes). The web
tests read the SAME golden and assert the TypeScript port reproduces ``ZR_SECTION_URLS``
and every case; editing one golden number reddens both surfaces.

Regenerate after a server or snapshot change with ``UPDATE_GOLDEN=1`` (the golden stays the
server output; the committed ``ZR_SECTION_URLS`` map must then be re-emitted to match).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.drawings.report import law_links, sources

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
GOLDEN = REPO / "apps" / "web" / "src" / "test-support" / "report-parity-law-links.json"

# Citations in the forms the report carries, plus blank/forbidden probes, pinned so the
# TypeScript port is proven against the server's own output (not a hand-typed expectation).
# ``None`` and ``123`` round-trip through JSON as null and a number for the web side.
_PAGE_CASES: list[object] = [
    "ZR 23-52(b)",
    "12-10",
    "ZR 23-344(c)(3)",
    "ZR 23-362",
    None,
    123,
    "",
    "Appendix A",
    "New York City Zoning Resolution (official text)",
    "ZR 11-25",
    # A section number buried after other text must yield "" on BOTH surfaces: the parse is
    # start-anchored (Python re.match; the website's start-anchored regex). This case pins
    # that anchoring in the golden, so dropping the website's leading anchor reddens the web
    # tests and any future server anchoring change reddens this parity test.
    "see 23-52",
]

# section_url cases: resolvable citations, a citation whose page has no capture (ZR 11-25 ->
# null), and the bare host (-> null, never a homepage link).
_URL_CASES: list[object] = [
    "23-362",
    "12-10",
    "ZR 23-52(b)",
    "ZR 11-25",
    "https://zoningresolution.planning.nyc.gov/",
]


def _compute_golden() -> dict:
    index = dict(law_links._section_index())
    page_cases = [
        {"cited": cited, "page": sources.zr_section_page_number(cited)} for cited in _PAGE_CASES
    ]
    url_cases = [{"cited": cited, "url": law_links.section_url(cited)} for cited in _URL_CASES]
    return {
        "section_index": index,
        "page_number_cases": page_cases,
        "section_url_cases": url_cases,
    }


def test_web_parity_law_links_golden_matches_server() -> None:
    computed = _compute_golden()
    if os.environ.get("UPDATE_GOLDEN") == "1":
        GOLDEN.write_text(json.dumps(computed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert golden == computed, (
        "golden drifted from the server law-link code; regenerate with UPDATE_GOLDEN=1 "
        "(and re-emit apps/web/src/lib/architect/zr-section-urls.ts to match):\n"
        + json.dumps(computed, indent=2, sort_keys=True)
    )


def test_section_index_is_the_capture_set_and_resolves_the_report_citations() -> None:
    """The index is the captured section pages, and the report's page-8 citations resolve to
    their exact section URL (never the host homepage)."""
    index = dict(law_links._section_index())
    assert index, "the capture set resolved to an empty index"
    # Every captured URL is an exact section URL (last path segment == its page key), never
    # the bare host or a chapter-only link.
    for page, url in index.items():
        assert law_links.official_zoning_text_url(url) == url, (page, url)
        assert url.rstrip("/").rsplit("/", 1)[-1] == page, (page, url)
    # the three page-8 citations the PDF links resolve to their exact sections.
    assert law_links.section_url("ZR 23-362") == index["23-362"]
    assert law_links.section_url("ZR 12-10") == index["12-10"]
    assert law_links.section_url("ZR 23-52(b)") == index["23-52"]
    # a citation whose page has no capture shows as plain text (null), matching the PDF.
    assert law_links.section_url("ZR 11-25") is None
