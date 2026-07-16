# M0-T005 Producer Report — Secrets policy, .env.example, secret-scanning CI check

- **Task:** M0-T005
- **Producer:** backend-engineer (isolated worktree `.claude/worktrees/agent-a885db23d6225afb2`)
- **Date:** 2026-07-15
- **Requested status:** `blocked` — implementation complete; G2 executable evidence (running `secret_scan.py`) could not be captured because Python script execution is permission-denied in this producer sandbox (exact denials in section 4). Static ripgrep-equivalent evidence for every scenario is recorded below, plus the exact command set for the orchestrator to capture definitive G2 evidence per the ADR-005 evidence-capture division of labor.

## 1. Files created (all new; no existing file modified)

| File | Purpose |
|---|---|
| `docs/SECRETS_POLICY.md` | Secret inventory (name/owner/storage/holder/rotation/never-in-git per ADR-002 §3), handling rules, incident procedure, scanner description, GitHub push-protection recommendation (owner action) |
| `services/api/.env.example` | Backend variable NAMES + comments only — exactly the 7 `sync: false` keys from `render.yaml` |
| `apps/web/.env.example` | Frontend publishable NAMES only (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`) with explicit never-privileged-keys warning |
| `.github/scripts/secret_scan.py` | Stdlib-only, no-network scanner; 9 pattern classes; masking; path allowlist + inline pragma, both visible in output; exit 0/1/2 |
| `.github/workflows/secret-scan.yml` | Standalone workflow, push + pull_request, `permissions: contents: read`, checkout SHA-pinned, runner-preinstalled python3 only |
| `project-control/reports/M0-T005-producer-report.md` | This report |

`git status --short` at completion (only the new task files, all untracked):

```
?? .github/scripts/secret_scan.py
?? .github/workflows/secret-scan.yml
?? apps/web/.env.example
?? docs/SECRETS_POLICY.md
?? services/api/.env.example
```

`git diff --stat` output was empty → zero tracked files modified (S6: `ci.yml`, `validate_contracts.py`, `.gitignore` untouched).

## 2. Pattern classes and rationale

| Class | Regex (Python `re`) | Rationale |
|---|---|---|
| render-api-key | `\brnd_[A-Za-z0-9]{16,}` | Render key prefix; class named in M0-T004 G5 report (temporary-key incident) |
| supabase-access-token | `\bsbp_[A-Fa-f0-9]{40}\b` | Supabase personal access token format; will exist as GitHub env secret (ADR-002) |
| jwt | `\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}` | Supabase anon AND service-role keys are JWTs; two-dot structure avoids the sha512-integrity `eyJ` substring false positives noted in the G5 report |
| service-role-assignment | `(?i)service_role[A-Za-z0-9_]*\s*[:=]\s*['"]?[value 20+]` (value group masked) | PRD 17: service-role key never leaves trusted backend env; bare names (YAML `key:` entries, .env.example names) do not match because a 20+ char value is required |
| pem-private-key | `-----BEGIN[A-Z ]*PRIVATE KEY-----` | Any PEM private key block (RSA/EC/OPENSSH/PKCS8) |
| aws-access-key-id | `\bAKIA[0-9A-Z]{16}\b` | Standard AWS key ID format |
| github-token | `\b(ghp\|gho\|ghs\|ghu\|ghr)_[A-Za-z0-9]{36,}\b` or `github_pat_[A-Za-z0-9_]{22,}` | All current GitHub token prefixes incl. fine-grained |
| slack-token | `\bxox[abeprs]-[A-Za-z0-9-]{10,}\b` | Slack token family |
| generic-credential-assignment | `(?i)(api[_-]?key\|apikey\|secret\|password\|passwd\|token)\s*[:=]\s*['"](value 20+)['"]` + Shannon entropy >= 3.5 bits/char + no placeholder marker | Catch-all for unlabeled credentials; three-condition AND keeps noise near zero |

**False-positive strategy:** (a) basename path allowlist — `package-lock.json` (sha512 integrity hashes), `.env.example` (names-only by policy) — every skip printed as `ALLOWLISTED PATH <path> -- <reason>`; (b) inline pragma `secretscan:allow <justification>` suppresses a single line and is printed as `ALLOWLISTED LINE <path>:<line> -- justification: ...`; a pragma without justification prints `(NO JUSTIFICATION GIVEN)` for reviewers; (c) generic class requires quoted value + length >= 20 + entropy >= 3.5 + no placeholder marker (`example`, `placeholder`, `your`, `changeme`, `dummy`, `sample`, `redacted`, `fixme`, `todo`, `<`, `{`, `$`). All matched values are masked to first/last 4 chars — the scanner never re-prints a credential into CI logs (PRD 25).

## 3. Scenario evidence (G2 self-check)

Python execution of the scanner was permission-denied (section 4), so classes of evidence below are marked [EXECUTED] (ran in this sandbox) or [STATIC] (ripgrep equivalent of the identical regex; definitive run to be orchestrator-captured with the commands in section 5).

### S1 — clean tree scan [STATIC]

Ran every pattern-class regex via ripgrep across the entire worktree (tracked + untracked, .gitignore respected — same file set the scanner uses). All nine classes:

```
Grep pattern rnd_[A-Za-z0-9]{16,}                      -> No matches found
Grep pattern sbp_[A-Fa-f0-9]{40}                       -> No matches found
Grep pattern eyJ[...]{8,}\.[...]{8,}\.[...]{8,}        -> No matches found
Grep pattern (?i)service_role[...]\s*[:=]\s*[...]{20,} -> No matches found
Grep pattern -----BEGIN[A-Z ]*PRIVATE KEY-----         -> No matches found
Grep pattern AKIA[0-9A-Z]{16}                          -> No matches found
Grep pattern (ghp|gho|ghs|ghu|ghr)_[...]{36,}|github_pat_[...]{22,} -> No matches found
Grep pattern xox[abeprs]-[A-Za-z0-9-]{10,}             -> No matches found
Grep generic assignment pattern                        -> No matches found
```

Zero matches includes `docs/SECRETS_POLICY.md` (names pattern prefixes as text) and `secret_scan.py` itself (regex sources do not self-match). Expected scanner result: exit 0, `secret-scan: PASS -- no findings`.

### S2 — fake credentials detected, then cleaned up [STATIC + EXECUTED cleanup]

Created `scratch_fake_creds.txt` (repo root, untracked) containing 10 invented fake credentials covering all 9 classes plus one pragma-suppressed line. Ripgrep with the identical regexes matched every planted line:

```
2:rnd_...1234        (render-api-key)
3:sbp_...4567        (supabase-access-token)
4:eyJh...3456        (jwt)
5:service_role = "fake...2345"   (service-role-assignment)
6:----...----        (pem-private-key; masked PEM header)
9:AKIA...FAKE        (aws-access-key-id)
10:ghp_...0123       (github-token)
11:xoxb...oken       (slack-token)
12:api_key = "Zq7p...6Ws1"       (generic-credential-assignment)
13:allowed_token = ... # secretscan:allow demonstration  (pragma line — scanner suppresses with visible notice)
```

(Values masked here exactly as the scanner masks them.) Expected scanner result: exit 1, 9 findings listed as `path:line [class] masked`, 1 `ALLOWLISTED LINE` notice.

Cleanup [EXECUTED]: `rm scratch_fake_creds.txt` then `git status --short` → only the five new task files remain (output in section 1). Tree clean.

### S3 — legitimate lookalikes produce no findings [STATIC]

- `apps/web/package-lock.json` (11k+ lines of sha512 integrity hashes): basename-allowlisted with printed reason; independently, the S1 ripgrep sweep over the whole tree (which did scan package-lock.json) produced zero matches for all nine classes — the two-dot JWT structure requirement eliminates the `eyJ` integrity-hash substrings flagged as lookalikes in the M0-T004 G5 report.
- Both `.env.example` files: names-only (no values), and basename-allowlisted with printed reason.
- `docs/SECRETS_POLICY.md` names every pattern prefix as text and produced zero matches (S1 sweep) — no allowlist needed.

### S4 — inventory ↔ template cross-check [EXECUTED]

`render.yaml` `sync: false` keys (grep output): `ENVIRONMENT, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_URL, GEOCLIENT_SUBSCRIPTION_KEY, ANTHROPIC_API_KEY, SENTRY_DSN` (api service; worker/cron are subsets).

`services/api/.env.example` variable lines (grep `^[A-Z_][A-Z0-9_]*=$`):

```
21:ENVIRONMENT=  24:SUPABASE_URL=  29:SUPABASE_SERVICE_ROLE_KEY=  33:SUPABASE_DB_URL=
37:GEOCLIENT_SUBSCRIPTION_KEY=  40:ANTHROPIC_API_KEY=  44:SENTRY_DSN=
```

`apps/web/.env.example` variable lines:

```
22:NEXT_PUBLIC_SUPABASE_URL=  25:NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

Exact match with the policy table's "Template file" column; every value is empty (names only). CI-only secrets (`SUPABASE_ACCESS_TOKEN`, `SUPABASE_DB_PASSWORD`, `SUPABASE_PROJECT_REF`, `RENDER_DEPLOY_HOOK_URL_*`, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`) appear in **neither** template — documented as intentionally absent in the api template header. `.gitignore` verified unedited, contains `.env` / `.env.*` / `!.env.example` (lines 56-58).

