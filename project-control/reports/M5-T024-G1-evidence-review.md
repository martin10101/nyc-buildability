# G1 GATE REPORT — M5-T024

> Preservation note: saved VERBATIM by the orchestrator from the reviewer's agent-return channel
> (transport entity-decoding only). Reviewer: independent code-reviewer agent.

**Task:** M5-T024 — D-043 internal web deploy: owner-executed Render service settings + env-var checklist
**Producer:** cloud-architect · **Reviewer (G1, this report):** independent, read-only
**Material commit:** `0002ddb7` on `candidate/D-024-mrl-option-b`
**Deliverables reviewed:** `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md`, `project-control/reports/M5-T024-producer-report.md`

## VERDICT: PASS with one BLOCKING required correction (RC-1)

The deliverable is accurate, complete, and privacy-clean on all deploy-critical settings, ordering, and scope. One correctness defect in the owner verification script (§9 step 2) must be fixed before acceptance: the "address flow" step is unreachable as written. Recorded per this repo's convention as PASS-with-required-corrections; RC-1 is BLOCKING for acceptance and any next gate.

## Frozen-SHA / identity check

`git diff 0002ddb7..HEAD --stat` = only `project-control/state.json` and `project-control/tasks/M5-T024.json` (control-plane lifecycle). Both deliverable files are byte-identical at `0002ddb7` and HEAD `b5082120`, so working-tree review == reviewed content. `git show 0002ddb7 --stat`: the two allowed files plus the orchestrator-assembled `M5-T024-evidence-map.json` (header `"assembled_by":"orchestrator"` — orchestrator artifact, not a producer scope breach). No forbidden path touched; `render.yaml` untouched.

## Pre-gate question — RESOLVED: §9 step 2 is UNREACHABLE as written → DEFECT

I verified the two-factor gate directly in source:
- `apps/web/src/lib/rule-evaluation.ts:96-103` — `ruleEvaluationSurfaceEnabled` returns false unless BOTH the env flag (`ruleEvaluationFlagEnabled`, line 99) AND an explicit `?ruleeval` true-token (lines 101-102) hold.
- `apps/web/src/app/property/page.tsx:30` passes that boolean to `PropertyLookup`.
- `apps/web/src/components/property/PropertyLookup.tsx:265` — `{ruleEvalEnabled ? <AddressResolutionScreen /> : null}`. Grep confirms this is the ONLY mount of `AddressResolutionScreen` in app code (all other hits are tests).
- `apps/web/src/app/page.tsx:19` links to `/property` (no `?ruleeval`); default `/property` renders only the BBL numeric lookup form (PropertyLookup.tsx:284-296), NOT an address field.

Consequently the address flow renders ONLY at `/property?ruleeval=on` (with the env flag on). Checklist §9 tells the owner to "Do the steps in the printed order" (line 11); step 2 (line 250-253, "enter a real NYC address in the address flow") comes BEFORE step 3 (line 255), which is where `?ruleeval=on` is first introduced. Following the order, at step 2 the owner is on the plain `/property` page with no address field and cannot perform the step — and would likely misread the missing address UI as a broken deploy. This is exactly the harness D-043-R001 requires ("flag-on address flow resolves a real address end-to-end") so the defect strikes the checklist's core verification value.

Consistency of the §2.1/§9.3 opt-in explanation: §2 step 1 (lines 122-123) and §9 step 3 (lines 255-259) describe `?ruleeval=on` as gating "the internal surface" / "the draft rule-evaluation surface" only. They never state that the SAME `ruleEvalEnabled` gate also controls the address front door (AddressResolutionScreen). So the checklist's mental model treats the address flow as independent of the opt-in, which contradicts the code. The fix must make both explicit.

## Per-scenario findings

### S1 completeness_and_order — PASS (subject to RC-1 in the §9 verification script)
- Service settings all present with exact values: repo `nyc-buildability` (§1.1), branch `candidate/D-024-mrl-option-b` with "not main" reason (§1.2), root `apps/web` (§1.3), runtime Node (§1.4), Node 22 (§1.5), build `npm ci && npm run build` (§1.6), start `npm run start` + `$PORT` note (§1.7), plan tradeoff left to owner (§1.8), region `oregon` (§1.9), health `/` (§1.10). All cross-checked below.
- Dependency ordering enforced: env-vars-before-build (§2 → §3, with the rebuild-on-change rule stated at §2 step 2 and §3); web-origin-before-CORS (§4 → §5). Both load-bearing orderings are also called out inline at lines 11-13.
- Both services covered: web (§2: `INTERNAL_RULE_EVAL_ENABLED`, `NEXT_PUBLIC_API_BASE_URL`, blank Supabase) and `nycdf-api` (§5: `API_CORS_ALLOWED_ORIGINS`, `INTERNAL_RULE_EVAL_ENABLED`).
- Auto Sync = No folded in (§7); M5-T019 stale-flag-name check folded in (§10).
- Zero agent dashboard steps: preamble (lines 5-9) and every step are owner-performed; no agent action anywhere (R003).

### S2 privacy_grep — PASS (reproduced independently)
My own grep over both files: only http(s) URL literal is `http://127.0.0.1` (checklist line 127; report lines 41,52) — the documented local default from `apps/web/.env.example:29` and `apps/web/src/lib/api.ts:153`, not a service URL or secret. Zero `onrender.com` hosts (the only "onrender" strings are the report describing its own clean grep). Zero keys/tokens/secrets — every "secret" match is the honest "not secret-proof"/"unlisted is not secret" framing. Private API URL appears only as `<owner-pastes-private-API-URL>` (§0 table, §2 step 2). D-043-R002 satisfied by construction.

