# G5 Security Review — M0-T116 (second golden re-certification)

**Verdict: PASS**
**Frozen review identity:** `869b313c583cc98107ce6dda96cf2e6973c9babd` (verified == HEAD, branch `control/D-024-fable-codex-loop`)
**Unit span reviewed:** `87091a5..869b313` (4 commits)
**Reviewer:** security-reviewer (t116-g5-sec), read-only. 2026-08-29.

## Summary
M0-T116 is a governance/re-certification unit with **zero code changes**. The diff touches only `project-control/**` (10 files: 2 gates, 5 reports, evidence map, task file, state.json). No application/runtime code, no secrets, no activation or resume action. The certified identity (golden-pack blob `cf03caaa`, supervisor tree `7487901c`) matches at HEAD, so the "re-run only" claim is provably true. The activation package still activates nothing and correctly gates the R276 resume on this unit's acceptance plus the full preflight. All external posture checks pass. I found no critical/high/medium/low security defects; one INFO observation below.

## Findings by severity
- **Critical / High / Medium / Low:** none.
- **INFO-1 (runtime state label):** the supervisor `status` reports `state: PREFLIGHT` with `trigger=owner_cleared_pause`, not a hard "STOPPED" string. However `mode: none`, `limited-auto: off`, `pending effects: 0`, `queued questions: 0`, `stop intent: none`, and no child subagents recorded — i.e. the loop is **not executing** and no resume occurred. The recertification report's phrasing ("currently stopped with no live process and no pending effects") is materially accurate; PREFLIGHT is the pre-resume staged state, not a running loop. No action required.

## Evidence per scope item

**1. Full diff read; scope + secret check — PASS.**
`git diff --stat 87091a5..869b313`: all 10 files under `project-control/**` (gates/M0-T116-G0.json, gates/M0-T116-G2.json, reports/M0-T096-activation-package.md, reports/M0-T116-G0-readiness.md, reports/M0-T116-G2-self-check.md, reports/M0-T116-evidence-map.json, reports/M0-T116-recertification.md, reports/M0-T116.json, state.json, tasks/M0-T116.json). Read every hunk. Added content is prose + SHAs + tree/blob digests + ISO timestamps only — no keys, tokens, credentials, URLs-with-secrets. state.json adds `M0-T116` to the in-review list and bumps `updated_at`. tasks/M0-T116.json is a re-indent plus control-plane transitions (backlog→awaiting_gate, producer set, progress_percent 0→85, one progress_log entry); allowed_paths and forbidden_paths **unchanged** (allowed_paths still restricts to golden pack + recertification report + activation package). No language in any added line activates or resumes the loop — the reports repeatedly condition resume on acceptance + preflight.

**2. R248/R273 posture — PASS.**
`git diff --name-only 87091a5..869b313 -- tools/ apps/ services/ packages/ supabase/ .claude/` → empty. No `.claude/**`, no dependency manifests (no requirements.txt/package*.json/lockfiles in span), no MCP config, no supervisor code, no journal-editing tooling touched. `gh pr view 241` → `state=OPEN, mergedAt=null, mergeable=MERGEABLE, headRefName=task/M5-T002-scenario-endpoint` — PR #241 remains open/unmerged as required.

**3. Activation-package honesty (second refresh) — PASS.**
Compared items 10–12 + the item-12 refresh paragraph across the span. Item 10 updates the certified identity to the post-repair `f89aa29` / tree `7487901c` / golden blob `cf03caaa` (41 tests). Item 11 lists the per-unit reviewer waves and states the second re-certification is "the acceptance the R276 resume waits on." Item 12's added paragraph describes the **already-past** owner-exercised first live limited-auto run (Amendment 9) that stopped fail-closed and exposed the seam defect, then states: "Resume of the authorized loop is gated on M0-T116 acceptance + the full R276 preflight." Recertification report §4 is explicit: "The package still activates nothing; the R187/R595 activation DECISION was already exercised by the owner (Amendment 9) — what remains gated by THIS unit's acceptance is the R276 RESUME of the authorized loop." No sentence implies the resume already happened; the past live run and the future gated resume are cleanly distinguished. Evidence map row D-024-R276 records "HOLD IN FORCE and honored."

**4. Gitleaks over the span — PASS.**
`gitleaks.exe detect --source . --no-banner --redact --log-opts "87091a5..869b313"` → "4 commits scanned … no leaks found", exit 0.

**5. CI evidence integrity — PASS.**
`gh api repos/.../commits/07233f520a1bf1ed29eb54a13612cea544af7527/check-runs`: `total_count=20`, all `status=completed`, all `conclusion=success`, none skipped/neutral. Includes `supervisor-bridge (pytest tools/test_agent_supervisor_*.py)` (whole-suite job) and `Scan repository for credentials` (credential scan), both success. This is the SHA pinned in the M0-T116 progress_log and reports.

**6. Supervisor runtime state — PASS (loop not running).**
`python -m tools.agent_supervisor status --checkout <ctl24>` (exit 0): `state=PREFLIGHT, mode=none, limited-auto=off, pending effects=0, queued questions=0, stop intent=none`, no child subagents recorded; journal integrity ok (sqlite_integrity=ok, 5 transitions), audit chain ok (head seq 16). No live executing loop — corroborates the unit's claim that nothing was resumed. (See INFO-1 on the PREFLIGHT label.)

**Re-run-only integrity (supporting §1/§4):** `git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py` = `cf03caaa261da9726c7a12fc1676acb68851bac1` and `git rev-parse HEAD:tools/agent_supervisor` = `7487901cea729f5c254f98c8f7dcf859eb64e2c5` — both match the certified identity byte-for-byte, confirming no code slipped in under a "re-run only" claim.

## Domain-specific security checks
Cross-tenant isolation, service-role secrecy, private storage, SSRF/injection defenses, upload controls, prompt-injection defenses, least privilege, and log redaction: **not applicable to this diff** — it changes no application/runtime code, RLS, storage, network, or handler surface. The certified runtime identity is unchanged (verified above), so the existing security posture of the supervisor is untouched by this unit. Log-redaction check on the added control-plane prose passed (no secrets to redact; only SHAs/digests/timestamps).

## Commands run (all read-only)
- `git rev-parse HEAD` / `--abbrev-ref HEAD`
- `git diff --stat 87091a5..869b313`; `git log --oneline 87091a5..869b313`
- `git diff 87091a5..869b313 -- <each file>`; `git show 869b313:<report files>`
- `git diff --name-only 87091a5..869b313 -- tools/ apps/ services/ packages/ supabase/ .claude/`
- `git rev-parse HEAD:tools/test_agent_supervisor_golden_run.py`; `HEAD:tools/agent_supervisor`
- `gh pr view 241 --json state,mergedAt,mergeable,headRefName`
- `gitleaks.exe detect --source . --no-banner --redact --log-opts "87091a5..869b313"`
- `gh api repos/{owner}/{repo}/commits/07233f5.../check-runs`
- `python -m tools.agent_supervisor status --checkout "C:\Users\MLFLL\Downloads\nyc-zoning\ctl24"`

**G5 VERDICT: PASS** — no security defects; prohibitions (R248/R273/R276) honored; activation package remains honest and resume-gated; certified identity intact; CI clean; loop not running.
