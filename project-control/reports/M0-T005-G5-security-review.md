# Gate Report

- Gate ID: G5 (security and privacy)
- Task ID: M0-T005
- Reviewer: security-reviewer (independent; did not produce the work; did not perform G3)
- Producer: backend-engineer
- Result: **PASS** (conditional on one mandatory follow-up rework task, scope in "Required rework"; no gate-blocking defect)
- Clean environment/worktree used: branch `task/M0-T005-secret-scan` at head `a687b21` in `.claude/worktrees/agent-a885db23d6225afb2`; reviewer independently executed S1, the SHA-pin network check, and regex desk-tests read-only (no files written, nothing modified)

## Acceptance criteria reviewed

Task packet `project-control/tasks/M0-T005.json` S1-S6 (security lens); G5 catalog items from `docs/GATES_AND_CHECKPOINTS.md`; ADR-002 §3 secret placement; PRD §14.3/§17/§25; G3 hand-off list (adjudicate D1-D4, D6; verify push-protection human action; threat-model the scanner as a control).

## Steps independently executed

1. `git log --oneline main..HEAD` + `git diff --stat main...HEAD` → 2 commits (4886551, a687b21), 8 files, **additions only**: the 6 contracted deliverables + producer memory + producer report. No existing file touched; `ci.yml`, `render.yaml`, `.gitignore`, `docs/adr/**` untouched (forbidden paths respected).
2. **S1 reproduced by this reviewer:** `python .github/scripts/secret_scan.py` from the worktree → `scanned 176 files in 0.47s`, 3 visible `ALLOWLISTED PATH` notices with reasons, `PASS -- no findings`.
3. **SHA pin independently network-verified:** `git ls-remote https://github.com/actions/checkout refs/tags/v4.2.2` → `11bd71901bbe5b1630ceea73d27597364c9af683`, exact match with `secret-scan.yml:33`. (Third independent verification after G2 and G3; the mislabeled `08c6903` = v5.0.0 is confirmed corrected.)
4. **Adversarial regex desk-tests (in-memory `python`, nothing written):**
   - `AUTH_TOKEN="<22-char entropy 4.46>"` → no match; `DB_PASSWORD="..."` → no match; bare `token="..."` → match (confirms G3 Defect 1).
   - `GEOCLIENT_SUBSCRIPTION_KEY="<32-hex>"` (quoted AND unquoted) → no match by generic OR any dedicated class. Note: the hex value's entropy is 3.93 ≥ 3.5, and `key` alone is not a keyword — so even the Defect-1 one-line fix does NOT catch this secret; the follow-up needs an inventory-name class too.
   - `VERCEL_TOKEN=<unquoted>` → no match (quotes required by generic).
   - `SUPABASE_DB_URL=postgresql://user:pass@host/db` → no match by any class (`:`/`@` outside generic charset; no URI pattern).
   - `RENDER_DEPLOY_HOOK_URL_API=https://...` → no match by any class. (All confirm G3 Defect 2.)
