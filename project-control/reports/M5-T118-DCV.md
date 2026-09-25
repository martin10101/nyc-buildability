# M5-T118 — directive-compliance verification (directive-compliance-verifier "dcv-t118", read-only)

> Transmission history: started at 3be7c22f (HEAD advanced to b1c43167 during the review through a disjoint
> peer accept seam; the ten T118 blobs and identity 47a46803 stayed byte-stable), delivered as five SendMessage
> parts (1..5) ending with END-OF-REPORT; no truncation (parts 2-5 were each queued twice, byte-identical; the
> first copy of each is joined). Joined verbatim by the orchestrator (transport wrapper tags removed only).
> Part 1 carries the blob-level restamp predicate with broad disjoint-peer tolerance.

---

M5-T118 DCV — restamp pre-authorization (UP FRONT), part 1 of report to follow.

Live HEAD at start: 3be7c22f. Frozen identity content_manifest_sha256 47a46803 (report + G1..G5 stamps all agree). I verified all 10 allowed-path blobs at HEAD match your claim exactly.

BLOB-LEVEL RESTAMP PREDICATE — my forthcoming PASS holds, and you may restamp my verification rows to any later HEAD WITHOUT re-review, so long as ALL of these blobs are byte-identical at the restamp target:
  sheet_reader.py 277161a5
  sheet_inline_image.py 0e4321da
  sheet_interpreter.py c570b6c0
  sheet_primitives.py 2bd28761
  sheet_objects.py 6be11292
  test_sheet_p3_features.py 092027b3
  test_sheet_reader.py 4da538f7
  test_sheet_reader_split_equivalence.py bb448f98
  test_sheet_content_features.py bddceb42
  M5-T118-producer-report.md 1b023958
and the task's content_manifest_sha256 stays 47a46803.

DISJOINT-PEER TOLERANCE (broad): any disjoint peer activity does NOT void this verdict — other tasks' files/gates/material (incl. M5-T116, M5-T117, M5-T119 and any new packets); other directives' registry binds; the orchestrator appending my verification rows to the D-066/D-087 verification.json with digest resyncs + audit entries; DISCOVERY_BACKLOG rows and sweep lines; lifecycle-only packet/state.json changes. Only a change to one of the 10 blobs above (or the manifest) voids it.

Requirement-by-requirement evidence, findings, and the final verdict line follow in subsequent parts.

---

M5-T118 DCV — part 2 of report. Requirement rows (primary evidence I reproduced myself).

D-066-R001 (obligation; navigation block) — SATISFIED
- tasks/M5-T118.json inputs[13] (line 21) carries the CODE-GRAPH NAVIGATION BLOCK: graph regenerated (844 files / 18356 nodes / 7841 edges), names consumers (sheet-reader modules imported only in app/drawings + tests/drawings; pdf_object_streams.py imports sheet_objects.py) and instructs `python tools/code_graph/query.py --no-regen impact <path>` before sweeps, marked ADVISORY. G0 report line 28 corroborates regen at the seam. Minor nit (F2, non-blocking): the input labels it "wave-1 seam" while G0 says "this seam"; identical node/edge counts — a provenance-label nit, not a content miss.

D-087-R001 (obligation; use capacity, gated) — SATISFIED
- registry evaluate_task_refs(M5-T118): ok=true, applicable_ids == cited_ids == [D-066-R001, D-087-R001, D-087-R002, D-087-R005, D-087-R009], zero missing/invalid/unresolved. Contract/wave-3 seam e8d101d7 (git subject "D-089 wave-3 contract seam (seq 130): M5-T118") — G0 recorded there. Claim seam f2ada974 (git subject "M5-T118: G0 PASS at the contract seam e8d101d7, claimed (full worktree paths), progress 20"). Produced by an orchestrator-dispatched subagent concurrently with disjoint M5-T116/M5-T117; every state present, no gate skipped (G0..G5 all recorded).

