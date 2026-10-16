#!/usr/bin/env python3
"""Self-test for tools/report_export_check.py (M0-T197, part A of M0-T195).

Stdlib + unittest, runnable as ``python3 tools/test_report_export_check.py``. It builds a
synthetic CONSISTENT bundle (real HTML printed to a real PDF by apps/web/scripts/
print-report-pdf.mjs, plus results.json, web dumps and roles.json) and proves the check is
green on it (S1), red on one-change mutations (S4), red on the real audited prints (S2, S3),
that its fingerprint equals the product's (S5), that it fails closed on a missing tool or
file (S6) and flags website defects (S7). Heavy work (Chromium print, poppler) runs under the
caller's heavy-run flock -- run as ``flock /root/project/lanes-runtime/heavy-run.lock
python3 tools/test_report_export_check.py``.

Real prints live OUTSIDE git: S2/S3 read them from ``REPORT_CHECK_FIXTURES`` and FAIL (never
skip) when a pinned file is missing or its LF sha256 differs. The folder and sha256 list are
in the producer report so the orchestrator can keep them in the session fixtures folder.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import report_export_check as rec  # noqa: E402

WEB = REPO / "apps/web"
PRINT_SCRIPT = WEB / "scripts/print-report-pdf.mjs"
TOKENS = json.loads((REPO / "docs/design/presentation-tokens.json").read_text("utf-8"))
WORDING = TOKENS["wording"]
SHA = "b7f473690580794265c73a6323908f2ad062cf15"   # a valid 40-hex commit for A1
WIDTHS = (320, 390, 768, 1024, 1440, 1920)

# The results document the synthetic bundle rests on: apartment+other=total, share 0.60,
# placed and fitted, eleven options, plus the four per-run metadata fields (excluded from
# the fingerprint). results.json and the printed fingerprint are derived from THIS object.
RESULTS = {
    "revision": 1, "computed_at": "2026-10-16T00:00:00Z",
    "results_id": "run-1", "option_id": "opt-1", "study_id": "study-1",
    "lot_area": 10075, "tax_clear": 33.34, "gis_clear": 35.31, "unused": 0,
    "building_alternatives": [
        {"placement": {"status": "placed"},
         "area_allocation": {"fitted": True, "share": 0.60, "apartment_area_sqft": 12090,
                             "other_area_sqft": 8060, "total_sqft": 20150}}],
    "options": [{"n": i} for i in range(1, 12)],
}
ROLES = {"footprint_roles": ["area_footprint"],
         "section_legal_line_roles": ["floor_stack_storey", "floor_stack_ff"]}


def _fingerprint() -> str:
    exclude = rec.load_repo(REPO).fingerprint_exclude
    return rec.document_fingerprint(RESULTS, exclude)


def synthetic_html(sha: str, fp: str) -> str:
    """A minimal but internally consistent report: token sizes, page footer, a drawn footprint
    claimed 'Shown on the site plan', the two-zone illustration drawn in proportion, reconciled
    numbers with their bases, the commit, the fingerprint and the data-mode marker."""
    apt, other, cap = WORDING["area_zone_apartment"], WORDING["area_zone_other"], \
        WORDING["area_illustration_caption"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Synthetic consistent report</title>
<style>
@page {{ size: A4 portrait; margin: 14mm;
  @top-left {{ content: "Synthetic \\00B7 block 1, lot 2"; font-size: 8.5pt; }}
  @top-right {{ content: "Preliminary zoning results"; font-size: 8.5pt; }}
  @bottom-left {{ content: "Results revision 1"; font-size: 8.5pt; }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages); font-size: 8.5pt; }} }}
html {{ font-family: Arial, Helvetica, sans-serif; color:#182B3A; }}
body {{ margin:0; font-size:10.5pt; }}
.report-page {{ break-before: page; }}
.report-page:first-of-type {{ break-before: auto; }}
h1 {{ font-size:22pt; margin:0 0 3mm; }}
h2 {{ font-size:14pt; margin:0 0 2mm; }}
.headline {{ font-size:30pt; font-weight:700; }}
svg text {{ font-size:8.5pt; }}
</style></head><body>
<section class="report-page" id="decision-summary">
  <h1>Synthetic consistent report</h1>
  <div class="headline">20,150 sq ft</div>
  <h2>Summary</h2>
  <p>Recorded lot area <span data-source="lot_area">10,075</span> sq ft.</p>
  <p>Clearance <span data-source="tax_clear">33.34 ft, printed tax map</span>;
     <span data-source="gis_clear">35.31 ft, city map outline</span>.</p>
  <svg class="bar-chart" viewBox="0 0 500 60" width="500pt" height="60pt">
    <text data-role="area_footprint" x="0" y="20">Footprint 100.76 ft</text>
    <text data-role="status" x="0" y="45">Shown on the site plan</text>
  </svg>
</section>
<section class="report-page" id="option-comparison">
  <h2>Comparison</h2>
  <table><thead><tr><th>Option</th><th>Result</th></tr></thead>
  <tbody><tr><td>Option 1</td><td>Conditional</td></tr></tbody></table>
</section>
<section class="report-page" id="scenario-B">
  <h2>Scenario</h2>
  <p>It is shown as zones inside the placed building footprint.</p>
  <svg data-drawing="area_allocation" viewBox="0 0 468 260" width="468pt" height="260pt">
    <g data-drawing-part="area_allocation" data-apartment-fraction="0.6">
      <text data-role="area_percentage" x="24" y="30">60% apartment area</text>
      <rect data-role="area_footprint" x="24" y="44" width="196" height="120"></rect>
      <rect data-role="area_zone_apartment" x="24" y="44" width="118" height="120"></rect>
      <rect data-role="area_zone_other" x="142" y="44" width="78" height="120"></rect>
      <line data-role="area_division" x1="142" y1="44" x2="142" y2="164"></line>
      <text data-role="area_label_apartment" x="24" y="190">{apt}</text>
      <text data-role="area_label_other" x="24" y="210">{other}</text>
      <text data-role="caption" x="24" y="236">{cap}</text>
    </g>
  </svg>
</section>
<section class="report-page" id="appendix">
  <h2>Appendix</h2>
  <p>Code commit: {sha}</p>
  <p>Document fingerprint: {fp}</p>
  <p>recorded-data development preview: recorded packs replayed through the engine.</p>
</section>
</body></html>
"""


