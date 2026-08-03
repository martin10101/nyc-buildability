# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-03**, at the M0-T036 build-dispatch capture (owner ruling 8).

## Where main is

| | |
|---|---|
| `origin/main` at refresh | `e7f5078` (+ the dispatch-capture PR queued on top) |
| accepted tasks | **54** (M0-T027 accepted 2026-08-03; CP-0036) |
| registries | D-004 v22 (733 ids) · D-005 · D-006 (32 ids) · **D-007 v2 (541 ids)** |
| open lanes | **M0-T036 DISPATCHED** (build, Phases 1–5) · M0-T035 `awaiting_gate` (all four gates PASS; acceptance on owner instruction) · M0-T034 `self_check` (lifecycle debt, owner-backlogged) · PR #64 (pre-existing) |

## 1. THE LIVE DISPATCH — M0-T036 Supervisor Bridge build

The owner's 2026-08-03 message (captured verbatim as **D-007 amendment 1, `source-002-amendment.md`,
rows R532–R541**, with rulings 1–2 as **D-004 amendment 21, R732–R733**) DISPATCHED M0-T036:
execute **Phases 1–5** per the captured D-007 directive (531 base rows + the amendment) and the
task packet. Fixed decisions: ADR-005 amendment ADOPTED (doc note in `docs/adr/ADR-005…`, in force
before any pushing mode); audit anchoring **Option A** (controller-pushed anchor branch);
controller location = **dedicated read-only checkout outside every Claude-writable path**; the two
**standing grants are ACTIVE** (task-scoped: `pytest tools/test_agent_supervisor_*.py` in the task
worktree; push to `task/M0-T036-supervisor-bridge` after passing review — never main); the two
outstanding behavioral probes (`--max-turns`, stream-json `canUseTool`) run as the **first Phase 1
acts**, results in the Phase 1 checkpoint, stop only if a result contradicts the CLI-adapter
decision. **Phase 5 ends at the shadow-pilot decision packet and STOPS for the owner's activation
decision. Limited-auto is never enabled by this task.** Every D-007 §18 stop condition is live.

## 2. Standing discipline (carry forward)

- **D-004-R721 (unchanged by the dispatch): EVERY MERGE QUEUES FOR THE OWNER.** A silent
  classifier or allowlist is never authorization (incident R718–R724; merges #143–#145 ratified,
  finding stands). Allowlists were narrowed 2026-08-03 (gh pr view/checks/diff/list/create only;
  `git merge --no-ff task/*` only).
- **R307 DISCHARGED (D-004-R732):** gate-class spawns run **pinned Fable 5** with honest
  disclosure — the Opus 5 exception is closed. Producers per R298 ceiling (recent precedent:
  explicit Opus 5). Writing producers spawn UNNAMED; reviewers may be named.
- **D-006 dispatch standards in force:** delta scope, settled-findings cited, one bounded
  deliverable per spawn, exact-file packets, sweep tiering (progress-auditor, data-not-judgment),
  N=6 measurement (5/6 recorded; per-spawn /usage honestly unobservable).
- **R024 public-repo hygiene:** scan before commit; redact with annotation; describe patterns,
  never quote them. 76 pre-existing username-bearing files untouchable (R560).
- Reviewers may signal idle without delivering — demand the complete return; preserve it verbatim
  THE MOMENT it arrives. Reviewer shell file-writes are guard-blocked (by design); returns come
  through the agent-return channel.
- Gate records stamp at HEAD == reviewed commit; the control-plane material identity is
  lifecycle-neutral (verified repeatedly). Keep the checkout parked on the reviewed branch during
  frozen-SHA reviews, or accept `git show`-based review (G3 OBS-3).
- Owner-plane local state (never touch/clean/reconcile): `bad-amend-backup` branch, the modified
  backend-engineer memory file, untracked agent-memory files, untracked root efficiency draft,
  `.claude/settings.local.json.bak-2026-08-03`.

## 3. Owner backlog (stays backlog — ruling 9)

C1 MATERIAL_FIELDS inversion · OBS-6 preservation-time redaction · D-001 capture-guidance for
`classified_at_identity` · drive M0-T034 to submit/accept · OBS-B evidence-map internal identity
fields · read-only-guard gaps (over-denials OBS-D + python-process write bypass, demonstrated
benignly scratchpad-only) · qa-engineer `--no-regen` (G5 O3) · round-1 producer memory notes
(preserved in the 2026-08-03 session record, R660 pattern) · weak
`test_manifest_is_order_independent…` test · M0-T035 + M0-T034 acceptance runs on owner
instruction.

## 4. NOT AUTHORIZED (unchanged unless a capture says otherwise)

Limited-auto activation (Phase 5 stops for it) · any merge without owner execution or an
R666-form/explicit-grant authorization · effort keys anywhere, ever · settings/hooks/rules changes
(the 2026-08-03 one-time grant is EXPIRED) · M0-T029/M0-T032/M0-T025 · product/legal-rule changes ·
`teammateDefaultModel` · deployment/hold releases · G6, Graphify, expansion, survey work.
