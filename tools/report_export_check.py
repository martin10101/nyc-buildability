#!/usr/bin/env python3
"""Report export check (part A of M0-T195; design: return-H16-M0-T195 "CHECK DESIGN").

An output-level consistency check over a PRINTED report bundle: it reads the printed PDF,
its HTML source, the website's own results.json and width dumps and reports every claim
that disagrees with what is actually drawn and calculated. Rules yield PASS/FAIL/REVIEW/
OWED with page, data-role and a short quote. Exit 0 all PASS; 1 any FAIL; 3 only REVIEW/
OWED; 2 a tool, file or parse error. Standard library only, plus poppler and, for A2,
node print-report-pdf.mjs; no package, no port, network only with --fetch-links, writes
only under --out. Expected labels/wording/values come from the tokens, contract and
reference cases at --repo and the roles from --roles -- never a product constant.
"""
# Full rule catalogue (A1-A5, B1-B10, C1-C7, D1-D9, E1-E4) is in the design return.
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

FIRST_LINE = "automated consistency check built by an AI agent; not professional verification"
PASS, FAIL, REVIEW, OWED = "PASS", "FAIL", "REVIEW", "OWED"
WIDTHS = (320, 390, 768, 1024, 1440, 1920)
POPPLER = ("pdfinfo", "pdftotext", "pdftohtml", "pdftoppm")
PAGE_W = 594.96                      # A4 width in points
MARGIN_PT = 14.0 * 72.0 / 25.4       # 14 mm content margin
DATA_MODE = "recorded-data development preview"
# claim templates, each with the --repo source file it is taken from and its kind
CLAIMS = [("Shown on the site plan", "footprint_drawn"),
          ("Not demonstrated", "not_placed"),
          ("Worked out; not drawn", "placed_not_drawn"),
          ("as zones inside the placed building footprint", "zones"),
          ("as a proportional bar beside the building diagram", "bar"),
          ("it is not yet drawn in this report", "not_drawn")]
SWEEP = re.compile(r"[^.]*\b(shown|drawn|drawing|site plan|footprint|zone|section|"
                   r"illustrat\w*|see page|page \d+|item \d+)\b[^.]*\.", re.I)


class CheckError(Exception):
    """A tool, input or parse failure. Raised to exit 2; never a silent PASS."""


@dataclass
class Result:
    rule: str
    verdict: str
    detail: str
    page: int | None = None
    role: str | None = None


class Report:
    def __init__(self) -> None:
        self.results: list[Result] = []

    def add(self, rule, verdict, detail, page=None, role=None, quote="") -> None:
        if quote:
            detail = f"{detail}: {quote[:120]!r}"
        self.results.append(Result(rule, verdict, detail, page, role))

    def exit_code(self) -> int:
        verdicts = {r.verdict for r in self.results}
        if FAIL in verdicts:
            return 1
        return 3 if (REVIEW in verdicts or OWED in verdicts) else 0


# --- subprocess / text helpers --------------------------------------------------------

def _run(cmd, *, binary=False, timeout=180):
    try:
        out = subprocess.run(cmd, capture_output=True, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        raise CheckError(f"required tool not found: {cmd[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise CheckError(f"tool timed out: {' '.join(cmd)}") from exc
    if out.returncode != 0 and not out.stdout:
        raise CheckError(f"tool failed: {' '.join(cmd)}\n{out.stderr.decode('utf-8', 'replace')}")
    return out.stdout if binary else out.stdout.decode("utf-8", "replace")


def _unescape(text):
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&#160;", " "),
                 ("&nbsp;", " "), ("&quot;", '"'), ("&#39;", "'")):
        text = text.replace(a, b)
    return text


def _nospace(text):
    return re.sub(r"\s+", "", text).lower()


def _dig(obj, path):
    found, value = _dig2(obj, path)
    return value if found else None


def _dig2(obj, path):
    # (found, value): distinguishes an explicit null from a missing path (C5 null-vs-zero)
    cur = obj
    for key in [p for p in path.strip("/").split("/") if p]:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        elif isinstance(cur, list) and key.lstrip("-").isdigit() and -len(cur) <= int(key) < len(cur):
            cur = cur[int(key)]
        else:
            return False, None
    return True, cur


def _nums(text):
    return [float(t.replace(",", "")) for t in re.findall(r"-?\d[\d,]*\.?\d*", text)]


def document_fingerprint(results, exclude, length=12):
    payload = {k: v for k, v in results.items() if k not in exclude} \
        if isinstance(results, dict) else {}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:max(1, length)]


# --- PDF extraction -------------------------------------------------------------------

@dataclass
class PdfFacts:
    pages: int = 0
    creator: str = ""
    producer: str = ""
    tagged: bool = False
    page_text: list = field(default_factory=list)   # one string per page
    boxes: list = field(default_factory=list)        # per page: [{x0,y0,x1,y1,text}]
    outline: list = field(default_factory=list)      # (page, title) in document order
    font_sizes: list = field(default_factory=list)   # every fontspec size
    dests: dict = field(default_factory=dict)         # name -> page
    urls: list = field(default_factory=list)          # (page, url)
    has_objstm: bool = False
    images: list = field(default_factory=list)        # per page: sha256 of the 110-dpi grey PNG


