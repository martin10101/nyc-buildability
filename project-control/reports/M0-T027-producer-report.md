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

---

# PHASE 3/4 CLOSEOUT ADDENDUM (2026-07-30, owner amendment 11 / `source-012`)

Appended under D-004-R132 (append-only): **sections 1–12 above are byte-preserved**. Their content
at the moment of this append hashes to `6674a8b916e1f0cdc002a0abf75a41ea20ae19433213e2ed03a5245b2f7a79c1`
(SHA-256 over the LF-normalized bytes of the file as it stood before this section was added), and
nothing in them has been softened, corrected, or re-scoped. Where an earlier section is now
superseded by a later fact, the later fact is stated **here**, not by editing the earlier text.

## 13. Phase 3 and Phase 4 producer evidence

### 13.1 Live reconciliation before any write (D-004-R422/R423/R516)

Performed before the first byte was written, against live `git`, `gh`, and `project-control`:

| Owner-stated value | Live result | Verdict |
|---|---|---|
| `main` = `origin/main` = `208c939dcb…` | `11f3540c602849f4100517f35b7b93eca6742a8d` | **differs — non-material, see below** |
| PR #132 merged | merge `b3018f38f8d715518e5de17c4d87cc7df69079dd` | match |
| PR #133 merged | merge `208c939dcb9c0afe9f0bb72cc53bc784f2cc2514` | match |
| M0-T033 accepted at 100% | `status=accepted`, `progress_percent=100` | match |
| M0-T027 blocked at 75% | `status=blocked`, `progress_percent=75` | match |
| accepted-task count 53 | `state.json` `accepted_tasks` = 53 | match |
| checkpoint CP-0035 | `state.json` `last_checkpoint` = `CP-0035` | match |
| D-004 manifest version 11 | `manifest.json` `version` = 11 | match |
| 420 locked append-only requirement IDs | 420 rows, validator exit 0 | match |
| M0-T032 backlog | `status=backlog` | match |
| M0-T025 backlog | `status=backlog` | match |
| no `M0-T029` task file | absent from `project-control/tasks/` | match |

**The one difference, disclosed rather than absorbed.** Live `main` is one commit *ahead* of the
owner's stated head: `11f3540c` is the merge of PR #134, a docs-only refresh of
`docs/SESSION_HANDOFF.md` (1 file, +92/−49) that the owner requested at the close of the prior
session, and which the same message's own leading "Starting message for the next session" block
names as its expected head. It changes no control-plane file, no directive file, and no product
file. Recorded as **non-material**; execution proceeded, and the difference is recorded in
`source-012-amendment.md` and in `manifest.json` `audit_log` entry 12.

**Transmission disclosure.** The owner's message arrived in two blocks. The leading "Starting
message for the next session" block was truncated mid-word by the transport in six places; the
operative "GO — EXECUTE M0-T027 PHASES 3 AND 4 ONLY" block arrived complete. Both are captured
verbatim in `source-012-amendment.md`, with the truncation points marked exactly where the received
text ends. **No requirement row is derived from a truncated fragment** — every requirement is taken
from the complete GO block, which covers the same ground. Nothing was reconstructed or guessed.

### 13.2 AS-1 — exact change (D-004-R432…R439)

**Before** (`acceptance_scenarios[0]`):

> AS-1 (executable): python tools/validate_directive_compliance.py exits 0 with D-004 active, 128
> locked requirement ids, and matching requirements_id_digest_sha256 /
> requirements_content_digest_sha256.

**After:** the literal `128 locked requirement ids` assertion is retired; **128 is preserved
explicitly as the contract-time (2026-07-24) historical baseline**, and the scenario now requires
(a) the **current append-only locked-ID total derived mechanically from the live registry at
execution time**, (b) matching `requirements_id_digest_sha256`, (c) matching
`requirements_content_digest_sha256`, (d) validator exit 0, and (e) no alteration, deletion,
renumbering, or rewriting of prior directive history. **No literal total is hard-coded as
permanent** — not 128, and not the current value either (D-004-R439).

