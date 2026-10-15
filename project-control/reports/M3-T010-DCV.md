# M3-T010 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `087670a963543946c28c42c9ad970805f766ba66` (branch `task/wave26-envelope-constraints`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R102, R104.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The sole residual item is advisory A2 (inapplicable use-allowance-glyph boilerplate still present in tables[*].header_structure of zr-23-12 and zr-23-371); it asserts no symbol meaning, changes no captured value/excerpt/digest/legend/cell, is already carried as a non-blocking advisory for a later tagged note cleanup, and does not block acceptance.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T08:35:33Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M3-T010 (directive D-094, 2 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is not a human or professional/legal review. I produced none of this work or its records; I re-derived every item below from primary evidence (the owner's words in the directive source, the task files at the frozen head, git objects, the registry tooling, and the recorded CI run), treating the producer report, evidence map, review record and gate records as claims to reproduce.

(1) HEAD VERIFIED
 - Frozen head 087670a963543946c28c42c9ad970805f766ba66 on branch task/wave26-envelope-constraints in /root/project/w-wave20; I read everything through `git show 087670a9:<path>` plumbing.
 - The live branch HEAD has since advanced to 307c8af2 (peer wave-26 tasks M5-T170/182/183/184); this does not touch my pinned reads.
 - Ancestry confirmed: material fd48fbc0 -> reviewed/submit 3170556f -> frozen 087670a9; corrections a6da66bd and 48d6587b are ancestors of both 3170556f and 087670a9.
 - The 45 allowed-path files are byte-identical between the reviewed head 3170556f and the frozen head 087670a9 (0 files differ), so the recorded gates cover the exact frozen content.

(2) ROWS

