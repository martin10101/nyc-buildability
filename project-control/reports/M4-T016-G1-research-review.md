# M4-T016 G1 gate report — independent data-contract review (verbatim reviewer return)

Recorded by the orchestrator from the independent reviewer's return (reviewer != producer;
reviewer read-only; pinned review HEAD confirmed).

---

**Task:** M4-T016 — D-045 A2 research: ZR geometry-mechanics section map + within-100-ft
wide-street lot-geometry mechanic (OQ-4)
**Reviewer:** data-contract-verifier (independent; producer was official-source-researcher)
**Gate:** G1 | **Type:** research-only, in-regime (directive_refs: D-045, D-046)
**Deliverable:** `project-control/reports/M4-T016-a2-geometry-mechanics-research.md`

## Pinned-HEAD confirmation
`git rev-parse HEAD` = `7c2761c2913f1809e4c923866c591b0e13716aa6` — matches the pinned review
head. Uncommitted files present are agent-memory + scratchpad + control-plane JSONs (the
orchestrator frozen-head pattern), not contamination of the reviewed report (which is committed
at eac7b42a). Proceeded.

## VERDICT: PASS

All five acceptance scenarios reproduced from evidence; the load-bearing §12-10 discovery
verified byte-exact against the live official source; connector-fit claims verified against
actual source; scope clean; provenance honest. No findings rise to FAIL or BLOCKED.

## Findings (claim → method → byte-exact result → severity)

**F1 — §23-433 setback depths (S1, load-bearing). PASS.**
Method: live WebFetch of `.../article-ii/chapter-3/23-433`. Result: wide-street setback "a
setback with a depth of at least 10 feet shall be provided," narrow-street "at least 15 feet
shall be provided from any street wall fronting on a narrow street" — matches report §1.1/§1.3
byte-exact. The "beyond 50 feet of a street line" / "65 degrees or less" carve-out matches
verbatim. Title "Standard setback regulations", Last Amended 12/5/2024, both as reported.
Severity: none.

**F2 — §23-736 sky-exposure-plane slopes + setbacks (S1, load-bearing). PASS.**
Method: live WebFetch of `.../23-736`. Result: initial setback narrow 20 ft / wide 15 ft; max
front-wall heights "60 feet or six stories" (R6/R7) and "85 feet or nine stories" (R8/R9/R10);
slopes narrow **2.7 to 1** / wide **5.6 to 1**; alternate (paragraph b) open-area depth narrow
15 / wide 10, alternate slopes narrow **3.7 to 1** / wide **7.6 to 1**. Every value matches
report §1.2 byte-exact. Severity: none.

**F3 — §23-731 applicability (S1). PASS.**
Method: live WebFetch. Result: applies to "R6 through R10 Districts without a letter suffix"
with exclusions R6-1/R6-2/R7-3/R9-1, un-suffixed R8 in the part of Manhattan CD9 north of West
125th Street, and Limited Height Districts — matches report §1.1 verbatim. Severity: none.

**F4 — §23-432 title/districts (S1). PASS.**
Method: live WebFetch. Result: title "Height and setback requirements"; table header row R6 R7
R8 R9 R10 R11 R12; Last Amended 12/5/2024. Matches report. Severity: none.

**F5 — §12-10 "wide street" discovery (S1 + the designated load-bearing item). PASS.**
Method: direct HTTPS GET (`curl -A Mozilla/5.0`) of `.../article-i/chapter-2/12-10`; hashed
and parsed locally at anchors `id="term-street, wide"` / `id="term-street, narrow"`. Result:
- Byte count 1,316,667 and sha256
  `0c341a0b55eb7bc0bea817144c434b4d229de41c7f7ebc9c1b021e2f824dd977` — **identical** to the
  report's E6 provenance record.
