# Session Handoff — resume state as of 2026-07-20 (session 16: M0-T020 ACCEPTED 39th; M0-T019 task PR #64 OPEN — policy-enforcement CORRECTION mid-implementation)

> **P0 DEPENDENCY-SECURITY WAVE — M0-T020 ACCEPTED (39th, live on main); M0-T019 UNDER OWNER-DIRECTED POLICY-ENFORCEMENT CORRECTION, mid-implementation.** M0-T020 accepted via PR #62 (`9391bb0`). M0-T019 (frontend Next/React security upgrade + permanent npm dependency-admission policy) was implemented + reviewed once (G3/G4 + G5 PASS at task head `3bbb594`), but an owner review found a **BLOCKING gap: `.npmrc min-release-age` is resolver-time only; CI's `npm ci` installs the committed `package-lock.json` WITHOUT resolving, so a hand-edited lock could smuggle a <7-day package past `npm ci` + `npm audit`.** The owner authorized a 3-part correction (packet amendment → implement a committed-lockfile age gate → fresh G3/G4/G5). **>>> RESUME POINT: the correction is MID-IMPLEMENTATION. Phase A + producer implementation are DONE and committed to the task worktree branch (LOCAL head `9961d39`, NOT pushed); the remaining work is: regenerate the lock (verify zero resolution change) → push task PR #64 → CI green → FRESH G3/G4/G5 → preserve new reports → return. The task PR stays OPEN + unmerged.** Checkpoint remains `CP-0031`. Do NOT merge task PR #64, accept M0-T019, record its acceptance gates, create a checkpoint, run Phase 2c, dispatch M2-T013/M2-T014 or any held task, modify M0-T020, or release any hold. The ledger (`project-control/`) is the source of truth.

Written by the orchestrator. Open this folder (`nyc-development-feasibility-claude-pack`) as the workspace root, then follow CLAUDE.md's start-of-session routine.

## >>> EXACT RESUME STEPS for the next chat (M0-T019 correction — finish it)

