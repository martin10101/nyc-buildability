# M5-T025 Directive-Compliance Verification (DCV) — independent verifier report

> Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent return
> (2026-09-14; transport entity-decoding only, per the report-preservation rule).
> Verifier ≠ producer (frontend-engineer). Read-only run in the primary checkout.

Verifier: directive-compliance-verifier (read-only; producer ≠ verifier). Landed in primary checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`; `git rev-parse --show-toplevel` = that path; HEAD = `2e2f7a1fd126f76fe5f19eebd7ea1af926d90ab6` (matches pin). Gated sha `89de37946a3ad3f8c542c03bbe70183742f048a9` exists (`git cat-file -e` OK). No writes, no git/gh state changes, no `project_control.py` write verbs were executed.

## 1. Conditional-restamp pre-authorization ruling

**PRE-AUTHORIZED, conditionally** — with one briefing correction the orchestrator must carry into the record.

**Correction to the briefing:** the intervening set is NINE commits, not five. `git log 89de3794..2e2f7a1f` = `0710125a, 0b112357, a476939c, 969f7e6e, 79b97636, a27d1e53, 02a9a70c, 668c5d48, 2e2f7a1f`. Per-commit ruling (file lists inspected via `git show --name-only`):

| Commit | Files touched | Material to M5-T025? |
|---|---|---|
| 0710125a | D-058 capture, `gates/M5-T025-G3.json`/`-G4.json`, `tasks/M5-T025.json`, `reports/M5-T025.json`, state, PROGRAM_KNOWLEDGE | No (control-plane records only; wrote the gate records themselves) |
| 0b112357 | `apps/web/src/app/property/page.tsx`, `apps/web/src/lib/rule-evaluation.ts` + its lib test, deploy checklist, M5-T026 report | **No** — M5-T026 producer; zero overlap with M5-T025 allowed_paths (`rule-evaluation.ts` is in M5-T025's *forbidden_paths*) |
| a476939c | WORKING_KNOWLEDGE, state, tasks M4-T020/M5-T025/M5-T026 | No (ledger records) |
| 969f7e6e | SESSION_HANDOFF, 2 checkpoints | No |
| 79b97636 | state.json | No |
| a27d1e53 / 02a9a70c / 668c5d48 / 2e2f7a1f | docs/WORKING_KNOWLEDGE.md only | No |

**My own diffs:** `git diff 89de3794..2e2f7a1f -- <all 9 allowed_paths>` = **empty**. Mechanical identity proof: I recomputed the CLI's own identity (`project_control._task_git_identity` → `frozen_git_identity` over allowed_paths, same exclude/control-plane prefixes) at live HEAD 2e2f7a1f: result `8fa2c7a4610cd2a7efcbdc8bb56943bf2ad167a4b1e5cf62569187b9e6a9b05d` — **byte-equal to `content_manifest_sha256` in both gate records**. Working tree clean for all material paths.

**The condition the orchestrator may cite:** *Restamp reviewed_sha 89de3794 → 2e2f7a1f is authorized iff, at record time, HEAD is still 2e2f7a1fd126f76fe5f19eebd7ea1af926d90ab6 (or any later head whose recomputed allowed_paths identity still equals 8fa2c7a4…b05d with a clean tree), the task's allowed_paths identity recomputes to exactly 8fa2c7a4610cd2a7efcbdc8bb56943bf2ad167a4b1e5cf62569187b9e6a9b05d, and no commit after 89de3794 touches any M5-T025 allowed_path.* All three limbs are verified true at 2e2f7a1f now. The four extra intervening commits (incl. the M5-T026 producer 0b112357) are disjoint peer commits per the proven identity-note pattern; additionally CI at 2e2f7a1f itself is green (20 check runs, 0 non-success — includes web + web-e2e over the identical material content coexisting with the M5-T026 change).

## 2. Per-requirement verdicts (all six applicable IDs)

Registry sweep first: `DirectiveRegistry.load().evaluate_task_refs(M5-T025)` → `ok: true`, applicable = cited = exactly the six IDs below; no missing, no unresolved, registry errors []. `python tools/validate_directive_compliance.py --check` → EXIT 0.

| requirement_id | verdict | evidence (personally inspected) | note |
|---|---|---|---|
| **D-056-R001** | **PASS** | `apps/web/src/lib/provenance-link.ts:27-46` (constant `DATASET_LANDING_PREFIX`, anchored `^[a-z0-9]{4}-[a-z0-9]{4}$`, null on invalid/absent); `ProvenanceDisclosure.tsx:80-91` and `RuleEvaluationResult.tsx:143-161` (anchor only via `datasetLandingUrl`, `target="_blank" rel="noopener noreferrer"`; `request_url` reaches only `urlHost()` text at `ProvenanceDisclosure.tsx:94`, `RuleEvaluationResult.tsx:165`); `provenance-link.test.ts:38-94` (reflected-URL/hostile rejections); `sections.test.tsx:150-231` and `rule-evaluation.test.tsx:122-169` (exact-href, invalid→no anchor honest text, absent→no row, and the required NEGATIVE hostile-request_url-never-in-any-href sweep in BOTH surfaces) | Both surfaces, constant-prefix + validated token only; honest absence preserved; harness fully present. |
| **D-056-R002** | **PASS** | Fix: `LotOutlineMap.tsx:111-124` (`runOnStyleReady`: `isStyleLoaded()` fast path + both `load`/`style.load` arms + idempotency), `:368-371` (new `error`→typed fallback), `:140-147` (`LOT_OUTLINE_MAX_ZOOM = 19.5`, padding 24); root cause stated with evidence in `LotOutlineMap.tsx:78-99` ROOT CAUSE block and producer report §R002 (line 62 ff.), both carrying `[ORCH-CORRECTED per M5-T025-G3 F1]` naming the reachable mechanism (one-time `load` never fires on degraded-GL device; no style.load arm/readiness/error surface). Regression guard: `lot-outline-map.test.tsx:385-448` (pure `runOnStyleReady` red-on-old unit rows; framing `maxZoom > 18` assertion at :445), `:464-478` (component wiring guard), `:485-503` (error→typed fallback). Display-only preserved: only coordinate math is `geometryBounds` for `fitBounds` (`:166-194`), geometry passed verbatim (`:378-386`). F1 correction commit 63495416 verified **comment/record-only** in the two web files (diff filter: zero non-comment code lines) | Concrete root cause, not a guess; guard is the strongest jsdom-expressible form; cause↔fix coherent (style.load arm + error surface). |
| **D-056-R003** | **PASS** | `LotOutlineMap.tsx:363` (`new gl.NavigationControl({ showCompass: false })`, "top-right", justification comment :359-362); `MapLike.addControl` :54; dynamic import + SSR structure unchanged (`:334-339`); fallback branches intact (`:442-527`) with tests still present for condo/no_feature/multiple_features/invalid_geometry/route_absent/network/no-WebGL (`lot-outline-map.test.tsx:283-377`); zero new dependencies: `git diff 6005f7c3..89de3794 -- package.json package-lock.json apps/web/package.json` empty; `maplibre-gl 6.7.0` present in `apps/web/package.json:18` since M5-T022 (f17a5869, 2026-09-12) | Keyboard accessibility rides on NavigationControl's native `<button>` elements (upstream; node_modules absent locally — thin client), which is within the bound harness "control present in the map init path; fallback tests stay green" — both reproduced. |
| **D-046-R001** | **PASS** | `tasks/M5-T025.json`: `worktree: "wt-m5t025"`, path_notes[0] (parallel disjoint packet while D-053 loop runs M4-T020, ceiling 2/3), progress_log 05:26 claim message; `tasks/M4-T020.json`: `worktree: "wt-m4t020"`, status claimed, allowed_paths all `services/api/**` + own report; D-056 `source-001.md#capture-context` (execution mode: loop worker + one dispatched producer = 2) at 89de3794 | Parallel production executed in isolated worktrees under the standing policy; concurrency 2 ≤ 3. |
| **D-046-R002** | **PASS** | Pairwise disjointness reproduced from packet files: M5-T025 allowed_paths (8× `apps/web/src/{components,lib}` + own report) ∩ M4-T020 (`services/api/app/connectors/dcm_street_centerline_geometry.py`, its test, own report) = ∅; ∩ M5-T026 (`apps/web/src/lib/rule-evaluation.ts`, `lib/__tests__/rule-evaluation.test.ts`, `app/property/page.tsx`, checklist doc, own report) = ∅ (note: `components/rule-evaluation/__tests__/rule-evaluation.test.tsx` ≠ `lib/__tests__/rule-evaluation.test.ts`); M5-T026 contracted 05:57, after M5-T025 producer material 10aaedcc landed; producer commit 10aaedcc touched exactly the 9 allowed files (verified `git show --name-only`) | No concurrent writers with overlapping scope; shared-surface integration was sequential (orchestrator commits). |
| **D-040-R001** | **PASS** | `.claude/rules/expansion-agent-dispatch-hold.md` §2.1 at `git show 89de3794:` — scoped release recorded citing `D-040:D-040-R001`, everything else SUSPENDED; M5-T025 lot-outline edits confined to `LotOutlineMap.tsx` on the address confirm card using MapLibre GL JS (inside the released increment; 3d-ui-expansion.md item 5); no expansion-pack task IDs anywhere (ledger `M<x>-T<n>` only); producer diff contains no 3D-massing/pack/GDS work; task `directive_refs` cite `D-040:D-040-R001` | Work sits squarely inside the carve-out; the hold on everything else is undisturbed. |

## 3. Material-identity statement (my own result)

`git diff 89de37946a3ad3f8c542c03bbe70183742f048a9..2e2f7a1fd126f76fe5f19eebd7ea1af926d90ab6 -- <all nine M5-T025 allowed_paths>` = **empty**; working tree clean on those paths; recomputed CLI content identity at live HEAD = `8fa2c7a4610cd2a7efcbdc8bb56943bf2ad167a4b1e5cf62569187b9e6a9b05d`, byte-equal to `content_manifest_sha256` in `project-control/gates/M5-T025-G3.json:9` and `M5-T025-G4.json:9` (both `reviewed_sha` = 89de3794, both PASS, reviewers code-reviewer / qa-engineer ≠ producer frontend-engineer).

Supporting evidence reproduced: CI **green at all three relevant heads** via `gh api .../check-runs`: 10aaedcc (20/20 success — briefing said 18/18; actual count is 20 check runs, benign counting difference), f5e7f4a1 (20/20), and live head 2e2f7a1f (20/20, 0 non-success). Validator EXIT 0 at live head. D-056 `verification.json` is a correctly unstamped v2 skeleton (`task_verifications: []`, `verified_by: null`) — nothing pre-stamped by a producer. Task status `awaiting_gate`; nothing merged/accepted/dispatched/deployed on this packet.

## 4. Blocking discrepancies

**None blocking.** Two record notes for the orchestrator (non-gating):
1. The acceptance record should list the full nine-commit intervening set (incl. 0710125a, 0b112357, a476939c, 969f7e6e), not the five in my briefing, and carry the standard disjoint-peer identity note for 0b112357 (M5-T026 producer touching apps/web outside — and partly inside the *forbidden_paths* of — M5-T025's scope).
2. D-056-R003 keyboard accessibility rests on maplibre-gl's native-button NavigationControl implementation (not independently executable here — thin client, no node_modules); the bound harness terms are fully met and G3/G4 reviewed it, so this is a residual observation only.

## VERDICT: **PASS** — all six applicable requirement IDs SATISFIED at the gated identity, identity carries to 2e2f7a1f, and the conditional restamp is pre-authorized on the condition stated in Section 1.