**Directive history was not rewritten** (D-004-R377/R438/R449): `requirements.json` grew
append-only 420 → 516 rows with **zero existing rows edited**, no committed `source-*.md` was
modified, and `python tools/validate_directive_compliance.py` exits 0 with the append-only ID
digest and the requirements-body content digest both re-derived and matching.

### 13.3 AS-6 — exact change (D-004-R440…R447)

**Before** (`acceptance_scenarios[5]`): a single-shot negative test in which *both* the Write
attempt and the Bash redirection are denied and the orchestrator then confirms the sentinel does
not exist.

**After:** the scenario now states the historical truth first and only then the remediation arc.

*Preserved exactly as recorded — the original Step-1 test FAILED:* at frozen SHA
`da0d42b6e9334e823a95aa5cd120f480dbc501c8` the reviewer's Write-tool attempt was blocked **only by
tool-unavailability** (`No such tool available: Write` — the guard's own denial text was never
produced), and the Bash redirection `echo x > ./PILOT_SENTINEL.tmp` **escaped the guard and created
the file**; the orchestrator's own independent `test -e` returned **exit 0 (EXISTS, 2 bytes,
untracked). The FAIL/FAIL/PASS verdicts and `AGENT-TEAMS-PILOT-1.md` are **unchanged on this
branch** (`git diff main...HEAD` lists no pilot report), and the original Step-1 result is **never
rewritten as a pass** (D-004-R441/R442/R447/R379).

*Satisfied only across the owner-sequenced remediation arc*, by citing
`project-control/reports/M0-T028-PHASE8-fresh-session-report.md` at frozen head `88045b06`:

- **(a) guard denial** — `readonly_agent_guard.py` *itself* denied the load-bearing Bash redirection
  with its verbatim `_deny` text naming the resolved identity `'code-reviewer'` (report §4 and
  Appendix A(b); D-004-R135/R137 ruled **PASS** by the independent verifier). The Phase-8 report is
  scrupulous about the other half: the Write attempt there was *also* blocked by tool-unavailability
  and the report states plainly, "I make no claim that the guard denied this call."
- **(b) independent absence verification** — the **orchestrator** ran
  `test -e ./PILOT_SENTINEL.tmp` → **exit 1, ABSENT**, corroborated by `ls` and `git status`
  (D-004-R215/R278 ruled **PASS**).
- **(c) ordering** — `project-control/blockers/B-015-teammate-readonly-guard-bypass.json` moved
  `open` → `resolved` **only after** that fresh-session proof, its audit entry citing PR #121,
  merge `9db4ab3…`, and frozen head `88045b0`.

### 13.4 Digest impact of the Phase-3 changes (D-004-R450/R380/R451)

`acceptance_scenarios` **is** in `directive_registry.MATERIAL_FIELDS`, so the material packet digest
moved:

| | value |
|---|---|
| material digest before Phase 3 | `dc5d2979f844675f1f7a9422f2cbea9c7b48e1cdbcdd194fd2b3b1113af830a0` |
| material digest after Phase 3 | `d6afb9d70cdaac3778faed121beb0e39bdf90cb842c2fde54b781966013cac31` |

**Control-plane consequence: none for this task**, and the reason is structural rather than
convenient. `material_digest` has exactly one consumer, `_legacy_grandfather_check`, and both
`submit()` (tools/project_control.py:833-844) and `accept()` (:1035-1043) reach it **only on the
`else` branch of `if _task_in_regime(t)`**. M0-T027 carries `directive_regime_version: "1.0"` and
`_task_in_regime()` returns `True`, so the grandfathering branch is never taken. There was also no
grandfathering to lose: M0-T027 is absent from the frozen migration manifest by design — it was
contracted 2026-07-24, long after the regime baseline `1acb9b51`.

`reviewer_agents` is **excluded** from `MATERIAL_FIELDS` (it is roster bookkeeping), so the
pre-flight roster correction contributes nothing to the digest change; the change above is entirely
attributable to the two authorized acceptance-scenario clarifications. **Nothing was backdated**:
every timestamp written in this phase is the actual write time (D-004-R451).

### 13.5 Pre-flight reviewer-roster correction and the historical G0 record

