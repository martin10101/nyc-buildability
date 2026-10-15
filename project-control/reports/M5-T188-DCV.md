# M5-T188 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `75ae32ce5958d2b16bb8a57f2fb684f5241d709e` (branch `task/wave27-comparison-appendix`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R015, R017, R037, R053, R116.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None that block the five rows' this-task verdicts; all five shares are satisfied by reproducible primary evidence and every binding/gate check passes. - Advisory for the orchestrator (does not change a row verdict): the packet names visual-quality-reviewer in reviewer_agents and assigns the S9 before/after visual artifact and R116's "checked by eye at print size" harness to it, but the reviews record contains no visual-quality-reviewer return — the single G3 gate was recorded PASS by code-reviewer (who did reproduce the before/after SVGs at the SVG level, and G4 reproduced the page-4 PDF diff). Before accept, confirm whether a visual-quality-reviewer by-eye pass is still required, or record that the SVG/PDF-level reproduction satisfies it for a change not visible on the current benchmark.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T12:06:12Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T188 (directive D-094, 5 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier), read-only. This is an independent software/control-plane verification, not a human or professional/legal review. I produced none of the work or records under review; every report, map, gate record and the brief itself I treated as an unverified claim and re-derived from primary evidence (the owner's words in the directive sources, the task's files, git objects, the gate/registry records, CI).

(1) HEAD VERIFIED
 - The frozen head is 75ae32ce5958d2b16bb8a57f2fb684f5241d709e on branch task/wave27-comparison-appendix in /root/project/w-wave20; I read every file through git plumbing (git show 75ae32ce:<path>), not the working tree.
 - The worktree HEAD is actually c8b0e434 (one commit past the frozen head: "Rule-check reports M3-T012/M3-T011"), a disjoint peer that touches no M5-T188 file and no D-094 registry file (git diff 75ae32ce c8b0e434 on the directive folder and the 8 task files is empty).
 - 75ae32ce is the submit commit; its parents chain monotonically: round-2 material 8302fc2e is an ancestor of the gate-record head defba522, which is an ancestor of 75ae32ce.
 - The task's 5 production + 3 test files are byte-identical between the gate head defba522 and 75ae32ce (git diff --stat empty); only control-plane bookkeeping (gates, reports, state, task json) changed after the gates were recorded.

(2) ROWS (this task's share, numeric order)

ROW D-094-R015 — PASS
 - Source source-001.md line 220 is quoted verbatim in requirements.json (dedicated constraints diagram, subject+neighbours dominant, dimensions anchored to edges); no row text was altered by this task.
 - This task's share is the close-up legibility polish: constraint_overlay.py (blob d40363ba) makes the established LINE label's first candidate a perpendicular unit-normal offset off the line, proven by test_s1 (anchor lies OUTSIDE the placed box; a drawn polyline vertex stays outside every box).
 - The frame grows only when a constraint is ACTUALLY drawn: site_context_plan.py passes overlay_present=overlay_was_drawn(sheet); test_s3 (established line → height>470, legend row fits) and test_s4 / test_s4_a (no overlay and benchmark-shape not-established list both stay 470) are the red/green guards.
 - Stays open: the full obligation (the diagram's overall subject/neighbour dominance and all edge-anchored dimensions on the live benchmark) is the shared share of M5-T166 and M5-T175; and the A1 effect is only demonstrable on a constructed established-line case because the benchmark establishes no line (per the evidence map's own known_limits).

ROW D-094-R017 — PASS
 - Source source-001.md line 222 is quoted verbatim (yard/setback areas drawn only when geometry and basis are established); classification prohibition; text unchanged by this task.
 - This task's share strengthens the prohibition at the frame level: the round-1 bug grew the frame for ANY carried constraint_lines block (the benchmark's four not_established/not_known items); the F1 fix ties frame growth to a drawn established constraint via overlay_was_drawn.
 - Reproduced from the diff and tests: a not_established/not_known item hits `continue` (no draw, no kind registered), so test_s4_a asserts the benchmark-shape list keeps height 470 with no CONSTRAINT_STYLE_KINDS on the sheet; test_overlay_was_drawn pins empty→False, not-established→False, established→True.
 - Consistent with the settled reading short-block-rear-yard.json (no unconditional 'no rear yard'; conditions named). Stays open: the engine-wide established-gating for every other constraint kind is the share of M5-T164/T167/T170/T175; nothing of this task's own share stays open.

