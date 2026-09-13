# M5-T024 producer report — D-043 internal web deploy checklist

- **Task:** M5-T024 (infrastructure) — owner-executed Render internal web deploy checklist.
- **Directive:** D-043 (D-043-R001..R004), `directive_refs` = `D-043:ALL`.
- **Producer agent:** cloud-architect. **Reviewers:** code-reviewer, security-reviewer.
- **Base SHA:** `c6aca328` (reset in worktree `agent-a692d1fcd8bc8eea1`).
- **Scope:** DOCS-ONLY, exactly two files (both in `allowed_paths`):
  - `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` — committed stub replaced with the full
    owner-executed checklist.
  - `project-control/reports/M5-T024-producer-report.md` — this report.
- Everything else was read-only. `render.yaml` was **not** edited (the `nycdf-web` block
  restoration is a recorded LATER debt, documented in the checklist §8 as owed-not-performed). The
  prior `nycdf-web` block was recovered **read-only** via `git show 23817a9f~1:render.yaml`.

## Acceptance scenarios

### S1 — completeness_and_order (PASS by construction)

The checklist is numbered dashboard steps in strict dependency order, every value present or an
explicit placeholder:

- **Create service (§1):** repo `nyc-buildability`, branch `candidate/D-024-mrl-option-b` (with the
  "not `main`" reason), root `apps/web`, runtime Node, Node 22, build `npm ci && npm run build`,
  start `npm run start` (+ `$PORT` binding note), plan choice with the Hobby/free spin-down tradeoff
  stated, region `oregon`, health `/`.
- **Env-before-build ordering (§2 → §3):** `NEXT_PUBLIC_API_BASE_URL` is set **before** the first
  build because it is build-time inlined; §3 states the rebuild-on-change rule. This directly
  answers the S1 ordering requirement and risk #2.
- **Origin-before-CORS ordering (§4 → §5):** the new web origin is captured in §4 **before** the
  CORS entry on `nycdf-api` in §5 — answering the S1 ordering requirement and risk #1.
- **Both services' env changes covered:** web service (§2: `INTERNAL_RULE_EVAL_ENABLED`,
  `NEXT_PUBLIC_API_BASE_URL`, blank Supabase vars) and `nycdf-api` (§5:
  `API_CORS_ALLOWED_ORIGINS`, `INTERNAL_RULE_EVAL_ENABLED`).
- **Folded-in standing items:** Blueprint Auto Sync = No (§7); M5-T019 stale-flag-name check (§10).
- **R003 owner-only:** the preamble and every step state the owner performs the dashboard actions;
  no agent action anywhere.

### S2 — privacy_grep (PASS)

No real service URL, no `onrender.com` host, no key/token/secret. The only URL literal is the
documented local default `http://127.0.0.1` (from `apps/web/.env.example` / `api.ts`), which is not
a service URL or secret. The private API URL appears only as `<owner-pastes-private-API-URL>`; the
web origin only as `<new-web-service-origin>`. D-043-R002 satisfied by construction.

Grep transcript (run in the worktree against both output files):

```
$ grep -rni 'onrender' docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md
$                                             # (no matches; exit=1)

$ grep -rnoE 'https?://[a-zA-Z0-9.-]+' docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md | sort -u
127:http://127.0.0.1                          # documented local default only

$ grep -rniE 'sk-|bearer |api[_-]?key *=|token *=|password *=|-----BEGIN' docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md
$                                             # (no matches; exit=1)
```

This report contains no secret either (placeholders only, and the same `127.0.0.1` default when
citing the code). A grep of this report yields the same clean result by construction.

### S3 — technical_accuracy (PASS; every claim carries a source)

Cross-checked against repo evidence:

- **Flag name** exactly `INTERNAL_RULE_EVAL_ENABLED` with documented true tokens `1/true/yes/on`
  (case-insensitive, trimmed) — `apps/web/src/lib/rule-evaluation.ts` lines 79, 83, 87-91.
- **CORS semantics** — exact origins, wildcard rejected at startup (`RuntimeError`), unset/empty =
  no cross-origin access — `services/api/app/main.py` lines 15-23, 66-82, 87, 103.
- **Build/start** — `npm ci && npm run build` / `npm run start`, matching
  `apps/web/package.json` (`build`=`next build`, `start`=`next start`) and the recovered prior
  `nycdf-web` block; `$PORT` binding explained (Next `next start` honors `PORT`; explicit
  `-- -p $PORT` alternative offered, flagged for UI confirmation).
