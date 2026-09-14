# M4-T018 - ZR 12-10 wide/narrow-street text capture + accepted-snapshot reconciliation

Producer: official-source-researcher. Date: 2026-09-14 (capture) / 2026-09-13 (task claim date).
Scope: RESEARCH ONLY - no code, no schema, no snapshot, no directive/queue edits. This report
resolves OQ-4-a/b/c from the accepted `M4-T016` research (B6, per its own G1 advisory 1: B6 before
B4) with a FRESH, independently-executed official capture - not a re-read of M4-T016's own capture.
Read-only pins consumed: `project-control/reports/M4-T016-a2-geometry-mechanics-research.md`,
`project-control/reports/M4-T013-street-width-research.md`,
`services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`,
`docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`,
`docs/research/owner-research/RQ005_Deep_Research_2026-09-14.md` (discovery aid only, D-050-R002).

## 0. Bottom line

- **S1 (capture): DONE, independently.** The print/PDF completeness channel (`entityprint/pdf/node/18523`,
  which 302-redirects to `/print/pdf/node/18523`) **504'd twice again today** - reproducing M4-T016's
  finding on a fresh attempt, not by re-quoting it. The documented canonical-HTML fallback succeeded:
  direct HTTPS GET of `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10`, browser
  User-Agent, HTTP 200, 1,316,658 bytes, sha256
  `4a75e22f22a736beea6daf52c57cca3ce66f9cacc4244807964577141216e0a4`, retrieved 2026-09-14 (server
  `Date` header 02:15:06 GMT). This independently reproduces M4-T016's central finding byte-for-byte
  on the operative clauses: the "street, wide" defined term is currently **Last Amended 3/26/2026**
  and its live text contains the C5-3/C6-4/C6-6 alternate-width clause and the two named-street
  designations. "street, narrow" is unchanged (Last Amended 12/15/1961). Full verbatim text: Part 1.
- **S2 (reconciliation): the conflict is real, dated, and precisely bounded here** - and one dating
  claim in the M4-T016 narrative is corrected (Part 2.3): the amendment date (2026-03-26) is
  **earlier than**, not later than, both the snapshot's own retrieval date (2026-07-22) and the
  M4-T013/M4-T016 report dates - meaning the fuller text was already the live law when the flat-text
  snapshot was captured. The conflict is NOT adjudicated and the snapshot is NOT edited (out of
  scope; a later rules-engineer task).
- **S3 (build-input specs):** both requested specs are written out in Part 3, sourced entirely from
  this task's own verbatim capture.
- **S4 (bounded negatives):** every negative claim below is bounded to the named source examined
  (D-051-R001); the Allen Street map-amendment material is explicitly marked as an unverified lead
  from the discovery aid, never asserted as this task's own finding.
- **S5 (scope):** exactly one file changed (this report); confirmed in the self-checks (Part 6).

## 1. Fresh official capture (S1)

### 1.1 Channel attempts (disclosed, not silently substituted)

1. **Print/PDF completeness channel**, attempted twice today, per the risk the task packet named:
   - `GET https://zoningresolution.planning.nyc.gov/entityprint/pdf/node/18523` -> HTTP **302** to
     `https://zoningresolution.planning.nyc.gov/print/pdf/node/18523` (0.16-0.34 s, confirmed via
     `curl -D -`, no `-L`).
   - Following the redirect (`curl -L`, 180 s timeout) twice: **HTTP 504 Gateway Timeout** both times
     (59.3 s and 59.3 s wall time, response body `"The application did not respond in time."`, 41
     bytes). This is a fresh reproduction of the same failure M4-T016 recorded for this page, not a
     re-quote of that report - the channel is confirmed unusable for this large page today as well.
