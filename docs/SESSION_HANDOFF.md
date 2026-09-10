# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume read it live -
`python tools/project_control.py status` - and reconcile; no SHA here is guaranteed current.
Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff - seq 95: M5-T012 + M5-T013 ACCEPTED (176); FIRST EVER PUSH + FIRST EVER CI RUN; loop DOWN.

1. **Generated:** 2026-09-10 ~08:00Z, session `01KCxUbUJdG1jvp8E6ura9g2`. Owner reason verbatim:
   *"i want you to also inculte the info about the graf not being build in to codex also sumrise our
   conver we had the last few very detelet and make a new md and tell me the file name so i can
   countinu the convo in new seasen"*. **Deep narrative companion:
   `docs/archive/session-handoffs/SESSION_HANDOFF-2026-09-10-deep-summary.md`** (budget-exempt; read it
   for the full reasoning, the owner corrections, and the research findings).
2. **Identity:** root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b`, HEAD **`a84b85e4`**, origin
   `https://github.com/martin10101/nyc-buildability.git`, upstream **now set** to
   `origin/candidate/D-024-mrl-option-b`. **Accepted: 176.** Dirty: ONLY untracked
   `.claude/agent-memory/qa-engineer/{MEMORY.md,feedback_probe_...md}` (pre-existing, leave) and
   `scratchpad/` (session scripts, gitignore-absent, do not commit).
3. **THE BRANCH IS PUSHED.** `git push -u origin candidate/D-024-mrl-option-b` ran with explicit owner
   authorization ("push"). 873 commits now on GitHub. **`main` UNTOUCHED at `d8b3899f`** (verified via
   `git ls-remote`). No PR opened. Pre-push gate: gitleaks `detect --log-opts=origin/main..HEAD` =
   **858 commits / 22.35 MB / 0 findings**, re-run immediately before pushing.
4. **THE REPO IS PUBLIC** (`gh repo view --json visibility` = PUBLIC). The profile already said so; a
   claim it was private earlier in-session was wrong. Never place a secret in any committed artifact.
   **Never ask the owner to paste a key into chat** - owner correctly objected; secrets go to Render's
   env store / OS secret store only, and the code reads them from the environment.
