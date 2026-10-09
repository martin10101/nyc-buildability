# M5-T081 — G4 delta re-review after the rework (qa-engineer "qa-cad", read-only)

> Transmission history: requested by SendMessage after the G4 FAIL (F1 BLOCKING honesty-label pin) rework
> (0ffe581c, cherry-pick of wt-m5t081 778bf8ca); pinned at f2870507 (HEAD advanced to cae4d82c during
> the review; both in-scope blobs verified byte-identical); delivered as two SendMessage parts (1/2, 2/2)
> ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags
> removed only). The original joint T081/T085 G4 report (T081 FAIL) stays in M5-T081-G4.md unchanged.

---

G4 rework-delta re-review, M5-T081 (qa-engineer, independent, read-only). Env: services/api, Python 3.11.9. Pin verified HEAD f2870507; blobs dxf_writer.py 152f1f2e, test_dxf_writer.py 2aa45291. HEAD advanced during review (f2870507 -> cae4d82c) but BOTH in-scope blobs stay byte-identical, so this verdict carries at the reviewed identity. No repo write (git status -- services/ clean; all mutation in-memory). Suite: `python -m pytest tests/cad/test_dxf_writer.py -q` = 24 passed.

Mutation table (mutant | target test | result):
- F1a PROPOSED_LABEL drop "NOT A CITY RECORD" | test_as4_annotation_carries_required_labels | RED killed (hardcoded literal + constant-equality both fail)
- F1b CRS_UNITS_NOTE weaken | same | RED killed
- F2 sanitizer CR/LF-only (my prior survivor) | test_as3_sanitizer_rejects_forbidden_bytes | RED on ALL 3 params (NUL / ESC / non-ASCII)
- F3a drop "MAXIMUM ALLOWED" from CLAIM_CLASS_WORDS | test_as4_claim_class_words_are_the_expected_set | RED killed
- F3b disable _assert_no_claim_words | test_as4_claim_word_guard_is_load_bearing | RED (build no longer refuses); pristine guard confirmed load-bearing (raises code=claim_class_word) so the test is non-vacuous
- INS INSUNITS 21->2 | test_as2_header_declares_drawing_unit | RED (emits (70,"2") vs hardcoded (70,"21"))
- B1 remove floor pre-check | test_as3_builder_refuses_over_cap_floor_count_before_allocating | RED (MAX_FLOORS+1 builds successfully)
- B2 remove magnitude bound in _format_real | test_as3_coordinate_magnitude_bound_refused | RED (1e9 coord renders instead of refusing)

All five producer-named mutants (INSUNITS 21->2, label drop, CR/LF-only sanitizer, claim-guard no-op, floor pre-check removed) reproduced RED, plus my own F1b/F3a/B2 weakenings. Findings + verdict in part 2/2.

---

M5-T081 rework-delta findings (2/2):

F1 (was BLOCKING) — CLOSED. test_as4_annotation_carries_required_labels now asserts the HARDCODED literals "PROPOSED - NOT A CITY RECORD" and the full CRS note in the SERIALIZED output AND pins both constants by equality. The by-value tautology I flagged is gone: the label-drop (F1a) and CRS-weaken (F1b) both redden. Two-mutant rule satisfied (literal + idiomatic).

F2 (was ADVISORY) — CLOSED. New parametrized test_as3_sanitizer_rejects_forbidden_bytes pins the 0x20-0x7E allowlist at NUL, ESC and a non-ASCII char, so my CR/LF-only survivor now reddens on all three. The injection-critical CR/LF path remains covered by the original tests.

F3 (was ADVISORY) — CLOSED. The claim-word guard is proven load-bearing (F3b reddens; pristine build refuses a claim word with code=claim_class_word, so the new test is meaningful not vacuous) and the full 11-word CLAIM_CLASS_WORDS set is pinned (F3a reddens on a shrink).

New guards non-vacuous: floor cap (B1), 1e8 coordinate-magnitude bound (B2), and the INSUNITS literal (INS) all redden when their guard is removed/mutated. INSUNITS 21 = US Survey Feet is the correct code for EPSG:2263; the test externally pins the literal (70,"21") rather than str(d.INSUNITS_*), so a 2-vs-21 regression reddens.

Minor non-blocking observations (no action required): the floor-cap and magnitude tests use clearly-over values (MAX_FLOORS+1; 1e8*10), so the boundary DIRECTION (`>` vs `>=`) is not pinned — immaterial for anti-abuse sanity caps (real NYC coords ~1e6). Determinism: golden re-anchored to 2d8988d6 for the deliberate INSUNITS 2->21 one-byte change; the 24-passed suite confirms byte-stability.

All three of my prior findings are closed with verified-reddening mutants, the new bound/units guards are non-vacuous, and the suite is green. No new inadequacy.

M5-T081 G4 VERDICT (rework delta): PASS

END-OF-REPORT
