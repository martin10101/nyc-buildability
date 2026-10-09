# M5-T124 — directive-compliance verification (directive-compliance-verifier "dcv-t124", read-only)

> Transmission history: pinned at 002f663c (the three T124 blobs and identity 00516535 byte-stable), delivered as four
> SendMessage parts (1/4 carries the up-front restamp pre-authorization) ending with END-OF-REPORT; no truncation.
> Joined verbatim by the orchestrator (transport wrapper tags removed only).

---

M5-T124 DCV (D-087 PKT-L2, phase C2 alignment) — PART 1/4: frozen head, restamp pre-authorization, identity, gates, prohibited-action sweep.

FROZEN HEAD at start: git rev-parse HEAD = 002f663c6050603e9a0e94f5040086ea2a98f8a4.

RESTAMP PRE-AUTHORIZATION (up front)
Blob-level predicate — this PASS holds at any HEAD where the three allowed-path blobs are byte-identical:
- services/api/app/drawings/drawing_alignment.py eede1e29
- services/api/tests/drawings/test_drawing_alignment.py c1de0c40
- project-control/reports/M5-T124-producer-report.md 286dc10b
and content_manifest_sha256 00516535 (I recomputed project_control._task_git_identity at HEAD 002f663c → 005165359511993410727a049cba6e6602ebe10d9fe88d60cd86e481891f39d1, equal to reports/M5-T124.json).
Disjoint-peer tolerance (broad): other tasks' files, gates and material (any new packets); other directives' registry binds; the orchestrator adding MY M5-T124 verification rows to the D-066 / D-083 / D-087 verification.json with digest resyncs + audit entries; DISCOVERY_BACKLOG rows and sweep lines; docs/SESSION_HANDOFF.md updates; lifecycle-only changes to project-control/tasks/M5-T124.json and state.json. Any of these may land without voiding the PASS while the three blobs and identity above are unchanged.

FROZEN IDENTITY — I recomputed _task_git_identity at HEAD = 00516535, and it equals: reports/M5-T124.json content_manifest_sha256 (00516535); the G2, G3, G4, G5 gate content_manifest_sha256 (all 00516535). G0 is the pre-production contract-seam readiness stamp (146e4c47 at 724248f2) — expected, not the material identity.

GATES (all PASS; all independent of producer backend-engineer):
- G0 PASS — orchestrator, administrative, reviewed_sha 724248f2.
- G2 PASS — orchestrator, self_check, reviewed_sha c65a0724, manifest 00516535.
- G3 PASS — code-reviewer, reviewed_sha f2986fac, manifest 00516535.
- G4 PASS — qa-engineer, reviewed_sha f2986fac, manifest 00516535.
- G5 PASS — security-reviewer, reviewed_sha f2986fac, manifest 00516535.

APPLICABILITY — I ran directive_registry.load_registry().evaluate_task_refs(task): ok=True; applicable_ids == cited_ids == [D-066-R001, D-083-R001, D-083-R006, D-087-R001, D-087-R002, D-087-R005, D-087-R009]; missing_ids [], invalid_refs [], unresolved []. Registry loaded with zero integrity errors on the three cited directives.

PROHIBITED-ACTION SWEEP: task status awaiting_gate (NOT accepted); NO verification row for M5-T124 in any directive verification.json (grep -rl, none); branch candidate/D-024-mrl-option-b (not main); PR #241 OPEN, mergedAt null — it is the unrelated M5-T002 "DO NOT MERGE" PR, untouched; no open blocker names M5-T124.

Requirement rows follow in parts 2–4.

---

M5-T124 DCV — PART 2/4: requirement rows (D-066-R001, D-083-R001, D-083-R006). Each judged on primary evidence I reproduced.

D-066-R001 (nav block present in the packet + producer prompt cites query.py --no-regen) — SATISFIED.
Primary: project-control/tasks/M5-T124.json inputs[] entry "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED at the wave-1 seam, 844 files / 18356 nodes / 7841 edges)" — names the module's inputs (draft-block shape from sheet_import.py / dxf_import.py READ-ONLY; validate_proposed_massing in app.scenario.proposal READ-ONLY), states no consumers (unmounted), and instructs "Run `python tools/code_graph/query.py --no-regen impact <path>` before sweeps; graph ADVISORY". Corroborated by M5-T124-G0.md lines 29–30. The requirement is packet-side and the packet carries it verbatim.

