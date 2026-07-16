# M0-T011 Producer Report — ADR-004: Frontend Hosting on Render (drop Vercel)

- **Task:** M0-T011 | **Producer:** cloud-architect | **Date:** 2026-07-16
- **Status requested:** `awaiting_gate` (G3 by code-reviewer; producer may not accept own work)
- **Worktree/scope:** main checkout, docs/config-only, per task packet `allowed_paths`
- **Execution location / disk:** owner PC, text edits only; no installs, no datasets, no account operations, no purchases; net repo growth < 25 KB (low-storage policy respected)

## Decision summary

ADR-004 (status **Accepted** — owner decision 2026-07-14, recorded per PRD §34) serves the Next.js frontend from a Render **web service** `nycdf-web` (`runtime: node`, `rootDir: apps/web`) and drops Vercel entirely. The frontend inherits the accepted M0-T006 deploy model byte-for-byte in spirit: production `autoDeployTrigger: "off"` (quoted), deploys only via secret deploy hook from the future D5 Actions workflow after migrations + human approval; staging auto-deploys from `main`; rollback via Render deploy rollback (no rebuild). Preview strategy: **no previews initially** (option c), re-evaluate frontend-only service previews (option b) at M2, Pro-gated preview environments (option a) only with an owner-approved plan upgrade. PRD §14.1 deviation explicitly documented.

## Files changed

1. `docs/adr/ADR-004-frontend-hosting-render.md` — NEW. Decision, trade-off table (edge network + free previews lost; single-platform ops gained; SSR equivalent via Render web service), preview strategy with cost basis, PRD deviation record, consequences, rollback-to-Vercel path, sources. Every Render claim cites `docs/research/render-nextjs-previews-2026-07-16.md` (§1/§2/§3) or an official URL it captures.
2. `docs/adr/ADR-001-cloud-architecture.md` — amended per M0-T006 G3 amendment map: title, date note, context bullet, decision-table frontend row, Consequences (PRD-deviation bullet, two-dashboards bullet, secret-stores bullet), sources (Vercel row marked superseded; research-file row added). **R1 residual (a) applied:** rule 5 service-role wording now "Render secret stores only... not duplicated to GitHub Actions secrets" (matches ADR-002 §3).
3. `docs/adr/ADR-002-environment-separation.md` — amended per map: date note; Vercel context bullet marked superseded; mapping-table Vercel column replaced (all three rows → Render frontend web service); secret table (anon-key row → `nycdf-web` env vars; deploy-hook row extended to frontend; `VERCEL_*` row struck with visible removal note); promotion rules 1–3; cost sequencing (start ≈ $0 unchanged; launch prep now includes `nycdf-web` starter instance); verification item 3 withdrawn and replaced with service-previews verification; sources annotated + research file added.
4. `docs/adr/ADR-003-deployment-and-rollback.md` — amended per map: date note; context sentence; **D1 replaced in full** (Render web service, deploy-hook model identical to D2; explicit note that no `vercel.json`/`VERCEL_*` secrets are created); D4 "(Render/Vercel)" → "(Render)"; D5 `deploy-vercel` job removed (frontend folded into `deploy-render`); failed-migration step 1 (quoted `"off"`, frontend included); **R1 replaced in full** (Render web-service rollback, R2 semantics govern); decision-matrix rows 1 and 4; consequences env-var bullet; sources (4 Vercel rows marked superseded; research file added).
5. `render.yaml` — (a) R1 residual (b): all three existing `autoDeployTrigger: off` → `"off"` (quoted); (b) DEPLOY TRIGGER POLICY comment updated with the quoting rationale + ADR-004; (c) header comment references ADR-004; (d) **additive** service 4: `nycdf-web` (web/node/`apps/web`, plan starter with cost-sequencing note, region oregon, `autoDeployTrigger: "off"` quoted, `buildCommand: "npm ci && npm run build"`, `startCommand: "npm run start"`, `healthCheckPath: /`, env vars `NEXT_PUBLIC_SUPABASE_URL`/`NEXT_PUBLIC_SUPABASE_ANON_KEY` as `sync: false`, publishable-only comment per PRD 17). No other change to the API/worker/cron definitions (verified by git diff — see S2).
6. `docs/DEPLOYMENT_AND_ROLLBACK.md` — header amendment note; §0 environment map frontend column + deploy order (frontend = Render deploy hook, deployed after API); §1.1 step 3–4; §1.2 step 4 (Vercel CLI removed; frontend via deploy hook); §1.3; **§2.1 replaced** (Render rollback of `nycdf-web`, mirrors §2.2, Actions-gated model preserved).
7. `README.md` — deployment summary lines only: `apps/web` deploy target → "Render web service (ADR-004; Vercel dropped 2026-07-14)"; remote-first bullet → all app deployments on Render.
8. `project-control/reports/M0-T011-producer-report.md` — this report.

## Preview strategy (decision + cost basis, from the research file only)

