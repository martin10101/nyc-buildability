# M4-T018 G1 gate report — independent data-contract review (verbatim reviewer return)

Recorded by the orchestrator from the independent reviewer's return (reviewer != producer;
reviewer read-only; pinned review HEAD confirmed).

---

**Reviewer:** data-contract-verifier (independent; not the producer, official-source-researcher)
**Task:** M4-T018 — research-only; scenarios S1–S5 + section_last_amended flag check
**Pinned review HEAD:** `859b34c926360e9800b3ce76bd71fc504d2eff7f` — **CONFIRMED** (`git rev-parse
HEAD` matches; expected uncommitted control-plane files observed; the reviewed report is
committed at HEAD and byte-identical to the working tree).
**Verdict: PASS**

The producer's central claims are not taken on faith — the reviewer re-fetched the live
official source and reproduced every load-bearing value byte-exact.

## Findings (claim → method → result → severity)

### F1 — S1 capture provenance: byte-exact reproduction (PASS)
- Claim: live GET of `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10`
  (browser UA) returns HTTP 200, 1,316,658 bytes, sha256
  `4a75e22f22a736beea6daf52c57cca3ce66f9cacc4244807964577141216e0a4`; canonical node/18523.
- Method: independent curl fetch to scratchpad; byte count + sha256; header inspection.
- Result: HTTP 200; Content-Length 1316658; downloaded 1316658 bytes; sha256 **identical**;
  `Link: rel="shortlink" .../node/18523`, `X-Generator: Drupal 9`. The page is **unchanged**
  since the producer's 2026-09-14 capture — no drift. Severity: none.