2. **Fallback channel used (per the task's documented instruction):** direct HTTPS GET of the
   canonical article page with a browser User-Agent (`curl -A "Mozilla/5.0 (Windows NT 10.0; Win64;
   x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"`), no auth, no bot-wall
   encountered.
   - URL: `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10`
   - HTTP 200; response headers: `Content-Type: text/html; charset=UTF-8`, `Content-Length: 1316658`,
     `X-Generator: Drupal 9`, `Link: <.../article-i/chapter-2/12-10>; rel="canonical"`,
     `Link: <.../node/18523>; rel="shortlink"` (confirms this canonical page IS node 18523, the same
     node the print channel targets), server `Date: Mon, 14 Sep 2026 02:15:06 GMT`.
   - Downloaded byte count matches `Content-Length` exactly: **1,316,658 bytes**.
   - **sha256 (over the exact captured bytes):** `4a75e22f22a736beea6daf52c57cca3ce66f9cacc4244807964577141216e0a4`
   - Retrieval date/time recorded: 2026-09-14 (server `Date` header 02:15:06 GMT; local capture
     completion 02:15:07 GMT per `curl` timing). Raw file kept only in the session scratchpad
     (thin client; not committed) - this sha256 + byte count + URL + timestamp is the provenance
     record, matching the M4-T013/M4-T016/M2-T021 pattern.
   - Note for future reconciliation: this capture's byte count (1,316,658) differs by 9 bytes from
     M4-T016's E6 capture of the same URL one day earlier (1,316,667 bytes, sha256
     `0c341a0b55eb7bc0bea817144c434b4d229de41c7f7ebc9c1b021e2f824dd977`) - expected day-to-day drift on
     a large, dynamically-rendered Drupal page (e.g. a cache-timestamp or unrelated-term edit
     elsewhere on the same all-terms page), NOT a change in the terms this report quotes below - every
     definitional term quoted here was independently re-located by its own HTML anchor in today's
     capture and is reproduced character-for-character from today's bytes.

### 1.2 Verbatim definitions (all quoted from today's capture, located by each term's own `id="term-..."` anchor)

| Term | Node | Last Amended | Verbatim text |
|---|---|---|---|
| **Street line** | `/node/21677` | 10/25/1973 | "A 'street line' is a lot line separating a street from other land." / "A 'street setback line' supersedes the street line in the application of yard, height and setback, and court regulations." |
| **Street setback line** | `/node/21679` | 9/19/1985 | "A 'street setback line' is a line shown on the City Map in the Borough of Staten Island, or in Community District 10 in the Borough of Queens. A street setback line shall not be located within a mapped street area." / "A street setback line supersedes the street line in the application of yard, height and setback, and court regulations." / "No building or other structure shall be erected within the area between street setback lines fronting on the same street, or between a street setback line and the opposite mapped street line if no street setback line exists. Any existing building or other structure within this area may be continued, changed, extended or structurally altered but shall not be enlarged." |
| **Street wall** (context, not requested but adjacent) | `/node/21680` | 12/15/1961 | "A 'street wall' is a wall or portion of a wall of a building facing a street." |
| **Street, narrow** | `/node/21678` | 12/15/1961 (unchanged) | "A 'narrow street' is any street less than 75 feet wide." |
| **Street, wide** | `/node/21683` | **3/26/2026** | Full text below (1.3). |

