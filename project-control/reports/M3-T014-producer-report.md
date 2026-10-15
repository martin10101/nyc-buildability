# M3-T014 producer report — zoning-law library capture-state and label corrections (DB-252, DB-272)

Producer: official-source-researcher (AI agent; unreviewed draft, ADR-007).
Worktree: `/root/project/nyc-buildability/.claude/worktrees/agent-a034e3c184e806299`.
Claim head reset to: `91a60805967a243dae97b595c94ec30b45fc3bc1` (branch `task/wave28-placement-wiring`).
Documents only. No reading, result, number, rule or coverage-status-vocabulary change. Capture state was
taken from the authoritative snapshot folder listing `docs/research/zr-snapshots/v1/` (git ls-tree), never
from a library flag; the 24-11/24-111/36-64/66-11 verbatim was read directly from the snapshot files.

## Authoritative inputs read (primary sources)

- Folder listing `git ls-tree --name-only HEAD docs/research/zr-snapshots/v1/` — zr-24-11, zr-24-111,
  zr-36-64, zr-66-11, zr-74-902, zr-74-903 all present (captured); zr-23-154 / zr-77-00 / shared-housing
  absent (genuinely NOT CAPTURED).
- zr-24-11.snapshot.json: section_title "Maximum Floor Area Ratio and Percentage of Lot Coverage";
  section_last_amended 2024-12-05; content_digest_sha256 `7ac0234975425e65cd327b114e25c4ed9bb8356d4fc79b6237ef7cb3c2227254`;
  verbatim+table name no other ZR section (0 cross-references).
- zr-24-111.snapshot.json: section_title "Maximum floor area ratio for certain community facility uses";
  section_last_amended 2024-12-05; content_digest_sha256 `77951e89b5edbbc83a9046cf88595a6355c3cc2059ef6ae6ca127ab557c4e8bb`;
  verbatim carries an "R1 R2" district header and names 73-11 (Agriculture and Open Uses), 73-13
  (Community Facilities), 73-18 (Recreation, Entertainment and Assembly Spaces), 74-902, 74-903 and 24-11.
- zr-36-64.snapshot.json (verbatim): C1-C8 — "whenever a #zoning lot# is divided by a boundary between
  districts having different requirements for #accessory# off-street loading berths, the provisions set
  forth in Article VII, Chapter 7, shall apply." → a narrow loading-berth pointer, not a C-district
  counterpart.
- zr-66-11.snapshot.json (verbatim): "66-11 Definitions" (Article VI Ch 6, TOD); defines "mass transit
  station" terms. The transit ZONES are the 12-10 defined terms (Transit Zone, Greater/Inner/Outer) +
  Appendix I. → 66-11 is not "the transit-zone definitions".

## Corrections (file:line @ edited head; before → after; source)

### A — 24-11 / 24-111 captured (DB-272) + consistency

1. `benchmark-r6b-sections.json` counts (lines 17-28): `captured 68→70`, `not_captured 5→3`,
   `cross_references_recorded 162→168`, `cross_references_followed 104→105`,
   `cross_references_not_followed 58→63`. Source: folder listing + recomputed tally over the data.
2. `benchmark-r6b-sections.json` 24-11 entry (~line 2015): `capture_status.state "NOT CAPTURED" →
   "captured"` + `snapshot_id "zr-24-11"` + `content_digest_sha256 7ac0…7254` (copied verbatim from the
   snapshot); `coverage_status "missing" → "not_evaluated"`; its cross-ref `24-111 captured false → true`;
   note "RECOMMEND capture" → "Captured M3-T009" (FAR 2.00 / coverage 80/60 reading preserved unchanged).
3. `benchmark-r6b-sections.json` 24-111 entry (~line 2036): `state "NOT CAPTURED" → "captured"` +
   `snapshot_id "zr-24-111"` + `content_digest_sha256 7795…e8bb` (copied verbatim); `coverage_status
   "missing" → "not_evaluated"`; `last_amended null → "2024-12-05"` (snapshot section_last_amended);
   `cross_references_out [] →` the 6 references its verbatim names (24-11 true; 73-11/73-13/73-18 false +
   reason; 74-902/74-903 true + reason); note "RECOMMEND capture" → captured, with the FAR-effect left
   OPEN. Source: zr-24-111 verbatim.
4. `benchmark-r6b-sections.json` 33-121 entry cross-ref (~line 1545): `24-111 captured false → true`
   (24-111 is now captured). Source: folder.