D-083-R001 (no permit / approved / unqualified maximum-allowed wording) — SATISFIED.
Primary: I grepped services/api/app/drawings/drawing_alignment.py for permit|approv|maximum allowed|survey. Every hit is a NEGATIVE disclaimer or a unit name, never an affirmative claim: line 36 "nothing is labelled a record, a permit, ``\"approved\"``, or a ``\"maximum allowed building\"``"; line 627 same in the align_draft_to_lot docstring; line 14 "US survey feet" (the EPSG:2263 unit name); line 83 "does not claim survey accuracy"; line 86 "NOT legal or survey values". The alignment provenance block (drawing_alignment.py:575–594) emits only method/formula/pair_count/rotation/translation/residuals/tolerance/scale/areas/precision/discrepancies — no claim-class vocabulary. Guard test test_no_permit_or_approved_or_maximum_allowed_wording scans the full JSON blob (G3:31, G4 L24, G5 test:443 all confirm).

D-083-R006 (input-precision provenance; conversion never upgrades input precision; user-confirmed, never automatic) — SATISFIED.
Primary in drawing_alignment.py:
- ALIGNMENT_PRECISION_NOTE (lines 81–84): "alignment places the imported drawing on the mapped lot; it does not upgrade the input precision and does not claim survey accuracy".
- _input_precision() (lines 420–428): reads provenance["precision"] and carries it UNCHANGED; a dedicated seam "so a test can prove an upgrade here would be caught".
- The alignment block sets input_precision = _input_precision(provenance) and precision_note = ALIGNMENT_PRECISION_NOTE (lines 591–592).
- ControlPair docstring (line 120): "NEVER auto-matched from drawing content" — alignment is user-confirmed.
- Guard + mutation: test_precision_label_kept_exactly_and_never_upgraded, reddened by producer mutant #10 (_input_precision → upgraded label); G4 (test:436) and G5 (line 38) independently confirm the label is echoed verbatim, deep-copied into the result (line 700), never upgraded.

Parts 3–4 follow.

---

M5-T124 DCV — PART 3/4: requirement rows (D-087-R001, D-087-R002, D-087-R009).

D-087-R001 (capacity: still a contracted, claimed, gated packet; no state or gate skipped) — SATISFIED.
Primary (git): contract seam 724248f2 = "D-089 wave-9 contract seam (seq 130): M5-T124" (G0 recorded there); claim seam 4c7437dd = "M5-T124: G0 PASS at the contract seam 724248f2, claimed (full worktree paths), progress 20"; produced by an orchestrator-dispatched subagent (packet inputs[0] PRODUCER MODE; progress_log agent backend-engineer). Full lifecycle present and in order: G0→G2→G3→G4→G5 all recorded PASS (part 1). No state or gate skipped.

D-087-R002 (no interference: pairwise-disjoint allowed_paths, worktree isolation) — SATISFIED.
Primary: allowed_paths is exactly the 3 task files; one worktree wt-m5t124 (tasks/M5-T124.json:121, progress_log claim entry). M5-T124-G0.md lines 32–54 give the disjointness table vs every state.json active task (M0-T021/034/080/109/133/145/153/155, M4-T001..006, M5-T001/110/120/122/123) — all "none - EMPTY overlap". I confirmed the material commit c65a0724 touches exactly the 3 allowed paths (git show --stat: drawing_alignment.py, test_drawing_alignment.py, M5-T124-producer-report.md; 3 files changed) — nothing shared with a peer.

