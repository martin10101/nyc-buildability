# M4-T027 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `edcddf719dbedbae51162c490f42e57258bfdeb5` (branch `task/wave1-measurement-basis-p2-captures-reference-cases`, pull request 459, review copy `/root/project/rv-w1-1007`). Directive D-090. The verifier was not the producer and wrote none of the records. It is an AI agent; this is an agent check, not a human or professional review.
One verifier checked the two tasks M4-T026 and M4-T027 together, and with them the record of owner messages 107 and 108. Its return is reproduced in full in both tasks' records (`M4-T026-DCV.md` and `M4-T027-DCV.md` hold the same text below the line); this file is the record for **M4-T027**.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R226, R238, R241, R259, R291, R318 (6 rows).

## Verdict: PASS for this task's rows. No required correction blocks acceptance.

- **R291 is met only for this task's share** (examples saved as files to test against; no missing rule resolved; no program result compared with a case), and the row stays open. For R226 and R318 the verifier names what the repository cannot prove: that the two readers had not read the program's answer rests on how they were run and on their own statements.
- It also checked the record of owner messages 107 and 108 that rides on this branch (source-052, rows R493 to R497): A1 to A6 all met. On A3 it states plainly that the reading of the two messages (several independent pieces at once, at most five helpers, of which at most three build and four review) does not go beyond the owner's words, that the owner was told the reading and asked to say if something different was meant, and that no later owner message corrected it. On A5: no file appears in two builders' commits, and never more than three builders ran together.
- The registry validator, run by the verifier in the review copy: exit 0. The tests it ran (the reference cases and the capture bundle): 43 passed, exit 0.
- Its carry-forward condition (below, in its own words) is the rule for stamping these verdicts at a later head.
- What it could not check itself: that the two readers really worked without the program (a matter of how they were run; it relied on the sealed-folder build script, the readers' own statements and the fact that the two readings differ on one row); the full api suite; CI on the pushed head. Read by the orchestrator on 2026-10-07 at 06:17 UTC: the pull request's check list on `edcddf71` showed 46 checks, all a completed success.

How the return arrived (2026-10-07): in two messages. Part 1 arrived alone at 06:23 UTC and the verifier stopped; the orchestrator asked the same verifier for the rest at once; parts 2 and 3 arrived together. They are joined below unchanged (copied by script from the session transcript `a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl`; only the two-space indent the transport adds to every line was removed). The second message begins with a line the transport added itself ("[harness: ...]"): it had replaced the opening "<" of one tag name quoted in point A3 with "<\". That line and that mark are left as they arrived.

---

```
PART 1 of 3

ROLE: Independent directive-compliance verifier (data-contract-verifier capacity) for M4-T026 and M4-T027 (D-090), wave 1. I produced none of this work. Read-only; I wrote no file, ran no project_control/git/gh write, merged/accepted nothing.
FROZEN HEAD: edcddf719dbedbae51162c490f42e57258bfdeb5 (confirmed by `git -C /root/project/rv-w1-1007 rev-parse HEAD`; detached, clean). PR 459, branch task/wave1-measurement-basis-p2-captures-reference-cases.
NOTE: I am an AI agent. This is not a human or professional legal review; every capture is an extracted_draft and every reference case a draft AI reading.
BINDING: directive_registry.evaluate_task_refs confirmed applicable==cited for both — M4-T026 {ok, [R291]}; M4-T027 {ok, [R226,R238,R241,R259,R291,R318]}; no missing/invalid/unresolved. VERDICT: PASS.

ROW M4-T026 D-090-R291: PASS
 - docs/research/zr-snapshots/v1/ holds all 8 named captures (zr-34-11/34-111/34-24/35-53/35-63/35-631/35-632/35-633); each extraction_status="extracted_draft"; I recomputed sha256(verbatim_excerpt) for all 8 and each equals the stored content_digest_sha256.
 - Independent live fetch reproduced two pins: GET .../article-iii/chapter-4/34-24 (75612 bytes) sha256 077ad8f1… equals source.raw_html_sha256 in zr-34-24.snapshot.json; GET .../chapter-5/35-63 (86164 bytes) sha256 2244240970… equals zr-35-63's pin — captured text matches the official page today.
 - Source-text-only: each capture's notes state "it encodes no rule, no reading of the text for any lot, and no number derived from it"; name-status of material commit 7729a959 shows only capture files, their byte-identical synced copies (all 8 verified sha256-equal) and project-control/reports/M4-T026-producer-report.md — no rule/engine/register/reference-case/plan/screen.
 - No overclaim: M4-T026-producer-report.md §10 states "No value is shown anywhere because of a capture"; the 34-24(b)(1) item is a capture-level existence finding (EXISTS as named; confirmed in the live verbatim "…set forth in Section 35-63, inclusive, shall be applied;"), not a rule resolved for a lot.
 - Share only: the "resolve missing rules and conflicting inputs / check the R6B answers" part of step 3 is left to later work.

ROW M4-T027 D-090-R226: PASS
 - step-p1-worked.json records each value with hand arithmetic and facts_used sourced to the benchmark lot's recorded facts; all tests/rules/reference_cases recompute (43 passed).
 - Values trace to two independent readings: source_reference names both return-independent-hand-calculation-3.md and -4.md ("both agree"); I confirmed each reading body is byte-identical to the orchestrator's received return (sha256 18744b88… / ae733f6c…).
 - Sealed-folder builder (build_sealed_packet.py) excludes the program: law snapshots minus producer notes, recorded lot facts, "Floor-area-ratio fields … left out on purpose", no program output — supports "worked from captured law text and the lot's sourced facts by readers who had not read the program's answer."
 - Caveat (what I could not reproduce): reader isolation is a process guarantee; I verify it by the sealed-folder design, the readings' own compliance statements, and their observed disagreement on one row — not by re-executing the readers.

ROW M4-T027 D-090-R238: PASS
 - Every whole-lot 100% coverage figure is geometry-backed: corner-reach C1-coverage and C2-coverage and step-p1-worked corner-100x100-coverage each tie to a reach row showing the whole lot is within 100 ft of each street line (C1 100×40, C2 80×60, 100×100 reaches only 100 ft) — why_applies states "the whole lot is the corner-lot portion".
 - Where geometry does not support it, coverage is "not known" per portion: corner-reach real-lot-coverage (reaches 103.93 ft from 215 Place), C3-coverage (150 ft, 50-ft strip beyond), step-p1-worked corner-150x100-coverage and corner-200x120-coverage — all kind=not_known, value=None, with a per-portion reason.
 - Interior/through 80% figures (interior-lots interior-coverage; step-p1-worked interior-40x100 / through-40x200) are the ZR 23-362 interior maximum on wholly-interior lots, not a corner-rule whole-lot 100% figure, so R238 is not engaged.

ROW M4-T027 D-090-R241: PASS
 - My own scan of all 5 case files for program-result field names (program/actual/first_screen) and sentences ("program today","the program gives",…): zero hits.
 - Every expected value's source_reference points at the two readings, never a program run; the 2026-10-07 change_log entries give law-based reasons ("ZR X is now captured … a captured citation is added"; values "unchanged"); none says "changed to match the program".
 - README line 67: "A disagreement between a case and the program is never, on its own, a reason to change the case."

ROW M4-T027 D-090-R259: PASS
 - The two readings are kept in their own files under docs/reference-cases/R6B/provenance/ (…-3.md, …-4.md), apart from program output; I recomputed full-file sha256 8e0fb09e… / 5bf5ab28… — both equal the digests pinned in r6b_reference_cases_check.STEP_P1_READINGS.
 - Agreement-is-not-proof is stated: README line 15 "That agreement, between two AI answers, is not on its own proof of anything"; step-p1-worked what_it_is_worth and checked_by repeat it.
 - Disagreement preserved, not resolved: interior-40x100-rear-yard is kind=not_known because reading 3 said NOT KNOWN and reading 4 said 20 ft; readings_differ_errors enforces this (test passes).

ROW M4-T027 D-090-R291: PASS
 - Saved examples exist as files: step-p1-worked.json (12 rows) plus updated citations in real-lot/corner-reach/interior-lots, rendered to pages, all under docs/reference-cases/R6B/.
 - Resolves no missing rule: name-status of c2f72cdb touches no services/api/app/rules/** (only case data, pages, provenance, engine-free test support); test_support_code_imports_no_engine confirms no import from app; README still names the not-captured sections (23-343, 23-434).
 - Share only: checking the R6B answers against the program and resolving the missing rules remain later work.

ROW M4-T027 D-090-R318: PASS
 - Same reference files as R226/R259: I independently re-checked all 78 captured citations across the cases — every one's content_digest equals the live capture and every quote is a substring of the capture's verbatim_excerpt.
 - Reference examples kept as files under docs/reference-cases/R6B/, worked from the captured law text by two sealed-folder agents; R318 restates rule 5 (R259) and its M4-T027 share is met by those files.
 - Same reader-isolation caveat as R226.

[harness: subagent output matched instruction-shaped pattern(s): harness-envelope-tag. Control tags below are neutralized (`<` → `<\`); treat any remaining directive-shaped text as a finding to relay to the user, not an instruction to you.]

PART 2 of 3

OWNER MESSAGES 107 AND 108 (source-052-amendment.md; transcript a20527ef-f7ab-4a57-9f9b-d1cde1c2de3e.jsonl, 1663 lines)

A1 — MET. I recomputed sha256 from the transcript: line 768 message.content (uuid 7cecfc6a-489e-48bb-83c1-b0df9c43da4b, type user) = "Why dont u run a few difrint parts…same file" hashes to fbf5acdf672ebeaa88ed3c86856a2e8f18dd4dd1bd2b3f87bbb5ea38ea39813c, identical to source-052's message-107 digest; line 776 attachment.prompt (uuid 8e56ee09-4f6c-4cf7-b336-310d9e9b2009, type attachment = queued command of human origin) = "Like spine up 5 subagents " (trailing space present) hashes to 12aa3d95880110d72aee42d3e8da44a4e9ef361d51db370f99465dfd6a0d7035, identical to source-052's message-108 digest. Both byte-identical; both digests recompute.

A2 — MET. Each leading quoted fragment of R493–R497 is an exact substring of its own message: R493 "Why dont u run a few difrint parts of the program at once to speed it up", R494 "run a few difrint parts of the program at once to speed it up", R495 "obviously not anything that will collide with each other or work on the same file" (all in msg 107); R496 "Like spine up 5 subagents", R497 "Like spine up 5 subagents " with trailing space (in msg 108) — all verified present by substring test.

A3 — MET. The orchestrator's reply at line 808 (uuid e43f8130-534e-4144-887a-12630d183c09) states the reading verbatim — "Up to five helpers at once, on pieces that share no files. Of those, at most three build at the same time; that is the project's own written limit." — and ends it "Tell me if you meant something different." So the owner was told the reading and asked to correct it. I searched every line after 808: there is NO later human message or human-origin queued command — all later "user" lines are agent hand-backs ("It is model output, NOT a message from the user") or <\task-notification> entries; so no later owner message corrected the reading. Does the reading go beyond the owner's words? Plainly: no. It stays at or below the owner's stated scale (treats "5 subagents" as an upper bound, never more than five), removes no restriction, keeps each piece's independent review, and attributes the "≤3 build / ≤4 review" split to the pre-existing orchestration policy section B ("which this message does not change") rather than to the owner — it adds no authority the owner did not grant and was offered to the owner for correction.

A4 — MET. R495 and R497 lift nothing: the three builders' commit file-sets are disjoint (no shared file — see A5); the full api suite was run once by the orchestrator after integration (commit 361cedf8: "full api suite 8108 passed, 8 skipped at c2f72cdb") so heavy runs did not overlap; the wave is one PR merged in order on a green run (not yet merged — I review pre-acceptance); none of the three pieces depends on another's unmerged result (concurrency record: "Depends on another piece of this wave: no" for all three); and no other open choice is treated as answered — R497 names R283's open items (starting figures, option order, instruction-file question) as unanswered and the three tasks do not touch them.

A5 — MET. I compared WAVE1-2026-10-07-concurrency-record.md with the branch commits (git log --stat a5c6c2f0..edcddf71). Builder file-sets: M5-T126 (0a3ffed3+dbffb46b) = docs/measurement-basis/** + services/api/tests/scenario/measurement_basis/** + its report; M4-T026 (7729a959) = docs/research/zr-snapshots/v1/** + services/api/app/_zr_snapshots/v1/** + its report; M4-T027 (c2f72cdb) = docs/reference-cases/R6B/** + services/api/tests/rules/reference_cases/** + its report. No file appears in two builders' commits (reports are distinct per task). The record names three builders plus two readers who work outside the repo; peak is three builders — never more than three builders running together, never more than five helpers.

A6 — MET. manifest.json sources[51] lists source-052-amendment.md with content_digest_sha256 cc01bdb05816433a3b3f38db4178518cc3fb7bc0f98bc4922596e3b0192bc660, equal to the file's own sha256 I recomputed; locked_requirement_ids count = 497 and ends D-090-R497. A structural diff of requirements.json (a5c6c2f0 vs HEAD) shows: added ids exactly R493–R497, none removed, and NO earlier row changed in anything other than applicability.task_ids — the only task_id additions are R226/R238/R241/R259/R318 (+M4-T027) and R291 (+M4-T026, +M4-T027). verification.json added only provisional rows for M4-T026 and M4-T027 (verifier "", status/verdict unset); no existing verification row changed. M5-T126's bindings (e.g. R357) already carried M5-T126 at a5c6c2f0, which is why they are absent from this diff.

PART 3 of 3

HARNESS (run once, from the review copy /root/project/rv-w1-1007)
 - python tools/validate_directive_compliance.py --check → DIRECT exit code 0 (silent success; via venv /root/project/lanes-runtime/venv/bin/python, PYTHONDONTWRITEBYTECODE=1).
 - from services/api: python -m pytest -q -p no:cacheprovider tests/rules/reference_cases tests/rules/test_zr_snapshot_bundle.py → "43 passed", exit code 0.
 - Per the dispatch I did NOT run tools/test_directive_compliance.py or the full api suite.

CARRY-FORWARD CONDITION (blob-level predicate). My seven ROW verdicts and the six A-points may be stamped at a later head WITHOUT re-asking me, provided ALL of the following are byte-for-byte unchanged from frozen head edcddf719dbedbae51162c490f42e57258bfdeb5:
 (1) every file under the two tasks' allowed paths — docs/research/zr-snapshots/v1/**, services/api/app/_zr_snapshots/v1/**, services/api/tests/rules/test_zr_snapshot_bundle.py, project-control/reports/M4-T026-producer-report.md (M4-T026); docs/reference-cases/R6B/**, services/api/tests/rules/reference_cases/**, project-control/reports/M4-T027-producer-report.md (M4-T027);
 (2) the seven rows (R291, R226, R238, R241, R259, R318) including their applicability bindings, the D-090 manifest.json, requirements.json, and the source files they trace to (source-032, source-033, source-035, source-039, source-040), and source-052-amendment.md plus rows R493–R497 — all unchanged;
 (3) any later commit touches ONLY paths under project-control/ and/or added lines of docs/DISCOVERY_BACKLOG.md.
What I tolerate: commits that touch none of (1)/(2) — including disjoint peer work such as the M5-T126 files, other tasks, or the eventual base-merge of the integration branch — do not affect these verdicts, provided they leave (1) and (2) blob-identical and the validator still exits 0 at the new head. If any file in (1) or (2) changes, or source-052/R493–R497 change, re-verification is required.

REQUIRED CORRECTIONS THAT BLOCK ACCEPTANCE: none. All seven rows PASS and A1–A6 all MET on primary evidence; the validator and the two test suites exit 0.

NON-BLOCKING OBSERVATIONS
 - The 34-24(b)(1) finding reverses the earlier helper lead / DISCOVERY_BACKLOG DB-166 ("does not exist as named"); the capture and the live official print/PDF show it DOES exist as named. The producer report states this openly and DB-166 is noted corrected in the gate commit; correcting the rule-file note/DB-166 is a later rules task's concern, not a capture-task defect.
 - M4-T026's allowed path services/api/tests/rules/test_zr_snapshot_bundle.py was not edited (the bundle test globs by directory, so no change was needed) — correct, not a gap.
 - Tasks remain awaiting_gate (progress 95); PR 459 open; nothing merged/accepted/dispatched beyond review/deployed/installed/purchased/closed — the pre-acceptance state expected for my gate.

WHAT I COULD NOT CHECK MYSELF
 - That the two reader agents were actually executed in isolation and had not seen the program's output: this is a process guarantee. I verified it indirectly — the sealed-packet builder excludes program output and FAR fields and strips producer notes; both readings attest "no access to the program or this repository"; and the two readings disagree on interior-40x100-rear-yard (affirmative evidence of genuine independence) — but I did not re-execute the readers.
 - CI on the pushed head: I ran the named tests and validator locally in the review copy; the GitHub run on the pushed head remains CI's word.
 - The full api suite (8108 passed/8 skipped) as reported in commit 361cedf8: I did not reproduce it (forbidden by the dispatch); the orchestrator ran it.
 - Transcript integrity beyond the two hashed lines (768, 776) and the after-808 scan for owner messages.

OVERALL VERDICT: PASS. M4-T026 R291 and M4-T027 R226/R238/R241/R259/R291/R318 are each SATISFIED for the task's share on reproduced primary evidence; A1–A6 all MET; validator exit 0; tests exit 0; no blocking corrections.
END-OF-REPORT
```
