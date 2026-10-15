# M3-T013 reviews (every return kept unchanged)

- Two producer rounds (backend-engineer, worktrees): round 1 builder commit 06651e8d (parent the claim head 1cbc8ccf) held off the branch while the evidence record NB-06 belonged to M5-T172, then integrated as c1061735 after M5-T172's acceptance (the 78 files equal the builder commit's); round 2 builder commit 0a428b64 integrated as 7785d0de (scope correction 1 at 7ab85ce8: NB-06 revision 6 re-pins evidence E10 to the signed zr-23-432 file; files equal). Nothing outside the allowed paths.
- G2 orchestrator self-check at 7785d0de: 37 table-bearing captures signed (glob-derived, including zr-22-131) with their bundled copies byte-identical; no excerpt digest moved; research_record_check PASS with NB-06 current; whole api suite at round 2 (builder) 10116 passed, 0 failed.
- Reviews of round 1 at 06651e8d: G1 data-contract-verifier PASS; G3 code-reviewer PASS (three advisories); G4 qa-engineer PASS with one REQUIRED item (F1, the NB-06 whole-file pin), closed in round 2. Delta checks of the integration and round 2 at 7785d0de follow each original return below.

Every reviewer is an AI agent; none is a human or professional review.

## G1 (data-contract-verifier)

G1 DATA-CONTRACT VERIFIER report — M3-T013 (ZR snapshot table-payload tamper-evidence, DB-276). I am an AI agent; this is an independent, read-only review, not a human/professional sign-off. Reviewed PINNED builder commit 06651e8d (parent/claim head 1cbc8ccf) entirely via `git show`/in-memory (the commit is not on the branch; working-tree HEAD is dc8449d1). All findings are reproducible.

VERDICT: PASS. The data contract is correct and complete. The only open item (NB-06 E10 re-pin) is explicitly the known second round after M5-T172 and is not a defect of this commit.