`street setback line` was **not verbatim-quoted by M4-T016** (only named as a "directly-leaned-on
term"); this report supplies its first verbatim capture in this chain. Its own text further confirms
it is a NARROW, geography-scoped concept (Staten Island / Queens CD10 City-Map lines only) that
supersedes the "street line" where it exists - distinct from, and not a general substitute for, the
`12-10` "street, wide"/"street, narrow" width test that this report otherwise addresses.

### 1.3 The "street, wide" full text (verbatim, today's capture)

> "A 'wide street' is any street 75 feet or more in width. In C5-3, C6-4 or C6-6 Districts, when a
> front lot line of a zoning lot adjoins a portion of a street whose average width is 75 feet or more
> and whose minimum width is 65 feet, such portion of a street may be considered a wide street; or
> when a front lot line adjoins a portion of a street 70 feet or more in width, which is between two
> portions of a street 75 feet or more in width, and which portion is less than 700 feet in length,
> such portion may be considered a wide street, and in that case, for the purposes of the height and
> setback regulations and the measurement of any publicly accessible open area or arcade, the street
> line shall be considered to be a continuous line connecting the respective street lines of the
> nearest portions of the street which are 75 feet or more in width."
>
> "In Community District 7 in the Borough of Manhattan, the roadways of Broadway between West 94th
> and West 97th Streets and in Community District 3 in the Borough of Manhattan, the roadways of
> Allen Street between Rivington and Delancey Streets, which are separated by mapped public park
> shall each be considered a wide street."

This is character-for-character identical to the text M4-T016 quoted from its own 2026-09-13
capture - an independent, dated re-confirmation (not a repetition on faith) that: (a) the amendment
is real and stable across two independent fetches on two different days; (b) the amendment date
stamp (3/26/2026) is consistent; (c) M4-T016's transcription of the clause was accurate.

**Amendment-date evidence, from this capture, not memory:** the `<time datetime="2026-03-26T12:00:00Z"
class="datetime">3/26/2026</time>` element sits inside this term's own
`definition__amended-date` block, directly attached to the "street, wide" `definition__title`
heading - this is the term's own dated amendment stamp, not a page-level banner.

## 2. Reconciliation against the accepted snapshot and the M4-T013 pin (S2)

### 2.1 What the accepted pin says

- `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json` (read-only; retrieved_at
  `2026-07-22T00:00:00Z`, `content_digest_sha256 4810adcb1beab01cd4d71176495c79183fb9867f4463ff05a8f111598030243a`,
  `extraction_status: extracted_draft`, `raw_html_verified: false`) carries only:
  `"A wide street is a street that is 75 feet or more in width. A narrow street is a street that is
  less than 75 feet in width."` - a flat one-sentence pair, with NEITHER the C5-3/C6-4/C6-6 clause
  NOR the two named-street designations.
- `project-control/reports/M4-T013-street-width-research.md` (accepted; section 1) quotes this exact
  same flat sentence, sourced from this same snapshot file, as its own pin for the wide/narrow-street
  threshold the A2 wave builds against.

### 2.2 What changed (WHAT)

Relative to the flat-75 pin, the CURRENT live text (Part 1.3, my own fresh capture) adds two
substantive blocks that this task's fresh capture confirms exist in the operative law today:

1. **The C5-3/C6-4/C6-6 alternate-width/street-line-continuity clause** - a Commercial-district-scoped
   alternate test (average width >= 75 ft AND minimum width >= 65 ft for a street "portion"; OR a
   70-ft-or-more, sub-700-ft "connector portion" between two >= 75-ft portions) that can qualify a
   portion of a street as "wide" even when it does not meet the flat 75-ft test, and which additionally
   redefines the "street line" itself (for height/setback and open-area/arcade measurement purposes
   only) as a synthetic continuous line across such a qualifying portion.
2. **Two unconditional named-street designations** - Broadway between West 94th and West 97th Streets
   in Manhattan Community District 7, and Allen Street between Rivington and Delancey Streets in
   Manhattan Community District 3 (the latter qualified by "which are separated by mapped public
   park") - each "shall be considered a wide street" regardless of any measured or DCM-recorded width.

### 2.3 When it changed, and a dating correction to the M4-T016 narrative

The "street, wide" term's own `Last Amended` stamp is **3/26/2026** (confirmed independently in this
task's capture, matching M4-T016's). Laid against the other dates in this chain:

| Date | Event |
|---|---|
| 2026-03-26 | "street, wide" term Last Amended (per the term's own `<time>` element, confirmed by two independent fetches on 2026-09-13 and 2026-09-14) |
| 2026-07-22 | `zr-12-10.snapshot.json` retrieved (flat text only) |
| 2026-09-13 | M4-T013 report dated (relies on the 2026-07-22 snapshot; does not re-fetch 12-10) |
| 2026-09-13 | M4-T016 report's own fresh 12-10 capture (fuller text found) |
| 2026-09-14 | This task's fresh 12-10 capture (fuller text re-confirmed) |

The amendment date (2026-03-26) is **earlier than**, not later than, the snapshot's own retrieval
date (2026-07-22). M4-T016's own Part 1.4 states: "Today's live 'street, wide' Last-Amended stamp
(3/26/2026) is LATER than both of those prior captures' retrieval dates" - **this specific clause is
chronologically backwards** (March is before July, both 2026); however, M4-T016's ultimate conclusion
in the same sentence - "this is not new law that appeared after the prior work; it means the prior
captures' text was already incomplete/simplified relative to the live site at the time they were
taken" - is the conclusion that correctly follows once the dates are read the right way round, and
this task's own capture supports exactly that conclusion: **the fuller text was already the live,
official text on 2026-07-22 (the snapshot's own retrieval date) and remained so through both the
M4-T013 and M4-T016 report dates; the flat-text snapshot did not reflect the law as it stood even at
its own capture time.** This is a factual, dated correction to one sentence's chronology in an
accepted report, offered as a precision, not a re-litigation of that report's finding (which this
task independently reproduces and agrees with).

**This resolves OQ-4-a as a fact of WHEN, not as an adjudication of WHICH TEXT GOVERNS A PAST
ACCEPTANCE.** Whether the M4-T013 pin (and any rule citing it) needs a corrective addendum, and
whether that addendum should be retroactive to any prior acceptance, is explicitly NOT decided here
per this task's binding constraint - it is routed to the rules-engineer/G6 track named in M4-T016's
own Part 4.3 (item "B6 - the §12-10 wide street text reconciliation... BEFORE the named-street
override table or the C5-3/C6-4/C6-6 clause are built").

### 2.4 Which accepted/draft artifacts reference the superseded (flat) text - named precisely

- `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json` - the pin itself; flat text; also carries a
  `section_last_amended: "2024-12-05"` field that matches NONE of the five per-term Last-Amended
  dates independently captured in this task (1973, 1985, 1961, 1961, 2026) - flagged as a probable
  pre-existing snapshot-metadata quality issue (likely borrowed from the page-level City-of-Yes
  banner date rather than this specific term's own stamp), separate from the wide-street text gap
  and NOT corrected here (no snapshot edits are in this task's scope).
- `project-control/reports/M4-T013-street-width-research.md` (ACCEPTED research report) - quotes the
  flat text verbatim as its own §12-10 pin (section 1).
- `services/api/app/rules/rulesets/r5_setback.rule.json` (`status: needs_review`, NOT published/
  Verified) - directly cites `snapshot_id: zr-12-10` and quotes the same flat sentence as one of its
  two citations.
- **Correction to this task's own packet premise:** the task description characterizes
  `r6_r7_r8_wide_street_conditional_far.rule.json` as "the accepted zr-12-10 snapshot referenced by"
  that rule file. A read of the rule file (this task's own required input) shows this is imprecise:
  its `citations` array cites **only** `snapshot_id: zr-23-22` (ZR 23-22's own FAR table/footnote
  text); it does **not** cite `zr-12-10` anywhere in the file. It relies on the general "wide street"
  *concept* only through ZR 23-22 footnote 1's own wording ("within 100 feet of a wide street"), and
  its own `limitations` already state "a wide-street determination is not performed" - so it never
  applies either the flat-75 value or the fuller current text today. It IS, however, the named
  downstream consumer this task's business reason points at for the eventual D-052-R001-style
  exception check, so it is named here for that reason, not because it currently quotes superseded
  text (it does not quote 12-10 text at all).
- Two further draft rules quote the OPERATIVE ZR 23-423 setback clause (not the 12-10 definitional
  entry itself), which itself uses the plain "wide street"/"narrow street" terms without restating
  their definition: `services/api/app/rules/rulesets/r1_r2_qrs_height.rule.json` and
  `services/api/app/rules/rulesets/r5_qrs_height.rule.json` (both `status: needs_review`). These are
  named for completeness (they are "wide street"-consuming artifacts) but they do not carry the
  superseded 12-10 TEXT themselves - only `r5_setback.rule.json` and the snapshot/M4-T013-report pair
  do that.
- **None of the four rule files above are `published`/Verified** (`release.qualified_human_approval:
  "pending"` in every one read); the conflict is therefore confined to one ACCEPTED research report
  (M4-T013), one accepted-as-input snapshot file, and draft (`needs_review`) rule files - not to any
  finally-approved legal determination. This bound is stated to avoid overclaiming severity, per
  D-051-R001's discipline applied symmetrically (never overclaim a negative OR a positive).
- **The conflict stays visible and is not adjudicated here**: this task does not state which text
  should govern any past acceptance, and does not edit the snapshot, the rule files, or their status.

## 3. Build-input specifications (S3)

### 3.1 Named-street override table (legislative facts, never DCM-derivable)

Per M4-T016's own G1 advisory 2, no DCM `Streetwidth` measurement can ever produce these two rows -
they are unconditional legislative text, sourced only from §12-10 itself:

| Field | Row 1 | Row 2 |
|---|---|---|
| `designation_id` | (build-packet assigns) | (build-packet assigns) |
| `borough` | Manhattan | Manhattan |
| `community_district` | CD 7 | CD 3 |
| `street_name` | Broadway | Allen Street |
| `frontage_from` | West 94th Street | Rivington Street |
| `frontage_to` | West 97th Street | Delancey Street |
| `roadway_note` | (none stated) | "which are separated by mapped public park" |
| `legal_basis` | ZR 12-10, "street, wide", 2nd paragraph, Last Amended 3/26/2026 | same |
| `effect` | unconditionally "considered a wide street"; overrides any DCM `effective_disposition` including `narrow_fail_closed` | same |
| `verbatim_source_quote` | "In Community District 7 in the Borough of Manhattan, the roadways of Broadway between West 94th and West 97th Streets and in Community District 3 in the Borough of Manhattan, the roadways of Allen Street between Rivington and Delancey Streets, which are separated by mapped public park shall each be considered a wide street." (one sentence covers both rows; capture Part 1.3) | same |

Build-packet requirements this specification implies (not built here):
- A location-matching mechanism independent of DCM `Streetwidth` (e.g., street-name + community
  district + cross-street match, or a small curated polygon/line reference) - this is itself new
  build scope, since nothing in the accepted connectors keys on community district or named
  cross-streets today.
- A distinct "legislative override" provenance/reason code (so a forced-wide disposition here is
  never confused with a DCM-measured "wide" disposition in the trace/output).
- **An open grammatical-reading flag, not resolved here:** the "which are separated by mapped public
  park" qualifier's scope is ambiguous on its face - it could modify only "the roadways of Allen
  Street ... " (most likely reading, given the sentence's proximity and the RQ-005 discovery aid's
  description of a center-mall/tax-lot configuration on Allen Street, Part 4 below) or, less likely,
  both named streets. This is offered as this task's own reading of its own captured text, not a
  legal ruling - the build packet should carry it as an open interpretation question for the two-row
  table's `roadway_note`, not silently resolve it either way.

### 3.2 C5-3/C6-4/C6-6 alternate-width test, as a D-052-R001-style exception-check input

**Applicability gate (must be checked FIRST, verbatim-scoped):** the subject zoning lot's district
designation must be exactly C5-3, C6-4, or C6-6. M4-T016's own Part 1.4 item 2 already flags that
this is facially outside the R6-R12 pure Residence Districts this A2 wave targets, and that whether
it is ever reachable for an R6-R12 lot (via a Commercial overlay or Residence-equivalent Commercial
mapping) is unresolved - carried forward here, unresolved, as OQ-4-c.

**Two independent trigger tests (either satisfies the clause):**

| | Test 1 - average/minimum test | Test 2 - 70-ft connector test |
|---|---|---|
| Inputs needed | Average width of the specific street *portion* the lot's front lot line adjoins; minimum width of that same portion | Width of the connecting portion; its length; the widths of the two portions on either side of it |
| Trigger condition (verbatim-grounded) | average width >= 75 ft **AND** minimum width >= 65 ft | portion width >= 70 ft **AND** portion length < 700 ft **AND** it lies between two portions each >= 75 ft wide |
| Effect | that portion "may be considered a wide street" | same, plus (both tests) the street LINE is redefined as a continuous line connecting the nearest >= 75-ft portions' own street lines, for height/setback and open-area/arcade measurement only |
| Data gap | No accepted connector computes "average width of a portion" or "minimum width of a portion" today - DCM's `Streetwidth` is a per-segment value/range/text, not a portion-level average/minimum as this clause defines "portion" | Same absence for the connector-portion's own width/length attribution across three adjoining portions |

**An unresolved interpretation flag carried forward, not decided here:** the clause's own verb is
"**may** be considered a wide street" (permissive), contrasted with the flat-75 rule's declarative "A
wide street **is** any street..." - whether "may" requires an affirmative administrative/agency
determination before a lot can rely on it, or whether it self-executes whenever the numeric
conditions are met, is a genuine open legal-reading question. A D-052-R001-style exception-check
implementation needs this resolved (by a qualified human / G6-track ruling) before it can decide
whether meeting the numeric test alone is sufficient, or whether an unresolved "may" leaves the
classification `professional_review_required` even when the numbers are satisfied.

## 4. Context note - the 2026 Allen Street demapping proceedings (bounded)

**What this task's OWN capture establishes (Part 1.3):** the current, live ZR §12-10 "street, wide"
definition (Last Amended 3/26/2026) already contains the Allen Street Rivington-Delancey,
Manhattan CD3 "considered a wide street" designation, today, independent of any map-amendment
proceeding's status.

**What is an unverified lead only, from the discovery aid, NOT independently captured by this
task:** `docs/research/owner-research/RQ005_Deep_Research_2026-09-14.md` section 5 (read-only,
D-050-R002 discovery aid) describes a CPC report **C 250306 MMM** (dated February 18, 2026, "Allen
Street Mall Demapping") describing Allen Street between Delancey and Rivington as mapped at 138 feet
with a center tax lot, and a companion zoning-text application **N 250307 ZRM** explaining a
provision to preserve wide-street treatment after a mapping change. The discovery aid itself states
that report's mapping-effectiveness question ("conditions effectiveness on the required filing of
certified counterparts... proof that those filings occurred was not established here") was left
**unverified** by that research. This task did not independently fetch either CPC document
(`nyc.gov/assets/planning/download/pdf/about/cpc/250306.pdf` / `.../250307.pdf`) and makes no claim
about them beyond what is stated here as an unverified lead.

**Build-relevant separation (bounded, not adjudicated):** the platform must not conflate (a) whether
a map-amendment proceeding affecting Allen Street's physical/mapped configuration has taken legal
effect, with (b) whether the ZR §12-10 TEXT currently grants the Allen St Rivington-Delancey segment
wide-street status. This task's own capture settles (b) as "yes, in the current live text, as of
2026-09-14." It says nothing about (a) - that remains an unverified lead from the discovery aid only,
bounded to that source (D-051-R001), never asserted as "resolved" or "not resolved anywhere."

## 5. Open questions (disposition of OQ-4-a/b/c, plus new items)

1. **OQ-4-a** - which capture is authoritative as of which effective date: **answered as a dated
   fact** (Part 2.3) - the fuller text was already live law before the flat-text snapshot was
   captured. **NOT answered**: whether/how the M4-T013 pin or any rule needs a corrective addendum,
   or whether that touches any past acceptance - explicitly routed onward (rules-engineer/G6 track),
   never decided by this task.
2. **OQ-4-b** - are the two named-street designations in scope for the A2 build: still an open
   product/scope decision; this report supplies the capture-ready spec (Part 3.1) either way.
3. **OQ-4-c** - is the C5-3/C6-4/C6-6 clause ever reachable for an R6-R12-district lot given
   mixed-use/overlay mapping: still open; this report supplies the capture-ready spec (Part 3.2)
   either way.
4. **New (this task): the "may be considered" vs "is" verb distinction** in the C5-3/C6-4/C6-6
   clause - open legal-reading question (Part 3.2), not decided here.
5. **New (this task): the "which are separated by mapped public park" clause's grammatical scope** -
   open reading question (Part 3.1), offered as this task's own parse only, not a ruling.
6. **New (this task): `zr-12-10.snapshot.json`'s own `section_last_amended: "2024-12-05"` field**
   does not match any of the five per-term Last-Amended dates captured live in this task - flagged as
   a likely pre-existing snapshot-metadata quality issue, not corrected here (no snapshot edits are
   in scope for this task).
7. **Carried, unverified lead only:** the Allen Street map-amendment (C 250306 MMM / N 250307 ZRM)
   filing/effectiveness status - bounded to the discovery aid, not independently captured by this
   task (Part 4).

## 6. Self-checks (documented_test_commands)

Run in this worktree (`wt-m4t018`, reset to `293d6c03`); results recorded verbatim below. Docs-only
change; both commands must stay EXIT 0.

```
$ python tools/validate_directive_compliance.py --check
<recorded verbatim in the producer return>

$ python tools/modularity_check.py --check
<recorded verbatim in the producer return>

$ git status
<recorded verbatim in the producer return - must show exactly one changed file,
 project-control/reports/M4-T018-zr1210-wide-street-reconciliation.md>
```

## Evidence index (this task's own captures)

- **F1** - `https://zoningresolution.planning.nyc.gov/entityprint/pdf/node/18523` -> HTTP 302 to
  `https://zoningresolution.planning.nyc.gov/print/pdf/node/18523` (confirmed via `curl -D -`, no
  follow); following the redirect twice with `curl -L` (180 s timeout each): **HTTP 504** both times
  (59.30 s and 59.34 s wall time; 41-byte body `"The application did not respond in time."`).
  Retrieved 2026-09-14.
- **F2** - `https://zoningresolution.planning.nyc.gov/article-i/chapter-2/12-10` (direct HTTPS GET,
  `curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
  Chrome/120.0 Safari/537.36"`, no auth). HTTP 200; 1,316,658 bytes (`Content-Length` matched);
  sha256 `4a75e22f22a736beea6daf52c57cca3ce66f9cacc4244807964577141216e0a4`. Retrieved 2026-09-14
  (server `Date` header `Mon, 14 Sep 2026 02:15:06 GMT`). `Link: rel="shortlink"` header confirms
  `node/18523` - the same node the print channel (F1) targets. Term anchors located and quoted from
  this file: `id="term-street line"` (`about="/node/21677"`), `id="term-street setback line"`
  (`/node/21679`), `id="term-street wall"` (`/node/21680`), `id="term-street, narrow"` (`/node/21678`),
  `id="term-street, wide"` (`/node/21683`).
- **Read-only pins consumed** (not re-fetched, cited for reconciliation): `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`;
  `project-control/reports/M4-T013-street-width-research.md`;
  `project-control/reports/M4-T016-a2-geometry-mechanics-research.md`;
  `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json`;
  `services/api/app/rules/rulesets/r5_setback.rule.json`;
  `services/api/app/rules/rulesets/r1_r2_qrs_height.rule.json`;
  `services/api/app/rules/rulesets/r5_qrs_height.rule.json`;
  `docs/research/owner-research/RQ005_Deep_Research_2026-09-14.md` (discovery aid, section 5 only,
  D-050-R002).