D-087-R009 (unchanged boundaries: zero new deps; unmounted; importers/readers/app.scenario/connectors untouched; PR #241) — SATISFIED.
Primary (I reproduced each):
- Zero new deps: drawing_alignment.py imports (lines 42–52) are only copy, math, dataclasses (stdlib), shapely.errors, shapely.geometry (shapely already admitted), and app.scenario.proposal. No numpy, no new package. requirements.txt/requirements.in not in the diff.
- Importers untouched / duck-typed: grep for sheet_import|dxf_import|dxf_reader|sheet_reader in the module → only docstring mentions (lines 4,5,12), no actual import. git show --stat c65a0724 = the 3 allowed paths only; no app/drawings/sheet_*, app/scenario/, app/connectors/, app/api/, app/main.py touched.
- Unmounted: no route/endpoint/app.main change (forbidden_paths cover them; material touches none).
- Modularity: `python tools/modularity_check.py --check` → exit 0 (captured via variable, no pipe); drawing_alignment.py NOT in the warn list (703 file lines, ~592 SLOC, under WARN 600). Ruff clean (part 4).
- PR #241 unmerged (part 1 sweep). Native-DWG hold (R007) not implicated — pure Python, no DWG library.

Part 4 (D-087-R005 judgment, advisories, harness, findings, verdict) follows.

---

M5-T124 DCV — PART 4/4: D-087-R005 judgment, harness, reviewer advisories, findings, verdict.

D-087-R005 (phase C2: "alignment to the mapped lot with any discrepancy shown, never auto-reconciled") — SATISFIED.
Primary in drawing_alignment.py: align_draft_to_lot (615–703) fits a 2D RIGID Kabsch/orthogonal-Procrustes transform, PROPER rotation only (_rigid_fit 248–254; formula 24–31), and moves the outline into 2263. "Never applied" is enforced by three dedicated seams: _applied_scale→1.0 (225–229), _choose_transform→rigid (300–309), _final_outline_vertices→identity (312–316). All four discrepancies are DISCLOSED not reconciled (_build_alignment_block 540–573): two_pairs_unchecked, residual_exceeds_tolerance (max vs tolerance), scale_mismatch (implied vs confirmed 1.0), better_mirror_fit (≥3 pairs), outline_outside_lot (shapely). The aligned block is re-validated by the UNCHANGED validate_proposed_massing (677); every failure is a typed AlignmentRefusal VALUE. I confirmed the six producer mutants #6/#7/#8 (apply scale / allow reflection / clip) redden, and G4 independently caught 6/6.
DISC-A / OQ-1 judgment: the producer discloses (Deviation 1 line 81, OPEN QUESTION 1 line 87, DISCOVERY DISC-A line 93) that both importers' build_draft validates NYC-2263 bounds INTERNALLY, so nothing in the repo yet emits the local-frame pre-alignment block this service consumes; the future mount must assemble it without that premature check and validate only the aligned block. G3 (line 33) independently verified this is a real fact (sheet_import.py:592), NOT a defect, and the aligner is correctly duck-typed and imports neither importer. This is an HONEST, DISCLOSED next-step: the packet's C2 scope is the pure, unmounted alignment service over a duck-typed block, and that is delivered in full. Not a gap against this packet.

HARNESS (I reproduced):
- ruff check . (cwd services/api) → All checks passed!
- pytest tests/drawings/test_drawing_alignment.py -q -p no:cacheprovider → 39 passed (local py3.11)
- modularity_check.py --check → exit 0, module not flagged
- validate_directive_compliance.py --check → EXIT 0 (one run, direct exit code) — registry integrity clean at HEAD
- CI (gh): f2986fac (material) AND 002f663c (HEAD) → CI + context-budget + secret-scan all success (py3.12 authoritative). I did NOT run test_directive_compliance.py (forbidden) — the control-plane CI job green at the frozen head covers test_project_control.py / test_directive_reminder.py.

ADVISORIES — none undercuts a cited requirement: G3 1–4 (docstring wording, [A,A,B] lot-ring distinctness, footprint-only outside-lot, None-without-row) benign/cosmetic; G4 A1–A3 (unreachable non_finite path, fixture notes, loose residual bound) not defects; G5 LOW-1 (repr'd srid/kind echo — unreachable in real flow, JSON not HTML, same class as accepted M5-T121 LOW-2) and LOW-2 (no pre-transform size cap — linear work, mount's job per DISC-B) both route/defense-in-depth.

FINDINGS: F1 (advisory) DISC-A is a disclosed future-mount dependency, tracked; F2 (advisory) LOW-1 escape/length-bound belongs to the mount/UI if the refusal detail is ever rendered as markup; F3 (advisory) LOW-2 + G3-2..4 are route/defense-in-depth items owned by the future mount. None blocking.

M5-T124 DCV VERDICT: PASS 7/7

END-OF-REPORT
