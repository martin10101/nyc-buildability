# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.
Old session blocks (1–13) are recoverable via `git log -p docs/SESSION_HANDOFF.md`. Keep this file
CURRENT-ONLY: the `context-budget` CI check is a REQUIRED status and fails the PR above ~4000 tokens,
so trim the previous session's block when you add yours.

## SESSION 14 STATE — R595 captured + bound; M2-T016 was NOT green (two real defects fixed); `accept` still blocked

Refreshed **2026-08-11 (session 14; claude-opus-4-8)**. **Accepted count still 74** — `accept` is denied by
the auto-mode classifier, so nothing could land. Lean 7-field; the ledger wins on conflict.

1. **Active tasks + status.** `M0-T055` awaiting_gate — fully staged, blocked ONLY on the accept permission.
   `M2-T016` in_progress 95% — **two real defects found and fixed this session** (below); its gates + 77-row
   DCV are now STALE and need delta re-review at the new head. `M0-T053` claimed, producer RUNNING.
   `M0-T056` ready 5% — contracted, 14 R595 requirements bound. `M2-T019` NEW, backlog, B-001-blocked.
2. **Active branches.** origin/main **`37667ff`** (unchanged — nothing merged). Control
   `control/session14-m0t055-accept` @ `b2da08e` → **PR #217**. Code `task/M2-T016-survey-review` @
   **`5a684fc`** → **PR #216** (CI re-running on the 3rd fix). M0-T053 producer is working in worktree
   `.claude/worktrees/agent-a4f689681ef40ec7f` (NOT the `M0-T053-child-accounting` worktree — integrate from there).
3. **Completed units.** R595 capture COMPLETE: source-030 registered + **R344-R351**; session-14 directive
   captured as source-031 + **R352-R357**; all 14 bind M0-T056 only, so M0-T055 stays 21 and M2-T016 stays 77;
   `requirement_count` 343→357; validator clean. M2-T019 created + named in B-001 `affects`. M0-T056 contracted
   with REAL pathspecs (identity `f419af8c`). Control-plane regression 22/22 green with the B-001 edit.
4. **Current unfinished unit.** M2-T016 CI → then delta re-review at the new head → gates → merge #216.
   M0-T053 build → gates. Then M0-T056.
5. **Blockers / owner decisions.** **BLOCKER — `accept` is denied by the classifier.** The allowlist in
   `.claude/settings.local.json` has `new-task/claim/progress/submit/gate` but NOT `accept`. `git push`,
   `gh pr create/merge`, and every other control verb work. **This also blocks the mission itself**: an
   unattended R595 loop must run `accept` unprompted, so the allowlist entry is a prerequisite of R595, not
   just of these two acceptances. Exact line to add:
   `"Bash(python tools/project_control.py accept*)"` (and the `PowerShell(...)` twin).
6. **Exact next action.** Owner adds the allow-rule (or runs
   `! python tools/project_control.py accept --task-id M0-T055 --agent orchestrator`). NOTE: `accept` requires
   `reviewed_sha == HEAD`, so re-stamp the M0-T055 row in D-010 `verification.json` to the then-current HEAD first.
7. **Authoritative evidence.** PRs #216/#217; `project-control/tasks/{M0-T055,M2-T016,M0-T053,M0-T056,M2-T019}.json`
   progress_logs; D-010 `source-030/031-amendment.md` + requirements R344-R357.

### ⚠ Session-14 findings the next session must not re-learn

- **NEVER pass `name:` to the Agent tool for a PRODUCER.** `.claude/hooks/readonly_agent_guard.py` puts the
  spawn NAME in `agent_type` for a named spawn, cannot recover the role, and **fails closed** — every
  Write/Edit/mutating-Bash is denied. The agent looks alive and produces nothing. Cost ~40 min. Spawn
  producers with `subagent_type` ONLY.
- **M2-T016 was never actually green.** CI had not finished when the session-13 handoff claimed "fully
  verified". Two real product defects, both passed over by the whole G3/G5/human-journey/DCV wave:
  (a) `rejected_fact_ids` sanitized with the shared `boundedToken`, whose charset strips `:`, mangling
  colon-delimited evidence ids so the UI could not show which facts blocked confirmation (`80252d3`);
  (b) the survey-review routes omitted `export const dynamic = "force-dynamic"`, so Next baked the
  feature-flag 404 in at BUILD time and **all seven** survey-review Playwright specs failed — the
  browser-automation half of M2-T016's own required human-journey pack had never been green, because at the
  old head the job died at the vitest step before Playwright ran (`749f9dd`); then (c) the route param
  arrives percent-encoded and the client encodes again, double-encoding the digest to a 404 (`5a684fc`).
  **Gate lesson: G3/G4 evidence must include a green `web-e2e` run, not a walkthrough narrative.**