5. `coverage.md` lines 49-51: "24-11 (**NOT CAPTURED**…) and 24-111 (**NOT CAPTURED**); plus the Article
   II Chapter 4 height/yard sections (numbers unresolved)." → "24-11 (captured, M3-T009; R6B FAR 2.00,
   coverage 80/60, last amended 12/5/2024) and 24-111 (captured, M3-T009); the Article II Chapter 4
   height/yard sections (24-161/162/163, 24-33 to 24-56) are captured." Source: folder (zr-24-161/162/163,
   zr-24-33..zr-24-56 present).
6. `cross-reference-closure.md` line 30: "community facility (24-11, 24-111 — NOT CAPTURED)" →
   "(24-11, 24-111 — captured, M3-T009)".
7. `cross-reference-closure.md` lines 67-68 and 75: reference counts "162 … 68 … 104 … 58" → "168 … 70
   … 105 … 63"; "re-extracts all 68 captured sections" → "70". Source: recomputed tally (consequence of A1).
8. `cross-reference-closure.md` line 109: removed 24-11, 24-111 from the "NOT CAPTURED, in scope" list;
   added "24-11 and 24-111 (community facility) are now captured (M3-T009)."
9. `options/README.md` line 52: "24-11/24-111/24-161/24-163 and the Chapter-4 height/yard sections NOT
   CAPTURED" → "… now captured".
10. `options/option-11-combinations.md` line 27: "CF FAR (24-11/24-111, not captured)" → "… captured".
11. `options/option-11-combinations.md` line 35: "Only 24-11 and 24-111 are not captured." → "Of the
    sections this file touches, only 23-154 (UAP), 77-00 and the shared-housing use/standards sections
    remain not captured; 24-11 and 24-111 are now captured (M3-T009)." (lines 31-34 HG history kept.)
12. `options/option-11-combinations.md` line 119: "**24-11 / 24-111 are NOT CAPTURED** … Next step:
    capture them." → "**24-11 / 24-111 are captured** (M3-T009) … Next step: read/compute their FAR
    contribution to the cap."

### B — 36-64 loading-berth pointer (not a C-district counterpart)

13. `benchmark-r6b-sections.json` 77-00 note (~line 2112): "36-64 (captured) is the C-district
    counterpart." → "36-64 (captured) is only a loading-berth pointer into Article VII, Chapter 7
    (accessory off-street loading berths), not a general C-district counterpart." Source: zr-36-64 verbatim.
14. `coverage.md` lines 64-66: "77-00 (**NOT CAPTURED**) with 36-64 as the C-district counterpart." →
    "77-00 (**NOT CAPTURED**); 36-64 (captured) is only a loading-berth pointer into Article VII, Chapter 7
    (accessory off-street loading berths), not a general C-district counterpart." (77-00 stays NOT CAPTURED.)

### C — 66-11 mass-transit-station Definitions (not the transit-zone definitions)

15. `coverage.md` line 53: "66-11 (transit-zone definitions)" → "66-11 (Article VI Chapter 6
    "Definitions" — defines the "mass transit station" terms, not the transit zones; the transit-zone
    definitions themselves are the 12-10 defined terms Transit Zone, Greater / Inner / Outer plus
    Appendix I)." Source: zr-66-11 verbatim + the 12-10 transit-zone term snapshots.

### D — label tidy (ADVISORY) — NOT APPLIED

- `coverage.md` line 44 "32-131 / 32-161 (commercial use permission)". The plan's proposed rewrite adds a
  new citation (32-421) and restructures the label — that is more than a plain label fix, so under the
  brief's condition ("D is optional: apply it if it is a plain label fix") it is NOT applied. Left as-is.

## Necessary-consequence edits beyond the plan's literal enumeration (disclosed)

Capturing 24-111 brings its snapshot verbatim into the cross-reference audit's scope. Its verbatim names
6 numbered references, so to keep the audit "zero dropped" (S2) and the catalogue true to the captured
text, I recorded those 6 in 24-111's `cross_references_out` (correction 3), updated the cross-reference
counts (corrections 1, 7), flipped the stale 24-111 cross-ref flag in 33-121 (correction 4), and set
24-111's `last_amended` from the snapshot. All are inside allowed files, documents-only, faithful to the
captured verbatim/folder; none changes a reading, FAR value or result. 74-902/74-903 are recorded
`captured: true` mirroring the existing M3-T011 attribution already in 33-121.