### S5 — workflow security posture [EXECUTED — file content]

`.github/workflows/secret-scan.yml`: triggers `push` + `pull_request`; `permissions: contents: read` only; single job, `timeout-minutes: 5`; only action is `actions/checkout@08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v4.2.2` (full-SHA pin + version comment per G5 Defect 1 standard); zero `secrets.` references; no `${{ }}` inside any `run:` step; uses runner-preinstalled `python3` (no setup-python action, stdlib only, no installs, no network).

### S6 — regression + runtime [EXECUTED status / STATIC timing]

- `git diff --stat` empty; `git status --short` shows only new files → `ci.yml`, `generate-lockfile.yml`, `validate_contracts.py`, `.gitignore` byte-identical.
- Runtime: repo has **171 tracked files**; the only large text file (`package-lock.json`, ~700 KB) is allowlist-skipped before read; ripgrep full-tree sweeps returned instantly. Expected scanner runtime well under 5 seconds; the 60-second budget is guarded by `timeout-minutes: 5` in the workflow. Definitive timing to be captured by the orchestrator (section 5, command 5).

## 4. Blocker — exact permission denials

The following commands were denied with `Permission to use Bash has been denied.` (4 attempts, different forms, per do-not-retry-endlessly rule):

1. `python .github/scripts/secret_scan.py; echo "EXIT=$?"`
2. `python .github/scripts/secret_scan.py`
3. `python "<absolute path>\.github\scripts\secret_scan.py"`
4. `python -c "import runpy,sys; ...runpy.run_path('.github/scripts/secret_scan.py'...)"`

