# M0-T027 — Producer report

**Task:** D-004 pilot-governance: agent-teams runtime pilots (Steps 1, 2, 4 evidence)
**Producer:** orchestrator (main session, ADR-005)
**Directive:** D-004 — Agent-teams runtime adoption, staged with pilots (`directive_refs: D-004:ALL`)
**Status of this report:** in progress — Step 1 only.

---

## 1. Authorization basis

D-004 `source-004-amendment.md` (owner amendment 3, 2026-07-24) is the explicit **conditional GO for
Step 1** with flag-3 **option (a)**. The condition was that the machine-verification and
re-orientation items be fully green. Both were checked before any Step-1 action; results are recorded
in §2 and in the D-004 manifest notes/audit log.

Steps 2, 3, 4, and 5 remain **un-authorized**. This task's Step-2 and Step-4 report outputs
(`AGENT-TEAMS-PILOT-2-PROBE.md`, `AGENT-TEAMS-PILOT-3.md`) are reserved in `allowed_paths` but are
**not** produced under the Step-1 GO.

## 2. Pre-conditions verified before Step 1

| Item | Result |
|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` active in session | `1` |
| CLI version >= 2.1.178 | 2.1.219 |
| Project path space-free (hook word-splitting fix) | confirmed, no space in the resolved path |
| Machine-global hooks block removed owner-side | confirmed: no `hooks` key in either global settings file |
| `.claude/settings.local.json` git-ignored | ignored via the owner's global ignore file |
| Local `main` == `origin/main` == frozen baseline | `421265709f81a40e20f3d890609907ed932967dd` |
| D-004 capture intact (7 artifacts + index entry) | confirmed before commit |
| Registry validator | `OK: 4 directive(s), 4 active` (exit 0) |

**Open note carried on D-004-R112:** `UserPromptSubmit` (and `SessionStart`) run clean. `PostToolUse`
and `Stop` are **not registered in any settings file** after the owner-side removal of the
machine-global hooks block, so they cannot be shown running and equally cannot error. Zero hooks
errored, so the D-004-R113 STOP condition did not trigger. Raised for owner confirmation.

## 3. Scope discipline

- `allowed_paths` are exactly the three named pilot report files plus this producer report, plus this
  task's own packet as the orchestrator lifecycle path (see `allowed_paths_note` in the packet).
- The D-004 directive-registry files committed alongside this packet are the orchestrator's **D-001
  capture authority**, not M0-T027 producer output, and are listed in `forbidden_paths`.
- **M0-T025 is untouched** (D-004-R022/R053).
- **No effort setting is applied anywhere** (D-004-R096/R124 standing hold).
- No product code and no ledger *product* state changed; this task is mechanism proof only.

## 4. Step 1 evidence — **the pilot FAILED its own negative test**

Full Step-1 evidence is recorded in
[`project-control/reports/AGENT-TEAMS-PILOT-1.md`](AGENT-TEAMS-PILOT-1.md), covering the five items
D-004 Step 1 requires: per-teammate `rev-parse` of the reviewed SHA; teammate names + agent types from
team configuration only; the sentinel negative test with verbatim guard denials **and** the
orchestrator's own independent `test -e` verification; confirmation each reviewer invoked
`/run-quality-gate`; and each reviewer's verdict plus full report content preserved verbatim.

**Outcome.** Four of the five items were satisfied. Item 3 — the sentinel negative test — **failed**:
a `code-reviewer`-role teammate's `echo x > ./PILOT_SENTINEL.tmp` was **not** denied and **did** create
the file. The orchestrator independently verified this with its own `test -e` (exit 0 = EXISTS, 2
bytes, untracked) rather than accepting the reviewer's word. The companion Write-tool attempt was
blocked only by tool-unavailability, not by the guard's own denial. The hook's logic is correct in
isolation and is correctly wired; the gap is in the live PreToolUse event path for **teammates**.
Recorded as blocker **B-015**; root-causing belongs to M0-T028 (D-004 Step 3), whose scope covers
producer confinement. The guard was **not** modified under this task.

Reviewer verdicts: `pilot-code-reviewer` FAIL · `pilot-control-plane` FAIL · `pilot-directive-compliance`
PASS. Both FAIL verdicts trace to the single sentinel defect; no reviewer found a defect in the
reviewed *content*.

**Scope note (flagged for the owner, not resolved unilaterally).** `project-control/blockers/` is
listed in this task's `forbidden_paths`, which was written to keep *pilot evidence* contained. Opening
B-015 is an orchestrator control action mandated by D-004's standing constraint that anything
ambiguous or blocked "becomes a blocker, not an action" — the same authority class as the D-004
registry writes, which are likewise excluded from `allowed_paths`. It is committed as such and
surfaced here rather than quietly reclassified.

## 5. Evidence hygiene

Everything written to the repository under this task is redacted per the D-004 standing constraint:
teammate **names and agent types only**, taken from team configuration. Session ids, pane ids,
absolute user paths, and machine-specific data are excluded.
