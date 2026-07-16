# Gate Report

- Gate ID: G3
- Task ID: M0-T005
- Reviewer: code-reviewer (independent; did not produce the work)
- Producer: backend-engineer
- Result: **PASS** (with 7 tracked defects, none critical/high; defects 1-2 handed to G5 for severity adjudication and a follow-up rework task)
- Clean environment/worktree used: reviewed branch `task/M0-T005-secret-scan` at head `a687b21` in worktree `.claude/worktrees/agent-a885db23d6225afb2`; reviewer sandbox permitted read-only execution, so S1, the history sweep, the SHA-pin network check, and regex desk-tests were independently executed by this reviewer (not only replayed from G2 evidence)

## Acceptance criteria reviewed

Task packet `project-control/tasks/M0-T005.json` scenarios S1-S6; G3 standard (normal/boundary/missing/failure cases); ADR-002 §3 secret placement; render.yaml `sync: false` keys; low-storage policy (no persistent local artifacts).

## Steps independently executed

All commands run by this reviewer from the worktree root (read-only):

1. `git log --oneline main..HEAD` + `git diff --stat main...HEAD` → 2 commits (4886551, a687b21); 8 files, all additions: the 6 deliverables + 2 producer agent-memory files. `ci.yml`, `validate_contracts.py`, `.gitignore`, `render.yaml` untouched.
2. **S1 reproduced:** `python .github/scripts/secret_scan.py` → exit 0, `scanned 176 files in 0.42s`, 3 visible `ALLOWLISTED PATH` notices (both `.env.example` + `apps/web/package-lock.json`, each with reason), `PASS -- no findings`.
3. **SHA pin independently verified over network:** `git ls-remote https://github.com/actions/checkout refs/tags/v4.2.2` → `11bd71901bbe5b1630ceea73d27597364c9af683` (matches `secret-scan.yml:33`); `08c6903cd8c0fde910a37f88322edcfb5dd907a8` → `refs/tags/v5.0.0` (confirms the G2 mislabel finding; do not copy the M0-T004 G5 report example).
4. **Full-history sweep:** `git log --all -p | grep -cE "<all prefix classes>"` → 0 matches on any branch/commit.
5. **Regex desk-tests (python -c, in-memory, no files written):**
   - `allowed_token = "Zq7pF3kN..."` → GENERIC_RE does **not** match (no `\b` between `_` and `token`).
   - `token = "Zq7pF3kN..."` → matches; fed through an exact replica of secret_scan.py lines 131-164: pragma branch fires and prints `ALLOWLISTED LINE f.txt:1 -- justification: reviewed test fixture`; empty justification prints `(NO JUSTIFICATION GIVEN)` and still suppresses (exit 0).
   - JWT with <8-char segments not matched; realistic Supabase-style JWT matched; lowercase `akia` not matched; `SERVICE_ROLE_KEY=<unquoted 20+>` **is** matched (dedicated pattern needs no quotes); `ghp_` 36-char matched; 19-char generic value under length floor not matched.
   - Producer fixture value `Zq7pL9mXv2Rt8Kn3Jd6Ws1`: 22 chars, entropy 4.46 ≥ 3.5 → the keyword boundary is the *sole* reason the pragma line never hit.
6. Cross-checks: SECRETS_POLICY §2 inventory ↔ ADR-002 §3 rows (all 6 rows represented, storage locations identical, including "service-role key never duplicated to GitHub") ↔ `render.yaml` `sync: false` keys (7 keys, all present in `services/api/.env.example`) ↔ `apps/web/.env.example` (2 publishable names only) ↔ `.gitignore:56-58` (`.env`, `.env.*`, `!.env.example`, pre-existing, unedited).
7. Line-by-line source review of `secret_scan.py` (masking, entropy gate, placeholder gate, allowlists, exit codes, file-set selection, unreadable/binary/oversize handling) and `secret-scan.yml` (triggers, permissions, timeout, pin, no `secrets.`, no `${{ }}` in `run:`, concurrency).

## Expected versus actual

