# M4-T031 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `b97177f4eb1288d43325e53f5f3c1d5ed4244b84` (branch `task/wave3-results-contract-readings-further-captures`, pull request 461, review copy `/root/project/rv-w3-1007d`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review. (Two verifiers had been started earlier at `ec5c0155`; the orchestrator stopped them when CI failed on that head, before either returned. This verifier is a fresh agent.)
One verifier checked the two tasks M4-T030 and M4-T031 together. Its return is reproduced in full in both tasks' records (`M4-T030-DCV.md` and `M4-T031-DCV.md` hold the same text below the line); this file is the record for **M4-T031**.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R291 (1 row).

## Verdict: PASS for this task's row. No required correction blocks acceptance.

- **R291 is met only for this task's share.** The row covers the whole of step 3 (check the R6B answers: resolve missing rules and conflicting inputs, and save independently calculated examples). This task captures 38 law texts as source text; it resolves no rule and reads the text for no lot. The row stays open in the registry.
- The verifier confirmed that the commit adds exactly 38 capture files and 38 byte-identical synced copies and nothing else but the builder's report; that no capture holds a rule, a reading or a result; and that the readers of M4-T030 did not have these texts and no record says otherwise.
- It fetched three official pages itself (ZR 34-22; the ZR 12-10 page, for the definition found under the inverted title "yard, rear"; ZR 23-443, a section with tables): each equals the pinned digest, and the table cells and text of ZR 23-443 equal the live page. It did not fetch the other pages: the gate reviewer re-read all 22, and the bundle test recomputes every digest.
- The directive validator, run by the verifier in the review copy: exit 0. The tests it ran: 76 passed, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head.
- Read by the orchestrator on 2026-10-07 at 10:52 UTC: the pull request's check list on `b97177f4` showed 46 checks, all a completed success.

How the return arrived (2026-10-07): in two messages (part 1 alone at 10:56 UTC; the orchestrator asked the same agent for the rest at once; part 2 with the closing line at 10:57 UTC). Both are reproduced below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`, lines 4090 and 4110; only the two-space indent the transport adds to every line was removed). In part 2 the verifier corrects a remark of its own part 1: the 12-byte difference it had seen on the page of ZR 23-443 came from its own command, and a clean fetch equals the pinned digest.

---

```
PART 1 of 2

HEADER
- Role: INDEPENDENT directive-compliance verifier (directive-compliance-verifier) for M4-T030 and M4-T031, directive D-090. I produced none of this work or its records; read-only.
- Frozen head: b97177f4eb1288d43325e53f5f3c1d5ed4244b84 (review copy /root/project/rv-w3-1007d, branch task/wave3-results-contract-readings-further-captures, PR 461). `git rev-parse HEAD` confirmed.
- This is an AI-agent review, not a human or professional/legal review. Two AI readings agreeing is not proof; neither is this review.
- Binding confirmed: directive_registry.evaluate_task_refs → M4-T030 applicable==cited=={R226,R241,R259,R291,R318}; M4-T031 applicable==cited=={R291}. ok=True, no missing/invalid.

ROW M4-T030 D-090-R226: PASS
 - docs/reference-cases/R6B/cases/step-p3-worked.json holds 21 worked rows; each has facts_used, a citations array with the law section + verbatim quote + snapshot_id + content_digest, why_applies, and an expected{kind,value}; arithmetic arrays carry the readings' own geometry (empty where the conclusion is textual). Each example cites its section.
 - The two readings (docs/reference-cases/R6B/provenance/return-independent-hand-calculation-7.md and -8.md) each state they worked ONLY from a sealed folder of law-text captures + the lot's recorded official facts + three made-up lots, with no program/repository access (reading 7 line 5; reading 8 line 5). I confirmed the committed provenance files are byte-identical to the readings the orchestrator received (return-reading-P3-1.txt/-2.txt) except a 6-line "reproduced below unchanged" header.
 - The readers' isolation ("had not read the program's answer") is their own CLAIM; what the repo supports: values trace to quoted law + sourced facts, never to a program run (what_it_does_not_establish, prepared_by, sources). What I cannot reproduce: whether the two helpers truly had zero program access during their run (their sandbox/transcripts are not inspectable from here) — corroborated only indirectly by self-consistency.