### F2 — S1 verbatim definitions at anchors (PASS)
- Method: parsed the captured HTML at each `id="term-…"` anchor; extracted text + `<time>`.
- Result — all byte-exact to the report:
  - **street, wide** — Last Amended **3/26/2026**; full text carries the **C5-3/C6-4/C6-6**
    alternate-width clause (avg ≥75 ft AND min ≥65 ft), the **70-ft**
    connector-between-two-75-ft-portions / <700 ft clause, the continuous-street-line
    redefinition for height/setback + open-area/arcade, and **both named designations**
    (Broadway W94–97, Manhattan CD7; Allen St Rivington–Delancey, Manhattan CD3, "which are
    separated by mapped public park"). Matches report Part 1.3 character-for-character. The
    amendment stamp is the term's own element:
    `<time datetime="2026-03-26T12:00:00Z" class="datetime">3/26/2026</time>`.
  - **street, narrow** — Last Amended **12/15/1961**, "A 'narrow street' is any street less
    than 75 feet wide." Confirmed.
  - **street line** — **10/25/1973** confirmed.
  - **street setback line** — **9/19/1985**, full SI / Queens-CD10 City-Map text incl. the
    erection-prohibition sentence confirmed.
- Severity: none.

### F3 — 504 channel disclosure (PASS, honesty-verified, not re-run)
- The report discloses the print/PDF channel (`entityprint/pdf/node/18523` → 302 →
  `/print/pdf/node/18523`) 504'd twice, with the canonical-HTML fallback used and pinned by
  sha256 — exactly the M4-T016 pattern. The reviewer did not re-execute the 504 (not
  load-bearing: the fallback provenance is fully verified byte-exact in F1). Disclosure is
  present and channel-honest. Severity: none.

### F4 — S2 accepted snapshot state (PASS)
- Read `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`: `verbatim_excerpt` = the
  flat-75 pair only (no C5-3/C6-4/C6-6, no named designations); `retrieved_at
  2026-07-22T00:00:00Z`; `content_digest_sha256 4810adcb…` (matches report);
  `extraction_status extracted_draft`; `raw_html_verified false`. All as claimed.
  Severity: none.

### F5 — S2 chronology correction accurate (PASS)
- The amendment date **2026-03-26 precedes** the snapshot retrieval **2026-07-22** — the
  fuller text was already the live law at snapshot-capture time; the flat snapshot was
  already incomplete when taken. The report states this correctly and correctly flags that
  M4-T016's "LATER than" sentence is chronologically backwards while M4-T016's ultimate
  conclusion still holds. Severity: none.

### F6 — S2 named superseded-text carriers + packet-premise correction (PASS)
- `r5_setback.rule.json` (`status: needs_review`, `qualified_human_approval: pending`)
  **cites `snapshot_id: zr-12-10`** and quotes the flat-75 sentence — confirmed carrier.
- M4-T013 report quotes the flat text sourced from the snapshot (lines 41–45).
- **Packet-premise correction verified:** grep of
  `r6_r7_r8_wide_street_conditional_far.rule.json` returns only `zr-23-22` and no `zr-12-10`
  anywhere. The producer's correction is accurate; the report names it as the downstream
  D-052-R001 consumer, not a superseded-text carrier.
- The two supplementary rules (`r1_r2_qrs_height`, `r5_qrs_height`) do not cite zr-12-10 —
  consistent with the report.
- **No adjudication / no snapshot edit:** snapshot and rulesets dir clean/unchanged. The
  report explicitly routes the "which text governs a past acceptance" question onward.
- Severity: none.

### F7 — S3 build-input specs capture-ready (PASS)
- Part 3.1 named-street override table: two rows with verbatim 12-10 anchors,
  borough/CD/frontage fields, legislative-override effect, verbatim source quote; the
  "separated by mapped public park" grammatical-scope question carried as open.
- Part 3.2 C5-3/C6-4/C6-6 test: both independent triggers with verbatim-grounded conditions,
  the data gaps (no accepted connector computes portion-level average/minimum width), and the
  **"may be considered" vs "is"** legal-reading question routed to a qualified human / G6.
- Severity: none.

### F8 — S4 bounded negatives (PASS)
- Every negative bounded to a named source. No universal-negative claim. The Allen St
  demapping proceedings (C 250306 MMM / N 250307 ZRM) explicitly marked an **unverified lead
  from the discovery aid**; map-status and zoning-text status kept separate. D-051-R001
  discipline satisfied. Severity: none.

### F9 — S5 scope (PASS)
- `git show --stat faf0b22e` and `git show --stat 00b28626` each touch exactly one file — the
  M4-T018 report (370 insertions, 4 deletions replacing the placeholder). Zero
  code/schema/fixture/snapshot/dependency changes. Severity: none.

### F10 — section_last_amended mismatch stated as observation, not fix (PASS)
- The snapshot's `section_last_amended: "2024-12-05"` matches none of the five per-term
  Last-Amended dates (1973/1985/1961/1961/2026). The report states this as a likely
  pre-existing snapshot-metadata quality issue, not corrected here. Snapshot unchanged.
  Severity: none.

### Directive-refs note (advisory to orchestrator)
In-regime task (D-045-R002/R008/R009, D-046-R001/R002, D-051-R001). The evidence-map claims
reproducible from source all hold: R002 F1–F8; R009/R002-disjointness F6/F9; D-051-R001 F8.
R008/D-046-R001 process claims are control-plane provenance outside this content review. The
formal verification.json PASS is the independent directive-compliance-verifier's pass;
nothing reproduced contradicts the evidence map.

## Advisories for the two downstream build packets
1. **Snapshot-update packet (rules-engineer):** update `zr-12-10.snapshot.json` to the full
   current street-wide text, correct `section_last_amended` (the term's own stamp is
   2026-03-26; "2024-12-05" appears borrowed from the page-level City-of-Yes banner), refresh
   retrieval date/digest, and flow a corrective addendum to the M4-T013 pin and
   `r5_setback.rule.json`. Keep the conflict visible until G6; do not let the addendum
   retroactively re-adjudicate any past acceptance without a qualified-human ruling.
2. **Exception-rule build packet (D-052-R001):** (a) the named-street override needs a
   location-match mechanism independent of DCM `Streetwidth` (community district + named
   cross-streets — new build scope), a distinct legislative-override provenance/reason code,
   and resolution of the "separated by mapped public park" grammatical scope; (b) the
   C5-3/C6-4/C6-6 alternate-width test requires portion-level average and minimum width
   inputs no accepted connector computes today, and a qualified-human ruling on "may be
   considered" vs "is" before it can auto-classify (otherwise leave
   professional_review_required). OQ-4-c (reachability for R6–R12 lots via overlay/mixed-use
   mapping) remains open.

## Reproduction commands
- `git rev-parse HEAD` → 859b34c9…
- curl (Chrome UA) of the 12-10 page → HTTP 200, 1,316,658 bytes, sha256 4a75e22f…e0a4
- HTML anchor extraction at the four term anchors → verbatim text + time dates as above
- `git show --stat faf0b22e` / `00b28626` → one file each
- grep `zr-12-10` in r6_r7_r8 rule → no match; in r5_setback → snapshot_id + flat quote

**VERDICT: PASS.** All five scenarios and the section_last_amended flag check reproduce from
source; the live official capture matches the recorded provenance byte-exact; no defects.
