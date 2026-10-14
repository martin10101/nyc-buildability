# M3-T007 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `98198b435c4dcacd3c2fa3d15f4c456ebc18079d` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R102, R104, R119.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-14 02:52 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M3-T007 (directive D-094, 3 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, independent software/source check at a frozen git head — not a human or professional legal review. I produced none of the work or records under review; I read every task record through git plumbing at the frozen head and reproduced each row's evidence from primary sources.

(1) HEAD VERIFIED
 - I read the frozen head 98198b435c4dcacd3c2fa3d15f4c456ebc18079d on branch task/wave24-report-v3 (base main b4704161); git confirms it is a real commit dated 2026-10-14 02:38:13Z.
 - Every directive, packet, gate, report, document and snapshot below was read with `git -C /root/project/w-wave20 show 98198b43:<path>`; no working-tree read was used for any row's evidence.
 - HEAD was at 98198b43 and the directive files were clean when I ran the one validator pass, and still 98198b43 after it.

(2) ROWS

ROW D-094-R102 — PASS
 - The zoning-law library continues as its own documents-only second line of work (task M3-T007), disjoint from the report lane: at the frozen head docs/zoning-law-library/options/ holds README.md + eight option files (02-03, 05, 06-07, 08, 09, 10, 11) + research-log.md, and options-sections.md gains second-pass blocks for options 2,3,5,6,7,8,9,10,11.
 - Each option file carries the unreviewed-draft/ADR-007 label and a section table with id, title, official URL, last-amended date, capture state (snapshot file or NOT CAPTURED) and handled state (rule file or NOT HANDLED), then a reading (applicable rule, definitions, exceptions, overlay/special-district effects, measurement basis, zoning-lot scope, lot facts with sources) and every not-sure point with a next step; I read option-02-03 and README in full to confirm this structure.
 - I reproduced primary evidence: the claimed-captured snapshots (zr-23-22, zr-23-432, zr-23-52, zr-33-121, zr-35-31/32/33, zr-32-131/161, zr-11-25, zr-23-20, zr-12-10-qualifying-*) all exist and the claimed-absent families (zr-24-*, zr-22-1*, zr-23-154, zr-32-421, zr-77-*, transit-zone-inner) are truly absent; the decisive 23-22 R6B row in zr-23-22.snapshot.json is standard 2.00 / qualifying 2.40 with no footnote, matching the file verbatim; research-log.md records the §23-154 HTTP-403 block twice, never evaded.
 - The material commit 9730b3e6 touches only the 11 allowed paths (all under docs/zoning-law-library/ plus the producer report), sharing no file with the report lane. Stays open for later work: the first-pass library-root files (coverage.md, cross-reference-closure.md, pitfalls.md) are M3-T006's scope and out of this task's edit set, and contracting the follow-on rules task plus capturing the NOT CAPTURED sections (backlog DB-253) remain future work.

ROW D-094-R104 — PASS
 - Read-only research helpers fed the work: ten saved read-only returns are in the session folder (/root/project/lanes-runtime/owner-docs/session-2026-10-14a/research/return-H{A,B,C,D,E,F,G,S,X1,X2}.md) — seven law readings, the sample's options (HS), the verbatim follow-ups (HX1) and the three open legal questions (HX2) — matching the evidence-map's "ten read-only research returns."
 - The session notes (2026-10-14) show these helpers dispatched "all read-only; 0 building"; only one helper ever built (the M3-T007 builder, agent ad76f4537916bbd49, in its own isolation worktree reset to 680cbe77), so R104's sub-limits of at most 3 building and never sharing files are honored (1 builder, no shared repo file).
 - The builder return confirms a single commit 63fc2b19 cherry-picked as 9730b3e6 touching only the 11 allowed paths; I reproduced its LF sha256 for options-sections.md (42a96d87…) and option-02-03 (e77fa94f…) at the frozen head and both match, so the integrated content is byte-identical to the helper-fed build.
 - How R104's eight relates to R119's ten: R104 set the standing ceiling at 8 at once (beyond-5 read-only); the run used up to 10, which exceeds R104's 8 but is authorized because R119 lifted the headcount to 10 for this one night — see R119. Stays open: nothing for this task; R104 remains a standing authorization whose 8-cap returns once tonight's session ends.

ROW D-094-R119 — PASS
 - The task was contracted (f9e43daa) and built on the night of 2026-10-14, the night for which the owner approved up to ten helpers at once (source-013, verbatim: "i want to lunch 10 subagents"); R119's required_harness is the testable condition and the session notes meet it.
 - The dispatch lines show the maximum concurrency was exactly ten helpers running at once (01:30, 01:38, 01:40, 01:41) and never more than ten; the building count was at most one at any moment (never more than three); and no two helpers shared a repo file (research helpers and packet/evidence/P8 readers wrote only their returns or private scratch dirs, per the logged audits; the sole repo writer was the M3-T007 builder in its own worktree).
 - Every running helper's work was a tracked task or read-only preparation for one: research returns feed M3-T007, packet checks prepare M5-T165/166/167/171/175/177, the P8 readers prepare M5-T177, the builder is M3-T007 itself.
 - Plainly, R104's eight and R119's ten stand in sequence: R104 is the standing eight-at-once ceiling (beyond-5 read-only), and R119 temporarily raised only the headcount to ten for the single night of 2026-10-14 while keeping R104's at-most-three-building and no-shared-files sub-limits; the observed run (up to ten, one building, no shared files) sits inside R119 and inside R104's unchanged sub-limits. Stays open: nothing for this task; R119's ten-helper allowance expires with tonight's session and reverts to R104's eight.

