# G5 Security & Privacy Gate Report — M0-T004 "Monorepo skeleton + GitHub Actions CI"

- **Gate:** G5 (security-reviewer, independent of producer)
- **Branch/head reviewed:** `task/M0-T004-monorepo-ci` @ `a0d8f3ac60678f0ed597c9d7df4a09513839a35d`
- **Worktree:** `.claude/worktrees/M0-T004`
- **Date:** 2026-07-15
- **Gate recording:** delegated to the orchestrator per ADR-005; this file is the full report returned by the security-reviewer agent.

## Verdict: PASS

## Summary

The diff (23 files, +6,305 lines) is a static monorepo skeleton with no auth, database, storage, upload, external-call, or AI code, so most G5 attack surfaces do not yet exist and are marked N/A with evidence. Zero secrets were found in the diff, in the working tree, and in all 18 commits of git history — specifically, the temporary Render API key (`rnd_` prefix) shared in chat was never written to disk anywhere in the repo or worktree, including the reverted scratch commits 9aec6b4/429c575. CI workflows use least-privilege `permissions: contents: read`, reference no secrets, contain no untrusted-input interpolation into `run:` steps, and all 364 lockfile packages resolve to `registry.npmjs.org`. Four medium/low follow-ups are recorded (tag-pinned actions, no dependency-audit step, unpinned Python deps, lingering `contents: write` utility workflow); none are critical or high, so the gate passes.

## Checklist

