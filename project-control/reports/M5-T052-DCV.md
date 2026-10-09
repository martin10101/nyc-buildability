# M5-T052 DCV — directive-compliance verification (directive-compliance-verifier, saved VERBATIM from the agent return)

M5-T052 DIRECTIVE-COMPLIANCE VERIFICATION — VERDICT: PASS (independently reproduced; producer≠verifier)

Applicability: evaluate_task_refs ok=true; applicable_ids == cited_ids == [D-066-R001, D-073-R006]; no missing/invalid/unresolved.

PER-REQUIREMENT:

D-066-R001 (obligation, graph-derived nav block + advisory-verify-in-source) — SATISFIED
- project-control/tasks/M5-T052.json inputs[3] "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this contract seam)": embeds key consumers (PropertyOverview.tsx: ArchitectEntry.tsx:24/ProfileViews.tsx:18/PropertyFacts.tsx:9/ReportView.tsx:11/ScenarioWorkspace.tsx:4/condo-resolution-display.test.tsx:12; AnalysisIdentityNotice consumers), dependencies (resolver via profile/zoning_crosscheck.py:524-633 + spatial/live_provider.py:47), impact set; instructs `python tools/code_graph/query.py --no-regen impact <path>` before sweeps; marks graph "ADVISORY - verify in source."
- STALE POINTER confirmed and judged non-material: nav text says services/api/app/rules/condo_base_lot.py; `git ls-tree e9abeaaf` shows the resolver actually at services/api/app/connectors/condo_base_lot.py, and the route (condo_records.py) imports the CORRECT path (resolve_condo_billing/condo_resolution_report present in connectors/condo_base_lot.py). Correction recorded in project-control/reports/M5-T052-G2.md:22-23. This is exactly the advisory-graph clause's safety net — the material conclusion was verified in source; the stale label did not propagate. Producer report §5 (lines 158-162) documents the native-tools consumer sweep + routes the one out-of-scope consumer (report-view.test.tsx) to the orchestrator.

D-073-R006 (obligation, records-vs-allowances separation) — SATISFIED
- Records under fail-safe, RECORD-class wording: PropertyOverview.tsx CondoRecordsChannelSection (lines 219-261) "City records for this condo" (240), "shown for reference under the professional-review determination above" (241); rendered at line 311 AFTER DevelopmentLimits grid (291) = UNDER the fail-safe (comment line 216).
- Monotone withhold: deriveCondoSurface line 206 `withholdAllowances = profileWithholds || channelWithholds` (OR — channel only ADDS); comment 181-183; withheld ⇒ shownScenario/shownEvaluation nulled (285-286).
- No allowance vocabulary (grep gates in condo-resolution-display.test.tsx): line 368 records `.not.toMatch(/allowance/i)`, 386 substitution, 417 conflict; heading semantics 367 `.not.toMatch(/\banalys(is|es|ed)\b|zoning result|computed result/i)`; no computed decimals 377/511.
- Honest absence: CondoRecordsChannelSection returns null for loading/unavailable/unresolved/resolver-error/non-condo (258-260); tests 390/397/530/540. Route condo_records.py emits resolver's OWN typed tokens (resolved_single_base_lot/multi_lot_set/unresolved/error/not_condo_billing); multi_lot_set fail-safe; honest absence on unresolved/error (lines 26-42).
- Proves in CI: run 35451055372 = success at a6f35a0f (headSha a6f35a0ffe4894d82e2ef6c4c0f5bf6edd8ee3a6); all 9 code files byte-IDENTICAL a6f35a0f..e9abeaaf (only producer-report.md changed via 2dcdb3f2).

CROSS-CUTTING (reproduced):
- Allowed_paths byte-stability e9abeaaf..HEAD(396081b5): all 10 STABLE.
- Re-freeze diff 6e3e1a40..e9abeaaf: control-plane/report only (reports + state.json + tasks/M5-T052.json); ZERO code change — matches "report text only."
- Material build 365f492f touched only allowed-path files; tagged fixes a6f35a0f (condo-records.ts) + 2dcdb3f2 (reports); routed sweep 46bf1105 = report-view.test.tsx (OUT of allowed_paths, correctly separated). No forbidden path touched (connectors/ resolver untouched).
- Gates G1-G5 all PASS; content_manifest_sha256 = 6ae71aeed51165b2800ae4106ee9f33a7ef97b985d62f97c60a786b93211d1cd consistent across all five; reviewed_sha 00a2c69e; all five delta-attested to carry to e9abeaaf.
- Prohibited-action: task status awaiting_gate (95%), NOT in accepted_tasks, no PR (open or merged). Nothing accepted/merged/dispatched/deployed/installed/purchased/closed.

VALIDATOR: `python tools/validate_directive_compliance.py --check` → exit 0 (foreground).

RESTAMP PRE-AUTHORIZATION (reproduced at 396081b5; re-check at the actual accept head <T>): PASS when (1) `git diff e9abeaaf..<T>` EMPTY on each of the 10 allowed_paths, (2) evaluate_task_refs ok (applicable==cited), (3) validator --check exit 0. Tolerated disjoint peers: gate-record/report/backlog commits (00a2c69e/396081b5), verification.json v2-row appends, and M5-T051/M5-T053 lane material (scenario/** + proposal_validation/scenario gate files — disjoint from every T052 allowed path).

v2 FIELDS:
- reviewed_manifest_sha256 = 6ae71aeed51165b2800ae4106ee9f33a7ef97b985d62f97c60a786b93211d1cd
- reviewed_sha = the accept/restamp target head (later head; set at record time per the pre-authorization)
- producer = backend-engineer
- verifier = directive-compliance-verifier

OVERALL: PASS. Both applicable requirements SATISFIED on reproduced primary evidence; zero VIOLATED/UNVERIFIABLE; no prohibited action. One recorded, corrected, non-material imperfection (nav-block resolver path rules/ vs connectors/, fixed in G2, route imports correct path).
