# M5-T190 reviews (every return kept unchanged)

- One build round (backend-engineer, worktree): builder commit cb226c05 (parent the claim head 8d7cf91b) integrated as the cherry-pick 26d1d4bf on task/wave28-placement-wiring (3 files, all inside the packet's allowed paths; LF sha256 of each equal to the builder's return).
- G2 orchestrator self-check at 26d1d4bf: the three files equal the builder's digests; nothing outside the allowed paths; page_evidence.py untouched (its docstring does not list the excluded fields, so RISK 2 did not arise); the cause and the fix match the read-only check (return-check-fingerprint.md: exactly four top-level fields differ between runs; no value differs).
- Both reviewers rebuilt the document twice through the live route and saw one fingerprint (b68f8a1f049d) and a moved fingerprint on a real value change.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (code-reviewer)

M5-T190 G3 CODE REVIEW (code-reviewer). I am an AI agent, read-only; this is not a human/professional review. Frozen sha 26d1d4bfc5e3920dca2ccd3380da9944e6c9a0cb (task/wave28-placement-wiring), archived to /tmp/claude-0/review-t190-g3. Ran under the lanes venv with the heavy-run lock.

VERDICT: PASS.

WHAT I INDEPENDENTLY VERIFIED (not from the producer's conclusion)
1. The diff is correct and complete. I ran the live results route twice through TestClient (benchmark_provider(with_zoning_lot=True, street_on=True), INTERNAL_RESULTS_ENABLED=LANE_A_ENABLED=1, NORTHERN_BBL, body standard_residence) and did a full recursive leaf-diff of the two documents: EXACTLY 4 differing leaves, ALL top-level — /computed_at, /option_id, /results_id, /study_id. One of my runs crossed a second boundary (14:57:39Z vs :40Z) so computed_at genuinely differed, yet /revision/created_at did NOT appear — because the emitted document's top-level `revision` is the integer 1 (the dict-with-created_at is the study's, never surfaced). A find() of every nested occurrence of the four per-run VALUES showed each appears exactly once, at top level. So option_id and study_id ARE the only per-run fields beyond results_id/computed_at, top-level and nested. Fingerprints equal across the two runs (b68f8a1f049d == b68f8a1f049d).
2. Nothing real is excluded. A real top-level value change (completeness_line) moves the hash; a real NESTED value change (deep in answers) moves the hash; dropping all four excluded fields keeps it stable; changing option_id/study_id keeps it stable. The exclusion is top-level-only, which is safe here because the four excluded names are pure per-run metadata.
3. Mutation proves the fix at the test level. Reverting _FINGERPRINT_EXCLUDE to ("results_id","computed_at") turns S1, S3 and S4 RED (e.g. S1 c813b01a2619 != 943f149d20a2) while the pre-existing test_s7_fingerprint_stable_excluding_run_id_and_timestamp stays GREEN — confirming the old test could not catch the option_id/study_id drift and the new tests pin the fix. I also confirmed programmatically: old tuple -> two live runs differ (825d94d9ce39 vs 61138a05c1d4); new tuple -> equal.
4. The live two-run test really goes through the route (S4 asserts d1/d2 option_id, study_id, results_id all differ, so it is non-vacuous) and one-test-per-input-state holds (S1 all-four-fields, S2 real-value via the retained test_s7 sensitivity test, S3 missing-ids, S4 live route, S5 prose).
5. Tests pass: tests/drawings/report/test_report_run_identity.py = 11 passed.
6. Prose is accurate. Module docstring, the comment above the tuple, and the document_fingerprint docstring all now list the four fields and say they are per-run metadata the live route mints — correct (results_id/computed_at/option_id/study_id are all minted per run in results_read.py). page_evidence.py's _run_identity docstring says only "stable for the same document, changing with any value" and does NOT enumerate fields, so RISK 2 does not materialise and no forbidden file needed touching (producer's claim verified).
7. No consumer breaks. grep: no test/fixture/snapshot pins a literal 12-hex fingerprint; test_report_css_escaping.py's run-identity test concerns CSS escaping of a revision/footer string, not the fingerprint; report_read.py imports only deployed_commit. 
8. ruff check passed on both changed files. run_identity.py is 91 lines, single responsibility (+8 net lines, one tuple element + docstring prose), no new responsibility or coupling — modularity is trivially satisfied.
9. Directive support (G3-level, DCV owns the authoritative per-requirement pass): the change makes the fingerprint stable for the same document, which is exactly what D-094-R058 (each result/diagram comes from one result revision and scenario) and D-094-R028 (identify what generated the report) require; before the fix the fingerprint changed on every print of the same property and proved nothing.

FINDINGS
- F1 (ADVISORY). run_identity.py:47 _FINGERPRINT_EXCLUDE is a deny-list correct for contract 1.5.0 as emitted. A future contract that adds another per-run id/timestamp would silently reintroduce drift (packet RISK 1). A value ALLOW-list would be more robust against new per-run fields (it fails toward stability), BUT it is riskier for provenance because a newly-added REAL value field would be silently omitted from the fingerprint, weakening R058's "any value change moves it" guarantee. Net: the deny-list is the right smallest fix now; keep it. The live two-run test (S4) already catches a new per-run drift the day it appears — that is the correct guard. Optional future hardening: assert/review the exclude set when contract_version bumps. No change required for this task.