**Correction applied** (D-004-R424/R425): `reviewer_agents` is now
`["control-plane-verifier", "directive-compliance-verifier", "code-reviewer", "security-reviewer"]`
— exactly one addition.

**Rationale, verified mechanically rather than accepted on assertion:**

1. M0-T027's `required_gates` include **G5**, unchanged.
2. `docs/GATES_AND_CHECKPOINTS.md:164` — "Security-sensitive work requires `security-reviewer` even
   if QA passed."
3. `tools/project_control.py` `gate()` rejects an independent gate whose reviewer is not rostered:
   `if a.reviewer not in reviewers: return fail(f"Reviewer {a.reviewer!r} is not in this task's
   reviewer_agents {reviewers}; independent gate {a.gate_id} rejected.")`

So before the correction the already-required G5 was **unsatisfiable by the proper specialist**. No
other reviewer was substituted (D-004-R428). `producer_agent` (`orchestrator`) and `required_gates`
(`G0`,`G2`,`G3`,`G5`) are **unchanged** (D-004-R426), verified by assertion in the applying script
and visible in the two-hunk packet diff.

**Historical G0 record (D-004-R429/R430).** `project-control/gates/M0-T027-G0.json` is **untouched**:
`git log -- <path>` shows exactly one commit (`0361491`, the original Step-1 commit);
`git status` reports it unmodified; and its working-tree bytes are identical to the committed blob
after EOL normalization (the CRLF is a Windows-checkout artifact of `core.autocrlf=true`, not an
edit). Canonical blob SHA-256: `40abdd492bc9d25953bede4251a35b4f654590775caffb37cc445c48a1ba3ad6`.
It remains valid for acceptance under the stored-history rule: `accept()` requires a PASS record per
required gate and, for *independent* gates only, a non-`self_check` record whose reviewer differs
from the producer. G0 is an **administrative** gate (`ADMINISTRATIVE_GATES`), lawfully recorded by
the orchestrator, and the CLI's documented backward-compatibility contract is that stored history is
never retro-rejected on read or at accept time. **No replacement G0 is required**, so the
stop-and-report condition of D-004-R431 is not triggered.

### 13.6 Frozen closeout identity (D-004-R382/R454)

One identity is frozen for the whole independent-review wave:

- **Reviewed SHA:** the head of `task/M0-T027-closeout-phases-3-4` at the "closeout evidence frozen"
  commit — stated exactly in §13.9 below and in every reviewer dispatch.
- **Content manifest:** `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` — the
  deterministic **empty-set** hash, because every `allowed_path` of this task lies under the
  excluded `project-control/` tree. This task's product **is** control-plane evidence by design; the
  empty-set hash is the correct value, not a defect, and it is identical to the value carried at the
  prior closeout attempt.

### 13.7 Evidence map regenerated by the canonical resolver (D-004-R383/R455…R458/R515)

`project-control/reports/M0-T027-evidence-map.json` was **rebuilt from
`directive_registry.evaluate_task_refs`**, not carried forward:

| quantity | value | what it is |
|---|---|---|
| contract-time D-004 total | **128** | the D-004 requirement total on 2026-07-24, when this packet was contracted — history only |
| current D-004 locked total | **516** | live append-only total in `manifest.json` after amendment 11 (420 → 516) |
| **applicable to M0-T027** | **233** | **derived by the canonical resolver** against this packet's `task_id`/`task_type`/`milestone`/`allowed_paths` |

The three numbers are kept strictly separate and none is substituted for another (D-004-R456). The
derived set is **233**, with **zero unresolved** applicability reasons — so the D-004-R458/R387 stop
condition is not triggered. Of those, **128** pointers were carried forward verbatim from the prior
map (all 128 remain applicable; **none** was dropped) and **105** are newly covered: 22 rows from
amendments 9–10 that describe this very closeout arc, and 83 rows from amendment 11. The previously
recorded coverage was **discarded and rebuilt**, not preserved (D-004-R457/R515). All 233 rows
resolve to D-004; no row of D-001/D-002/D-003/D-005 is applicable to this packet — D-001's 136 rows,
for example, are all scoped `task_ids: ["M0-T023"]`.