**Verified starting state:** main = remote main = `4c649601f902eeb0ffdfac48748df07ee3f886df` (after amendment PR #66). Ledger 39 accepted / 2 blocked / 7 backlog / 1 claimed (M0-T019 `claimed`). Checkpoint CP-0031. 1 open PR: **#64** (M0-T019 task PR, remote head still `3bbb594` = the rev-1 reviewed head). The corrected work is committed LOCALLY on the task worktree branch but NOT pushed.

- **Worktree:** `.claude/worktrees/M0-T019-frontend` on branch `task/M0-T019-frontend-security`, LOCAL head **`9961d39`** (= merge of amended main `af26db6` + the rev-2 producer commit). This is AHEAD of the remote task branch (`3bbb594`) and contains all the correction work. `git -C .claude/worktrees/M0-T019-frontend log --oneline -3` to confirm.

**Owner correction = 3 parts (A done, B mostly done, C + finish remain):**

**A. Packet amendment — DONE.** PR #66 merged → main `4c64960`. `project-control/tasks/M0-T019.json` now has: allowed_paths += `apps/web/scripts/dependency_age_gate.mjs` + `apps/web/scripts/tests/**`; acceptance += **FE-S9** (deterministic fail-closed committed-lockfile release-age gate; validates EVERY registry pkg/version — direct/transitive/dev/build/optional/scoped/platform — ≥ exactly 604800 s vs the registry Date-header UTC clock; boundary 604800 pass / 604799 fail; fail-closed on outage/missing/malformed/integrity-mismatch/unexpected-host; runs in PR+push CI + scheduled npm-audit), **FE-S10** (exact direct+dev pins, ZERO resolution change), **FE-S11** (continuous npm@11.18.0 CLI tooling advisory verification; policy doc distinguishes 4 enforcement layers).

**B. Implement + amend task PR #64 — producer edits DONE + committed to the worktree branch (`9961d39`); LOCK REGEN + PUSH + CI remain.** The task branch was merged up to amended main (`af26db6`), then the frontend-engineer implemented (committed at `9961d39`):
  - `apps/web/scripts/dependency_age_gate.mjs` (NEW, Node ESM, node-builtins-only, no npm deps): mirrors the accepted Python `services/api/scripts/dependency_age_gate.py`. Pure `parseLock`/`decide`/`evaluateLock`/`checkNpmTooling` (injectable `now` + providers) + a single networked `RegistryClient`. Enumerates every `packages` entry with a `resolved` (dedup name@version); requires `resolved` host == registry.npmjs.org + committed `integrity` == registry `dist.integrity` (anti-forgery); publish time from packument `time[version]`; `ageSeconds = Math.floor((nowMs-publishedMs)/1000)`; PASS iff `>= 604800`; fail-closed (throw→FAIL) on every missing/malformed/outage/mismatch. `checkNpmTooling` = OSV advisory + age for npm@11.18.0. No allowlist/suppression.
  - `apps/web/scripts/tests/dependency_age_gate.test.mjs` (NEW, `node --test`, node-builtins-only): boundary 604800 PASS / 604799 FAIL, integer-second floor, positive, full-lock, every fail-closed branch, enumeration/dedupe, FE-S11 tooling. **Local run PASSING** (the explicit-file invocation `node --test apps/web/scripts/tests/dependency_age_gate.test.mjs` passed tests 1-5 boundary/positive before the session was paused).
  - `apps/web/package.json` (FE-S10): every direct dep + devDep EXACT-pinned to its already-resolved version (^/~ removed). Map (all verified ≥7 days, so no <7-day version smuggled): `@eslint/eslintrc` 3.3.6, `@playwright/test` 1.61.1, `@testing-library/dom` 10.4.1, `@testing-library/jest-dom` 6.9.1, `@testing-library/react` 16.3.2, `@types/node` 22.20.1, `@types/react` 19.2.17, `@types/react-dom` 19.2.3, `@vitejs/plugin-react` 4.7.0, `eslint` 9.39.5, `jsdom` 26.1.0, `typescript` 5.9.3, `vitest` 3.2.7 (next 15.5.20 / react 19.1.2 / react-dom 19.1.2 / eslint-config-next 15.5.20 already exact; `overrides.postcss` 8.5.10 kept).
  - `.github/workflows/ci.yml`: NEW BLOCKING job `web-lockfile-age-gate` = checkout + setup-node 22 + pin npm 11.18.0 + `node --test apps/web/scripts/tests/` + `node apps/web/scripts/dependency_age_gate.mjs apps/web/package-lock.json --npm-tooling-version "$(npm -v)"`.
  - `.github/workflows/scheduled-npm-audit.yml`: appended the `node --test` + live gate after the blocking audit.
  - `docs/DEPENDENCY_SECURITY_POLICY.md`: distinguishes the 4 npm layers (a .npmrc resolver-time filtering; b committed-lockfile age gate = authoritative; c npm audit; d npm CLI tooling advisory).
  - `project-control/reports/M0-T019-producer-report.md`: rev-2 section appended (rev-1 preserved).
  - (The producer also wrote `.claude/agent-memory/frontend-engineer/**` — NOT part of the task; do NOT commit it to the PR.)

  **⚠️ WATCH ITEM:** locally, `node --test apps/web/scripts/tests/` (directory arg with trailing slash) errored `MODULE_NOT_FOUND` on Node 22.18.0, but the EXPLICIT file `node --test apps/web/scripts/tests/dependency_age_gate.test.mjs` PASSES. The CI job uses the directory form — **if the CI `web-lockfile-age-gate` job fails on test discovery, switch the CI step (ci.yml + scheduled-npm-audit.yml) to `node --test apps/web/scripts/tests/*.test.mjs` or the explicit file path.** (Verify in CI.)

  **B — REMAINING (do these next):**
  1. **Regenerate the lock:** package.json was exact-pinned, so the committed lock's root `packages[""].devDependencies` declared ranges must be regenerated. Push package.json+scripts+workflows to the task branch, then dispatch `generate-lockfile.yml` on `task/M0-T019-frontend-security` (npm 11.18.0). Pull the bot's lock commit. **VERIFY ZERO RESOLVED-VERSION CHANGE** (diff resolved `node_modules/*` versions + integrity old-vs-new; the producer pre-verified all 17 exact targets == current resolved, so expect only the root declared-range strings to change). **If ANY resolved version or integrity changes, STOP and report (FE-S10 STOP condition).**
  2. **Push + CI:** push the task branch (fast-forward from `3bbb594` via the `af26db6` merge → PR #64 head advances). Run ALL CI to completion (foreground polls): the new `web-lockfile-age-gate` (node --test + live gate over ~530 pkgs hitting registry+OSV — may be slow but should pass), web / web-e2e / `npm audit (web tree)`, and every Python job green.

**C. Fresh independent review — NOT STARTED.** Because PR #64 gets new commits, the rev-1 G3/G4/G5 verdicts (at `3bbb594`) do NOT authorize the corrected head. Re-dispatch **code-reviewer (G3/G4)** + **security-reviewer (G5)** against the NEW exact task-PR head. Require them to specifically test: a manually injected too-new lock entry fails CI; 604800 passes / 604799 fails; registry/error conditions fail closed; all direct package.json declarations are exact; npm@11.18.0 tooling is in the recurring advisory enforcement; no M0-T020 control weakened. Preserve the NEW verbatim reports under DISTINCT filenames (e.g. `project-control/reports/M0-T019-G3-G4-code-review-rev2.md`, `M0-T019-G5-security-review-rev2.md`) via a control PR; retain the rev-1 reports (`M0-T019-G3-G4-code-review.md`, `M0-T019-G5-security-review.md`, already on main) as historical.

**Then:** update this handoff; deliver the owner's return packet (packet-amendment PR + merge SHA `4c64960`; new PR #64 head SHA; changed files + diffstat; exact-pin inventory; proof resolved versions did not change; age-gate test results incl. the two boundary cases + fail-closed cases; npm tooling advisory result; complete CI; fresh G3/G4/G5 reports bound to the new head; current ledger/checkpoint; confirmation PR #64 open/unmerged; confirmation no held task dispatched/released). **STOP** — do not merge PR #64, do not accept, no checkpoint, no held-task dispatch, no M0-T020 change, no hold release.

## Owner correction directive (verbatim intent)

Root finding: `.npmrc min-release-age=7` applies at RESOLUTION; `npm ci` installs the committed lock without resolving, so a manually altered lock could contain a <7-day package and pass `npm ci` + `npm audit` (if no advisory yet). The "release age enforced only at regeneration" reviewer note is therefore BLOCKING. Also correct two related inconsistencies: (1) direct devDeps still had `^` ranges (save-exact governs only future saves) → exact-pin all; (2) npm@11.18.0 tooling had only point-in-time evidence → add recurring machine advisory check. New allowed paths: `apps/web/scripts/**`. PR #64 stays open; new commits + fresh review; NOT accepted; no checkpoint; no hold released; M0-T020 unchanged.

## Exact repository state

- **main = remote main = `4c649601f902eeb0ffdfac48748df07ee3f886df`** (chain this session: `9391bb0` PR #62 M0-T020 acceptance → `301f5a2` PR #63 M0-T019 dispatch → `97d3c79` PR #65 rev-1 reviewer-report preservation → `4c64960` PR #66 policy-enforcement packet amendment). **1 open PR: #64** (M0-T019 task, remote head `3bbb594`).
- **Ledger: 39 accepted / 2 blocked / 7 backlog / 1 claimed (M0-T019).** **Checkpoint CP-0031** (next checkpoint deferred per the M0-T020 packet rule: only after M0-T020 + M0-T019 accepted + Phase 2c + both Python & npm audits green on reconciled main).
- **M0-T020 — ACCEPTED (39th), live on main, IMMUTABLE.** Python dependency-policy enforcement (hash-pinned tooling lock + `dependency_age_gate.py` + CI hardening). Do not reopen.
- **M0-T019 — CLAIMED (frontend-engineer); rev-1 implemented + reviewed PASS/PASS at `3bbb594` (on the remote PR #64), NOW under policy-enforcement correction (rev-2 committed locally at `9961d39`, not pushed).** See resume steps above. rev-1 verbatim reviewer reports on main: `project-control/reports/M0-T019-G3-G4-code-review.md` + `M0-T019-G5-security-review.md` (SUPERSEDED by the correction — do NOT use them to authorize the corrected head).
- **M0-T018 (38th, ACCEPTED, IMMUTABLE).**
- **Repo PUBLIC**; ruleset `protect-main` active; secret scanning + push protection ON. B-005..B-009 resolved.
- **Worktrees:** `.claude/worktrees/M0-T019-frontend` (M0-T019 producer, branch `task/M0-T019-frontend-security` @ local `9961d39` — HOLDS THE UNPUSHED CORRECTION WORK; do not delete). `agent-a501f3e0a11bdd091` (stopped rev-0 research; superseded) preserved. Older harness-managed stale `agent-*` worktrees (two locked — leave).
- **Working tree (main checkout):** clean except `.claude/agent-memory/**` (permitted) + this handoff branch.

## HARD RULES (unchanged)

(1) **Protected-main PR workflow** — NEVER push to main; task/control branch → push → `gh pr create` → wait checks green (FOREGROUND polls) → `gh pr merge --merge --delete-branch --match-head-commit <FULL-40-char-SHA>` (a SHORT sha errors "Could not coerce value to GitObjectID") → `git fetch` + `git merge --ff-only origin/main` → verify. (2) **HARDENED project_control.py** — G0 backlog→ready; claim needs `ready`; submit→awaiting_gate; G2 `--reviewer orchestrator`; independent gates (G3/G4/G5) need a rostered reviewer ≠ producer; accepted tasks IMMUTABLE; report paths must EXIST when the CLI runs (record acceptance gates AFTER the task PR merges, in a later acceptance control PR). (3) **ADR-005** — only the orchestrator runs project_control.py/git/gh; producers edit files + return a report (no git/npm — thin client); reviewer returns preserved VERBATIM (byte-scan python bytes <9 or 14–31). (4) **THIN-CLIENT** — no local node_modules/npm; the web lockfile regenerates on a GitHub runner via `generate-lockfile.yml` (workflow_dispatch). SHELL: Bash + PowerShell SHARE a persisted cwd — after any `cd` run `cd "$(git rev-parse --show-toplevel)"` before relative CLI reads; `node --test <dir>/` may need the explicit-file/glob form. IDE: background-task completion does NOT re-invoke the session — run CI waits in the FOREGROUND (bounded polls; `gh pr checks <n> --watch` may background — poll `gh pr checks <n>` directly). Permission posture: auto mode, ask only for deletions.

## Blockers

**B-001** (HIGHEST — Supabase token; blocks M0-T007/T008 + persistence/citywide-import), **B-002** (Render), **B-004** (Geoclient). B-003 closed; B-005..B-009 resolved.

## Owner decisions pending

1. **Finish the M0-T019 correction** (regen lock + push + CI + fresh G3/G4/G5), then owner reviews + authorizes acceptance — the immediate resume gate.
2. Release the DISPATCH HOLDS on the survey workstream (M2-T014/T015/T016), M2-T013, M4-T001.
3. Credentials when ready: B-001 (highest), B-002, B-004.
4. GDS/expansion planning review (counter-notice §2 hold).
5. CORS/proxy decision (M2-T001 D8). 6. M2-T016 professional-confirmation role definition.

## Holds this run (do NOT dispatch / do NOT release)

M2-T012, M2-T013, M2-T014, M2-T015, M2-T016, M4-T001, M6-T001; survey Packets B/C. All GDS/expansion (counter-notice §2) + 3D holds preserved. M0-T019 task PR #64: open + under correction, NOT merged.

## Session 16 log (condensed)

M0-T020 accepted (PR #62 → `9391bb0`). M0-T019 dispatched (PR #63 → `301f5a2`) → implemented + reviewed rev-1 (task PR #64 head `3bbb594`, G3/G4 + G5 PASS) → rev-1 reports preserved (PR #65 → `97d3c79`). Owner found the `npm ci` age-enforcement gap → packet amended (PR #66 → `4c64960`, FE-S9/S10/S11) → frontend-engineer implemented the fail-closed committed-lockfile age gate + tests + exact pins + CI wiring + policy/report updates → committed to the task worktree branch (`9961d39`, unpushed). Local age-gate tests passing. Session paused before lock-regen/push/CI/fresh-review.

## Prior sessions (condensed)

- **S15:** M0-T020 implemented + reviewed; bounded pytest 9.0.3 amendment (PR #59).
- **S14:** accepted M0-T018 (38th). **S13:** M2-T011 (36th) + M2-T010 (37th) at CP-0031. **S12:** M2-T007/T008/T009 (33rd–35th; repo made PUBLIC).

## Environment/process lessons (this session)

- **`.npmrc min-release-age` does NOT gate `npm ci` of a committed lock** — it is resolver-time only. A committed-lockfile age gate (the npm parallel of M0-T020's `dependency_age_gate.py`) is required to make the policy machine-enforced against every future lockfile change. (This is the M0-T019 correction.)
- **`gh pr merge --match-head-commit` requires the FULL 40-char SHA** — a short SHA errors "Could not coerce value ... to GitObjectID". Use `gh pr view <n> --json headRefOid --jq .headRefOid`.
- **A fresh owner instruction does not override an already-approved packet rule** (the interim CP-0032 conflicted with the M0-T020 checkpoint rule; owner corrected to keep CP-0031). Surface conflicts.
- **Node `node --test <dir>/`** (trailing-slash directory) can throw MODULE_NOT_FOUND on Node 22.18.0 while the explicit-file form works — use `*.test.mjs`/explicit path in CI if the directory form fails.
- **Deferred-ledger + review-only boundary:** keep the task-PR head == the reviewed SHA; preserve reviewer reports on main via a separate control PR (rev-1 → PR #65); record acceptance gates + accept together only in a later owner-authorized acceptance control PR. Producer works in an isolated worktree; the orchestrator commits/pushes/regenerates-lock/opens-PR; reviewers dispatched WITHOUT isolation, pointed at the task-branch worktree + `gh pr diff`.
