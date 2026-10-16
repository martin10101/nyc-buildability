# M3-T015 reviews (every return kept unchanged)

- One producer round (official-source-researcher, worktree): builder commit 940ffa12 (parent the contract head b7f47369) integrated as the cherry-pick b32a17b3 on task/wave29-scenario-drawings (46 files: 19 new canonical ZR snapshots, 19 byte-identical bundle copies produced by running sync_zr_snapshots.py, 7 law-library files, the producer report; every file inside the packet's allowed paths; LF sha256 of each equal to the builder's return). Documents only; no api code, test or sync script changed.
- G0 PASS at the contract head (orchestrator). G2 orchestrator self-check at b32a17b3: the 46 files equal the builder's digests; nothing outside the allowed paths; the capture folders stay prose-only (no table_digest on a prose capture); 23-154 stayed NOT CAPTURED (HTTP 403, no node invented); the whole api suite passed on the increment (10116 passed, 8 skipped; api-suite-M3-T015.log); lane coverage PASS; research record check PASS.
- G1 data-contract-verifier: PASS with one advisory (two 35-36 cross-reference reason fields gained a '(SPDist1 null)' lot-applicability clause; factually sound, source-backed, changes no number or vocabulary value). Seven sections re-opened live on the official site this pass (77-22 node 18899 cross-checked); content_digest == sha256(excerpt) on all 19; no stray table_digest; bundle byte-identical; 23-154 re-confirmed 403; the library capture-claim invariant holds (71 captured / 2 not).

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

VERDICT: PASS (G1 — data-contract-verifier: official-source captures) for M3-T015 at commit b32a17b36cbde8bb8900fec1194ef605d0f22e41 (wave-29). One ADVISORY only; no REQUIRED defects. I am an AI agent; this is not a human or professional review.

## What I verified (reproduced independently, frozen SHA b32a17b3)

OFFICIAL-SOURCE RE-CHECK (7 sections re-opened live on zoningresolution.planning.nyc.gov this pass; the 4 named + a 73-1x heading + two more):
- 77-22 Floor Area Ratio — title, Last Amended 12/5/2024, body MATCH verbatim; node 18899 confirmed by reading its entityprint/pdf/node/18899 PDF ("77-22 - Floor Area Ratio", banner 10/15/2026). The HTML `<ol>` renders (a)/(b) in the section's own print (snapshot keeps (a)/(b); a markdown viewer shows 1./2. — same words).
- 77-11 — title + Last Amended 6/29/1989 MATCH; the fetched 3rd paragraph is byte-verbatim to the excerpt; the first two paragraphs came back paraphrased by the fetcher but are substantively identical (Dec 15 1961 / >50% / 25 ft / perpendicular / R3-2 / R4).
- 77-211 — title + 12/5/1990 MATCH; full body MATCHES verbatim including (a)/(b).
- 76-131 — title "Boundary line parallel to the short dimension of block" + 12/15/1961 MATCH; body (a)/(b)/(c) 200/150/100 ft district lists MATCH verbatim.
- 35-36 — title + 12/5/2024 MATCH; confirmed heading-only (no own body; children 35-361/35-362) — excerpt = number+title, correct.
- 73-13 — title "Community Facilities" + 6/6/2024 MATCH; heading-only confirmed (children 73-131..136).
- 77-00 — title "GENERAL PROVISIONS" + Last Amended 8/14/1987 MATCH; heading-only confirmed. (These unusual per-section dates differ from the chapter banner, exactly as the producer disclosed; taken from the page.)
Node ids are honest, not invented (node 18899 cross-check passed; S5 respected).

STRUCTURAL (all 19 new snapshots, both trees):
- content_digest_sha256 == sha256(verbatim_excerpt) on every file (19/19). Spot values match the producer report table (73-11 9cfacedc, 77-22 90af26a3, 35-36 ff9d0e7e); the §4 whole-file LF-sha256 list reproduces exactly.
- NO file carries table_digest_sha256 and none carries a table/tables payload (19/19) — correct, all prose.
- snapshot_id == filename, schema zr_section_snapshot/v1, extraction_status extracted_draft, raw_html_verified=false, ADR-007 label present on every file; no determination status words ("verified"/compliant/feasible) anywhere.
- Each bundled copy under services/api/app/_zr_snapshots/v1/ is byte-identical to its canonical (19/19). Both trees hold 274 snapshot files.

GUARDS FAIL CLOSED (disconfirming — green tests are not vacuous; proven in-memory against app.rules.snapshots at the frozen SHA):
- A 1-char mutation to zr-77-22's excerpt makes _digest != stored (load would raise) — content_digest guard is live.
- A stray table_digest_sha256 on a prose capture raises SnapshotError; a table payload without a digest raises; a correct table+digest passes (positive control). So the "no stray table_digest" invariant is machine-enforced.
- 23-154: independently re-confirmed HTTP 403 Forbidden on the section URL this pass. Producer correctly wrote no file (neither tree), left the library 23-154 entry NOT CAPTURED, recorded a dated access-blocked note; no node invented. S4/S10 satisfied; stays UNKNOWN (also owner N1 "split lot" meaning stays OPEN).