### 13.8 Containment (D-004-R477/R478 and AS-9)

Complete `git diff --name-only main...HEAD` for this closeout, with each path's authority:

| path | authority |
|---|---|
| `project-control/directives/D-004-…/source-012-amendment.md` | orchestrator **D-001 capture** authority (deliberately outside `allowed_paths`; see the packet's `allowed_paths_note` and `forbidden_paths`) |
| `project-control/directives/D-004-…/requirements.json` | same — append-only rows R421–R516 |
| `project-control/directives/D-004-…/manifest.json` | same — version, source digest, locked IDs, digests, `audit_log` |
| `project-control/tasks/M0-T027.json` | `allowed_paths` entry 5, the **orchestrator lifecycle path** |
| `project-control/reports/M0-T027-evidence-map.json` | lifecycle artifact of the in-regime submit (`--evidence-map`) |
| `project-control/reports/M0-T027-producer-report.md` | `allowed_paths` entry 4 |
| `project-control/state.json` | ledger sync written by the CLI (`sync_state()`), never by hand |

**Nothing else.** No product file, no `services/**`, `apps/**`, `packages/**`, no `tools/**`, no
`.claude/hooks/**`, `.claude/agents/**`, `.claude/rules/**`, no settings file, no deployment
definition, no other task's packet or report. `project-control/tasks/M0-T025.json` is **unmodified**
(D-004-R492), and **no `effort`/`effortLevel` key** was added or changed anywhere (D-004-R497) — both
verified by diff, not by assertion.

### 13.9 Producer self-checks at the frozen identity

Recorded in §13.10 (self-check gate G2) together with the exact frozen SHA, so that the numbers and
the identity they were measured at cannot drift apart.

### 13.10 Producer self-checks (G2 evidence)

All run by the producer/orchestrator on this branch immediately before the evidence commit that
freezes the closeout identity:

| check | command | result |
|---|---|---|
| directive registry | `python tools/validate_directive_compliance.py --check` | **exit 0** — 5 directives, 5 active; source hashes, ID append-only, and producer/verifier separation verified |
| control-plane suite | `python tools/test_project_control.py` | **exit 0** — all **15/15** test groups passed |
| directive-compliance suite | `python tools/test_directive_compliance.py` | **exit 0** — **55 tests, OK** |
| M0-T033 guard operating normally (D-004-R472) | S10 block of the control-plane suite | **PASS** — "governance-orchestrator unblock semantics (4 conjunctive conditions, preserved defaults, fail-closed malformed data, gate() unchanged, source-level generality proofs)", **118 cases** across its 10 blocks (32/9/2/3/6/31/12/12/8/3) |
| unblock admitted on shape, not on a special case | `invalid_unblock_roster(packet)` | returns **`None`** both **before** and **after** the roster correction — confirmed mechanically *before* the transition was attempted, never assumed (D-004-R453) |
| ledger | `python tools/project_control.py status` | M0-T027 present, in-regime, `in_progress` at 80%; **53 accepted**; **CP-0035** |
| resolver | `evaluate_task_refs(M0-T027)` | refs **ok**, **233** applicable ids, **0 unresolved** |
| content identity | `_task_git_identity` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty-set hash by design, §13.6) |
| blockers | scan of `project-control/blockers/*.json` | **no OPEN blocker references M0-T027**; B-015 `resolved` |
| dependency | `M0-T024` | **accepted** |
| D-004 registry totals | `manifest.json` | **516** locked ids; `requirements_id_digest_sha256` `70758c67…`, `requirements_content_digest_sha256` `f8e09fac…`, both re-derived and matching |

**On the frozen SHA.** The closeout identity is the SHA of the evidence commit that carries
everything above. By construction that SHA cannot appear inside the tree it names; it is stamped in
the **G2 gate record** (`project-control/gates/M0-T027-G2.json` → `reviewed_sha`), in the submit
record, and verbatim in **every** reviewer dispatch, so all four independent reviewers rule on one
identical identity. Section 14 records each reviewer's own `git rev-parse HEAD` against it.
