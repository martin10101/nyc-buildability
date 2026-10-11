# M5-T159 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `2ca8069648691ec2965581e64b7168cdd28b73a7` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-090, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R584, R027.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 06:23 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T159 (directives D-094 and D-090, 2 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only, automated check, NOT a human or professional/legal review. I produced none of this work. I re-derived each item from primary evidence (git objects, the law captures, the real report builder, the registry helpers, the two permitted validators). Reports/maps/gate records were treated as claims.

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` = `2ca8069648691ec2965581e64b7168cdd28b73a7` on `task/wave23-density-zoning-lot`; every file below was read at that head through git plumbing.
 - Gate records G2/G3/G4 cite reviewed_sha `ced5bd73` (one commit earlier, the submit commit); 2ca80696 is the gate-record/ledger commit. The five allowed-path files carry IDENTICAL blob ids across 0330d598 (material) → ced5bd73 (reviewed) → 2ca80696 (frozen): law_links.py 535f15b2e0, page_evidence.py 1cd2ba8e33, sources.py 23e5f2b9db, test_report_law_links.py 186e265660, producer-report 23ee17b8ac — so the gates validly cover the frozen head.

(2) ROWS

ROW D-090-R584 — PASS (this task's share)
 - Hold: keep activation restrictions — all production switches stay off, no hidden feature turned on by the emitting piece or display. `git diff 9e107bf3 2ca80696` over the three production files, grepped for flag/feature/enable/disable/switch/setting/env/getenv/os.environ/deploy/activ/config/settings, returns NOTHING.
 - page_evidence.py's only behavioral change is deleting the hard-coded homepage constant `_LAW_URL` and calling `law_links.section_url(section)` with a plain-text fallback; sources.py only adds the `zr_section_page_number` helper; law_links.py is a new pure-resolution module using the existing read-only SnapshotStore. No feature is gated, toggled, or defaulted-on.
 - The two task material commits (f48b3d97, 0330d598) touch only the 5 allowed-path files; forbidden paths (readers.py, test_report_pages.py, rulesets/, render.yaml, .github/, apps/web/package*.json, .claude/) are untouched.
 - Nothing stays open for this task: the HTML-only link change introduces no activation change, so the hold is fully honored here (the hold itself persists directive-wide for other pieces).

ROW D-094-R027 — PASS (this task's share: the HTML law links only)
 - Obligation: every law link resolves to its exact current section (not the homepage); affected results connect to review-register entries; destinations checked in the exported PDF. I rendered the evidence page myself from `packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` through the real `build_report_html`: 12 law hrefs, every one an exact section-page URL (article-ii/chapter-3/23-22, /23-52, /23-432) equal to the captures' own `source.request_url`; the homepage is ABSENT from the href set.
 - I opened the captures directly: zr-23-22/zr-23-52/zr-23-432 carry official `article/chapter/section` request_urls and zr-12-10 carries `/article-i/chapter-2/12-10`; zr-11-25 carries only `https://zr.planning.nyc.gov/entityprint/pdf/node/18433` (wrong host), so 11-25 prints as plain text — I confirmed in the rendered HTML that label `11-25` appears with no anchor, and 23-52(b) keeps its sub-paragraph label while linking to section page 23-52. S3 fail-closed behavior reproduced.
 - Focused suite `tests/drawings/report/test_report_law_links.py` = 22 passed at the frozen head (lanes venv). The oracle is fixture-derived and independent of the module under test (`_capture_section_url` scans the capture files directly); this is the G3/G4 fixture-derived rework. G3 and G4 each ran their own homepage/query-rejection mutations and the guards failed as required.
 - STAYS OPEN for report v3 (correctly deferred by the packet risks + evidence-map, not a defect here): the exported-PDF link-destination harness (the row's required_harness/required_evidence, link-check record R060) and connecting affected results to their existing review-register entries. This task delivers the HTML law links only; the PDF-destination check and register linkage are unverified and owed.

(3) BINDING B1–B5
 - B1 PASS: contract commit 4c1cbacd appended "M5-T159" to `applicability.task_ids` of both rows; the only other change in each requirements.json is the file-header `updated_at`; no row `text` changed.
 - B2 PASS: `directive_registry.sha256_text_artifact(requirements.json)` equals each manifest's `requirements_content_digest_sha256` — D-094 `3c44684429763b99…fe4e05e8`, D-090 `160eac6fe5826a20…c944a070`.
 - B3 PASS: each `verification.json` has exactly one M5-T159 row — D-094 with `["D-094-R027"]`, D-090 with `["D-090-R584"]` — state `pending`, `verifier` "" (empty), producer backend-engineer, schema v2.
 - B4 PASS: `evaluate_task_refs(M5-T159.json)` → ok=True, applicable_ids == cited_ids == ['D-090-R584','D-094-R027'], missing/invalid/unresolved all empty.
 - B5 PASS: no uncited applicable requirement; `python3 tools/validate_directive_compliance.py --check` exit code 0 (direct). Packet `required_gates` = G0,G2,G3,G4 and all are PASS: G0 at contract 4c1cbacd; G2 (orchestrator self-check), G3 (code-reviewer), G4 (qa-engineer) all at content_manifest 0edb5fb5 / reviewed_sha ced5bd73 — one content identity. NOTE: the packet does NOT require G1 for this task (G1 belonged to sibling M5-T157); the brief's "G1/G2/G3/G4" wording is looser than the packet — not a defect, the required set is fully satisfied.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT re-review provided the blob-level predicate holds: the five allowed-path files keep their frozen-head blob ids [law_links.py 535f15b2e0, page_evidence.py 1cd2ba8e33, sources.py 23e5f2b9db, test_report_law_links.py 186e265660, M5-T159-producer-report.md 23ee17b8ac] AND both rows' text and their M5-T159 applicability binding are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE granted: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/ including other evidence records, their packets, gates, reports, other tasks' directive bindings, ledger state), plus this task's own acceptance records, and a main-line merge that changes none of the predicate's files — none of these void this verdict.

(5) REQUIRED CORRECTIONS
 - None.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - Live reachability/currency of the recorded ZR URLs — no network; by design the committed captures are the authority and I verified every href equals a capture's request_url.
 - The exported-PDF link-destination check (R060) and review-register linkage of affected results — not implemented in this task (deferred to report v3), therefore nothing to verify now; correctly left open and owed.
 - Byte-identity of `docs/research/zr-snapshots/v1/` vs the app copy `services/api/app/_zr_snapshots/v1/` — the loader (and the code) use the app copy, which I verified directly; I did not diff the docs mirror.
 - Full api/web suites and CI at the head — forbidden to me and CI's responsibility; I ran only the focused law-links suite (22 passed) plus the two permitted validators (directive-compliance --check exit 0; research_record_check --check exit 0, 6 records structurally valid).
END-OF-REPORT
```