- **Node 22** — matches `.github/workflows/ci.yml` (`node-version: 22`); `apps/web/package.json`
  has no `engines` field, so the version must be set explicitly. The **exact Render mechanism** is
  NOT fixed by repo evidence (see Ambiguities) and is marked `[confirm in the dashboard UI]`.
- **Build-time inlining** — `apps/web/.env.example` lines 6-8, 27-35; `docs/DEPLOYMENT_AND_ROLLBACK.md`
  §1.3.
- Region `oregon`, health `/`, plan tradeoff — `render.yaml` + recovered prior block.
- A **Provenance summary** table at the end of the checklist maps every material claim to its
  source file/lines.

### S4 — honest_exposure_and_scope (PASS)

- **No-auth exposure stated plainly** (§0 bullet, §6): the API has no authentication, so turning the
  internal flag on makes flag-gated routes reachable by anyone holding the API URL; unlisted != secret
  — the directive's own words. Sources: `services/api/app/main.py` docstring lines 6-11;
  `docs/MVP_AGENDA.md` §I; D-043 source-001.md.
- **Internal/dev labeling stays; NOT a public launch** (§0, §9 expected-absent, §8): no listing,
  marketing, or indexing steps appear anywhere (D-043-R004). Verified by reading the whole file.
- **Restoration debt + duplicate-service caution recorded as owed, not performed** (§8), linked to
  Auto Sync = No (§7). `render.yaml` untouched.

## Documented test commands (captured outputs)

- `python tools/modularity_check.py --check` → **selected 397 files; failures 0; warnings 16**
  (all 16 warnings are pre-existing, unrelated files under `apps/web/src/lib/surveyReview/`,
  `services/api/**`, `tools/agent_supervisor/**`, `tools/context_benchmark.py`; **neither of my two
  files appears**). Docs-only change stays EXIT 0.
- `python tools/validate_directive_compliance.py --check` → **exit=0**.
- Privacy grep → transcript under S2 (placeholders only).

## Ambiguities I could NOT resolve from repo evidence (flagged, not guessed)

1. **Exact Render Node-version mechanism.** The repo research capture
   (`docs/research/render-nextjs-previews-2026-07-16.md` §1) records only that Render documents
   Node-version pinning on a separate "Specifying a Node Version" page — it does **not** capture the
   exact field (e.g. `NODE_VERSION` env var vs `.node-version` file). I did not invent one; §1 step 5
   instructs the owner to set version **22** via whichever mechanism the current UI offers and to
   confirm Node 22 in the build log — marked `[confirm in the dashboard UI — not evidenced in the
   repo]`.
2. **`DEPLOYMENT_AND_ROLLBACK.md` section "0.1".** The packet cited sections "0.1 and 1.3" for the
   inlining rule, but at base SHA `c6aca328` this file has **no** subsection 0.1 (its section 0 is
   the environment map; the inlining/rebuild rule is authoritatively in `apps/web/.env.example`
   lines 27-35 and DEPLOYMENT §1.3 "Env var changes are deploys"). I cited the sources that actually
   exist. Not a blocker; flagged so the reviewer isn't surprised by the missing subsection number.
3. **Render New-Web-Service UI labels, `$PORT` listen confirmation, Auto Sync toggle label.** These
   are live-dashboard specifics not fixed by repo evidence; each is marked
   `[confirm in the dashboard UI]` rather than asserted.

## Scope-compliance confirmation

- Only the two `allowed_paths` files were written. No forbidden path touched (`render.yaml`,
  `apps/web/**`, `services/api/**`, `project-control/**` except this report, etc. all read-only).
- Only permitted git write was `git reset --hard c6aca328`; the only other git use was read-only
  `git show 23817a9f~1:render.yaml`. No commit, no push, no `tools/project_control.py`.
- No credential, key, or real URL in either file (D-043-R002). No dashboard action performed by any
  agent (D-043-R003). No public-launch content (D-043-R004).

## Requested status

**awaiting_gate** — G0, G1, G5 required; reviewers code-reviewer + security-reviewer.
Producer does not self-accept. Work left as UNCOMMITTED edits in worktree `agent-a692d1fcd8bc8eea1`.