5. Line-by-line security review of `secret_scan.py` (masking, entropy/placeholder gates, allowlists, binary heuristic, subprocess usage — fixed argv arrays, no shell=True, no network) and `secret-scan.yml` (triggers, permissions, no `secrets.` references confirmed by grep, no `${{ }}` inside `run:`, concurrency expressions used only in the group key — not a shell sink).
6. Grep for live `secretscan:allow` pragmas in scanned files → none (references exist only in the scanner's own definition, the policy doc, and the producer report).
7. Cross-checks: policy §2 inventory ↔ ADR-002 §3 (verified row by row, incl. "service-role key in Render only, never duplicated to GitHub/Vercel"); templates ↔ inventory (7 backend names + 2 frontend publishable names, all values empty); `.gitignore:56-58` (`.env`, `.env.*`, `!.env.example`) verified unedited; `docs/HUMAN_ACTIONS_REQUIRED.md` checked for the push-protection item (see Finding F2).
8. Verified G2 evidence (`project-control/reports/M0-T005-G2-evidence.md`, both runs at 4886551 and a687b21): 9/9 planted classes detected with first/last-4 masking, cleanup verified, 0.48-0.62s timing.

## Expected versus actual — G5 checklist

| G5 item | Result | Evidence |
|---|---|---|
| RLS / cross-tenant isolation | N/A | No runtime/tenant code in scope; policy correctly defers anon-key safety to RLS (§2 row 4) |
| Service-role secrecy | PASS | Policy §2 row 1 exactly matches ADR-002 §3 row 1: Render env (`sync: false`) only, never GitHub/Vercel/frontend/CI; `services/api/.env.example:26-29` warning; frontend template §"SECURITY BOUNDARY" forbids it under apps/web with or without NEXT_PUBLIC_ prefix |
| Private storage | N/A | No storage buckets in scope |
| SSRF / injection defenses | PASS (note F1) | Scanner: stdlib only, zero network, subprocess argv arrays, no shell=True, no eval/exec. Workflow: no `${{ }}` in `run:`; expressions only in concurrency group key (not a shell sink) |
| Upload controls | N/A | No uploads in scope |
| Prompt-injection defenses | N/A | No AI component; scanner is deterministic |
| Least privilege | PASS | `permissions: contents: read` (secret-scan.yml:18-19); zero `secrets.` references; `timeout-minutes: 5`; bounded concurrency; single action pinned to network-verified full SHA `11bd719...` = v4.2.2; no setup actions, installs, or network in the job |
| Sensitive-log redaction | PASS | `mask()` first/last-4 (full asterisks ≤12 chars) verified in source lines 85-89 and in G2 output for all 9 classes; scanner never re-prints a full candidate value; policy §3.2 forbids echoing env values (PRD §25) |
| Dependency vulnerabilities | PASS | Python stdlib only; one SHA-pinned action; no third-party scan action (deliberate — no license/secret/supply-chain dependency) |
| No secrets in deliverables / history | PASS | Reviewer-run clean scan; G3's full-history sweep (0 matches, all branches); templates values-empty; policy/docs contain names and pattern prefixes only |
| Secret-detection efficacy (negative space) | PASS with defects | D1/D2 confirmed by reviewer desk-tests — Medium, mandatory follow-up (below) |

## Human-style walkthrough findings

Covered by G3 (PASS). From the security angle: a developer who leaks any of the 9 dedicated classes gets file:line:class + masked value + a remediation hint pointing at the policy's incident procedure, whose ordering is correct — **rotate first**, then update storage, then scan history, then record, and it explicitly states history rewriting does not un-leak a value. The incident procedure is sane and matches provider realities (rotation locations per §2 match each provider's actual dashboard flow).

## Regression/security/provenance findings — threat model of the scanner as a control

**Who can weaken the control?** The scanner, its allowlists, and the workflow live in the same repository a PR modifies. A malicious/compromised PR can gut `PATTERNS`, extend `PATH_ALLOWLIST`, pragma its own lines, or delete the workflow — and the weakened scanner will pass its own scan, keeping CI green. This is inherent to any repo-local control, not a defect of this implementation. Mitigations, in order of strength:
1. **GitHub push protection / secret scanning** (server-side, not modifiable from repo content) — the designated compensating control; currently only *recommended* in policy §6, not yet tracked in the canonical human-action queue (Finding F2).
2. **Branch protection with required review on `main`** — assumed by the project's gate process; not verified as enabled (owner-permission setting). Any diff touching `.github/scripts/secret_scan.py`, `.github/workflows/secret-scan.yml`, or adding `secretscan:allow` pragmas deserves explicit reviewer attention; policy §5 already instructs reviewers to check pragma justifications.
3. The project's own G3/G5 gate process for changes to these files.
Residual risk accepted and now documented here; it does not block a detective control of this class.

**Can the scan job be poisoned via filenames?** Partially — see Finding F1. Findings print repo-relative paths verbatim; `git ls-files -z` delivers raw bytes and Linux runners permit `\n` in filenames, so a committed filename containing a newline + `::notice ...`/`::add-mask::...` could emit GitHub workflow commands from the scan job's log. Blast radius is minimal: the job holds no secrets, `GITHUB_TOKEN` is contents:read, and the dangerous commands (set-env/set-output) are disabled in current runners — worst case is log-annotation spoofing or masking strings in this job's own log. Low; fix is one `repr()`-style sanitization of printed paths.

**Provenance:** policy cites ADR-002 §3 + `render.yaml` as authoritative placement sources and PRD sections; ADR-002 carries retrieval-dated official URLs. Consistent.

## Defects — severity adjudication of G3 hand-off