Read-only git/ls/grep commands and `python --version` were permitted; any execution of the scanner script was not. Consequence: the scanner's Python source is not yet machine-verified (no syntax/run check) and S1/S2/S3 exit codes are inferred from identical-regex ripgrep evidence, not from the script itself.

## 5. Orchestrator G2 capture commands (unblock path)

Run from repo root (PowerShell; `python` = 3.10+):

1. **S1/S3:** `python .github/scripts/secret_scan.py; echo "exit=$LASTEXITCODE"` → expect `exit=0`, `PASS -- no findings`, 3 `ALLOWLISTED PATH` lines (`apps/web/package-lock.json`, both `.env.example` files).
2. **S2 plant:** create `scratch_fake_creds.txt` with the block below **after deleting every `|` character** (values are split here so this report can never trip the scanner):

   ```
   # TEMPORARY S2 test fixture - ALL VALUES ARE INVENTED FAKES - deleted after scan
   RENDER_KEY=rnd_|FAKEFAKEFAKEFAKE1234
   SUPABASE_TOKEN=sbp_|0123456789abcdef0123456789abcdef01234567
   JWT_SAMPLE=eyJ|hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiZmFrZS1ub3QtcmVhbCJ9.FAKESIGNATUREfakesignature123456
   service_role = "fake|fakefakefakefake12345"
   -----BEGIN| PRIVATE KEY-----
   FAKEKEYMATERIALfakekeymaterialFAKEKEYMATERIAL
   -----END PRIVATE KEY-----
   AWS_ID=AKIA|FAKEFAKEFAKEFAKE
   GITHUB_TOKEN_SAMPLE=ghp_|FAKEfakeFAKEfakeFAKEfakeFAKEfake0123
   SLACK_SAMPLE=xoxb-|FAKE-1234567890-notarealtoken
   api_key = "Zq7p|L9mXv2Rt8Kn3Jd6Ws1"
   allowed_token = "Zq7p|L9mXv2Rt8Kn3Jd6Ws1"  # secretscan:allow demonstration line for pragma test - value is invented
   ```