(3) BINDING B1–B5
 - B1 PASS: the contract commit f9e43daa appended "M3-T007" to exactly the applicability.task_ids of R102, R104 and R119 and to no other row; the only other change to requirements.json in that commit is the updated_at field (no requirement body/text edited), and those three rows are byte-identical at the frozen head.
 - B2 PASS: directive_registry.sha256_text_artifact over requirements.json at the frozen head = 64f77b64b02370d6b216d1ed80cae6817ec5f2735a761a594efd01f79d6aa605, equal to the manifest's requirements_content_digest_sha256; `python3 tools/validate_directive_compliance.py --check` returned exit 0 (quiet) with HEAD at the frozen head and the directive files clean.
 - B3 PASS: verification.json holds exactly one M3-T007 entry with applicable_requirement_ids = [D-094-R102, D-094-R104, D-094-R119], verifier "" (empty), reviewed_sha null, and all three requirement rows state "pending".
 - B4 PASS: reg.evaluate_task_refs on the M3-T007 packet returned ok=True with applicable_ids == cited_ids == [R102, R104, R119], and empty missing_ids, invalid_refs and unresolved.
 - B5 PASS: the applicable set derived across the whole active registry is exactly those three rows with missing_ids empty, so no other active-directive requirement applies to M3-T007 uncited; the validator pass corroborates registry-wide integrity. Gates: G0 PASS at the contract head f9e43daa; G1 PASS (data-contract-verifier) and G2 PASS (orchestrator self-check) both recorded at e27bc2a0 — one content identity — with the two G1 reviewers having read 9730b3e6 whose eleven blobs are byte-identical to e27bc2a0 and to the frozen head; CI run 38501250522 at e27bc2a0 shows 21/21 jobs success.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review while this blob-level predicate holds: the eleven allowed-path files keep their frozen-head blob ids — options-sections.md 6307145bd723dd0e1aa8ce442ac38543e2654fc2; options/README.md 67653c2a6c560f4007a08df7be1ba43ed7abacb6; option-02-03 c10ca0324a5f8e86bf4d8fc89695fe372b1e67b4; option-05 ee6e24c44673febaa5b5e1fc4a72b0c674f57fc5; option-06-07 6d9c2c399cf396798ed85dde3dda63ae76ea70cf; option-08 977709f01f968eca49af60e00a486792ed08ec0b; option-09 a7c4d2110f53baec3e82dd912ea9f7d744f35175; option-10 f52b826403167a0880f01de41bac8e7bc10d9a8f; option-11 0d5c254df11ac245fcefb5e3a51512bc59b92375; research-log.md 86c9e115297e8e92456e66727ed1738372590013; project-control/reports/M3-T007-producer-report.md f1086549fef8f9e9bb267c65bdc78cf2db0d4140 — AND rows R102, R104, R119 keep their text and their M3-T007 applicability binding (requirements content digest 64f77b64…).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other wave tasks under services/, apps/, packages/, docs/, .claude/; their packets, gates, reports and directive bindings; new rows appended to D-094; ledger/state), plus this task's own acceptance records (its gates/reports, the verification.json M3-T007 row, task status), and a merge of the main line that changes none of the eleven predicate blobs or the three rows — none of these voids this verdict.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I verified concurrency, building count, shared-file isolation and tracked-work from the orchestrator's session notes plus the saved helper returns and the logged P8-reader path audits; I did not have the raw subagent dispatch transcripts, so my concurrency reconstruction rests on those records rather than an independent process log.
 - R119's non-harness sub-clauses (no model override, no timers, no unattended merges, gates unchanged) are outside its required_harness and I could not fully verify them from the notes; I note that the builder's material commit 63fc2b19 carries a "Co-Authored-By: Claude Opus 5.5" trailer, which I could not reconcile against the opus-4-8 subagent pin (D-064/D-085) — it may be a dispatch-time model choice or an attribution-config artifact, and the dispatch line records no model override. This is outside R119's harness and the three rows' core authorizations, so it does not change the SATISFIED verdicts; I flag it for the orchestrator to reconcile against the subagent transcript if the model pin is to be enforced.
 - I did not fetch the NOT CAPTURED ZR sections' verbatim text (§23-154 is a durable HTTP 403; Article II Ch.4/Ch.7, 77-xx, 24-xx, 22-1xx, etc.): the files correctly mark them NOT CAPTURED / access-blocked with next steps and do not rely on them for the benchmark lot.
 - I did not re-derive the R6B reference cases (step-p4/p5-worked.json, overlay-reading.json); per the brief I checked a pointer only, confirming step-p5-worked.json records "Served transit zone = Outer Transit Zone (a recorded value, not a rule)" from PLUTO BBL 4073340070, which agrees with the option files.
 - I did not run the full tools/test_directive_compliance.py (forbidden; hours) or the full api suite; the authoritative harness evidence I relied on is validate_directive_compliance.py --check (direct exit 0 at the frozen head) plus CI run 38501250522 (21/21 success at the submit head e27bc2a0, whose eleven blobs are byte-identical to the frozen head).
END-OF-REPORT
```
