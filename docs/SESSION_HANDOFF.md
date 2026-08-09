# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.
Old session blocks (1–10) are recoverable via `git log -p docs/SESSION_HANDOFF.md`.

Refreshed **2026-08-09 (session 11; running on claude-opus-4-8)**. Supersedes older sections; the
ledger wins on any conflict. (Lean per the parked efficiency directive — see below.)

## SESSION 11 STATE — M0-T054 turnover mechanism IMPLEMENTED (awaiting-gate); one owner-decision surfaced

**Accepted count 72.** Main `dd4a0c9` (PRs #200–#204 merged — verify). Two active task branches:
- `task/M2-T015-survey-ingestion` @ **`1e4125c`** — 3j done; **3k is the only remaining product unit**,
  now HELD by a blocking dependency on M0-T054.
- `task/M0-T054-turnover-watchdog` @ **`9cd7d38`** — the turnover mechanism (below).

**R289 recovery COMPLETE + proven.** Fable hit its weekly limit; built-in `fallbackModel` did NOT
auto-switch (verdict **DID-NOT-SWITCH**, D-010 source-027). Owner manually `/model`'d to Opus 4.8
(this session). Owner then authorized (source-028) adding `claude-opus-4-8` to the protected
`config.toml [claude] allowed_models` (narrowly supersedes R297); **applied + R314 doctor proof ALL
PASS** (accepted SHA `6aef12a9`, line-ending-only diff from pre-registered `9560f901`, owner decision
"A"). Worker `C:/SupervisorController/model_selection.toml` `[claude] model = "claude-opus-4-8"`,
validated against the live config. Evidence: `project-control/reports/M0-T054-protected-config/`
(doctor_proof.py + output) and `.../D-010-R289-fallback-incident/`. **Protected config,
`default_mode=shadow`, supervised runtime, LIMITED-AUTO off — all intact.** Revert worker + settings
`effortLevel` + reviewer files on the owner's typed "Fable is back" (R290).

**M0-T054 (in_progress 75%, owner priority-correction D-010 source-028 R304–R319) — mechanism DONE.**
Four additive increments on the task branch, **69 deterministic tests**, full supervisor suite
**1471 passed / 2 skipped** (freeze baseline ≥1165 preserved, 0 failures):
- inc1 `model_turnover.py` fail-closed detection (25); inc2 `turnover_controller.py` exactly-once
  actuation (16); inc3 `turnover_adapters.py` real lock/audit/launcher/identity (16); inc4 gated
  loop integration `worker_turnover.py` + `loop.py` (+37/−0) + `cli.py` (+10/−0) (12).
- **⚠️ OWNER-DECISION (surfaced, work around, don't block):** production wiring is
  **RECORD-INTENT-ONLY** — `default_actuation_authorization` is False unconditionally because no
  runnable mode authorizes an automatic worker redispatch (shadow forwards nothing; supervised holds
  every forward at `WAIT_FOR_OWNER`; LIMITED-AUTO off). A confirmed exhaustion is
  classified+recorded+surfaced but **never auto-launched** in production. An actual automatic
  production launch needs an owner-authorized actuation channel (**R595 activation**), which conflicts
  with the reaffirmed SHADOW-ONLY / LIMITED-AUTO-off holds. **Owner must decide** whether to authorize
  production auto-launch (R595) or keep record-intent-only. Does NOT block the rest.

**REMAINING (all standard-gate, no owner needed except the R595 decision above):**
1. **M0-T054 bounded LIVE proof (R316)** — on an ISOLATED non-product runtime with an authorized
   channel (authorize=True + real controller/adapters/launcher), drive a real Fable worker (exhausted)
   → detect → exactly one opus-4.8 xhigh successor launched → observe. No production change. Must not
   touch M2-T015 or production data.
2. **M0-T054** producer report + G0/G2/G3/G5 + DCV + acceptance (defect-lane frozen-module change:
   re-establish the `M0-T039-supervisor-freeze.md` baseline at 1471).
3. On M0-T054 acceptance → **resume M2-T015 3k on Opus 4.8** (DecoderSeam: route the in-repo vector-PDF
   reader through `services/api/app/documents/extraction/routing.py::begin_extraction_job`, behind the
   `isolation.py` fail-closed gate; assemble survey_evidence facts; deterministic checks; **every
   gated-edge transition uses `promotion_gated_transition`, raw `transition()` is authority-only**;
   e2e + `docs/M2-T015-SB-COVERAGE-MATRIX.md` (R272) + full CI SB-S9) → producer report → G0–G5 + DCV
   + PR + accept → **M2-T016** (first task under the leaner efficiency process).

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
- **M0-T047 (nanoid):** age-eligible 2026-08-10; until then `web-dependency-security` stays red
  repo-wide (NON-required; Tier A merges unaffected).
- Rework queue (M0-T021/M0-T034) and the M3 chain (under blockers) remain available.

## Carried rules
- Task branches from origin/main; producers spawned UNNAMED (or via Agent-tool pinned agents);
  classifier denial ⇒ exact-path staging first, else STOP + surface the `!` line; all
  `project-control/**` + `directives/**` explicit LF; commits stage exact paths; ADR-006 Tier A merges
  after green required checks; owner dry-run-first for any elevated script.
- Reviewer models `claude-opus-4-8` xhigh (standing). Orchestrator currently opus-4.8 (manual R286/R295).
- Standing holds unchanged: deployment/G6/Graphify/expansion; supervised runtime; `default_mode=shadow`;
  LIMITED-AUTO off; R595 pre-activation blocking.