ROW M4-T030 D-090-R241: PASS
 - No expected value was taken from or changed to match a saved program result. My row-by-row diff f5c2a8f2→25ba6c04 over all 7 R6B case files: 0 rows changed expected.kind. Only value TEXT changed in step-p3#sections-and-facts-not-had (F1 tightening) and three overlay rows where only the word "uncaptured" was deleted — none changed a value to match program output.
 - Eight older not_known rows now carry machine-readable superseded_by (corner-reach: real-lot-rear-yard, C3-rear-yard; overlay-reading: section-35-633; real-lot: L12; step-p1-worked: corner-150x100-rear-yard, interior-40x100-rear-yard, through-40x200-rear-yard, special-density-real-lot). services/api/tests/rules/reference_cases/r6b_reference_cases_lib.py load_row refuses a superseded row unless allow_superseded=True, so no test can assert a stale value.
 - No value is recorded that both readings do not give on the same basis (checked special-downtown-brooklyn-district, sections-and-facts-not-had, zr-23-362b-eligible-sites, real-lot-rear-yard-beyond-corner against readings 7 and 8 myself).

ROW M4-T030 D-090-R259: PASS
 - Reference cases live in their own files under docs/reference-cases/R6B/, apart from program output; what_it_is_worth and checked_by state "their agreement alone is not proof." Each row carries facts, the law quotes relied on and the readings' arithmetic, so a person can follow with source + calculator.
 - A value/yes-no is recorded only where both readings agree on the same basis; the special-downtown-brooklyn-district row records "outside on the recorded facts" and explicitly names that reading 8 holds it subject to Article X Ch 1 while reading 7 treats it as settled — matching reading 7 Q5 and reading 8 Q5 that I read.
 - Expected values change only with a recorded reason (change_log + dated 2026-10-07 round-2 entries per changed file; render --check PASSED per the gate record).

ROW M4-T030 D-090-R291: PASS
 - M4-T030's share (step 3, "save independently calculated examples to test against"): independently worked examples saved as files (cases/step-p3-worked.json). Previously-not-known reference answers are now resolved where the newly-captured law + both readings settle them (interior-40x100-rear-yard, through-40x200-rear-yard-equivalent, manhattan-core, special-downtown-brooklyn-district, zr-23-436-paragraphs); genuine gaps stay not_known (real-lot-rear-yard-beyond-corner, real-lot-lot-width, base-plane-real-lot) — matching required_harness "each known gap is resolved or shown as not known."
 - It resolves no engine rule and shows no program result (no result field; arithmetic only from the readings). The engine-side resolution of conflicting inputs and the option connection are later work (steps 4+).

ROW M4-T030 D-090-R318: PASS
 - The reference examples are worked from the source text by agents that did not see the program's output and are kept as files (same evidence as R226/R259: step-p3-worked.json + provenance -7/-8). Source-backed (every row cites a pinned snapshot digest).
 - Same residual: reader program-isolation is an attested claim I can corroborate only indirectly.

ROW M4-T031 D-090-R291: PASS
 - Material commit cbbdb6b8 adds exactly 38 snapshot captures under docs/research/zr-snapshots/v1/ plus 38 byte-identical synced copies under services/api/app/_zr_snapshots/v1/ (cmp: 0 differing); only project-control/reports/M4-T031-producer-report.md else touched. This task captures law text only.
 - All 38 carry extraction_status=extracted_draft; union of top-level keys is capture metadata only (no rule/reading/result/interpretation key); notes carry no interpretive claim. No record claims a rule resolved, a lot read, or a result.
 - I re-fetched official pages: zr-34-22 raw_html_sha256 and the §12-10 page raw_html_sha256 (source of zr-12-10-yard-rear, an inverted-title definition) match the pins EXACTLY; zr-23-443 (a table section) legal text + table cells (LH-1 50ft … LH-3 100ft) match the live page (12-byte raw-HTML drift on a dynamic page; pinned content_digest and text faithful).
 - The M4-T030 readers did not have these 38 texts: both readings explicitly list 34-22 and 34-23 as not had, and step-p3#sections-and-facts-not-had + the loader comment record them as not had. No record says otherwise.

END OF PART 1.
```

```
PART 2 of 2

