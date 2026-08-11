# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.
Old session blocks (1–10) are recoverable via `git log -p docs/SESSION_HANDOFF.md`.

Refreshed **2026-08-09 (session 11; running on claude-opus-4-8)**. Supersedes older sections; the
ledger wins on any conflict. (Lean per the parked efficiency directive — see below.)

## SESSION 13 STATE — M0-T055 + M2-T016 built/reviewed/verified, BLOCKED ONLY on the `accept` permission

Refreshed **2026-08-09 (session 13; claude-opus-4-8)**. **Accepted count still 74** (nothing accepted this
session — see the blocker). Lean 7-field current-state; the ledger wins on conflict.

1. **Active tasks + status.** `M0-T055` (lean-process policy) `awaiting_gate` 96% — fully staged for accept.
   `M2-T016` (survey review UI + review-action API, Packet C) `in_progress` 95% — fully built + reviewed +
   DCV-verified, integrated. `M0-T056` (R595 activation) `backlog` — HELD (Tier-D; build not started).
2. **Active branch + latest safe SHA.** origin/main `37667ff` (unchanged). M2-T016 code branch
   `task/M2-T016-survey-review` @ `d45f330` → **PR #216** (open, CI running, NOT merged). Backend unit
   `57d8574`, frontend unit `dc8c5de` (both on the branch).
3. **Completed units.** M0-T055: G2/G3/G5 PASS + DCV 21/21 PASS; verification.json row IN the D-010 registry;
   packet corrected (governance type, G0 dropped as structurally non-recordable for an orchestrator-produced
   task). M2-T016: design spec + backend (G3+G5 delta PASS, blocking C1/F1 found+fixed, 190 tests) + frontend
   (G3-code + human-journey delta PASS, F1/F3 fixed) + DCV **77/77 PASS** (`reports/M2-T016-DCV-verification.json`).
   R595 owner authorization captured verbatim (D-010 `source-030-amendment.md`, uncommitted; R344-R351 registry
   append still owed before any M0-T056 dispatch).
4. **Current unfinished unit.** M2-T016 control-plane finalization: transcribe the 77-row verification.json into
   the D-010 registry, record G0/G2/G3/G4/G5 at the acceptance HEAD, create the B-001-blocked survey-review
   HTTP-route/production-`ReviewStore` follow-up task, merge #216 after CI green, accept. M0-T055: re-stamp
   reviewed_sha (empty-set identity, stable) + accept.
5. **Blockers / owner decisions.** **BLOCKER — the `accept` CLI is denied by the auto-mode permission
   classifier** (only `accept` + directive-registry Bash-writes are gated; build/review/gate/push/PR all work).
   Nothing lands without the owner allowing/running `python tools/project_control.py accept`. Owner decisions
   surfaced (mechanisms built, non-blocking): professional-confirmation **role identity** (Tier-D legal);
   authoritative **survey-geometry** as a profile input (new contracted decision, STOP); **R595** production
   auto-launch authorized (M0-T056) but build held.
