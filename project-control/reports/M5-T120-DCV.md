# M5-T120 — directive-compliance verification (directive-compliance-verifier "dcv-t120", read-only)

> Transmission history: pinned at 506d2151 (the corrected identity 80c33f6d after the [ORCH-CORRECTED per M5-T120 G1]
> doc-only commit 793fed27; HEAD later advanced through disjoint peer seams - the M5-T124 contract and the M5-T123
> accept - with the eleven T120 blobs byte-stable), delivered as four SendMessage parts (1/4 carries the up-front
> restamp pre-authorization) ending with END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport
> wrapper tags removed only).

---

M5-T120 DCV (directive-compliance-verifier, READ-ONLY) — PART 1/4. Verdict in Part 4.

HEAD at start: `git rev-parse HEAD` = 506d2151eed3a1d4e97d6f286ed52fd05f4710b0. Method: read the two directive sources + amendment, requirements.json for D-087 and D-066, the packet, the six gate records + reports, the frozen submission, the material diffs, and the source; reproduced the offline harness, ruff, modularity, the digests, and CI myself. I did not re-fetch the real PDF corpus (network/out-of-tree, producer deleted the copies) — the corpus causal claim is judged on G4's independent reproduction + the in-tree code/tests I ran.

RESTAMP PRE-AUTHORIZATION (up front).
Blob-level predicate — I authorize restamping my rows to any later HEAD provided ALL of these git blobs at that HEAD are byte-identical to what I reviewed and the task identity is unchanged:
- sheet_path_state.py blob 64e5e088
- sheet_interpreter.py blob 04f2e39a
- sheet_inline_image.py blob 16bd1843
- sheet_primitives.py blob 8e16392a
- sheet_reader.py blob 84368ef7
- test_sheet_p4_features.py blob 7e6527a9
- test_sheet_p3_features.py blob 092027b3
- test_sheet_reader.py blob cfd0def1
- test_sheet_reader_split_equivalence.py blob 51197f59
- test_sheet_content_features.py blob bddceb42
- M5-T120-producer-report.md blob b134e064
- task content identity 80c33f6d (project_control._task_git_identity at HEAD).
All eleven confirmed at HEAD 506d2151 via git ls-tree; identity confirmed = 80c33f6d.

Disjoint-peer tolerance (broad): I tolerate, without re-review, any change outside those eleven blobs — other tasks' files/gates/material (M5-T122, M5-T123 in final checks; new packets e.g. M5-T124); other directives' registry binds; the orchestrator appending MY D-066/D-087 verification rows with digest resyncs + audit_log entries; DISCOVERY_BACKLOG rows and contract-seam sweep lines; lifecycle-only packet edits (status/progress/worktree). Any change to one of the eleven blobs, or identity != 80c33f6d, voids the carry and needs a fresh delta.

APPLICABILITY (mechanical). directive_registry.load_registry().evaluate_task_refs(M5-T120) = ok:true, applicable == cited == {D-066-R001, D-087-R001, D-087-R002, D-087-R005, D-087-R009}, missing:[], invalid:[]. I also scanned every other requirement's applicability.task_ids: none other lists M5-T120 (R003/R004/R006/R007/R008/R010/R011/R012 and D-066-R002/R003/R004 exclude it). So five applicable requirements, all cited — nothing missing, nothing invented.

Continues in Part 2 (frozen identity, gates, harness, CI, prohibited-action sweep). END-OF-PART-1

---

M5-T120 DCV — PART 2/4 (frozen identity, gates, harness reproduced, CI, prohibited-action sweep).

FROZEN IDENTITY. project_control._task_git_identity(dr, task) at HEAD = 80c33f6deaea51920c99496de59c0c959839bca0587aa4e607222c4976542d23 (resolved_sha 506d2151, error None). This EQUALS reports/M5-T120.json content_manifest_sha256 (80c33f6d) AND the content_manifest_sha256 stamp on every material gate G1/G2/G3/G4/G5. Match confirmed.

