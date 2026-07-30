# M0-T027 — Producer report

**Task:** D-004 pilot-governance: agent-teams runtime pilots (Steps 1, 2, 4 evidence)
**Producer:** orchestrator (main session, ADR-005)
**Directive:** D-004 — Agent-teams runtime adoption, staged with pilots (`directive_refs: D-004:ALL`)
**Status of this report:** Step 1 (§§1–5, recorded 2026-07-24, byte-preserved) plus the CLOSEOUT
addendum (§§6–12, recorded 2026-07-30 under D-004 amendment 8). Sections 1–5 are historical evidence
and are NOT rewritten, softened, or removed (D-004-R132).

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

---

# CLOSEOUT ADDENDUM (2026-07-30)

Appended under the owner's GO for the **M0-T027 closeout only**, captured append-only as D-004
amendment 8 (`source-009-amendment.md`, rows D-004-R307–R326). Sections 1–5 above are unchanged.

**Model disclosure (D-004-R310 — actual models, never misreported).** This closeout runs under the
owner's temporary Fable-5-unavailability exception (D-004-R307): the lead/orchestrator is **Opus 5**
and every independent reviewer/verifier for this closeout is spawned with an **explicit Opus 5**
model. No claim of Fable 5 is made for any closeout review. Historical model facts (including the
Step-1 off-policy Sonnet spawns) are restated unchanged in §10.

## 6. Live reconciliation before any write (D-004-R316)

`git fetch --all --prune`; `origin/main` = local `main` = HEAD =
**`87e0ad6d87fa3e45cf647ebe45bf7db4029e7b75`**; working tree clean apart from expected machine-local
state; PR #128 **MERGED** at that SHA; main CI green at that head (CI, secret-scan, context-budget
all success); ledger **52 accepted**, checkpoint **CP-0035**, M2-T018 and M4-T008 **accepted**,
M0-T027 **blocked at 60%**. Every element of the owner's stated expected state was verified rather
than assumed, and matched exactly.

## 7. Evidence reconciliation — the three pilot reports (D-004-R317)

All three outputs named in the packet exist as merged, committed artifacts:

| Output | Commit | Lines | Content |
|---|---|---|---|
| `AGENT-TEAMS-PILOT-1.md` | `0361491` | 547 | Step 1 read-only reviewer pilot (frozen SHA `da0d42b6e9334e823a95aa5cd120f480dbc501c8`) |
| `AGENT-TEAMS-PILOT-2-PROBE.md` | `cc3fcb8` | 287 | Step 2 no-write worktree capability probe (frozen base `b43b4988…`) |
| `AGENT-TEAMS-PILOT-3.md` | `6f9c4b6` | 128 | Step 4 two-producer pilot (frozen base `84c1bf2…`; merged head `3122648`) |

**Step 1.** Three reviewer teammates from named agent definitions; each returned its OWN
`git rev-parse HEAD` equal to the frozen SHA; each invoked `/run-quality-gate`; verdicts
`pilot-code-reviewer` **FAIL** · `pilot-control-plane` **FAIL** · `pilot-directive-compliance`
**PASS**, with full report content verbatim. Both FAILs trace to the single sentinel escape — the
pilot doing its job — which became **B-015**.

**Step 2.** Verdict: the probe **FAILS the "REMAIN" criterion** — teammates can enter a pre-created
worktree and see it correctly, but the working directory resets to the primary checkout before every
Bash call, so residency does not exist. Every probe spawn passed an explicit model value (R160/R161).
A valid recorded mechanism finding; the owner has since resolved the resulting design question
(D-004-R313, §9).

**Step 4.** Two-producer pilot: M2-T018 and M4-T008 produced by unnamed roster producers at explicit
Opus 5 in harness-isolated worktrees at one frozen base, with mandatory pre-write attestation (one
spawn STOPPED on mismatch with **zero writes**), orchestrator exact-diff containment review and
tree-identical ports, four independent Fable 5 gate reviews all **PASS**, 10/10 independent directive
verification, sequential protected-main merges, both tasks **accepted** (51, 52).

## 8. B-015 and step-evidence completeness (D-004-R318)