## Group F — open reading questions (preserved, NOT resolved; named for a research task)

- Whether 24-111 (R1 R2 header) changes the R6B community-facility FAR vs 24-11 at 2.00 (option-06-07
  reads it as deferring to 24-11 at 2.00). Left OPEN in the 24-111 note.
- The "split lot" meaning: two buildings on one zoning lot vs a district-boundary split (option-08).
- Whether a C2-2 overlay edge is a Chapter-7 district boundary (option-08).
- The full 35-31 "except where explicitly stated otherwise" carve-out sweep (option-11 lines 116-118).
- 23-154 (UAP, HTTP 403), the 77-00 family and the shared-housing use/standards sections stay genuinely
  NOT CAPTURED.

## Out-of-allowed-path observations (NOT edited — reported for a follow-up)

These are outside this task's allowed paths; the packet declares the first advisory-only. None is a stale
claim inside the five corrected files.
- `options-sections.md` line 114 still literally reads "36-64 … as the C-district counterpart"; the same
  file corrects it at lines 121-122. Packet path_notes marks line 114 an ADVISORY consistency tidy only.
- `options/research-log.md` lines 38 and 53 are historical helper search rows recording "zr-24-* NOT
  CAPTURED / next step capture" and transit-zone-inner items — dated research records, not current claims.
- `option-08-split-lot.md` (line 83) and `option-10-parking-and-transit-zone.md` (line 60) quote the old
  36-64 / 66-11 phrasings only to refute them (corrections already present).

## Checks (each with its direct exit code)

```
$ python3 -c "import json;json.load(open('docs/zoning-law-library/benchmark-r6b-sections.json'))"
(no output)                                                                               EXIT=0

$ python3 -c "import json;d=json.load(open('docs/zoning-law-library/benchmark-r6b-sections.json'));print(d['counts']);[print(s['section_id'],s['capture_status']) for s in d['sections'] if s['capture_status'].get('state')!='captured']"
counts captured 70 / not_captured 3; only 23-154, 77-00, shared-housing-use-and-standards NOT CAPTURED  EXIT=0

$ python3 /tmp/claude-0/M3-T014/verify_captures.py .   # capture-claim check (verify_captures.py contract)
checked 73 sections and 38 defined terms …; PASS: every capture claim matches the snapshot folder     EXIT=0
#   (same script FAILED on the baseline 91a60805 head: 24-11 and 24-111 NOT CAPTURED while their
#    snapshot files exist — R2/S2 — then PASS after the fix.)

$ python3 /tmp/claude-0/M3-T014/audit_refs.py .        # cross-reference audit (audit_refs.py contract)
audited 70 captured sections; TOTAL sections with missing refs: 0; total missing refs: 0              EXIT=0
#   (validated: reports 0 dropped on the baseline 68 captured sections too, matching the committed claim)

$ python3 scripts/lanes/check_lane_paths.py --coverage
LANE COVERAGE PASS: 10831 file(s), each owned by exactly one lane.                                     EXIT=0

$ grep -rnEi '(24-11|24-111|36-64|66-11)' docs/zoning-law-library/ | grep -Ei 'not captured|transit-zone definition|C-district counterpart|"captured": false'
no stale hit inside the five corrected files (remaining hits are correction narratives / historical log /
the documented advisory options-sections.md:114)                                                       EXIT=1(no-match within scope)

$ git diff --stat
only the five allowed library files changed (benchmark-r6b-sections.json, coverage.md,
cross-reference-closure.md, options/README.md, options/option-11-combinations.md)                      OK
```

The capture-claim check (`verify_captures.py`) and cross-reference audit (`audit_refs.py`) are scratch
tools (not deliverables), reconstructed in `/tmp/claude-0/M3-T014/` from the contracts documented in
`docs/zoning-law-library/research-log.md`, the M3-T006 producer report and `cross-reference-closure.md`
("Reproduce"). Both were validated against the committed baseline (capture-claim fails on exactly 24-11
and 24-111; audit reports 0 dropped over the baseline 68) before use.

## Requested status

awaiting_gate. Required gates per packet: G0 (recorded), G1 (data-contract-verifier — re-run the
capture-claim check + cross-reference audit at the frozen head as acceptance evidence),
G2 (directive-compliance-verifier — in-regime DCV for D-094-R102). No code change; no pytest needed.