ROW D-094-R102 — PASS (this task's share)
 - All 20 captures verified at the frozen head: snapshot_schema == zr_section_snapshot/v1, content_digest_sha256 == sha256(verbatim_excerpt), snapshot_id == filename, extraction_status extracted_draft, source.raw_html_verified false, and an ADR-007 not-professionally-reviewed label present on all 20.
 - Each docs/research/zr-snapshots/v1 file is byte-identical (LF-normalized) to its services/api/app/_zr_snapshots/v1 bundled copy (20/20); 18 section captures pin both raw_html_sha256 and raw_pdf_sha256 (cross_check result "match", 25-24 correctly "no_own_body"), and the two 12-10 terms pin HTML with the disclosed 504/403 "unavailable_documented_fallback".
 - The library stale-state corrections are applied: options-sections.md line ~155 now reads 66-11 'mass transit station'; benchmark-r6b-sections.json is valid JSON with 32-131 re-pointed to option 6/7 and the C2-2 retail permission re-attributed to 32-161; option-06-07 / option-02-03 capture-state cells flipped NOT CAPTURED -> the captured snapshot ids with no reading or value changed; the index legitimately references none of the 20 new sections (119 entries, 0 overlap), so adding no new index rows was correct.
 - Stays open: R102 as a whole (the library lane — full cross-reference closure, the complete handles/does-not list, the official-guidance pitfall list, and the still-owed captures the producer report names: 22-131..135, 33-261/262, 23-154, 77-xx, 33-27/28/30, CF parking, 74-902/903) continues in later tasks, and no rule yet cites these captures (documents only).

ROW D-094-R104 — PASS (this task's share)
 - The task ran as a single documents-only producer (packet producer_agent official-source-researcher); its reviewer_agents (data-contract-verifier, directive-compliance-verifier) are read-only, so it added one builder, not a swarm.
 - Its 45 allowed_paths have zero intersection with every in-flight wave-26 task at the frozen head (M5-T170 89 paths, M5-T182 5, M5-T183 5, M5-T184 19, M5-T175 15 — all 0 shared), so "never sharing files" holds for this task.
 - The section list was fed by read-only research helpers (the sealed option readers and the comparer of session 2026-10-15a) per the packet inputs; capture reads and research, consistent with the "extra helpers only read and research" authorization.
 - Stays open: the session-wide concurrency ceiling (at most 8 helpers / at most 3 building at once) is a session-level posture recorded in session notes/dispatch records, not fully reconstructable from this task's committed artifacts; this task's own contribution to that ceiling is compliant.

(3) BINDING B1–B5
 - B1 PASS: contract commit 1d6b7c90 appended only "M3-T010" to the applicability.task_ids of R102 and R104 (plus the top-level updated_at); no requirement row text changed.
 - B2 PASS: at the frozen head sha256_text_artifact(requirements.json) = ee63ca8f516de341209eee44eabb7d99c4143fc3d86ab65050b9206a5d39f7b7 == manifest requirements_content_digest_sha256; id digest f56cd5d6e63ef8071817ba8189bd1693b9d5575b6ed7eb70f0bbf057fa44dd6d == manifest requirements_id_digest_sha256; 166 rows, R102/R104 both locked.
 - B3 PASS: verification.json has exactly one M3-T010 row, applicable_requirement_ids [D-094-R102, D-094-R104], both state "pending", producer official-source-researcher, verifier "" (empty) — awaiting this verdict.
 - B4 PASS: applying the registry's conjunction semantics, the packet's cited set {R102, R104} equals the applicable set; no unresolved applicability; evaluate_task_refs would return ok.
 - B5 PASS: scanning all 92 active directives' requirements at the frozen head, exactly D-094-R102 and D-094-R104 are applicable to M3-T010 — nothing else applies uncited; `python3 tools/validate_directive_compliance.py --check` exited 0 (settled head 307c8af2).
 - Gates PASS: G0 PASS (orchestrator, reviewed_sha 1d6b7c90), G1 PASS (data-contract-verifier, 3170556f), G2 PASS (orchestrator self_check, 3170556f); G1 and G2 share content_manifest_sha256 36bd5bf7..., i.e. one content identity; CI run 38704399016 at headSha 3170556f completed success, 21/21 jobs.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review provided the blob-level predicate holds: the task's 45 allowed-path files keep their frozen-head blob ids (combined tree digest 22e1456a395b8876411b37f878df962340c0e6705cc4d2db99d59103486c571a), and the text of D-094-R102/R104 and their applicability.task_ids containing M3-T010 are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits MAY touch any other file — other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports, directive bindings of other tasks, new rows appended to D-094, and ledger state — and MAY include this task's own acceptance records (verification.json M3-T010 row, a G3/accept record) and a merge of the main line that changes none of the predicate's files. Any such change does not void this verdict.

(5) REQUIRED CORRECTIONS
 - None. The sole residual item is advisory A2 (inapplicable use-allowance-glyph boilerplate still present in tables[*].header_structure of zr-23-12 and zr-23-371); it asserts no symbol meaning, changes no captured value/excerpt/digest/legend/cell, is already carried as a non-blocking advisory for a later tagged note cleanup, and does not block acceptance.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Live correspondence of each raw_html_sha256 to the official NYC DCP portal bytes: I am read-only with no network and the brief forbids browser/server use, so I verified internal integrity (digest==excerpt, docs==bundle byte-identity, schema, labels, pinning) but rely on the G1 reviewer's recorded live re-fetch (all 20 byte-identical, 12 by G1 + 7 by precheck) as a claim I could not re-reproduce.
 - Print/PDF list-label fidelity (pdftotext item-by-item against the official print): G1 reproduced this; I did not re-run it (no PDFs/network).
 - The session-wide helper/builder count for R104 (<=8 / <=3 at once): session-level evidence outside this task's committed artifacts.
 - I did not run tools/test_directive_compliance.py or the full api suite (forbidden by the brief); I relied on CI run 38704399016 (21/21 green at the reviewed head), validate_directive_compliance.py --check (exit 0), and the producer/G1 bundle + law-links runs (28 passed under the lock) which I could not execute myself read-only.

END-OF-REPORT
```
