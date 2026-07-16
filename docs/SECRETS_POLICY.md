# Secrets Policy

- **Status:** Active (task M0-T005; pending G3/G5 review)
- **Date:** 2026-07-15
- **Authoritative placement source:** `docs/adr/ADR-002-environment-separation.md` section 3 ("Secret placement") and `render.yaml` `sync: false` declarations
- **Related:** PRD sections 14.3 (no API secrets in frontend code), 17 (Security), 25 (Observability — never log secrets); `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`

## 1. Core rule

**No secret exists in Git, ever.** Not in code, not in configuration, not in fixtures, not in documentation, not in commit history, not in CI logs. This is mechanically enforced by the repo-local secret scanner (section 5) and should additionally be enforced by GitHub push protection (section 6).

## 2. Secret inventory

Every planned credential for this project, per ADR-002. "Template file" is the `.env.example` that documents the variable **name** (never a value); "n/a (CI only)" means the value is used only inside GitHub Actions and must not appear in any local env file.

| Secret name | Owning service | Storage location (per env) | Who may hold it | Rotation guidance | Template file | In Git? |
|---|---|---|---|---|---|---|
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase | Render env vars (`sync: false`), scoped per Render project environment. Never duplicated to GitHub or Vercel. | Backend API + workers (trusted server-side only). Never frontend, never CI, never local by default. | Rotate in Supabase dashboard immediately on suspected exposure or personnel change; redeploy Render services. | `services/api/.env.example` | **Never** |
| `SUPABASE_DB_URL` | Supabase | Render env vars (`sync: false`) per environment. | Backend API + workers. | Reset DB password in Supabase dashboard; update Render env vars. | `services/api/.env.example` | **Never** |
| `SUPABASE_URL` | Supabase | Render env vars (`sync: false`); frontend copy as `NEXT_PUBLIC_SUPABASE_URL` in the `nycdf-web` Render service env vars (ADR-004). Environment-scoped config, low sensitivity, still never committed (environments differ). | Backend, workers, frontend build. | n/a (project URL; changes only if project is recreated). | `services/api/.env.example` + `apps/web/.env.example` (as `NEXT_PUBLIC_SUPABASE_URL`) | Never |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` (anon/publishable key) | Supabase | `nycdf-web` Render service env vars (`sync: false`), scoped per environment (ADR-004). | Frontend (publishable by design — enforced by RLS), backend if needed for user-context calls. | Rotate via Supabase dashboard if abused; update Render envs. | `apps/web/.env.example` | Never (env-scoped; committing pins the wrong environment) |
| `SUPABASE_ACCESS_TOKEN` | Supabase (account-level CLI token, `sbp_` prefix) | GitHub environment secrets (`staging`, `production`) only — official Supabase CI migration flow. | GitHub Actions migration jobs only. | Revoke and regenerate in Supabase account settings; update GitHub environment secret. | n/a (CI only) | **Never** |
| `SUPABASE_DB_PASSWORD` | Supabase | GitHub environment secrets (`staging`, `production`) for CLI migrations. | GitHub Actions migration jobs only. | Reset in Supabase dashboard; update GitHub secret and the Render `SUPABASE_DB_URL`. | n/a (CI only) | **Never** |
| `SUPABASE_PROJECT_REF` (per env) | Supabase | GitHub environment secrets/variables (`staging`, `production`). Identifier, low sensitivity; kept out of Git to avoid hard-coding environments. | GitHub Actions migration jobs. | n/a (identifier). | n/a (CI only) | Never |
| `RENDER_DEPLOY_HOOK_URL_API`, `RENDER_DEPLOY_HOOK_URL_WORKER`, `RENDER_DEPLOY_HOOK_URL_CRON`, `RENDER_DEPLOY_HOOK_URL_WEB` | Render | GitHub `production` environment secrets **only**. A deploy hook is a per-service secret URL (ADR-002/ADR-003; `_WEB` added for the `nycdf-web` frontend service per ADR-004). | GitHub Actions production deploy workflow only. | Regenerate the hook in the Render dashboard if compromised; update GitHub secret. | n/a (CI only) | **Never** |
| `GEOCLIENT_SUBSCRIPTION_KEY` | NYC API Developers Portal | Render env vars (`sync: false`). Duplicated to a GitHub environment secret only if CI ever runs live smoke tests (not currently planned; live tests stay out of deterministic CI). | Backend API + workers. | Regenerate the subscription key at api-portal.nyc.gov; update Render env vars. | `services/api/.env.example` | **Never** |
| `ANTHROPIC_API_KEY` | Anthropic | Render env vars (`sync: false`). | Backend workers (AI extraction jobs). | Revoke and reissue in the Anthropic console; update Render env vars. | `services/api/.env.example` | **Never** |
| `SENTRY_DSN` | Sentry | Render env vars (`sync: false`). A DSN is low-sensitivity (submit-only) but is treated as environment-scoped config-secret and kept out of Git. | Backend API + workers. | Rotate DSN in Sentry project settings if spammed/abused. | `services/api/.env.example` | Never |
| `ENVIRONMENT` | (not a secret) | Render env vars (`sync: false` so one Blueprint serves staging and production, ADR-002). Listed for completeness because it appears alongside secrets in `render.yaml`. | All backend services. | n/a. | `services/api/.env.example` | Never (env-scoped) |
| `GITHUB_TOKEN` | GitHub Actions | Auto-issued per workflow run; never stored anywhere. Scope minimized via explicit `permissions:` blocks in every workflow. | The issuing workflow run only. | Automatic (expires with the run). | n/a | n/a |

Any **new** secret introduced by a future task must be added to this table in the same change, with a storage location chosen per ADR-002, before the secret is provisioned.

## 3. Handling rules

1. **Never in Git or code.** No secret value in any tracked file, commit message, branch name, or fixture — including "temporary" or "example" real values. `.env.example` files contain variable names and comments only.
2. **Never in logs or CI output.** Do not `echo`/print env values in workflows, scripts, or application logs (PRD 25). The secret scanner masks everything it matches for the same reason.
3. **Never in the frontend.** `apps/web` may only ever reference publishable values (`NEXT_PUBLIC_SUPABASE_URL`, the anon key). The service-role key, DB URLs, and all provider tokens are server-side only (PRD 14.3/17). Any `NEXT_PUBLIC_*` variable is public by construction — treat adding one as a design decision, not a convenience.
4. **Never written to disk from chat.** Credentials shared by the owner in a conversation are entered directly into the target provider dashboard/secret store and are never saved into repo files, reports, agent memory, or scratch files (precedent: the temporary Render key incident audited in `project-control/reports/M0-T004-G5-security-review.md`).
5. **Deploy-time secrets live in GitHub environment secrets** (`dev`/`staging`/`production` environments per ADR-002), never in repository-level plaintext, workflow files, or repo variables.
6. **Runtime backend secrets live in Render env vars / environment groups** declared `sync: false` in `render.yaml` (values entered in the Render dashboard, scoped per project environment; excluded from preview environments by Render's own behavior).
7. **Frontend runtime config lives in the `nycdf-web` Render service env vars** (`sync: false`), scoped per environment (ADR-004 — Vercel dropped; frontend served from Render).
8. **Local `.env` files** are for future approved local development only. They are already gitignored (`.env`, `.env.*`, with only `!.env.example` tracked). Default development is remote (Codespaces/Actions/Render) per the low-storage policy; do not create local `.env` files containing production or staging credentials.
9. **Least privilege.** Every workflow declares an explicit `permissions:` block (default `contents: read`). Secrets are attached to GitHub *environments*, not the repository, so they are only exposed to jobs that target that environment.

## 4. Incident procedure (suspected or confirmed leak)

Treat any secret that ever reached a pushed commit, a log, a chat transcript file, or an untrusted machine as **compromised**, even if later deleted — history rewriting does not un-leak a value.

1. **Rotate first.** Immediately revoke/regenerate the credential at the owning service (see rotation column above). This is the only step that actually ends the exposure.
2. **Update storage.** Enter the new value in its single authorized location (Render dashboard / GitHub environment secret / Vercel env). Redeploy dependent services.
3. **Scan history.** Run `python .github/scripts/secret_scan.py` on the working tree and search full history (`git log --all -p` piped through the same pattern classes) to find every occurrence and any sibling secrets leaked alongside.
4. **Record.** File a blocker/audit entry in `project-control/` describing what leaked, where, rotation timestamp, and verification evidence. Security-relevant incidents get a G5 follow-up review.
5. **Clean up (secondary).** Remove the value from the tree; history rewriting is optional and only worthwhile before others have fetched — rotation is mandatory regardless.

## 5. Mechanical enforcement in this repository

- `.github/scripts/secret_scan.py` — stdlib-only, deterministic, no-network scanner run by the standalone `secret-scan` workflow on every push and pull request. It fails CI when it finds: Render keys (`rnd_` prefix), Supabase access tokens (`sbp_` prefix), JWTs (`eyJ` base64 header with two dot-separated segments — Supabase anon/service-role keys are JWTs), `service_role` assignments carrying values, PEM private-key headers (BEGIN ... PRIVATE KEY blocks), AWS access key IDs (`AKIA` prefix), GitHub tokens (`ghp_`/`gho_`/`ghs_`/`ghu_`/`ghr_`/`github_pat_`), Slack tokens (`xox` prefix), generic **and compound-prefixed** `…api_key/secret/password/token = "<high-entropy value>"` assignments above an entropy threshold (compound names such as `AUTH_TOKEN=`, `DB_PASSWORD=`, `allowed_token=` are matched), **exact inventory-name assignments** (every secret name in section 2 carrying a non-placeholder value, independent of entropy), **`postgres://`/`postgresql://` URIs containing a password**, **Render deploy-hook URLs**, and hex-format keys (e.g. Geoclient subscription keys). Files are decoded with UTF-8/UTF-16 BOM detection, so PowerShell-redirected UTF-16 files are scanned rather than skipped.
- **False-positive handling:** an **exact-path** allowlist (only `apps/web/package-lock.json` is fully skipped for npm integrity hashes; the two policy-approved templates `services/api/.env.example` and `apps/web/.env.example` are still content-scanned — any non-empty value in them is a finding) plus an inline pragma (`secretscan:allow <justification>`) for individually verified lines. All allowlist and pragma usage is printed in the scan output (`ALLOWLISTED PATH` / `ALLOWLISTED LINE` notices) so reviewers see every suppression; a pragma with an empty justification does not suppress anything — the scanner reports the finding and fails (exit 1). A `.env.example` file anywhere else in the tree is scanned as a normal file.
- Matched values are masked (first/last 4 characters) so the scanner never re-prints a credential into CI logs, and all printed paths/lines are stripped of control characters so findings cannot inject GitHub workflow commands into the log.
- **Exit codes:** 0 = clean, 1 = findings (or an empty-justification pragma), 2 = scanner could not run (e.g. not a git repository) — CI treats any non-zero as failure; oversized (>2MB) and binary files are skipped with visible notices.
- `.gitignore` blocks `.env` and `.env.*` while allowing `.env.example` (verified; rule exists at repo root).

## 6. Relationship to GitHub push protection (owner action recommended)

The repo-local scanner is a **complement to, not a replacement for**, GitHub's own secret scanning:

- Regex scanning has inherent **false-negative risk** — it only catches known prefixes and high-entropy assignments. GitHub push protection uses provider-verified patterns and blocks secrets **before** they enter history, which no post-push CI job can do.
- **Recommended human action (owner):** enable *Secret scanning* and *Push protection* in the GitHub repository settings (Settings → Code security). This is an owner-permission repository setting and cannot be done by agents; track it as a human action item. Availability on private repos may depend on the GitHub plan (GitHub Advanced Security); enable whatever tier the current plan allows and note the residual gap if unavailable.
- The repo-local scanner remains valuable regardless: it enforces project-specific pattern classes (Render/Supabase/NYC-specific), runs identically for every contributor and agent, and requires zero external configuration or paid features.