| Scenario | Expected | Actual | Result |
|---|---|---|---|
| S1 normal | exit 0, workflow-equivalent clean scan | Reproduced by reviewer: exit 0, 176 files, 0.42s, 3 visible path-allowlist notices | **PASS** |
| S2 invalid-input | exit nonzero; file/line/class listed; values masked | G2 evidence (both runs, 4886551 and a687b21): 9/9 classes detected at correct lines, exit 1, first/last-4 masking; mask() also fully asterisks values ≤12 chars (boundary verified in source lines 85-89) | **PASS** |
| S3 boundary | no false positives; allowlist documented and used, visible in output | package-lock.json path-allowlisted with printed reason AND independently zero JWT-pattern matches on its content; `.env.example` allowlisted with printed reason; SECRETS_POLICY.md names prefixes without tripping the scan (clean run proves it). Inline pragma: documented, and the visible-notice code path exists and works (reviewer-verified in-memory) but was never exercised by executed evidence — see Defect 1/adjudication | **PASS** (with evidence-gap caveat) |
| S4 missing-data | every policy secret in correct template, no values; .gitignore verified | Exact match: 7 backend names, 2 frontend names, all values empty; CI-only secrets intentionally absent and documented as such; `.gitignore:56-58` verified, not edited | **PASS** |
| S5 security | contents: read; full-SHA pins with version comments; no secrets; push+PR | All confirmed; SHA→tag mapping independently network-verified by reviewer; no expression injection into `run:`; timeout-minutes: 5; concurrency bounded | **PASS** |
| S6 regression | ci.yml untouched; runtime < 60s | Branch diff is additions-only (6 deliverables + producer memory); reviewer-measured 0.42s, G2 0.48-0.62s | **PASS** |

G3 case coverage: normal = S1; boundary = mask() short-value/entropy/length-floor desk-tests; missing/ambiguous = deleted-but-listed file handled (OSError → skip, secret_scan.py:125-126), empty file set degenerates to `scanned 0` + PASS; failure = exit 2 on `git rev-parse` failure (verified in source lines 100-109) — but see Defect 5 for the `git ls-files` failure path.

## Evidence paths

- `project-control/reports/M0-T005-G2-evidence.md` (orchestrator-captured S2 execution)
- `project-control/reports/M0-T005-producer-report.md` (read last, after independent review)
- Reviewer commands and outputs: transcribed above (steps 1-7); all reproducible read-only from the worktree

## Human-style walkthrough findings

A developer who accidentally commits any of the 9 planted classes gets a failing CI job with file:line:class and a masked value plus a remediation hint pointing at the policy's incident procedure — clear and actionable. Allowlist suppressions are visible each run for path allowlists. The policy doc is readable, correctly scoped, and honest about regex false negatives and the push-protection dependency (owner action item). The `.env.example` headers actively teach the security boundary (NEXT_PUBLIC compilation into the public bundle). No persistent artifacts written to the local device; scan is in-place read-only; scratch fixture cleanup verified in G2.

## Regression/security/provenance findings

No existing file modified; no secrets created or referenced; workflow is least-privilege. Full-history sweep clean (0 matches, all branches). Provenance: policy cites ADR-002/render.yaml/PRD sections as authoritative sources; retrieval-dated URLs inherited from ADR-002.

## Defects

1. **[medium] Generic keyword regex misses `*_token/*_secret/*_password/*_key` compound names** — `secret_scan.py:72`: `\b(?:api[_-]?key|apikey|secret|password|passwd|token)\b` cannot match after `_` (word char → no boundary), so `AUTH_TOKEN="..."`, `MY_SECRET="..."`, `DB_PASSWORD="..."`, and the producer's own fixture `allowed_token = "..."` all bypass the catch-all. This contradicts demonstrated design intent (producer report §5 expected line 13 to hit) and silently voided the pragma-path test. Repro: `python -c` desk-test above. Fix is one line (allow an optional `[A-Za-z0-9_-]*` identifier prefix before the keyword); entropy+quotes+placeholder gates keep noise controlled.
2. **[medium] Several secrets in the project's own inventory evade all pattern classes in `NAME=value` form** — `GEOCLIENT_SUBSCRIPTION_KEY` (32-hex), `VERCEL_TOKEN`, `SUPABASE_DB_PASSWORD`, `SUPABASE_DB_URL` (postgres URI — `:`/`@` are outside the generic value charset), `RENDER_DEPLOY_HOOK_URL_*` (secret URL). SECRETS_POLICY.md enumerates these exact names, so a deterministic zero-noise pattern (inventory-name assignment with non-empty value) is cheap. Within the task contract (S2 lists only the 9 required classes) but a real gap vs. policy §1 "mechanically enforced". Hand to G5.
3. **[low-medium] Basename path allowlist applies anywhere in the tree** — `secret_scan.py:35-38,117-119`: any file *named* `.env.example` or `package-lock.json` in any directory is skipped entirely, so a real value pasted into one passes CI (visible notice only). Producer disclosed this (§7). Recommend pinning exact relative paths or scanning `.env.example` for non-empty values.
4. **[low] Pragma with no justification still suppresses and exits 0** — `secret_scan.py:147-151`: prints `(NO JUSTIFICATION GIVEN)` but allows. Policy §5 delegates to code review; mechanical failure on empty justification would be stronger. Design choice, disclosed.
5. **[low] `git ls-files` failure exits 1, not 2** — `secret_scan.py:92-97`: `check=True` inside `list_files` raises uncaught `CalledProcessError` → interpreter exit 1 (traceback), indistinguishable from a findings exit by code alone. Contract (line 19) reserves 2 for execution errors. Only the `rev-parse` failure is mapped to 2.
6. **[low] UTF-16 text files are skipped as binary** — `secret_scan.py:127`: null-byte heuristic skips UTF-16 (the default encoding of Windows PowerShell 5.1 `>` redirection), so a secret echoed into such a file bypasses silently. Note for G5 / policy §6 residual-gap list.
7. **[low] Oversized (>2MB) and binary files skipped silently** — no notice analogous to `ALLOWLISTED PATH`, reducing suppression visibility.

