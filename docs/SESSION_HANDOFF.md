# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-09 (session 9, SUPERVISED-AUTO active; M2-T015 98%, unit 3i complete)**.
**This block supersedes older sections**; the ledger wins on any conflict.

## SESSION 9 STATE — M2-T015 ingestion/validation/reader chain COMPLETE through unit 3i

**Accepted count 72.** Main `0f1d3df` (at refresh; verify live). Task branch
`task/M2-T015-survey-ingestion` @ **`733df60`** — units 1..3i all committed+pushed, each with
passing tests. Full `services/api/tests/documents/` suite at that SHA: **888 passed / 1 skipped**
(symlink skip runs on Linux CI).

**Delivered this session (each a committed micro-unit, all supervised runs):** 3d-2 unit typing
H2 (`b3d2398`); 3e-1 geometry/location validation H3 (`2174505`); 3e-2 correction-history H4
(`3b0f2bc`); 3f-1 promotion gate module H5 (`05fcb1c`); 3f-2 state-machine wiring R265
(`98e87bc`); 3g-1..3 all eight SB-S3 deterministic checks (`16b8a08`,`c17fc01`,`66daba4`);
3h SB-S4 tax-lot cross-check (`bb37b98`); 3i-1 fail-closed isolation gate R275/R276 (`1e0bbfa`);
3i-2 format routing + isolation-gated entry + wrong-address routing SB-S2/S7 (`6733347`);
3i-3a-1/2/3a/3b + 3i-3b the complete IN-REPO strict-subset deterministic vector-PDF reader
(lexer -> objects -> xref -> container -> content interpreter; `b210d56`,`9fd3b19`,`7aea0a0`,
`c12f41a`,`733df60`).

**Design decision (recorded in ledger + commits):** no third-party PDF parser is admitted and
`requirements.in` is OUTSIDE the packet's allowed_paths, so the SB-S1/R274 real vector path is
the in-repo fail-closed grounded-subset reader; a hardened third-party parser remains a lawful
LATER G5 dependency-admission step. Production parsing stays DISABLED wherever the
Landlock+seccomp boundary is unprovable (isolation.py, no bypass); Linux CI is the provable
substrate (R274/R275); production enablement deployment-gated under B-001.

