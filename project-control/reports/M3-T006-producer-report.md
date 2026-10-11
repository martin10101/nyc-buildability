# M3-T006 producer report — zoning-law library, first pass (documents only)

Producer: legal-corpus-engineer. Directive: D-094 R102 (owner, 2026-10-11), R104.
Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-abb0b60c2ab150d3c`.
Claim head: `aac892fcde5dc035848af9bf99f7cea0bc8edec2` (branch `task/wave24-report-v3`).
Everything here is an **unreviewed draft** (ADR-007): a discovery aid with source links; nothing is
professionally reviewed, nothing is labelled Verified, no result is called compliant, buildable, or
feasible.

## What each file holds

- `docs/zoning-law-library/benchmark-r6b-sections.json` — the machine-readable core. 73 section entries
  (each: `section_id`, `title`, `zr_url`, `capture_status` [snapshot_id + content_digest_sha256 copied
  from the snapshot, or NOT CAPTURED], `cross_references_out` [ids with captured yes/no], `handled_by`
  [rule-file paths or "NOT HANDLED: reason"], `coverage_status` [matrix §2 vocabulary], `last_amended`,
  `scope_status`, `notes`) plus a `defined_terms` list of 38 12-10 terms (captured file or NOT CAPTURED,
  with `used_by_sections`). Capture fields are read straight from `docs/research/zr-snapshots/v1/`, so
  they match the folder by construction (S1).
- `cross-reference-closure.md` — the traversal: start sets (rule citations + the benchmark reading),
  what was followed / terminal / out of scope + reason, and two checked findings (the r6b_height
  correction and the NB-06 discrepancy).
- `coverage.md` — handled (6 sections) vs not handled, grouped; the not-handled families the remaining
  options need; the 8 uncaptured 12-10 terms.
- `options-sections.md` — the eleven options in the owner-approved order (`options.py` lines 21-33), each
  with the sections it needs and captured/handled state; the open "split lot" question stays open.
- `pitfalls.md` — one row per item (topic, section, official source with number/date/status or BSA
  calendar number + year, link, one-line watch); DOB bulletins + BSA + DCP guidance; never the program's
  finding, no bulk-copied text.
- `research-log.md` — every search (source, query, result, missing item, next step), the access blocks,
  and the open discrepancies.
- `README.md` — what the library is and is not; the unreviewed-draft label; scope (R6B + C2-2, benchmark
  215-16 Northern Boulevard, the eleven options) and limits; how to extend it.

## Counts

- Sections: **73** total — **68 captured**, **5 NOT CAPTURED** (24-11, 24-111, 23-154, 77-00,
  shared-housing use/standards).
- Handled by a rule file: **6** (11-25, 23-22, 23-52, 23-362, 23-432, 23-344(a)); **67 not handled**.
- Cross-references recorded (rework 1): **162** — **104 followed**, **58 not followed** (each with a reason).
- Defined terms: **38** — **30 captured**, **8 NOT CAPTURED**.
- Pitfalls: **14** DOB Buildings Bulletins (2 rescinded: BB 2014-025, BB 2009-030) + **6** BSA
  project-specific topics + DCP guidance (reached indirectly, no page numbers cited).

## Checks (each with its direct exit code)

```
$ python3 -c "import json;json.load(open('docs/zoning-law-library/benchmark-r6b-sections.json'))"
(no output)                                                                       EXIT=0

$ python3 <capture-claim script>   # verify_captures.py, kept in scratch (not committed)
checked 73 sections and 38 defined terms against .../docs/research/zr-snapshots/v1
PASS: every capture claim matches the snapshot folder                             EXIT=0

$ python3 scripts/lanes/check_lane_paths.py --coverage
LANE COVERAGE PASS: 10191 file(s), each owned by exactly one lane.                EXIT=0