`project-control/blockers/B-015-teammate-readonly-guard-bypass.json`: status **`resolved`**, audit log
**2 entries** — the original OPENED record (byte-preserved) and the RESOLVED record citing the merged
fix (PR #121, merge `9db4ab3`) and the passing fresh-session sentinel at `88045b0`. Resolution
evidence: `M0-T028-PHASE8-fresh-session-report.md`, accepted with M0-T028 (task 50).

Step-evidence completeness: Step 1 complete (with its FAIL preserved); Step 2 complete (probe verdict
recorded); Step 4 complete (both pilot tasks accepted). Steps 3 and 5 are not M0-T027 evidence —
Step 3 was executed and accepted as M0-T028; Step 5 remains un-authorized.

## 9. Acceptance-scenario self-assessment (producer view — reviewers rule)

Two scenarios cannot be claimed clean on their literal wording. Both are disclosed in full rather
than narrated as passes; the independent reviewers decide.

| AS | Producer assessment | Evidence / disclosure |
|---|---|---|
| AS-1 | **PASS on substance; numeric drift disclosed** | `validate_directive_compliance.py --check` exits **0**; D-004 `active`; both digests recompute exactly. The literal "128 locked requirement ids" is now **326** — the baseline legitimately grew through eight owner amendments, each append-only with prior rows proven byte-identical. The AS text captured a snapshot of the capture-time baseline, not an invariant. |
| AS-2 | PASS | `project_control.py status` shows M0-T027 present, `directive_regime_version` 1.0, citing D-004; resolver coverage OK; derived applicable set **128 rows**, zero unresolved. |
| AS-3 | PASS (historical, at capture) | The D-004 capture and the M0-T027 packet landed together in ONE PR (#106) on a non-main branch via the protected-main workflow; `git log` shows no direct push to main. Every later amendment and this closeout used the same workflow. |
| AS-4 | PASS | PILOT-1 §1: each teammate's own verbatim `git rev-parse HEAD` equals `da0d42b6…` (3/3). |
| AS-5 | PASS | Names/agent types from team configuration only; session ids, pane ids, absolute paths redacted (PILOT-1 §§2, 4). |
| AS-6 | **NOT satisfied inside Step 1 — satisfied across the owner-sequenced arc; REVIEWERS MUST RULE** | In Step 1 the Write attempt was blocked by **tool-unavailability** (not a guard denial), the Bash redirection was **NOT denied**, and the orchestrator's independent `test -e` recorded the file **EXISTED** — the opposite of AS-6's end state, byte-preserved and not rewritten (D-004-R132). The owner then ratified that outcome (source-005: Step-1 evidence accepted AS-IS; B-015 ratified; fix + on-policy rerun assigned to M0-T028), and the rerun produced exactly the AS-6 shape: Write attempt honestly attributed to tool-unavailability, Bash redirection **denied by `readonly_agent_guard.py` itself** with verbatim denial text, orchestrator's independent `test -e` → **exit 1 / ABSENT** (`M0-T028-PHASE8-fresh-session-report.md` §4, accepted). Producer position: AS-6's purpose — prove confinement with independent verification and no reviewer self-assertion — is satisfied across the arc the owner explicitly sequenced, but its literal single-run form was NOT met inside Step 1. This is the one genuinely arguable item in the closeout. |
| AS-7 | PASS | PILOT-1 §4: each teammate invoked `/run-quality-gate`, frozen 40-char SHA stated in the spawn prompt, skill explicitly instructed. |
| AS-8 | PASS | PILOT-1 §5 preserves each verdict and FULL report content verbatim (§§5a–5c). |
| AS-9 | PASS | This task's contribution touches only `allowed_paths` (three pilot reports, this report, the packet). `project-control/tasks/M0-T025.json` unmodified. No `effortLevel`/effort key added or changed in any settings file — none has ever been written (R096/R124/R159). |
| AS-10 | PASS | The pilots changed no product state. The M2-T018/M4-T008 lifecycle changes are those tasks' own accepted lifecycles under the Step-4 GO, not side effects of the pilot mechanism; master plan and milestone states are unchanged by the pilot. |

## 10. Deviations and disclosures carried into this closeout (never softened)

1. **Step-1 off-policy model.** All three Step-1 reviewer teammates were spawned with an explicit
   **Sonnet** override, not Fable 5, violating D-004-R090 as it then stood. Self-reported by the
   orchestrator at the time (progress log, 2026-07-24); the owner accepted Step-1 evidence AS-IS and
   deferred the on-policy re-run, which was later executed under M0-T028 Phase 8 with explicit
   Fable 5. Preserved, not rewritten (D-004-R132).
2. **Step-1 sentinel escape.** Preserved exactly as it happened (§9, AS-6).
3. **Step-2 REMAIN failure.** Preserved as the probe's real verdict. The owner's **D-004-R313** now
   accepts the harness-isolation mechanism as the mechanism of record — isolated worktree at the
   exact frozen base, mandatory pre-write attestation, zero writes on mismatch, packet-path
   confinement, no producer git/gh/control-CLI mutations, orchestrator exact-diff containment review,
   orchestrator port onto the controlled task branch, tree-identical proof, orchestrator-only
   integration — and **D-004-R314** requires Step 5 to describe THAT mechanism rather than the
   unsatisfiable literal pre-created-worktree wording.
4. **Step-4 post-gate model switch.** Disclosed in PILOT-3 and accepted by the owner (D-004-R315);
   no rerun required.
5. **This closeout's models.** Lead and all reviewers/verifiers: **Opus 5** under the temporary
   exception (D-004-R307/R320).

## 11. Self-checks run for this closeout

- `python tools/validate_directive_compliance.py --check` → exit 0 (registry green with amendment 8).
- `python tools/project_control.py status` → M0-T027 in-regime, blocked at 60%; 52 accepted; CP-0035.
- Registry derivation for M0-T027 → **128 applicable requirement ids, zero unresolved**; git-canonical
  content identity `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` — the
  deterministic empty-set hash, because every `allowed_path` lies under the excluded
  `project-control/` tree, so this task has no reviewable non-control-plane content by design.
- Blocker scan: no OPEN blocker references M0-T027 (B-015 resolved).
- Dependency `M0-T024`: accepted.

## 12. Requested status

**`awaiting_gate`** — the three pilot evidence artifacts exist and reconcile, B-015 is resolved, the
closeout's own checks are green, and the two arguable items (AS-1 numeric drift; AS-6
literal-vs-arc satisfaction) are disclosed for the independent reviewers to rule on rather than
resolved by the producer.
