# M5-T036 DCV verification — directive-compliance-verifier return (VERBATIM)

Verifier agent: directive-compliance-verifier (spawn dcv-m5t036), read-only, pinned HEAD
5b9da18dd9ba7ab4ad0f7b23f09df3aafd8fe9a6. Saved verbatim from the agent-return channel
(transport entity-decoding only). Orchestrator note: the restamp condition was re-verified at
bc1fae15 before assembly (only control-plane files changed since 5b9da18d; the packet's
CODE-GRAPH NAVIGATION BLOCK input byte-stable) — the carry is valid.

---

DCV FINAL REVIEW — M5-T036 — VERDICT: PASS (both applicable requirements SATISFIED)

HEAD verified: `git rev-parse HEAD` == 5b9da18dd9ba7ab4ad0f7b23f09df3aafd8fe9a6 (branch candidate/D-024-mrl-option-b). Read-only throughout; no writes.

APPLICABLE SET (reproduced myself, not trusted): ran reg.evaluate_task_refs on project-control/tasks/M5-T036.json → applicable_ids == cited_ids == ['D-066-R001','D-071-R002']; missing=[], invalid=[], unresolved=[], ok=True. Confirmed no other active directive leaks in: D-064-R005 has paths ['apps/web/'] but non-empty task_ids ['D-064-BOOTSTRAP','M5-T032'] excludes M5-T036 under the registry's conjunction semantics (_applicability_matches, tools/directive_registry.py:605-606). No amendments exist for either directive (only source-001.md in each dir).

MATERIAL IDENTITY — CONFIRMED. `git diff 82143124 HEAD --name-only` shows ONLY control-plane files (gates/M5-T036-G1..G5.json, reports/M5-T036-G2.md, -ci-evidence.md, -delta-attestations.md, -evidence-map.json, state.json, tasks/M5-T036.json) — NO file inside the task's allowed_paths (the 9 apps/web files + producer-report.md). Lineage: build 657b238d (6 web files + report), test-only rework 82143124 (only zoning-context-panel.test.tsx + report addendum, verified via `git show 82143124 --stat`: no production file), intervening f31f28ff = control-plane only. Submit fb00ac0c froze that content; gates recorded at reviewed_sha fb00ac0c validly cover the 82143124 material content. NOTE: working tree has uncommitted control-plane-only edits to tasks/M5-T036.json (progress 85→95) and state.json (timestamp) — no allowed_paths content, does not affect identity.

—— PER-REQUIREMENT ROWS ——

D-066-R001 (obligation: regenerate graph at contract seam + embed graph-derived nav block naming consumers/deps/impact for target files + instruct producer to use query.py --no-regen before broad sweeps + graph stays advisory, conclusions verified in source) — SATISFIED.
  • Nav block PRESENT in packet: project-control/tasks/M5-T036.json inputs[] "CODE-GRAPH NAVIGATION BLOCK (D-066-R001...)" (line 13), carries seam-regen counts 732 files/15341 nodes/6791 edges matching the contract-seam commit 8dccf758 ("graph regenerated (732/15341/6791)").
  • Cites query.py --no-regen: block text "For who-consumes/impact questions run 'python tools/code_graph/query.py --no-regen impact <path>' BEFORE broad sweeps" and closes "Graph is ADVISORY - verify every material conclusion in source." Present in both inputs and outputs REVIEW GUIDANCE.
  • Pointers verified in ACTUAL SOURCE by me (more than two): PropertyOverview importers at exact cited lines — ArchitectEntry.tsx:24 (imports the PropertyOverview component; mounts at :95), ProfileViews.tsx:18, PropertyFacts.tsx:9, ReportView.tsx:11, ScenarioWorkspace.tsx:4 (latter four import only sibling re-exports PropertyIssuesSummary/DraftHeadline, NOT the component — which is exactly why the panel does not leak to the printed brief). Also zolaLotUrl at provenance-link.ts:53 (returns string|null), mappedFeatureView at contract.ts:257, ZoningSection arrays districts/commercial_overlays/special_districts at ZoningSection.tsx:113-128. All accurate.
  • Advisory-verified-in-source corroborated by independent G3 (project-control/reports/M5-T036-G3.md:62 "the code-graph nav block was accurate and useful — PropertyOverview's five importers and the ReportView print reach matched source exactly").
  • Could-not-fully-verify (marked explicitly, not a violation): the physical `generate.py --repo .` invocation isn't reproducible from git objects alone. The required harness (block present + query.py cited + advisory) is fully met and the block content is independently source-accurate, which is R001's substance. D-066-R003 (wall-time/token comparison) is NOT applicable to M5-T036 (its task_ids are D-066-BOOTSTRAP + M5-T033 only) — correctly out of scope.

