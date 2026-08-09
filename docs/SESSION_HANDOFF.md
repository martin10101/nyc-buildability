# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.
Old session blocks (sessions 1–9) are recoverable via `git log -p docs/SESSION_HANDOFF.md`.

Refreshed **2026-08-09 (session 10, R289 fallback-incident recovery; running on claude-opus-4-8)**.
**This block supersedes older sections**; the ledger wins on any conflict.

## SESSION 10 STATE — R289 = DID-NOT-SWITCH; manual Opus-4.8 recovery; M2-T015 3j done, 3k blocked

**Accepted count 72.** Main `a41f237` (PR #200 merged — verify; may have advanced). Task branch
`task/M2-T015-survey-ingestion` @ **`1e4125c`** (pushed).

**R289 fallback test resolved (D-010 source-027, R292–R303).** Fable 5 hit its weekly usage limit
mid-session and **hard-stopped** ("switch models with /model"). The built-in `fallbackModel` did
**NOT** auto-switch the orchestrator to Opus — verdict **DID-NOT-SWITCH**. The owner switched
manually via `/model claude-opus-4-8`; this session is the R286-authorized **manual** Opus-4.8
successor (the automatic path is not claimed as working). Durable record:
`project-control/reports/D-010-R288-fallback-expectation-log.md` (appended verification section,
original untouched) + `project-control/reports/D-010-R289-fallback-incident/` (hard-stop screenshot).
Three honest causes: config-maybe-not-reloaded / quota-maybe-not-a-`fallbackModel`-trigger /
**no process outside the exhausted session to launch a successor** (load-bearing gap → M0-T054).

**Model posture NOW:** settings (committed, PR #199) `model: claude-fable-5` +
`fallbackModel: ["claude-opus-4-8"]` + `effortLevel: xhigh`. **Worker** `model_selection.toml`
`[claude] model = ""` (lawful account-default; see the R296 block). Reviewers on opus-4.8 xhigh
(standing). **Revert on the owner's typed "Fable is back" (R290):** settings `effortLevel`, reviewer
files, and (if changed) the config allowlist.

**⛔ R296 BLOCKER — supervised WORKER cannot be flipped to opus-4.8 by the mutable path.** The
protected immutable `C:/Program Files/SupervisorConfig/config.toml` has `[claude] allowed_models = []`
(account-default-only). `validate_selection` **fail-closes** on any explicit `claude.model`, so
naming `claude-opus-4-8` in the mutable `model_selection.toml` is rejected (`selection_rejected`), and
R297 forbids editing the protected config. `model_selection.toml` was reverted to the only lawful
value `""`. With settings pinned to exhausted Fable and no auto-fallback, a headless worker cannot
run opus-4.8. **Owner decision needed to unblock 3k dispatch:** either add `claude-opus-4-8` to
`config.toml` `[claude] allowed_models` (owner-only protected-config change), or wait for Fable
credits (R290). This is also a direct input to M0-T054's design.

**M2-T015 = 99%, status blocked. Unit 3j COMPLETE.** 3j-1 `survey_evidence.ts` generator extension
committed @ `1e4125c` (contracts tests 29 passed / 5 new; property_profile/rule_evaluation/scenario
byte-identical). Scope-blocked r32/r33 worker edits were preserved (R298), packet `allowed_paths`
amended for `generate_ts_types.py` + its test. Fixture matrix (4 valid + 8 invalid) existed from
unit 1 (`cabe128`); **SB-S8 green** — `.github/scripts/validate_contracts.py` exit 0, survey_evidence
auto-covered (4/4 valid pass, 8/8 invalid rejected); byte-identity enforced by `contracts-typegen` CI.

**ONLY remaining product unit = 3k** (needs the R296 unblock or a producer path): DecoderSeam wiring
— route the in-repo vector-PDF reader through `services/api/app/documents/extraction/routing.py`
`begin_extraction_job`, STILL behind the fail-closed isolation gate (`isolation.py`, no bypass);
assemble survey_evidence facts; run the deterministic checks; **every gated-edge transition must use
`promotion_gated_transition` (state.py) — raw `transition()` is authority-only**; add e2e real-path
test + `docs/M2-T015-SB-COVERAGE-MATRIX.md` (R272) + full CI (SB-S9). Then
`project-control/reports/M2-T015-producer-report.md`, the gate lifecycle (G0–G5 + DCV + PR + accept),
then **M2-T016** (proof #2).

**Bounded turnover-defect M0-T054 (BACKLOG, R300–R302):** independently-live watchdog OUTSIDE the
Claude session that detects a quota hard stop, preserves evidence, launches **exactly one**
`claude-opus-4-8` xhigh successor, loads the handoff, updates the lawful mutable worker selection,
resumes from the latest safe checkpoint **without duplicate workers/commits**, **fails closed** on
ambiguity; deterministic tests required (restart-config-load, hard-stop-detect, exactly-once-launch,
audit-preservation, duplicate-prevention, safe-failure). Scheduled **after M2-T015 acceptance, before
M2-T016**, unless needed sooner for safe continuation. Small — no supervisor redesign.

## Supervised dispatch mechanics (raised window)

Foreground (not background): `Bash` tool timeout `1500000` ms, `--unit-timeout 1200 --max-cycles 1
--max-turns 12..16`, fresh runtime base `%LOCALAPPDATA%/NYCBuildabilitySupervisor-rNN` (r36 used next
free). **Both provider executables are REQUIRED** (`start` refuses PATH discovery):
`--claude-executable C:\Users\MLFLL\.local\bin\claude.exe`,
`--codex-executable C:\Users\MLFLL\AppData\Roaming\npm\node_modules\@openai\codex\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe`.
Full invocation: `python -m tools.agent_supervisor start --mode supervised --runtime-base <base>
--claude-executable <..> --codex-executable <..> --config "C:\Program Files\SupervisorConfig\config.toml"
--model-selection "C:\SupervisorController\model_selection.toml" --task-packet
project-control/tasks/M2-T015.json --worktree C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015 --branch
task/M2-T015-survey-ingestion`. Scope law: one novel module per window (tests as a follow-up unit);
pattern-mirroring units fit module+tests together; never commit a module without its passing tests
(accumulate rule). Orchestrator captures test/commit evidence (evidence-capture division of labor);
in-loop Codex evidence-boundary REVISE/HALT verdicts are resolved by orchestrator out-of-loop
verification (run suite, review diff, verify scope, commit, record).

## Other open items

- **M0-T047 (nanoid GHSA-2v37-7h3g-55p8):** age-eligible **2026-08-10T10:39:22Z**; until then
  `web-dependency-security` stays red repo-wide (NON-required; Tier A merges unaffected — precedent
  PRs #178–#185).
- **M0-T053** (child-accounting + C1 launch-path containment gate) BACKLOG — blocking only if the
  per-launch C1 Job-Object proof fails or the host changes (D-010 source-025 R244/R245).
- Rework queue (M0-T021/M0-T034) and the M3 chain (under its blockers) remain available.

## Carried rules (unchanged)

- Task branches from origin/main in the orch worktree; producers spawned UNNAMED; classifier denial
  ⇒ exact-path staging first, else STOP and surface the `!` line; `project-control/directives/**` and
  all `project-control/**` explicit LF; commits stage exact paths; ADR-006 Tier A merges after green
  required checks; owner dry-run-first rule for any elevated script (R195).
- **Reviewer models:** gate reviewers `claude-opus-4-8` + `xhigh` (standing fallback; 5 flipped agent
  files uncommitted in the PRIMARY checkout — revert to `claude-fable-5` when owner says "Fable is
  back"). Orchestrator currently opus-4.8 (manual R286/R295 recovery), normally `claude-fable-5`.
- Standing holds unchanged: deployment/G6/Graphify/expansion; supervised runtime, `default_mode=shadow`
  untouched, limited-auto OFF.
