# D-024 persistent-local-loop proof plan (Amendment 51, R753 statement — recorded BEFORE proof work)

Recorded 2026-09-04 (UTC) at ctl24 HEAD d5e1b599 by the orchestrator, from the read-only
controller-capability map (verified against both the candidate tip and the installed copy).

## 1. R750 reconciliation result (read-only)

Every expected anchor matches the live state: M0-T107 accepted as the 156th task; acceptance
record `9dcbdd09`; DCV reviewed commit `7d282011` (the anchor's "frozen identity" label names
this reviewed commit; the frozen CONTENT identity is `1bbedd34…` — both live values match);
handoff seq 80 `b8856e49`; worker revisions `4047c79c`; bounded correction `777ef5e4`; ctl24 and
wt-m0t107 clean; next campaign unit M0-T109 (claimed, wt-m0t109 @ `1c069571`, clean, zero drift
on its own output paths vs the tip); PR #241 untouched (no upstream anywhere, nothing pushed);
R595/Option-A + R603–R605 owner-gated. **Discrepancies: none.** Two non-blocking notes:
(a) wt-m0t109's base commit predates the recent candidate advance (immaterial: its three output
paths are byte-identical between `1c069571` and the tip; the worktree will be fast-forwarded at
dispatch); (b) the supervisor journal is parked at `WAIT_FOR_OWNER` (`tier_ask_blocking`) — the
journey-m0t107-01 REVISE forward hold, superseded by the completed Amendment-50 out-of-band
adjudication and acceptance; it must be settled via the canonical owner-answer transition before
the next dispatch (recorded as step F below; the pending M0-T107 prompt is declined-as-superseded,
never forwarded).

## 2. R753 statement: can M0-T109 alone prove all seven facts? **NO.**

Mapped controller reality (file:line evidence in the capability map, summarized):

- The MRL one-shot path (all live proof so far) is structurally single-task/single-cycle
  (`mrl_launch_path.py:91-97`, R581). Multi-cycle and multi-task run ONLY on the legacy
  `ClaudeRunner`/`CodexReviewer` path (`cli.py:2746-2752`) — never yet live-proven with the
  real CLI (the golden run proved it against the deterministic fake CLI; commissioning proved
  the real CLI on the MRL path only).
- REVISE auto-relaunch (facts 1–2) exists ONLY in `--mode limited-auto
  --owner-enable-bounded-auto` (`loop.py:2289-2301`); in supervised mode every REVISE is an
  owner-held process exit (`loop.py:2304-2309`).
- Task advancement (facts 3–4) requires `--packet-queue` + `--max-tasks ≥ 2` in limited-auto
  (`next_task.py:793-803`); selection walks the owner-supplied ordered queue file with durable
  journal queued-digest snapshots and exactly-once advancement records. **Architecture fact,
  stated honestly:** the controller does NOT enumerate the project-control ledger; "durable
  repository state" is satisfied by the committed task PACKETS the queue entries bind plus the
  durable journal records — the ORDER is owner-supplied. The controller never accepts ledger
  tasks (`loop.py:2174-2179`); gates and acceptance remain with the orchestrator.
- Controlled interruption/resume (facts 5–6): durable manual-pause flag honored at the
  between-cycle seam (`loop.py:2874-2877`), graceful-stop intent lands the in-flight unit and
  survives restart (`state_machine.py:290-306`); a stable `--run-id` resumes budgets and skips
  already-advanced tasks exactly-once.
- Foreground view (fact 7): the controller prints one exit report only (`start_gate.py:466-511`)
  — no task id, stage, model, or pending-approval digest. The accurate view is assembled by the
  launcher wrapper from `--json` output, the durable run artifacts, and the real-time
  `audit.jsonl` tail (the same honest surface R730 recorded). No controller change is made for
  this; the wrapper-level view is what is proven.
- One further gate: the legacy runner's checkpoint validation historically failed when a worker
  omitted the four git-state fields (journey-5 `invalid_checkpoint`). The contracted fix —
  controller-authoritative checkpoint envelope, **M0-T133** — is REAL, 85% complete, and sits in
  rework on exactly one blocking finding (modularity ceiling: `claude_runner.py` 1432 > 1410;
  G3/G4 otherwise strong with RED-on-mutant proofs). Running the legacy path live without it
  would gamble on worker-emitted factual fields, violating convergence rule 12.

## 3. Minimum sequence of existing real tasks (no new stabilization campaign)

| Step | Task | Role | Provider? |
|---|---|---|---|
| 1 | **M0-T144** (policy) | Owner-ordered deficit-convergence policy install (separate Part-B duty; not a proof vehicle) | NO |
| 2 | **M0-T133** (existing, rework) | Complete the one blocking rework item (extract checkpoint helpers out of claude_runner.py per the G3-preferred option, correct the misreporting, re-gate, accept); then the R247 recertification at the new frozen candidate and a transactional byte-verified controller install (an authorized task specifically requiring the controller change — R756 carve-out) | NO (deterministic tests only) |
| 3 | **M0-T109 + M0-T025** (existing) | ONE live limited-auto queue run on the fixed legacy path: `--packet-queue [M0-T109, M0-T025] --max-tasks 2 --max-cycles 3` per task, unlimited run wall-clock (omit `--run-wall-clock-seconds`), stable run-id, launcher-wrapper view + audit tail | YES (the bounded proof run, R755-authorized) |

Fact coverage: facts 1–2 from any natural Codex REVISE cycle across the two units (two real
chances; never forced); facts 3–4 at the M0-T133→… no — at the **M0-T109 → M0-T025 advancement**
(exactly-once record + queue selection + fresh dispatch); facts 5–6 by a deliberate manual pause
at a between-cycle seam plus resume (and run-id budget continuity); fact 7 by the wrapper view
capturing `--json`, the run artifacts, and the live audit tail. M0-T109 is then carried through
its packet gates (G0/G2/G3/G4/G5) + DCV + acceptance by the orchestrator; M0-T025 continues
under standard mechanics from whatever checkpoint its unit reaches (it is real contracted work
either way — nothing is manufactured for proof).

If the legacy path exposes a structural boundary incompatibility live, `/deficit-convergence`
governs: preserve, reproduce, trace, ONE bounded causal-cluster repair, one affected wave —
never serial live-launch discovery (R757). If the proofs do not converge within this sequence,
the terminal outcome is BLOCKED_FOR_PERSISTENT_ACTIVATION with one consolidated blocker list
and an architecture-level viability decision (R760).

## 4. Boundaries restated (R756)

Worker exactly `claude-fable-5`; Codex `gpt-5.6-sol`; restricted tool surface, fail-closed,
bounded subagents, cleanup, identity checks, breakers all kept; one writer per overlapping
state (M0-T133 rework produced by the orchestrator in ctl24 BEFORE any supervised dispatch;
queue tasks isolated in wt-m0t109 / wt-m0t025); no guard weakened; controller changed only via
accepted M0-T133 + certified install; no fixed overall wall-clock on the loop; no push/PR/
merge/deploy/credentials/PR #241; persistent-loop START, R595/Option-A, R603–R605 stay with
the owner.