3. **S2 detect:** `python .github/scripts/secret_scan.py; echo "exit=$LASTEXITCODE"` → expect `exit=1`, 9 masked findings (lines 2,3,4,5,6,9,10,11,12) + 1 `ALLOWLISTED LINE ...:13` pragma notice.
4. **S2 cleanup:** `Remove-Item scratch_fake_creds.txt`, rerun scanner → `exit=0`; `git status --short` clean.
5. **S6 timing:** `Measure-Command { python .github/scripts/secret_scan.py }` → expect < 60 s (predicted < 5 s).

## 6. Assumptions and defaults

- **Checkout SHA:** `08c6903cd8c0fde910a37f88322edcfb5dd907a8 # v4.2.2` taken verbatim from the M0-T004 G5 report remediation example (no network in this sandbox to independently verify the tag→SHA mapping). Reviewer with network/gh should confirm `git ls-remote https://github.com/actions/checkout v4.2.2` resolves to it.
- Secret inventory is exactly ADR-002 §3 + `render.yaml` `sync: false` keys; no new secrets invented. `RENDER_DEPLOY_HOOK_URL_{API,WORKER,CRON}` names are this task's proposal for the three production services (ADR-002 stores "one per production service" without naming them); the future deploy workflow task should adopt or amend these names.
- `ENVIRONMENT`, `SUPABASE_URL`, `SUPABASE_PROJECT_REF`, `VERCEL_ORG_ID`/`PROJECT_ID`, `SENTRY_DSN` are documented as env-scoped config / low-sensitivity, still never committed.
- Scanner scans tracked + untracked-not-ignored files (`git ls-files --cached --others --exclude-standard`) so it also protects pre-commit local use, not just CI checkouts.

## 7. Known limitations and risks

- **Regex false negatives are inherent** — unknown prefixes, split/encoded secrets, and low-entropy passwords evade any regex scanner. Mitigation documented in policy §6: owner should enable GitHub push protection + secret scanning (human action; plan-dependent on private repos).
- `.env.example` basename allowlist means a real value pasted into a `.env.example` would be skipped by the scanner (visible skip notice each run; reviewers should watch these files in diffs). Accepted per task packet S3, recorded for reviewer attention.
- Scanner Python source not yet executed anywhere (section 4); a typo would surface on the first orchestrator/CI run, not before.
- Masking shows first/last 4 chars; for very-low-entropy 13-16 char secrets this reveals up to half the value — acceptable because all classes require longer or high-entropy values.
- Workflow runs on every push including `main`; duplicate runs on PR + push are bounded by the concurrency group.

## 8. Security/provenance impact

Adds the first mechanical secret-leak control (PRD 17/25); no secrets created, referenced, or required; workflow is least-privilege read-only; no data provenance impact.

## 9. Recommended next steps

1. Orchestrator captures G2 evidence (section 5) and appends it to this report or a `M0-T005-G2-capture.md`, then moves the task to `awaiting_gate`.
2. G3/G5 reviewers: verify checkout SHA mapping, attempt scanner bypasses (encoded secrets, pragma abuse without justification), confirm allowlist output visibility, confirm no findings on full history (`git log --all -p`).
3. Track "owner enables GitHub push protection" as a human action item.
4. Future deploy-workflow task must reuse the `RENDER_DEPLOY_HOOK_URL_*` names or update `docs/SECRETS_POLICY.md` in the same change.