WHAT I COULD NOT CHECK
- I ran the single affected test file (11 passed) plus targeted consumer greps and the specific CSS test, not the full tests/drawings/report folder (225) or the whole api suite (10084) — those must be read GREEN in CI at the accept head (orchestrator, D-090-R639).
- I did not run tools/modularity_check.py --check across the full tree (needs tools/ and the whole tree); I corroborated the file's size/responsibility directly. The producer's documented full run reported 0 failures.
- No preview/server/PDF print (forbidden here); the rendered page is covered by the report tests.

END-OF-REPORT

## G4 (qa-engineer)

GATE REPORT — M5-T190 G4 (qa-engineer), independent read-only review. I am an AI agent; this is not a human/professional review.

VERDICT: PASS

PINNED: 26d1d4bfc5e3920dca2ccd3380da9944e6c9a0cb on task/wave28-placement-wiring (3 files: run_identity.py, test_report_run_identity.py, M5-T190-producer-report.md). Reviewed from a fresh archive of that sha under the lanes venv; heavy runs under flock heavy-run.lock.

WHAT I CHECKED (reproduced, not read from the producer):
1. ruff check . — exit 0, "All checks passed!".
2. Focused tests/drawings/report/test_report_run_identity.py — 11 passed, exit 0.
3. Full tests/drawings/report folder — 225 passed, exit 0 (71.55s).
4. My own mutation (reverted _FINGERPRINT_EXCLUDE to the two-field ("results_id","computed_at") tuple), ran S1/S3/S4 + the two S7 tests: 3 FAILED (S1,S3,S4), 2 PASSED (S7 stability, S7 sensitivity), exit 1. S7-stability stays green because it only tweaks results_id/computed_at — confirming the old test could not catch the option_id/study_id drift. Restored; restored sha256 = bb4f718f... (matches the builder's LF digest).
5. POST /report twice through TestClient with benchmark_provider(with_zoning_lot=True, street_on=True) + recorded_pack_provider(benchmark_215_16_northern_window): "Document fingerprint" line = b68f8a1f049d in BOTH runs (identical), while the two runs really minted different option_id/study_id/results_id (not a vacuous match).
6. Real-value mutation in a harness (not a fixture): the rendered report line equals document_fingerprint(returned doc); changing floor_area_allowance[1].value 20150.0→20151.0 moved the fingerprint b68f8a1f049d→2f401a741436, both at document_fingerprint() and the rendered report line.
7. Provenance of the excluded fields: results_read.py:343/351/388 mint option_id/study_id/results_id as uuid.uuid4().hex and :344/389 set computed_at via _now_iso() — none carry value. An exhaustive two-run diff of the emitted document showed the ONLY differing top-level fields are exactly {computed_at, option_id, results_id, study_id} = the new exclude set; emitted top-level `revision` is the integer 1 and is stable; the identical two-run fingerprint empirically proves no nested per-run value leaks.
8. Scope: exactly 3 files, all in allowed_paths; no forbidden path touched. page_evidence.py (forbidden) is untouched and its _run_identity docstring does not enumerate the excluded fields, so RISK 2 does not materialize. All imports added to the test are used.

ACCEPTANCE SCENARIOS: S1 (stable across all four run fields) PASS; S2 (sensitivity, pre-existing test_s7_fingerprint_changes_when_any_value_changes) PASS; S3 (document without option_id/study_id unchanged) PASS; S4 (live results route twice, same fingerprint; old tuple makes it red) PASS; S5 (module docstring + comment above the tuple list the four fields and say why) PASS — verified in source.

DIRECTIVE REQUIREMENTS (re-derived from requirements.json; both applicable to M5-T190):
- D-094-R028 (obligation) SATISFIED: the run identity (fingerprint, commit, revision, computed) stays in the named appendix and still identifies what generated the report; making the fingerprint reproducible strengthens "identify what actually generated this report." No info removed, no repeated headings affected.
- D-094-R058 (harness) SATISFIED: the fingerprint's purpose is to prove each result and diagram comes from one document revision; before the fix it changed on every print of the same document (proving nothing), after it is stable for one document and still moves on any real value. S4's live two-run test is the verifying harness. The "distinguish allowance/scheduled area/site fit/apartment estimate/legal unit limit" clause is a page-content concern unchanged by this metadata-only change.

MODULARITY: run_identity.py is 91 lines; the change is a 2-element tuple extension plus prose. No responsibility mixing, no new module, no growth concern.

FINDINGS:
1. [ADVISORY] Could not run tools/modularity_check.py --check in the archive copy (no .git → git ls-files exit 128). The file size and change nature carry no modularity risk; producer reported exit 0 and the control-plane CI job covers the merge head. Correction: orchestrator confirms modularity_check green in CI at the accept head (R639). Not a defect.
2. [ADVISORY] RISK 1 in the packet (a future contract adding another per-run id/timestamp would re-introduce drift) is real but already mitigated — S4's live two-run test fails the day it happens. No action now.

WHAT I COULD NOT CHECK:
- The whole services/api suite (producer: 10084 passed) — I ran only the two suites the brief required (11 + 225 passed). The full suite + all security checks must be read green IN CI at the exact accept head (R639); that is the orchestrator's pre-accept step, not mine.
- Windows behavior (no Windows here; CI covers it).
- modularity_check (see finding 1).

No REQUIRED corrections. The fix is correct, complete, reproducible and value-sensitive, in scope, and provenance-sound.

END-OF-REPORT
