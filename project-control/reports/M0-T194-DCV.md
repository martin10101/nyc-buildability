# M0-T194 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `72fe33cfbf2cb4a02428fa874fac690bdc1ad107` (branch `task/wave24-report-v3`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R056, R057, R069, R072, R077, R083.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 20:40 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T194 (directive D-094, 6 rows)
VERDICT: PASS
PART 1 of 1

I am an AI agent (directive-compliance-verifier). This is an independent machine review, not a human or professional review. I produced none of this work or its records. I judged each item from primary evidence (owner source files, the task files at the frozen head, the images outside git, re-run scripts, git objects), treating every report/map/gate/brief as an unverified claim.

D-093 agreement: I agree this task changes no property fact, rule, calculation or certainty label. The two material commits touch only project-control/reports/D-094-visual-proof-before.md; no rule, engine, result or label file is in scope. It only freezes the "before" pictures and word counts.

(1) HEAD VERIFIED
 - git -C /root/project/w-wave20 cat-file -t 72fe33cfbf2cb4a02428fa874fac690bdc1ad107 = commit; it is the tip of task/wave24-report-v3 (commit msg "M0-T194 and M0-T193: submitted at 4e92b20c").
 - I read every file through `git show 72fe33cf:<path>`; the live worktree HEAD moved to 5a8228c1 mid-review (a disjoint peer wave-24 commit), so I did NOT rely on on-disk checkout state.
 - Base is main b4704161; contract head fc96fd9c; claim head aac892fc — all confirmed in git.

(2) ROWS (directive order; all six are D-094)

ROW D-094-R056 — PASS
 - Owner words match source-001 Acceptance checks verbatim: "Render and inspect every exported page at readable size... a text extraction alone does not verify layout."
 - This task's share is the before render of every exported page: the manifest pins page-1..9.png (colour) and grey-1..9.png at 110 dpi; I recomputed all 115 sha256 = 115/115 match, perfect 1:1 (no missing/extra).
 - I confirmed report.pdf = 9 pages A4 and page/grey PNGs = 909x1287 px (A4 at 110 dpi); I opened page-1 and page-8 — genuine, readable renders (footers "Page 1 of 9", "Page 8 of 9").
 - Open for later: the after-side render and the per-page layout inspection against the redesign belong to each page-changing task; nothing of the before share stays open.

ROW D-094-R057 — PASS
 - Owner words match source-001 verbatim: "Check the website at representative desktop and mobile sizes... figures, labels, caveats, and source references appear in both outputs."
 - Before share is the website capture: the manifest pins w{320,390,768,1024,1440,1920}-results-viewport/-strip-NN/-report-preview; I recomputed every sha256 (within the 115/115) and viewport dims equal their widths.
 - I opened w390-results-viewport (mobile Results panel, 20,150 sq ft) and w1440-report-preview (desktop Results + Report block + report start) — both genuine captures at mobile and desktop widths.
 - Open for later: the figure/label/caveat/source parity check between the new website and PDF is the report-redesign tasks' share.

ROW D-094-R069 — PASS
 - Owner words match source-002 verbatim: "I read and visually checked all nine pages... the presentation problem is largely unchanged."
 - Before share freezes the exact report the reviewer audited: report.html is byte-identical (cmp) to session-2026-10-11c/print-main23/report.html (the print from main b4704161), sha256 d2359b16 on both.
 - Product identity holds: `git diff --name-status b47041611 fc96fd9c -- apps/ services/ packages/` shows only one added test file (services/api/tests/contracts/test_results_contract_1_5_0.py), no runtime diff; page-1 shows "17 to 22 apartments" and page-8 the "29" ceiling, matching the reviewed state.
 - Open for later: R069's substance (next revision judged first on presentation) is the redesign work, not this freeze task.

ROW D-094-R072 — PASS
 - Owner words match source-002 verbatim: "option-comparison and building-diagram pages are unchanged... approximately 10% more text."
 - Before share records the baseline budget: I re-ran metrics_before.py once — PDF words/page 364/193/291/338/245/719/296/346/201 = 2993; HTML per-section 349/428/316/225/948/505 = 2775 — exactly matching the manifest.
 - Before screenshots of the named pages exist (option-comparison section; page-5 scenario/building-diagram) and are sha256-pinned.
 - Open for later: the after-comparison proving those pages changed and the text did not grow is each page-changing task's share.

ROW D-094-R077 — PASS
 - Owner words match source-002 verbatim: "Pages 6-9 Supporting information is useful, but explanations repeat... clearly organized evidence appendix."
 - Before share records the baseline repeats: my re-run reproduced PDF 3 distinct sentences / 7 printings and HTML 3 distinct / 8 printings, each sentence listed, matching the manifest.
 - Before screenshots of pages 6-9 (page-6..9.png colour + grey) are pinned and sha256-verified.
 - Open for later: the actual removal of repeats, the appendix reorganization and the after-count are later report tasks' share.

