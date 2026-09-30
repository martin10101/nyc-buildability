# PDF converter trial (E-02)

Queue item E-02 (plan M1-22; plan section 5c point 4): choose the tool that turns our HTML report
pages into a PDF on the server. Candidates: **WeasyPrint** and **headless Chromium**, with
**ReportLab** (the competitor's tool) for comparison.

**This trial admits nothing.** No dependency file changed (`services/api/requirements*`,
`pyproject.toml`, `package.json`, any lock). Adding a library is a separate Tier B step with a G5
security review (`.claude/ORCHESTRATION_POLICY.md` section G, `docs/DEPENDENCY_SECURITY_POLICY.md`).

**Recommendation: WeasyPrint 70.0**, on three conditions (details in "What has to happen before
WeasyPrint is admitted" below):

1. **System libraries.** The server must have the Pango and HarfBuzz system libraries. Nobody has
   yet confirmed that Render's plain Python runtime has them. How those OS libraries are supplied
   and kept patched also needs its own security decision, because our lock and audit gates do not
   cover them.
2. **Tier B admission with a G5 review.**
3. **`fonttools` age.** The newest `fonttools` releases are too new today, so the lock must use one
   that is at least 7 days old.

All facts below were checked on **2026-09-30** (PyPI registry clock `2026-09-30T06:27:46Z`).
Anything taken from upstream documentation and not tested here says **(not tested here)**.

---

## 1. What was actually tried

| Step | Result |
|---|---|
| Installed `weasyprint` into a throwaway venv (Python 3.12.3, Ubuntu 24.04 host), outside the repo | Installed: WeasyPrint 70.0 plus 12 other packages, **all as ready-built wheels** (nothing compiled, no install scripts). About 64 MB on disk. |
| `import weasyprint` | **Failed.** `OSError: cannot load library 'libpango-1.0-0'`. |
| Checked which system libraries WeasyPrint 70.0 loads (its `text/ffi.py`) against the host (`ldconfig -p`) | **Missing:** `libpango-1.0.so.0`, `libpangoft2-1.0.so.0`, `libharfbuzz.so.0`, `libharfbuzz-subset.so.0` (optional today; WeasyPrint warns it will become required), `libharfbuzz-vector.so.0` (optional). **Present:** `libgobject-2.0.so.0`, `libfontconfig.so.1`, `libfreetype.so.6`, `libffi.so.8`. Nothing was installed with `apt-get`, as instructed. |
| Rendering the sample page | **Not done**, because of the missing libraries above. So render time, file size and font embedding were **not measured**, and there is **no PDF** in this folder. |
| Checked the sample page with WeasyPrint's own HTML and CSS parsers (`tinyhtml5`, `tinycss2`, which load without Pango) | The inline drawing lands as SVG elements (`svg`, `pattern`, `marker`, `path`, `text`, ...). The style sheet has 19 rules and 0 parse errors. The two tables have 5 and 80 body rows. |
| Read WeasyPrint 70.0's source for the features we need | See the "How it fits our plan" rows in the table. |
| Headless Chromium | **Not run.** No Chromium is installed on this host, and the plan forbids running `npm`, `npx` or `node` here. Judged from upstream documentation and from how the repo's CI already uses it. |

`trial-sheet.html` in this folder is the test page for the render once the libraries exist: US
Letter, header and footer boxes, "Page X of Y", a page break, and a filler table of 80 rows on a
fresh page. At 9 pt, those rows need at least 1200 pt of height, and a Letter page has 680 pt of
usable height with these margins, so the table must run onto another page. That makes the "header
row repeats" check real. The page also has one inline SVG site plan with a diagonal hatch, dimension strings and labels. It is the same
made-up example lot as `docs/samples/cad` (100 ft x 80 ft lot, 60 ft x 40 ft building), stamped
"Example lot - not a real property" and "PROPOSED - NOT A CITY RECORD". It loads nothing from the
network or the disk.

---

## 2. Findings

| | **WeasyPrint** | **Headless Chromium** (Playwright `page.pdf()`) | **ReportLab** (comparison) |
|---|---|---|---|
| **Version checked** | 70.0 (PyPI) | Python `playwright` 1.63.0 (PyPI). The web app's lock has npm `playwright` / `@playwright/test` 1.61.1 | 5.0.1 (PyPI) |
| **Published / 7-day rule** | 2026-09-08, 21.8 days: **passes** | 1.63.0: 2026-09-15, 14.6 days: **passes** (1.62.0: 60.6 days) | 2026-08-20, 40.7 days: **passes** |
| **Other packages it pulls in** | 12: `brotli` 1.2.0, `cffi` 2.1.1, `cssselect2` 0.10.1, `fonttools` 4.66.1, `pillow` 12.3.0, `pycparser` 3.0, `pydyf` 0.12.1, `pyphen` 0.18.1, `tinycss2` 1.5.1, `tinyhtml5` 2.1.0, `webencodings` 0.6.1, `zopfli` 0.4.3. None is in our runtime lock today. A universal lock (`uv --universal`) also carries `brotlicffi` 1.2.0.2, which `fonttools[woff]` uses on non-CPython (MIT, 0 advisories, 39.5 days old), so the lock gets **14** new entries. | 3: `pyee` 13.0.1, `greenlet` 3.5.6, `typing-extensions` 4.16.0 (already in our lock). **Plus the Chromium browser itself**, downloaded separately (see "System needs"). | 2: `pillow` 12.3.0, `charset-normalizer` |
| **Age problems in that set** | `fonttools` 4.66.1 is 0.6 days old and 4.66.0 is 6.5 days old: **both fail today**. 4.65.0 (19.6 days) passes. Measured from the **newest** file of each release, as `dependency_age_gate.py` does: 4.66.0 passes from **2026-09-30T17:59:14Z** and 4.66.1 from **2026-10-06T16:11:53Z**. All other packages pass. | None | `charset-normalizer` 3.5.2 is 0.1 days old: **fails**. 3.4.9 (84.7 days, already in our tools lock) passes. |
| **Known advisories on the checked version** | **0** for WeasyPrint 70.0 and for each of its 12 packages (GitHub Advisory Database; PyPI's list is also empty). | **0** for `playwright` 1.63.0 (pip), for npm `playwright`, `playwright-core` and `@playwright/test` 1.61.1, and for its 3 packages. | **0** for 5.0.1, `pillow` 12.3.0 and `charset-normalizer` 3.4.9. |
| **Advisory history (why this matters)** | 4 past advisories: GHSA-jf6q-chmf-3h3v (medium, file read / SSRF, fixed **only in 70.0**, so 70.0 is the only clean version), GHSA-jhhc-3hcp-qhm5 (medium, CSS injection when "presentational hints" are on, affects up to 68.1), GHSA-983w-rhvv-gwmv (high, SSRF through a redirect, fixed in 68.0), GHSA-35jj-wx47-4w8r (high, fixed in 61.2). `fonttools` had 2 (fixed in 4.43.0 and 4.60.2). Lesson: every WeasyPrint fix so far was about fetching URLs, so our code must never let it fetch anything. | npm `playwright` GHSA-7mvr-c777-76hp (high): browser downloads without checking the TLS certificate, fixed in 1.55.1. **The Chromium browser itself is not a pip or npm package**, so neither the GitHub Advisory Database, `pip-audit` nor `npm audit` sees its security bugs. Chromium fixes arrive only by upgrading Playwright. | 4 old ones (2 critical, 2 high), all fixed by 3.6.13 or earlier. |
| **License** | BSD-3-Clause. Its packages: BSD, MIT, MIT-0, MIT-CMU (Pillow), Apache-2.0 (`zopfli`). **`pyphen` is GPL-2.0+ or LGPL-2.1+ or MPL-1.1** (we can pick MPL or LGPL): needs a license note in the G5 review. | Apache-2.0 (Playwright). The Chromium build has its own mixed open-source licenses **(not tested here)**. | BSD |
| **System needs** | Pango (upstream says 1.44 or newer **(not tested here)**), pangoft2, HarfBuzz, HarfBuzz-subset (will become required), fontconfig, GObject, plus the font files we use. **None of these is covered by the hash lock, the age gate or `pip-audit`.** | A browser download of roughly 150 MB or more from Playwright's own servers at build time, outside the PyPI/npm locks, plus many OS libraries (NSS, ATK, GBM, ALSA, X11 and others). `playwright install --with-deps` installs those with `apt`, which needs administrator rights **(not tested here)**. | None (ready-built wheels) |
| **Fits plan section 5c point 4 (HTML templates with print styling)** | Yes, directly. It implements CSS paged media: page size, header and footer boxes (`@top-left` ... `@bottom-right` are in its CSS code), `counter(page)` and `counter(pages)`, page breaks, and repeated table headers (`layout/table.py` lays out the `table-header-group` again on each page). No JavaScript (we don't need any: the SVG is made on the server). | Yes. Header and footer templates with page number and page count, `preferCSSPageSize`; CSS header and footer boxes supported since Chrome 131 **(not tested here)**. Best CSS coverage, and it draws SVG exactly as the screen does. | No. Pages are built in Python code, not HTML templates. SVG needs another library (`svglib`), not evaluated. |
| **Inline SVG stays vector** | Yes, from the source: WeasyPrint draws SVG with its own renderer straight into the PDF as vector paths. **Not measured** (render blocked). | Expected yes for plain paths and text **(not tested here)**. | Only through `svglib` (not evaluated). The competitor pastes sections and 3D as JPEG pictures. |
| **Hatch patterns** | Yes, from the source: SVG `<pattern>` (including `patternTransform`) becomes a PDF tiling pattern (`PatternType 1`) drawn with vector lines. SVG `marker` is supported too. | Expected yes **(not tested here)**. | Possible by hand in code. |
| **Fonts embedded** | Yes, from the source: fonts are cut down to the glyphs used (HarfBuzz subset, or `fontTools` if HarfBuzz-subset is missing) and embedded. **Not measured.** | Yes, subset and embedded **(not tested here)**. | Yes, for fonts registered in code. |
| **Archive and accessibility PDF types** | PDF/A (1b to 4f), PDF/UA-1 and -2, PDF/X variants (from the source). | No PDF/A **(not tested here)**. | PDF/A: limited, not evaluated. |
| **Same input gives the same file (for snapshot tests)** | Can fix the PDF dates from `<meta name="dcterms.created">` / `dcterms.modified` (the sample page does this) and accepts a fixed PDF identifier (`pdf_identifier`), from the source. Byte-for-byte sameness **not measured**. | No documented way to fix the creation date **(not tested here)**; snapshots would compare page images, not bytes. | Can set dates in code. |
| **Blocking file and network access** | Yes: `URLFetcher(allowed_protocols=..., allow_redirects=False, fail_on_errors=True)` in 70.0. The default allows every protocol and follows redirects, so our code must always pass a locked-down fetcher. | Page can be run offline with request blocking **(not tested here)**; a whole browser is a much bigger attack surface. | No fetching in normal use. |
| **Render: plain Python runtime** (`render.yaml`: `runtime: python`, `plan: starter`, build `pip install -r requirements.txt`) | **Unverified.** No Render documentation in the repo says which system libraries the Python runtime has, or whether `apt` can run during the build. The repo only records (from `https://render.com/docs/blueprint-spec`, retrieved 2026-07-16) that "buildCommand + startCommand [are] required for non-Docker services", which confirms a Docker option exists as a fallback. | **Unverified**, and harder: needs the browser download and its OS libraries at build time, and a lot of memory per render. The memory of the `starter` plan is not recorded in the repo. | Works: no system libraries. |
| **CI fit** | Runs inside the existing Python test jobs. The runner needs the Pango/HarfBuzz packages; whether `ubuntu-latest` already has them is **unverified**. An `apt` install step would be a `.github/` change (Lane C), and it is itself a download outside a reviewed lock, so it waits for the same OS-library decision (section 4 step 5). | Already used, **for tests only**: `web-e2e` in `.github/workflows/ci.yml` runs `npx playwright install --with-deps chromium`. That downloads the browser outside the lock and is not an admission for production. The API would need Python `playwright` too, with a second version to keep in step with the web app's 1.61.1. | Easy. |

For comparison, the repo already has a dependency-free PDF writer (`services/api/app/cad/pdf_sheet_writer.py`,
one landscape sheet). It uses only the built-in Helvetica font, ASCII text, straight lines and
rectangles, and has no layout engine, so it cannot produce the multi-page report with tables and
our own fonts. It stays as it is; this trial does not change it.

---

## 3. Why WeasyPrint

1. **It does exactly what plan section 5c point 4 describes**: HTML templates with print CSS
   (headers, footers, page numbers, cover sheet, tables) turned into a PDF, with the server-made
   SVG embedded as vector drawings, including the hatch patterns section 5c point 5 asks for.
2. **Its Python layer can be proven under our security rules; its OS-library layer cannot yet.**
   The Python part is 14 ordinary PyPI packages that go through our existing hash-pinned lock,
   age gate and `pip-audit`. The system libraries are a different matter: Pango, pangoft2,
   HarfBuzz (with subset), fontconfig and FreeType are outside the lock, the age gate and every
   advisory gate. Installing them with `apt` (in CI, at build time, or in a Docker image) is
   itself a "dynamic dependency download outside an explicitly reviewed lock" under policy
   section G. So that layer needs its own section G / G5 decision before admission (section 4
   step 5). The options: a Render-provided image, a digest-pinned base image, or distro-signed
   packages with a named way of tracking their security updates.
   Chromium has the same kind of gap, only bigger. Its browser download comes from the vendor and
   sits outside any reviewed lock, and its security bugs are invisible to our advisory checks.
   The WeasyPrint gap is smaller: a few distro-signed text libraries against a whole
   vendor-downloaded browser.
3. **It is small and pure Python** apart from the text libraries. Chromium means a full browser,
   its OS libraries and much more memory on a `starter` server.
4. **Snapshot tests are easier**: fixed PDF dates and identifier.
5. What we give up: Chromium would draw the SVG exactly as the screen does. WeasyPrint has its own
   SVG renderer, so small visual differences are possible. This does not affect checks C-4 and
   C-5, which compare numbers, and the benchmark snapshot tests (E-06) compare each PDF with its
   own approved snapshot, not with the screen.

ReportLab is not recommended: it does not use HTML templates, so it does not match the plan.

**Fallback if the Python runtime cannot get Pango:** there are two ways, and both belong to Lane C
or the owner, not Lane E: (a) move the API to a Docker service on Render with a pinned base image
that installs the libraries (a `render.yaml` and deployment-design change, see ADR-001 and
ADR-003; the image's OS packages still need the section 4 step 5 decision), or (b) ask the owner to reconsider Chromium, accepting the unverifiable browser.

---

## 4. What has to happen before WeasyPrint is admitted (the later Tier B task)

The steps in order. None of them was done here.

1. **Confirm the Render runtime (owner / Lane C).** Check whether Render's Python runtime has
   GObject, Pango 1.44 or newer, pangoft2, HarfBuzz with the subset library, and fontconfig. For
   example, run a one-off probe in a staging build that finds each library and reads the Pango
   and HarfBuzz versions:
   `python -c "import ctypes, ctypes.util as u; n=('gobject-2.0','pango-1.0','pangoft2-1.0','harfbuzz','harfbuzz-subset','fontconfig'); p={k: u.find_library(k) for k in n}; print(p); f=lambda k, s: getattr(ctypes.CDLL(p[k]), s); f('pango-1.0','pango_version_string').restype=ctypes.c_char_p; f('harfbuzz','hb_version_string').restype=ctypes.c_char_p; print(f('pango-1.0','pango_version_string')(), f('harfbuzz','hb_version_string')())"`.
   A missing library prints as `None`, and the probe then stops with an error. On this trial
   host it printed `None` for pango-1.0, pangoft2-1.0, harfbuzz and harfbuzz-subset.
   If any library is missing, or Pango is older than 1.44, choose the fallback above. This is a
   blocker, not a detail.
2. **Choose the exact set** on the day of admission, measured against the PyPI clock:
   `weasyprint==70.0` (older versions have GHSA-jf6q-chmf-3h3v), and `fonttools` at a version at
   least 7 full days old. Age is measured from the newest file of the release, as
   `dependency_age_gate.py` does. Today that is 4.65.0; 4.66.0 qualifies from
   2026-09-30T17:59:14Z and 4.66.1 from 2026-10-06T16:11:53Z. Re-check every package's age and
   advisories that day.
3. **Lane C edits the hot files:** add `weasyprint==70.0` (and a `fonttools` pin if the resolver
   would pick a too-new one) to `services/api/requirements.in` with a comment like the existing
   ones, add the allowed range to `services/api/pyproject.toml`, regenerate
   `services/api/requirements.txt` with `services/api/scripts/lock_requirements.sh` (pinned `uv`,
   `--universal --python-version 3.12 --generate-hashes`), and confirm `lock_requirements.sh --check`.
4. **Run the gates:** `services/api/scripts/dependency_age_gate.py` on the new lock (every package
   at least 604800 seconds old), `pip-audit -r requirements.txt --strict` with zero findings, and
   hash checks against PyPI. No suppressions.
5. **G5 security review** (`docs/DEPENDENCY_SECURITY_POLICY.md` section 5). Check:
   - name and typosquat;
   - maintainers. Note: `webencodings` 0.6.0 and 0.6.1 (2026-08-15) are its first releases
     since 0.5.1 (2017), and CourtBouillon now publishes them instead of the original author. This
     is a maintainer change to assess. Pinning 0.5.1 also satisfies `tinyhtml5`.
   - install scripts: the 13 packages installed here all came as wheels, so none ran. Check the
     14th, `brotlicffi`, the same way.
   - registry origin and age;
   - necessity: the in-house writer cannot lay out text, embed fonts or build tables;
   - licenses: the `pyphen` tri-license, and its 50 bundled hyphenation dictionaries (84 files
     with their own READMEs and licenses).

   **Separately and before admission, decide the OS-library layer under section G.** Pango,
   pangoft2, HarfBuzz (with subset), fontconfig and FreeType are outside the lock, the age gate and
   `pip-audit`, and an `apt` install is a download outside a reviewed lock. Record how they are
   supplied and how their security updates are tracked: a Render-provided image, a digest-pinned
   base image, or distro-signed packages with a named update-tracking method. Nothing below may
   install them until that decision exists.
6. **CI (Lane C, `.github/`), after the step 5 OS-library decision:** supply the system
   libraries the way that decision says, then run a render test and the page snapshot tests. The
   `web-e2e` harness and `exact-production-install` jobs also import the app. So either E-04
   imports `weasyprint` only inside the render function (preferred: the rest of the app does not
   need Pango), or those jobs need the libraries too.
7. **Code rules for Lane E's report builder (E-04)**, behind the lane flag:
   - Render only our own templates. Escape every value with `html.escape`. Keep
     `presentational_hints` off.
   - Always pass `URLFetcher(allowed_protocols={'data'}, allow_redirects=False, fail_on_errors=True)`,
     or a fetcher that serves only our bundled font files. Never pass `xmp_metadata` or style
     sheets by URL (that is the path GHSA-jf6q-chmf-3h3v exploited).
   - Set `dcterms.created` / `dcterms.modified` and `pdf_identifier` from the report's revision,
     never from the clock.
   - Import `weasyprint` inside the render function, not at module level, so the app still
     starts where the system libraries are missing.
   - Cap page count and render time.
8. **Fonts:** Inter, Instrument Serif and IBM Plex Mono (plan section 5c) are under the SIL Open
   Font License. Bundling the font files is a license check, separate from the Python packages.
9. **Finish the trial on the benchmark lots** (215-16 Northern) once the libraries exist and the
   drawing kit (E-01) produces the real SVGs. Render `trial-sheet.html` and the benchmark pages,
   and record render time, file size (under 200 KB for the sample), whether the SVG stays vector,
   and which fonts are embedded (`pdffonts`).

---

## 5. How the facts were gathered (for re-checking)

- Package data: `https://pypi.org/pypi/<name>/<version>/json` (license classifiers,
  `vulnerabilities`, and the upload times of the release's files). Ages use the **newest upload
  time among all files of the version**, which is what `dependency_age_gate.py` checks, since
  the hash lock admits every wheel and the sdist. For every package here except `fonttools`, all
  files were uploaded within a few minutes of each other, so the day counts are the same either
  way. The registry clock comes from PyPI's `Date` header.
- Advisories: `gh api -X GET /advisories -f ecosystem=pip -f affects=<name>@<version>` (and
  `ecosystem=npm` for Playwright). The query was checked against `pillow@9.0.0`, which correctly
  returns 13 advisories.
- WeasyPrint internals: its 70.0 source in the throwaway venv (`text/ffi.py` library list,
  `svg/defs.py` patterns, `pdf/stream.py` `PatternType 1`, `pdf/fonts.py` subsetting,
  `pdf/pdfa.py` / `pdfua.py` / `pdfx.py` variants, `html.py` `dcterms.created`, `urls.py`
  `URLFetcher`).
- Missing libraries: `ldconfig -p` on the host.
- Chromium in CI: `.github/workflows/ci.yml`, job `web-e2e`; versions from `apps/web/package-lock.json`.