D-087-R002 (prohibition; no interference / pairwise-disjoint) — SATISFIED
- G0 report disjointness table: all 19 active neighbors "none - EMPTY overlap". One worktree (task.worktree wt-m5t118). Material commit 992c47b1 `git show --name-status` = exactly 9 files, all inside allowed_paths, none forbidden; the 10th allowed path test_sheet_content_features.py is untouched → 9 of 10. G3 independently confirmed: "material commit 992c47b1 touches EXACTLY the 9 allowed paths; NO forbidden path" (peer M5-T116/M5-T117 files in the wider range are not M5-T118).

Continued in part 3 (R005, R009).

---

M5-T118 DCV — part 3.

D-087-R005 (authorization; PDF blueprint reading, C-track honesty) — SATISFIED
- Source (three features): sheet_reader.py:146-153 per-page vs per-document budget constants — MAX_CONTENT_OPERATORS 200k / MAX_PATH_POINTS 500k per PAGE, MAX_DOCUMENT_OPERATORS 20M / MAX_DOCUMENT_PATH_POINTS 50M per DOCUMENT — matching the report table; sheet_interpreter.py:75 `_SKIP_SHADING=frozenset({"sh"})` applied at :429 (skip + count, never refuse); :435→:638 `_op_bi`→:644 `skip_inline_image`; sheet_inline_image.py:105 `skip_inline_image(...) -> InlineImageSpan | SheetRefusal`, "never decodes samples", ambiguity→typed refusal.
- Honesty (reproduced): G4 (qa-engineer) INDEPENDENTLY downloaded all six real PDFs in-memory via urllib, sha256-pinned to docs/research/architect-drawing-corpus-2026-09.md, fed to read_sheet, and reproduced the producer table byte-for-byte — items 1/3/4 READ (88pp / 14pp w/4 sh / 8pp scan+OCR w/3 inline), item 2 refuses "'l' with no current point", items 5-6 scan-only. "3 of 6 read fully" independently confirmed; item 4 disclosed as OCR/raster (G4 A2). Material commit carries no corpus bytes (9 code/test/report files only).
- F1 (advisory, non-blocking): G1 FINDING A — an inline image carrying a /DP DecodeParms dictionary is fail-safe REFUSED, not skipped (no regression: all inline images refused pre-M5-T118; not present in the real corpus). Typed refusal, never wrong geometry; "any ambiguity = typed refusal" is the packet's own contract. Does not undercut R005; recommend the orchestrator log it as a disclosed follow-up.

D-087-R009 (prohibition; unchanged boundaries) — SATISFIED
- Zero new deps: sheet_inline_image.py imports only __future__, dataclasses, app.documents.extraction.pdf_lexer, app.drawings.sheet_objects/primitives (grep) — no third-party; no requirements.txt/.in in the material (name-status).
- Forbidden paths byte-identical f2ada974→HEAD (git diff --stat empty): pdf_object_streams.py, test_pdf_object_streams.py, sheet_marked_content.py, app/documents/.
- Modularity: sheet_interpreter.py = 748 lines (wc -l) < 750; sheet_inline_image.py 340.
- Unwired: no app/api, app/main.py, or route file in the material; G5 grep-confirmed no route/main import of read_sheet; decoded per-document ceiling unchanged 128 MiB. Raised doc ceilings are a disclosed design choice with the future route's duties recorded (G5 L1; producer OPEN-Q2; DB-076 d). PR #241 OPEN/unmerged.

Continued in part 4 (identity, gates, sweep, verdict).

---

M5-T118 DCV — part 4.

FROZEN IDENTITY (reproduced) — `project_control._task_git_identity(dr, task)` at the live HEAD returns 47a4680373c6691e6959754e9867e47c401c5f17a7e52af5a1482a78688da477, ERR None (working tree clean for the scope). That value equals:
- reports/M5-T118.json content_manifest_sha256 (47a46803…),
- and the content_manifest_sha256 stamped on G1, G2, G3, G4, G5 (all five equal 47a46803…).
Gate reviewed_sha 2fdca967 is a linear ancestor of HEAD; I sampled its blobs for producer-report.md, sheet_inline_image.py, sheet_interpreter.py, sheet_reader.py and each equals the HEAD blob. All 10 allowed-path blobs at HEAD match my part-1 predicate list exactly. Frozen identity intact.

