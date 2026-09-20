# M5-T056 DCV — directive-compliance verification (saved VERBATIM from the verifier return; this header line is the orchestrator's)

I have complete primary evidence for all four applicable requirements. The CI run at the frozen-tree-equivalent head (bd408ab9, byte-stable material) shows `web-e2e (vitest): success`, `web: success`, `api: success`, `modularity: success`. Task is `awaiting_gate` (progress 85), not accepted — no prohibited action.

---

# DIRECTIVE-COMPLIANCE VERIFICATION — M5-T056 (DB-036 condo-surface rider cluster)

**Verdict: PASS** (all 4 applicable requirements SATISFIED on reproduced primary evidence)

Reviewer: directive-compliance-verifier (read-only; producer ≠ verifier). Repo `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch `candidate/D-024-mrl-option-b`.

## Identity / integrity (reproduced)

- **Applicable == cited:** `evaluate_task_refs(M5-T056)` → `ok:true`, applicable = cited = `[D-066-R001, D-073-R006, D-077-R002, D-077-R003]`, `missing_ids:[]`, `invalid_refs:[]`.
- **Validator:** `python tools/validate_directive_compliance.py --check` → **exit 0**.
- **Frozen material byte-stability:** `git diff db0cf0f8..HEAD` over the 8 material files + evidence map → **empty (exit 0)**. Live head advanced db0cf0f8 → bd408ab9 → **83e9cbcf** during review; the only new commit past bd408ab9 is `83e9cbcf` (M5-T055 review-wave — a disjoint T055 peer). Material stays byte-stable at 83e9cbcf; working tree clean for material files.
- **Material commit `5b7b4b30`:** touches exactly 8 files (7 code/test + report), **zero forbidden paths**. Old-blobs at `5b7b4b30^` and new-blobs at db0cf0f8 both match the report's `<old>→<new>` bindings (e.g. condo-records.ts `020255b0→35abf328`, PropertyOverview.tsx `4a82771e→3d61696b`, condo_records.py `b21e34fd→73d4e504`). `ReportView.tsx` (permitted) not in the commit — confirms the report's "unchanged" claim.
- **CI at bd408ab9 (run 35494571792): success**, jobs include `web-e2e (vitest…): success`, `web (lint+typecheck+build): success`, `api (ruff+pytest): success`, `modularity: success`. The T056 web/api test files are byte-stable in that tree, so this run covers the T056 suites.
- **No prohibited action:** T056 `status=awaiting_gate`, progress 85; no G2–G5/accept records; not merged/deployed.

## Per-requirement rulings

### D-066-R001 — code-graph nav block at the contract seam — **SATISFIED**
- **Nav block present:** `tasks/M5-T056.json` inputs[3] = "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this contract seam)" naming the condo-records.ts consumer set, PropertyOverview consumer set, `condo_records.py` mount, and `bbl.ts` read-only; instructs `python tools/code_graph/query.py --no-regen impact <path>` before sweeps; "the graph is ADVISORY - verify in source."
- **Source-accuracy of nav claims (reproduced):** `PropertyOverview.tsx:18` and `ReportView.tsx:12` both `import … from "@/lib/condo-records"`; `main.py:32` imports `condo_records` router, `:175` `include_router`. `validateBblInput` exists at `bbl.ts:36` (the read-only target).
- **Producer honored it:** `bbl.ts`/`bounded.ts` byte-unchanged (empty diff db0cf0f8..HEAD); `deriveCondoSurface` (PropertyOverview.tsx:197) and `CondoRecordsChannelSection({decision})` signatures unchanged (props stable); ReportView.tsx not modified.
- **G0.md** attests regen at seam. Both evidence-map bullets reproduced. (The regen *action* itself is orchestrator-attested, not independently re-runnable, but the nav-block content is source-accurate — the required harness/evidence, "nav block present + producer prompt cites query.py," is met.)

### D-073-R006 — records vs calculated allowances; honest gating — **SATISFIED**
Primary evidence = `PropertyOverview.tsx` diff (5b7b4b30) + tests + `condo-records.ts`:
- **Records ≠ allowances:** records section labeled "City records for this condo … shown for reference **under the development limits above**"; comment "the professional-review fail-safe above governs; these are city records, shown for reference."
- **Entered vs billing honesty (b):** distinct `condo-entered-lot` / `condo-billing-lot` labels; `billingLot` renders the BBL only when `billingBblStatus==="recorded"`, else "not recorded (unknown)" — never the entered unit BBL relabelled. `condo-records.ts` parses `entered_bbl` via read-only `validateBblInput` (→null on malformed), plus `billingBblStatus`.
- **Zoning gating (e):** divergent notice gated `anyZoningRecorded && divergentZoningNotice`; ZTLDB gap note gated `anyZoningUnknown && recordedZoningDependency`; scope-aware copy. `condo-records.ts` parses `recorded_zoning_status` (honest fallback) + `recorded_zoning_dependency`.
- **Tests reproduce it** (condo-resolution-display.test.tsx DB-036 block): unit input never under billing label; no-zoning → `queryByTestId("condo-divergent-notice")` null + ZTLDB gap; mixed → divergent + partial gap "recorded districts shown above are unaffected"; exact `retrieved: 2026-09-01T14:05:56Z` value pin.
- **T052 guard preserved:** `deriveCondoSurface` unmodified (line 197, before the 225–280 hunks); new render locals are derivations, not a second decision. `boundedToken` charset untouched (bounded.ts empty diff); DB-036(a) preserved. CI `web-e2e` success covers these.

### D-077-R002 — three disjoint loop lanes, full contract drill (lane-3) — **SATISFIED**
- **Contract/claim seams reproduced:** `29c5bc0b` (D-077 three-lane contract); **G0 PASS** `gates/M5-T056-G0.json` (`result:PASS`, `reviewed_sha:29c5bc0b`); claim seams `455e598e` + `92b0d265` (claimed frontend-engineer, FULL worktree path `wt-m5t056`, progress 20). Harvest `7a10fb05` exists on-branch; integration `5b7b4b30`.
- **Pairwise disjointness:** `M5-T056-G0.md` — T056∩T054=∅, T056∩T055=∅ (api split file-exact: T056 holds `condo_records.py` only).
- **In-worktree self-checks:** producer report §10/§13 + orchestrator appendix: ruff clean, `tests/api` 501 passed, modularity exit 0; CI `api` job success at bd408ab9. (Prior wrong-cwd exit-1/exit-4 results are correctly preserved as command-routing artifacts, not code failures.)

### D-077-R003 — released, non-held MVP scope; (a)/(d) preserved OPEN — **SATISFIED**
- **Released scope:** DB-036 rider cluster is a named released lane in D-077 source-001. Packet objective: "NOT in scope: DB-036(a) slash-district sanitizer … and DB-036(d) coupling decision."
- **(a)/(d) preserved OPEN:** boundedToken charset untouched (bounded.ts empty diff); `condo-records.ts` §9 + tests confirm timestamps stay `boundedTimestamp`; report §14 routes (a) to the future zoning-propagation packet, (d) to substrate-substitution.
- **No held surface touched:** only 8 allowed-path files; forbidden paths (`address/`, `bbl.ts`, `bounded.ts`, `e2e/`, `connectors/`, `rules/`, `scenario/`, `contracts/`) all clean. G0.md confirms (a)/(d) preserved and forbidden pins.

## RESTAMP PRE-AUTHORIZATION (stated up front)

I authorize the orchestrator to restamp `verification.json` for D-066-R001, D-073-R006, D-077-R002, D-077-R003 to a restamp-target head **AT or PAST** the current HEAD (83e9cbcf) on this branch, **conditioned on all of**:
1. **Path-scoped content identity unchanged:** the 8 material files + `M5-T056-evidence-map.json` byte-identical to db0cf0f8 (blobs: condo-records.ts `35abf328…`, PropertyOverview.tsx `3d61696b…`, condo-records.test.ts `84bb4218…`, condo-resolution-display.test.tsx `cb6d134d…`, report-view.test.tsx `5eddbe73…`, condo_records.py `73d4e504…`, test_condo_records_api.py `2f004119…`). `git diff <restamp-head> -- <those paths>` MUST be empty.
2. `reviewed_manifest_sha256` carried from the recorded gate records for this task (not recomputed by the producer).
3. `validate_directive_compliance.py --check` exit 0 AND `evaluate_task_refs(M5-T056)` applicable==cited at the restamp head.

**Disjoint-peer tolerance (explicit):** disjoint peer commits landing between freeze and restamp DO NOT void this authorization, specifically — (a) the **T055 lane** (address web files + responsive-a11y CLS spec, including `[ORCH-CORRECTED]` commit `05f1aea2`) and any **T055 acceptance-seam** commits; (b) the **T057 lane** (api proposal-check route files); (c) the already-landed T055 review-wave commit `83e9cbcf`. None of these touch any of the 8 T056 material files (verified: diff empty at 83e9cbcf), so any of them landing before the restamp is tolerated. Any change to a T056 material file voids this and requires re-review.

**Overall: PASS.**
