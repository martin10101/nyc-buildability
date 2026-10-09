# M5-T037 — Directive-compliance verification return (VERBATIM; directive-compliance-verifier, read-only)

Orchestrator note: returned via the agent-return channel 2026-09-18T10:37:33Z; the transport
truncated the first delivery inside the D-045-R009 row. Part 1 below is the truncated delivery
verbatim; Part 2 is the resent remainder, verbatim. VERDICT: PASS all 4 applicable rows.

---

## Part 1 (first delivery, verbatim)

I have completed independent primary-evidence verification of all four applicable requirements at live HEAD fd2b8178. Returning the full DCV report.

---

# DCV REPORT — M5-T037 (rule_evaluation v1.1.0 screen wiring: DB-014 + DB-020 + display + report parity)

## VERDICT: **PASS**

All four applicable requirements SATISFIED on reproduced primary evidence. No VIOLATED/UNVERIFIABLE/BLOCKED rows. No prohibited action taken (task at `awaiting_gate`, not accepted; nothing merged/deployed/installed/purchased/closed; PR #241 open; no open blocker names the packet).

## Identity / frozen-head verification (reproduced myself)

- **Applicable set independently confirmed** via `directive_registry.load_registry().evaluate_task_refs(task)`: `{D-045-R008, D-045-R009, D-066-R001, D-073-R003}` — cited == applicable, `missing_ids: []`, `invalid_refs: []`. Matches the lead's set exactly.
- **(a) `git diff 1c89922c..HEAD --stat` is control-plane-only** — 14 files, all under `project-control/` (gates G1-G5, reports G1-G5/HJ/ci-evidence, state.json, tasks/M5-T037.json). No material file. CONFIRMED.
- **(b) api/schema/contract surface byte-stable a6875731..HEAD** — empty diff over all 12 contract/api/schema/lib paths (schemas, generated TS, integration.py, response.py, wide_street_live_provider.py, api tests, rule-evaluation-contract.ts, contract-versions.test.ts, CalculationEvidence.tsx). Both schema copies byte-identical at HEAD (`git hash-object` = `0f2eebd6…` for `packages/contracts/schemas/v1/rule_evaluation.schema.json` and `services/api/app/_contract_schemas/v1/rule_evaluation.schema.json`). CONFIRMED.
- **(c) Material identity = a6875731 (16 files, +1112/-54) + 75daaebd (F1/F2, 3 files) + d532928f (casing, 1 test file).** I enumerated every non-control-plane change a6875731..HEAD: exactly `DevelopmentLimits.tsx`, `ReportView.tsx`, `development-limits.test.tsx`, `report-view.test.tsx` (all from the two tagged rework commits), PLUS two disjoint-peer files that are **not** in M5-T037's allowed_paths and were baked in **before** 1c89922c — `docs/DISCOVERY_BACKLOG.md` (via M5-T038 accept 85e1f21d) and `services/api/tests/scenario/test_scenario_contract.py` (via sanctioned out-of-scope consumer-sweep be0a7062 for the enum bump, per the consumer-sweep rule). Neither touches M5-T037's material identity. CONFIRMED consistent with the lead's characterization.
- **Gates**: G1-G5 all `result: PASS`, shared `content_manifest_sha256 df500aad…`, `reviewed_sha e41804c4` (child of 1c89922c, inside the control-plane-only span, so material byte-stable). Reviewers: data-contract-verifier/orchestrator/code-reviewer/qa-engineer/security-reviewer. HJ = **PASS unconditional at 1c89922c** (F1+F2 applied and verified from source; F3/F4 backlog advisories) — `project-control/reports/M5-T037-HJ.md`.
- **CI independently re-verified** via `gh api …/commits/1c89922c…/check-runs`: **all 20 check-runs = success** (incl. `api`, `web`, `web-e2e`, `contracts`, `contracts-typegen`, `exact-production-install`). Matches `project-control/reports/M5-T037-ci-evidence.md` addendum.

## Per-requirement verdicts (each on reproduced source, not producer claims)

**D-045-R008 (sequencing) — SATISFIED.** M5-T037 is a single bounded packet (rule_evaluation v1.1.0 screen wiring, 20-path scoped allowed_paths in `project-control/tasks/M5-T037.json`), not a monolithic all-districts task, executed under the full G0-G5+HJ gated process. Evidence: gate records `project-control/gates/M5-T037-G{1..5}.json` all `result: PASS`.

**D-045-R009 (prohibition / scope-limit) — SATISFIED.** DRAFT/needs-review preserved on every surface: `DevelopmentLimits.tsx` panel heading `<span>Draft</span>` + line ~90 `"Draft — pending qualified legal review (not verified)."`; `CalculationEvidence.tsx:27` `"Draft · … · Professional review required"`; schema `$defs/wide_street` description states `"Never Verified - DRAFT pending G6; the higher wide-street FAR is withheld on uncertainty (D-051)"`. No compliance declarat[TRANSPORT TRUNCATION POINT]

---

## Part 2 (resent remainder, verbatim; delivered 10:38:20Z, clipped again inside the R003 parity bullet — Part 3 below)

Resending the remainder from the truncation point.

## D-045-R009 (prohibition / scope-limit) — SATISFIED (continued)

No compliance declaration is made anywhere in the surface. **No new dependency**: empty diff over `package.json` / `package-lock.json` / `apps/web/package.json` / `services/api/requirements.txt` / `services/api/pyproject.toml` across the full material span (a6875731~1..HEAD) — the wide-street work reused existing modules, so the §G package-admission path is not triggered. **PR #241 remains unmerged**: `gh pr view 241` → `state: OPEN, mergedAt: null, closed: false` (and nothing in the material diff touches it). **Higher wide-street FAR withheld on uncertainty**: `integration.py` `select_conditional_far_row` sets professional_review when `governing is None` (line ~528), and the UI renders the honest escalation rather than a value. DRAFT/needs-review preserved on every surface (DevelopmentLimits panel "Draft" + "Draft — pending qualified legal review (not verified)"; `CalculationEvidence.tsx:27` "Draft · … · Professional review required"; schema `$defs/wide_street` description "Never Verified - DRAFT pending G6; the higher wide-street FAR is withheld on uncertainty (D-051)"). Gap-list scope untouched (this task is one named-group increment, not a coverage expansion).

## D-066-R001 (obligation) — SATISFIED

The packet `project-control/tasks/M5-T037.json` carries a graph-derived navigation block: an explicit impact set naming the four api consumers of the changed serialization (`api/v1/evidence.py:95`, `api/v1/rule_evaluation.py:60`, `api/v1/scenario.py:73`, `api/v1/scenario_analysis.py:101`) and their test suites; the strict web runtime validator dependency (`apps/web/src/lib/rule-evaluation-contract.ts`); and the generated-TS note (`packages/contracts/generated/rule_evaluation.ts` is generated — regenerate via `packages/contracts/scripts/generate_ts_types.py`, never hand-edit). It instructs the producer to run `code_graph/query.py --no-regen impact <path>` BEFORE broad sweeps and marks the graph `ADVISORY - verify every material conclusion in source`. This is a packet-content obligation and is met in the packet text.

## D-073-R003 (obligation, load-bearing NEW row — first verification) — SATISFIED

Verified each element in source:
- **End-to-end chain (address → property → street info → conditions → calculation → result + evidence):** `services/api/app/spatial/wide_street_live_provider.py` obtains the street/geometry substrate and attests the DB-020 digest `source_raw_digest=page.raw_digest` (line 362, with the M5-T035 G1 F1 rationale comment that the digest MUST be the geometry-page raw-body sha256). `services/api/app/rules/integration.py` folds the determination via `select_conditional_far_row` (D-051 fail-safe: within→wide/higher row, not_within→standard/conservative row, else professional_review) and emits the optional block **only when a determination actually fired** (`as_dict` lines 193-194 — a 1.0.0-shaped body is preserved, no invented block). `services/api/app/rules/response.py:59` serializes at contract 1.1.0 for every document.
- **Result reaches the interface with WHAT / UNITS / CONDITIONS / SOURCES:** `apps/web/src/components/architect/DevelopmentLimits.tsx` `WideStreetResult` renders the FAR value, `"Wide-street conditional FAR — a dimensionless ratio. Floor area = FAR × zoning-lot area (sq ft)."`, `"Applies within 100 ft of a wide street."` (or the outside-100ft conservative line), the Draft marker, and a `"Wide-street sources and provenance →"` link into `CalculationEvidence.tsx` (D-052 provenance quintuple at lines 24-40). The delivery gap is removed — the accepted result no longer stays inside an internal component; it renders on both screen and report.
- **Report parity from the SAME document / calculation / evidence (F1 correction):** both the screen path (`apps/web/src/components/architect/ArchitectEntry.tsx:73`) and the report path (`apps/web/src/components/architect/ReportView.tsx:30`) a[SECOND TRUNCATION POINT]

---

## Part 3 (final fragment, verbatim; delivered 10:38:49Z — return COMPLETE)

Here is the remainder of the D-073-R003 report-parity bullet onward.

## D-073-R003 — remaining bullets

- **Report parity (F1, continued):** both the screen path (`ArchitectEntry.tsx:73`) and the report path (`ReportView.tsx:30`) apply the identical gate `evaluationIsInspectable(identityEvaluation) ? identityEvaluation : null` and feed the SAME shared `DevelopmentLimits` + `CalculationEvidence` components — structural parity, not duplicated logic, so screen and report cannot quietly disagree. Pinned by `apps/web/src/components/architect/__tests__/report-view.test.tsx`: asserts `reportValue === screenValue` (line 61) and withholds the panel on BOTH surfaces for a non-inspectable document (lines 92-102).
- **Calm presentation (F2):** the raw server `draft_label` / `reason` / `fallback_direction_note` strings are kept off the calm answer-first panel — they remain verbatim only behind the evidence disclosure in `CalculationEvidence.tsx:27-30`. The jargon-guard test (`report-view.test.tsx:110-138`; `development-limits.test.tsx`) asserts the tokens `D-045-R009`, `D-051`, `needs_review`, `within_100ft_of_wide_street`, `ZR 23-22` never reach the panel while the `3.44` result still shows.
- **Honest escalation, never a fabricated FAR:** `professional_review_required` renders "Professional review required — the higher wide-street floor-area ratio is withheld until a qualified reviewer confirms the determination.", with tests asserting no `3.44` appears in that state.
- **Contract additivity + CI:** `contract-versions.test.ts` proves a 1.0.0 doc stays valid (no block), 1.1.0 accepted with/without the block, out-of-enum rejected, malformed block fails total validation. Independent `gh api …/commits/1c89922c…/check-runs` = all 20 success.

## CONDITIONAL RESTAMP PRE-AUTHORIZATION — GRANTED

I pre-authorize restamping my verification blocks (D-045, D-066, D-073) from `reviewed_sha 1c89922c` to the seam commit `<seam_sha>`, conditional on the orchestrator reproducing, at record time, ALL of:

1. `git diff 1c89922c..<seam_sha> -- services/ apps/ packages/ docs/research/` is **empty**;
2. `git diff 1c89922c..<seam_sha> --stat` shows **only** files under `project-control/`;
3. both schema copies remain byte-identical at `<seam_sha>` (`git hash-object` still `0f2eebd6…` for `packages/contracts/schemas/v1/rule_evaluation.schema.json` and `services/api/app/_contract_schemas/v1/rule_evaluation.schema.json`).

If any condition fails, do not restamp — return for re-verification at the new head.

## Conclusion (one line)

**PASS** — all four requirements (D-045-R008, D-045-R009, D-066-R001, D-073-R003) SATISFIED on reproduced primary evidence; no prohibited action (task `awaiting_gate`, not accepted; PR #241 open; no open blocker names M5-T037); restamp pre-authorized under the three conditions above.
