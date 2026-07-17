<!-- Verbatim reviewer return (agent-return channel; agentId a67800ce59c2e3304, code-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdict: G3 PASS (zero blocking defects; LOW observations OBS-A/B/C). -->

# G3 Gate Report — M0-T016 Project-control CLI hardening follow-up

**Gate:** G3 (independent human-style walkthrough)
**Reviewer:** code-reviewer (independent; did not produce this work)
**Task packet:** `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T016.json`
**Review target:** worktree `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T016\`, branch `task/M0-T016-control-hardening-followup`, HEAD `debe698`, merge-base with main `7087ee1`
**Date:** 2026-07-17
**Method:** read packet acceptance scenarios first; audited the merge-base diff; verified enforcement placement against every CLI code path; ran the full test suite; drove the CLI against disposable temp-dir ledgers I created (no real-ledger writes, no git/gh/project_control.py writes).

## Scope containment

`git diff 7087ee1..HEAD --stat` (merge-base diff) touches exactly the three allowed paths — 392 insertions, 0 deletions elsewhere:
- `tools/project_control.py` (+82)
- `tools/test_project_control.py` (+167)
- `project-control/reports/M0-T016-producer-report.md` (+143)

Note for the record: `git diff main --stat` shows phantom ledger deletions (`M0-T016-G0.json`, `M2-T003-G0.json`, state.json, etc.) because **main advanced past the branch point** with orchestrator ledger commits after the branch was cut. Those are main-side additions appearing reversed, not branch changes. Scope audits on this branch must diff against merge-base `7087ee1`.

**CRITICAL check:** `git diff main -- project-control/tasks/M0-T007.json project-control/tasks/M0-T008.json` is **empty** — both byte-unchanged. Live ledger confirms both are `blocked` with `producer_agent: null` and `reviewer_agents: []` — exactly the packets the new precondition binds.

## Test suite

```
$ python tools/test_project_control.py   (in the worktree)
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (134 real ledger files parse; legacy records accepted; validation is write-time only)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: all 10 project-control test groups passed
EXIT=0
```

10/10 groups green, matching the producer report and CI (PR #15, 12/12 including the `control-plane` job — orchestrator-provided evidence; not independently re-run per read-only protocol).

## Findings table — S1–S4

| Scenario | Cases walked | Result | Evidence |
|---|---|---|---|
| **S1 — orchestrator roster prohibition (D1)** | Normal: `--reviewers orchestrator`, `rev-y,orchestrator`, `orchestrator,rev-z` all rejected at `new_task` (`project_control.py:299`), no task file created. Independent-gate branch (`gate()`, line 468) rejects `--reviewer orchestrator` for each of G1/G3/G4/G5/G6 **even with a legacy packet that rosters orchestrator** — no gate record written. Preserved positives: orchestrator G2 → `role: self_check`, G0/G7 → `role: administrative` still succeed (the self_check/administrative branches evaluate first and *require* the orchestrator literal — untouched). Rostered real reviewer still passes G3. | **PASS** | S8 test group (1), (1b), (1c) — asserts error substring `reserved`, file non-creation, role fields; my probe P4 confirms combined-violation rejection leaves no file |
| **S2 — `--gates` enum validation (D2)** | Rejection before file write (`project_control.py:290-293`): `G9`, `bogus`, `G0,G9`, `G3,bogus,G4`, `g3` (lowercase), `G8`, `G10` all rejected; error names offending entry(ies) and lists the full G0–G7 enum; task file not created. Full valid combo `G0..G7` accepted and stored unchanged. My probes: empty entry (`G0,,G3`) and whitespace entry (`G0, G3`) also rejected fail-closed (exit 2, no file). Config-default gates flow through the same check (validation covers both branches). `--gates ""` falls back to config defaults (pre-existing behavior). | **PASS** | S8 test group (2); probes P1/P2/P3/P9 (exact exit code 2) |
| **S3 — blocked-roster precondition (OBS-3)** | `invalid_unblock_roster()` (lines 335-363) called only on `blocked → non-canceled` transitions in `progress()` (line 391). Rejections (empty roster, producer==orchestrator, reviewer==producer, reviewer==only-orchestrator) all leave status `blocked` with bounded error directing packet amendment. `blocked → canceled` always allowed. Post-amendment unblock works (`blocked → in_progress` in tests; my probes confirm `→ ready`, `→ backlog`, `→ awaiting_gate` too). Message-only progress on a blocked task never gated. **Placement verified correct:** `progress` is genuinely the *sole* exit from blocked — `claim` requires {ready, rework} (probe P7: rejected from blocked), `submit` requires {claimed, in_progress, self_check, rework} (P7: rejected), `gate` status effects never leave blocked (FAIL only acts from awaiting_gate; PASS G0 only from backlog/rework — probe P8: G0 PASS on a blocked task records evidence but status stays `blocked`), `accept` requires awaiting_gate. The chokepoint fully closes the path. | **PASS** | S8 test group (3); probes P5/P6/P7/P8; code inspection of all five status-mutating functions |
| **S4 — no retro-rejection / suite green** | S7 (unchanged from M0-T014) copies the entire real ledger (134 files) into a temp project: all parse, `status` runs, ≥21 accepted tasks visible, a message-only progress write on a real copied task succeeds, and a legacy-shaped task (no role fields, empty `reviewer_agents`, backslash report path, G3 by unrostered legacy reviewer) still satisfies `accept()`. S8 adds the explicit message-only-progress-on-blocked-with-empty-roster assertion. All new validation is write-time only; `accept()` tolerance untouched. | **PASS** | S7 + S8 output above; `accept()` lines 549-571 unchanged in diff |

## Code-quality assessment

- **Placement:** correct. The roster check lives at the single chokepoint (`progress()`); the D1 rail is duplicated at both write points (authoring and gating) so a hand-edited legacy roster cannot smuggle the orchestrator through gate time. The self_check/administrative branches are structurally unreachable by the new rejection (they match first and require the literal).
- **Test honesty:** strong. Tests assert error-text substrings (`reserved`, `amend`, the offending gate entry, presence of the enum bounds `G0`/`G7`), file non-creation on rejection, status invariants after rejection, and role fields on preserved positives — not just non-zero exit. Exit codes asserted as `!= 0` rather than `== 2` matches the suite's pre-existing convention; actual is 2 (verified).
- **Documentation:** module docstring TASK LIFECYCLE section updated with the blocked-roster precondition (packet required "document AND enforce" — satisfied); `RESERVED_ORCHESTRATOR` carries an explanatory constant comment; test-file header documents S8.
- **Producer report:** disclosures are honest — the "valid roster" definition is stated as an assumption mirroring the existing independent-gate rule, the literal-string limitation is disclosed (consistent with G4 OBS-1, not re-litigated here), and the "progress is the sole exit" claim is stated with its verification reasoning, which I independently confirmed.
- **No smuggled changes:** merge-base diff contains nothing outside the three items; `accept()`, `submit()`, `claim()`, containment, and atomic-write code untouched.

## Defects

None blocking. Observations (all LOW, non-blocking, no rework required):

| ID | Severity | Blocking | Description |
|---|---|---|---|
| OBS-A | LOW | No | `--gates` split does not filter empty entries (`a.gates.split(",")`) while `--reviewers` does (`if x`): a trailing comma (`--gates "G0,G3,"`) is rejected with an awkward-but-bounded message naming an empty offender (`Invalid --gates entry(ies): . Allowed gates are …`). Direction is fail-closed, so harmless; align the two splits in a future maintenance pass. |
| OBS-B | LOW | No | The unblock precondition requires a non-empty `producer_agent` even for a never-claimed task blocked from `backlog`; unparking such a task to backlog forces pre-assigning a producer that `claim()` will later overwrite. This matches the packet objective verbatim ("amended with valid producer and independent-reviewer rosters") and is conservative — friction only, and it is precisely the intended binding for M0-T007/T008. |
| OBS-C | LOW | No | Module docstring BACKWARD COMPATIBILITY section still says "21 accepted tasks" (written at M0-T014); the ledger now has 25+. Pre-existing text, not touched by this diff; cosmetic staleness for a future doc pass. |

## Verdict rationale

The implementation does exactly what the packet says: all three enforcement items are present, placed at the correct chokepoints, bounded in their error messages, write-time-only, and covered by honest negative *and* preserved-positive tests. M0-T007/T008 are byte-untouched, the real ledger is never retro-rejected, the full suite is green in the worktree, and the merge-base diff contains no collateral changes.

G3: PASS
