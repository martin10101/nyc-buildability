# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-04**, at the V1.2-integrated / session-wrap point.

## Where things are

| | |
|---|---|
| `origin/main` | `cb9a999` (owner's PR #150 merge; unchanged all session) |
| task branch | `task/M0-T036-supervisor-bridge` tip **`6548ee1`** (V1.2 code at `33e3336`) |
| accepted tasks | **55** (M0-T035 accepted 2026-08-04) |
| registries | D-004 **v24** (745 ids, model-governance R734-R745) · D-006 · D-007 **v11** (596 ids, thru amendment 10) |

## 1. M0-T036 — supervisor build: Phase 5 done, V1.1 re-gated, V1.2 integrated (98%, in_progress)

- **Phase 5 decision packet** (`reports/M0-T036-PHASE5-DECISION-PACKET.md`, frozen 43848bd): shadow
  pilot 1-6 (run 6 full live cycle, 0/2 touches); five independent gate reviews all PASS; owner
  decision **DO NOT ACTIVATE** — shadow-only stands (D-007 am.7, R577; §6 allowlist inert).
- **V1.1 correction unit** (frozen c193a52): B-1..B-4 + F-2/F-4/F-5 + L-1/V-6/V-4; five-review delta
  re-gate all PASS; reviews preserved `reports/M0-T036-V1.1-*`.
- **V1.2 unit — BUILT + INTEGRATED at `33e3336`** (D-007 am.10, R592): (A) approval-broker wiring
  into the assembled loop (closes G3 V-1 — supervised allow path reachable; shadow permits/forwards
  nothing); (B) model-identity discipline (R739 — explicit `--model`, per-event model verification,
  downgrade → dispatch-nothing-new/finish-bounded/refresh-handoff/rotate/relaunch-pinned, unavailable
  → pause+notify); (C) context-threshold rotation (R743-745 — `context_rotation_threshold` default
  400000, treated exactly like a downgrade; B+C share one **seam-only** actuator, never mid-unit).
  Orchestrator verification: 7/7 hashes match producer, **1114 passed / 2 skipped** (+23, zero
  regressions), doctor PASS, scanner PASS. Verbatim diff `reports/M0-T036-V1.2.diff`.
- **doctor --live probe** (owner-authorized, R588): control-response wrapper **VERIFIED live (deny
  leg)** on the controller (`reports/M0-T036-doctor-live-probe.md`). Allow leg deferred to V1.2 by
  design (owner ruled the deny leg satisfies the R739/R582 gate; R591).

## 2. NEXT — the three V1.2 live exercises (orchestrator-run; pending the owner controller pull)

Ready to run once the owner pulls the controller to current (`git -C C:/SupervisorController pull
--ff-only`; controller is at 58d036f, needs `6548ee1`). All three use **synthetic probe units only**,
shadow-only for real work, nothing forwards to a real task (R593/R594); evidence preserved verbatim.
Synthetic packet staged in the session scratchpad. Exact invocations in
`reports/M0-T036-V1.2.diff` producer return (§4):
1. **Live allow round-trip** (closes QA gap 1): supervised synthetic unit, in-scope AUTO tool
   permitted by the wired broker and actually executes.
2. **Live rotation** (closes QA gap 4): `--context-rotation-threshold 1 --max-cycles 2` → seam
   rotation before cycle 2 (`reason_code=context_threshold`).
3. **Live model mismatch**: `--expected-worker-model claude-does-not-exist-99 --max-cycles 2` →
   detected downgrade → seam rotation (`reason_code=model_downgrade`); worker launches only on its
   real model.

After the exercises: freeze the SHA and HOLD for the Fable-5 reviews (§4).

## 3. Model governance — LANDED (D-004 am.22-24, R734-R745; commit 8b1b386)

- `.claude/settings.json` `model: claude-fable-5` (NEW sessions default Fable 5; effortLevel unwritten
  — high is the Fable 5 default; no standing xhigh/max in any settings file; no subagent-model env var).
- **Six-file Fable-5 pinned set** (explicit, no effort key): the 5 gate reviewers + the orchestrator
  agent. **19 non-reviewer agents**: `model: claude-opus-4-8` + `effort: high`.
- **Live-session note:** the MAIN session runs **Opus 4.8** by a live override (/fast or /model).
  **Owner directive: leave main on Opus until the Fable-5-pinned reviews are done** — switching early
  would draw on the Fable 5 window being preserved for the V1.2 delta re-gate + the held G2 wave.

## 4. HELD / NOT AUTHORIZED (owner-gated; do not do without a fresh owner instruction)

- **Fable-5-pinned reviews** — the **V1.2 delta re-gate** (five-review wave over the 33e3336 delta) and
  the **held G2 wave** for M0-T036 (satisfies control-plane F-CPΔ-3; G2 record must exist before any
  M0-T036 acceptance): both run **only after the owner says the Fable 5 window has reset** (R596/R589).
- **Supervised single-forward rehearsal** — NOT authorized; returns to the owner after the V1.2 delta
  re-gate (R595).
- **Limited-auto activation** — DECLINED; shadow-only in force (R577). §6 AUTO-allowlist proposal inert
  (R578). **M0-T036 formal acceptance** — needs the G2 record first, then owner decision.
- Also standing: any merge without owner execution (R721); effort keys beyond the named model-governance
  keys (R159 stands, Codex-side + supervisor §3.1 config); settings/hooks/rules changes; **no npm
  install/update anywhere, apps/web lockfile frozen (R586)**; deployment/holds; G6/Graphify/expansion/
  survey; M0-T029/M0-T032/M0-T025; product/legal-rule changes.

## 5. Standing discipline (carry forward)

- **Ledger writes go through `tools/project_control.py` ONLY** (CPV F-CP-1 lesson: hand-edits are
  caught and require CLI re-record). Every directive amendment gets a `manifest.audit_log` entry AT
  capture time (F-CP-2). Registry must validate clean (`validate_directive_compliance.py --check`).
- **R740 (binding):** an owner-typed gated command that fails closed and is later made ready comes
  back to the owner as a line to TYPE; a session-executed act is never labeled owner-typed. (The
  M0-T035 accept was session-executed after the owner-typed attempt failed closed — label corrected
  in the record.)
- Gate-class spawns pinned Fable 5; producers unnamed (now Opus 4.8 via frontmatter), reviewers named.
  Reviewers are read-only, may signal idle without delivering — demand the full return, preserve it
  verbatim the moment it arrives.
- Controller checkout `C:\SupervisorController` is owner-plane / read-only from Claude — the OWNER
  pulls it; the supervisor runs from there. Runtime dirs under `%LOCALAPPDATA%\NYCBuildabilitySupervisor\`
  (incl. `*.pilot-run*-parked`) are owner-plane; never touch/clean.
- Owner-plane local state (never touch): the modified backend-engineer memory file, untracked
  agent-memory files, `.claude/settings.local.json.bak-2026-08-03`, the many stale
  `worktree-agent-*` branches/worktrees and the M0-T030/M0-T031 codegraph worktrees, the
  `bad-amend-backup` and owner `git stash` entries.

## 6. Session-end status

Nothing is running in the background (V1.2 producer completed; all monitors stopped; no gh watches).
Everything through V1.2 integration is committed and pushed at `6548ee1`. A fresh session takes over
from here: on resume, if the owner has pulled the controller, run the three live exercises; the
Fable-5 reviews and everything in §4 wait for explicit owner instruction.