**REMAINING M2-T015 work:** **3j** H6 adversarial fixture matrix + H7 contract pipeline +
`packages/contracts/generated/survey_evidence.ts` generation or lawful-exclusion record + SB-S8;
**3k** DecoderSeam wiring (route the pdf reader through `begin_extraction_job`; ALL gated-edge
call sites must use `promotion_gated_transition`, raw `transition()` is authority-only — standing
forward-note), e2e real-path test, `docs/M2-T015-SB-COVERAGE-MATRIX.md` (R272), full CI/SB-S9;
then `project-control/reports/M2-T015-producer-report.md`, then the gate lifecycle (G0-G5 + DCV +
CI + PR + merge + accept), then **M2-T016** (proof #2).

**SUPERVISED MECHANICS — SESSION-9 LESSONS (critical, supersede session-8 cadence notes):**

1. **Foreground, not background.** The harness background-kill window shrank below worker
   time-to-first-write (3 consecutive zero-output kills). Run every unit FOREGROUND:
   Bash-tool timeout 600000, `--unit-timeout 540 --max-cycles 1 --max-turns 12..16`. Reliable
   for ~24 runs since.
2. **Fresh runtime base per unit**: `%LOCALAPPDATA%/NYCBuildabilitySupervisor-rNN` (r8..r31
   used; NEXT = r32). A PAUSED_RECOVERY base can be reused only after the audited
   `clear-recovery` verb.
3. **Scope law:** novel-design units (parsers, new engines) fit ONE module per window — tests
   as a follow-up tests-only unit; pattern-mirroring units (validators/checks following an
   existing module's idiom) fit module+tests together. Never commit a module without its
   passing tests (accumulate rule). If a window produces zero writes, split the scope, don't
   just retry.
4. **Worker prompts must forbid shell commands** (no packet-documented test command exists, so
   every command DEFERs and wastes turns) and demand write-first turn budgets + an HONEST
   checkpoint stating tests run out-of-loop.
5. **In-loop Codex verdicts of the evidence-boundary class** (HALT_UNSAFE/REVISE complaining the
   packet lacks the task-worktree diff/tests — supervisor collects git evidence from the
   canonical checkout) are RESOLVED by orchestrator out-of-loop verification per the
   evidence-capture division of labor: run the suite, review the diff, verify scope, commit,
   record in ledger. Honest checkpoints have also yielded clean CONTINUEs.
6. Dispatch command template unchanged (see session-8 block below); model_selection pins the
   worker to claude-fable-5; one r29-class provider stall (2 events/540s) — just retry on a
   fresh base.

_Session-8 activation/mechanics block retained below (still-valid template + activation
history)._

**Accepted count 72.** Main `7b4f30f` (at refresh; may have advanced — verify). Task branch
`task/M2-T015-survey-ingestion` @ **`9120a02`** carries the M2-T015 product work (not yet PR'd;
opens at task completion).

**Activation done + durable (do not redo):** owner typed SUPERVISED-AUTO decision captured
(D-010 source-023, PR #189/#190); active runtime = supervised, `default_mode=shadow` untouched,
limited-auto OFF. B-018 resolved; **M0-T052** (START_CLAUDE crash-window fix) ACCEPTED (PR
#192/#193). **M0-T053** contracted BACKLOG (child-accounting + C1 launch-path containment gate) —
becomes blocking only if the per-launch C1 Job-Object proof fails or the host changes (D-010
source-025 R244/R245); otherwise finish M2-T015+M2-T016 first. Activation-record C1 pin
(per-launch `containment: job_object`) is in `M0-T036-ACTIVATION-CHECKLIST.md`.

**Owner directive D-010 source-025 (R242-R284)** = product-first M2-T015 hardening + SB-S1..S9
scope closure. Routing/coverage map: `project-control/reports/M2-T015-ROUTING-COVERAGE-MAP.md`
(all 8 hardening areas INSIDE M2-T015 via **v1 application validators**, no v2 wire break; only
deferred item = production parser-isolation/storage DEPLOYMENT under B-001; code lands in-task +
CI-proven).

**M2-T015 progress = 68%.** Committed micro-units on the task branch (each with passing tests):
3a models+state machine, 3b S1 upload gate (3b-1 sniff+extension, 3b-2 size+SHA256, 3b-3
temp-path), 3c immutable-original storage abstraction, 3d-1 fact-type taxonomy (H1). Full
`services/api/tests/documents/` suite: **161 passed / 1 skipped** (symlink-forbidden host;
runs on Linux CI). **NEXT micro-units** (routing map order): 3d-2 unit typing (H2), 3e
geometry+correction-history (H3/H4), 3f promotion gate (H5), 3g deterministic checks (SB-S3),
3h tax-lot cross-check (SB-S4), 3i extraction+parser-isolation gate (SB-S1/S2/S7), 3j adversarial
fixtures + contract pipeline + `survey_evidence.ts` (H6/H7/SB-S8), 3k end-to-end real path +
SB-S1..S9 coverage matrix + full CI (R272/R274/SB-S9). Then M2-T015 gate lifecycle (G0-G5 + DCV +
CI + PR + merge + accept), then **M2-T016** (proof #2).

**SUPERVISED EXECUTION MECHANICS (critical for resume):** run the worker via
`python -m tools.agent_supervisor start --mode supervised --runtime-base <fresh base per unit>
--config "C:\Program Files\SupervisorConfig\config.toml" --model-selection
"C:\SupervisorController\model_selection.toml" --task-packet project-control/tasks/M2-T015.json
--worktree C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015 --branch task/M2-T015-survey-ingestion`.
**The harness kills long background commands unpredictably**, so: keep each unit tiny (≤~16
max-turns), one small module + its tests; on kill, the M0-T052 fix lets `start` re-enter from
START_CLAUDE, and worker output already written is preserved — **accumulate surviving code/test
halves across retries, never commit code without its passing tests**. Orchestrator captures the
test/commit evidence (evidence-capture division of labor). Reviewer models `claude-opus-4-8`
xhigh (Fable fallback); producer/orchestrator per D-004.

_History: session-7 block (activation prerequisites) recoverable via `git log -p
docs/SESSION_HANDOFF.md`._

<!-- superseded session-7 block retained below for reference -->

## SESSION 7 STATE — ALL ACTIVATION PREREQUISITES CLOSED (superseded by Session 8)

**Accepted count 71.** Main (at refresh) `1fd9983`. Full supervisor suite **1392 passed / 2
skipped** (the 2 skips adjudicated legitimately environment-conditional, R155/R156).

Units accepted + merged this session:

- **M0-T048** (PR #180/#181, count 68): C2 closure + owner-ordered G3-MAJOR-1 fix — cross-process
  resume cross-checks the journal `approved_digest` against the sealed hash-chained
  operator-approval audit event before any forward; fail-closed, zero provider calls, durable
  refusal. R152 deferred-then-DISCHARGED. Residuals carried to the activation decision: **G5 N-4**
  (full-local-write chain rewrite — R140-excluded, Phase 3 Option A external anchoring), **G5
  N-5** (same-run approved-content replay — narrowed), **G3 MINOR-2** (fail-closed ambiguity
  false-refusal edge).
- **Controller-config relocation** (source-017/018, PR #182/#183): owner-run elevated move to
  `C:\Program Files\SupervisorConfig\config.toml` (dedicated protected parent; the original
  `C:\SupervisorConfig` plan was STOPPED by the C:\ inherited-Modify preflight check).
  `model_selection.toml` stays MUTABLE at `C:\SupervisorController\model_selection.toml`.
  Config-content check ruled the shadow config exactly correct for supervised-auto (no immutable
  field change needed; claude allowlist [] = account-default posture, live-proven).
- **M0-T049/T050/T051** (PRs #184/#185/+, counts 69-71): THREE owner-demonstrated
  hardening-script defects, each caught by the owner's fail-closed inspection BEFORE privilege
  was exercised, each fixed + adversarially regression-tested + G3/G5/DCV'd + merged:
  (1) WinPS 5.1 parser failure (`$Var:` interpolation) → brace fix + whole-script parser-API test;
  (2) `$Args` automatic-variable collision dropped every command argument → `$CommandArgs` +
  full-vector dry-run tests + dry-run wording branch;
  (3) explicit `Authenticated Users:(M)` ACE survived the apply → `icacls /reset` before
  `/inheritance:r` (deterministic three-ACE DACL by construction) + poisoned-fixture tests.
  **Barred blobs (never elevate): `0f01d649`, `ca3811cd`, `9625514e`. Applied reviewed blob:
  `b6ee6589d93b4cd95283ce6d45c22f7010aba56a`.**
- **LIVE PROTECTED PROOF captured + merged** (`M0-T036-PROTECTED-live-proof.md` + raw doctor
  JSON): unelevated doctor — `controller_config_acl.protected: true`, file + parent both
  PROTECTED, config readable, SHA `29eb765e..da1cb` unchanged, model_selection unelevated-
  writable, nothing activated. Closes the last activation-checklist item.

**Directive registry:** D-010 sources 015–022 captured (R144–R213), validator green throughout;
verification rows recorded for M0-T048/T049/T050/T051 (all-PASS at their frozen identities).

## THE ONE REMAINING ITEM (R131/R212)

⛔ NO activation without the owner typing the decision line (presented 2026-08-08, with the
N-4/N-5/MINOR-2 residuals disclosed):
`ACTIVATE SUPERVISED-AUTO — I have read and accept the N-4/N-5/MINOR-2 residuals; proceed per R595/R131.`
(or `HOLD activation`). On the typed activation line: record it durably (directive capture), then
dispatch **M2-T015 + M2-T016** as the two supervised-auto product proof tasks — HELD until then
(R133/R143/R153/R167/R196/R213).

## OTHER OPEN ITEMS

- **M0-T047 (nanoid GHSA-2v37-7h3g-55p8):** age-eligible **2026-08-10T10:39:22Z**; contracted
  packet (CI-bot lock regeneration, NO local npm); until then `web-dependency-security` stays red
  repo-wide (NON-required; Tier A merges unaffected — precedent PRs #178–#185).
- **Registered follow-up candidates (reviewer-recommended, owner-optional, none contracted):**
  rollback-path dry-run wording (same class as R190, one-line branch); parent-first hardening
  order (removes the theoretical transient in the general case); MINOR-2 cycle-disambiguation;
  `-rs` on the CI pytest invocation; Phase 3 external audit-anchor (Option A) for N-4.
- **Housekeeping (classifier-denied, owner may run):** `! git push origin --delete task/M0-T048-c2-close`
  and `! git branch -D task/M0-T048-c2-close` (content fully merged). The orch worktree sits on
  the merged `task/M0-T051-explicit-ace-strip`; re-point at next claim.
- Rework queue (M0-T021/M0-T034) and the M3 chain (under its blockers) remain available.

## Carried rules (unchanged)

- Task branches from origin/main in the orch worktree; producers spawned UNNAMED; classifier
  denial ⇒ exact-path staging first, else STOP and surface the `!` line;
  `project-control/directives/**` explicit LF; commits stage exact paths; ADR-006 Tier A merges
  after green required checks; owner dry-run-first rule for any elevated script (R195).
- **Reviewer models:** gate reviewers `claude-opus-4-8` + `xhigh` (standing fallback; the 5
  flipped agent files remain uncommitted in the PRIMARY checkout — revert to `claude-fable-5`
  pins when the owner says "Fable is back"). Orchestrator `claude-fable-5`.
- Standing holds unchanged: deployment/G6/Graphify/expansion; SHADOW-ONLY until the owner's typed
  activation decision.

---

_History: superseded session blocks (sessions 1–7 pre-seam = CP-0037..CP-0045) recoverable via
`git log -p docs/SESSION_HANDOFF.md`; the ledger remains authoritative._