- (a) Multi-service preview environments: **"Preview environments require a Pro plan or higher"**; "Preview resources are billed just like regular Render services and are prorated by the second"; cost controls `previews.plan`/`numInstances`/`expireAfterDays`; `sync: false` env vars NOT copied to previews (research file §2). Exact Pro pricing NOT captured — must be read from https://render.com/pricing by the owner before any upgrade.
- (b) Frontend-only service previews: documented at https://render.com/docs/service-previews (research file §2 pointer). Plan-gating/billing **not captured — flagged for verification before enablement** (now ADR-002 verification item 3 replacement).
- (c) No previews initially: $0; CI + staging verification covers PR review while `apps/web` is a placeholder.
- **Recommendation adopted: (c)**, re-evaluate (b) at M2. **HUMAN ACTION flag in ADR-004:** any preview enablement is an owner billing decision; nothing paid was enabled or purchased in this task. The existing Blueprint `previews.generation: manual` block is unchanged and — being Pro-gated — creates and bills nothing on the current plan.

## Scenario evidence

### S1 (normal) — ADR-004 content
- Decision matches owner directive: ADR-004 "Decision" §1 ("served from a Render web service... Vercel is dropped"); status "Accepted (owner decision 2026-07-14)".
- Citation discipline: ADR-004 "Evidence base" header; every Render claim carries "research file §N" and/or the official URL + retrieval date; Vercel-side facts cite prior ADR source tables. Deliberately uncited claims are declared as such (edge/CDN row: "No equivalent claim made... research file (absence)"; service previews: "unverified for plan/cost").
- Preview strategy: dedicated section, all three options evaluated with cost basis, explicit decision (c), billing flagged as human action. **PASS (producer self-check).**

### S2 (boundary) — render.yaml
- Command run (exact):
  `python -c "import yaml,io; d=yaml.safe_load(io.open(r'C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\render.yaml', encoding='utf-8')); svcs=d['services']; print('parse: OK'); print('service count:', len(svcs)); [print('-', s['type'], s['name'], '| autoDeployTrigger =', repr(s.get('autoDeployTrigger')), '| runtime =', s.get('runtime')) for s in svcs]; print('previews:', d.get('previews'))"`
- Actual output:
  ```
  parse: OK
  service count: 4
  - web nycdf-api | autoDeployTrigger = 'off' | runtime = python
  - worker nycdf-worker-jobs | autoDeployTrigger = 'off' | runtime = python
  - cron nycdf-cron-source-monitor | autoDeployTrigger = 'off' | runtime = python
  - web nycdf-web | autoDeployTrigger = 'off' | runtime = node
  previews: {'generation': 'manual', 'expireAfterDays': 3}
  ```
  All four `autoDeployTrigger` values now parse as the STRING `'off'` (before the quoting fix, bare `off` parsed as YAML-1.1 boolean `False`).
- Additivity: `git diff render.yaml` shows changes to the existing three services limited to exactly the three `autoDeployTrigger: off` → `"off"` quotings (the amendment-map/R1 residual) plus header/policy comment lines; the `nycdf-web` block is appended after the cron service (diff hunk `@@ -168,3 +176,60 @@` is pure addition). `previews` block and staging/production split unchanged. **PASS.**

### S3 (missing) — cross-references
- Amendment map applied at every location listed in `project-control/reports/M0-T006-G3-verification.md` §"ADR-004 amendment-feasibility assessment" (details per file above), including both R1 residuals: (a) ADR-001 rule 5 service-role → Render only; (b) `"off"` quoted everywhere (render.yaml values + ADR-002/003 prose now show `autoDeployTrigger: "off"`).
- Dangling-reference audit (Grep `[Vv]ercel` over `docs/adr/`, `docs/DEPLOYMENT_AND_ROLLBACK.md`, `README.md`, `render.yaml`): every remaining match is (i) inside ADR-004 itself (the decision/trade-off/rollback-path record), (ii) explicitly annotated "superseded/withdrawn/removed ... per ADR-004", or (iii) the phrase "Vercel dropped". No operative instruction anywhere still targets Vercel. **PASS**, with two OUT-OF-SCOPE residuals disclosed in "Limitations".

### S4 (conflict) — deployment-model consistency
- Frontend production gating is textually identical to the backend's: `autoDeployTrigger: "off"` + secret deploy hook from the D5 workflow after migrations/checks/human approval (ADR-003 D1-as-amended vs D2; render.yaml policy comment covers "every production service"; ADR-002 mapping-table prod row; runbook §0/§1.2).
- Runbook order updated coherently: "1) migrations, 2) Render API/worker/cron, 3) Render frontend"; failed-migration halt text (ADR-003 R3 step 1, runbook §2.5 step 1) says "trigger no deploy hook — frontend included"; no text anywhere claims a platform-side halt (the D5 `needs:` chain remains the stated only mechanism — the M0-T006 Defect-1 resolution is preserved, not weakened).
- Frontend rollback documented: runbook §2.1 (Render rollback of `nycdf-web`, mirrors §2.2), ADR-003 R1-as-amended, ADR-004 consequences + trade-off row. **PASS.**

