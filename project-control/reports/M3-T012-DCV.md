# M3-T012 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `4269c75751de36db1726bd22ffe9a20465d8a668` (branch `task/wave27-comparison-appendix`, review copy `git plumbing at the frozen head`). Directives D-093, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R038, R050, R052, R003, R104.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T11:42:54Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M3-T012 (directive D-094, 5 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is not a human or professional review. The MIH/IH legal reading in the record stays an unreviewed draft (ADR-007); I did not legally certify it and was instructed not to re-derive the settled R6B figures. The task cites 5 rows across two directives: D-093 R038/R050/R052 and D-094 R003/R104.

(1) HEAD VERIFIED
 - I read the frozen head 4269c75751de36db1726bd22ffe9a20465d8a668 on branch task/wave27-comparison-appendix in /root/project/w-wave20 via git plumbing (the worktree itself is at a later descendant fcd953e1; I did not rely on it for frozen content).
 - The task's 5 allowed-path files have identical blob ids at the producer commit 8891fb99, the submit head ac7b69e9, and the frozen head 4269c757 (NB-07 7e9b650f, NB-05 3ba32636, README eae99f8e, RESEARCH_REQUESTS 117ec533, producer report 16932d1b), so material identity is byte-stable and the gates recorded at ac7b69e9 apply to 4269c757.
 - ac7b69e9 is an ancestor of 4269c757; the later commit only added acceptance records (reviews, evidence map, gate records), not material files.

(2) ROWS
ROW D-093-R038 — PASS
 - Source re-derived: D-093 source-001.md lines 108-111 and the mapping table line 222 carry the owner's verbatim "one concise record ... Question and scope ... Primary evidence (authority, title, URL, ID, page, document/effective date, retrieval date, excerpt/field) ... save permitted source material"; the registry row reproduces it faithfully (not weakened/invented).
 - This task's share is met: docs/research/evidence-records/NB-07-mih-inclusionary-status.json is one concise record with question+scope (BBL 4073340070; lot_scope zoning_lot_unconfirmed; whole_site; current_law) and primary evidence E1-E5 each carrying authority, title, URL, reference/ID, document_date, retrieved and excerpt.
 - Permitted source material is saved: E4 carries saved_copy docs/research/zr-snapshots/v1/zr-appendix-f.snapshot.json with LF-sha256 0a7952bd...40008, which I recomputed on the frozen-head blob and it matches exactly; the live GIS layers keep saved_copy null with the query excerpt recorded.
 - Stays open: only the un-transcribed nycmih/nycihda metadata PDFs and the Appendix F CD 11 map image, correctly kept as recorded searches/conditions; the broader row also applies to M0-T190/M5-T158/M5-T160, whose records are other tasks' shares.

ROW D-093-R050 — PASS
 - Source re-derived: D-093 source-001.md line 133 / table line 234 states the reviewer must open the decisive sources, consider exception+counterexample, work the result before the code, and report pending if review is unavailable; the row reproduces it.
 - Independent review is present and reproducible: NB-07 review.agent_reviews has two entries (official-source-researcher, data-contract-verifier), both verdict "agrees", reviewed_revision 1; the two sealed returns return-research-MIH.md and return-check-MIH-independent.md were worked independently (the check states "sealed (I did not see any other researcher's answer)").
 - The existing review workflow's G1 gate (data-contract-verifier) independently re-opened MapPLUTO, nycmih, nyih and Appendix F ("I did not trust the packet summary or the two returns"), considered the UAP exception and the qualifying-residential-site R1-R5 counterexample, and reproduced OUT/OUT with distances 5,925 ft and 17,618 ft; there is no code to check (code_paths []), so "before the code" is met in substance.
 - Stays open: the downstream UAP/23-22/23-432 affordable-pathway reading is intentionally carried as an unreviewed draft (ADR-007), i.e. reported pending as R050 permits; only the membership interpretation is reviewed.

ROW D-093-R052 — PASS
 - Source re-derived: D-093 source-001.md line 137 / table line 236 requires the smallest check so a result cannot be marked verified when its evidence record is absent/stale/unresolved, validating structure only and certifying nothing, with no verified:true treated as proof; the row (classification harness) reproduces it.
 - I ran `python3 tools/research_record_check.py --check` -> EXIT 0, PASS, 7 records; NB-07 reported status=answered_from_primary_source, code_current=True, review_state=current, requested_label=Provisional.
 - The checker prints "structural check only; not a professional verification" and "no record claims the Verified label without meeting every condition" — nothing is labelled Verified and there is no verified:true field; NB-04 is reported (not failed) code_current False and NB-05 reported stale, confirming the check surfaces staleness without certifying.
 - Stays open: nothing for this task; the check itself was authored under M0-T190 and is reused here.

ROW D-094-R003 — PASS
 - Source re-derived: D-094 source-001.md line 19 / table line 208 carry the owner's verbatim "Research and verification (D-093) applies; put its dispatch clause in every brief." and "Do not repeat completed work."; the row reproduces both.
 - Completed work was reused, not repeated: the producer report states "I did not re-run the live DCP nycmih/nyih/MapPLUTO/ZAP fetches; I relied on the two sealed independent returns" and copied the validated draft byte-identical, re-verifying each field — demonstrable reuse of the two prior determinations.
 - The D-093 workflow was applied: the record keeps unresolved inputs unresolved (3 conditions, recorded searches), distinguishes evidence from the draft interpretation, and labels nothing Verified; my own verifier brief carries the D-093 dispatch clause.
 - Stays open: nothing material for this task; the session-wide "dispatch clause in every brief" obligation continues across other briefs (dispatch-prompt texts are not committed — see section 6).