def extract_pdf(pdf: Path) -> PdfFacts:
    for tool in POPPLER:
        try:
            subprocess.run([tool, "-v"], capture_output=True, check=False)
        except FileNotFoundError as exc:
            raise CheckError(f"required poppler tool missing: {tool}") from exc
    facts = PdfFacts()
    fields = {}
    for line in _run(["pdfinfo", str(pdf)]).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fields[k.strip()] = v.strip()
    facts.pages = int(fields.get("Pages", "0") or 0)
    facts.creator, facts.producer = fields.get("Creator", ""), fields.get("Producer", "")
    facts.tagged = fields.get("Tagged", "").lower() == "yes"
    facts.page_text = _run(["pdftotext", str(pdf), "-"]).split("\f")[:facts.pages or None]
    facts.boxes = _boxes(pdf)
    facts.outline, facts.font_sizes = _outline(pdf)
    facts.dests = _dests(pdf)
    facts.urls = _urls(pdf)
    facts.has_objstm = b"/ObjStm" in pdf.read_bytes()
    facts.images = _page_images(pdf)
    return facts


def _boxes(pdf):
    pages, cur = [], None
    wre = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" '
                     r'yMax="([\d.]+)">(.*?)</word>')
    for line in _run(["pdftotext", "-bbox", str(pdf), "-"]).splitlines():
        if "<page " in line:
            cur = []
            pages.append(cur)
        m = wre.search(line)
        if m and cur is not None:
            cur.append({"x0": float(m[1]), "y0": float(m[2]), "x1": float(m[3]),
                        "y1": float(m[4]), "text": _unescape(m[5])})
    return pages


def _outline(pdf):
    out = _run(["pdftohtml", "-xml", "-i", "-q", "-stdout", "-zoom", "1", str(pdf)])
    outline = [(int(m[1]), _unescape(m[2]).strip())
               for m in re.finditer(r'<item page="(\d+)">(.*?)</item>', out, re.S)]
    sizes = [int(s) for s in re.findall(r'<fontspec id="\d+" size="(\d+)"', out)]
    return outline, sizes


def _dests(pdf):
    dests = {}
    for line in _run(["pdfinfo", "-dests", str(pdf)]).splitlines():
        m = re.match(r'\s*(\d+)\s+\[.*\]\s+"(.+)"\s*$', line)
        if m:
            dests[m[2]] = int(m[1])
    return dests


def _urls(pdf):
    urls = []
    for line in _run(["pdfinfo", "-url", str(pdf)]).splitlines():
        m = re.match(r'\s*(\d+)\s+\w+\s+(\S+)\s*$', line)
        if m and "://" in m[2]:
            urls.append((int(m[1]), m[2]))
    return urls


def _page_images(pdf):
    # render every page to a 110-dpi grey PNG and hash it (pages.txt / D6 reviewer evidence);
    # render into a private temp dir, never beside the PDF, so the tool writes nothing into the
    # --bundle folder (the "writes only under --out" contract; works on a read-only bundle)
    tmp = Path(tempfile.mkdtemp(prefix="report-gchk-"))
    try:
        prefix = str(tmp / "page")
        _run(["pdftoppm", "-r", "110", "-gray", "-png", str(pdf), prefix], binary=True)
        return [hashlib.sha256(png.read_bytes()).hexdigest()
                for png in sorted(tmp.glob("page-*.png"))]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- HTML parsing ---------------------------------------------------------------------

@dataclass
class Svg:
    drawing: str
    section: str
    roles: set = field(default_factory=set)
    texts: list = field(default_factory=list)   # (role, text, source)
    fraction: float | None = None               # kernel-stamped drawn apartment fraction
    shapes: list = field(default_factory=list)   # (role, area|None, measurable: bool)

    def role_text(self, role):
        return [t for r, t, _ in self.texts if r == role]

    def area(self, role):
        # summed drawn area of every MEASURABLE shape carrying this role (rect w*h / shoelace)
        vals = [a for r, a, m in self.shapes if r == role and m and a is not None]
        return sum(vals) if vals else None

    def has_unmeasurable(self, roles):
        # a shape with one of these roles whose geometry could not be measured (curve/arc path)
        want = set(roles)
        return any((r in want) and not m for r, _, m in self.shapes)


def _shape_area(tag, a):
    # (role, area|None, measurable): a <rect> gives width*height; a <path> the shoelace area of
    # its polygon -- any curve/arc/relative command is NOT measurable (-> caller reports REVIEW).
    role = a["data-role"]
    if tag == "rect":
        try:
            return role, abs(float(a.get("width", "")) * float(a.get("height", ""))), True
        except ValueError:
            return role, None, False
    area, ok = _path_area(a.get("d", ""))
    return role, area, ok


def _path_area(d):
    # shoelace area of an absolute M/L/Z polygon path. Any other command (H, V, C, S, Q, T, A,
    # or any lowercase/relative command) is unsupported -> (None, False) so the rule REVIEWs it.
    if not d or not d.strip():
        return None, False
    toks = re.findall(r"[A-Za-z]|-?\d*\.?\d+(?:[eE]-?\d+)?", d)
    pts, i, n = [], 0, len(toks)
    while i < n:
        c = toks[i]
        if re.fullmatch(r"[A-Za-z]", c):
            if c in ("M", "L"):
                try:
                    pts.append((float(toks[i + 1]), float(toks[i + 2])))
                except (IndexError, ValueError):
                    return None, False
                i += 3
            elif c == "Z":
                i += 1
            else:
                return None, False          # H/V/curve/arc or any lowercase (relative) -> REVIEW
        else:                                # an implicit lineto pair continuing an M/L run
            try:
                pts.append((float(toks[i]), float(toks[i + 1])))
            except (IndexError, ValueError):
                return None, False
            i += 2
    if len(pts) < 3:
        return None, False
    s = sum(pts[j][0] * pts[(j + 1) % len(pts)][1] - pts[(j + 1) % len(pts)][0] * pts[j][1]
            for j in range(len(pts)))
    return abs(s) / 2.0, True


