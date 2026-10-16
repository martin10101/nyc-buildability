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

Real prints live OUTSIDE git: S2/S3 (and the A1 wrap regression) read them from
``REPORT_CHECK_FIXTURES`` and FAIL (never skip) when a required file is missing. The folder and
the LF sha256 list are in the producer report; byte-level pinning of those fixtures is the
orchestrator's fixture-management step, not asserted here.
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
# the real current-main print wraps this 40-hex commit across two PDF lines (G4 finding 1)
WRAP_COMMIT = "065e3fb55457e1c4c3b06768e5179a6e1f1b662a"
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
    """S1: every rule PASS except the explicitly-owed D-rule gaps (D5 and the D6 dark-pixel
    sub-check are not implemented and say so; D6 clipping-only is REVIEW, never PASS), so a
    consistent bundle exits 3, never a silent all-green 0 (code-review finding 1 / G4 finding 3)."""

    def test_s1_only_d5_d6_gaps_exit_three(self):
        out = Path(tempfile.mkdtemp(prefix="rec-s1-out-"))
        args = _args(_BUNDLE_DIR, out)
        code = rec.run(args)
        report = json.loads((out / "check.json").read_text())
        non_pass = sorted((r["rule"], r["verdict"]) for r in report["results"]
                          if r["verdict"] != rec.PASS)
        # the ONLY non-PASS rows on a consistent bundle are the surfaced D5/D6 gaps
        self.assertEqual(non_pass, [("D5", rec.OWED), ("D6", rec.OWED), ("D6", rec.REVIEW)],
                         f"expected only the D5/D6 gaps, got {non_pass}")
        self.assertEqual(code, 3)
        self.assertTrue((out / "check.md").read_text().startswith(rec.FIRST_LINE))
        self.assertTrue((out / "drawings-visible.md").exists())
        self.assertTrue((out / "pages.txt").exists())

    def test_d5_d6_owed_lines_pinned(self):
        # finding 1 / G4 finding 3: the unimplemented sub-checks are surfaced, D6 never PASS here
        rep = run_group(rec.rules_d, load(_BUNDLE_DIR), False)
        rows = {(r.rule, r.verdict, r.detail) for r in rep.results}
        self.assertIn(("D5", rec.OWED, "not implemented -- figure/caption page attribution"), rows)
        self.assertIn(("D6", rec.OWED, "dark-pixel subcheck not implemented"), rows)
        self.assertNotIn(rec.PASS, {v for ru, v, _ in rows if ru == "D6"})


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

    def test_lot_area_midpoint_fails_c4(self):
        # G4 finding 4: the midpoint of the recorded (10,075) and GIS (10,387.99) lot areas is a
        # reconciled figure the report must never print; the pair is read from the reference case.
        b = load(_BUNDLE_DIR)
        b.pdf.page_text[0] += " lot area 10,231.50 sq ft "
        self.assertEqual(verdicts(run_group(rec.rules_c, b), "C4"), {rec.FAIL})

    def test_drawn_zone_geometry_0898_fails_b5(self):
        # G4 finding 2: a drawn apartment zone at 0.898 of the footprint against a 0.60 share must
        # FAIL on the measured geometry -- WITH and WITHOUT the stamped data-apartment-fraction.
        for stamp in (0.6, None):
            b = load(_BUNDLE_DIR)
            svg = next(s for s in b.html.svgs if "area_zone_apartment" in s.roles)
            svg.fraction = stamp
            svg.shapes = [("area_footprint", 196 * 120, True),
                          ("area_zone_apartment", 176 * 120, True),   # 176/196 = 0.898
                          ("area_zone_other", 20 * 120, True)]
            self.assertEqual(verdicts(run_group(rec.rules_b, b), "B5"), {rec.FAIL},
                             f"stamp={stamp}")

    def test_unmeasurable_zone_path_is_review_not_pass(self):
        # a curve/arc path the shoelace cannot measure must REVIEW (never a false PASS)
        b = load(_BUNDLE_DIR)
        svg = next(s for s in b.html.svgs if "area_zone_apartment" in s.roles)
        svg.fraction = None
        svg.shapes = [("area_zone_apartment", None, False),
                      ("area_zone_other", None, False)]
        self.assertEqual(verdicts(run_group(rec.rules_b, b), "B5"), {rec.REVIEW})

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