ROW D-094-R037 — PASS
 - Source source-001.md line 242 is quoted verbatim (no unconditional zero rear yard inferred from GIS; the corner-radius test is not the only exception); prohibition; text unchanged.
 - This task's share is confined to page-1 wording: page_decision_summary.py (blob a4a27fce) strips the leading row title only at a word boundary (char after the title is ':' , whitespace, or end), reproduced in the diff.
 - test_s6 (five states) proves 'Rear yard Rear yard …' still collapses to the conditional 'Rear yard is conditional under ZR 23-344 …' reading while a bare-prefix ('Rear yardage…') is NOT mis-stripped; the change is behaviour-identical on the benchmark and introduces no unconditional zero rear yard.
 - Consistent with the settled short-block-rear-yard.json ("the corner test of 23-344(a) is never worded as the only exception"). Stays open: the substantive rear-yard pathways (ZR 23-344(b) short-block / (c)(3) adjoining side line, diagram+conclusion together) are the share of M5-T163/T165/T176/T167, not this task.

ROW D-094-R053 — PASS
 - Source source-001.md line 258 is quoted verbatim (real source-based geometry, useful line weights, anchored dimensions, readable street/lot labels, north arrow, scale; illustrative geometry marked distinctly); obligation; text unchanged.
 - This task's share is label readability: close_frame_dimensions.py (blob e2f1adfe) excludes keys starting "mapped_street_width:" from the other-basis LOT band, so each street width reads once as "<n> ft mapped width" on its frontage and is not duplicated as a "map outline" chip.
 - test_s10 (three states) pins it: street-width facts present → only the lot fact drawn, no "100 ft, map outline"/"60 ft, map outline"; absent → lot band unchanged; a lot's OWN gis fact still reads "map outline". The G4 real-print page diff (reproduced independently) shows page 4's only change is the two duplicate chips removed, frontage "100/60 ft mapped width" kept, lot "10,387.99 sq ft, map outline" kept.
 - The widths 100 ft (Northern Blvd) / 60 ft (215 Place) and the lot areas 10,075 / ~10,388 sq ft match the settled overlay-reading.json and short-block-rear-yard.json facts. Stays open: the full obligation (line weights, north arrow, scale, all labels, illustrative-geometry marking across all drawings) is primarily the share of M0-T193/M5-T166/M5-T175.

ROW D-094-R116 — PASS
 - Source source-011-amendment.md quotes the owner verbatim ("Ok fix it", 9 chars, digest recorded) as a decision answering K1; the requirements.json reading (basis once under the drawing, every label beside its line on a white background, addresses off, lighter neighbours, checked by eye) is unchanged by this task; it depends on D-094-R115.
 - This task's share is the "every label beside, never on, its line, with a white background" piece for the constraint overlay line: the A1 perpendicular first candidate keeps halo=True (white box), proven beside-the-line by test_s1.
 - The other K1 elements (one basis note under the drawing, neighbour addresses off, lighter neighbours) are M5-T166's share; the evidence map states the existing beside-line/basis tests stay green, which is outside this task's edited files.
 - Stays open: the owner-facing by-eye check at print size and the beside-line demonstration for an actual constraint line are deferred because the benchmark establishes no line (RISK 1); and the remainder of K1 rides on M5-T166.

