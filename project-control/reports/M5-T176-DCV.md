# M5-T176 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `6e5a528791ecade258dd11b338833d92b4e4ab4d` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R036, R037, R044, R079.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 23:58 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T176 (directive D-094, 4 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only
reproduction of primary evidence — NOT a human review and NOT a professional or legal
determination. The case's zoning readings are AI drafts (ADR-007); two agreeing AI
readings are not proof.

(1) HEAD VERIFIED
 - I read the frozen head 6e5a528791ecade258dd11b338833d92b4e4ab4d on task/wave24-report-v3 in /root/project/w-wave20; at start HEAD equalled it exactly.
 - While I worked, disjoint peers advanced the branch to cd6d7fc3 (M5-T165/M5-T166 reworks); I pinned every read to 6e5a5287 via `git show 6e5a5287:<path>`. The M5-T176 packet, D-094 requirements.json, manifest.json and verification.json are byte-identical on disk vs the frozen head.
 - Product files (docs/reference-cases + services/api/tests/rules/reference_cases) are byte-identical between the submit head bc8c650a and the frozen head 6e5a5287 (`git diff --stat` empty); the frozen head adds only project-control gate/report/task/state files.

(2) ROWS
No D-090 requirement is applicable to this task (derive_applicable returned only the four D-094 rows). D-094 rows in numeric order; each judged for THIS TASK'S SHARE (step-P7 reference rows only — no rule file, engine, result, capture, register entry or human verdict).

ROW D-094-R036 — PASS
 - Share = the independent evaluation of ZR 23-344(b) AND the R6–R12 adjoining-side-line provision 23-344(c)(3) against the actual zoning-lot/boundary evidence; the "update the diagram and conclusion" clause is report/engine work owned by other tasks.
 - The case short-block-rear-yard carries rows for 23-344(b) (b-what-measured…b-block-boundary, M1–M10, real-lot-*) and for 23-344(c)(3) (c-1-vs-c-3, M7, M8, real-lot-z1/z2-rear-yard, real-lot-beyond-100-sliver, real-lot-missing-facts), evaluating the real lot under Z1 (lot 70 alone) and Z2 (lots 70+1) on each measurement basis from block-7334 outlines, DCM centrelines, PLUTO rows and tax-map labels.
 - I verified the quotes against the captures: zr-23-344.snapshot.json verbatim_excerpt contains the (b) and (c)(1)/(c)(2)/(c)(3) text exactly (content_digest 91f94915… matches the citation), and zr-12-10-short-dimension-of-a-block (digest 3ec2dadd…) matches. Both readings reach these on the same basis.
 - Stays open for later work: the rear-yard diagram+conclusion update and the engine (M5-T167), which consumes this case — outside M5-T176.

ROW D-094-R037 — PASS
 - Share = the reference rows may record no unconditional zero rear yard and must not treat the corner test as the only exception.
 - real-lot-z1-rear-yard and real-lot-z2-rear-yard are kind=not_known with value=None; each names its conditions (measurement basis, zoning lot, neighbour lot-line kind) and quotes ZR 23-344; what_it_does_not_establish states the 23-344(a) corner test is never worded as the only exception.
 - The GIS figures (e.g. 203.13 ft, reach 99.97 ft) carry a basis and are never used to infer an unconditional zero rear yard; on the GIS/centreline basis the frontage is NOT a short dimension, so the row stays not_known. The real_lot_rear_yard_errors guard plus mutation test test_an_unconditional_no_rear_yard_in_a_real_lot_row_is_refused reproduce green (an injected unconditional "no rear yard" is refused).
 - Nothing stays open in this task's share.

ROW D-094-R044 — PASS
 - Share = invent no geometry; every figure traces to source with a basis. This task produces no drawing/layout (none in allowed_paths).
 - 11 quantities across the real-lot rows each carry exactly one of the nine QUANTITY_BASES (administrative_record / printed_tax_map / gis / derived); quantity_basis_errors plus its mutation tests (missing basis, second basis) reproduce green; program_result_errors == [] (no program-run value).
 - Where the two readings' figures differ (215 St–215 Pl centreline 260.02 ft reading 1 vs 261.0 ft reading 2) both are kept and real-lot-short-dimension stays NOT SETTLED; the ten made-up cases M1–M10 are labelled made-up, not property measurements.
 - Nothing stays open in this task's share (R044's drawing-geometry thrust is exercised by the drawing tasks M5-T164/M5-T166).

ROW D-094-R079 — PASS
 - Share = an explicit, independently worked applicability check of ZR 23-344(b) (short-block-frontage) beside the 100-ft point test, before completion; the exemption not presented as established.
 - The case IS that applicability check: what (b) measures; "< 230 feet" strict (b-less-than-230, confirmed by M1 229.99 yes / M2 230.00 no / M3 230.01 no); measuring "within 100 feet" (not_known); what can bound a block; M1–M10; and the real lot under Z1/Z2 on each basis — set beside the 100-ft corner (a) test (fit-b-on-corner-lot, fit-multiple-apply, real-lot rows naming both (a) and (b)/(c)).
 - The exemption is NOT established: real-lot-z1/z2-rear-yard stay not_known on unresolved measurement basis; NB-03 (read only, revision 2) is research_status "interpretation_awaiting_review". Two independent readings (provenance 15 and 16) underlie it.
 - Stays open for later work: the engine change (M5-T167), the report's rear-yard item, and NB-03's independent review/promotion — owned by M5-T163/M5-T164/M5-T165/M5-T167.