class WritesUnderOut(unittest.TestCase):
    """Round-2 finding 2: _page_images renders into a private temp dir, never beside the bundle
    PDF, so the tool writes nothing into the --bundle folder -- even a read-only one."""

    def test_page_images_render_outside_a_readonly_bundle(self):
        import shutil
        folder = Path(tempfile.mkdtemp(prefix="rec-ro-"))
        (folder / "report.pdf").write_bytes((_BUNDLE_DIR / "report.pdf").read_bytes())
        before = {p.name for p in folder.iterdir()}
        captured: dict = {}
        real_run = rec._run

        def spy(cmd, **kw):
            if cmd and cmd[0] == "pdftoppm":
                captured["prefix"] = cmd[-1]
            return real_run(cmd, **kw)

        os.chmod(folder, 0o500)   # read-only bundle dir (blocks the old beside-the-pdf write)
        rec._run = spy
        try:
            facts = rec.extract_pdf(folder / "report.pdf")
        finally:
            rec._run = real_run
            os.chmod(folder, 0o700)
        # the render prefix is NOT inside the bundle folder ...
        self.assertIn("prefix", captured)
        self.assertNotIn(folder.resolve(), Path(captured["prefix"]).resolve().parents)
        # ... and the bundle folder gained no file (no report-gchk-*.png residue) ...
        self.assertEqual({p.name for p in folder.iterdir()}, before)
        # ... while the per-page hashes are still produced
        self.assertTrue(facts.images)
        shutil.rmtree(folder, ignore_errors=True)


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


class S9A1Wrap(unittest.TestCase):
    """A1 must reconstruct a 40-hex commit wrapped across PDF lines (G4 finding 1). The real
    current-main print wraps 'Code commit:' as '065e3fb55457e1c4c3b067' then '68e5179a6e1f1b662a';
    the un-fixed regex captured only the first run and FALSE-FAILED the correct candidate."""

    def test_a1_joins_a_wrapped_commit_unit(self):
        low = ("appendix code commit: 065e3fb55457e1c4c3b067 68e5179a6e1f1b662a "
               "results revision: 1 document fingerprint: 4fcfe7a6f915 recorded-data")
        self.assertEqual(rec._printed_commit(low), WRAP_COMMIT)
        self.assertEqual(rec._printed_commit("code commit: unknown document fingerprint: abcdef"),
                         "")

    def _wrap_pdf(self):
        root = os.environ.get("REPORT_CHECK_FIXTURES")
        if not root:
            self.fail("REPORT_CHECK_FIXTURES unset; the wrapped-commit print must be provided")
        pdf = Path(root).parent / "print-main-065e3fb5" / "report.pdf"
        if not pdf.exists():
            self.fail(f"missing wrapped-commit regression fixture {pdf}")
        work = Path(tempfile.mkdtemp(prefix="rec-wrap-"))
        local = work / "report.pdf"
        local.write_bytes(pdf.read_bytes())
        return rec.extract_pdf(local)

    def test_a1_passes_the_real_wrapped_print_at_its_own_commit(self):
        b = _Fake(self._wrap_pdf(), rec.ReportHtml())
        for sha, want in ((WRAP_COMMIT, rec.PASS), (SHA, rec.FAIL)):
            rep = rec.Report()
            rec.rules_a(rep, b, rec.load_repo(REPO), sha, None)
            self.assertEqual(verdicts(rep, "A1"), {want}, f"sha={sha[:12]}")


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