5. **FIRST CI RUN EVER - 13 of 18 jobs pass, 5 fail.** Run `34450369207` (+ secret-scan `34450369304`).
   - **CRITICAL: Next.js unauthenticated RCE** (GHSA-p293-qw3h-jr36) + RCE via image-optimization AVIF
     (GHSA-2xp9-vwfh-vxw4); `sharp` HIGH, `js-yaml` HIGH, `browserslist` MODERATE. **7 vulns (1 crit,
     3 high, 3 moderate).** Fix = `next@15.5.25`, which is OUTSIDE the stated range -> a real
     dependency change under `docs/DEPENDENCY_SECURITY_POLICY.md` (7-day age, exact pin, zero
     advisories, no waiver). **The web app must NOT be deployed until this is fixed.**
   - **`exact-production-install` (Render's exact install path): 2820 pass, 3 FAIL** - the evidence
     route counts **0** and the four analysis routes come back **empty** in the installed tree. So the
     two features just accepted may **not register when deployed**. Cause NOT yet determined
     (packaging looks fine: `[tool.setuptools.packages.find] include = ["app*"]`); could be genuine
     registration failure or environment-fragile tests. **Must resolve before Render deploy means
     anything.** pip-audit PRODUCTION + TOOLING = zero advisories; age gate both locks PASS; Render's
     exact install command + create_app smoke = success.
   - **`control-plane`: directive registry INVALID (6 errors)** - PROVEN cause: the directive integrity
     digest is computed over **on-disk CRLF** bytes (`f62c6fc8`), but `.gitattributes` forces
     `project-control/directives/** text eol=lf`, so CI's LF checkout computes `0e9de4cc`. **The
     tamper-detection mechanism only validates on this one Windows machine.** Earlier sessions
     (including this one) recorded the CRLF digest as a "trap to preserve" - it is a DEFECT. Fix =
     hash line-ending-normalised content (or the git blob), not raw disk bytes.
   - **`secret-scan`: 1 finding** - `project-control/reports/M5-T013-G5-rereview.md:185`
     `[postgres-uri-with-password]`. It is G5's own FAKE canary (`postgres://u:p@h/db`). Nothing to
     rotate. Repo precedent exists (an AWS example key in M0-T106-G5 is allowlisted among 17 entries):
     add a justified `.gitleaksignore` entry rather than editing reviewer evidence.
   - **`api`: ruff only** - the known **27** errors (23 E501 / 2 I001 / 2 B905), all in already-ACCEPTED
     M5 engine files inside this packet's forbidden_paths. Count verified UNMOVED across 4 rounds.
   - **BIG UNLOCK: `web` (lint+typecheck+build) and `web-e2e` (vitest+Playwright) BOTH PASS.** The
     "no frontend-green path" wall that parked M5-T004 and all UI acceptance **is gone** - CI can now
     run front-end tests. Also settled: 3.12 is fine (2820 passed), so the 3.11 collection gap was not
     hiding breakage.
6. **THE CODE GRAPH IS NOT WIRED INTO THE LOOP (owner asked for this explicitly).** `tools/code_graph/`
   (generate.py + query.py + tests) plus `repo_index_*.py`, `context_pack_index.py`, `memory_graph.py`
   EXIST (M0-T030, D-005 V1) and the `code-graph` CI job passes. But its own README states it is an
   **"advisory navigation index, never authoritative truth"** with source verification MANDATORY. The
   supervisor has exactly TWO references: a line running its test file (`cli.py:1272`), and
   `review_packet.py:294` listing `full_code_graph` in **`PROHIBITED_MARKER_KEYS`** - i.e. the only real
   relationship is **forbidding** dumping the graph into a review packet. **Neither Codex/the loop nor
   any producer/reviewer in this session used it**; they navigated by Read/Grep. **No measured token or
   time saving exists, and none may be claimed.** What actually controls tokens: the bounded
   review-packet ceiling (~64k tok + structural byte cap), the prohibited-dump list, per-run budgets.
   Measured per-run cost: 3.0-5.8M cumulative context tokens, peak live 148k-243k (runs 20-29).
   **Decision for the successor: either wire the index into the producer's navigation step and MEASURE,
   or stop counting it as an asset.** One small task either way.
7. **LOOP IS DOWN: `PAUSED_RECOVERY`**, run `persistent-local-29` (M5-T013), audit head 643 (chain OK,
   not forked), **1 queued stale ask**, no supervisor process alive. Third consecutive
   `checkpoint_field_mismatch` close (worker writes the 8-char `starting_sha`, controller demands 40) -
   benign; work was complete. Relaunch drill: deny stale ask -> `reconcile_dispatch_intent.py` ->
   `clear-recovery` -> `scratchpad/relaunch_m5t013.ps1` pattern from `wt-controller-src` cwd with a NEW
   run-id `persistent-local-30`; **fix `$Branch` by hand** (the sed template mangles it every time).
   Monitors are SESSION-BOUND - **re-arm the break watcher**.
8. **SUB-AGENTS: none active.** Producer (1) + G1/G3/G4/G5/DCV (5) all completed and were reconciled
   into the ledger; all gate reports and re-reviews are committed. None were killed.
9. **M5-T013 accept detail:** reviewed `209b9548`, material identity **`5506a594`** (DCV computed via
   the accept path's own `_task_git_identity`; matched FIRST try), accept commit `a84b85e4`. G1 FAILed
   `29ca7bca` on a **silent projection** - the evidence document dropped **18 required contract fields**
   (root 14/20, trace 7/19), including `exceptions_applied` ("a higher FAR up to 2.00 per ZR 23-21
   applies... the result is conditional"), `notes` ("NOT an evidence-based determination"),
   `computation_steps`, and `rule_release.verified_eligible:false`. The page built to prove nothing is
   overstated was itself overstating. Fixed by wholesale deep-copy + key-set equality against the app's
   OWN bundled `rule_evaluation.schema.json`. DCV leaf classification: 1,413 leaves -> 1,404
   transported byte-equal, 9 authored, none a legal value.
10. **Owner decisions this session (standing):** gate waves AUTHORIZED (dispatch 5 reviewers, gate+accept
    silently, surface one line per feature + genuine breaks); rework via DIRECT producer agent, not a
    loop relaunch; push branches but NEVER main; **Render free tier for MVP** (owner will grant a Render
    MCP exception - set it up but the OWNER pastes every secret); **Render Postgres instead of Supabase
    for now** (see deep summary for the 30-day-deletion caveat); legal "draft" wording need not be
    surfaced to testers (keep it in the DATA, de-emphasise in UI only); B-010 replaced by an owner-
    proposed **reverse-engineering validation** plan (see deep summary - the comparison is a ONE-SIDED
    bound, not equality).
11. **Standing restrictions (unchanged):** NEVER merge PR #241; R595/autostart/continuous-mode
    owner-only (supervisor SHADOW); supervisor changes need a cited `D-024-R###`; expansion-planning
    hold; Bootstrap Gate 0 (cwd = this worktree root, `/mcp` empty/allowlisted) before any write;
    launch the supervisor ONLY from `wt-controller-src`; no bare `git stash`; no new packages as a side
    effect; Tier D (credentials/payment/production/legal) always stops for the owner. **main stays
    untouched.** Campaign record `D-024-fable-codex-loop` NEXT pointer is STALE (points at M0-T136 MRL
    Tranche B, 2026-09-01) and 5 `D-032-*.json` campaign files are INVALID (missing required fields) -
    the **ledger + git win**; do not act on that pointer.

## Validation (this session, exact)
- `pytest services/api/tests/api` -> **371 passed**; `pytest services/api/tests/scenario` -> **388
  passed**; `tools/modularity_check.py --check` -> failures 0 EXIT 0 (no warn names
  `app/api/v1/evidence.py`); `validate_directive_compliance.py --check` -> **EXIT 0 locally** (but CI
  says INVALID - item 5); `context_budget_check.py` -> PASS; ruff on the 3 owned files -> clean.
- `apps/web/scripts/dependency_age_gate.mjs` -> **PASS, every committed package >= 7 days** (newest
  `ws@8.21.1`, ~58d). Lockfile carries NO known-compromised package (axios/node-ipc/@mastra/
  easy-day-js/plain-crypto-js = 0 entries); the 7 packages from the chalk/debug incident are all on
  CLEAN versions (`debug` is 4.4.3 = the post-fix release). **No node_modules installed anywhere.**
  `npm config get ignore-scripts` = **true** (user-level, so CI does NOT inherit it - gap).

## Authoritative files (smallest set)
`CLAUDE.md`; `docs/SESSION_HANDOFF.md`; `docs/archive/session-handoffs/SESSION_HANDOFF-2026-09-10-deep-summary.md`;
`project-control/state.json` + `tasks/M5-T013.json`;
`project-control/directives/D-038-build-product-not-self/{requirements,manifest,verification}.json`;
`docs/DEPENDENCY_SECURITY_POLICY.md`; `render.yaml`; memory `d038-product-pivot` +
`loop-relaunch-mechanics`.

## EXACT NEXT ACTION (ordered; do NOT broaden)
1. `.gitleaksignore` entry for `M5-T013-G5-rereview.md:185` (fake canary; follow the M0-T106 precedent).
2. Diagnose the `exact-production-install` 3-test route failure - it silently breaks deployment.
3. Fix the CRLF/LF directive-digest defect (item 5) so integrity validates on any machine.
4. Ruff cleanup: 27 errors. **G5 already ruled the hard part**: `breakeven.py:535` is `zip(xs, xs[1:])`
   whose operands differ by one BY CONSTRUCTION, so `strict=True` would crash every non-empty domain -
   use `itertools.pairwise`, never ruff's `--fix`. Re-check line length after.
5. Next.js RCE upgrade - OWNER-STEER first (dependency policy change, critical advisory).
6. Then resume the D-038 product cycle: contract the next feature, relaunch (item 7), re-arm the watcher.

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Bootstrap Gate 0: primary cwd must BE
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` and `/mcp` must be empty or allowlisted BEFORE any write.
Verify root/worktree/branch/HEAD/origin/upstream first. Read `CLAUDE.md`, `docs/SESSION_HANDOFF.md`,
**`docs/archive/session-handoffs/SESSION_HANDOFF-2026-09-10-deep-summary.md`** (full narrative), and
memory `d038-product-pivot` + `loop-relaunch-mechanics`; then `python tools/project_control.py status`
and reconcile - **the ledger and git win over all prose, including the stale D-024 campaign NEXT
pointer and the INVALID D-032 campaign files.** **176 accepted; M5-T012 (toolkit API, 175th) and
M5-T013 (evidence/provenance endpoint, 176th) accepted this session, each after a FAIL -> rework ->
five-reviewer re-attestation arc.** The branch is PUSHED (873 commits, `main` untouched at `d8b3899f`)
and the repo is **PUBLIC**. CI ran for the first time: 13/18 green; the 5 failures and their proven
causes are in item 5 - work them in the EXACT NEXT ACTION order. The loop is DOWN in PAUSED_RECOVERY
with 1 stale ask. OPERATING MODEL = invisible operator (loop builds; you gate+accept silently with 5
independent reviewers; surface one line per feature + genuine breaks). Do NOT: push or merge `main`,
merge PR #241, activate continuous/autostart, ask the owner for a secret in chat, place any secret in a
committed file, deploy the web app before the Next.js RCE is fixed, install any package outside
`docs/DEPENDENCY_SECURITY_POLICY.md`, answer worker asks against a live run, launch the supervisor from
ctl24 cwd, or claim the code graph saves tokens (item 6). Report READY TO RESUME or BLOCKED.