LIBRARY CAPTURE-STATE RECONCILIATION:
- Diff is capture-state flags + notes ONLY across the 7 files; no computed number, no coverage-vocabulary value change, no rule, no reading-for-a-lot. Option 8's "split lot" meaning stays OPEN ("This question stays open", "not sure which reading", "whether a C2-2 overlay edge is a Chapter-7 district boundary … UNRESOLVED" all preserved); 24-111's R6B CF-FAR effect stays an OPEN reading ("project-specific carve-out, not followed"). option-02-03 and all forbidden paths untouched.
- benchmark-r6b-sections.json counts reconcile: 73 total = 71 captured + 2 not_captured; the 2 remaining uncaptured are exactly 23-154 and shared-housing-use-and-standards. Defined terms 30 captured / 8 not = 38, untouched by this task.
- Capture-claim invariant holds: all 76 snapshot_id-bearing entries resolve to real files; no captured:false flag left stale where a file now exists; no NOT-CAPTURED entry carries a snapshot_id; 77-00 flipped to captured with snapshot_id zr-77-00 + content_digest bd37979c (matches the file).
- Extra 35-30/35-31 -> 35-36 cross-ref flips (beyond the named 77-00 + 73-11/13/18): JUDGED SOUND. zr-35-36 now exists, so flipping captured:true + snapshot_id is a necessary reconciliation (leaving false would be a stale flag). See ADVISORY-1 on the reason wording.

TESTS RE-RUN (lanes venv, from the archived tree, heavy multi-file run under flock):
- python services/api/scripts/sync_zr_snapshots.py --check -> "OK … 274 file(s)", exit 0.
- pytest tests/rules/test_zr_snapshot_bundle.py tests/rules/test_zr_snapshot_table_digest.py tests/drawings/report/test_report_law_links.py -> 41 passed, exit 0.

## Findings

ADVISORY-1 (benchmark-r6b-sections.json lines 1607 and 1646): the two 35-36 cross-ref `reason` fields were reworded from "…NOT CAPTURED; not yet followed" to "…CAPTURED (M3-T015…); not followed for this lot (SPDist1 null)". "(SPDist1 null)" is a newly introduced (not pre-existing) lot-applicability clause inside a reason field, which is a touch beyond strict "capture-state only." It is factually sound and non-blocking: the benchmark lot having no special purpose district (spdist1/2/3 absent from the served PLUTO row, BBL 4073340070) is an established, source-backed fact across docs/reference-cases/R6B (step-p1/step-p3 and multiple hand-calculation records already use the exact phrase "SPDist1 null"); 35-36 is a special-area provision, so "not followed" for a lot in no special area is correct. It changes no coverage-vocabulary value, number, option meaning, or 24-111 effect. Optional correction: revert to "not yet followed" to keep the reason purely capture-state, or leave as-is since it restates an established fact. Does not block PASS.

## What I did NOT check
- I re-fetched full bodies for 7 of 19 sections (a representative spread incl. all unusual Last-Amended dates); I did not independently re-fetch the bodies of 73-11, 73-18, 77-01, 77-10, 77-12, 77-20, 77-21, 77-24, 77-25, 77-26, 77-27, 77-28 — their digests are internally consistent and the producer's print/PDF cross-check = match. For 77-11 two paragraphs were only paraphrase-level confirmed (title/date/3rd-paragraph verbatim confirmed).
- raw_html_sha256 is a per-session whole-page pin (non-reproducible Drupal chrome, as documented); I relied on content_digest, not the raw-HTML digest.
- I did not re-run the "extractor reproduces zr-35-31 byte-for-byte" step (unnecessary — I compared excerpts directly to the official pages, which is stronger).
- The full D-094 R102/R258 directive-compliance pass is the separate directive-compliance-verifier's job (verification.json); from my capture-focused scope the documents-only / primary-official-source / provenance discipline those requirements call for appears satisfied.
- Full api pytest is CI's job (documents-only task, no api code touched; the review register pins no edited file).

Reproduction: archive b32a17b3 to scratch (`git -C /root/project/w-wave29 archive b32a17b3 | tar -x -C <scratch>`); digest/table/byte-identity via python over docs/research/zr-snapshots/v1 vs services/api/app/_zr_snapshots/v1; invariant via counts + snapshot_id resolution over docs/zoning-law-library/benchmark-r6b-sections.json; sync --check and the three pytest files under /root/project/lanes-runtime/heavy-run.lock with the lanes venv; official re-check via the section URLs and entityprint/pdf/node/18899.

END-OF-REPORT