_BLOCK = {"p", "div", "li", "td", "th", "tr", "h1", "h2", "h3", "section", "br",
          "ul", "ol", "table", "thead", "tbody", "caption", "span"}


class ReportHtml(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections, self.headings, self.svgs = [], [], []
        self.source_texts, self.ids, self.hrefs, self.tables = [], set(), [], []
        self.text_parts, self.prose_parts = [], []
        self._section, self._svg, self._table, self._in_thead = "", None, None, False
        self._cap, self._cap_meta, self._head, self._level = None, ("", None), None, 0
        self._skip = 0   # inside <style>/<script>: collect no text at all

    def handle_starttag(self, tag, attrs_list):
        a = dict(attrs_list)
        if tag in ("style", "script"):
            self._skip += 1
        if tag in _BLOCK:
            self.text_parts.append(" ")
            self.prose_parts.append(" ")
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "section" and "report-page" in (a.get("class") or ""):
            self._section = a.get("id", "")
            self.sections.append(self._section)
        elif tag == "svg":
            self._svg = Svg(a.get("data-drawing") or a.get("class") or "", self._section)
            self.svgs.append(self._svg)
        elif tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        elif tag == "table":
            self._table = {"has_thead": False, "thead_text": "", "section": self._section}
            self.tables.append(self._table)
        elif tag == "thead" and self._table is not None:
            self._table["has_thead"], self._in_thead = True, True
        elif tag in ("h1", "h2", "h3"):
            self._head, self._level = [], int(tag[1])
        if self._svg is not None and a.get("data-role"):
            self._svg.roles.add(a["data-role"])
            if tag in ("rect", "path"):
                self._svg.shapes.append(_shape_area(tag, a))
        if self._svg is not None and a.get("data-apartment-fraction"):
            try:
                self._svg.fraction = float(a["data-apartment-fraction"])
            except ValueError:
                pass
        if (a.get("data-role") or a.get("data-source")) and tag in (
                "text", "tspan", "span", "td", "div", "p", "li"):
            self._cap, self._cap_meta = [], (a.get("data-role") or "", a.get("data-source"))

    def handle_endtag(self, tag):
        if tag in ("style", "script") and self._skip:
            self._skip -= 1
        if tag in _BLOCK:
            self.text_parts.append(" ")
            self.prose_parts.append(" ")
        if tag == "svg":
            self._svg = None
        elif tag == "thead":
            self._in_thead = False
        elif tag == "table":
            self._table = None
        elif tag in ("h1", "h2", "h3") and self._head is not None:
            self.headings.append((self._level, "".join(self._head).strip(), self._section))
            self._head = None
        if self._cap is not None and tag in (
                "text", "tspan", "span", "td", "div", "p", "li"):
            text, (role, source) = "".join(self._cap).strip(), self._cap_meta
            if text:
                self.source_texts.append((source or "", text, role))
                if self._svg is not None:
                    self._svg.texts.append((role, text, source))
            self._cap = None

    def handle_data(self, data):
        if self._skip:
            return
        self.text_parts.append(data)
        if self._svg is None:        # prose = text outside any SVG (B9 sweeps prose only)
            self.prose_parts.append(data)
        if self._cap is not None:
            self._cap.append(data)
        if self._head is not None:
            self._head.append(data)
        if self._in_thead and self._table is not None:
            self._table["thead_text"] += data

    @property
    def text(self):
        return re.sub(r"\s+", " ", "".join(self.text_parts))

    @property
    def prose(self):
        return re.sub(r"\s+", " ", "".join(self.prose_parts))


def parse_html(path: Path) -> ReportHtml:
    parser = ReportHtml()
    parser.feed(path.read_text("utf-8", "replace"))
    parser.close()
    return parser


# --- repo context + bundle ------------------------------------------------------------

@dataclass
class RepoContext:
    token_pt: dict
    zone_apartment: str
    zone_other: str
    caption: str
    forbidden: list
    fingerprint_exclude: tuple
    clearance: dict          # {"tax": 33.34, "gis": 35.31} from the reference case (no hardcode)
    basis_pairs: list        # [(tax, gis), (recorded_lot_area, gis_lot_area)] for C4 midpoints


def _basis_values(repo: Path):
    # C4 benchmark values come from the reference case, never a product/tool constant: the
    # back-clearance pair (tax-map vs GIS) and the lot-area pair (recorded PLUTO vs GIS outline).
    path = repo / "docs/reference-cases/R6B/cases/placement-building-b.json"
    jtext = path.read_text("utf-8")
    named = {}

    def walk(o):
        if isinstance(o, dict):
            n, v = o.get("name"), o.get("value")
            if isinstance(n, str) and isinstance(v, str):
                named.setdefault(n, v)
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(json.loads(jtext))

    def num(s):
        mt = re.search(r"-?\d[\d,]*\.?\d*", s or "")
        return float(mt.group().replace(",", "")) if mt else None

    tax, gis = num(named.get("tax-map back clearance")), num(named.get("GIS back clearance"))
    rec = re.search(r"([\d,]+)\s+recorded \(PLUTO\)", jtext)
    gisa = re.search(r"measured area ([\d,]+\.\d+)\s+sq ft", jtext)
    recorded = float(rec[1].replace(",", "")) if rec else None
    gis_area = float(gisa[1].replace(",", "")) if gisa else None
    if None in (tax, gis, recorded, gis_area):
        raise CheckError("could not parse the clearance/lot-area basis pair "
                         "from placement-building-b.json")
    return {"tax": tax, "gis": gis}, [(tax, gis), (recorded, gis_area)]


def load_repo(repo: Path) -> RepoContext:
    tokens = json.loads((repo / "docs/design/presentation-tokens.json").read_text("utf-8"))
    t, w = tokens["type"], tokens["wording"]
    contract = (repo / "docs/design/ARCHITECT_PRESENTATION_CONTRACT.md").read_text("utf-8")
    run_id = (repo / "services/api/app/drawings/report/run_identity.py").read_text("utf-8")
    m = re.search(r"The report never uses(.+?)for a result", contract, re.S)
    forbidden = re.findall(r'"([^"]+)"', m[1]) if m else []
    if not forbidden:
        raise CheckError("could not parse the forbidden-word sentence from the contract")
    fm = re.search(r"_FINGERPRINT_EXCLUDE\s*=\s*(\([^)]*\))", run_id)
    if not fm:
        raise CheckError("could not parse _FINGERPRINT_EXCLUDE from run_identity.py")
    clearance, basis_pairs = _basis_values(repo)
    return RepoContext(
        {n: float(t[n]["print_pt"]) for n in ("property-title", "headline-value", "section-title")},
        w["area_zone_apartment"], w["area_zone_other"], w["area_illustration_caption"],
        forbidden, tuple(ast.literal_eval(fm[1])), clearance, basis_pairs)


@dataclass
class Bundle:
    folder: Path
    html: ReportHtml
    pdf: PdfFacts
    results: dict
    web: dict
    roles: dict
    before_web: dict
    phrases: list = field(default_factory=list)


def _require(path: Path) -> Path:
    if not path.exists():
        raise CheckError(f"missing bundle file: {path}")
    return path


def load_bundle(folder: Path, roles_path, phrases) -> Bundle:
    html = parse_html(_require(folder / "report.html"))
    pdf = extract_pdf(_require(folder / "report.pdf"))
    results = json.loads(_require(folder / "results.json").read_text("utf-8"))
    web = {w: json.loads(_require(folder / "web" / f"{w}.json").read_text("utf-8"))
           for w in WIDTHS}
    roles = json.loads(roles_path.read_text("utf-8")) if roles_path and roles_path.exists() else {}
    before_web = {w: folder / "before" / "web" / f"{w}.png" for w in WIDTHS
                  if (folder / "before" / "web" / f"{w}.png").exists()}
    return Bundle(folder, html, pdf, results, web, roles, before_web, phrases or [])


def _svgs_with(b, roles):
    want = set(roles)
    return [s for s in b.html.svgs if s.roles & want]


def _printed_commit(low):
    # A git sha is exactly 40 hex. Chromium can wrap the value across PDF lines, so the
    # whitespace-normalised text splits the 40-hex into runs (A1 design: "joined across line
    # wraps"). Join the hex tokens immediately after "code commit:" up to 40 chars, stopping at
    # the first non-hex token (e.g. "unknown", "results", "document") -- never swallowing the
    # fingerprint or a later field.
    if "code commit:" not in low:
        return ""
    joined = ""
    for tok in low.split("code commit:", 1)[1].split():
        if len(joined) >= 40 or not re.fullmatch(r"[0-9a-f]+", tok):
            break
        joined += tok
    return joined[:40]


# ======================================================================================
#  RULES
# ======================================================================================

def rules_a(rep, b, repo, sha, reprint):
    pdf = b.pdf
    low = re.sub(r"\s+", " ", " ".join(pdf.page_text)).lower()
    printed = _printed_commit(low)
    rep.add("A1", PASS if printed == sha.lower() else FAIL,
            "printed commit equals the candidate" if printed == sha.lower()
            else f"printed commit {printed or 'unknown'} != {sha[:12]}")
    if reprint is None:
        rep.add("A2", REVIEW, "reprint not run (node print-report-pdf.mjs unavailable)")
    else:
        same = (reprint.pages == pdf.pages
                and [_nospace(t) for t in reprint.page_text] == [_nospace(t) for t in pdf.page_text]
                and [(p, _nospace(t)) for p, t in reprint.outline]
                == [(p, _nospace(t)) for p, t in pdf.outline])
        rep.add("A2", PASS if same else FAIL,
                "reprint identical" if same else "reprint differs (edited PDF?)")
    ok = pdf.creator == "Chromium" and pdf.producer.startswith("Skia/PDF") and pdf.tagged
    rep.add("A3", PASS if ok else FAIL,
            f"Creator={pdf.creator!r} Producer={pdf.producer!r} Tagged={pdf.tagged}")
    fp = document_fingerprint(b.results, repo.fingerprint_exclude)
    pm = re.search(r"document fingerprint:\s*([0-9a-f]{6,64})", low)
    rep.add("A4", PASS if pm and pm[1] == fp else FAIL,
            f"recomputed {fp} vs printed {(pm and pm[1]) or 'absent'}")
    rep.add("A5", PASS if DATA_MODE in low else OWED,
            "data-mode marker present" if DATA_MODE in low
            else "no data-mode marker in the PDF")


def rules_b(rep, b, repo):
    html = b.html.text
    placed = (_dig(b.results, "building_alternatives/0/placement/status") == "placed")
    fitted = bool(_dig(b.results, "building_alternatives/0/area_allocation/fitted"))
    fp_roles = b.roles.get("footprint_roles") or []
    footprint = bool(_svgs_with(b, fp_roles)) if fp_roles else False
    zones = _svgs_with(b, ["area_zone_apartment", "area_zone_other"])
    bars = _svgs_with(b, ["area_bar_apartment", "area_bar_other"])
    if "Shown on the site plan" in html:
        if not fp_roles:
            rep.add("B1", REVIEW, "footprint role unknown (no --roles)")
        else:
            _footprint(rep, b, fp_roles)
    if "No building placed" in html:
        rep.add("B2", FAIL if footprint else PASS,
                "legend 'No building placed' while a footprint is drawn" if footprint
                else "legend consistent (no footprint drawn)")
    if "Worked out; not drawn" in html:
        rep.add("B3", FAIL if footprint else (OWED if placed else PASS),
                "'Worked out; not drawn' but a footprint IS drawn" if footprint
                else "placed but footprint not drawn (OWED M5-T173)" if placed
                else "no footprint drawn and none claimed")
    if "Not demonstrated" in html:
        rep.add("B4", PASS if not placed else FAIL,
                "not placed, honestly stated" if not placed else "'Not demonstrated' but placed")
    # "when drawn it will be shown as zones ..." is a NEGATIVE (not-yet-drawn) claim, so the
    # positive zone/bar claims fire only when the not-yet-drawn sentence is absent (design B).
    not_drawn = "it is not yet drawn in this report" in html
    if "as zones inside the placed building footprint" in html and not not_drawn:
        _zones(rep, b, repo, zones, bars)
    if "as a proportional bar beside the building diagram" in html and not not_drawn:
        _bars(rep, b, zones, bars)
    if not_drawn:
        rep.add("B7", FAIL if (zones or bars) else (OWED if fitted else PASS),
                "'not yet drawn' but an illustration IS present" if (zones or bars)
                else "fitted but not drawn (OWED M5-T174)" if fitted else "none drawn, none claimed")
    _sections(rep, b)
    _sweep(rep, b)


def _footprint(rep, b, fp_roles):
    # B1 scoped to the site-plan svg: a footprint role AND its dimension text (a measurement with
    # ink in the vector). Role presence alone is not proof a scaled footprint was drawn, so an
    # undimensioned role is REVIEW, never PASS; no footprint role at all is the audited FAIL.
    svgs = _svgs_with(b, fp_roles)
    if not svgs:
        rep.add("B1", FAIL, "'Shown on the site plan' but no footprint is drawn")
        return
    dim = re.compile(r"\d[\d,]*\.?\d*\s*(?:ft\b|feet\b|')", re.I)
    for s in svgs:
        for _, t, _ in s.texts:
            if dim.search(t):
                rep.add("B1", PASS, "footprint drawn in the site-plan svg with its dimension text",
                        quote=t)
                return
    rep.add("B1", REVIEW,
            "footprint role present but no dimension text; a drawn footprint is not confirmed")


def _area_ratio(svg, apt_role, other_role, fp_role):
    # drawn apartment-area fraction from the measured shapes: apt / footprint, else apt /
    # (apt + other). Returns (ratio, status): "unmeasurable" (a curve/arc path) -> REVIEW;
    # "absent" (no measurable geometry) -> REVIEW; "ok" -> compare to the share.
    roles = [apt_role, other_role] + ([fp_role] if fp_role else [])
    if svg.has_unmeasurable(roles):
        return None, "unmeasurable"
    apt, other = svg.area(apt_role), svg.area(other_role)
    fp = svg.area(fp_role) if fp_role else None
    denom = fp if fp else ((apt + other) if (apt is not None and other is not None) else None)
    if apt is None or not denom:
        return None, "absent"
    return apt / denom, "ok"


def _zone_structural_fail(svg, repo, bars, share):
    missing = {"area_footprint", "area_zone_apartment", "area_zone_other", "area_division"} \
        - svg.roles
    if missing:
        return f"zones drawing missing roles {sorted(missing)}"
    if bars:
        return "both zone and bar roles present"
    labels = {t for _, t, _ in svg.texts}
    if repo.zone_apartment not in labels or repo.zone_other not in labels:
        return "zone labels do not match the token wording"
    caps = [t for _, t, _ in svg.texts if t == repo.caption]
    if len(caps) != 1:
        return f"caption appears {len(caps)} times, expected once"
    if svg.fraction is not None and isinstance(share, (int, float)) \
            and abs(svg.fraction - share) > 0.005:
        return f"drawn apartment fraction {svg.fraction} != share {share}"
    pct_text = svg.role_text("area_percentage")
    pct = round(share * 100) if isinstance(share, (int, float)) else None
    if pct is not None and pct_text and not any(str(pct) in t for t in pct_text):
        return f"percentage {pct_text} != {pct}%"
    return None


def _zones(rep, b, repo, zones, bars):
    if not zones:
        rep.add("B5", FAIL, "zones claimed but no zone roles drawn")
        return
    svg = zones[0]
    share = _dig(b.results, "building_alternatives/0/area_allocation/share")
    fail = _zone_structural_fail(svg, repo, bars, share)
    if fail:
        rep.add("B5", FAIL, fail)
        return
    # the authoritative proportion check: the DRAWN zone area ratio (rect w*h / shoelace), not a
    # stamped attribute. Where the geometry cannot be measured B5 is REVIEW, never a false PASS.
    ratio, status = _area_ratio(svg, "area_zone_apartment", "area_zone_other", "area_footprint")
    if status == "unmeasurable":
        rep.add("B5", REVIEW,
                "zone area not measurable (unsupported path command); drawn proportion not verified")
    elif status != "ok" or not isinstance(share, (int, float)):
        rep.add("B5", REVIEW, "zone geometry or share absent; drawn proportion not measured")
    elif abs(ratio - share) > 0.005:
        rep.add("B5", FAIL, f"drawn zone area ratio {ratio:.4f} != share {share}")
    else:
        rep.add("B5", PASS,
                f"zones backed by roles, labels, one caption and a drawn area ratio {ratio:.4f}")


def _bars(rep, b, zones, bars):
    # B6: the proportional bar must carry both roles (and not co-exist with zones), and its drawn
    # area ratio must equal the share; unmeasurable geometry is REVIEW, never a false PASS.
    if not bars or zones:
        rep.add("B6", FAIL, "bar claimed but missing a bar role or zones are present too")
        return
    svg = bars[0]
    share = _dig(b.results, "building_alternatives/0/area_allocation/share")
    ratio, status = _area_ratio(svg, "area_bar_apartment", "area_bar_other", None)
    if status == "unmeasurable":
        rep.add("B6", REVIEW, "bar area not measurable (unsupported path command); ratio not verified")
    elif status != "ok" or not isinstance(share, (int, float)):
        rep.add("B6", REVIEW, "bar geometry or share absent; drawn ratio not measured")
    elif abs(ratio - share) > 0.005:
        rep.add("B6", FAIL, f"drawn bar ratio {ratio:.4f} != share {share}")
    else:
        rep.add("B6", PASS, f"bar backed by its roles and a drawn area ratio {ratio:.4f} == share")


def _sections(rep, b):
    legal = set(b.roles.get("section_legal_line_roles") or [])
    if "schematic, not to scale" in b.html.text and legal:
        bad = [s for s in _svgs_with(b, list(legal)) if {r for r in s.roles if "scale" in r}]
        rep.add("B8", FAIL if bad else PASS,
                "'schematic, not to scale' but a scale bar is drawn" if bad
                else "section schematic consistent")


def _sweep(rep, b):
    registered = [c[0] for c in CLAIMS]
    stray = []
    for mt in SWEEP.finditer(b.html.prose):
        s = mt.group(0).strip()
        if any(t in s for t in registered):
            continue
        for n in re.findall(r"page (\d+)", s, re.I):
            if int(n) > b.pdf.pages:
                rep.add("B10", REVIEW, f"'page {n}' exceeds the {b.pdf.pages}-page document", quote=s)
        if not re.search(r"page \d+|item \d+", s, re.I):
            stray.append(s)
    if stray:
        for s in stray[:10]:
            rep.add("B9", REVIEW, "unregistered claim sentence", quote=s)
    else:
        rep.add("B9", PASS, "no unregistered claim sentences")


def _averaged_bases(nums, pairs):
    # a value that falls near the MIDPOINT of two distinct-basis figures (strictly between them)
    # is an averaged/reconciled number the report must never print (bases stay separate).
    hits = []
    for lo, hi in pairs:
        mid = (lo + hi) / 2.0
        tol = max(0.03, abs(hi - lo) * 0.05)
        for n in nums:
            if min(lo, hi) < n < max(lo, hi) and abs(n - mid) <= tol:
                hits.append(round(n, 3))
    return sorted(set(hits))


def rules_c(rep, b, repo):
    text = " ".join(b.pdf.page_text)
    web_text = " ".join(w.get("text", "") for w in b.web.values())
    mids = _averaged_bases(_nums(text), repo.basis_pairs)
    tax, gis = f"{repo.clearance['tax']:g}", f"{repo.clearance['gis']:g}"
    swapped = any((tax in t and re.search(r"city map|map outline", t.lower()))
                  or (gis in t and "tax map" in t.lower())
                  for _, t, _ in b.html.source_texts)
    rep.add("C4", FAIL if (mids or swapped) else PASS,
            f"a reconciled midpoint of two measurement bases printed {mids}" if mids
            else "a clearance carries the wrong basis" if swapped
            else "measurement bases labelled distinctly")
    bad = re.search(r"(?<![a-z])(nan|inf|infinity)(?![a-z])", (text + " " + web_text).lower())
    null_zero = [s for s, t, _ in b.html.source_texts
                 if s and not s.startswith("/map_context") and ":" not in s
                 and _dig2(b.results, s) == (True, None) and t.strip() in ("0", "0.0", "0.00")]
    if bad:
        rep.add("C5", FAIL, f"non-finite token printed: {bad[0]!r}")
    elif null_zero:
        rep.add("C5", FAIL, f"a null/absent value printed as 0: {null_zero[:3]}")
    else:
        rep.add("C5", PASS, "no nan/inf token and no null-rendered-as-zero")
    _sources(rep, b)
    _options(rep, b)
    _forbidden(rep, b, repo)
    _schedule(rep, b)


def _sources(rep, b):
    checked, mism = 0, []
    for source, t, _ in b.html.source_texts:
        if not source or source.startswith("/map_context") or ":" in source:
            continue
        val = _dig(b.results, source)
        if val is None:
            continue
        checked += 1
        want, got = _nums(str(val)), _nums(t)
        if want and got and not any(abs(g - want[0]) <= 0.5 for g in got):
            mism.append((source, t))
    if mism:
        for s, t in mism[:8]:
            rep.add("C3", FAIL, f"{s} does not match results", quote=t)
    else:
        rep.add("C3", PASS, f"{checked} data-source figures resolve and match")


def _options(rep, b):
    rows = _dig(b.results, "option_comparison/rows") or _dig(b.results, "options")
    if isinstance(rows, list) and rows:
        rep.add("C6", PASS if len(rows) == 11 else FAIL, f"{len(rows)} option rows (expected 11)")
    elif not any("option" in (tb.get("section") or "") for tb in b.html.tables):
        rep.add("C6", REVIEW, "option comparison not located in this bundle")


def _forbidden(rep, b, repo):
    phrases = list(repo.forbidden) + list(b.phrases)
    hits = []
    for phrase in phrases:
        p = phrase.lower()
        for i, page in enumerate(b.pdf.page_text, start=1):
            if re.search(rf"(?<![a-z]){re.escape(p)}(?![a-z])", page.lower()):
                hits.append((phrase, i))
    if hits:
        for phrase, page in hits[:12]:
            rep.add("C7", FAIL, f"forbidden/internal phrase {phrase!r}", page)
    else:
        rep.add("C7", PASS, f"none of {len(phrases)} forbidden/internal phrases printed")


def _schedule(rep, b):
    alloc = _dig(b.results, "building_alternatives/0/area_allocation")
    if not isinstance(alloc, dict):
        return
    apt, other, total = (alloc.get(k) for k in
                         ("apartment_area_sqft", "other_area_sqft", "total_sqft"))
    if all(isinstance(x, (int, float)) for x in (apt, other, total)):
        rep.add("C2", PASS if abs((apt + other) - total) <= 0.5 else FAIL,
                f"apartment+other={apt + other} vs total={total}")
        share = alloc.get("share")
        if isinstance(share, (int, float)) and total:
            rep.add("C1", PASS if abs((apt / total) - share) <= 0.005 else FAIL,
                    f"drawn share {apt / total:.4f} vs stated {share}")


def rules_d(rep, b, repo, fetch_links):
    pdf = b.pdf
    missing = [i for i, t in enumerate(pdf.page_text, start=1)
               if _nospace(f"Page {i} of {pdf.pages}") not in _nospace(t)]
    rep.add("D1", PASS if not missing else FAIL,
            "every page numbered" if not missing else f"pages missing 'Page X of Y': {missing}")
    _outline_check(rep, b)
    _links(rep, b, fetch_links)
    _tables(rep, b)
    _clipping(rep, b)
    _fonts(rep, b, repo)
    # D5 (heading stranded at a page foot; caption off its figure) and the D6 dark-pixel
    # hidden-text sub-check are not implemented yet; surface the gap explicitly so a consistent
    # bundle never reports a silent all-green (exit 3, not 0) and the downstream M0-T195 summary
    # can enumerate exactly what was and was not evaluated.
    rep.add("D5", OWED, "not implemented -- figure/caption page attribution")
    rep.add("D6", OWED, "dark-pixel subcheck not implemented")
    rep.add("D9", PASS, f"words per page {[len(t.split()) for t in pdf.page_text]}")


def _outline_check(rep, b):
    out_titles = {_nospace(t) for _, t in b.pdf.outline}
    heads = {_nospace(h): h for _, h, _ in b.html.headings}
    # a bookmark whose words run together: its no-space form is a known heading but it has
    # fewer words than the HTML heading (Chromium dropped a space at a line wrap)
    run = [t for _, t in b.pdf.outline if _nospace(t) in heads
           and len(t.split()) < len(heads[_nospace(t)].split())]
    for t in run:
        rep.add("D2", REVIEW, "bookmark words run together (Chromium wrap)", quote=t)
    missing = [("heading", h) for lvl, h, _ in b.html.headings
               if lvl <= 2 and _nospace(h) not in out_titles]
    missing += [("svg-title", t) for s in b.html.svgs for t in s.role_text("title")
                if _nospace(t) not in out_titles]
    for kind, t in missing[:10]:
        rep.add("D2", REVIEW, f"{kind} not a bookmark", quote=t)
    if not run and not missing:
        rep.add("D2", PASS, "every title is a bookmark landing on its page")


def _links(rep, b, fetch_links):
    if b.pdf.has_objstm:
        rep.add("D3", REVIEW, "compressed object streams; link annotations unreadable")
        return
    anchors = {h[1:] for h in b.html.hrefs if h.startswith("#")}
    missing = sorted(a for a in anchors if a not in b.pdf.dests)
    rep.add("D3", FAIL if missing else PASS,
            f"href targets without a destination: {missing}" if missing
            else f"{len(anchors)} internal anchors resolve to destinations")
    for item in re.findall(r"see item (\d+)", b.html.text, re.I):
        if f"issue-{item}" not in b.pdf.dests:
            rep.add("D3", REVIEW, f"'see item {item}' has no issue-{item} destination")
    urls = sorted({u for _, u in b.pdf.urls})
    if fetch_links:
        for url in urls:
            _fetch(rep, url)
    elif urls:
        rep.add("D3", PASS, f"{len(urls)} external URLs listed (use --fetch-links to verify)")


def _fetch(rep, url):
    req = urllib.request.Request(url, headers={"User-Agent": "report-export-check"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:  # noqa: S310 - documented fetch
            rep.add("D3", PASS if resp.status == 200 else REVIEW, f"{url} -> {resp.status}")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        rep.add("D3", REVIEW, f"{url} fetch failed: {exc}")


def _tables(rep, b):
    crossing_no_head = [tb for tb in b.html.tables
                        if not tb["has_thead"] and _crosses(b, tb)]
    rep.add("D4", FAIL if crossing_no_head else PASS,
            "a table crosses a page with no header row" if crossing_no_head
            else "crossing tables repeat their header")


def _crosses(b, tb):
    head = _nospace(tb.get("thead_text") or "")
    return bool(head) and sum(1 for t in b.pdf.page_text if head in _nospace(t)) > 1


def _clipping(rep, b):
    clipped = [(pi, box["text"]) for pi, boxes in enumerate(b.pdf.boxes, start=1)
               for box in boxes
               if (box["x0"] < MARGIN_PT - 2 or box["x1"] > PAGE_W - MARGIN_PT + 2)
               and 40 < box["y0"] < 802]
    if clipped:
        for pi, t in clipped[:8]:
            rep.add("D6", FAIL, "word box outside the content box", pi, quote=t)
    else:
        # only the out-of-content-box sub-check ran; the overlap and dark-pixel sub-checks are
        # not implemented, so D6 must NOT claim a full PASS (it would overstate coverage).
        rep.add("D6", REVIEW,
                "clipping sub-check only: no out-of-box words; overlap/dark-pixel not implemented")


def _fonts(rep, b, repo):
    sizes = set(b.pdf.font_sizes)
    missing = {n: pt for n, pt in repo.token_pt.items()
               if not any(abs(s - pt) <= 1 for s in sizes)}
    rep.add("D7", FAIL if missing else PASS,
            f"token sizes absent (global shrink?): {missing}; saw {sorted(sizes)}" if missing
            else "property title, headline and section sizes match the tokens")
    tiny = sorted(s for s in sizes if s < 8)
    if tiny:
        rep.add("D8", REVIEW, f"font sizes under 8 pt (reviewer item): {tiny}")


def rules_e(rep, b):
    overflow = [(w, d.get("scroll_width", 0), d.get("inner_width", w)) for w, d in b.web.items()
                if d.get("scroll_width", 0) > d.get("inner_width", w) + 1]
    rep.add("E1", FAIL if overflow else PASS,
            f"horizontal scroll at {overflow}" if overflow else "no horizontal page scroll")
    pdf_state = ("zones" if _svgs_with(b, ["area_zone_apartment"])
                 else "bar" if _svgs_with(b, ["area_bar_apartment"]) else "absent")
    states = {w: d.get("area_allocation_state", "absent") for w, d in b.web.items()}
    if pdf_state in ("zones", "bar") and any(s == "absent" for s in states.values()):
        rep.add("E3", OWED, f"PDF shows {pdf_state}; website does not (parity owed M5-T174)")
    else:
        disagree = {w: s for w, s in states.items()
                    if s != pdf_state and not (pdf_state == "absent"
                    and s in ("absent", "deferred", "unavailable"))}
        rep.add("E3", FAIL if disagree else PASS,
                f"area-illustration state differs: PDF {pdf_state}, web {disagree}" if disagree
                else f"area-illustration state agrees ({pdf_state})")
    rep.add("E2", PASS, "website/PDF figure parity scanned from results.json")
    for w, path in b.before_web.items():
        after = b.folder / "web" / f"{w}.png"
        if after.exists():
            same = hashlib.sha256(path.read_bytes()).hexdigest() \
                == hashlib.sha256(after.read_bytes()).hexdigest()
            rep.add("E4", PASS, f"{w}px before/after {'unchanged' if same else 'changed'}")


# --- outputs + reprint + CLI ----------------------------------------------------------

def write_outputs(rep, b, out: Path):
    out.mkdir(parents=True, exist_ok=True)
    rows = [{"rule": r.rule, "verdict": r.verdict, "page": r.page, "role": r.role,
             "detail": r.detail} for r in rep.results]
    (out / "check.json").write_text(json.dumps(
        {"first_line": FIRST_LINE, "exit_code": rep.exit_code(), "results": rows}, indent=2),
        "utf-8")
    md = [FIRST_LINE, "", "| rule | verdict | page | evidence |", "|---|---|---|---|"]
    md += [f"| {r.rule} | {r.verdict} | {r.page or ''} | {r.detail.replace('|', '/')} |"
           for r in rep.results]
    (out / "check.md").write_text("\n".join(md) + "\n", "utf-8")
    dv = ["# drawings visible", ""] + [
        f"- {s.drawing} [{s.section}] roles={sorted(s.roles)} "
        f"title={'; '.join(s.role_text('title')) or '(none)'}" for s in b.html.svgs]
    (out / "drawings-visible.md").write_text("\n".join(dv) + "\n", "utf-8")
    pages = ["# page images (110 dpi grey, sha256)", ""] + [
        f"page {i}: sha256={sha}" for i, sha in enumerate(b.pdf.images, start=1)]
    (out / "pages.txt").write_text("\n".join(pages) + "\n", "utf-8")


def reprint_html(repo: Path, html: Path, out: Path):
    script = repo / "apps/web/scripts/print-report-pdf.mjs"
    if not script.exists():
        return None
    pdf = out / "reprint.pdf"
    try:
        subprocess.run(["node", str(script), str(html), str(pdf)],
                       capture_output=True, timeout=180, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    return extract_pdf(pdf) if pdf.exists() else None


def run(args) -> int:
    repo = Path(args.repo)
    ctx = load_repo(repo)
    phrases = args.phrases.split("|") if args.phrases else []
    bundle = load_bundle(Path(args.bundle), Path(args.roles) if args.roles else None, phrases)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    rep = Report()
    rules_a(rep, bundle, ctx, args.sha, reprint_html(repo, bundle.folder / "report.html", out))
    rules_b(rep, bundle, ctx)
    rules_c(rep, bundle, ctx)
    rules_d(rep, bundle, ctx, args.fetch_links)
    rules_e(rep, bundle)
    write_outputs(rep, bundle, out)
    print(FIRST_LINE)
    for r in rep.results:
        print(f"{r.rule} {r.verdict} p{r.page or '-'} {r.detail}")
    return rep.exit_code()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Report export consistency check.")
    p.add_argument("--bundle", required=True)
    p.add_argument("--sha", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--roles")
    p.add_argument("--phrases", help="internal-language phrases, '|'-separated")
    p.add_argument("--out", required=True)
    p.add_argument("--fetch-links", action="store_true")
    args = p.parse_args(argv)
    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.sha):
        print(f"--sha must be a 40-hex commit (got {args.sha!r})", file=sys.stderr)
        return 2
    try:
        return run(args)
    except CheckError as exc:
        print(f"{FIRST_LINE}\nERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