GATES — all six present and PASS; independent reviewers ≠ producer (producer = backend-engineer):
- G0 PASS, orchestrator (administrative readiness), reviewed_sha 8b67ac41.
- G1 PASS, data-contract-verifier, manifest 80c33f6d.
- G2 PASS, orchestrator (producer self-check; CLI rejects the producer's own name — correct).
- G3 PASS, code-reviewer, manifest 80c33f6d.
- G4 PASS, qa-engineer, manifest 80c33f6d.
- G5 PASS, security-reviewer, manifest 80c33f6d.
Each of G1/G3/G4/G5 carries a DELTA attestation confirming the [ORCH-CORRECTED per M5-T120 G1] commit is doc-only and the PASS carries to identity 80c33f6d. None of the four independent reviewers is backend-engineer.

HARNESS — reproduced by me (not trusted from the report):
- Drawings suite via the 3.11 shim from services/api: 322 passed in 11.68s (includes split-equivalence goldens + the new p4 tests). Independent of the producer's 289 count; matches G3/G4's 322.
- `python -m ruff check .` (cwd services/api) = All checks passed, exit 0.
- `python tools/modularity_check.py --check` = exit 0; sheet_interpreter.py (577), sheet_path_state.py (250), sheet_inline_image.py (445) NOT flagged (interpreter under the 600 warn line).
- test_directive_reminder.py = 12 tests OK, exit 0.
- validate_directive_compliance.py --check: SKIPPED per your allowance — its digest rows are settled directly (Part 3); the CI control-plane job (which runs it) is green below.
- test_project_control.py: my local run was still executing at report time (grown-registry slowness); superseded by the CI control-plane job (runs it at 3.12, the authority), green below.

CI — I read it myself. Run 36118660330 at the M5-T124 seam 724248f2, which is a descendant of HEAD 506d2151 (git merge-base --is-ancestor confirmed) and carries T120 identity 80c33f6d (the eleven blobs are byte-stable 858989c1..HEAD): api (ruff + pytest) ✓ 1m19s, control-plane (ADR-005) ✓ 4m17s, modularity ✓, code-graph ✓, plus every other job ✓. So the corrected head IS through CI green (the earlier "queued behind an in-flight run" note is now resolved).

PROHIBITED-ACTION SWEEP — all clean: no task_verifications row keyed to M5-T120 (not accepted/verified; the single "M5-T120" string in D-087 verification.json is inside ANOTHER task's evidence noting T120's reader modules as its forbidden path); no open blocker names M5-T120; branch candidate/D-024-mrl-option-b (not main); PR #241 not implicated (own diff is drawings + report only); status awaiting_gate.

Continues in Part 3 (requirement rows R001/R002/R009/R066). END-OF-PART-2

---

M5-T120 DCV — PART 3/4 (requirement rows; each judged on primary evidence I located).

D-066-R001 (graph nav block + query.py instruction) — SATISFIED. Primary evidence: tasks/M5-T120.json inputs[20] carries the "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED at the wave-1 seam, 844 files / 18356 nodes / 7841 edges)" naming the sheet-reader consumers, the forbidden neighbors, and the `python tools/code_graph/query.py --no-regen impact <path>` instruction with "graph ADVISORY — verify every material conclusion in actual source." reports/M5-T120-G0.md:28-29 confirms regeneration at the seam. Present and correct.

D-087-R001 (use capacity; every unit a contracted/claimed/gated packet, no state or gate skipped) — SATISFIED. Primary evidence: M5-T120 is a full ledger packet — required_gates G0,G1,G2,G3,G4,G5 (all PASS, Part 2), producer backend-engineer, its own worktree wt-m5t120, run as an orchestrator-dispatched subagent producer (inputs[0]; G0 report Authority). It is one of the ~dozen concurrent M5-T1xx builders. Lifecycle order is intact: claimed(20)→in_progress(90)→rework(90)→in_progress(90)→submit(awaiting_gate) (progress_log + G2 history), i.e. the awaiting_gate→rework→in_progress→submit re-freeze — no state or gate skipped.

D-087-R002 (no interference; pairwise-disjoint allowed_paths, isolated worktree) — SATISFIED. Primary evidence: I computed set intersections — M5-T120 allowed_paths ∩ M5-T121 = ∅, ∩ M5-T122 = ∅, ∩ M5-T123 = ∅ (all DISJOINT). reports/M5-T120-G0.md:31-51 pairwise table shows EMPTY overlap for every active neighbor. One isolated worktree (tasks/M5-T120.json "worktree": wt-m5t120). Independent corroboration: the disjoint peer commits in 0c638f88..HEAD touch apps/web/** and services/api/app/api/v1/{dxf_import,export,scene}_api.py — entirely outside T120's app/drawings scope.

D-087-R009 (unchanged boundaries: zero new deps, unwired, forbidden files untouched, one golden substitution, max-envelope unmounted, PR #241, gates) — SATISFIED. Primary evidence: M5-T120's OWN two commits — material 5ae5700e (9 files) and correction 793fed27 (3 files) — touch ONLY allowed_paths (git show --name-only). The named forbidden drawings files pdf_object_streams.py, test_pdf_object_streams.py, sheet_marked_content.py, sheet_objects.py are byte-identical 0c638f88..HEAD (empty diff). requirements.txt / requirements.in unchanged; no new import (ruff + G5 grep clean); no route/app/main.py/app/api change by this task. Exactly ONE golden substitution (refuse_l_no_current → refuse_curve_no_current) confirmed in the split-equivalence suite (G3 F4 machine-verified, all 61 other per-case digests unchanged, reproduced in my 322-pass run). G0 report:16-19 records PR #241 / R007 DWG hold / max-envelope UNMOUNTED all standing; the module remains unwired so nothing mounts.

Continues in Part 4 (D-087-R005 four steps + corpus honesty, advisories, verdict). END-OF-PART-3

---

M5-T120 DCV — PART 4/4 (D-087-R005, advisories, findings, verdict).

D-087-R005 (architect-PDF reading, four steps, honest real-corpus) — SATISFIED. Primary evidence, each verified in source:
(1) SPLIT: services/api/app/drawings/sheet_path_state.py exists (250 lines, `_PathState` mixin; `_StreamRun(_PathState)`); sheet_interpreter.py = 577 (< 750). Byte-identity proved by the split-equivalence suite passing in my 322 run; exactly one intended case substitution.
(2) /DP DICTIONARIES: sheet_inline_image.py `_DECODE_PARMS_KEYS={DP,DecodeParms}` (:86), `_MAX_INLINE_DP_DICT_DEPTH=1` (:87), `_nested_dict_allowed` (:309-314) — one nested level for /DP or /DecodeParms only, same 4096-byte cap, value stored as a sentinel (no sample decoded); a non-/DP nested dict refuses (:185-188) and a 2nd level refuses (:382-385).
(3) CITATIONS: grep confirms NO residual "8.9.5.2"; §8.9.3 (row alignment, :20/:224), §8.9.5.1/Table 89 (:73), Table 93 (colour-space abbreviations, :7/:21/:100/:437) all present.
(4) ORPHAN LINETO: sheet_path_state.py `_lineto` (:71-73) routes a no-current-point `l` to `_orphan_lineto` (:83-102), which opens a NEW subpath at its OWN mapped point (`_cur_points=[point]`), draws NO segment from the stale pre-paint point, and increments page+document orphan_subpaths; `_curveto` (:104-108) keeps orphan curves a typed refusal. The G1 REQUIRED correction IS applied (I read git show 793fed27): the docstring now states Canvas-2D/pdf.js verified (the "[recalled - verify]" marker removed) and MuPDF STRICTER (warns-and-ignores, not a match) — and the change is doc-only (both hunks entirely inside docstrings; executable lines unchanged context).

Corpus honesty: producer report:14-17/124-136/209-215 states 4 of 6 read (item 2, the 94pp VA set, newly unblocked by the orphan rule; items 5-6 scan-only refuse; /DP proven by SYNTHETIC tests only — item 2's 8,154 inline images carry no /DP dict; no real file hits an orphan curve). No overclaim. G4 (qa-engineer, independent, not producer) re-fetched all six by urllib, sha256 all MATCH, reproduced 4-read/2-refuse, and proved item-2 causality by REVERTING `_lineto` to the pre-P4 refusal (→ item 2 refuses) and restoring (→ reads) — the causal claim is reproduced, not asserted.

ADVISORIES — none undercuts a cited requirement. G3 A1 (cite → routed to G1, resolved), A2 (/DP synthetic-only — honestly disclosed, bounded, mutation-covered), A3 (documented mixin coupling, ruff-only CI). G4 advisory (Table 92 wording — resolved by the correction). G5 L1 (document ceiling), L2 (filtered early-EI), LOW-1 (/UserUnit isfinite) — all carry-forward at the FUTURE mount, none introduced by T120; the module stays UNMOUNTED (R009), so these belong to the mount, not this packet.

FINDINGS
- F1 (informational): CI at the corrected head is green via the M5-T124 seam run (Part 2) — the "queued behind an in-flight run" note is resolved; no action.
- No blocking findings. No VIOLATED, UNVERIFIABLE, or BLOCKED requirement.

Requirement tally: D-066-R001 SATISFIED, D-087-R001 SATISFIED, D-087-R002 SATISFIED, D-087-R005 SATISFIED, D-087-R009 SATISFIED.

M5-T120 DCV VERDICT: PASS 5/5

END-OF-REPORT
