# M4-T036 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `698de7ca4e7bfc8d87f9880e5809880b554091d3` (branch `task/wave8-captures-measurement-basis`, review copy `/root/project/rv-w6-b`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R291, R517, R526.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-08 06:03 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M4-T036 (directive D-090, three rows)
VERDICT: PASS
I am an AI agent (directive-compliance-verifier). This is an automated agent review, NOT a human or professional/legal review. Read-only; I produced none of this work or its records.

(1) HEAD VERIFIED
 - `git rev-parse HEAD` in /root/project/rv-w6-b = 698de7ca4e7bfc8d87f9880e5809880b554091d3, the frozen head.
 - `git diff --name-status 599f9b0c 698de7ca -- docs/research/zr-snapshots/v1` = 29 files, all "A"; none M/D/R among the 156 older captures.

(2) ROWS

ROW D-090-R291 — PASS (for this task's capture share; row stays open for the rest)
 - Row text (sequencing): "step 3: the R6B answers are checked: missing rules and conflicting inputs are resolved, and independently calculated examples are saved as files to test against."
 - This capture task's only share is adding source law-text files that feed later rule-resolution; it added 29 ZR captures as files under docs/research/zr-snapshots/v1 and saved none that resolve a rule or compute an example — `git diff` over services/api/app/rules, docs/reference-cases, docs/zoning-rule-review between claim head and frozen head is empty.
 - No capture or the report states what a text means for a lot (searched all 29 + report; the sole "is resolved" hit in zr-33-12 is a structural heading-only/intro note, not a rule verdict).
 - The substance of the row — checking the R6B answers, resolving conflicts, and saving independently calculated examples — is not done by a capture task and stays OPEN in the registry (row still applies to M4-T024..T035 and D-090-BOOTSTRAP).

ROW D-090-R517 — PASS (for this task's capture share; row stays open for the rest)
 - Row text (external_fact): each statement of law in the owner's message is checked at its official source before a record is changed because of it, and a difference is told to the owner first.
 - The task supplies the official source texts so statements can be checked: the producer report records the builder fetching all 29 pages (one HTTPS GET of the canonical HTML + the section's own print/PDF as a text cross-check), and the review record states the independent data-contract-verifier re-fetched 22 of the 29 official pages itself and compared word-for-word (the other 7 — 33-11, 33-12, 36-232, 36-24, 36-25, 25-22, 25-23 — from capture text only).
 - No record was changed because of these captures (rules/reference-cases/register unchanged, confirmed by diff), and I independently recomputed sha256(verbatim_excerpt)==content_digest_sha256 for all 29.
 - The full row — checking every statement of law in the message (shared-space, amenity base, the two energy routes, wall exclusion, R6B base/heights, dwelling-unit factors, bicycle, imagery, PDF behaviour) — exceeds a capture task and stays OPEN; I could not re-fetch live pages, so the capture-to-live-page correspondence rests on the reviewer's recorded 22-page re-fetch.

ROW D-090-R526 — PASS (not violated by this task; row stays open for the rest)
 - Row text (prohibition): no option is presented as feasible while parking/loading/bicycle applicability is unresolved; until then results say not yet checked; the report section may come later.
 - A capture task can only violate this by asserting feasibility/resolution; I searched all 29 captures and the report and found no sentence saying an option is feasible, needs/does not need parking, loading or bicycle spaces, or that a rule is resolved — the parking/loading/bicycle words present are official section titles and a table-content description ("a PRC column and NO loading requirement category column").
 - The task instead captures the provisions R526 needs read first (25-212, 25-22, 25-23, 36-231/232, 36-30, 73-432/433, 74-52, 75-31, 32-131/161) as source text only; every capture's notes repeat "no reading of the text for any lot".
 - The prohibition's live scope — the option comparison, the website display, and the report — is enforced by the computational/UI tasks and stays OPEN in the registry.

(3) BINDING B1–B5 — ALL CONFIRMED
 - B1: diff of D-090 requirements.json 39e7f2d2→698de7ca appends only "M4-T036" to R291/R517/R526 applicability.task_ids; each row's text byte-identical; no row text changed anywhere in the file (other task_id changes are M5-T135's and two new M5 rows R565/R566).
 - B2: tools/directive_registry.sha256_text_artifact(requirements.json) = 1f621ca2d076461fb5a9aef10cf63b052996b9bae71e15dd10e2faa149868bc1 == manifest.requirements_content_digest_sha256; manifest audit_log holds the 2026-10-08T03:57:04Z "applicability_bound" entry naming M4-T036→R291,R517,R526 with the digest resync and the provisional verification row, same commit.
 - B3: verification.json has exactly one M4-T036 row; applicable_requirement_ids = [R291,R517,R526]; each requirement state "pending"; verifier "".
 - B4: DirectiveRegistry().load().evaluate_task_refs(M4-T036 packet) → ok=True, applicable_ids==cited_ids==the three, missing/invalid/unresolved empty.
 - B5: scanning every directive's requirements.json, exactly three requirements (all D-090) carry M4-T036 in task_ids, all three cited, none uncited.
 - Gates: G0 PASS, G2 PASS, G3 PASS, G4 PASS. G2/G3/G4 all carry one content identity content_manifest_sha256=cbd2b57f1b9069e636927ecec6f14fb41ac4ed72a29072751699b3fd215384c9 (G3/G4 reviewed_sha f5dc4855).
 - Ledger-history truth: the first return (G3 FAIL / G4 PASS, both parts) was committed in 04300e0c (2026-10-08T05:33) into BOTH project-control/reports/M4-T036-G3G4.md (contains "G3: FAIL") and the task progress_log, BEFORE the correcting commit 7c601b30 (05:43) and its integration a6072e1e (05:45); 6526d902 is an ancestor of 7c601b30; the correcting commit touched only the 59 capture/report files (not the review record or log); all three returns (FAIL, addendum-corrected-to-PASS, delta confirmation) are kept verbatim in the record. The ledger tells it truly.
 - Harness: sync_zr_snapshots.py --check = 185 byte-identical, exit 0; pytest test_zr_snapshot_bundle.py + reference_cases = 78 passed, exit 0; validate_directive_compliance.py --check = exit 0 (no findings); test_project_control.py = 25 passed; test_directive_reminder.py = 12 passed. All 29 captures: digest reproduced (29/29), both retrieved_at earlier than first material commit 9663a523 (2026-10-08T04:43:13Z), copies byte-identical, correction note present; zr-36-233 carries both the retrieved_at correction note and the literal-"#"/U+200B disclosure note.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head without re-review while: every file under docs/research/zr-snapshots/v1 and services/api/app/_zr_snapshots/v1 and project-control/reports/M4-T036-producer-report.md keeps the exact blob id it has at 698de7ca; everything under docs/reference-cases, services/api/app/rules and docs/zoning-rule-review is unchanged; and the text of R291/R517/R526 and their binding to M4-T036 is unchanged.
 - Tolerated later commits: commits touching ONLY project-control/** and/or docs/DISCOVERY_BACKLOG.md; and a merge of the integration branch that changes none of the predicate's files. (Verified in-copy: a6072e1e→698de7ca leaves the allowed-path blobs identical and touches only project-control/.)

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The live correspondence of each capture to the official zoningresolution.planning.nyc.gov page (read-only, no web fetch): I reproduced content_digest_sha256 for all 29 but rely on the reviewer's recorded 22-of-29 re-fetch for the words-match-the-live-page claim; the 7 un-re-fetched pages (33-11, 33-12, 36-232, 36-24, 36-25, 25-22, 25-23) were checked from capture text only.
 - The per-session raw_html_sha256 / response_bytes pins (disclosed as non-reproducible due to Drupal form_build_id drift) were not reproduced.
 - tools/test_directive_compliance.py was not run (forbidden; hours-long); CI's control-plane job is its authority.
END-OF-REPORT
```
