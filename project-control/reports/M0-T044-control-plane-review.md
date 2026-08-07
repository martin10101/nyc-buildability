# Control-Plane Review — M0-T044 "Automatic safe GitHub flow (0A.8 item 8; AD-077; Section 19.4 proofs)"

**Reviewer:** control-plane-verifier (independent, read-only) — §5.2 control-plane leg of the
supervisor-code required review set (control-plane + security + crash/replay).
**Task:** M0-T044 | **Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch`
**Branch:** `task/M0-T044-github-flow` @ HEAD `8fc05ae` | **Base:** `origin/main` `341fa4d`
**Producer content commit:** `af46b3e` (material byte-identical to HEAD; verified below)
**Verdict:** PASS

---

## Item 1 — Task lifecycle integrity — CONFIRMED

Full committed lifecycle, each transition legal per `docs/GATES_AND_CHECKPOINTS.md`
(`backlog → claimed → in_progress → self_check → awaiting_gate`), `updated_at` strictly
monotonic, no skipped state:

| Commit | Status | updated_at (UTC) |
|---|---|---|
| `341fa4d` (base) | backlog | 2026-08-07T09:50:11 |
| `a3feb3e` | claimed (+G0 PASS) | 2026-08-07T11:31:17.412642 |
| `b5acbe4` | in_progress | 2026-08-07T11:32:08.299205 |
| `0b40889` | self_check | 2026-08-07T11:51:33.624384 |
| `7437747` | awaiting_gate (+G2) | 2026-08-07T11:51:43.600064 |
| `15407d5` | awaiting_gate (+G3) | 2026-08-07T12:03:16.158345 |
| `8fc05ae` | awaiting_gate (+G4) | 2026-08-07T12:07:45.843875 |

The packet exists at base `341fa4d` already at `backlog` (updated 09:50:11) carrying the full
7-requirement `directive_refs`; it was claimed on this branch at `a3feb3e`. (This explains the
`created_at` value `2026-08-07T01:33:11.425300+00:00`, which predates the branch commits — the
packet was authored at backlog on main, then claimed. Benign; monotonicity of lifecycle
transitions holds — `created_at` is the earliest timestamp, not out of order.)

**Directive refs carried on claim — CONFIRMED.** `tasks/M0-T044.json` `directive_refs` = D-010
{R006, R007, R010, R077, R093, R116, R117} at base and at HEAD; claim commit `a3feb3e` message
cites the same set. All 7 IDs resolve in
`project-control/directives/D-010-autonomous-engineering-restructure/manifest.json`.

## Item 2 — Gate records — CONFIRMED

| Gate | reviewer/role | result | report | report-before-gate? | reviewed_sha | content_manifest_sha256 |
|---|---|---|---|---|---|---|
| G0 | orchestrator/administrative | PASS | `M0-T044-g0-readiness.md` | same commit `a3feb3e` (report present in tree at gate) | `341fa4d` (base) | `cdaeeb7a…0cb2d27` (pre-content, expected) |
| G2 | orchestrator/self_check | PASS | `M0-T044-producer-report.md` (committed earlier in `af46b3e`) | YES | `0b40889` | `16149fc3…ac4a59` |
| G3 | code-reviewer/independent_review | PASS | `M0-T044-g3-code-review.md` (`4d76f3f`) BEFORE gate record (`15407d5`) | YES | `4d76f3f` | `16149fc3…ac4a59` |
| G4 | qa-engineer/independent_review | PASS | `M0-T044-g4-qa-review.md` (`0536467`) BEFORE gate record (`8fc05ae`) | YES | `16149fc3…ac4a59` | `16149fc3…ac4a59` |

`content_manifest_sha256` = `16149fc32263f4ed9509e3c15b71f328cc4701b88252c7bf22bbcaff13ac4a59`
is identical across G2/G3/G4 (material identity stable since content commit). Independently
confirmed: `git diff af46b3e HEAD -- tools/` is EMPTY — the three implementation files
(`github_flow.py`, `external_effects.py`, `test_agent_supervisor_github_flow.py`) are byte-identical
from `af46b3e` through HEAD; all post-content commits touch `project-control/**` only. All
`reviewed_sha` values (`341fa4d`, `0b40889`, `4d76f3f`, `0536467`) are real ancestor commits of
HEAD on this branch. `tools/project_control.py` (lines 1119-1130) mechanically stamps
`content_manifest_sha256`/`reviewed_sha` from the git-canonical identity, so the values are
tool-produced, not hand-authored.

## Item 3 — Reviewer independence — CONFIRMED

- Producer: `backend-engineer` (unnamed spawn; `tasks/M0-T044.json` producer_agent +
  progress_log[0] "Producer dispatched (unnamed backend-engineer)"). G3 = `code-reviewer` ≠ producer.
  G4 = `qa-engineer` ≠ producer ≠ G3. Verifier = `control-plane-verifier` ≠ all.
- `tools/project_control.py` (lines 1093-1106) rejects the reserved orchestrator identity for
  independent gates and rejects `reviewer == producer` / reviewer not in `reviewer_agents`; that G3
  and G4 recorded at all is mechanical proof the reviewers were independent and listed.
- No reviewer wrote implementation: all code (`github_flow.py` NEW, `external_effects.py` MODIFIED,
  test file NEW) is in the producer commit `af46b3e`; reviewer commits (`4d76f3f`, `15407d5`,
  `0536467`, `8fc05ae`) touch ONLY reports/gates/state/task. All commits are git-authored by the
  orchestrator identity (`martin10101 <myhappybook212@gmail.com>`), the expected ADR-005 pattern
  (orchestrator commits; reviewer identity lives in the gate record + report attribution).

## Item 4 — Crash/replay control-plane concern (§5.2 leg) — CONFIRMED

`external_effects.py` change (`af46b3e`) is strictly additive and default-behavior-preserving:
an optional `extra_specs` kwarg (defaults `None → {}`), a new instance-scoped `_spec_for()` that
checks `extra_specs` then falls back to the registry `spec_for()`, and two call sites switched
`spec_for(x) → self._spec_for(x)` (in `begin()` and `assert_not_destructive()`). With the live-path
default `extra_specs={}`, `_spec_for(x) ≡ spec_for(x)`. **No persisted-journal schema change** — the
change affects only in-memory spec resolution, so existing journals holding only `MODELED_EFFECTS`
rows load and reconcile identically.

Tests re-run independently by this reviewer (real counts):
- `test_agent_supervisor_crash.py` → **32 passed**
- crash + replay + recovery → **125 passed**
- `test_agent_supervisor_github_flow.py` → **57 passed**
- `test_agent_supervisor_invariants.py -k invariant_9` → **2 passed** (shadow posture: no
  `MODELED_EFFECTS` entry performs a gated/merge/deploy action)
- github_flow shadow/unmodeled tests → **3 passed**
- Full supervisor suite `test_agent_supervisor_*.py` → **1271 passed, 2 skipped** (matches
  producer, G3, and G4 exactly; the 2 skips are pre-existing, not in the new file).

Shadow merge cannot enter a live journal: a plain live `ExternalEffectJournal` (default
`extra_specs={}`) refuses `begin(effect_type="github_pr_merge")` as `unmodeled_effect`
(`test_a_plain_journal_cannot_journal_a_merge`, passed). `github_pr_merge` is absent from
`MODELED_EFFECTS` (invariant 9 holds). Repo-wide `git grep "github_flow"` returns NO importer
outside the module and its test file — no live path (`loop`, controller, bridge) can reach the
capability.

## Item 5 — Ledger consistency — CONFIRMED

- `state.json` `accepted_tasks` length = **62**; M0-T044 is NOT in `accepted_tasks` (it is in
  `active_tasks`). Accepted count unchanged; no acceptance/G5 record for M0-T044 exists.
- No blocker/hold records touched by this branch (branch changeset has no `blockers/` edits;
  `blocked_tasks` unchanged at M0-T007/M0-T008; `failed_gates` empty).
- No `project-control/directives/` edits on the branch (forbidden path honored). Full branch
  changeset vs `341fa4d` touches only: `gates/M0-T044-{G0,G2,G3,G4}.json`, `reports/M0-T044-*`,
  `reports/M0-T036-ACTIVATION-CHECKLIST.md`, `state.json`, `tasks/M0-T044.json`, and the three
  allowed `tools/` files. No `.github/`, `.claude/`, `apps/`, `services/`, or manifest/lockfile edits.
- The `M0-T036-ACTIVATION-CHECKLIST.md` addition (+22 lines, `4d76f3f`) is an orchestrator report
  edit registering MINOR-1/MINOR-2 as pre-activation MUST-RESOLVE items; purely additive and
  explicitly reinforces the R595-gated shadow posture — allowed.

## Item 6 — SHADOW-ONLY / R595 posture — CONFIRMED

No lifecycle record, report, or code on this branch claims activation or lifts R595. Every
R595/activation reference asserts the opposite: producer report ("Nothing is wired into a live
path; the R595 activation gate is not lifted"; line 151 defers live wiring to R595 out of scope),
G3 ("SHADOW-ONLY; R595 activation gate not lifted; no live path imports `github_flow`"), G4
(OBS-1/OBS-2 "shadow-only, R595 not lifted"), and task risk line ("no live merge occurs before
activation (R104)"). No live importer exists (Item 4). Task is not accepted.

---

## Observations (non-blocking; not control-plane defects)

- **OBS-A (explained, benign):** `created_at` (2026-08-07T01:33:11 UTC) predates the branch
  commits because the packet was authored at backlog on main (present at base `341fa4d`,
  status `backlog`) and claimed later. No transition is out of order.
- **OBS-B (forward, already pinned):** MINOR-1 (Tier B change-class detection covers 3 of 11 §5.2
  classes → fail-open for the 8 semantic classes) and MINOR-2 (empty-`authorized_branch`
  fall-through) are disclosed by both G3 and G4 and registered on
  `M0-T036-ACTIVATION-CHECKLIST.md` as pre-activation MUST-RESOLVE items. Non-blocking for this
  shadow-only, R595-gated scope; flagged for whoever eventually wires the flow live.

## Control-plane verdict: PASS

Lifecycle legal and monotonic; every gate has a real reviewer report committed at/before its
record; material identity stable and tool-stamped; producer ≠ every reviewer ≠ verifier; no
reviewer authored implementation; crash/replay schema is backward-compatible and the shadow merge
is unreachable from any live journal; ledger totals intact (accepted 62, M0-T044 not accepted);
forbidden paths honored; shadow-only/R595 posture is genuine and load-bearing.
