# G5 Security Review — M0-T112 (D-024 Amendment 8, unit M: final golden re-certification)

**Verdict: PASS**

**Frozen review identity:** `14d204363c3ad44dff9a96333a9fe0e5662541ca` — confirmed equal to `git rev-parse HEAD`.
**Base for diff:** `a2aec114` (prior accepted tip).
**Branch:** `control/D-024-fable-codex-loop`. **Repository visibility:** PUBLIC (raises the bar for leakage findings; applied throughout).
**Reviewer:** security-reviewer (read-only; no writes, no git mutations).
**Nature of unit:** governance/certification claiming ZERO code changes — control-plane records only.

## Scope and method

Bounded G5 review per the six-item charter: diff-surface secret/path scan, R248 prohibition verification, Telegram-discipline check, activation-package honesty, gitleaks scan of the unit's commits, and CI evidence integrity. I read the complete diff (small; ~24 KB) line by line and corroborated the load-bearing claims against GitHub via `gh`.

## Result summary

| Charter item | Result |
|---|---|
| 1. Diff surface (only project-control/**; no secrets/new-path-leakage/activation instruction) | PASS |
| 2. R248 prohibitions (hooks/settings/MCP/deps/PR#241/supervisor untouched) | PASS |
| 3. Telegram discipline unchanged (no live-send/canary/credential; owner-gating not weakened) | PASS |
| 4. Activation-package honesty (DEFAULT-OFF; presentable only post-acceptance) | PASS |
| 5. Gitleaks posture | PASS (0 leaks, exit 0) |
| 6. Evidence integrity (CI 20/20, none skipped/neutral) | PASS |

No BLOCKER, MAJOR, or MINOR findings. Two INFO notes below.

## Findings

### INFO-1 — Workstation absolute path present in added control-plane text (pre-existing class, not new)
`project-control/reports/M0-T112-G0-readiness.md` item 1 and `project-control/tasks/M0-T112.json` (`"worktree"` field) contain the absolute path `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`. In a PUBLIC repo this discloses the owner's OS username and directory layout, but this is an **already-conventional class** of content in this repo's control plane (worktree fields and readiness reports routinely carry it), not a new class of leakage introduced by this unit. Per the review charter ("flag only NEW classes of leakage") this is INFO, not a defect. No credential, token, host, or network-reachable identifier is exposed. No action required for this unit; if the owner ever wants to harden the public control plane, normalizing worktree paths to a repo-relative placeholder would be a separate, repo-wide task.

### INFO-2 — Gate `reviewed_sha` values predate the frozen HEAD (expected control-plane sequencing; not a security issue)
`M0-T112-G0.json` pins `reviewed_sha: a4f94b77…` (the certification run head) and `M0-T112-G2.json` pins `reviewed_sha: c2518d4c…`; the frozen HEAD is `14d20436`. This is normal seam-by-seam recording: each control-plane gate was committed at its own seam and the final commit records the G2 submit. Critically for security posture, the **supervisor material identity is invariant across every commit in this range** — no `tools/agent_supervisor/**` or other code path changed (verified below), so nothing security-relevant moved between these SHAs. This is flagged only as context for the G3/DCV identity-discipline reviewers; it carries no G5 impact.

## Evidence — commands run and outputs

**1. Identity + diff surface**
```
git rev-parse HEAD
  → 14d204363c3ad44dff9a96333a9fe0e5662541ca   (matches frozen identity)

git diff a2aec114..14d20436 --stat
  → 9 files changed, 363 insertions(+), 87 deletions(-); ALL under project-control/

git diff a2aec114..14d20436 --name-only
  → project-control/gates/M0-T112-G0.json
    project-control/gates/M0-T112-G2.json
    project-control/reports/M0-T096-activation-package.md
    project-control/reports/M0-T112-G0-readiness.md
    project-control/reports/M0-T112-G2-self-check.md
    project-control/reports/M0-T112-evidence-map.json
    project-control/reports/M0-T112-recertification.md
    project-control/state.json
    project-control/tasks/M0-T112.json
```
I read the entire diff. Added lines are: two gate JSONs (git SHAs, SHA-256 content manifests, ISO timestamps — no secrets); the recertification report and G0/G2 reports and evidence map (test counts, SHAs, prose); a `state.json` one-line addition of `M0-T112` to `completed`; and `tasks/M0-T112.json` (a whitespace re-indent from 1→2 spaces plus status/producer/progress_log updates). Nothing outside project-control/**.

**2. R248 prohibited-path check (all 4 commits, union and per-commit)**
```
git log a2aec114..14d20436 --name-only -- \
  ".claude/" "tools/agent_supervisor/" "package.json" "package-lock.json" \
  "requirements.txt" "pyproject.toml" "uv.lock" ".mcp.json" "mcp.json"
  → (no output — zero touches of any prohibited path across all 4 commits)
```
Confirmed: no `.claude/hooks/**`, no `.claude/settings*`, no MCP config, no dependency manifest/lockfile, and no `tools/agent_supervisor/**` change — even transiently within any single commit. Supervisor stays SHADOW-ONLY; no activation flag is flipped anywhere in the diff (grep for activation keywords returns only owner-gating language, see item 4).

**3. PR #241 untouched and still OPEN**
```
gh pr view 241 --json state,headRefName,baseRefName,title
  → state=OPEN, headRefName=task/M5-T002-scenario-endpoint, baseRefName=main
```
PR #241 lives on a separate branch (`task/M5-T002-scenario-endpoint`); none of this unit's 4 commits (`a4f94b7`, `615f661`, `c2518d4`, `14d2043`) touch it. It remains OPEN and unmodified, consistent with the standing owner hold ("DO NOT MERGE until owner authorizes").

**4. Telegram discipline + activation-package honesty**
```
git diff a2aec114..14d20436 | grep '^\+' | grep -Ei 'bot_token|chat[_-]?id|api[_-]?key|secret|password|BEGIN (RSA|OPENSSH|PRIVATE)'
  → (no matches, exit 1)

git diff a2aec114..14d20436 | grep '^\+' | grep -E '[0-9]{6,12}:[A-Za-z0-9_-]{30,}'
  → (no matches, exit 1)   # Telegram bot-token shape absent
```
No credential material, no chat id, no live-send invocation, and no canary execution evidence were added. The activation-package edit is prose-only. Comparing items 10–12 and the Amendment-8 banner before/after:
- Banner now reads that both capabilities are ACCEPTED and re-certification has run, then: *"This package becomes presentable for the R187/R595 activation decision ONLY once M0-T112 itself is ACCEPTED through its gates; presentation and activation remain owner-gated."* This **strengthens**, not weakens, the gating — it adds an explicit acceptance precondition.
- Item 12 refresh reiterates lane-1 INJECTED only; the natural-event lane stays `pending_live_observation` and gates the live 4.8 bridge (R228).
- Recertification §4 states the package "still activates nothing (DEFAULT-OFF; R187/R595 owner-gated)"; §6 records no continuous-mode activation, no live bridge, no PR #241 touch.

No sentence asserts the package is now *presented* or that activation is *authorized*. Honesty preserved.

**5. Gitleaks (read-only scan of this unit's commits)**
```
C:/Users/MLFLL/.gitleaks/gitleaks.exe detect --source . --no-banner --redact \
  --log-opts "a2aec114..14d20436"
  → 4 commits scanned; ~24.18 KB; "no leaks found"; GITLEAKS_EXIT=0
```

**6. CI evidence integrity — certification tip 615f661**
```
gh api repos/martin10101/nyc-buildability/commits/615f661a1ad30883469c72932970dd1ae64dc317/check-runs
  → 20 check-runs, every one status=completed, conclusion=success. None neutral/skipped/cancelled.
```
The 20 contexts include `supervisor-bridge (pytest tools/test_agent_supervisor_*.py)` = success (the whole-supervisor-suite confirmation the recertification relies on) and `Scan repository for credentials` = success (independent secret-scan corroborating gitleaks). The unit's `progress_log` claim of "CI 20/20 green on pushed certification tip 615f661" is accurate; no check was skipped or neutral-washed.

## Cross-tenant / least-privilege / injection considerations

This unit ships no code, no schema, no RLS, no storage config, no external I/O, no upload path, and no LLM-facing surface — so cross-tenant isolation, service-role secrecy, private-storage, SSRF/injection defenses, upload controls, and prompt-injection defenses are **not in scope for this diff** and are unchanged by it. Least privilege holds: the producer wrote only within allowed_paths plus orchestrator-owned control-plane records; no privilege, hook, setting, or dependency surface was expanded. Log/redaction posture is unaffected (no logging code touched; gitleaks + the CI credential-scan both clean).

## Conclusion

M0-T112 is a control-plane-only re-certification record. The diff is confined to `project-control/**`; it introduces no secrets, no new class of path leakage, no dependency/hook/settings/MCP change, and no supervisor code change; PR #241 stays OPEN and untouched; the activation package remains DEFAULT-OFF and explicitly conditions presentability on this unit's own acceptance; gitleaks is clean; and the cited CI evidence (20/20, including the supervisor-bridge and credential-scan contexts) verifies with no skipped or neutral checks. Nothing in this unit activates continuous mode, enables the live 4.8 bridge, or crosses the owner gate.

**G5 verdict: PASS** at frozen identity `14d204363c3ad44dff9a96333a9fe0e5662541ca`. Two INFO notes recorded; no BLOCKER/MAJOR/MINOR defects.
