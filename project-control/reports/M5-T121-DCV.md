# M5-T121 — directive-compliance verification (directive-compliance-verifier "dcv-t121", read-only)

> Transmission history: pinned at 3cb9d684 (HEAD later advanced through disjoint peer seams - the M5-T123 and
> M5-T120 harvests - with the three T121 blobs and identity 243a7da1 byte-stable), delivered as four SendMessage
> parts (1/4 carries the up-front restamp pre-authorization) ending with END-OF-REPORT; no truncation (parts 2-4
> were queued twice, byte-identical; the first copy is joined). Joined verbatim by the orchestrator (transport
> wrapper tags removed only).

---

M5-T121 DCV — PART 1/4 (HEAD + restamp pre-authorization, UP FRONT)

Live HEAD at start: 3cb9d684ce7eac97c1ed1e2339d0f3cad6f0041c (branch candidate/D-024-mrl-option-b). CI green at HEAD (run 36114594719): control-plane (ADR-005), api (py3.12), modularity, code-graph, contracts, web-e2e all success.

FROZEN IDENTITY — reproduced, not trusted. _task_git_identity(reg, task) at HEAD = 243a7da1f600197b77561d059c79605a22e93dc43ae6cd1884f3fa43a1c6ddf0. Equals reports/M5-T121.json content_manifest_sha256 AND the G2/G3/G4/G5 stamps (all 243a7da1). git diff --stat d865d977..HEAD over the 3 allowed paths is EMPTY — HEAD blobs are byte-identical to material d865d977.

RESTAMP PRE-AUTHORIZATION
Blob-level predicate — this PASS stands at any later accept-time HEAD as long as the three allowed-path blobs are byte-identical to what I reviewed:
- sheet_import.py faa95c04
- test_sheet_import.py ecc14b54
- M5-T121-producer-report.md ea826181
- identity 243a7da1
Equivalently: reports/M5-T121.json content_manifest_sha256 stays 243a7da1 and _task_git_identity at the new HEAD returns 243a7da1. If any of the three blobs changes (identity != 243a7da1) this PASS is void and re-review is required.

Disjoint-peer tolerance (broad; no re-review) — I tolerate: other tasks' files/gates/material (M5-T120, M5-T122, M5-T123 and any new packets); other directives' registry binds; the orchestrator adding my verification rows to the D-066/D-083/D-087 verification.json with digest resyncs and audit-log entries; DISCOVERY_BACKLOG rows and sweep lines; and lifecycle-only packet changes to M5-T121 (status/progress transitions that leave the 3 blobs byte-stable).

APPLICABILITY reproduced via registry.evaluate_task_refs(task): ok=True; applicable == cited == {D-066-R001, D-083-R001, D-083-R006, D-087-R001, D-087-R002, D-087-R005, D-087-R009}; missing=[], invalid_refs=[], unresolved=[].

---

M5-T121 DCV — PART 2/4 (requirement rows, primary evidence reproduced)

D-066-R001 (obligation — nav block + query.py cue; graph advisory): SATISFIED. project-control/tasks/M5-T121.json inputs[20] carries the graph-derived navigation block (regenerated wave-1 seam, 844 files/18356 nodes/7841 edges; consumers = none/unmounted; deps = reader public types, dxf_import public names, app.scenario.proposal READ-ONLY) and instructs the producer to run `tools/code_graph/query.py --no-regen impact <path>` before sweeps, "graph ADVISORY - verify every material conclusion in actual source."

D-083-R001 (prohibition — no claim-class wording): SATISFIED. sheet_import.py emits only honest labels: DRAFT_SOURCE_LABEL "Proposed - not a city record" (:604 / dxf_import.py:75), DRAFT_INPUT_PRECISION "imported drawing - not survey-confirmed" (:603), FRAME_NOTE local-frame (:619). No "permitted / approved / maximum allowed / as of right / demonstrated maximum" anywhere (read the full source; it is a proposal-import service and computes no regulatory ceilings). Corroborated: test_provenance_block_is_complete_and_honest asserts _FORBIDDEN_WORDS absent (test:76-78, 334-336); G5 confirms.

D-083-R006 (obligation — input-precision provenance, never upgraded): SATISFIED. Provenance block sheet_import.py:601-622: input_class "imported_pdf" (:602, const :100), precision "imported drawing - not survey-confirmed" (:603; VALUE confirmed at dxf_import.py:76), frame_note "...not aligned to the mapped lot" (:619, FRAME_NOTE :102-105). Precision is a set-once constant; test_mutation_precision_not_upgraded (test:436-442) reddens by upgrading it, so the literal is load-bearing.

