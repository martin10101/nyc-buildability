# M3-T012 producer report (official-source-researcher)

Task: record NB-07 (215-16 Northern Boulevard, BBL 4073340070 is outside every Mandatory
Inclusionary Housing area and every former Inclusionary Housing designated area), its two
index lines, and the NB-05 half of backlog row DB-274. Documents only.

I am an AI agent. Nothing here is a professional or legal review. The membership facts are
answered from the primary DCP layers; the downstream affordable-housing reading stays an
unreviewed draft (ADR-007). Nothing is labelled Verified.

Setup: worktree `/root/project/nyc-buildability/.claude/worktrees/agent-acb00a793b175796a`
(show-toplevel is NOT the primary checkout or any forbidden worktree); `git fetch` then
`git reset --hard 593f8c7ace9e807cd9ecd0790c87489e16827965`; HEAD confirmed at that sha with an
empty `git status --porcelain` before any edit.

## What I did

1. Copied the validated draft record verbatim into
   `docs/research/evidence-records/NB-07-mih-inclusionary-status.json`
   (`diff` draft vs placed = identical; valid JSON). I did not re-author it.
2. Re-verified every field against the two sealed independent returns
   (`return-research-MIH.md`, `return-check-MIH-independent.md`) and the README format.
3. Added one NB-07 index line to the evidence-records paragraph of `docs/RESEARCH_REQUESTS.md`
   and one NB-07 row to the records table in `docs/research/evidence-records/README.md`
   (status cell `answered_from_primary_source` = the record's `conclusion.research_status`).
4. NB-05 (DB-274 half): bumped `revision` 6 -> 7 and clarified the revision-6
   `dependency_assessment` entry's `(revision 5)` parenthesis so it reads as the previous code
   identity now superseded (not the revision in which the refresh happened). No reading, value,
   code identity or status changed.

## Field-by-field re-verification of NB-07 (every field checked; nothing corrected)

- `schema` research_record/v1; `record_id` NB-07; file name starts with it; `revision` 1;
  `last_changed`/`retrieved`/`checked_on` 2026-10-15 (live-fetch date in both returns).
- `question`: text/property (215-16 Northern Boulevard, Queens; borough 4 block 7334 lot 70;
  BBL 4073340070); lot_scope zoning_lot_unconfirmed (NB-01); site_scope whole_site; time_scope
  current_law. All in-vocabulary.
- E1 MapPLUTO (gis_geometry): ZoneDist1 R6B, Overlay1 C2-2, LotArea 10075 sq ft, centroid
  EPSG:2263 (1048850.089, 216370.771), 5-vertex ring byte-identical to the committed fixture -
  matches return-research-MIH (lot facts) and return-check-MIH (byte-identical ring). document_date
  carries the 26v2 release caveat (RISK 3); saved_copy/sha256 null (live fetch).
- E2 nycmih (gis_geometry): serviceItemId 491d74ba..., SR 2263, dataLastEditDate 2026-09-30;
  full ring + centroid intersect 0; nearest 'Douglaston Parkway Rezoning' (CD 11) 5,925 ft; next
  '217-14 24th Avenue Rezoning' 7,501 ft; the "not for tax-lot-level eligibility" disclaimer quoted.
  Matches both returns.
- E3 nyih (gis_geometry): serviceItemId e0806bbb..., SR 2263, w83z-2kf9, dataLastEditDate
  2026-09-09; full ring + centroid intersect 0; no nyih feature in CD 11; nearest 'Jamaica'
  (CD 12, adopted 2007-09-10) 17,618 ft. Matches both returns (the 17,618 ft figure is the
  independent check's exact distance).
- E4 ZR Appendix F (map_document): landing node 21424, Last Amended 9/24/2026, retrieved
  2026-10-14; Queens CD 11 Map 1 (3/13/19) and Map 2 (2/24/26), both portions; map images not
  transcribed. saved_copy `docs/research/zr-snapshots/v1/zr-appendix-f.snapshot.json` exists at
  head; its LF-normalized whole-file sha256 I recomputed at HEAD =
  `0a7952bd26c7adb509283e67d689e9ad54f16c73870594f61640c16edaa40008`, equal to the pinned value
  (no correction). Only E4 carries a saved_copy.
- E5 ZAP P1998Q0688 (filing_record): bounded block-7334 search returns one project, STARBUCKS
  unenclosed sidewalk cafe, Withdrawn-Other, certified 1999-10-21; bounded, not a city-wide
  negative. Matches return-research-MIH.
- meaning_and_applicability: provisions_read (Appendix F, 27-131, 27-133, 12-10 qualifying
  affordable housing, 23-22, 23-432, 27-111/UAP referenced-not-re-derived); exceptions_considered
  (UAP outside MIH; regulatory agreement; qualifying residential site R1-R5 only); applies
  conditional. reading carries the headline membership fact plus the downstream pathway labelled
  an unreviewed draft.
- measurement_basis.quantities: nearest MIH-area edge 5925 ft and nearest former-IH-area edge
  17618 ft, basis gis; double_count_risk "none identified".
- conclusion: research_status answered_from_primary_source; 5 observed_facts (facts only, no law
  reading); interpretation carries the UAP/23-22/23-432 reading as a draft; conflicts [] (the two
  returns agree); 3 conditions (layer disclaimer + un-transcribed Appendix F map; zoning lot
  unconfirmed; pathway awaiting review ADR-007); settled_by names E2/E3/E4 + the two researchers.
- searches: 3 (found, found, not_found for the un-transcribed metadata PDFs with a next step);
  status is not a dead-end status, so no dead-end search entry is required.
- implementation: affected_outputs (option2/3/11 pathways); code_paths [] and code_identity {}
  (no MIH/IH connector wired; `zoning_features_arcgis.py` has no MIH/IH layer; a wired check is
  future work); worked_example prepared_by official-source-researcher, "not professionally
  checked"; dependency_assessment notes map_based_rules._inclusionary_housing reports "Check
  needed" and is unchanged by this record.
- review: producer orchestrator; two agent_reviews (official-source-researcher and
  data-contract-verifier), both verdict agrees, reviewed_revision 1, reviewed_code_identity {},
  report null, each reproducing its sealed return; professional_review null.
- freshness: method live_fetch, snapshot_date null, limitation records the 26v2/metadata-PDF/
  Appendix-F-image caveats. promotion.requested_label Provisional (nothing Verified).

Corrections made to the draft: none. The placed record is byte-identical to the validated
draft and every field reproduces the two returns; E4's sha was independently recomputed at HEAD
and already matched.

## NB-05 (DB-274 half)

Only change: `revision` 6 -> 7 and a text clarification of the last `dependency_assessment`
entry. The `(revision 5)` parenthesis now reads "superseding the previous (revision 5) identity"
with an added note stating the parenthesis names the previous code identity now superseded, that
nothing substantive changed, and that this is the DB-274 NB-05 half. No evidence, reading,
measurement value, code_identity, review or status changed; its checker line (status, code_current,
review_state, requested_label) is unchanged from the pre-edit baseline.

## Checks (commands and exit codes)

- `python3 tools/research_record_check.py --check` -> exit 0 (PASS). 7 records; NB-07 present:
  `status=answered_from_primary_source code_current=True review_state=current
  requested_label=Provisional`. NB-05 line byte-identical to the pre-edit baseline. No other
  record's line changed.
- E4 LF sha256 recompute at HEAD -> `0a7952bd26c7adb509283e67d689e9ad54f16c73870594f61640c16edaa40008`
  (matches the pin).
- `python3 scripts/lanes/check_lane_paths.py --coverage` -> exit 0 ("LANE COVERAGE PASS: 10684
  file(s), each owned by exactly one lane").
- `git diff --name-only` -> the three tracked files below; `git status --porcelain` additionally
  shows the new NB-07 record. All five are allowed paths; no forbidden path touched.

## Files changed (all within allowed_paths)

- `docs/research/evidence-records/NB-07-mih-inclusionary-status.json` (new)
- `docs/RESEARCH_REQUESTS.md` (one NB-07 index line)
- `docs/research/evidence-records/README.md` (one NB-07 table row)
- `docs/research/evidence-records/NB-05-special-density-area.json` (revision bump + parenthesis
  clarification)
- `project-control/reports/M3-T012-producer-report.md` (this report)

## What I could not check / limitations

- I did not re-run the live DCP nycmih/nyih/MapPLUTO/ZAP fetches; I relied on the two sealed
  independent returns and corroborated only the repository-side fact I can verify at HEAD: E4's
  LF sha256 against the committed Appendix F snapshot (matches).
- The nycmih/nycihda field-level metadata PDFs are binary and were not transcribed (recorded in
  `searches` and `freshness.limitation`); the Appendix F CD 11 map image (the legal instrument)
  is not transcribed. The membership fact is robust given the 5,925 ft / 17,618 ft margins, but a
  definitive legal determination reads the Appendix F map image. The record keeps these as
  conditions and label Provisional; nothing is Verified.
- The downstream UAP / 23-22 / 23-432 reading is an unreviewed draft (ADR-007); this task computes
  no value and wires no connector.