GATES — all six required gates PASS, each by an identity that is NOT the producer (producer = backend-engineer):
- G0 PASS — orchestrator, administrative, reviewed_sha e8d101d7 (contract seam), manifest a1425c02 (pre-material, expected for an administrative readiness gate).
- G1 PASS — data-contract-verifier "g1-t118": web-verified ISO 32000-1 §8.9.7/§8.7.4.2 citations, empirically confirmed the ID+first-sample-byte handling; BLOCKING none.
- G2 PASS — orchestrator, role self_check (the CLI bars the producer's own name; records the 9-file cherry-pick, blobs match HEAD).
- G3 PASS — code-reviewer "cr-t118": verified scope, budgets no-bypass, golden revisions scoped, re-ran ruff/modularity/272 tests; BLOCKING none.
- G4 PASS — qa-engineer "qa-t118": 15/15 own mutants + the independent real-corpus reproduction above; BLOCKING none.
- G5 PASS — security-reviewer "sec-t118": bounded parser, overflow pre-emption, desync protection verified; 0 Critical/High/Blocking-Medium.
G1/G3/G4/G5 manifests all 47a46803… at reviewed_sha 2fdca967. Reviewer advisories (G1 A-C, G3 A1-A2, G4 A1-A2, G5 L1-L2) are all fail-safe / disclosed / non-blocking; none undercuts a cited requirement.

Continued in part 5 (harness, sweep, HEAD movement, verdict).

---

M5-T118 DCV — part 5 (final).

HARNESS (reproduced) — I re-ran `tests/drawings` via the orchestrator shim from services/api: 272 passed in 7.27s (matches the harvest; the unrelated DXF timing test did not trip this run). Full local `validate_directive_compliance.py --check` DELIBERATELY SKIPPED, and I say so: (a) evaluate_task_refs returns ok=true — the registry loads and binds M5-T118 correctly at the live HEAD; (b) the pushed head ca007dcf (contains M5-T118 material 992c47b1/a120220e + its registry binds) shows the "CI" control-plane job green (run 36107082334, plus secret-scan + context-budget green); (c) concurrent accepts are actively moving HEAD, so a 12-min run's exit code would be unreliable (transient-c14) — registry integrity is CI's authority here. Harvest head not yet pushed (rely on local evidence, as you flagged).

PROHIBITED-ACTION SWEEP — clean:
- Not accepted: task status awaiting_gate; state.json accepted_tasks excludes M5-T118.
- No verification row yet: grep of D-087 and D-066 verification.json = 0 M5-T118 rows.
- Not on main: material 992c47b1 is not an ancestor of origin/main.
- PR #241 untouched: OPEN, unmerged, headRef task/M5-T002-scenario-endpoint (a different task).
- No open blocker names M5-T118.

HEAD MOVEMENT — HEAD advanced 3be7c22f → b1c43167 ("Accept seam: M5-T117 ACCEPTED (301 accepted)") during my review. That peer commit touches only docs/DISCOVERY_BACKLOG.md, the D-066/D-087 verification.json (M5-T117 rows), M5-T117-DCV.md, state.json, M5-T117.json; `git diff --stat 3be7c22f HEAD` over M5-T118's 10 allowed paths is EMPTY. 3be7c22f is a linear ancestor. Fully within my part-1 disjoint-peer tolerance; verdict unaffected. My blob-level restamp predicate (part 1) stands at b1c43167 and any later head where the 10 blobs + manifest 47a46803 hold.

FINDINGS: F1 (advisory) G1 /DP-dict inline-image fail-safe refusal — disclose as follow-up; F2 (advisory) the "wave-1 vs this seam" graph-regen label nit. Neither blocks. No requirement is VIOLATED or UNVERIFIABLE.

M5-T118 DCV VERDICT: PASS 5/5
END-OF-REPORT