Producer-report accuracy note (not a deliverable defect): §3-S2 and §5-step-3 predicted an `ALLOWLISTED LINE ...:13` notice that could not occur with that fixture; G2 evidence line 32 ("correctly NOT flagged") is true for the wrong reason — the line was never a hit at all. Superseded by the G2 deviation note and this report.

## Adjudication of the invisible-pragma deviation (G2 §Deviations item 1)

**Not a missing feature; acceptable with follow-up.** The visible-notice code path exists (`secret_scan.py:147-151` collect, `161-164` print, format exactly `ALLOWLISTED LINE <path>:<line> -- justification: ...`) and was verified working by an in-memory replica of the exact per-line logic. The notice never appeared in G2 because the fixture's pragma line never produced a hit — root cause is Defect 1's boundary bug, proven by desk-test (`allowed_token` no-match; same value with `token =` matches, suppresses, and prints the notice). Consequence: the pragma suppression path has never been executed against the real script. Required follow-up (bundle with Defect 1 fix): correct the regex, change the S2 fixture pragma line to a form that hits (e.g. `token = "<fake>" # secretscan:allow ...`), and re-capture S2 showing the visible `ALLOWLISTED LINE` notice. S3 as written is satisfied via the path allowlist ("path **or** inline pragma"), so this does not fail the gate.

## Bypass attempts and outcomes

| Attempt | Outcome |
|---|---|
| Pragma with no justification | Suppresses, exits 0, prints `(NO JUSTIFICATION GIVEN)` — Defect 4 |
| Secret split across lines | Not caught — inherent to line-based regex, disclosed (§7) |
| Real secret in a new `anything/.env.example` | Not caught (basename allowlist) — Defect 3, visible notice printed |
| Lowercase `akia...` | Not caught — non-standard form, acceptable |
| JWT with <8-char segments | Not caught — real Supabase JWTs have long segments, acceptable |
| Generic value 19 chars / entropy <3.5 | Not caught — disclosed threshold design |
| `AUTH_TOKEN="<22-char entropy 4.46>"` | Not caught — Defect 1 (should be caught per design intent) |
| Unquoted generic `API_KEY=<value>` | Not caught — disclosed quotes-required design (`secret_scan.py:67-69`); note dedicated `service_role` pattern correctly needs no quotes |
| Secret in UTF-16 file | Not caught — Defect 6 |
| `SUPABASE_DB_URL=postgres://...` / deploy-hook URL | Not caught — Defect 2 |

## Required rework

None gate-blocking. Orchestrator should open one small follow-up task: fix Defect 1 (one-line regex), re-fixture and re-capture the pragma-visible-notice evidence, and let G5 decide whether Defects 2-4/6 fold into the same task or a later hardening pass.

## Reviewer conclusion

**PASS.** All six acceptance scenarios pass on independently reproduced or independently verified evidence, the branch diff is exactly the contracted deliverables plus producer memory, the SHA pin is network-verified correct, full history is clean, and docs/templates/inventory/ADR-002/render.yaml are mutually consistent. The defects found are hardening gaps in the catch-all layer, not failures of any contracted scenario; the one behavior that contradicted producer intent (pragma notice) traces to a reproducible one-line regex bug with a defined follow-up.

**For the G5 security reviewer, specifically:**
1. Adjudicate Defects 1-2 severity (catch-all misses common compound names and several inventory secrets — postgres URIs, hex subscription keys, secret URLs).
2. Defect 3: basename allowlist as an exfiltration channel that keeps CI green (notice-only control).
3. Defect 6: UTF-16 bypass, especially relevant on this Windows/PowerShell host.
4. Confirm the "owner enables GitHub push protection" human action item is tracked — the policy's stated compensating control for all regex false negatives.
5. Workflow posture is clean (contents: read, no secrets, no injection sinks, verified pin), so G5 effort is best spent on the scanner's negative space, not the workflow.
