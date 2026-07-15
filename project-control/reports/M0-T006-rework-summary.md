# M0-T006 Rework Summary — 2026-07-15

- Task: M0-T006 "ADRs + Render Blueprint + deploy/rollback procedures" (G3 FAIL → rework)
- Producer: cloud-architect | Requested status: awaiting_gate (G3 re-review)
- Directive: owner rework directive 2026-07-15 (binding); platform facts sourced exclusively from `docs/research/deploy-trigger-gating-2026-07-15.md` (official URLs, retrieved 2026-07-15)
- Companion detail: "Rework 2026-07-15" section appended to `project-control/reports/M0-T006-producer-report.md`

## Defect → files/lines changed

| Defect | File | Change (locations are post-edit) |
|---|---|---|
| 1 (HIGH) deploy-trigger contradiction | `render.yaml` | New "DEPLOY TRIGGER POLICY" header block (L25-43); `autoDeploy: true` → `autoDeployTrigger: off` on web (L71-73) and worker (L114-116); `autoDeployTrigger: off` ADDED to cron (L152-155, previously omitted → default `commit`) |
| 1 | `docs/adr/ADR-003-deployment-and-rollback.md` | Context dating note (L11); D1 rewritten — Vercel git deploys disabled for `production` via `git.deploymentEnabled` (planned `vercel.json` config, apps/web out of scope), Vercel CLI deploy from Actions, one-sentence ADR-004/M0-T011 note (L15-20); D2 rewritten — `autoDeployTrigger: off` (deprecates `autoDeploy`), deploy hooks with `ref=<validated SHA>`, staging `commit` (L22-29); NEW section D5 "Production deploy workflow (GitHub Actions — future implementation task)" with the (a)-(d) `needs:` chain and explicit not-implemented statement (L45-58); failed-migration step 1 rewritten, "promotion halts automatically" removed (L93); cron-revert bullet (L76); decision matrix cron + infra rows (L105, L107); new Consequences bullet — ordering exists only in future D5, procedural until then (L114-115); Sources header + rows updated (L120-135) |
| 1 | `docs/adr/ADR-002-environment-separation.md` | Amended date line (L4); mapping table prod row — Render `autoDeployTrigger: off` + deploy hooks; Vercel git auto-deploy disabled, CLI deploy (L36); promotion rule 2 — staging keeps auto-deploy, D4 safety rationale (L56); promotion rule 3 rewritten — nothing deploys on the push; future workflow enforces (a) migration validation → (b) prod migrations → (c) required checks → (d) human approval (required reviewers) → deploy hooks/`ref` + Vercel CLI (L57); Sources header + 4 new rows (L99-107) |
| 1 | `docs/DEPLOYMENT_AND_ROLLBACK.md` | Header dating note (L3); §0 prod row + order note — `needs:` chain is the only enforcement, manual-mode STOP rule (L11-13); §1.2 steps 3-4 rewritten with full gated sequence and citations (L28-29); §2.5 step 1 rewritten, "Pipeline halts automatically" removed (L65) |
| 1 (verified no-op) | `docs/adr/ADR-001-cloud-architecture.md` | UNTOUCHED — grep for `autoDeploy|auto-deploy|Vercel production deploy` returned no matches; ADR-001 states no auto-deploy model (directive point 5 condition not met) |
| 2 (MED) ENVIRONMENT literals | `render.yaml` | All three `value: production` literals → `sync: false` with environment-scoped comment (web L82-87, worker L119-122, cron L159-162) |
| 2 | `docs/adr/ADR-002-environment-separation.md` | Note under §3 secrets table: `ENVIRONMENT` declared `sync: false`, value entered per Render environment at Blueprint/service creation (L51) |
| 3 (MED) nonexistent smoke-test cron | `docs/adr/ADR-002-environment-separation.md` | §6 watch item rewritten: dev/CI activity is the only keep-warm mechanism; no keep-warm service (cron cost note); dashboard unpause per runbook (L76) |
| 4 (LOW) service-role key in CI secrets | `docs/adr/ADR-002-environment-separation.md` | §3 row 1: service-role key + DB URL in Render env vars/groups ONLY, not duplicated to GitHub (L44); new rows: Render deploy hook URLs and `VERCEL_TOKEN`/`VERCEL_ORG_ID`/`VERCEL_PROJECT_ID` as GitHub `production` environment secrets (L47-48) |
| 5 (LOW) unverified staging auto-deploy | `render.yaml` (policy block L39-43), `docs/adr/ADR-002-environment-separation.md` (rule 2, L56), `docs/adr/ADR-003-deployment-and-rollback.md` (D2, L27), `docs/DEPLOYMENT_AND_ROLLBACK.md` (§1.1 step 3, L22) | Decision stated identically in all four places: staging uses `autoDeployTrigger: commit`, configured at staging instantiation, marked [confirm at first use] cross-referencing ADR-002 verification item 1 |
| 6 (LOW) YAML validation in CI | `.github/workflows/ci.yml` | contracts job: new step "Validate render.yaml (Blueprint YAML syntax)" — `python3 -m pip install --quiet pyyaml` + `python3 -c "import yaml; yaml.safe_load(open('render.yaml', encoding='utf-8'))"` (step at L77-80; job comment disclosing the PyYAML install at L73-74). No restructuring |

## New citations used (all from the research doc; retrieved 2026-07-15)