M4-T030 FAILED FIRST REVIEW — KEPT UNCHANGED, LOG HONEST
- project-control/reports/M4-T030-G3G4.md records both heads: verdict line "G3 FAIL and G4 FAIL at f5c2a8f2; after the corrections, G3 PASS and G4 PASS at 25ba6c04." The full first review (section "The first review (at f5c2a8f2): FAIL", G3: FAIL / G4: FAIL) is reproduced unchanged, including the per-row walkthrough naming row 21 sections-and-facts-not-had as the F1 defect and findings F1/F2/F3 with their reasoning and smallest-correction notes. The report states the reviewer returns are "reproduced below unchanged (copied by script from the session transcript … lines 3565 and 3775; only the two-space transport indent removed)."
- The two findings the gate failed on are exactly what the prompt described: F1 = a row that recorded as agreed (both readers "not had" ZR 36-64/35-71) something only reading 7 said while reading 8 listed them as in its folder; F2 = older not_known rows standing beside new rows answering the same question with no machine-readable supersede. I reproduced both: the round-2 diff removed 36-64/35-71/23-34 from the agreed list, and eight rows gained superseded_by.
- project-control/tasks/M4-T030.json progress_log is honest: the 70% entry (orchestrator, 2026-10-07T09:50) records "Independent review (code-reviewer) at f5c2a8f2, before submit: G3 FAIL and G4 FAIL. F1 (must fix)…"; the 85% entry records the rework commit 25ba6c04 and the same-reviewer re-review. Status now awaiting_gate.

CORNER-COVERAGE POINT — CONFIRMED
- No row records "100 percent for this corner lot" as a value. The only whole-lot-coverage rows are not_known: cases/real-lot.json L5 (kind not_known, no superseded_by; reason: "No single whole-lot coverage figure. The corner-lot 100-percent rule covers only the part … within 100 feet … this lot reaches 103.93 feet … so the whole lot is not the corner-lot portion … corner-lot portion 100 percent and the remaining interior-lot portion 80 percent"); cases/corner-reach.json real-lot-coverage (not_known); cases/step-p1-worked.json corner-150x100-coverage and corner-200x120-coverage (not_known). The value rows corner-100x100-coverage=100 percent, interior=80, through=80 are legitimately settled (a 100x100 lot is wholly within 100 ft of the corner).
- cases/step-p3-worked.json row zr-23-362b-eligible-sites records only the §23-362(b) scope conclusion; its does_not_establish quotes both readings' passing Q7c "100 percent for this corner lot" and states the whole-lot corner-coverage reading "stays per portion and not known: cases/real-lot.json row L5 … keep their not-known per-portion value." This matches reading 7 Q7c and reading 8 Q7c, which I read.
- Diff f5c2a8f2→25ba6c04 shows no change to any coverage row's kind/value. A test guard enforces it: services/api/tests/rules/reference_cases/test_r6b_reference_cases.py::test_the_corner_coverage_pins_hold_and_a_moved_pin_is_refused calls step_p3.pinned_coverage_errors and includes a mutation proof that setting a pinned row to "100 percent" is refused. must_stay_not_known_errors guards the step-p3 not_known rows. L5 is unchanged (no supersede, still not_known).

HARNESS (direct exit codes)
- python tools/validate_directive_compliance.py --check (from review copy): DIRECT exit code 0.
- cd services/api && python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/rules/test_zr_snapshot_bundle.py tests/spatial/test_lot_reach.py: exit code 0, 76 passed in ~2.25s (includes the corner-coverage pin guard, the superseded-row round2 suite, the snapshot bundle/register tests, and lot-reach). I did NOT run tools/test_directive_compliance.py or the full api suite (per instruction).

GIT — TASK FILES UNCHANGED AFTER REVIEWS
- git diff --stat b8b9d886 b97177f4 over docs/reference-cases/R6B/, services/api/tests/rules/reference_cases/, docs/research/zr-snapshots/v1/, services/api/app/_zr_snapshots/v1/: EMPTY. The gates were recorded at b8b9d886; from there to the frozen head nothing under the two tasks' allowed paths changed.
- Reviewed-head identity also holds: 25ba6c04 (M4-T030 reviewed) → b8b9d886 EMPTY over those dirs; cbbdb6b8 (M4-T031 reviewed) → b97177f4 EMPTY over the snapshot dirs.
- The only changes b8b9d886→b97177f4 are M5-T128's results schema/_contract_schemas/test_results_three_ways_slot.py, one CODING_RULES.md line, DISCOVERY_BACKLOG.md, and project-control gate/report/task/state records — none in either of my two tasks' allowed paths.

