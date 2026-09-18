# M5-T038 — Directive-compliance verification return (VERBATIM; directive-compliance-verifier, read-only)

Orchestrator note: returned complete (untruncated) via the agent-return channel
2026-09-18T10:05:21Z. VERDICT: PASS (sole applicable row D-066-R001); conditional restamp
pre-authorization granted with exact wording (§ end).

---

M5-T038 directive-compliance verification — VERDICT: PASS. Verified at live HEAD e829050e, frozen material d94bbcb6.

APPLICABLE SET (independent): registry evaluate_task_refs on the M5-T038 packet returns applicable=cited={D-066-R001}, missing=[], invalid=[]. Sole applicable requirement confirmed.

BYTE-STABILITY d94bbcb6..HEAD (13 allowed_paths): `git diff d94bbcb6 e829050e` over all 13 packet paths = EMPTY (exit 0). Frozen submission identity holds. The rest of the range is disjoint: M5-T037 lane material (rule-eval display/contract/api files) + the orchestrator [ORCH-CORRECTED] e2e copy fix (8c089343, e2e spec only, OUTSIDE allowed_paths) + control-plane files.

--- D-066-R001 (obligation; orchestrator embeds a seam-regenerated code-graph navigation block + query.py --no-regen instruction, graph advisory): SATISFIED / PASS ---
Primary evidence reproduced:
1. Nav block PRESENT in the packet: project-control/tasks/M5-T038.json inputs[1] carries the "CODE-GRAPH NAVIGATION BLOCK (D-066-R001...)" with (a) regen provenance "M5-T035 acceptance seam c759a049: 734 files, 15427 nodes, 6852 edges" — c759a049 confirmed to exist (M5-T035 accept, 219th) and those exact counts match the independently-recorded M5-T039 DCV at the SAME seam (verification.json M5-T039 row); (b) key consumers/dependencies/impact set for the target files; (c) the query.py instruction verbatim: "Run `python tools/code_graph/query.py --no-regen impact <path>` BEFORE broad sweeps"; (d) advisory clause: "Graph is ADVISORY - verify every material conclusion in source." Tooling present: tools/code_graph/generate.py + query.py.
2. Block pointers independently verified in ACTUAL SOURCE (advisory-verified-in-source): AddressResolutionScreen.tsx:17 imports AddressAutocomplete (exact line match); AddressAutocomplete.tsx:9 imports @/lib/address-search; use-address-suggestions.ts:3 imports address-search (file at apps/web/src/lib/architect/use-address-suggestions.ts — block wrote the bare filename, path-prefix informality only, correct file); PropertyOverview consumed by ArchitectEntry/ProfileViews/PropertyFacts/ReportView/ScenarioWorkspace (all 5 found).
3. Build honored the stated impact boundaries in source (git show d94bbcb6): PropertyOverview.tsx additive-only — public props signature unchanged; the existing `<a>` truthy branch preserved (now with aria-hidden glyph + data-testid), only the former `null` else-branch became the honest-absence note behind data-testid site-zola-absent (PropertyOverview.tsx:55-68). development-limits.test.tsx (M5-T037 lane) NOT touched by the material commit. Material commit = 9 files, ALL within the 13 allowed_paths; the one out-of-scope consumer (e2e architect-workspace.spec.ts DB-009 copy) corrected by the orchestrator at 8c089343, tagged "[ORCH-CORRECTED per web-e2e CI on d94bbcb6]", e2e-spec-only, M5-T032 precedent — so d94bbcb6 material identity stays byte-stable.
4. Corroboration: evidence-map project-control/reports/M5-T038-evidence-map.json D-066-R001 row; CI evidence (vitest 42/42 at material; all 20 green at corrected 8c089343); gates G2 PASS(orchestrator)/G3 PASS(code-reviewer)/G4 PASS(qa)/G5 PASS(security), reviews pinned at material d94bbcb6. Note: the producer report does not narrate graph consultation, but R001 is an ORCHESTRATOR obligation whose primary evidence is the packet (present + verified) — consistent with the recorded M5-T035 verification basis.

PROHIBITED-ACTION check: M5-T038 status=awaiting_gate (not accepted); HEAD not on main (candidate/D-024-mrl-option-b); no open blocker references M5-T038. Nothing merged/deployed/closed on its behalf. Acceptance correctly gated on this verification.

CONDITIONAL RESTAMP PRE-AUTHORIZATION: YES — I pre-authorize restamping my D-066-R001 verification row (reviewed_sha) from d94bbcb6 to the acceptance seam sha, CONDITIONAL on the orchestrator verifying, at the seam sha, BOTH: (1) `git diff d94bbcb6 <seam-sha> --` over the packet's 13 allowed_paths is EMPTY (byte-stable), AND (2) the seam diff d94bbcb6..<seam-sha> touches ONLY control-plane files (project-control/**) plus already-landed disjoint M5-T037-lane/e2e-correction commits — no change to any of the 13 packet allowed_paths and no change to the nav-block text in tasks/M5-T038.json inputs. If either fails, do not restamp; return to me.

Exact condition wording to record: "Restamp of D-066-R001 (M5-T038) from d94bbcb6 to <seam-sha> is authorized ONLY IF (a) git diff d94bbcb6..<seam-sha> over the 13 packet allowed_paths is empty AND (b) git diff d94bbcb6..<seam-sha> --stat is control-plane-only (project-control/**) with the M5-T038 nav-block packet input byte-stable; verified by the orchestrator before assembly."

OVERALL: PASS — D-066-R001 SATISFIED on reproduced primary evidence; no VIOLATED/UNVERIFIABLE rows; directive-compliance clears M5-T038 for acceptance.