D-087-R001 (obligation — full gated ledger packet under today's capacity): SATISFIED. Full lifecycle: G0 PASS at f0d9ea9b (gates/M5-T121-G0.json), claimed a990de06, orchestrator-dispatched subagent producer run concurrently with disjoint M5-T119/T120/T122/T123; required gates G0/G2/G3/G4/G5 all recorded PASS — no state or gate skipped.

---

M5-T121 DCV — PART 3/4 (rows cont. + the D-087-R005 judgment)

D-087-R002 (prohibition — no interference / disjoint scope / isolated worktree): SATISFIED. allowed_paths = exactly the 3 NEW files (sheet_import.py, test_sheet_import.py, producer report); the reader modules M5-T120 is editing sit in THIS task's forbidden_paths (tasks JSON:37-60). One worktree wt-m5t121 (:119). Material d865d977 touches exactly those 3 paths (git ls-tree + empty diff vs HEAD), each blob MATCH. Disjoint from M5-T119/T120/T122/T123.

D-087-R005 (authorization — phase-C assisted PDF import; C-track honesty): SATISFIED, and the disclosed limit is honest, not a gap. list_candidates (:355) lists closed rings by STABLE index, bounded 200 / total disclosed, measured in sheet units, scale notes escaped and NEVER parsed (:339-352). build_draft (:534): the SERVICE measures the user-named edge itself (_measure_edge :418, _resolve_scale :452); RoleAssignment has NO client-measurement field (structural test :250-256); scale = known_ft / measured (:489). The user-ASSIGNED ring (_select_ring by stable index :508) is scaled with explicit closure (:523) and enters the SAME validate_proposed_massing contract (:592); kind stays "proposed" (:589). Discrepancy shown, never auto-reconciled: a LOCAL frame fails the UNCHANGED NYC-2263 bounds (proposal.py:96-99, reproduced) → draft_invalid, never georeferenced (test:306-311).
JUDGMENT on deviation 3 / OQ-1 / DISC-A: the packet objective itself scopes alignment OUT ("a frame note that the outline is in a LOCAL scaled sheet frame, not aligned to the mapped lot (alignment is a later step)"). A real un-aligned sheet failing as draft_invalid is therefore a correctly-disclosed first-slice limit, NOT a shortfall against what the packet promised. Honest.

D-087-R009 (prohibition — unchanged boundaries; zero new deps; unmounted): SATISFIED. Imports only math/dataclasses + internal dxf_import/sheet_primitives/scenario.proposal — zero new deps; requirements.txt/.in are forbidden and untouched. Unmounted (no route, no app/main.py; only 3 files). dxf_import + reader modules + app/scenario untouched (forbidden_paths; diff empty). modularity_check --check EXIT 0, sheet_import.py NOT flagged (reproduced). All gates PASS; CI green at HEAD.

---

M5-T121 DCV — PART 4/4 (gates, sweep, harness, findings, verdict)

GATES — all required PASS by independent reviewers, none the producer (backend-engineer): G0 orchestrator/administrative (f0d9ea9b); G2 self-check recorded by orchestrator (per CLI rule); G3 code-reviewer; G4 qa-engineer; G5 security-reviewer. G2/G3/G4/G5 all stamp content_manifest 243a7da1 == frozen identity.

PROHIBITED-ACTION SWEEP (all clean): not accepted (status awaiting_gate); verification rows for M5-T121 = 0/0/0 across D-087/D-083/D-066 verification.json; material d865d977 NOT on main; PR #241 OPEN on unrelated branch task/M5-T002, untouched; no blocker file mentions M5-T121.

HARNESS: pytest tests/drawings/test_sheet_import.py → 31 passed (local py3.11), reproduced. CI: named run 36113132489 success at ed229971; latest HEAD 3cb9d684 CI + secret-scan + context-budget all success; control-plane (ADR-005), api (py3.12), modularity jobs success at HEAD. I SKIPPED the 12-min validate_directive_compliance.py --check per your allowance — the intake/digest rows are settled by (a) the control-plane CI job success at HEAD (it runs the validator) and (b) my local registry-loader reproduction (evaluate_task_refs ok=True, zero integrity errors / invalid refs for all 3 cited directives).

FINDINGS (all ADVISORY; none blocks; none undercuts a cited requirement):
- F1 = G4-A1: last-edge scale (scale_edge=n-1) untested; current code correct (`(edge_index+1)%n`, :437). Test-coverage gap only.
- F2 = G5 LOW-1: list_candidates echoes page floats (:403, :333-334) without the finiteness guard; not reachable today (lexer caps magnitude ~1e63 finite); mount/reader owner's job (producer DISC-B).
- F3 = G5 LOW-2: _escape_drawing_text escapes C0+0x7F but not C1/bidi — byte-identical to the accepted DXF helper (parity, JSON data). Track under DB-070/DB-081.
The G3 A1-A2 / G4 A1-A4 / G5 LOW-1/2 advisories are all defensive/coverage items consistent with the accepted DXF precedent; each reviewer states it does not weaken the validate_proposed_massing contract or the honesty/provenance discipline. Confirmed.

Every applicable requirement judged on reproduced primary evidence (source, deterministic tests, git objects, control-plane records) — not the producer's matrix.

M5-T121 DCV VERDICT: PASS 7/7
END-OF-REPORT
