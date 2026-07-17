<!--
PROVENANCE: This is the security-reviewer's G3 return for M0-T012, saved VERBATIM by the
orchestrator from the agent-return channel (transport entity-decoding only, per the
report-preservation rule in .claude/rules/project-control.md). Reviewer agent id
abf7b72a6d32dc19c; review performed read-only against worktree .claude/worktrees/M0-T012
@ e5f6ea4 with live gh api re-resolution. Saved 2026-07-17 by the orchestrator.
-->
# Gate Report

- Gate ID: G3 (security walkthrough, G5-scope checklist applied)
- Task ID: M0-T012 — CI hygiene: pin all GitHub Actions to reviewed immutable commit SHAs
- Reviewer: security-reviewer (independent; did not produce the work)
- Producer: backend-engineer
- Result: **PASS** — zero blocking defects
- Clean environment/worktree used: yes — `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T012`, branch `task/M0-T012-sha-pinning` @ `e5f6ea4`, one producer commit on base `2678509`. Review order: packet → G2 evidence → diff → independent live re-resolution → producer report LAST. All SHA/release/CI evidence below was resolved live by this reviewer via `gh api`; nothing was accepted from the producer's outputs.

## Acceptance criteria reviewed

Binding packet S1–S6 from `project-control/tasks/M0-T012.json` (main checkout), plus the reviewer directive's supply-chain checks (independent tag re-resolution, official-org provenance, same-major-line rule, no ride-along changes, no new attack surface).

## Steps independently executed

1. `git log`/`git status`/`git diff 2678509 --stat` in the worktree — exactly 3 files changed: `.github/workflows/ci.yml` (+10/−10), `.github/workflows/generate-lockfile.yml` (+2/−2), `project-control/reports/M0-T012-producer-report.md` (+182 new). Worktree clean.
2. `git diff 2678509 -- .github` — read every hunk in full.
3. THE CRITICAL CHECK — live tag re-resolution from scratch: `gh api repos/actions/<name>/git/ref/tags/<vX.Y.Z>` for all four tags.
4. Same-major latest-release verification: `gh api repos/actions/<name>/releases?per_page=100` filtered to the in-use major (after establishing that `releases/latest` returns different MAJOR lines — v7.0.0 / v7.0.0 / v6.3.0 / v7.0.1 — and is therefore not usable alone for S3).
5. `grep -nE "uses:.*@v[0-9]"` on both files; `grep -n "uses:"` on all three workflow files; `uniq -c` pin-consistency count.
6. `git diff 2678509 -- .github/workflows/secret-scan.yml` — empty (untouched).
7. PyYAML parse of both changed files in the worktree + parse of base `ci.yml` via `git show 2678509:...`; compared job names, step counts, triggers, and permissions.
8. Live S5 verification: `gh api repos/martin10101/nyc-buildability/actions/runs/{29554930113,29554930067}` + per-job conclusions.
9. Read producer report last and cross-checked every claim against my own evidence.

## Expected versus actual

**Critical check — independent SHA re-resolution (all four MATCH, byte-for-byte):**

| Action | Tag | Reviewer-resolved SHA (live, 2026-07-17) | SHA written in workflows | Match | Latest in same major? |
|---|---|---|---|---|---|
| actions/checkout | v4.3.1 | `34e114876b0b11c390a56381ad16ebd13914f8d5` | same (6 refs) | YES | YES (v4.x list: v4.3.1 > v4.3.0 > v4.2.2) |
| actions/setup-node | v4.4.0 | `49933ea5288caeca8642d1e84afbd3f7d6820020` | same (3 refs) | YES | YES (v4.4.0 newest v4.x) |
| actions/setup-python | v5.6.0 | `a26af69be951a213d495a4c3e4e4022e16d87065` | same (2 refs) | YES | YES (v5.6.0 newest v5.x) |
| actions/upload-artifact | v4.6.2 | `ea165f8d65b6e75b540449e92b4886f43607fa02` | same (1 ref) | YES | YES (v4.6.2 newest v4.x) |

- Annotated-tag handling: all four refs returned `object.type: "commit"` (lightweight tags) — the returned `object.sha` IS the commit SHA; no dereference step was required, and the producer's identical claim is confirmed.
- **Official-org provenance (explicit):** each resolution was performed against the API path `repos/actions/<name>/git/ref/tags/...` — the lookup itself proves each tag exists in the official `actions` GitHub organization repository and points at exactly the pinned SHA. No third-party or fork repo is involved.
- Malicious/mistaken-pin hypothesis: rejected on evidence — every pinned SHA equals the official tag target, every version is the newest release of the already-in-use major line (no downgrade, no major bump), and the branch CI run proves the SHAs resolve and execute.

**Directive checks 1–6:**