6. **Exact next action.** Owner: `! python tools/project_control.py accept --task-id M0-T055 --agent orchestrator`
   (or allow that command). Then finalize + accept M2-T016 (transcribe DCV → registry, record gates at the
   integration HEAD, merge #216, accept), then optionally the held M0-T056 (R595) build.
7. **Authoritative evidence.** `project-control/tasks/{M0-T055,M2-T016,M0-T056}.json` progress_logs (canonical);
   `project-control/reports/M2-T016-*` (verbatim gate reports + DCV JSON + producer report); PR #216;
   D-010 `verification.json` (M0-T055 row) + `source-030-amendment.md`; worktrees `M2-T016-integrate` (d45f330),
   `agent-a8724b1c4277f23fe` (backend), `agent-a973a7a01a1a58933` (frontend), `agent-a670edbfa2d06a655` (spec).

## SESSION 12 STATE — M0-T054 + M2-T015 BOTH ACCEPTED (74); next = M2-T016 / M0-T055

Refreshed **2026-08-09 (session 12; claude-opus-4-8)**. **Accepted count 74.** Main **`d265269`** (verify).

- **M0-T054 ACCEPTED (73)** — unattended Fable→Opus turnover watchdog. Code merged PR #211; acceptance
  PR #212. Gates G0/G2/G3/G5 + DCV 16/16 PASS. **Mechanism only (record-intent-only in production); live
  auto-actuation = owner-gated R595 (follow-up M0-T056), NOT a defect.** SHADOW-ONLY / LIMITED-AUTO-off /
  protected-config holds unchanged.
- **M2-T015 ACCEPTED (74)** — secure survey/official-document ingestion + deterministic-verification
  pipeline (Packet B). Units 3k (DecoderSeam behind isolation gate) + 3l (SB-S4 tax-lot BBL cross-check)
  → code PR #213 → acceptance PR #214. **97/97 D-010 PASS; gates G0–G5 + DCV all PASS.** A full 4-reviewer
  gate wave (897e7df) correctly FAILED it (ruff + missing named outputs + stale report); reworked
  (whole-tree ruff 0.13.0 clean, committed synthetic fixture pack SVY01–SVY14 + MANIFEST +
  `docs/SURVEY_FIXTURE_MATRIX.md`, report current) → re-gated at 1b3af35 → accepted.
  **Honestly-deferred LATER units (documented in SURVEY_FIXTURE_MATRIX + coverage matrix):** SB-S4 AREA
  cross-check (needs lot-area geometry reconstruction), OCR/raster extraction, rotation-normalization,
  distance/bearing normalization, boundary/area reconstruction. B-001 storage still designed-but-deferred.

**⚠ ENV LANDMINE — PEP 695 / Python 3.12:** `services/api/app/documents/units.py::_match_unit` uses PEP 695
generics (correct: `requires-python>=3.12`, ruff `target-version=py312`, CI `api` job = Python **3.12**).
**This sandbox has only Python 3.11.9** (the `py -0p`-listed 3.13 exe is MISSING) → `pytest` cannot even
collect `tests/documents/` (SyntaxError on import). Verify Python via the **captured 3.12 CI evidence**
(evidence-capture division of labor); ruff parses independently so `ruff check .` still works locally. Also:
**local ruff was 0.9.9 but CI pins 0.13.0** — always `pip install ruff==0.13.0` before trusting a local ruff
result (0.9.9 flags UP038 which 0.13.0 dropped, and misses I001/UP047 sorting differences → a false "clean").

**NEXT (no owner needed):**
1. **M0-T055** (lean operating process) — Part-D review PASS on file; remaining: G3 (code-reviewer) + G5
   (security-reviewer) gates + verification.json (R320–R343) + accept. Small acceptance cycle.
2. **M2-T016** — first product task under the lean process (needs M2-T015 accepted — now done). Contract
   via `/start-controlled-task`, then dispatch under `docs/LEAN_OPERATING_PROCESS.md`.
3. Optional follow-ups: **M0-T056** (R595 live-activation, owner-gated), the M2-T015 deferred later units,
   rework queue (M0-T021/M0-T034), the M3 chain (under blockers).

**Repo hygiene done this session:** reviewer-model fallback flip + agent-memory flush committed; redundant
owner-directive intake copies + `.npmrc` + settings backups gitignored; transient `*.sqlite3-wal/-shm`
gitignored; survey fixture pack marked `binary` in `.gitattributes`.

---

## SESSION 11 STATE (historical) — M0-T054 turnover mechanism IMPLEMENTED (awaiting-gate); one owner-decision surfaced

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

**M0-T054 (in_progress 90%, D-010 source-028 R304–R319) — mechanism + LIVE PROOF DONE; gates in flight.**
Task branch `task/M0-T054-turnover-watchdog` @ **`3c36c42`**. **Five** additive increments, **79
deterministic tests**, full supervisor suite **1481 passed / 2 skipped** (freeze baseline preserved):
- inc1 detection (25); inc2 exactly-once actuation (16); inc3 real adapters (16); inc4 gated loop
  integration `loop.py` (+37/−0) + `cli.py` (+10/−0) (12); inc5 live-signal plumbing (10) — surfaces
  the real exhaustion evidence (`result_text` + `seven_day` rate-limit) so the turnover fires in the
  live loop (a real gap the live proof caught; `claude_runner.py` additive).
- **LIVE PROOF (R316) DONE** — `project-control/reports/M0-T054-live-proof/LIVE-PROOF.md`: real Fable
  exhaustion (exit 1, real signal) → `classify_exhaustion` → FABLE_EXHAUSTED → integration on the real
  signal → one opus-4-8 launch decision + audit link → a **real opus-4.8 worker launches** (exit 0).
  Every real link proven; only the single-continuous-auto-run is production-gated (see below).
- **ALL 3 GATES PASS at `3c36c42`** (verbatim reports on main): G3 code-reviewer PASS
  (`M0-T054-G3-code-review.md`), G5 security-reviewer PASS (`M0-T054-G5-security-review.md`), DCV
  directive-compliance-verifier PASS 16/16 (`M0-T054-DCV-verification.md`). **READY TO ACCEPT.**
- **EXACT ACCEPT RECIPE (mechanical, all evidence PASS):** M0-T054 applicable D-010 set = **16 reqs**
  `[R300,R301,R302,R304,R305,R306,R307,R308,R309,R310,R312,R315,R316,R317,R318,R319]` (compute:
  `DirectiveRegistry().derive_applicable(M0-T054.json)`). Steps: (1) write a `verification.json`
  **v2** `task_verifications[]` row for M0-T054 — `directive_id=D-010`, `producer=orchestrator`,
  `verifier=directive-compliance-verifier`, `reviewed_sha=3c36c42` (must == the reviewed HEAD),
  `reviewed_manifest_sha256`, and a `requirements[]` row **state=PASS** for each of the 16
  (R305/R306/R310 carry the live-activation-deferred note; all PASS at mechanism scope per the DCV);
  (2) producer report (AOS s6); (3) `submit --requested-status awaiting_gate` with an evidence-map;
  (4) record gates G0/G2/G3/G5 (`--sha 3c36c42`); (5) `accept --task-id M0-T054 --agent orchestrator`.
  Watch the `reviewed_sha==HEAD` + material-identity gotchas (see memory `in-regime-accept-mechanics`).
  Accepting M0-T054 **unblocks M2-T015 3k**.
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