$ git diff --name-only aac892fc
docs/zoning-law-library/README.md
docs/zoning-law-library/benchmark-r6b-sections.json
docs/zoning-law-library/coverage.md
docs/zoning-law-library/cross-reference-closure.md
docs/zoning-law-library/options-sections.md
docs/zoning-law-library/pitfalls.md
docs/zoning-law-library/research-log.md
project-control/reports/M3-T006-producer-report.md                               (only allowed paths)
```

The capture-claim script lives at `/tmp/claude-0/verify_captures.py` (scratch, not a deliverable — the
packet's `allowed_paths` is exactly the seven docs files + this report). It takes the repo base as its
one argument and checks that every `captured` entry's snapshot_id + content_digest_sha256 equal the
snapshot file's and every `NOT CAPTURED` entry has no snapshot file.

An S8 text scan confirmed the only occurrences of "verified / compliant / buildable / feasible" in the
seven docs are inside prohibitions or honest negative caveats ("not re-verified", "primary page
access-blocked"); none asserts verification of a result.

## Findings checked, not copied (the brief required checking the helpers)

1. **r6b_height handles 23-432 only.** H6 reported it handles 23-431/23-432/23-433. The rule file's
   `citations[]` names 23-432 alone and its `computation` emits only the 23-432 height table; 23-431
   (street-wall location) and 23-433 (setback depth) appear in prose/interactions as context but are
   **not** formally cited and **not** computed. Both are recorded NOT HANDLED (`not_evaluated`). This is
   a real coverage gap for the base R6B envelope.
2. **NB-06 vs `zr-12-10.snapshot.json` discrepancy — CONFIRMED.** NB-06 rev 2 search S3 records the ZR
   12-10 "street, wide"/"street, narrow" text as not captured. I checked the snapshot directly: it IS
   captured (section_title "Definitions - wide street and narrow street"; contains "wide"/"narrow"/"75
   feet"; last amended 2026-03-26; digest
   `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`). NB-06's claim is stale at this
   commit. I did **not** edit NB-06 (read-only, forbidden path); logged in `research-log.md` for the
   orchestrator.

## Recommendations for the orchestrator (none made in this task)

1. **New ZR captures** (via the print/PDF node channel with a browser UA, sha-pinned): the 8 uncaptured
   12-10 terms (Mandatory Inclusionary Housing areas, UAP developments, outer court, bulk, Commercial
   District / commercial use / community facility use / residential use, development / enlargement /
   conversion, detached / semi-detached / attached / zero lot line building, required yard); ZR 23-154
   (UAP); ZR 24-11 and 24-111 (community-facility FAR); the Article VII Ch 7 77-00 family (if the
   "split lot" reading needs it); and the City-of-Yes shared-housing use/standards sections once their
   numbers are resolved.
2. **Source Access Registry — add BSA** (H4): a machine channel (NYC Open Data "BSA Applications Status"
   `yvxd-uipr` via SODA, Socrata baseline) and a human channel (the resolutions search portal, 1998+;
   resolution PDFs behind the nyc.gov bot wall). Caveats to pin: every resolution is project-specific and
   never general provenance; the dataset is "informational purposes" and does not cover the Board's full
   jurisdiction; freshness is a single `rowsUpdatedAt` signal = 1790020601 = **2026-09-21T19:56:41Z**
   (producer-computed; see recommendation 5). This is a discovery recommendation; a G1 reviewer must
   re-read api/views + the portal terms before a verified row. The registry is a forbidden path here.
3. **Coverage-matrix rows** (the file is a forbidden path here): the matrix's "Zoning Resolution text"
   row is dated 2026-07-20 and still reads `missing`; this library shows it is now `partial` for a
   handful of R6B sections. Also consider rows for the not-handled families (side yards, overlay FAR,
   community facility, parking/transit, shared housing, split lot).
4. **NB-06 correction** (research-and-verification workflow, orchestrator): fix search S3 / the freshness
   note so it records the wide/narrow text as captured.
5. **`yvxd-uipr` freshness (resolved, G1 A2):** `rowsUpdatedAt` epoch 1790020601 = **2026-09-21T19:56:41Z**
   (producer-computed with `datetime.utcfromtimestamp`), not the "Jan 17 2025" the fetch model rendered
   (that would be epoch 1737072000). Record this exact value in any BSA registry row.

## What I could not check

- No primary-page read of ZR 23-154 (HTTP 403 on both portal hosts; relied on H6's web-search summary;
  exact R6B UAP wording **not sure**).
- No capture of 24-11 / 24-111 (recorded from H6's single official read of 24-11; I did not re-open the
  page — snapshot/registry edits are out of this task's scope).
- No verbatim DOB bulletin PDF bytes (nyc.gov bot wall; `bb_2019-009.pdf` served 716 KB of unparsed
  binary). Bulletin "watch" lines are drafts from index titles + search snippets; current/rescinded
  status of several older bulletins (BB 2008-003, 2011-010, 2012-008, 2018-002) is **not re-verified**.
- No DCP Zoning Handbook page numbers (>10 MB + 403); the moved districts-tools R6 page's new URL is
  **not sure**.
- The "split lot" meaning (two buildings on one zoning lot vs a district-boundary split) and the
  shared-housing ZR section numbers are **open / not sure**; whether 215-16 Northern Blvd falls under an
  airport imaginary surface is **not sure**.
- I did not re-fetch the ~45 captured sections live (relied on the repository snapshots as the captured
  primary sources, as the brief directs); H1 live-checked 23-344 and it matched.

## Rework 1 (G1 r1 FAIL — F1 required, A1-A3 advisories)

G1 verdict was FAIL on one required finding (F1); 7 of 8 scenarios + both discrepancies verified PASS.

- **F1 (S2 closure) — FIXED.** The first pass drew cross-references from the helpers' `refers_to`
  summaries, which dropped real numbered references in eleven options-frontier sections. Rework 1 re-runs
  the producer's **own** extraction over the verbatim text + table + footnotes of **every** captured
  section and records every numbered reference in `cross_references_out` with `captured` true/false and,
  where not followed, a one-line reason. My extraction found more than the reviewer's named list (20
  sections, 54 previously-missing refs). NAICS sector codes (31-33/44-45/48-49) are excluded only inside
  the Article-32 use-group sections and documented. The "Followed" summary in `cross-reference-closure.md`
  is corrected: the options-frontier sections are captured but their onward internal references are not all
  followed.
  - Reference counts now: **162 recorded, 104 followed, 58 not followed.**
  - Zero-dropped audit (`audit_refs.py`): `TOTAL sections with missing refs: 0; total missing refs: 0`
    (EXIT 0).
- **A1 — applied.** 34-113 coverage_status `not_applicable` → `not_evaluated` (whether this lot ever
  received a floor-area bonus is an unresolved property fact); scope_status now conditional.
- **A2 — applied.** BSA dataset freshness `rowsUpdatedAt` 1790020601 = **2026-09-21T19:56:41Z**
  (producer-computed; the fetch model's "Jan 17 2025" would be epoch 1737072000). Recorded in
  `research-log.md`, `pitfalls.md`, and the recommendations.
- **A3 — applied.** `pitfalls.md` now records that BB 2016-013 rescinded BB 2014-025 **because NYS General
  City Law (GCL §36) was amended.**

Rework-1 checks (direct exit codes): JSON load EXIT 0; capture-claim script PASS EXIT 0; reference audit
zero-dropped EXIT 0; `scripts/lanes/check_lane_paths.py --coverage` PASS EXIT 0; forbidden-word scan clean;
`git diff --name-only 737d9cd5` = only the 7 docs files + this report.

## Requested status

awaiting_gate (re-review). Required gates per packet: G0, G1, G2; reviewer agents data-contract-verifier
and directive-compliance-verifier. Producer self-checks (JSON load, capture-claim, reference audit, lane
coverage, diff scope, S8 scan) all pass.