- https://render.com/docs/blueprint-spec — `autoDeployTrigger` (`commit`/`checksPass`/`off`) replaces deprecated `autoDeploy`, takes precedence; default `commit` for new services
- https://render.com/docs/deploy-hooks — per-service secret URL; `ref` param deploys a specific commit SHA; 200/202/401; regenerate on compromise
- https://vercel.com/guides/how-can-i-use-github-actions-with-vercel — `vercel pull` → `vercel build --prod` → `vercel deploy --prebuilt`; `VERCEL_TOKEN`/`VERCEL_ORG_ID`/`VERCEL_PROJECT_ID`
- https://vercel.com/docs/project-configuration/git-configuration — `git.deploymentEnabled` per-branch disabling (default `true`; `github.enabled` deprecated)

Added to the Sources tables of ADR-002 and ADR-003; cited inline in render.yaml comments and runbook §1.2.

## Self-check evidence (actual outputs)

1. Removal patterns — Grep tool over `docs/adr/`, `docs/DEPLOYMENT_AND_ROLLBACK.md`, `render.yaml`:

```
pattern: halts automatically|blocks the dependent|autoDeploy: true|staging smoke-test cron   (docs/adr)          -> No matches found
pattern: halts automatically|blocks the dependent|autoDeploy: true|staging smoke-test cron|value: production (runbook) -> No matches found
pattern: value: production|autoDeploy: true|halts automatically   (render.yaml)              -> No matches found
pattern: halts|blocks everything   (docs/, recursive) -> only ADR-003 L47 ("no platform-side deploy runs or halts on its own" - the compliant needs:-chain framing) and the research doc itself
```

2. New-model presence — `autoDeployTrigger` matches:

```
render.yaml: L26, L28, L40 (policy comments), L73 (web: off), L116 (worker: off), L155 (cron: off)
ADR-003: L25 (D2 off), L27 (staging commit), L76 (cron revert), L107 (matrix confirm-note), L126 (source row)
ADR-002: L36 (prod mapping), L56/L57 (promotion rules), L103 (source row)
runbook: L11 (prod row), L22 (staging commit), L59 (confirm-note)
```

3. Defect-4 check — `service-role` in ADR-002 secrets context:

```
L44: "| Supabase service-role key, DB URL (per env) | Render env vars/env groups (scoped per project environment) **only**. Not duplicated to GitHub: the official migration CI flow needs only the CLI secrets in the row below, and no current workflow needs the service-role key. |"
```

4. ENVIRONMENT in render.yaml (Defect 2):

```
L86-87 / L121-122 / L161-162:  - key: ENVIRONMENT
                                 sync: false
(zero `value:` keys remain anywhere in render.yaml)
```

5. Programmatic YAML parse — **DENIED in this sandbox** (verbatim): `Permission to use Bash has been denied.` (both attempts: `python -c "import yaml; yaml.safe_load(open('render.yaml', encoding='utf-8'))"` and the same for `.github/workflows/ci.yml`). Fallback performed per the original G2 protocol: manual structural review of every edited hunk (consistent 2-space indentation; `autoDeployTrigger` aligned with sibling service keys; comments `#`-prefixed; list items under `envVars` unchanged in shape; ci.yml step uses the same indentation as sibling steps and a `run: |` block scalar). **Request:** orchestrator captures `python -c "import yaml; yaml.safe_load(open('render.yaml', encoding='utf-8'))"` (and same for ci.yml) per the ADR-005 evidence-capture protocol, as it did for the original G3 (Defect 6 addendum).

## Assumptions and disclosed nuances

1. Unquoted `off` for `autoDeployTrigger` follows the official Blueprint spec spelling as recorded in the research doc. YAML 1.1 loaders (PyYAML) read unquoted `off` as boolean `false`; parse success is unaffected. If Render's parser rejects the boolean form, the fix is quoting (`"off"`) — flagged for first Blueprint sync, not guessed either way.
2. Whether Blueprint infrastructure syncs still apply automatically with `autoDeployTrigger: off` is NOT claimed — marked [confirm at first use] in ADR-003 matrix and runbook §2.4 (the research doc covers deploy triggers, not Blueprint sync semantics).
3. The production deploy workflow (ADR-003 D5) is documented as a FUTURE implementation task everywhere it is mentioned; no file claims it exists.
4. `vercel.json` (`git.deploymentEnabled`) is documented as PLANNED configuration; the file lives in `apps/web`, outside this task's allowed paths. A tracked follow-up task must add it before the first production deploy.

## Known limitations

- Bash/python execution denied in this sandbox: YAML machine-parse and `git diff` outputs could not be captured by the producer; orchestrator capture requested (see item 5 above).
- The G3 reviewer should re-verify S4 end-to-end: ADR-002 rule 3 ↔ ADR-003 D2/D5/failed-migration step 1 ↔ runbook §0/§1.2/§2.5 ↔ render.yaml now describe one identical deployment sequence.

## Risks

- No new risks introduced. Existing recorded risks unchanged (private-repo required-reviewers gap, render.yaml placeholders, free-project pausing). One new tracked dependency: the D5 deploy workflow + `vercel.json` git config are prerequisites for the first production deploy and need follow-up tasks.

## Orchestrator-captured parse evidence (2026-07-15, per ADR-005 evidence-capture rule)

```
python -c "import yaml; yaml.safe_load(open('render.yaml', encoding='utf-8'))"   -> render.yaml parse OK
python -c "... open('.github/workflows/ci.yml' ...)"                              -> ci.yml parse OK; jobs: ['web', 'api', 'contracts', 'control-plane']
autoDeployTrigger values parsed by PyYAML (YAML 1.1): [('nycdf-api', False), ('nycdf-worker-jobs', False), ('nycdf-cron-source-monitor', False)]
```

Note for G3 reviewer: PyYAML reads unquoted `off` as boolean false (YAML 1.1). The official Render blueprint-spec examples write `autoDeployTrigger: off` unquoted; whether Render's parser expects the string "off" is flagged `[confirm at first use]` by the producer. Reviewer should assess whether quoting "off" is the safer spelling.