def write_web(folder: Path, *, state="zones", overflow=False) -> None:
    (folder / "web").mkdir(parents=True, exist_ok=True)
    for w in WIDTHS:
        sw = w + 80 if (overflow and w == 320) else w
        (folder / "web" / f"{w}.json").write_text(json.dumps({
            "width": w, "inner_width": w, "scroll_width": sw, "text": "",
            "area_allocation_state": state}))


def build_bundle(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    fp = _fingerprint()
    (folder / "report.html").write_text(synthetic_html(SHA, fp), "utf-8")
    subprocess.run(["node", str(PRINT_SCRIPT), str(folder / "report.html"),
                    str(folder / "report.pdf")], cwd=str(WEB), check=True, capture_output=True)
    (folder / "results.json").write_text(json.dumps(RESULTS))
    (folder / "roles.json").write_text(json.dumps(ROLES))
    write_web(folder)


_BUNDLE_DIR: Path | None = None


def setUpModule() -> None:
    global _BUNDLE_DIR
    if not PRINT_SCRIPT.exists() or (WEB / "node_modules").exists() is False:
        raise RuntimeError("apps/web/node_modules missing; run `npm ci` in apps/web first")
    _BUNDLE_DIR = Path(tempfile.mkdtemp(prefix="rec-s1-"))
    build_bundle(_BUNDLE_DIR)


def tearDownModule() -> None:
    if _BUNDLE_DIR is not None:
        import shutil
        shutil.rmtree(_BUNDLE_DIR, ignore_errors=True)


def load(folder: Path) -> rec.Bundle:
    return rec.load_bundle(folder, folder / "roles.json", [])


def verdicts(rep: rec.Report, rule: str) -> set[str]:
    return {r.verdict for r in rep.results if r.rule == rule}


def run_group(group, bundle, *extra) -> rec.Report:
    rep = rec.Report()
    group(rep, bundle, rec.load_repo(REPO), *extra)
    return rep


class S1Consistent(unittest.TestCase):
    """S1: every rule PASS, exit 0."""

    def test_s1_all_pass_exit_zero(self):
        out = Path(tempfile.mkdtemp(prefix="rec-s1-out-"))
        args = _args(_BUNDLE_DIR, out)
        code = rec.run(args)
        report = json.loads((out / "check.json").read_text())
        bad = [r for r in report["results"] if r["verdict"] != rec.PASS]
        self.assertEqual(bad, [], f"expected every rule PASS, got {bad}")
        self.assertEqual(code, 0)
        self.assertTrue((out / "check.md").read_text().startswith(rec.FIRST_LINE))
        self.assertTrue((out / "drawings-visible.md").exists())
        self.assertTrue((out / "pages.txt").exists())


class S4Mutations(unittest.TestCase):
    """S4: one-change mutations each turn a rule red; the legitimate zero stays green."""

    def test_zone_fraction_change_fails_b5(self):
        b = load(_BUNDLE_DIR)
        svg = next(s for s in b.html.svgs if "area_zone_apartment" in s.roles)
        svg.fraction = 0.90
        self.assertEqual(verdicts(run_group(rec.rules_b, b), "B5"), {rec.FAIL})

    def test_basis_swap_fails_c4(self):
        b = load(_BUNDLE_DIR)
        b.html.source_texts.append(("gis_clear", "35.31 ft, printed tax map", "other-basis"))
        self.assertEqual(verdicts(run_group(rec.rules_c, b), "C4"), {rec.FAIL})

    def test_inserted_average_fails_c4(self):
        b = load(_BUNDLE_DIR)
        b.pdf.page_text[0] += " clearance 34.33 ft "
        self.assertEqual(verdicts(run_group(rec.rules_c, b), "C4"), {rec.FAIL})

    def test_nan_in_text_fails_c5(self):
        b = load(_BUNDLE_DIR)
        b.web[320]["text"] = "estimate NaN units"
        self.assertEqual(verdicts(run_group(rec.rules_c, b), "C5"), {rec.FAIL})

    def test_null_rendered_zero_fails_c5(self):
        b = load(_BUNDLE_DIR)
        b.results["beds"] = None
        b.html.source_texts.append(("beds", "0", "value"))
        self.assertEqual(verdicts(run_group(rec.rules_c, b), "C5"), {rec.FAIL})

    def test_legitimate_zero_passes(self):
        b = load(_BUNDLE_DIR)
        b.html.source_texts.append(("unused", "0", "value"))  # results.unused == 0
        self.assertEqual(verdicts(run_group(rec.rules_c, b), "C5"), {rec.PASS})
        self.assertNotIn(rec.FAIL, verdicts(run_group(rec.rules_c, b), "C3"))

    def test_option_count_fails_c6(self):
        b = load(_BUNDLE_DIR)
        b.results["options"] = b.results["options"][:10]
        self.assertEqual(verdicts(run_group(rec.rules_c, b), "C6"), {rec.FAIL})


class S5Fingerprint(unittest.TestCase):
    """S5: the recomputed fingerprint equals the product's run_identity.document_fingerprint."""

    def _product(self):
        path = REPO / "services/api/app/drawings/report/run_identity.py"
        spec = importlib.util.spec_from_file_location("product_run_identity", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_matches_product_and_exclusion_parsed(self):
        prod = self._product()
        exclude = rec.load_repo(REPO).fingerprint_exclude
        self.assertEqual(exclude, prod._FINGERPRINT_EXCLUDE)  # read from the file text
        self.assertEqual(rec.document_fingerprint(RESULTS, exclude),
                         prod.document_fingerprint(RESULTS))

    def test_a_value_change_changes_the_fingerprint(self):
        exclude = rec.load_repo(REPO).fingerprint_exclude
        base = rec.document_fingerprint(RESULTS, exclude)
        changed = copy.deepcopy(RESULTS)
        changed["lot_area"] = 9999
        self.assertNotEqual(base, rec.document_fingerprint(changed, exclude))

    def test_per_run_metadata_does_not_change_the_fingerprint(self):
        exclude = rec.load_repo(REPO).fingerprint_exclude
        base = rec.document_fingerprint(RESULTS, exclude)
        other = copy.deepcopy(RESULTS)
        other["results_id"] = "run-2"
        self.assertEqual(base, rec.document_fingerprint(other, exclude))


class S6FailClosed(unittest.TestCase):
    """S6: a missing file or tool exits 2; compressed object streams review the link checks."""

    def test_missing_bundle_file_exits_2(self):
        folder = Path(tempfile.mkdtemp(prefix="rec-missing-"))
        (folder / "report.html").write_text("<html></html>")
        out = Path(tempfile.mkdtemp(prefix="rec-missing-out-"))
        self.assertEqual(rec.main(_argv(folder, out)), 2)

    def test_missing_tool_exits_2(self):
        saved = rec.POPPLER
        rec.POPPLER = (*saved, "poppler_tool_that_does_not_exist")
        try:
            self.assertEqual(rec.main(_argv(_BUNDLE_DIR, Path(tempfile.mkdtemp()))), 2)
        finally:
            rec.POPPLER = saved

    def test_object_streams_review_links(self):
        b = load(_BUNDLE_DIR)
        b.pdf.has_objstm = True
        b.html.hrefs.append("#issue-1")
        rep = rec.Report()
        rec._links(rep, b, False)
        self.assertEqual(verdicts(rep, "D3"), {rec.REVIEW})


class S7Website(unittest.TestCase):
    """S7: horizontal scroll fails E1; a missing illustration while the PDF draws zones is owed;
    'unchanged' only on equal digests."""

    def test_horizontal_scroll_fails_e1(self):
        b = load(_BUNDLE_DIR)
        b.web[320]["scroll_width"] = 480
        rep = rec.Report()
        rec.rules_e(rep, b)
        self.assertEqual(verdicts(rep, "E1"), {rec.FAIL})

    def test_pdf_zones_but_website_absent_is_owed(self):
        b = load(_BUNDLE_DIR)
        for w in WIDTHS:
            b.web[w]["area_allocation_state"] = "absent"
        rep = rec.Report()
        rec.rules_e(rep, b)
        self.assertEqual(verdicts(rep, "E3"), {rec.OWED})

    def test_before_after_unchanged_only_on_equal_digests(self):
        b = load(_BUNDLE_DIR)
        before = b.folder / "before" / "web"
        before.mkdir(parents=True, exist_ok=True)
        same = b.folder / "web" / "320.png"
        same.write_bytes(b"IMG-A")
        (before / "320.png").write_bytes(b"IMG-A")
        (before / "390.png").write_bytes(b"IMG-A")
        (b.folder / "web" / "390.png").write_bytes(b"IMG-B")
        b.before_web = {320: before / "320.png", 390: before / "390.png"}
        rep = rec.Report()
        rec.rules_e(rep, b)
        e4 = [r.detail for r in rep.results if r.rule == "E4"]
        self.assertTrue(any("320px before/after unchanged" in d for d in e4))
        self.assertTrue(any("390px before/after changed" in d for d in e4))


class S2RealHeads(unittest.TestCase):
    """S2: at 8fbf701b (the audited head) B1 and B5 FAIL; at b7f47369 (the honest head) no B1/B5
    FAIL and B3/B7 are OWED. Real prints read from REPORT_CHECK_FIXTURES, fail-not-skip."""

    def _head(self, name: str) -> rec.Bundle:
        root = os.environ.get("REPORT_CHECK_FIXTURES")
        if not root:
            self.fail("REPORT_CHECK_FIXTURES unset; the S2 head prints must be provided")
        folder = Path(root) / name
        for rel in ("report.html", "report.pdf", "results.json", "roles.json"):
            if not (folder / rel).exists():
                self.fail(f"missing pinned fixture {folder / rel}")
        return rec.load_bundle(folder, folder / "roles.json", [])

    def test_audited_head_fails_b1_and_b5(self):
        rep = run_group(rec.rules_b, self._head("head-8fbf701b"))
        self.assertEqual(verdicts(rep, "B1"), {rec.FAIL})
        self.assertEqual(verdicts(rep, "B5"), {rec.FAIL})

    def test_honest_head_is_owed_not_failed(self):
        rep = run_group(rec.rules_b, self._head("head-b7f47369"))
        self.assertNotIn(rec.FAIL, verdicts(rep, "B1"))
        self.assertNotIn(rec.FAIL, verdicts(rep, "B5"))
        self.assertEqual(verdicts(rep, "B3"), {rec.OWED})
        self.assertEqual(verdicts(rep, "B7"), {rec.OWED})


class S3MainPrints(unittest.TestCase):
    """S3: main 86a450d4's prints -- report.pdf fails A1 (commit unknown) and D2 lists the four
    run-together bookmarks and page 4's missing SVG title; the 8-page print fails D7."""

    def _root(self) -> Path:
        root = os.environ.get("REPORT_CHECK_FIXTURES")
        if not root:
            self.fail("REPORT_CHECK_FIXTURES unset; the main 86a450d4 prints must be provided")
        return Path(root) / "main-86a450d4"

    def _pdf(self, name: str) -> rec.PdfFacts:
        pdf = self._root() / name
        if not pdf.exists():
            self.fail(f"missing pinned fixture {pdf}")
        work = Path(tempfile.mkdtemp(prefix="rec-s3-"))
        local = work / "report.pdf"
        local.write_bytes(pdf.read_bytes())
        return rec.extract_pdf(local)

    def _html(self) -> rec.ReportHtml:
        html = self._root() / "report-with-commit.html"
        if not html.exists():
            self.fail(f"missing pinned fixture {html}")
        return rec.parse_html(html)

    def test_commit_unknown_fails_a1(self):
        b = _Fake(self._pdf("report.pdf"), self._html())
        rep = rec.Report()
        rec.rules_a(rep, b, rec.load_repo(REPO), SHA, None)
        self.assertEqual(verdicts(rep, "A1"), {rec.FAIL})

    def test_d2_lists_runtogether_and_missing_title(self):
        b = _Fake(self._pdf("report.pdf"), self._html())
        rep = rec.Report()
        rec._outline_check(rep, b)
        details = " ".join(r.detail for r in rep.results if r.rule == "D2")
        self.assertIn("thisshape", details.replace(" ", ""))
        self.assertIn("Site plan: the lot among its neighbours", details)

    def test_eight_page_print_fails_d7(self):
        b = _Fake(self._pdf("report-with-commit-8-pages.pdf"), rec.ReportHtml())
        rep = rec.Report()
        rec._fonts(rep, b, rec.load_repo(REPO))
        self.assertEqual(verdicts(rep, "D7"), {rec.FAIL})


class _Fake:
    """A minimal bundle carrying just a parsed PDF and HTML for the focused S3 rule calls."""

    def __init__(self, pdf, html):
        self.pdf = pdf
        self.html = html
        self.results: dict = {}
        self.roles: dict = {}
        self.web: dict = {}
        self.phrases: list = []
        self.folder = Path(".")
        self.before_web: dict = {}


def _args(bundle: Path, out: Path):
    import argparse
    ns = argparse.Namespace(bundle=str(bundle), sha=SHA, repo=str(REPO),
                            roles=str(bundle / "roles.json"), phrases=None,
                            out=str(out), fetch_links=False)
    return ns


def _argv(bundle: Path, out: Path):
    return ["--bundle", str(bundle), "--sha", SHA, "--repo", str(REPO),
            "--roles", str(bundle / "roles.json"), "--out", str(out)]


if __name__ == "__main__":
    unittest.main(verbosity=2)
