# M0-T087 producer report — bootstrap-continuity slice (D-024 A2)

Producer: orchestrator. Date: 2026-08-25.
Supervisor-freeze qualifying evidence: **D-024-R099** (Phase A item 7 — prove the bootstrap
continuity path before the longest implementation units; explicitly listed in D-024).

## What was built (smallest safe slice, reuse-first)

**Investigation finding:** the existing `session_continuity.py` / `loop_turnover.py` machinery
(M0-T080 lineage) solves PROVIDER-session resume inside the supervised Codex↔Claude loop — a
different boundary from what D-024 §15-A item 7 requires: the IMPLEMENTATION CAMPAIGN itself
surviving primary-session turnover from durable artifacts without owner re-prompting. What already
served that need (SESSION_HANDOFF prose + ledger + captured directive + the D-025 `/session-handoff`
skill + the SessionStart directive reminder) lacked one machine-validated piece: a durable,
fail-closed, exactly-once-advancing record of the campaign's authority, state, frozen identity,
standing restrictions, and **exact next bounded action**. That is the slice built here.

- `tools/agent_supervisor/campaign_continuity.py` (~260 SLOC, stdlib-only, 3.11-compatible):
  `campaign_continuity/v1` schema; fail-closed `validate`/`load` (missing/malformed/vocabulary
  violations raise — orientation is never silently empty); `atomic_write` (tmp + `os.replace`, LF);
  `advance` with a monotonic `sequence` — a writer must present the sequence it read, so two
  successors racing from one snapshot cannot both win (exact-once, D-024 §3); `staleness` (frozen
  identity vs live HEAD — a mismatch is a reconcile-first warning, never silently trusted, because
  the ledger and git win); `orientation_summary`; read-only status entry point
  `python -m tools.agent_supervisor.campaign_continuity --status` (exit 1 fail-closed when no/invalid
  record). No existing supervisor module was modified — the slice is additive, integration into
  `cli.py status` belongs to Phase D/F under their own review.
- Live record instantiated (orchestrator control-plane act, like `state.json`):
  `project-control/campaigns/D-024-fable-codex-loop.json` — authority = the captured v4 source +
  digest; lineage base `7649acf`; five standing restrictions (PR #241 hold, owner-gated activation,
  Gate 0, freeze citation duty, no worker quotas); `next_action` maintained by the orchestrator at
  every seam.
- `tools/test_agent_supervisor_bootstrap_continuity.py`: **35 deterministic tests** — validation
  rejects every missing field and every vocabulary/shape defect (parametrized), malformed/missing
  files fail closed, atomic LF round-trip, invalid records refuse to persist, exact-once advance
  (stale sequence refused; two-racers-one-wins with the loser's write provably absent), restriction
  preservation, staleness detection, orientation contents, and the status entry point's
  fail-closed/valid/invalid behaviors.

## End-to-end proof: successor orientation from durable artifacts alone

A fresh isolated context (subagent — per the documented startup model it receives the task message,
CLAUDE.md hierarchy, and git snapshot, NOT this conversation) was given a deliberately
campaign-ignorant prompt: only the worktree path and "orient from durable artifacts per the
repository's start-of-session routine; report campaign, exact next action, frozen identity,
restrictions, READY/BLOCKED." Zero campaign identifiers, task IDs, or hints were provided.

Result (full report in the session record; verdict verbatim): it identified campaign
D-024-fable-codex-loop under the v4 authority with the correct source digest; reported the exact
next bounded action **including the in-flight state** ("continue M0-T087 — already claimed — do not
re-claim"), explicitly resolving the committed-handoff prose ("claim M0-T087") against the live
ledger **in the ledger's favor, citing the repository's own precedence rule**; verified frozen
identity `064484b` == campaign record == G0 gate record == live HEAD == origin (three-way match);
enumerated all standing restrictions including ones sourced OUTSIDE the campaign record (expansion
hold, open blockers with none binding, PUBLIC-repo caution); classified the dirty working tree as
"in-flight M0-T087 work, nothing stale or foreign"; and returned **READY TO RESUME** with the
correct first steps (Gate 0 before any write, then this report, then the recorded review chain).

That discrepancy-resolution behavior is the strongest part of the evidence: the successor did not
merely parrot the record — it reconciled prose vs ledger exactly as D-024 §1 requires.

## Campaign-turnover status (honest scope)

- Crossed already: dead capture session → this session (adopted uncommitted work only after an
  independent Gate-0 pass — D-024-R128 — recorded in the D-024 audit_log). That crossing required
  one owner prompt because the v4 correction needed owner input; it predates this slice.
- Proven here: successor orientation from durable artifacts alone, with zero campaign-specific
  prompting (above).
- Still owed later (not claimed): the live cross-terminal turnover of THIS campaign under the
  one-command start, and the §16.9 golden-run crossing — owned by M0-T092/M0-T096 where those
  requirement rows also bind. The campaign record + `/session-handoff` + this slice are the
  mechanism they will exercise.

## Verification runs

- `pytest tools/test_agent_supervisor_bootstrap_continuity.py -q` → **35 passed** (0.34s).
- Combined with probe tests → 51 passed. `ruff check` both files → clean.
- Full supervisor suite (freeze §4 duty) re-run with the new module: exact result recorded in the
  G2 self-check.
- Live: `python -m tools.agent_supervisor.campaign_continuity --status` prints the full orientation
  (campaign, NEXT, restrictions); record validated on write.
- Modularity: single-responsibility module well under thresholds (`code-architecture` rule).

## Limitations (disclosed)

- The record is orientation, not authority — by design; every consumer instruction says ledger+git win.
- `--status` scans `project-control/campaigns/*.json` in the CWD; it is a successor-orientation
  tool, meaningful only at a repository root (Gate 0 guarantees that context).
- Integration into `python -m tools.agent_supervisor status` and the SessionStart hook surface is
  deliberately deferred to Phase D/F tasks (they own `cli.py` / `.claude/hooks` respectively).