- "street, wide" shows **Last Amended 3/26/2026** with the full multi-paragraph text: the
  C5-3/C6-4/C6-6 alternate-width clause (avg ≥75 ft / min 65 ft), the 70-ft "between two
  portions ≥75 ft ... less than 700 feet in length" continuous-street-line clause, AND both
  named-street designations (Broadway between W94th–W97th, Manhattan CD7; Allen Street between
  Rivington–Delancey, Manhattan CD3, "separated by mapped public park ... considered a wide
  street"). This matches the report's §1.4 block quote **verbatim**.
- "street, narrow" shows Last Amended 12/15/1961, "A 'narrow street' is any street less than
  75 feet wide." Matches report.
- The report ROUTES this as OQ-4-a/b/c (§1.4 item 4, §4.2 items 2–4) and explicitly does NOT
  adjudicate which capture is authoritative or whether the M4-T013/zr-12-10 snapshot needs
  correction — exactly the required posture (permanent principle 4: conflict stays visible).
Severity: none. This is the single most consequential claim and it is fully substantiated.

**F6 — §12-10 other defined-term dates (S1). PASS.**
Method: local extraction from the same sha256-pinned HTML. Result: street line 10/25/1973,
street wall 12/15/1961, base plane 5/12/2021, sky exposure plane (/front sky exposure plane)
4/18/1987 — all four match report Table §1.3 byte-exact. Severity: none.

**F7 — OQ-4 geometry design grounded, not assumed (S2). PASS.**
Method: verified the ZR 23-22 footnote-1 pin in `r6_r7_r8_wide_street_conditional_far.rule.json`
("For zoning lots, or portions thereof, located within 100 feet of a wide street.") — matches
report §2.1 byte-exact. The geometric operations (per-segment classify → 100-ft planar buffer →
lot-polygon intersect/intersection, "any portion" test) are stated as design, not
implementation, and correctly tie the buffer to the projected foot-unit CRS. Edge cases
inventoried (§2.4): corner lots/multiple frontages, irregular/ambiguous segments,
multi-segment/non-uniform-width streets, exact-100-ft tangency, C5-3/named-street override,
missing-segment. Comprehensive; where no source convention exists (tangency tolerance) it says
so rather than inventing one. Severity: none.

**F8 — EPSG:2263 / US-survey-foot evidence chain (S2). PASS with disclosed substitution
(adequate).**
Method: live WebFetch of `https://epsg.io/2263`. Result: CRS Name "NAD83 / New York Long Island
(ftUS)", Unit "US survey foot" — matches report E9 byte-exact. The report discloses that the
primary registry `epsg.org/crs_2263/...` returned HTTP 403 and that epsg.io was substituted; it
does not hide this. Judgment: epsg.io is a recognized EPSG-registry mirror and the "(ftUS)"
appears in the CRS's own name, which is itself authoritative; the connectors independently pin
wkid 102718/latestWkid 2263 from DCP service metadata. The substitution is adequate and
honestly recorded. Severity: none.

**F9 — Connector-fit claims vs actual code (S4). PASS.**
Method: read `dcm_street_centerline_arcgis.py`, `mappluto_lot_outline.py`,
`mappluto_geometry_arcgis.py` (imports/docstrings/constants), fixture `MANIFEST.json`. Results:
- `build_segment_query_url` (the sole URL builder) never emits `returnGeometry` (the string is
  absent; it sets `outSR=2263&f=json`), so ArcGIS's documented default `returnGeometry=true`
  means polyline geometry IS transported today.
- `parse_segment_page` reads `feature["attributes"]` only and never touches
  `feature.get("geometry")` — geometry is fetched then discarded. The report's correction of
  the packet's "returnGeometry flip" shorthand to a **parse-and-expose gap** is precise and
  code-accurate.
- Fixture MANIFEST note quoted by the report ("Larger byte size ... returnGeometry defaults
  true on this endpoint; no anomaly", Margaret Corbin Drive / `unknown_hedged_below_75`)
  exists byte-exact.
- `mappluto_lot_outline.py` is display-only, EPSG:4326, "No area, dimension, or any
  measurement is EVER computed from these degree coordinates" — verbatim match; must not be
  used for the buffer test.
- `mappluto_geometry_arcgis.py` provides the measurement-grade side: EPSG:2263/wkid
  102718/US survey feet, `compute_area_sq_ft`, `WrongCRSError`, `BOUNDARY_TOLERANCE_FT = 20.0`.
  The report's caution that this 20-ft positional-accuracy constant must NOT be silently
  repurposed as a 100-ft legal-buffer tolerance is well-founded. Gaps recorded as build
  requirements (B3–B7), not papered over. Severity: none.

**F10 — OQ-3 never resolved (S3). PASS.**
The report surfaces OQ-3 (ambiguity-class fail-closed policy) in §0, §2.2 step 2, §3.3, and
§4.2 item 1, keeps it fail-closed-to-narrow, and routes it to a G6-class/architect ruling; it
resolves no interpretation question in-task. DRAFT-until-G6 posture preserved (D-045-R009).
Severity: none.

**F11 — Research-only scope (S5). PASS.**
Method: `git show --stat` on both commits. Result: `232a889b` and `eac7b42a` each touch exactly
one file — `project-control/reports/M4-T016-a2-geometry-mechanics-research.md` (+506/-4,
identical diff, confirming the clean cherry-pick). The out-of-scope agent-memory commit
`a34a61ca` touches only `.claude/agent-memory/official-source-researcher/...` and is NOT part
of eac7b42a — disclosed and correctly not integrated. Zero code/schema/fixture/dependency
changes. allowed_paths = single report file. Severity: none.

**F12 — Provenance discipline & directive requirements. PASS.**
Every material section carries URL + retrieval date (2026-09-13). The print-render channel 504
(entityprint/pdf/node/18523) and the epsg.org 403 are both recorded as failed channels rather
than silently substituted; the 12-10 canonical HTML is sha256-pinned and matched live.
Thin-client respected (captures held in scratchpad, digests recorded, nothing bulk committed).
Directive mapping re-derived: D-045-R002 (mechanics documented with their data inputs, geometry
grounded in source, gaps honest) satisfied; D-045-R008 (bounded gated research packet)
satisfied; D-045-R009 (coverage-only, no rule published, OQ-3 fail-closed) satisfied;
D-046-R001 (wave-3 slot-1 isolated-worktree integration) satisfied; D-046-R002
(pairwise-disjoint — single uniquely-named report file, shares no path with M4-T017) satisfied
by construction. Modularity: docs-only change, no handwritten production source touched — not
applicable. Severity: none.

## Advisories for the A2 build packets (informational; PASS is not conditioned on these)
1. **B6 must precede B4's wide-street text usage.** The §12-10 3/26/2026 amendment is real and
   materially fuller than the accepted zr-12-10 snapshot / M4-T013 pin. Do not build the buffer
   test against the flat 75-ft text; resolve OQ-4-a first (architect/G6) and capture the
   authoritative-as-of-effective-date text with a fresh snapshot.
2. **Named-street override is legislative, not measurable.** The two designations (Broadway
   W94–97 CD7; Allen St Rivington–Delancey CD3) can never be produced by DCM `Streetwidth` or
   geometry; if in scope (OQ-4-b), they require a small, explicitly-§12-10-sourced override
   table — never derived.
3. **CRS parity is a genuine simplification but re-assert it at runtime.** Both DCM and
   MapPLUTO-measurement connectors pin EPSG:2263; the build should still validate
   `outSR`/metadata wkid on every query envelope (the existing connectors already do) before
   any buffer/intersect.
4. **Do not reuse `BOUNDARY_TOLERANCE_FT = 20.0` for the 100-ft buffer** (positional accuracy
   ≠ legal buffer allowance); OQ-4-d has no sourced convention yet.
5. **DCM geometry is a parse-and-expose task, not a query change** — geometry already arrives;
   add a typed, CRS-validated geometry parse (sibling-module pattern per `mappluto_lot_outline`
   beside `mappluto_geometry_arcgis`), leaving the byte-immutable accepted module's public
   discipline intact.

## Reproduction commands
- `git rev-parse HEAD` → 7c2761c2913f1809e4c923866c591b0e13716aa6
- `git show --stat 232a889b` / `git show --stat eac7b42a` / `git show --stat a34a61ca`
- `curl -s -A "Mozilla/5.0" https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10`
  → 1,316,667 bytes, sha256 `0c341a0b55eb7bc0bea817144c434b4d229de41c7f7ebc9c1b021e2f824dd977`;
  anchors `term-street, wide` (Last Amended 3/26/2026) / `term-street, narrow` (12/15/1961)
- WebFetch 23-432, 23-433, 23-731, 23-736, epsg.io/2263 (results above)
- Source reads: `services/api/app/connectors/dcm_street_centerline_arcgis.py` (lines 148-166,
  391-398, 789-797), `mappluto_lot_outline.py` (lines 1-38), `mappluto_geometry_arcgis.py`
  (lines 26-63, 215), `tests/fixtures/dcm_street_centerline/MANIFEST.json` (line 153),
  `rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json` (footnote-1 quote)

**Verdict: PASS.** The orchestrator may record G1 PASS for M4-T016 and unblock the A2 build
packets (with advisories 1–5 pinned).