| # | Defect | G5 severity | Block? | Rationale |
|---|---|---|---|---|
| D1 | Generic regex misses compound names (`AUTH_TOKEN=`, `DB_PASSWORD=`, `MY_SECRET=`) — `secret_scan.py:72` `\b` cannot fire after `_` | **Medium** | No — mandatory follow-up | Compound `NAME_TOKEN/_PASSWORD/_SECRET` is the *most common* real-world leak form, so the catch-all layer largely fails at its purpose. Not blocking because: (a) every contracted S2 class (the project's primary secret shapes — Supabase JWTs, `sbp_`, `rnd_`, `ghp_`, PEM, AKIA) is caught by dedicated patterns independent of this bug; (b) zero real secrets exist yet (B-001..B-004 all open); (c) the fix is one line and must land before the first real credential is provisioned. Reviewer-confirmed by desk-test. |
| D2 | Inventory secrets evade all classes in `NAME=value` form (`GEOCLIENT_SUBSCRIPTION_KEY` 32-hex, `VERCEL_TOKEN`, `SUPABASE_DB_PASSWORD`, `SUPABASE_DB_URL` postgres URI, `RENDER_DEPLOY_HOOK_URL_*`) | **Medium** | No — mandatory follow-up (same task as D1) | Reviewer-confirmed all five evasions, including that the D1 fix alone does NOT cover them (`key` not a keyword; unquoted values never match; URI charset excluded). Policy §1's "mechanically enforced" is overstated until fixed. An inventory-name pattern class is deterministic and zero-noise because policy §2 already enumerates the exact names, and those names carrying any non-placeholder value in Git is *always* a violation. Same non-blocking rationale as D1. |
| D3 | Basename allowlist matches `.env.example`/`package-lock.json` anywhere in the tree — exfiltration channel that keeps CI green (visible notice only) | **Low-Medium** | No — same follow-up | Requires a deliberate insider action (creating a decoy allowlisted filename), which the same actor could achieve more quietly via pragma or value-splitting; the `ALLOWLISTED PATH` notice prints on every run, so it is the *loudest* of the bypasses. Fix: pin exact relative paths and content-scan `.env.example` files for non-empty assignments instead of skipping them. |
| D4 | Pragma with empty justification suppresses and exits 0 (`secret_scan.py:147-151`) | **Low** | No — same follow-up | Disclosed design delegating to code review; but policy §5 itself says an unjustified pragma "should fail code review" — enforcing it mechanically (exit 1 on `(NO JUSTIFICATION GIVEN)`) is a two-line change and removes reliance on reviewer vigilance. |
| D6 | UTF-16 files skipped as binary (`secret_scan.py:127` null-byte heuristic) — the default encoding of PS 5.1 `>` on this project's own dev host | **Medium-Low** | No — same follow-up | Real on this Windows host (already a documented project foot-gun: PS 5.1 redirection writes UTF-16LE, whose interleaved NULs trip the binary skip). Silent, needs no attacker intent — an owner `echo $env:KEY > f.txt` artifact would sail through. Fix: detect UTF-16 BOM and decode before the binary heuristic. Compensated meanwhile by push protection (once enabled) and review. |
| D5, D7 (G3) | ls-files failure exit code; silent binary/oversize skips | **Low** | No | Robustness/visibility, not exploitable paths; fold into the follow-up opportunistically. |

## Additional G5 findings (this reviewer)

1. **[Low] Workflow log-annotation injection via filenames** — `secret_scan.py:160,164,169` print raw repo-relative paths; a committed filename containing a newline (legal on Linux runners; `ls-files -z` preserves it) can start an output line with `::notice`/`::add-mask` etc., spoofing annotations or masking strings in the scan job's log. No secret/privilege impact (contents: read, no secrets in job, set-env disabled by runner). Fix in follow-up: strip/escape control characters (`\n`, `\r`, `\x00-\x1f`) from printed paths.
2. **[Low] Push-protection human action item not in the canonical queue** — policy §6 records the recommendation (satisfying the letter of the requirement), but `docs/HUMAN_ACTIONS_REQUIRED.md` has no entry and there is no `project-control/blockers/` record, despite that file stating every action maps to a blocker record. This is the **stated compensating control for every regex false negative above**, so it must not live only inside a policy subsection. `docs/HUMAN_ACTIONS_REQUIRED.md` was outside the producer's allowed paths — this is an **orchestrator** action, not producer rework: add "Enable GitHub secret scanning + push protection (Settings → Code security)" with a blocker ID, noting plan-gating on private repos per policy §6.
3. **[Info] Self-modifiable control residual risk** — documented in the threat model above; no code change required, but branch protection on `main` (owner-permission) should be confirmed/tracked alongside Finding 2, since it is the second mitigation layer.
4. **[Info] `mask()` reveals 8 characters of values ≥13 chars** — for the shortest matchable values (e.g. 20-char `rnd_` minimum) that is 40% of the credential. Acceptable for triage (industry-standard style) and strictly better than full echo; not a defect. Optional hardening: hash-fingerprint instead of first/last-4.
5. **[Info] Vercel rows may become moot** — `docs/HUMAN_ACTIONS_REQUIRED.md` §3 records the owner preference to serve the frontend from Render (ADR-004/M0-T011 pending). Policy §2 correctly mirrors ADR-002 as it stands today; when ADR-004 lands, the inventory table must be updated in the same change (policy §2 last paragraph already mandates this discipline).

## Required rework

None gate-blocking. **One mandatory follow-up task (recommend `M0-T005-R1`, small, single producer, G3+G5 re-check on the diff only), to be accepted before the first real credential is provisioned (B-001/B-002/B-004) or M0 exit, whichever first.** Scope — `.github/scripts/secret_scan.py`, `docs/SECRETS_POLICY.md` §5 (one sentence), and re-captured evidence only:

1. Generic regex: allow compound identifiers — optional `[A-Za-z0-9_-]*` prefix before the keyword group (D1).
2. New zero-noise pattern class "inventory-name assignment": the exact names from policy §2 (`SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`, `SUPABASE_DB_PASSWORD`, `SUPABASE_ACCESS_TOKEN`, `GEOCLIENT_SUBSCRIPTION_KEY`, `ANTHROPIC_API_KEY`, `VERCEL_TOKEN`, `RENDER_DEPLOY_HOOK_URL_\w*`, `SENTRY_DSN`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`) followed by `[:=]` and a non-empty, non-placeholder value — quoted or unquoted (D2).
3. Postgres URI class: `postgres(?:ql)?://[^:/\s]+:[^@\s]+@` (D2).
4. Path allowlist → exact relative paths (`services/api/.env.example`, `apps/web/.env.example`, `apps/web/package-lock.json`); additionally content-scan `.env.example` files for `NAME=<non-empty>` instead of skipping them wholesale (D3).
5. Empty pragma justification → counts as a finding, exit 1 (D4).
6. UTF-16/UTF-16BE BOM detection before the null-byte binary heuristic (D6).
7. Sanitize control characters in printed paths (Finding F1).
8. Opportunistic: map `git ls-files` failure to exit 2 (G3-D5); print a skip notice for oversized/binary files (G3-D7).
9. Re-fixture S2 so the pragma line actually hits (e.g. `token = "<fake>" # secretscan:allow reviewed demo`), and re-capture evidence showing the visible `ALLOWLISTED LINE` notice plus new fixture lines for: compound name, inventory hex key (quoted and unquoted), postgres URI, deploy-hook URL, UTF-16 file.

**Separate orchestrator actions (not producer rework):** (a) add the GitHub push-protection/secret-scanning enablement to `docs/HUMAN_ACTIONS_REQUIRED.md` with a blocker record (Finding F2); (b) track/confirm branch protection on `main` in the same entry (Finding F3).

## Reviewer conclusion

**PASS.** Every G5 checklist item in scope passes on independently reproduced or independently verified evidence: least-privilege workflow with a network-verified SHA pin and zero secret references, no injection sinks, stdlib-only no-network scanner with verified masking, names-only templates exactly matching a policy inventory that is row-for-row consistent with ADR-002 §3 (service-role key confined to Render), a correct rotate-first incident procedure, and a clean tree and full history. The confirmed weaknesses (D1/D2/D3/D4/D6, F1) are all in the detective control's negative space, are honestly disclosed by the policy's own false-negative statement, are compensated by the push-protection control once the owner enables it, and have a small, precisely scoped follow-up. None permits a secret to be *placed* correctly and still leak; they permit an incorrectly placed secret to go undetected by this one layer — which the policy explicitly does not claim to be the only layer. Gate passes conditional on the follow-up task being contracted and the push-protection human action being formally tracked.
