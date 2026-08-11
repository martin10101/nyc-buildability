# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.
Old session blocks (1–14) are recoverable via `git log -p docs/SESSION_HANDOFF.md`. Keep this file
CURRENT-ONLY: the `context-budget` CI check is a REQUIRED status and fails the PR above ~4000 tokens,
so trim the previous session's block when you add yours.

## SESSION 15 STATE — bounded truth reconciliation (owner directive D-011); nothing accepted this session

Refreshed **2026-08-11 (session 15; model `claude-opus-4-8`)**. The prior session's "PRs #217/#218 open
and green" claim was **false** and is corrected here. **Accepted count = 75** (M0-T055 accepted on this
branch only — see below). No new acceptance this session. The ledger wins on any conflict.

### Ground truth (verified live 2026-08-11)

- **origin/main = `7cc1fed`**. **PR #216 MERGED** — M2-T016 survey-review product code is on main.
- **PR #217** open (control `control/session14-m0t055-accept`), **PR #218** open
  (`task/M0-T053-child-accounting` @ `a3873311`). **Neither is fully green.** On BOTH, every
  functional/required check passes; the ONLY red is **`web-dependency-security`** (non-required) on the
  known **nanoid** advisory GHSA-2v37-7h3g-55p8 (needs ≥3.3.17; the lock still pins 3.3.16). So the
  workflow conclusion is red while all required contexts are green — do not call them "green".
- **M2-T016 code is merged (PR #216) but the TASK is NOT accepted** — status `in_progress` 97%. "Merged"
  ≠ "accepted".
- **M0-T053** producer work COMPLETE and both independent reviews **RETURNED**: G5 security PASS and G3
  code PASS (verbatim reports on file). Gates not yet recorded; task `in_progress` 96%, not accepted.
- **No Opus 5 authorship** is claimed anywhere; this session ran on `claude-opus-4-8` (owner-set).

### `accept` fails closed already (item 4 — verified)

`project_control.py accept()` (lines 1196-1199) refuses when **any required gate has no PASS record**, and
`INDEPENDENT_GATES` further reject a `self_check` role or a gate recorded by the producer. **Reviewer
silence therefore can never become acceptance** — there is simply no PASS record, so accept fails closed.
**P6 is additive, not a duplicate gate:** it should add bounded reviewer-timeout detection → one controlled
retry / re-dispatch → then **PAUSE/STOP with visible evidence**. It does not touch the acceptance gate.

### R595 pre-actuation pins — correct classification (item 3; NOT eight equivalent blockers)

Pinned in `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md`. Before M0-T056 **live actuation**:

- **P1, P2, P3 — REQUIRED engineering corrections** (G5): P1 claude_runner terminate-without-verify (live
  unrecorded orphan → double-launch on R347); P2 `clear_child_record` whole-key wipe (fail-open once the
  M0-T056 successor-launch seam records anything); P3 achieved per-cycle containment must **STOP**, not
  merely record.
- **P6 — REQUIRED, deterministic**: reviewer timeout → one retry/re-dispatch → PAUSE/STOP (above).
- **P4, P5 — RECOMMENDATIONS, not mandatory blockers.**
- **P7 — wording/interpretation**: "doctor parity" is wrong; doctor and the launch gate share a
  containment **source** (`default_containment_kind()`), but their **verdicts are not equivalent** (doctor
  prints `ok` on POSIX/process_group while the gate REFUSES). Use "same containment source".
- **P8 — Windows-only deployment constraint**: the gate hard-refuses on every POSIX host (incl. Render and
  shadow mode), so the supervisor is currently Windows-Job-Object-only. Real narrowing, breaks nothing today.

### Active tasks + what each still needs

1. **M0-T055** accepted on THIS branch only (PR #217, not merged → on main it is effectively in-flight).
   Its `allowed_paths` is empty ⇒ frozen identity is the **empty-set hash** `e3b0c442`, binding no files.
   **D-011 item 5**: repair `allowed_paths` to its real deliverables (`docs/LEAN_OPERATING_PROCESS.md`,
   `CLAUDE.md`, its reports) and rerun ONLY the identity-bound gate/DCV evidence that repair invalidates.
2. **M2-T016** `in_progress` — merged code, not accepted. Exact-head **G3 delta re-attestation PASS at
   `e3c2ce6`** is preserved (`reports/M2-T016-delta-G3-code-review.md`). **OUTSTANDING**: the SECOND G3
   reviewer's return is held only as an explicitly-labelled condensation — the verbatim second return is
   NOT captured; do not treat the condensation as verbatim. Also owed: G5 delta, G0/G2/G4 records, a
   RE-STAMPED DCV at the gated head, and the same empty-set `allowed_paths` repair (item 5).
3. **M0-T053** — record G0/G2/G3/G5, DCV, then accept. P1/P2/P3 are pre-**M0-T056**, NOT pre-M0-T053
   acceptance. Preserve the verbatim G5 return (owed at `reports/M0-T053-G5-security-review.md`).
4. **M0-T057** backlog — the empty-identity fail-closed guard (D-011 item 6): smallest mechanical guard
   that REFUSES when a non-path-free task's `allowed_paths` resolve to the empty set; allow an explicit
   opt-in marker + justification for genuinely path-free governance packets. Audit already captured.
5. **M0-T047** backlog — nanoid 3.3.17 remediation (D-011 item 8): add exact-pin `overrides` to
   `apps/web/package.json` and regenerate the lock via the **CI-bot workflow (NO local npm)**; age gate now
   passes (earliest 2026-08-10). No waiver, no audit suppression, no unrelated upgrades.

### R595 / Codex — NOT activated (holds stand)

D-011 R001-R003 re-affirm: **do not start M0-T056, do not activate R595, do not add the broad accept
allowlist.** "Open Codex fully" is the destination, not authorization. Gating before actuation: land
P1-P3 + P6, accept M0-T053, then owner flips the switch. **Model-fallback (D-011 R018):** each new session
must try the MAIN model first and fall back to the lazy model ONLY on unavailability (cap/token/outage),
never sticky across sessions — supervisor investigation in flight.

## Carried rules
- Task branches from origin/main; producers spawned **UNNAMED** (named spawns hit `readonly_agent_guard`
  fail-closed); classifier denial ⇒ exact-path staging first, else STOP + surface the `!` line; all
  `project-control/**` + `directives/**` explicit LF; commits stage exact paths; ADR-006 Tier A merges
  after green **required** checks; owner dry-run-first for any elevated script.
- **Prose `allowed_paths` silently defeat the identity machinery** — use real pathspecs. Do not retrofit
  accepted packets (moving the digest invalidates their verification); M0-T057 is the mechanical fix.
- Reviewer models `claude-opus-4-8` xhigh (standing). Orchestrator currently `claude-opus-4-8`.
- Standing holds unchanged: deployment/G6/Graphify/expansion; supervised runtime; `default_mode=shadow`;
  LIMITED-AUTO off; R595 pre-activation blocking.