ROW D-094-R083 — PASS
 - Owner words match source-002 verbatim: "before-and-after screenshots of every changed PDF page and corresponding website view, checked against the existing design requirements."
 - This task is the explicit before (H0) half: every page (9 colour + 9 grey) and every website width (viewport + strips + report preview at six widths), with re-runnable commands and sha256s — I verified 115/115 hashes and that metrics-run1.json == metrics-run2.json byte-identically (S4).
 - The before set is self-consistent and re-runnable; metrics reproduce exactly on a fresh run.
 - Open for later: the "after" screenshots of every changed page/view and the design-contract check are each page-changing task's share.

(3) BINDING B1-B5
 - B1: In the contract commit fc96fd9c, exactly the 6 rows gained M0-T194 in applicability.task_ids; diff vs fc96fd9c^ shows no `text` change and no non-task_ids field change on any row. The R109/R110 re-read is recorded: audit_log "requirements_reread" at 2026-10-11T19:14:51 in parent f0540a03, digest resynced same commit; R110 text unchanged; R109's owner-quoted single-quoted fragment is byte-identical (only the post-colon interpretation and required_harness were refined to source-008). Owner quoted words unchanged.
 - B2: I recomputed sha256_text_artifact over requirements.json at the frozen head via directive_registry = bae4d0cd78c523f2...e3a9, equal to manifest.requirements_content_digest_sha256. MATCH.
 - B3: D-094 verification.json has exactly one M0-T194 row; applicable_requirement_ids = the 6 ids; producer "orchestrator"; verifier ""; all six requirement states "pending"; reviewed_sha null.
 - B4: I scanned requirements across all 92 directive requirements.json at the frozen head; the applicable set for M0-T194 = {R056,R057,R069,R072,R077,R083} == the packet's cited set. applicable == cited.
 - B5: No other active directive carries an uncited row for M0-T194 (the only hits are the six D-094 rows). Gates: G0 PASS (orchestrator, reviewed fc96fd9c), G2 PASS (orchestrator, 4e92b20c), G3 PASS (visual-quality-reviewer, 4e92b20c) — G2/G3 at one content identity (reviewed_sha 4e92b20c; manifest blob 6ac8ce1f). The [ORCH-CORRECTED] commit 2098b043 diff is 3 wording/command hunks only; no sha256 table row, metric value, or scenario line changed. Both material commits (c5326454, 2098b043) touch only the allowed path. validate_directive_compliance.py --check exited 0. Cited CI runs are green: 38171255530 at 4e92b20c (success) and 38170691051 at 2098b043 (success).

(4) CARRY-FORWARD CONDITION
 - Blob-level predicate: the packet's only allowed-path file project-control/reports/D-094-visual-proof-before.md keeps blob id 6ac8ce1fcecf1d5998f1116bac8267c7f8f9074f at the stamping head; the six rows' `text` (combined hash 90e9a5e4...) and their M0-T194 binding are unchanged; D-094 requirements_content_digest_sha256 stays bae4d0cd...; the six before-set files I spot-cited keep their manifest sha256.
 - Broad disjoint-peer tolerance: later commits may touch any other file — other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, ledger state — plus this task's own acceptance records (verification.json M0-T194 row, gate records, task state transitions) and a merge of the main line that changes none of the predicate's files.
 - This predicate already holds at the current live head 5a8228c1 (manifest blob, six-row text hash, binding and content digest all unchanged there), so my PASS may be stamped at a later head without a new review.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - S5 live-preview running-state at capture time: ephemeral and past, and I am forbidden to touch ports 3000/3001/8000. The manifest records "RUNNING (revision b47041611...)" before and after; I accept it as a record, as the G3 reviewer did, not re-verifiable now.
 - By-eye readability of all 115 images: I reproduced structural evidence for every file (115/115 sha256, 1:1 correspondence, PDF page count, PNG dimensions) and visually confirmed four images (page-1, page-8, w390 viewport, w1440 report-preview); per-image visual readability of every strip/page was the G3 visual-quality-reviewer's pass, which I relied on for the remainder.
 - CI at the frozen head 72fe33cf itself shows the CI workflow "cancelled" (superseded by the next branch push, a benign signature) with context-budget and secret-scan green; full CI green at the accept head is the orchestrator's R639 step, outside my six rows, and I did not re-run any job.
 - I verified B4 by a direct frozen-head scan of all directive requirements rather than the live-disk registry call, because the worktree HEAD had advanced off the frozen head; the scan is the semantic equivalent of evaluate_task_refs.

END-OF-REPORT
```