### S3 technical_accuracy — PASS (every material claim verified against its cited source)
- Flag name `INTERNAL_RULE_EVAL_ENABLED` — `rule-evaluation.ts:83`; true tokens `1/true/yes/on` — line 79; server-read (not NEXT_PUBLIC) — lines 60-65,82; two-factor gate — lines 54-77,96-103. All exact.
- CORS semantics — `services/api/app/main.py`: exact comma-separated origins and "unset/empty = no cross-origin access" (docstring lines 15-19); `_parse_allowed_origins` at lines 66-82 raises `RuntimeError` on any `*` (lines 77-81); applied in `create_app` at line 87 and `allow_origins` at line 103. Checklist's cited line numbers (66-82, 18-19, 74; provenance table 15-23,66-82,87,103) all check out.
- Build/start + `$PORT` — `apps/web/package.json:8-9` (`build`=`next build`, `start`=`next start`); matches the recovered prior `nycdf-web` block (`git show 23817a9f~1:render.yaml`: `buildCommand: "npm ci && npm run build"`, `startCommand: "npm run start"`, `runtime: node`, `rootDir: apps/web`, `plan: starter`, `region: oregon`, `healthCheckPath: /`). `$PORT` handling correctly described (Next honors `PORT`; explicit `-- -p $PORT` offered, flagged for UI confirm).
- Node 22 — `.github/workflows/ci.yml` has `node-version: 22` at lines 32, 69, 137 (checklist's "three setup-node steps" is exact); `apps/web/package.json` has no `engines` field (confirmed). The exact Render mechanism is honestly marked `[confirm in the dashboard UI — not evidenced in the repo]` rather than guessed (principle 3 respected).
- NEXT_PUBLIC build-time inlining — `apps/web/.env.example:6-8,27-35` and `docs/DEPLOYMENT_AND_ROLLBACK.md §1.3`; browser cross-origin default `http://127.0.0.1:8000` — `api.ts:152-154` (function is 152-154; docstring 146-151 — citation "147-154" is off by ~1 at the start, immaterial), `address-api.ts` confirms it calls `GET /api/v1/address-resolution`.
- Provenance summary table (lines 288-301) maps every material claim to a source. No guessed schema, unit, or effective date anywhere.

### S4 honest_exposure_and_scope — PASS
- No-auth reachability stated plainly: §0 bullet (lines 30-33) and §6 (lines 197-210), cited to `services/api/app/main.py` docstring lines 6-11 (verified) and `docs/MVP_AGENDA.md §I`. "Unlisted is not secret" is explicit (§6 lines 202-205).
- NOT a public launch: §0 line 28; whole-file scan for `robots|sitemap|index|marketing|SEO|publicly list|go public` returns only the checklist's own "NOT a public launch" sentence. No listing/marketing/indexing step exists (R004).
- render.yaml restoration debt + duplicate-service caution recorded as owed-not-performed (§8), linked to Auto Sync = No (§7); `render.yaml` untouched (diff confirms). Matches the live `render.yaml` note block "3) … WITHHELD" (lines 156-168).

## Directive prohibitions bound to this task
- **D-043-R002 (privacy) — PASS.** Verified independently above (S2). Placeholders only; §2 step 2 instructs the value is pasted in the dashboard only, never a repo file/commit/chat.
- **D-043-R004 (no public launch) — PASS.** No listing/marketing/indexing anywhere; internal/dev posture preserved; restoration debt recorded not performed.
(Formal per-requirement R001–R004 verification is the independent `directive-compliance-verifier`'s pass; from a G1 evidence standpoint, note that R001's required harness — "flag-on address flow resolves a real address" — is precisely the step RC-1 corrects.)

## Required corrections

**RC-1 (BLOCKING) — §9 step 2 address-flow reachability.** The address flow (`AddressResolutionScreen`) renders only at `/property?ruleeval=on` with the env flag on (verified: `rule-evaluation.ts:96-103` two-factor gate → `PropertyLookup.tsx:265`). As printed, step 2 precedes the `?ruleeval=on` introduction in step 3, so the owner cannot perform it and may mistake the absent address UI for a broken deploy. Correct §9 so the address-resolution step explicitly uses `/property?ruleeval=on` (or reorder so the `?ruleeval=on` opt-in precedes/covers it), AND update the §2 step 1 / §9 step 3 opt-in explanation to state that `?ruleeval=on` gates BOTH the address front door and the draft rule-evaluation surface (the same `ruleEvalEnabled` gate) — not the rule-eval surface alone. Docs-only fix, confined to `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` (in scope).

## Advisory notes (non-blocking; not task defects)
- **A-1 (out of scope).** `apps/web/src/app/property/page.tsx:22` docstring ("a per-request `?ruleeval=off` acts only as a fail-safe kill switch") is stale versus the code: `?ruleeval` is a positive opt-in (must be a true token to enable), not merely an off switch. `page.tsx` is a forbidden path for this task — record for a future apps/web change; do not fix here.
- **A-2 (out of scope).** `apps/web/src/.env.example:33-34` references `docs/DEPLOYMENT_AND_ROLLBACK.md` "sections 0.1 and 1.3", but section 0.1 does not exist at this SHA (producer flagged this correctly and cited only the existing §1.3; the checklist wisely avoids citing 0.1). Pre-existing repo inconsistency in a forbidden file.
- **A-3.** `api.ts` citation "lines 147-154" starts ~1 line early (function is 152-154). Immaterial; no action needed.

## Notes on evidence I could not fully self-execute
None. All checks (git diff/show, greps, source reads) executed successfully in this sandbox; no orchestrator-captured evidence was required.

**Recommendation to orchestrator:** record G1 = PASS with RC-1 as a BLOCKING condition (via `progress --message`); do not dispatch the next gate or accept M5-T024 until RC-1 is applied to `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md`, re-verified, and committed.