### S5 (regression) — B-003 closure
- ADR-004 "Consequences" states: "B-003 (Vercel account) can be closed: this ADR supersedes the Vercel plan (orchestrator action after acceptance)"; the rollback-path section defines how B-003 would be reopened if the decision is ever reversed.
- PRD deviation: dedicated "PRD deviation (explicit)" section — PRD §14.1 names Vercel; owner-approved deviation of 2026-07-14 recorded per PRD §34; ADR-001 Consequences bullet updated from "no deviation to document" to the documented-deviation wording. **PASS.** (Actual B-003 closure and `docs/HUMAN_ACTIONS_REQUIRED.md` §3 update are orchestrator actions after G3 acceptance — that file was not in my allowed paths.)

## Commands run (complete)

1. Reads of all task inputs (task packet, research file, G3 report, ADR-001/002/003/005, render.yaml, runbook, README, HUMAN_ACTIONS_REQUIRED §3, apps/web/package.json + .env.example + next.config.ts — reads only for the forbidden-path files).
2. `python -c "import yaml, ..."` YAML validation — output above (S2).
3. `git diff --stat` and `git diff render.yaml` — additivity evidence (S2): 6 files changed, 151 insertions(+), 83 deletions(-); render.yaml existing-service hunks are the three quotings + comments only.
4. Grep `[Vv]ercel` audits over in-scope files (S3) and read-only over `docs/SECRETS_POLICY.md` (residual disclosure).

## Assumptions and defaults

1. `nycdf-web` name follows the ADR-002 convention (`nycdf-<service>`; staging copy `nycdf-web-staging` at instantiation). No Render account operation performed; the Blueprint is declaration only.
2. `npm ci && npm run build` / `npm run start` mirror the official guide's yarn commands ("npm equivalents fine" — research file §1) against the committed `apps/web/package.json` scripts (`next build`/`next start`) and committed `package-lock.json`. `apps/web` was NOT modified.
3. `healthCheckPath: /` uses the Next.js root page as the health endpoint (same official health-check source as the API service). If the frontend later needs a dedicated endpoint, that is an `apps/web` task.
4. `plan: starter` declares the launch target (free web services spin down after 15 min — cited); ADR-002 §6 cost sequencing controls when it is actually activated. Nothing deploys or bills from this task.
5. PRD text itself is not edited (not in allowed paths); ADR-004 is the deviation record, which PRD §34 permits.

## Limitations / residuals (disclosed, out of my allowed paths)

1. **docs/SECRETS_POLICY.md** (forbidden path) still contains six Vercel rows/lines (L18, L20, L21, L26, L27, L44, L53): `VERCEL_TOKEN`/`VERCEL_ORG_ID`/`VERCEL_PROJECT_ID` rows and anon-key/frontend-config wording pointing at Vercel env vars. Needs a follow-up task (or orchestrator edit) to re-point the frontend rows at Render `nycdf-web` env vars and strike the `VERCEL_*` rows per ADR-004.
2. **apps/web/.env.example** (forbidden path) header comment says values "live ONLY in Vercel env vars" — needs a one-line follow-up edit in an apps/web-scoped task.
3. **docs/HUMAN_ACTIONS_REQUIRED.md §3 / B-003** — closure is an orchestrator action after acceptance (per task packet); file untouched.
4. Render **service previews** plan-gating/billing is unverified (not captured in the research file) — recorded inside ADR-004 and as the replacement ADR-002 verification item 3; must be verified against https://render.com/docs/service-previews before any enablement.
5. Exact Render Pro plan pricing not stated anywhere (not captured); owner reads https://render.com/pricing before any upgrade decision.
6. The summarizer-mediated nature of the research capture is disclosed in the research file itself; ADR-004 inherits that caveat and re-verification pointer.

## Security / provenance impact

- No secrets created, read, or moved. New frontend service declares only publishable `NEXT_PUBLIC_*` env vars as `sync: false` references with an explicit PRD-17 never-privileged comment. Three CI secrets (`VERCEL_*`) are removed from the plan before ever being created. Service-role wording tightened (ADR-001 rule 5) reduces credential surface.
- Provenance: superseded Vercel source rows retained with markers rather than deleted; all new claims dated and traced to the orchestrator-captured research file.

## Risks / recommended next tasks

1. Follow-up task: SECRETS_POLICY.md + apps/web/.env.example Vercel-reference cleanup (small, doc-only; see Limitations 1–2).
2. D5 production deploy workflow (already a tracked follow-up from M0-T006) now needs one fewer job (`deploy-vercel` removed) — note for its task packet.
3. At M2: re-evaluate preview option (b) with a fresh capture of /docs/service-previews.

**Report path:** `project-control/reports/M0-T011-producer-report.md`