1. No ride-along changes: every hunk in `git diff 2678509 -- .github` is a single-line `uses:` `-`/`+` substitution pair (12 total: ci.yml lines 29, 30, 58, 59, 64, 90, 106, 107, 125, 139; generate-lockfile.yml lines 19, 20). Diff stat = the 2 workflow files + producer report only. No formatting, dependency, comment, or functional edits anywhere. Owner no-ride-along directive satisfied. PASS.
2. Zero remaining tag refs on `uses:` lines in both files (grep: NONE). `secret-scan.yml` byte-identical to base and still pinned at `11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2` (I re-resolved v4.2.2 implicitly via the producer's method being reproduced by my own resolutions; the file itself is untouched, which is the binding requirement). PASS.
3. Consistency (S6): exactly 4 distinct pin strings across all 12 refs — checkout ×6, setup-node ×3, setup-python ×2, upload-artifact ×1. No mixed pins of the same action. PASS.
4. YAML parses (PyYAML) for both files; job set `['api','contracts','control-plane','web','web-e2e']` and per-job step counts `{web:6, web-e2e:10, api:5, contracts:3, control-plane:2}` are identical to base `2678509`; `generate-lockfile.yml` job `lockfile` (4 steps) unchanged. PASS.
5. S5 verified LIVE (not from the evidence file): CI run 29554930113 = `completed/success` at `head_sha e5f6ea4583...` on `task/M0-T012-sha-pinning`, all 5 CI jobs individually `success` (control-plane, web, api, web-e2e, contracts); secret-scan run 29554930067 = `completed/success` at the same SHA. The pinned SHAs demonstrably resolve and run. PASS (see finding 3 on "6 jobs" wording).
6. No new attack surface: no new actions introduced (same four actions previously referenced by tag); triggers unchanged (ci.yml: push/pull_request; generate-lockfile.yml: workflow_dispatch); permissions unchanged (ci.yml top-level `contents: read`; generate-lockfile.yml top-level `contents: write` — pre-existing in base, untouched by this diff). PASS.

## Evidence paths

- Worktree diff: `git -C "C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T012" diff 2678509 -- .github`
- Packet: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T012.json`
- G2/S5 evidence: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T012-G2-evidence.md`
- Producer report: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T012\project-control\reports\M0-T012-producer-report.md`
- Live reproduction commands: `gh api repos/actions/checkout/git/ref/tags/v4.3.1` (and the three siblings); `gh api "repos/actions/checkout/releases?per_page=100" --jq '[.[].tag_name | select(startswith("v4."))][0:3]'` (and siblings); `gh api repos/martin10101/nyc-buildability/actions/runs/29554930113/jobs --jq '[.jobs[] | {name, conclusion}]'`

## Human-style walkthrough findings

A downstream consumer (CI itself) is the "user" here: the branch CI run at the exact reviewed commit is green across every job including the Playwright e2e job that exercises checkout, setup-node, setup-python, and upload-artifact — all four pinned actions executed successfully in anger, not just parsed.

## Regression/security/provenance findings

G5 checklist disposition for this diff (CI-workflow-only change):
- **Supply chain / least privilege:** materially improved — 12 mutable tag refs replaced with immutable commit SHAs; workflows are no longer exposed to tag-rewrite attacks on the `actions` org tags. Closes the recorded G5 M0-T005-R1 / M2-T001 F1 debt. Workflow permissions remain least-privilege and unchanged.
- **Service-role secrecy, cross-tenant/RLS isolation, private storage, SSRF/injection, upload controls, prompt-injection defenses, log redaction:** N/A — the diff touches no application code, no secrets, no storage, no network calls, no AI pipeline, no logging. Verified by the exhaustive hunk inspection: nothing outside `uses:` lines changed.
- **Provenance:** each pin carries a `# vX.Y.Z` trailing comment matching the established secret-scan.yml style, preserving human-readable version provenance next to the immutable SHA.

## Defects

1. **(Non-blocking, informational)** Packet inventory said 11 tag refs; repository reality was 12 (fifth `checkout@v4` in the M2-T001 `web-e2e` job). The producer disclosed this in §1 of its report and pinned all 12, which is the correct reading of S1's zero-tag-refs rule. No action required beyond the orchestrator noting the packet inventory was stale.
2. **(Non-blocking, informational)** `generate-lockfile.yml` carries top-level `permissions: contents: write`. Pre-existing, `workflow_dispatch`-only, out of this task's scope, and unchanged by this diff — recorded only so it is not mistaken for a ride-along. Optional future hardening candidate.
3. **(Non-blocking, informational)** S5/G2 wording says "all 6 jobs"; the CI workflow contains 5 jobs, and the 6th green check is the separate secret-scan workflow. Both runs are `success` at `e5f6ea4`, so the substance of S5 is fully satisfied; only the phrasing conflates workflow jobs with branch checks.

## Required rework

None.

## Reviewer conclusion

**PASS.** All four claimed pins were independently re-resolved live from the official `actions` org and match the workflow files byte-for-byte; all are lightweight tags requiring no dereference; each version is the latest release of its same major line; all 12 refs use exactly 4 consistent pins; the diff contains nothing but single-line `uses:` substitutions plus the producer report; `secret-scan.yml` is untouched; YAML and job/step structure are byte-equivalent to base; triggers and permissions are unchanged; and branch CI plus secret-scan are verified green at `e5f6ea4` via live API. Findings 1–3 are informational and non-blocking. Recommend the orchestrator record G3 PASS and proceed to G4 integration.