(3) BINDING B1–B5
 - B1 PASS: the contract commit b8a23afe appended exactly one "M5-T188" entry to the task_ids of all five rows (R015,R017,R037,R053,R116) and changed nothing else in requirements.json except updated_at; no row text was modified by this task.
 - B2 PASS: I recomputed directive_registry.sha256_text_artifact over requirements.json at the frozen head = 209ddf6b1a528283012f6fd60c9306305bd6c7d543f31d8c0f266cb59afe29e1, which equals manifest.requirements_content_digest_sha256.
 - B3 PASS: verification.json has exactly one M5-T188 task_verifications row (schema directive_verification/v2) with applicable_requirement_ids == the five ids, verifier "", reviewed_sha null, and all five requirement states "pending".
 - B4 PASS: reg.evaluate_task_refs on the packet returns ok=True, applicable_ids == cited_ids == the five ids, missing_ids=[], invalid_refs=[], unresolved=[].
 - B5 PASS: missing_ids=[] across the whole loaded registry (no uncited applicable requirement from any active directive); M5-T188 is in manifest.affected_tasks; the two material commits (3c95cae9, 8302fc2e) touch only allowed-path files (no neighbourhood_map/block_map/scenario/ or other forbidden peer). Gates: M5-T188-G0/G2/G3/G4/G5 all recorded result=PASS; G0 orchestrator at the scope-correction head 2e0600eb; G2 (orchestrator), G3 (code-reviewer), G4 (qa-engineer), G5 (security-reviewer) all at one content identity defba522; CI run 38729622697 at defba522 = 21/21 jobs success, and defba522's material files are byte-identical to the frozen head. The task is status awaiting_gate, not in accepted_tasks, and 75ae32ce is not on origin/main — nothing merged/accepted/dispatched/deployed/installed/purchased/closed.

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while the blob-level predicate holds: the packet's allowed-path files keep these exact blob ids at the stamping head — constraint_overlay.py d40363ba, context_scene.py 0e92520e, site_context_plan.py b3962a58, page_decision_summary.py a4a27fce, close_frame_dimensions.py e2f1adfe, test_constraint_overlay.py e5f58c74, test_site_context_close_frame.py fcb2f912, test_page_one_title_boundary.py 85ef5e8b — AND the five rows' text plus their M5-T188 binding are unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/; their packets, gates, reports, directive bindings of other tasks; new rows appended to D-094; ledger state), plus this task's own acceptance records (gates/reports/state/task json/evidence map/reviews/verification), plus a merge of the main line that changes none of the predicate's files. Any of these alone does not void the verdict.

(5) REQUIRED CORRECTIONS
 - None that block the five rows' this-task verdicts; all five shares are satisfied by reproducible primary evidence and every binding/gate check passes.
 - Advisory for the orchestrator (does not change a row verdict): the packet names visual-quality-reviewer in reviewer_agents and assigns the S9 before/after visual artifact and R116's "checked by eye at print size" harness to it, but the reviews record contains no visual-quality-reviewer return — the single G3 gate was recorded PASS by code-reviewer (who did reproduce the before/after SVGs at the SVG level, and G4 reproduced the page-4 PDF diff). Before accept, confirm whether a visual-quality-reviewer by-eye pass is still required, or record that the SVG/PDF-level reproduction satisfies it for a change not visible on the current benchmark.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run a by-eye visual review at print size and no visual-quality-reviewer return exists to verify; I am not a visual reviewer, and the A1/A2 overlay change is not visible on the benchmark (it establishes no constraint line), so its visual proof rests on the constructed close-frame case others rendered.
 - I did not run the full services/api pytest, web-e2e, tools/test_directive_compliance.py, or any server/port-bound print (all forbidden by the brief); I relied on CI run 38729622697 (21/21 success at defba522, the byte-identical gate head) for the full-suite and print evidence, and on the producers'/reviewers' reproductions of the real print, which I did not re-execute end-to-end.
 - I confirmed test ASSERTIONS by reading the three task test files at the frozen head and the mutation descriptions, but did not re-execute the pytest mutations myself (read-only; the brief forbids the heavy suites); the G3/G4/G5 returns report reproducing them.
 - I verified the registry/binding at the w-wave20 HEAD c8b0e434 after confirming its directive folder and the eight task files are byte-identical to the frozen head; the validate_directive_compliance.py --check I ran (exit 0, twice: primary checkout and w-wave20) reflects that identical registry state.
END-OF-REPORT
```