ROW D-094-R104 — PASS
 - Source re-derived: D-094 source-004-amendment.md carries the owner's verbatim "That's question I2 in your file" / "So please add that on this it should spone up agents" and its reading (up to 8 helpers when extras only research; at most 3 building; never sharing files); the row reproduces it.
 - This task's share is met: it ran one documents-only producer (official-source-researcher) whose five files are in no other in-flight packet; the collision with M5-T170 (which held RESEARCH_REQUESTS.md and the README) was resolved by a hard dependency, and I confirmed M5-T170 status=accepted at the frozen head, so no overlapping parallel write occurred.
 - The G0 report records "No file is shared with a task in flight"; the diff touches only the five allowed paths, consistent with the never-sharing-files rule.
 - Stays open: the session-wide concurrency caps (<=3 builders, <=8 helpers at once) and "next session spins up research agents" are ongoing session obligations verified here only for this task's single producer (session-notes matter — see section 6).

(3) BINDING B1-B5
 - B1 PASS: contract commit a491433a appended "M3-T012" to applicability.task_ids of exactly the 5 cited rows (D-093 R038/R050/R052; D-094 R003/R104) as an append-only edit; no requirement text changed; the producer commit 8891fb99 did not touch any requirements.json. At the frozen head all 5 rows still carry M3-T012 and their text matches the source files.
 - B2 PASS: I recomputed sha256_text_artifact (LF-normalized) of each requirements.json at the frozen head and it equals the manifest's requirements_content_digest_sha256 — D-093 afca00f0...47dd4, D-094 209ddf6b...fe29e1. The contract commit carried the resync + an audit_log applicability_bound entry + affected_tasks append in the SAME commit for both directives.
 - B3 PASS: each directive's verification.json has exactly one M3-T012 task_verifications row — D-093 with [R038,R050,R052], D-094 with [R003,R104] — producer official-source-researcher, verifier "", every requirement state pending, reviewed_sha null.
 - B4 PASS: I reconstructed derive_applicable/_applicability_matches over all 92 active directive folders at the frozen head using the registry's own logic; the applicable set is exactly {D-093-R038,R050,R052, D-094-R003,R104} — applicable == cited, zero missing, zero cited-not-applicable, zero wildcard hits, zero unresolved.
 - B5 PASS: the same full scan found no other active-directive requirement applicable to M3-T012 uncited. Gates: G0 (orchestrator) PASS, G1 (data-contract-verifier, independent) PASS, G2 (orchestrator self-check) PASS; G1 and G2 share one content identity 8b8f676b...e91b92 at ac7b69e9. `python3 tools/validate_directive_compliance.py --check` -> DIRECT_EXIT=0 (quiet on success); CI run 38726761775 at ac7b69e9 completed success, 21/21 jobs.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided this blob-level predicate holds at the stamping head: the five allowed-path files keep their frozen-head blob ids (NB-07 7e9b650f6bd82cd9972d77391f0e6574136fb886; NB-05 3ba32636f7ed89ae0c3caa75f7a3e8c1454de1b8; docs/research/evidence-records/README.md eae99f8ed84b490842507ab7eec4bc3d6ac03ebc; docs/RESEARCH_REQUESTS.md 117ec533418f12e1458a968fb038c4d1bc5f8a1e; project-control/reports/M3-T012-producer-report.md 16932d1b72d6c1529eca527e649c474e0ca35261); the text of the 5 rows is unchanged; each row still lists M3-T012 in applicability.task_ids; and each directive's manifest requirements_content_digest_sha256 stays in sync with its requirements.json.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file — other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets, gates, reports, the directive bindings of other tasks, new rows appended to either directive, and ledger state — plus this task's own acceptance records (reviews, evidence map, gate records, verification.json stamp) and a merge of the main line that changes none of the predicate files. Such changes do not require a re-review; only a change inside the predicate does.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not re-run the live DCP nycmih/nyih/MapPLUTO/ZAP fetches (no server/browser permitted); the membership facts rest on the two sealed determinations and the G1 reviewer's independent live re-open, which I read but did not re-execute. I did independently reproduce the one repository-side fact — E4's LF-sha256 against the committed Appendix F snapshot — and it matches.
 - The actual dispatch-prompt texts given to the producer and the two sealed researchers are not committed to the repo; I confirmed the D-093 dispatch clause only in my own verifier brief and inferred the others from the record's adherence (reuse of completed work, conditions preserved, nothing Verified).
 - Session-wide concurrency counts for R104 (<=3 builders / <=8 helpers at once across the whole session) live in session notes outside the frozen head; I verified only this task's single documents-only producer and its no-shared-files sequencing behind the accepted M5-T170 dependency.
 - The downstream UAP / ZR 12-10 / 23-22 / 23-432 / 27-131 legal reading is an unreviewed draft (ADR-007) by design and per my brief I did not re-derive the settled R6B figures; I confirmed only that the draft is internally consistent with the two sealed determinations and that the R6B reference cases exist under docs/reference-cases/R6B/cases/.
 - My research_record_check and directive-validator runs executed against the working tree (fcd953e1, a descendant); they are authoritative for the frozen head here because I confirmed the records, the 5 rows' M3-T012 bindings, and both manifest digests are byte-stable/in-sync between the frozen head and that head.
END-OF-REPORT
```