WHAT I CHECKED (each independently, not from the producer's claims):

CHECK 1 — set re-derivation. My own glob over docs/research/zr-snapshots/v1/*.snapshot.json at 1cbc8ccf (255 files) yields EXACTLY 37 table-bearing files = 18 `tables` + 18 `table.rows` + 1 `table.row_groups`, INCLUDING zr-22-131; none carries both `table` and `tables`. This equals the 37 signed files. PASS.

CHECK 2 — additive-only change. git diff 1cbc8ccf..06651e8d: 78 files = 37 canonical + 37 bundled + 4 non-snapshot (snapshots.py, RULES_ENGINE_ARCHITECTURE.md, the new test, the producer report). For each of the 74 snapshots: exactly one JSON key added (`table_digest_sha256`), zero removed; every other key value byte-identical; `content_digest_sha256` unchanged; unified diff shows exactly one added line and no removed/changed line (the field sits on the line above content_digest, so that line stays byte-identical). All 37 bundled copies are byte-identical to their canonical file at the new head. Zero non-table snapshots changed. PASS.

CHECK 3 — digest recomputation. I recomputed sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",",":")).encode()) over the parsed payload for all 37; all 37 match the stored value (0 mismatches). Producer-report values spot-checked for 5 files — match. PASS.

CHECK 4 — loader rule + fail-closed. snapshots.py diff is purely additive (three helpers + one call inserted AFTER the unchanged content_digest check). I exec'd the actual shipped module and drove every case: valid table.rows/tables/row_groups load; digest mismatch, payload-without-digest, digest-without-payload, empty-string digest, both table+tables, table-without-rows/row_groups, tables-not-a-list all raise SnapshotError; non-table loads; key-reorder canonicalization stable. Documented shapes (table.rows / tables / table.row_groups) match the code. No captured text/value/reading changed; citation content_digests 943b65f9 (zr-23-22) and 9fab7be8 (zr-23-432) are unchanged and still equal sha256(verbatim_excerpt), so the rule/reference-case/register/library pins keyed on them do not move. All 255 production snapshots still load (37 signed, 218 payload-free). PASS.

CHECK 5 — doc §5.1. Accurate: documents the three mutually-exclusive shapes with real examples, the exact canonical form, parsed-payload rationale, fail-closed behavior, and that the field is additive metadata changing no fact/rule/calc/result/label. PASS.

CHECK 6 — whole-file-hash pin sweep (second-round scope). I scanned all 7 evidence records: 36 saved_copy pins to zr-snapshots; EXACTLY ONE pins a table-bearing snapshot — NB-06 (docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json) evidence E10 → zr-23-432.snapshot.json. Its pinned hash == old whole-file LF sha256 37c1414c…; the new whole-file LF sha256 is ae06010e… — exactly the producer's re-pin target. research_record_check.py validates saved_copy via _sha256_lf (whole-file, CRLF→LF) and scans ONLY docs/research/evidence-records/*.json, so NB-06 E10 is the sole LIVE enforced whole-file pin that breaks. No rule file, review_register, reference case, or pytest pins a snapshot's whole-file hash (their pins are content_digest over the excerpt, which did not move) — the producer's claim is accurate.

FINDINGS:

F1 (ADVISORY — known/handled, round 2) NB-06 E10 whole-file re-pin is REQUIRED for tools/research_record_check.py --check to pass, but is explicitly the second round after M5-T172 (NB-06 is an M5-T172-owned forbidden path here). Independently confirmed OLD 37c1414c2f1fb93404dca4178d70304c6f39eeecf0f39aa215bd2754cd16887a → NEW ae06010e91a8fae0017f7a33a671c8ce5750c8ddb4f25a647a92ca79c1280898; E10's reading/labels are unchanged (only file bytes moved by the additive field). Correction: add NB-06 to allowed_paths and re-pin E10.sha256 as a scope correction after M5-T172 accepts. Not a defect of this commit.

F2 (ADVISORY — scope-completeness note) Two historical producer reports mention OLD whole-file hashes of table-bearing snapshots: project-control/reports/M3-T009-producer-report.md (zr-24-11, zr-24-111, zr-24-162, zr-24-34, zr-24-522) and project-control/reports/M5-T160-producer-report.md (zr-23-432). These are report prose, NOT enforced pins — no tool validates them — so no correction is owed; recorded only so round 2 is not surprised by stale hashes in reports. No other file pins any snapshot's whole-file hash.

F3 (ADVISORY) The new test test_zr_snapshot_table_digest.py is substantive and non-tautological: test_digest_bearing_set_equals_glob_set asserts digest_set == glob_set (and zr-22-131 present), which is the real S1 guard backing the hard-coded count constant; mutation + revert-direction (content_digest blind to the table edit) proofs for all three shapes; both-direction fail-closed; non-table pass; canonicalization stability. Independently re-derives the canonical form rather than importing the production helper.

WHAT I COULD NOT CHECK (and why): I did not run the full api pytest suite. The producer and the brief note 4 pre-existing failures (tests/rules/test_zoning_rule_review_register*.py "orphan calculation page": calc-area-allocation.md, calc-first-placement.md) that originate from M5-T172 placeholder pages removed on the branch at dc8449d1, not from this commit — handled elsewhere per the brief; I did not reproduce them and they are byte-identical to the claim head in this commit's diff (not touched). I did not read live ZR pages (R6B readings settled in docs/reference-cases/R6B/cases/; this task adds integrity metadata only, changing no captured value). CI-green-at-head is the orchestrator's read before accept.

Net: the G1 data-contract scope is fully satisfied at content identity 06651e8d. PASS, with the NB-06 E10 re-pin to be applied by the orchestrator as the already-identified second round after M5-T172.

END-OF-REPORT

## G1 (data-contract-verifier, delta check)

G1 DATA-CONTRACT VERIFIER — M3-T013 round-2 delta (ZR snapshot table-payload tamper-evidence, DB-276). I am an AI agent; this is an independent, read-only review, not a human/professional sign-off. Reviewed at PINNED head 7785d0dedaa538a2241dbd700813a77388d367ab in /root/project/w-wave20 (HEAD unchanged before and after every run). All findings reproducible.

VERDICT: PASS (G1 share of the round-2 delta). The integration equals the reviewed round-1 commit; round 2 closes the round-1 G4 F1 NB-06 re-pin with no other effect.

WHAT I CHECKED (each re-derived, not from the producer's claims):

1. ROUND-1 INTEGRATION IDENTITY. `git diff 06651e8d c1061735 -- <the 78 files of 06651e8d>` = EMPTY (exit 0). Integration c1061735 is byte-identical to the reviewed builder commit over exactly those 78 files. (The full tree differs only by other accepted tasks on the branch — M3-T014/M5-T172/T189/T190 — none in this task's 78 files.) PASS.

2. ROUND-2 DELTA = minimal. `git diff c1061735 7785d0de` touches exactly TWO files: NB-06 and M3-T013-producer-report.md (both in allowed_paths; NB-06 added by scope correction 1). No snapshot, loader, doc, test, rule, register or reference case changed. Builder round-2 commit 0a428b64 is byte-identical to integration 7785d0de over those two files (empty diff). PASS.

3. NB-06 E10 RE-PIN. Recomputed LF sha256 (`git show 7785d0de:…zr-23-432.snapshot.json | tr -d '\r' | sha256sum`) = ae06010e91a8fae0017f7a33a671c8ce5750c8ddb4f25a647a92ca79c1280898 — EXACTLY the new E10.sha256; old was 37c1414c…; bundled copy app/_zr_snapshots/v1/zr-23-432 hashes identically. NB-06 diff = revision 5→6, E10.sha256 re-pin, one appended implementation dependency_assessment entry. PASS.

4. DEPENDENCY ASSESSMENT IS TRUE. zr-23-432 change across the whole task (1cbc8ccf→7785d0de) = ONLY `+table_digest_sha256`; verbatim_excerpt and content_digest_sha256 (9fab7be8…) byte-identical, and content_digest still == sha256(verbatim_excerpt) (recomputed, MATCH). E10 excerpt byte-stable (the R6B 30/45/55 ft base-height readings unchanged). The assessment's statements are accurate. PASS.

5. CODE IDENTITY + READINGS UNCHANGED. NB-06 implementation.code_identity byte-identical rev5→rev6; interpretation/conditions untouched (only the three diff hunks above). PASS.

6. NOTHING VERIFIED. research_status=interpretation_awaiting_review; promotion.requested_label=null; professional_review=null. The only "Verified" strings in NB-06/zr-23-432 are negative ("Nothing … is a Verified …"; "not professionally verified"). PASS.

7. research_record_check.py --check → exit 0, PASS; NB-06 code_current=True, requested_label=None. No other record/snapshot pin moved (round-2 delta = 2 non-snapshot files; all 7 records' pins current). Round-1 G4 F1 is now CLOSED. PASS.

8. README correctly NOT changed: its index format is `| Record | Question | Research status |` (no revision column), so S10 owed no edit. PASS.

FINDINGS: none (no REQUIRED, no ADVISORY) for the G1 round-2 delta scope.

NON-BLOCKING OBSERVATIONS (pre-existing, not this task): NB-06 review_state=stale/reviewed_revision=2 and NB-04 code_current=False are reported-not-failed by the tool and predate this delta.

WHAT I COULD NOT CHECK: I did not re-fetch live ZR pages (R6B readings settled in docs/reference-cases/R6B/cases/; this delta re-pins a saved-copy hash and changes no captured value). I did not run the full api pytest/modularity (outside the records-only round-2 delta scope; CI-green-at-head is the orchestrator's read before accept). research_record_check ran against the clean checkout at 7785d0de (HEAD verified unchanged across the run), not an archive, because the read-only guard blocked scratch tar extraction; it is a light hashing run, not a heavy suite.

Net: round 2 closes G4 F1 cleanly and the integration equals the reviewed commit. PASS.

END-OF-REPORT

## G3 (code-reviewer)

GATE REPORT — M3-T013 (wave 28) G3 code review. Reviewer: code-reviewer (independent, READ-ONLY AI agent; not a human/professional review). Reviewed SHA: 06651e8d57067e6523b2f0d0cd59723b3b2fad69 (parent/claim head 1cbc8ccf).

VERDICT: PASS. No REQUIRED findings. Three ADVISORY/observational notes below.

WHAT I CHECKED (reproducible; extracted copy at the pinned SHA via `git -C /root/project/w-wave20 archive 06651e8d | tar -x`; lanes venv; heavy runs under flock heavy-run.lock):

1. Loader change (services/api/app/rules/snapshots.py, +74 lines, now 261 lines). Correct and clean. Order of checks matches the contract: verbatim_excerpt presence -> unchanged content_digest_sha256==sha256(excerpt) -> new _verify_table_digest(raw). The new check runs strictly AFTER the excerpt digest. _canonical_table_digest uses json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",",":")).encode("utf-8") exactly per spec, over the PARSED payload. _table_payload enforces table XOR tables (both -> SnapshotError), requires a table dict with rows/row_groups, requires tables to be a list. Fails closed on: digest mismatch, payload-without-digest, digest-without-payload, both-shapes, unexpected table shape. Non-table snapshots unaffected.

2. Error messages never echo untrusted content at length: only snapshot_id + the digest strings ({stored!r}/{actual!r}) are echoed — identical pattern to the pre-existing content_digest message. The potentially large table payload is NEVER echoed. Satisfied.

3. Loader callers / in-memory constructors: searched every caller of load_snapshot_file and SnapshotStore and every tests/tools file constructing "table"/"tables" dicts. All production callers (law_links.py, dsl.py, evaluator.py, registry.py, named_street_override_matching.py) and all affected tests read real snapshot files from disk (which now carry the digest) or build their own self-consistent fixtures; test_r1_r12_residential_far_provenance.py copies real files and re-dumps compact — the parsed-payload digest survives re-dump, so baselines still load. No caller builds a table payload in memory without a digest and feeds it to the loader. Nothing breaks.

4. ruff: `cd services/api && python -m ruff check .` -> "All checks passed!"

5. Tests (flock heavy-run.lock): test_zr_snapshot_table_digest.py + test_zr_snapshot_bundle.py + test_r1_r12_residential_far_provenance.py + tests/rules/reference_cases/test_r6b_reference_cases.py -> 85 passed in 3.13s. The 13 new tests cover one test per input state (correct/mismatch/no-digest/no-payload/both/unexpected-shape/non-table), the mutation proof (flipped table value raises "table_digest_sha256 mismatch"), a genuine revert proof (test_pre_change_excerpt_digest_is_blind_to_the_table_edit asserts content_digest still matches after the flip, so the OLD loader would have accepted it — the new check is the sole load-time guard), tables-list and row_groups round-trips, and parsed-payload canonicalization stability. The S1 digest assertions recompute the canonical JSON INDEPENDENTLY of the loader (non-tautological).

6. Independent data verification: 255 snapshot files; exactly 37 table-bearing (18 table.rows + 1 table.row_groups + 18 tables-list), all 37 signed, digest_set==glob_set, zr-22-131 included, zero unsigned-table-bearing, zero signed-without-payload, zero both-shapes. Recomputed stored digests for zr-23-432/zr-22-131/zr-24-522 -> all MATCH; bundled copies byte-identical (table_digest and content_digest). Diffs are additive-only: table_digest_sha256 inserted on the line above content_digest_sha256; content_digest bytes unchanged (zr-23-432 still 9fab7be8…, matching the register pin). sync_zr_snapshots.py --check -> OK, 255 files byte-identical.

7. Modularity: snapshots.py = 261 SLOC, below WARN_SLOC(600)/HARD_SLOC(1000), not in modularity_baseline.json, not in exceptions; test file is excluded ("tests" is an excluded segment + test_ prefix). No threshold crossed, no symbol-ceiling issue (SYMBOL_CEILING=40). NOTE: I could not run `tools/modularity_check.py --check` to a clean PASS because the scratch extract is not a git repo and the read-only guard blocks `git init`; I verified the result deterministically by reading the tool and the line/baseline/exception facts. The orchestrator should confirm with one live `python tools/modularity_check.py --check` at the integration head.

8. Doc: docs/RULES_ENGINE_ARCHITECTURE.md new §5.1 accurately documents the three payload shapes (table.rows, tables, table.row_groups), the canonical-JSON formula, the parsed-payload property, and the four fail-closed cases. Matches the code.

ADVISORY / OBSERVATIONS:
- A1 (ADVISORY, tests): a `tables` key whose value is not a list, and a non-string/empty table_digest with a payload present, are handled by the loader but have no dedicated test. Covered logically by existing paths; a one-line probe each would close the gap. Not blocking.
- A2 (ADVISORY, packet doc only, not a code defect): the packet documented_test_commands/S7 name `tests/rules/test_r6b_reference_cases.py`; the real path is `tests/rules/reference_cases/test_r6b_reference_cases.py`.
- A3 (OBSERVATION, pre-cleared): research_record_check.py --check FAILs on NB-06 evidence[9] (zr-23-432 whole-file pin 37c1414c… -> ae06010e…), exactly the known/handled-elsewhere item in the review brief (E10 re-pin is a second round after M5-T172). No OTHER research record fails like it (NB-04 is a pre-existing NOTE, not a FAIL). Not a finding of this commit.

WHAT I COULD NOT CHECK: the full services/api pytest and CI-green at the integration head (orchestrator's step; the brief notes the four "orphan calculation page" failures come from the contract placeholder pages, not this commit); a live modularity_check PASS (guard-blocked git init in scratch — see item 7); directive_refs D-093-R043/R051/R052 requirement-by-requirement compliance (owned by the separate directive-compliance-verifier pass).

END-OF-REPORT

## G3 (code-reviewer, delta check)

GATE REPORT — M3-T013 (wave 28) G3 code review, DELTA CHECK (integration + round 2). Reviewer: code-reviewer (independent, READ-ONLY AI agent; NOT a human/professional review). Pinned head: 7785d0dedaa538a2241dbd700813a77388d367ab on task/wave28-placement-wiring in /root/project/w-wave20. Round-1 reviewed SHA 06651e8d (G3 PASS, no REQUIRED); integration c1061735; round-2 head 7785d0de.

VERDICT: PASS. No REQUIRED findings. Two carry-forward ADVISORY notes (non-blocking); the round-1 A3/G4 F1 item is now RESOLVED.

WHAT I CHECKED (reproducible; lanes venv /root/project/lanes-runtime/venv; worktree clean at the pinned head, 3 touched .py files on disk diff 0 vs 7785d0de):

1. INTEGRATION IDENTITY — PASS. `git show 06651e8d --name-only` = 78 files. `git diff 06651e8d c1061735 -- <those 78 files>` = 0 lines. c1061735 is a clean cherry-pick: identical 78-file set, identical stat (614 insertions, 2 deletions). The loader (snapshots.py), the doc (RULES_ENGINE_ARCHITECTURE.md), the test (test_zr_snapshot_table_digest.py) and the 74 snapshot files are byte-for-byte equal to 06651e8d. At the FINAL head 7785d0de, `git diff 06651e8d 7785d0de` over the 77 code+doc+snapshot files = 0; only project-control/reports/M3-T013-producer-report.md (of the original 78) differs — the legitimate round-2 report update.

2. ROUND 2 TOUCHES NO CODE — PASS. c1061735..7785d0de is a single commit touching exactly two files: docs/research/evidence-records/NB-06-...json (data/evidence record) and the producer-report .md. No .py, no snapshot capture, no loader/doc/test. NB-06 diff = revision 5->6; E10 (evidence[9]) saved_copy sha256 re-pinned 37c1414c... -> ae06010e...; one appended dependency_assessment note; last_changed unchanged (2026-10-15). Re-pin verified: LF sha256 (`git show 7785d0de:docs/research/zr-snapshots/v1/zr-23-432.snapshot.json | tr -d '\r' | sha256sum`) = ae06010e...; pre-task (06651e8d~1) = 37c1414c...; bundled copy = ae06010e... (byte-identical). zr-23-432 whole-task diff = one added line (table_digest_sha256); content_digest_sha256 unchanged (9fab7be8...). So round 2 closes F1 with no other effect.

3. RUFF AT HEAD — PASS. `cd services/api && ruff check .` (ruff 0.13.0) -> "All checks passed!" exit 0.

CLOSURE OF ROUND-1 OPEN ITEMS (read-only, live at head):
- G4 F1 / round-1 A3: `tools/research_record_check.py --check` -> exit 0 PASS; NB-06 now code_current=True. (NB-04 code_current=False is PRE-EXISTING, reported-not-failed, forbidden path for this task.)
- Round-1 G3 item 7 (modularity): `tools/modularity_check.py --check` -> exit 0; snapshots.py (261 SLOC) not flagged (warnings are all pre-existing on other modules).
- S10 README condition: README index columns are "Record | Question | Research status" — no revision column — so no README edit was required; builder's judgment correct.

CARRY-FORWARD ADVISORY (from round-1 G3, non-blocking, no re-finding): A1 — a `tables` non-list value and empty/non-string digest-with-payload have no dedicated test (logically covered). A2 — packet names tests/rules/test_r6b_reference_cases.py; real path tests/rules/reference_cases/test_r6b_reference_cases.py.

WHAT I COULD NOT CHECK: full services/api pytest and CI-green at the integration head (orchestrator's step); directive_refs D-093-R043/R051/R052 requirement-by-requirement compliance (separate directive-compliance-verifier pass).

END-OF-REPORT

## G4 (qa-engineer)

G4 QUALITY GATE — M3-T013 (ZR snapshot table-payload tamper-evidence, DB-276 Option A). Reviewer: qa-engineer, independent, READ-ONLY. I am an AI agent; this is not a human/professional review. Reviewed at the PINNED builder commit 06651e8d (parent/claim head 1cbc8ccf), run in an archive copy under flock heavy-run.lock. All conclusions re-derived from source and from my own runs, not from the producer's conclusion.

VERDICT: PASS with one REQUIRED correction (the correction is an orchestrator integration-seam action, not a producer code defect; it blocks accept until applied).

=== CHECKS I RAN (archive copy of 06651e8d; venv py3.12.3, ruff 0.13.0; exit codes) ===
1. new test tests/rules/test_zr_snapshot_table_digest.py ............ 13 passed, exit 0.
2. FULL tests/rules .......... 1273 passed, 4 failed, exit 1 (78.9s). The 4 failures are ONLY the known orphan-calculation-page tests (test_zoning_rule_review_register.py + _calculations.py: calc-area-allocation.md / calc-first-placement.md). PROVEN PRE-EXISTING & NOT new: register.json, docs/zoning-rule-review/calculations/, and both test files are byte-identical to claim head 1cbc8ccf and none appear in the 06651e8d diff. Matches the brief's KNOWN-AND-HANDLED note (2).
3. services/api/scripts/sync_zr_snapshots.py --check .......... OK, 255 files byte-identical, exit 0.
4. ruff check . (services/api) .......... All checks passed, exit 0.
5. bundle + far-provenance + r6b reference_cases (S6/S7) .......... 72 passed, exit 0.
6. research_record_check --check .......... exit 1, ONE FAIL only: NB-06 evidence[9].saved_copy zr-23-432.snapshot.json (stored 37c1414c…, actual ae06010e…). This is the known NB-06 pin (brief note 1); I independently reproduced the exact OLD→NEW hashes the producer reported. NB-04 shows code_current=False ("reported, not failed") — pre-existing, unrelated to this commit. Nothing else like it: no other evidence record, reference case, or rule breaks on a whole-file snapshot pin.
7. modularity_check --check — COULD NOT RUN (archive is not a git repo; `git ls-files` exit 128). snapshots.py is 261 lines; the diff adds 3 small focused helpers + 1 call line, no giant function, no dumping-ground; producer reported pass. ADVISORY: orchestrator should confirm from a git checkout.

=== MY OWN MUTATIONS (direct via load_snapshot_file on REAL production snapshots; each: base loads → mutation fails → restore loads) — ALL 6 CORRECT ===
- table.rows flip (zr-23-432) → SnapshotError "table_digest_sha256 mismatch". ✓
- tables-list flip (zr-22-131) → mismatch. ✓
- table.row_groups flip (zr-24-522) → mismatch. ✓
- delete digest (zr-23-22) → "table payload present but no table_digest_sha256". ✓
- add digest to a non-table file (zr-11-23) → "table_digest_sha256 present but the snapshot carries no table payload". ✓
- both table+tables (zr-23-432) → "carries both 'table' and 'tables' payloads (mutually exclusive)". ✓

=== SUITE-CATCHES-A-BYPASSED-LOADER ===
Reverted the single wiring line `_verify_table_digest(raw)` in the archive loader and re-ran the new test file: 8 of 13 FAILED (every mutation/fail-closed assertion), 5 passed (static data/glob/canonicalization only). The suite robustly guards the new loader behaviour; restoring the line → 13 passed again.

=== INDEPENDENT DATA RE-DERIVATION ===
- Glob over docs/research/zr-snapshots/v1 (255 files): 37 table-bearing (18 table.rows + 18 tables + 1 row_groups), 37 digest-bearing, sets EQUAL, zr-22-131 included (S1). Count derived, not hard-coded (the _EXPECTED_TABLE_BEARING_COUNT=37 is a tripwire; the set-equality is the real guard).
- Recomputed sha256 of the canonical JSON of each parsed payload for all 37: 0 mismatches vs stored table_digest_sha256; all 37 bundled copies byte-identical.
- vs claim head 1cbc8ccf: content_digest_sha256 moved on 0 of 37; 37 gained table_digest; 218 non-table files unchanged (S2/B2 confirmed — the 943b65f9…/9fab7be8… citation pins do not move).

=== SCENARIOS ===
S1 VERIFIED; S2 VERIFIED; S3 VERIFIED (my mutation + test); S4 VERIFIED (both directions, my mutations + tests); S5 VERIFIED; S6 VERIFIED (sync --check + bundle test green); S7 VERIFIED (provenance + r6b reference suites green); S8 VERIFIED (RULES_ENGINE_ARCHITECTURE.md §5.1 documents the three shapes, the field, the parsed-payload canonical formula, and the fail-closed behaviour); S9 PARTIAL — modularity I could not run in-sandbox (producer reports pass), and research_record_check currently FAILS on the single NB-06 pin (Finding F1).

=== FINDINGS ===
F1 (REQUIRED, orchestrator/integration action — NOT a producer code defect). File: docs/research/evidence-records/NB-06-street-wall-setback-side-yard.json evidence E10 (evidence[9].saved_copy) pins zr-23-432.snapshot.json by whole-file sha256. Signing zr-23-432 (mandatory; table-bearing, in the glob set, carries the governing R6B base-height table) moved its bytes, so research_record_check --check fails (37c1414c…→ae06010e…, reproduced exactly). NB-06 is a forbidden path; the producer correctly did NOT edit it and flagged it. Correction: after M5-T172 (which owns NB-06) is accepted, the orchestrator adds NB-06 to allowed_paths and re-pins E10.sha256 37c1414c2f1fb93404dca4178d70304c6f39eeecf0f39aa215bd2754cd16887a → ae06010e91a8fae0017f7a33a671c8ce5750c8ddb4f25a647a92ca79c1280898 (mechanical saved_copy hash update; E10's reading/label unchanged, no D-093 fact/label trigger), so research_record_check is green at the accept head. This matches the brief's KNOWN-AND-HANDLED note (1), the producer blocker, and the "second round after M5-T172" plan. This gate must not be accepted until F1 lands.

F2 (ADVISORY). modularity_check --check not runnable in the non-git archive; orchestrator should confirm it passes at a real checkout head (snapshots.py 261 lines, 3 small helpers — no concern on inspection).

=== KNOWN FAILURES NOTED SEPARATELY (not findings of this commit) ===
(a) 4 tests/rules orphan-calculation-page failures — pre-existing, byte-identical to claim head, M5-T172-owned placeholder pages removed on-branch at dc8449d1. (b) NB-06 research_record_check fail — see F1.

=== WHAT I COULD NOT CHECK ===
modularity_check (no git in archive — F2); directive binds D-093-R043/R051/R052 (owned by the directive-compliance-verifier pass, not this gate); I did not re-fetch live ZR pages (R6B readings settled per docs/reference-cases/R6B/cases/; this task adds integrity metadata only and changes no captured value/reading/label); I started no server and touched no ports. Nothing new resembling the NB-06 whole-file-pin issue was found.

Summary: the feature works, the fail-closed behaviour is robust in both directions and across all three payload shapes, the test suite catches a loader that skips the check, the data is byte-stable where required, and no new regression was introduced. PASS conditional on the F1 NB-06 re-pin (orchestrator, post-M5-T172) before acceptance.
END-OF-REPORT

## G4 (qa-engineer, delta check)

G4 QUALITY GATE — M3-T013 DELTA (ZR snapshot table-payload tamper-evidence, DB-276). Reviewer: qa-engineer, independent, READ-ONLY. I am an AI agent; this is not a human/professional review. All results re-derived from source; archive copy of pinned head 7785d0de (/tmp/claude-0/review-t013-g4-d/arc7785), lanes venv py3.12.3; heavy run under flock heavy-run.lock.

VERDICT: PASS. Round 2 closes my round-1 F1 with no other effect; the integration equals the reviewed commit.

=== INTEGRATION IDENTITY (round-1 builder 06651e8d -> integrated c1061735) ===
All 78 files of 06651e8d have IDENTICAL blob OIDs in c1061735 (0 missing, 0 blob-different; ls-tree -r comparison). Literal per-file diffs empty: snapshots.py=0, zr-23-432.snapshot.json=0, test_zr_snapshot_table_digest.py=0. (The full-tree 06651e8d..c1061735 diff touches 108 files only because c1061735 also carries sibling integrations e.g. M5-T172; M3-T013's 78 files are byte-stable.) The brief's one-line `git diff ... --pathspec-from-file` form printed git usage on this git build — I proved identity by blob OIDs + per-file diffs instead; stronger, fully reproducible.

=== ROUND 2 (c1061735 -> 7785d0de) = records-only, closes F1 ===
diff --name-status: exactly 2 files — docs/research/evidence-records/NB-06-...json (M), project-control/reports/M3-T013-producer-report.md (M, +42). Structural NB-06 key-diff shows ONLY three intended changes: revision 5->6; evidence[9]=E10 sha256 37c1414c... -> ae06010e...; dependency_assessment list 7->8 (one appended M3-T013 note). No reading, interpretation, condition, code_identity or label moved. research_status=interpretation_awaiting_review; promotion.requested_label=null; the sole "Verified" string is the new note asserting nothing is labelled Verified. last_changed stays 2026-10-15.

Re-pin correctness (independently recomputed, whole-file LF sha256): zr-23-432.snapshot.json = ae06010e91a8fae0017f7a33a671c8ce5750c8ddb4f25a647a92ca79c1280898 at 06651e8d, c1061735 AND 7785d0de (signed file byte-stable). E10 now pins ae06010e (= signed file). Old pin 37c1414c... = the pre-signing LF sha256 at claim head 1cbc8ccf; it was still stale in NB-06 at c1061735 (rev 5), which is what failed research_record_check. Re-pin is mechanically exact.

=== MY G4 CHECKS (archive of 7785d0de; exit codes) ===
1. tools/research_record_check.py --check -> exit 0, PASS; NB-06 code_current=True (F1 CLOSED). NB-04 code_current=False is pre-existing, "reported, not failed", unrelated (NB-04 untouched/forbidden).
2. scripts/sync_zr_snapshots.py --check -> exit 0, 255 files byte-identical.
3. new test tests/rules/test_zr_snapshot_table_digest.py -> 13 passed, exit 0.
4. FULL tests/rules (flock) -> 1277 passed, exit 0, 85s. The 4 round-1 orphan-calc failures are GONE (M5-T172 accepted in the base).
5. MUTATION (real zr-23-432, table.rows R6B base-height table): base load OK; flip one cell ('R6A'->'R6A_TAMPERED') leaving table_digest_sha256 unchanged -> SnapshotError "table_digest_sha256 mismatch" (tamper caught); pure re-indent (no value change) still loads (digest over parsed payload, indent-stable). Loader refuses the flip. Confirmed.

=== FINDINGS ===
None REQUIRED. F1 (round 1) is verified closed. No new defect.

=== WHAT I COULD NOT CHECK ===
modularity_check (archive is not a git repo; git ls-files fails) — N/A for this delta: round 2 changed no handwritten production source, and round-1 snapshots.py (261 lines) is blob-identical in the integration. Directive compliance D-093-R043/R051/R052 is the directive-compliance-verifier's pass, not this gate. CI-green-at-accept-head is the orchestrator's read (D-090 R639). I did not re-fetch live ZR pages (R6B readings settled in docs/reference-cases/R6B/cases/; this task adds integrity metadata only and round 2 is records-only — no captured value/reading/label changed). Started no server; touched no ports; wrote nothing in any repo.

Net: integration is byte-identical to the reviewed commit over all 78 files; round 2 is a correct, traceable, records-only re-pin that makes research_record_check green and changes no fact/reading/label. PASS for the G4 share.
END-OF-REPORT