(3) BINDING B1–B5 — all PASS
 - B1 PASS: at the contract commit d1a0f2b0 "M5-T176" was appended to applicability.task_ids of all four rows; each row's text is byte-unchanged vs the pre-contract capture (verified text-equality R036/R037/R044/R079). No row text was changed by this task.
 - B2 PASS: I recomputed directive_registry.sha256_text_artifact(requirements.json) on the frozen-head bytes = 66a6f6ec9f7a46a5cdef444821e0788cfdd7b515cc1bdadd22eeb451960c7114, equal to manifest.requirements_content_digest_sha256. (I could not re-derive requirements_id_digest_sha256 — no matching public helper — but the validator exit 0 covers manifest/id integrity.)
 - B3 PASS: verification.json holds exactly one M5-T176 row; applicable_requirement_ids = {R036,R037,R044,R079}; verifier=""; all four requirement entries state=pending, evidence=[], reviewed_sha=null.
 - B4 PASS: reg.evaluate_task_refs(packet) → ok=true, applicable_ids == cited_ids == the four, missing_ids/invalid_refs/unresolved all empty.
 - B5 PASS: reg.derive_applicable(packet) returns exactly those four ids across all active directives — nothing else applies uncited. Gate records: G0 PASS (orchestrator/administrative, sha 89c63124), G2 PASS (orchestrator self_check), G3 PASS (data-contract-verifier), G4 PASS (qa-engineer); G2/G3/G4 share one content identity (content_manifest_sha256 2fbe086b…, reviewed_sha bc8c650a). G3/G4 reviewers are in the packet's reviewer_agents.
 - Independent reproduction: ruff clean; `pytest tests/rules/reference_cases` 118 passed incl. 19 step-P7; r6b_reference_cases_render.py --check PASSED; modularity_check --check exit 0 (no FAIL; only pre-existing warnings, none on this task's files); validate_directive_compliance.py --check exit 0. The quote-integrity checker is genuine (digest + official_url + markup-stripped verbatim-substring). Both readings hash to the pinned digests (ba7efca9…, 1c806925…), differ, and end with END-OF-REPORT. CI run 38184931071 at the submit head bc8c650a = all 21 jobs success (api, control-plane, modularity, contracts, web, web-e2e, security gates).

(4) CARRY-FORWARD CONDITION
This PASS may be stamped at a later head WITHOUT re-review while BOTH hold:
 - Blob-level predicate — at the stamping head the eleven allowed-path files keep their frozen-head blob ids: short-block-rear-yard.json ccea9e0f; short-block-rear-yard.md ded7a361; README.md ad93cf74; provenance/return-independent-hand-calculation-15.md 1e9c1596; -16.md cee250bf; r6b_reference_cases_step_p7.py fbcbc065; test_r6b_reference_cases_step_p7.py 256d534e; r6b_reference_cases_lib.py 6bd4a915; r6b_reference_cases_check.py 80d65b74; r6b_reference_cases_render.py 01912f3d; test_r6b_reference_cases.py 41da63a4 — AND the four rows' text and their M5-T176 applicability binding unchanged in requirements.json (manifest content digest 66a6f6ec…).
 - Broad disjoint-peer tolerance — later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/ including docs/research/NB-04 by M5-T166, .claude/; other packets, gates, reports, directive bindings of other tasks; ledger state), plus this task's own acceptance records (gates/reports/verification.json/state) and a merge of main that changes none of the predicate files. I already observed this holding: peers advanced HEAD to cd6d7fc3 and M5-T166 edited NB-04, yet all predicate files stayed byte-identical.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The sealed folder itself (sealed-p7-v2 on the private build server) — I did not open it. I confirmed the two readings are byte-pinned, genuinely differ, and that their law quotes match the repo zr-snapshots; I relied on the G3 reviewer's statement that the sealed captures equal the repo snapshots.
 - The two readings' actual independence/no-collusion — I can confirm two distinct byte-identical-to-pin files with consistent agreements and recorded disagreements (centreline 260.02 vs 261.0; the R6B-suffix condition raised by reading 2 only), but not the process that produced them.
 - CI at the eventual accept head — the main CI run at the exact frozen head 6e5a5287 was CANCELLED by an immediate peer push (benign duplicate-push signature; context-budget and secret-scan succeeded there). The green 21/21 run is at bc8c650a, whose product content is byte-identical to the frozen head. Reading CI green at the actual accept head is the orchestrator's D-090-R639 step, not mine.
 - requirements_id_digest_sha256 was not independently recomputed (helper name differs); covered indirectly by validator exit 0.
 - This is an AI reproduction, not a human or professional legal review; the case's zoning interpretations are unreviewed drafts.
END-OF-REPORT
```