| # | Item | Result | Evidence |
|---|------|--------|----------|
| 1 | No secrets/tokens/keys in diff | PASS | `git diff main...` grep for `rnd_/sbp_/eyJ/api_key/password/Bearer/service_role/PRIVATE KEY` → only 2 hits, both sha512 integrity-hash substrings in `apps/web/package-lock.json:1475,4242` (not JWTs) |
| 1a | Render key never written to disk | PASS | `grep -rniE "rnd_[A-Za-z0-9]{8,}"` over entire repo (incl. `.claude/`, excl. `.git`) → 0 hits; `git log --all -p` over all 18 commits → 0 hits; no `.env*` files exist anywhere |
| 2a | Workflow least privilege | PASS | `.github/workflows/ci.yml:12-13` `permissions: contents: read`; no secrets referenced in any workflow |
| 2b | No pull_request_target misuse | PASS | `ci.yml:8-10` uses `push`/`pull_request` only; `generate-lockfile.yml:9-10` uses `workflow_dispatch` only (write-access users only can dispatch) |
| 2c | No script injection via `${{ }}` | PASS | Only interpolation is `${{ github.ref }}` in `ci.yml:16` concurrency group (not a shell context); zero `${{ }}` inside any `run:` step in either workflow |
| 2d | Actions pinning | PASS w/ follow-up | `actions/checkout@v4`, `setup-node@v4`, `setup-python@v5` — major-tag pinned, not SHA (Defect 1, medium) |
| 2e | Zero-secret CI | PASS | No `secrets.` reference anywhere; `generate-lockfile.yml:36` pushes with default `GITHUB_TOKEN` only |
| 2f | workflow_dispatch inputs | PASS | `generate-lockfile.yml` declares no inputs; `npm install --package-lock-only` (line 25) does not execute lifecycle scripts |
| 3 | Dependency posture | PASS w/ follow-ups | `apps/web/package.json`: next 15.3.4 (post-CVE-2025-29927), react 19.1.0, eslint 9 — all mainstream, no typosquats; all 364 `resolved` URLs in package-lock.json → `registry.npmjs.org`, lockfileVersion 3; `services/api/pyproject.toml:11-21`: fastapi/uvicorn/pytest/httpx/ruff only (Defects 2, 3) |
| 4 | FastAPI placeholder | PASS | `services/api/app/main.py` — 24 lines, single static `/api/v1/health`, no debug flag, no CORS middleware at all, no env exposure, no eval/exec, no host binding in code (deferred to Render start command) |
| 5 | Next.js placeholder | PASS | No `NEXT_PUBLIC_*` anywhere in diff; `next.config.ts` sets only `reactStrictMode: true`; pages are static JSX with the PRD s29 disclaimer (`src/lib/disclaimer.ts`) |
| 6 | Logging/redaction | PASS | No logging configuration or log statements added anywhere in the diff; health endpoint returns static `{status, version}` |
| 7 | Low-storage policy | PASS | All installs/builds run on GitHub-hosted runners (`ci.yml:5-6` comment, README "Remote-first development"); lockfile generated remotely (`generate-lockfile.yml`); no artifact uploads; nothing writes to owner PC |
| 8 | No telemetry/credential capture | PASS | `NEXT_TELEMETRY_DISABLED: "1"` at `ci.yml:27`; `--no-audit --no-fund` on npm; no analytics/telemetry deps; CI scripts (`validate_contracts.py`, `test_project_control.py`) are stdlib-only, no network imports (subprocess in the latter only re-invokes the repo's own `project_control.py` in a tempdir) |
| — | .gitignore adequacy | PASS | Root `.gitignore` covers `node_modules/`, `.venv/`, `.next/`, caches, `*.db`, datasets, GIS exports, playwright output, `.env`/`.env.*` (with `!.env.example`), `.claude/worktrees/` |
| — | RLS / cross-tenant isolation | N/A | No database, auth, or Supabase code in diff; `supabase/migrations/` contains only `.gitkeep` |
| — | Service-role secrecy | N/A (verified absent) | grep `service_role` across diff and history → 0 hits |
| — | Private storage / uploads / SSRF / prompt-injection defenses | N/A | No storage buckets, upload handlers, outbound HTTP calls, or AI/ingestion code exist in this diff; must be re-gated when M0-T005+ introduces them |

## Defects

1. **Medium — GitHub Actions pinned by mutable major tag, not commit SHA.** Location: `.github/workflows/ci.yml:29,30,53,54,72,81` and `.github/workflows/generate-lockfile.yml:19,21` (`actions/checkout@v4`, `actions/setup-node@v4`, `actions/setup-python@v5`). A compromised upstream tag could execute arbitrary code in CI. Risk is currently bounded because the repo has zero secrets and `contents: read`, but it becomes high the moment deployment secrets are added (M0-T005/T006). Remediation: pin to full commit SHAs with a version comment (e.g., `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v4.2.2`) and enable Dependabot `github-actions` ecosystem updates. Reproduce: `grep -n "uses:" .github/workflows/*.yml`.
2. **Low — No dependency-vulnerability scanning in CI.** `ci.yml:38` runs `npm ci --no-audit`; there is no `npm audit`, `pip-audit`, or Dependabot config in the diff. Remediation: add a Dependabot config (`npm`, `pip`, `github-actions`) or a scheduled audit job before M1.
3. **Low — Python dependencies unpinned (version ranges, no lockfile).** `services/api/pyproject.toml:11-21` uses ranges (`fastapi>=0.115,<1`), and `ci.yml:58` caches on `pyproject.toml`. Builds are not reproducible and silently drift. Remediation: adopt a pinned lock (uv/pip-tools `requirements.txt` generated in CI, mirroring the npm lockfile approach) before the API gains real dependencies.
4. **Low — One-shot lockfile workflow retains `contents: write`.** `.github/workflows/generate-lockfile.yml:12-13`. Its purpose is complete (lockfile committed at 05c19ae/e4e57a0). Exploitation requires repo write access to dispatch, so risk is low, but it is standing write-capable automation with no remaining use. Remediation: delete the workflow (or restrict via an `environment:` with required reviewers) in a follow-up commit on main.

No critical or high defects. Per G5 policy, medium/low items are recorded as follow-ups and do not fail the gate. Recommended tracking: fold Defect 1 into whichever M0 task first adds a repository/CI secret; Defects 2-4 as small backlog items.

## Commands run (abbreviated key outputs)

```
git log --oneline -5                              → head a0d8f3a; scratch commit 9aec6b4 reverted by 429c575
git diff main...task/M0-T004-monorepo-ci --stat   → 23 files, 6305 insertions
git diff main... | grep -niE "rnd_|sbp_|eyJ|api_key|password|bearer|service_role|PRIVATE"
                                                  → 2 hits, both sha512 integrity hashes in package-lock.json
git log main..HEAD -p | grep -niE "<secret patterns>"           → 0 hits (incl. reverted commits)
grep -rniE "rnd_[A-Za-z0-9]{8,}" <repo root, excl .git>          → 0 hits
git log --all -p | grep -cniE "rnd_[A-Za-z0-9]{8,}"              → 0 (all 18 commits)
grep -oE '"resolved": "[^"]+"' package-lock.json | grep -v registry.npmjs.org → 0 of 364
find . -name ".env*"                                             → none
grep -nE "subprocess|urllib|requests|socket|eval" tools/test_project_control.py .github/scripts/validate_contracts.py
                                                  → subprocess only, invoking repo-local project_control.py
```

## Files reviewed

- `.github/workflows/ci.yml`, `.github/workflows/generate-lockfile.yml`, `.github/scripts/validate_contracts.py`
- `services/api/app/main.py`, `services/api/pyproject.toml`, `services/api/tests/test_health.py`, `services/api/README.md`
- `apps/web/package.json`, `apps/web/package-lock.json` (scanned), `next.config.ts`, `eslint.config.mjs`, `tsconfig.json`, `src/app/layout.tsx`, `src/app/page.tsx`, `src/lib/disclaimer.ts`
- `packages/contracts/schemas/v1/property_profile.schema.json`, `analysis_state.schema.json`, `coverage_status.schema.json` (scanned)
- `.gitignore`, `README.md`, `supabase/migrations/.gitkeep`
- `tools/test_project_control.py` (pre-existing, executed by CI — scanned for network/exec)