- **Prose `allowed_paths` silently defeat the content-identity machinery.** M2-T016's entries look like
  `"apps/web/src/** (survey review feature areas)"` — they match no files, so `frozen_git_identity` returns
  the **empty-set hash** `e3b0c442` and the frozen identity binds NO code. M0-T055 is the same. Use real
  pathspecs (M0-T056 now does). Do not retrofit in-flight packets: changing `allowed_paths` moves the
  material digest and invalidates existing verification.
- **M0-T053 is a prerequisite of R595 production actuation.** D-010-R347 makes "no duplicate workers"
  binding, and the ACTIVATION-RECORD PIN records that until M0-T053 lands, `record_launched_child` has no
  production caller, `recover_boot`'s surviving-child fail-closed is inert in production, and the C1
  job-object bar is a written precondition only. M0-T053 is now a dependency of M0-T056.

## Supervised dispatch mechanics
Foreground: `Bash` timeout `1500000` ms, `--unit-timeout 1200 --max-cycles 1 --max-turns 12..16`,
fresh runtime base `%LOCALAPPDATA%/NYCBuildabilitySupervisor-rNN`. **Both provider executables are
REQUIRED** (`start` refuses PATH discovery): `--claude-executable C:\Users\MLFLL\.local\bin\claude.exe`,
`--codex-executable C:\Users\MLFLL\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`.
Worker model is now `claude-opus-4-8` (lawful). Producers spawned via the Agent tool run on their
pinned model (backend-engineer = opus-4.8), unaffected by Fable exhaustion — used for M0-T054 inc1–4.
Orchestrator captures test/commit evidence; in-loop Codex evidence-boundary REVISE/HALT resolved by
orchestrator out-of-loop verification.

## Other open items
- **Owner product-efficiency directive** — captured (D-010 source-029, R320–R343). **Phase 1 DONE**
  (M0-T055, PR #206): `docs/LEAN_OPERATING_PROCESS.md` + CLAUDE.md pointer; canonical routine record =
  per-task `progress_log` + git + CI; lean 7-field ≤2000-tok handoff + 6 seam triggers; 1–2
  routine-control-PR batching; concise-code/parameterized-test/safer-packet guidance. Effective
  **M2-T016 onward** (prospective; nothing retroactive). **Part-D independent review = PASS**
  (control-plane-verifier; verbatim `project-control/reports/M0-T055-partD-review.md`). Remaining for
  M0-T055 accept: G0/G2 + G3/G5 gates (dispatch code-reviewer G3 + security-reviewer G5) +
  verification.json (R320-R343; R338/R339/R342 pending-with-justification; R336 NA post-acceptance) +
  accept. **Phase 2** = run/measure M2-T016 under the rules
  (needs M2-T015 accepted first). **Phase 3** = one bounded projector helper only if M2-T016 still
  shows duplication. PDF keep-vs-replace assessment (B9) = post-M2-T015-acceptance, comparison-only.
  **Apply the lean rules to all product work from M2-T016 on.**
- **M0-T047 (nanoid): STILL RED as of 2026-08-11** — `npm audit` reports 1 HIGH,
  `nanoid <3.3.17` (GHSA-2v37-7h3g-55p8, "custom generators can loop indefinitely when size is zero").
  The age gate has passed, so the bump is now admissible; what blocks it is that the lockfile cannot be
  regenerated here (local npm installs are prohibited). `web-dependency-security` is NON-required, so
  Tier A merges are unaffected, but the advisory is real and the check stays red repo-wide until
  M0-T047 lands a hash-pinned lock bump to >= 3.3.17.
- Rework queue (M0-T021/M0-T034) and the M3 chain (under blockers) remain available.

## Carried rules
- Task branches from origin/main; producers spawned UNNAMED (or via Agent-tool pinned agents);
  classifier denial ⇒ exact-path staging first, else STOP + surface the `!` line; all
  `project-control/**` + `directives/**` explicit LF; commits stage exact paths; ADR-006 Tier A merges
  after green required checks; owner dry-run-first for any elevated script.
- Reviewer models `claude-opus-4-8` xhigh (standing). Orchestrator currently opus-4.8 (manual R286/R295).
- Standing holds unchanged: deployment/G6/Graphify/expansion; supervised runtime; `default_mode=shadow`;
  LIMITED-AUTO off; R595 pre-activation blocking.