CARRY-FORWARD CONDITION (blob-level predicate)
- My six PASS verdicts may be stamped at a later head WITHOUT re-asking me iff, at that head: (1) every file under the two tasks' allowed paths is byte-identical to the frozen head b97177f4 — namely docs/reference-cases/R6B/**, services/api/tests/rules/reference_cases/**, project-control/reports/M4-T030-producer-report.md, docs/research/zr-snapshots/v1/**, services/api/app/_zr_snapshots/v1/**, services/api/tests/rules/test_zr_snapshot_bundle.py, project-control/reports/M4-T031-producer-report.md; (2) the six requirement rows (D-090 R226/R241/R259/R291/R318 and R291 for M4-T031), the D-090 manifest and digests, and the five source amendments they trace to (source-032/033/035/039/040) are unchanged; and (3) every commit between b97177f4 and that head touches ONLY project-control/ records and/or lines of docs/DISCOVERY_BACKLOG.md.
- Tolerance for commits touching another task's files: I tolerate any change that touches none of the paths/artifacts in (1)-(2) — specifically the M5-T128 contract-schema work (packages/contracts/schemas/v1/results.schema.json, services/api/app/_contract_schemas/**, services/api/tests/contracts/test_results_three_ways_slot.py), .claude/rules/CODING_RULES.md, and the acceptance/gate writes for all three wave tasks. These are outside both tasks' allowed paths and the directive sources and do not touch my evidence, so a disjoint peer commit between freeze and stamp does not void these verdicts.

REQUIRED CORRECTIONS THAT BLOCK ACCEPTANCE: none.

NON-BLOCKING OBSERVATIONS
- Correction to my PART 1 remark about ZR 23-443: there is NO real raw-HTML drift. The capture's pinned source.raw_html_sha256 = 46d3ae43f2fd366bf052fe7a856bef6fe825582688c47ffa6ace614833b33e78 reproduces EXACTLY on a clean fresh fetch, confirmed twice back-to-back. My earlier "12-byte difference" (observed hash ab179042…, size 132343 vs the pinned 132331) was an artifact of my own command: that run piped curl's `-w "\nsize=%{size_download}\n"` summary line into sha256sum, so I hashed the body plus the appended "size=…" bytes. A clean fetch (no -w contamination) matches the pin, so the pinned raw digest still matches a fresh fetch and response_bytes 132331 is the true body size. The DCP portal does embed per-request Drupal tokens (form_build_id, js-view-dom-id) but they did not perturb these fetches. Net: all three spot-checked pages (zr-34-22, the §12-10 page behind zr-12-10-yard-rear, zr-23-443) reproduce their pinned raw_html_sha256 exactly; zr-23-443's table cells (LH-1 50 ft … LH-3 100 ft) and legal text match the live page.
- R291 is a step-3 sequencing requirement broader than these two tasks; both tasks satisfy only their share. The remainder of step 3 — resolving conflicting inputs inside the engine and connecting an option to the screen — is explicitly later work (owner's steps 4+); neither task claims it.
- M4-T031's own gate (project-control/reports/M4-T031-G3G4.md) is a clean G3/G4 PASS (no FAIL history, unlike M4-T030 and M5-T128); its reviewer independently re-fetched all 22 distinct pages byte-identical, re-extracted every excerpt, re-computed all 38 digests, and confirmed source-text-only discipline. My independent spot-checks agree.

WHAT I COULD NOT CHECK MYSELF
- Whether the two M4-T030 AI readers truly had zero access to the program/repository during their run. I verified it only from their own written statements and from the self-consistency of the readings (values trace to quoted law + sourced facts, never to a program output); the readers' sandboxes/transcripts are not inspectable from here, so reader program-isolation is an attested CLAIM corroborated indirectly, not reproduced.
- I did not re-fetch all 38 official pages or machine-diff every table cell (the M4-T031 gate reviewer did, byte-for-byte). I reproduced 3 captures (2 exact raw-HTML digest matches + 1 whole-page §12-10 digest match that covers zr-12-10-yard-rear, plus the 23-443 table/text match) and the 38-digest/sync integrity via the passing test_zr_snapshot_bundle suite and the empty allowed-path diffs.

OVERALL VERDICT: PASS for all six rows (M4-T030 R226, R241, R259, R291, R318 and M4-T031 R291). No VIOLATED/UNVERIFIABLE result among the six; no blocking correction.

END-OF-REPORT
```