D-071-R002 (obligation: loop-2 lane = DB-016 context-panel parity — designations [districts incl. split-lot, commercial overlays, special districts, landmark/historic] with provenance + validated ZoLa link alongside computed answers; fold in DB-005 ZoLa-link unification; label-display-only, no computation/new data source; computed engine stays the differentiator) — SATISFIED.
  • Panel delivered: apps/web/src/components/architect/ZoningContextPanel.tsx renders districts/commercial_overlays/special_districts via the shared ZoningValueList with honest emptyText, and landmark/histdist via mappedFeatureView with "Unknown — not supplied" honest absence; per-value provenance via provenanceById/resolveFactProvenance/ProvenanceDisclosure; ZoLa link via zolaLotUrl(profile.identity.bbl) → null renders explicit honest-absence, no raw template.
  • Mounted alongside the computed answer: PropertyOverview.tsx build diff adds `<ZoningContextPanel profile={profile}/>` below DevelopmentLimits; panel carries "Nothing here is computed — the calculated result stays in Development limits."
  • DB-005 unification verified in both files: PropertyOverview.tsx dropped inline `https://zola.planning.nyc.gov/bbl/${bbl}` for zolaLotUrl(bbl); AddressConfirmCard.tsx removed the ZOLA_BBL_URL_PREFIX constant + inline template for zolaLotUrl(canonicalBbl). grep for raw zola template URLs in the three touched files → zero.
  • Label-display-only / no api/contract/lib change: material commits touched NO forbidden path (services/api/**, apps/web/src/lib/**); lib is imported not modified (G1 F6, G5 finding 3 "No new network path / api change" — reproduced: no fetch/XHR/axios and no env/secret in the components). Computed-answer engine (DevelopmentLimits) not in the material diff.
  • Independent review: all six required gates G0-G5 recorded PASS (G0 orchestrator@8dccf758; G1 data-contract-verifier, G2 orchestrator self-check, G3 code-reviewer, G4 qa-engineer, G5 security-reviewer @fb00ac0c) — none by the producer (frontend-engineer). Five reviewers' VERBATIM carry-attestations at 82143124 on file (project-control/reports/M5-T036-delta-attestations.md) confirming the rework is test-only and their PASS holds.
  • CI green at corrected head — reproduced independently: `gh run view 35289402788` (CI workflow, push at 82143124) = success, with web-e2e (vitest+Playwright) = success, web (lint+typecheck+build) = success; secret-scan + context-budget runs also success.

REGISTRY INTEGRITY: `python tools/validate_directive_compliance.py --check` exit 0 (clean; digests match, no c14 issue).

PROHIBITED-ACTION EVIDENCE: task status = awaiting_gate (not accepted); no open blocker references M5-T036; 82143124 is contained only in candidate/D-024-mrl-option-b, NOT main; ZoningContextPanel.tsx absent from origin/main. Nothing merged/accepted/dispatched/deployed/installed/purchased/closed. This is a valid pre-accept verification.

RESTAMP RULING (conditional pre-authorization, per the proven M5-T034 pattern): My PASS rows for BOTH requirements may be carried VERBATIM to your later accept-seam head PROVIDED `git diff 5b9da18dd9ba7ab4ad0f7b23f09df3aafd8fe9a6 <accept-head> --name-only` contains NO file inside the task's allowed_paths (the nine apps/web source/test files AND project-control/reports/M5-T036-producer-report.md). Control-plane-only changes between (gates/, other reports/, evidence-map, state.json, tasks/M5-T036.json, verification.json) do not break the carry. ADDITIONAL condition on D-066-R001: the packet's CODE-GRAPH NAVIGATION BLOCK input text in tasks/M5-T036.json must remain byte-stable — if it is edited, re-check R001 before carry. If any allowed_paths file (including an [ORCH-CORRECTED] producer-report edit) changes, walk rework→submit to re-freeze and re-attest before carrying.

CORRECTIONS REQUIRED: none.

HONESTY BAR: I did not attempt an exhaustive audit of every line of the 9 files or every reviewer finding; I reproduced the primary evidence for each requirement ID cited above. The one item I could not reproduce from git alone (the physical graph-regen invocation) is stated explicitly and does not block, because R001's harness and source-accuracy are independently verified.
