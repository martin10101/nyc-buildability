# M0-T033 — INDEPENDENT DIRECTIVE-COMPLIANCE VERIFICATION REPORT

> **Orchestrator preservation note.** The body below is the `directive-compliance-verifier` return
> preserved **VERBATIM** per `.claude/rules/project-control.md` (report-preservation rule), with
> transport entity-decoding only (`&lt;`/`&gt;`/`&amp;` restored to `<`/`>`/`&`). Nothing was added,
> removed, condensed, or reworded. The verifier was dispatched read-only on explicit Opus 5 under
> the D-004-R307 availability exception and produced no writes; the orchestrator recorded its
> verdict into D-004 `verification.json`.
>
> This file is cited as the evidence path for all 52 requirement rows in that verification record.

---

**Reviewer:** `directive-compliance-verifier` (independent; NOT the producer of `requirements.json`, NOT the producer of the code)
**Model actually used:** Opus 5 — exact model id `claude-opus-5[1m]`, explicit spawn under the D-004-R307 availability exception. No Fable 5 was used and none is claimed.
**Mode:** read-only. No `tools/project_control.py` write subcommand, no git write, no `gh` write, no ledger or `verification.json` edit was executed.
**Directive:** D-004 `project-control/directives/D-004-agent-teams-runtime-adoption/`
**Task:** M0-T033 — Governance-orchestrator unblock-roster semantics
**Branch:** `task/M0-T033-unblock-roster-semantics`

## VERDICT: **PASS — with 5 binding corrections (V1–V5)**

52 of 52 applicable requirement ids reproduced as SATISFIED against primary evidence. Zero VIOLATED. Zero UNVERIFIABLE. Zero BLOCKED. Two requirements (R372, R373) are PASS-to-date with a residual obligation that falls due at merge/accept and must be re-verified there. Per `.claude/rules/project-control.md`, a "PASS with required corrections" is recorded as PASS and the corrections are BLOCKING for the next gate and for acceptance.

---

## 1. IDENTITY — verified first, and a drift detected mid-review

At the start of this review:

```
$ git rev-parse HEAD
1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0
```

This **matches the frozen reviewed identity** given to me. I proceeded.

**Mid-review the head advanced.** Re-checked at the end:

```
$ git rev-parse HEAD
6dec7a5b6793d188d2627c9f9661c4a19ce8f2fd

$ git diff --name-status 1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0 HEAD
A	project-control/reports/M0-T033.json
```

I did **not** treat this as fatal, because I proved the reviewed content identity is unchanged rather than assuming it:

```
$ git ls-tree -r --full-tree <SHA> -- tools/project_control.py tools/test_project_control.py docs/GATES_AND_CHECKPOINTS.md

8fd0019  b250643ac1291b47ec4462c39ff18a4fafeb5a7f  docs/GATES_AND_CHECKPOINTS.md
         6b7d3ac7b52ea3444682a08d818f81541102c2a6  tools/project_control.py
         1b5fe813a00cc130be95abc4e14ca803e7838d0d  tools/test_project_control.py
1e86cd7  (identical three blobs)
6dec7a5  (identical three blobs)
```

The path-scoped manifest excludes `project-control/` (`tools/project_control.py:311` `_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)`), so the reviewed content identity is exactly those three blobs. I recomputed it byte-for-byte with the registry's own algorithm (`tools/directive_registry.py:688-725`):

```
computed path-scoped content identity: cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665
submit record claims                 : cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665
MATCH: True
```

**Conclusion:** the identity `cd8f93b7…` is stable across `8fd0019 → 1e86cd7 → 6dec7a5`. The drift commit `6dec7a5` adds only `project-control/reports/M0-T033.json` (the CLI submit record, previously untracked). All code, test and registry evidence in this report is identical at the frozen SHA and at current head. I also observed uncommitted orchestrator lifecycle writes in flight (`project-control/state.json`, `project-control/tasks/M0-T033.json`, untracked `project-control/reports/M0-T033-control-plane-verification.md`) — all under `project-control/`, all excluded from the content manifest.

---

## 2. THE DERIVED APPLICABLE SET — 52 ids, derived not read

Derived through the canonical resolver, never from a report:

```
$ python -c "import sys,json; sys.path.insert(0,'tools'); from directive_registry import DirectiveRegistry; ..."
COUNT: 52
UNRESOLVED: []
D-004-R332, R335, R336, R337, R338, R339, R340, R341, R342, R343, R344, R345, R346,
R347, R348, R349, R350, R351, R352, R353, R354, R355, R356, R357, R358, R359, R360,
R361, R362, R363, R364, R365, R366, R367, R368, R369, R370, R371, R372, R373,
R387, R389, R410, R411, R412, R413, R414, R415, R416, R417, R418, R419
R420 in applicable? False
```

**The orchestrator's count of 52 is CONFIRMED. Zero unresolved.**

### R420 — in the registry, correctly NOT applicable

`D-004-R420` exists (`requirements.json`, row id `D-004-R420`, text *"No Step 5, no M0-T032, and no unrelated work."*, `source_ref: source-011-amendment.md#port-and-gates`). Its `applicability.task_ids` is `["D-004-OPTIONB"]`. The resolver's conjunction semantics (`tools/directive_registry.py:227-228`) require `task["task_id"] in task_ids` for any non-empty `task_ids`; `M0-T033 ∉ {D-004-OPTIONB}`, so it does not derive.

I checked whether that scoping is a *weakening* rather than a convention, and it is not: `D-004-OPTIONB` is the **established sentinel from amendment 9** for arc-level items — `R327-R329` (preamble), `R333-R334` (Phase 0 reconciliation), `R390-R399` (STILL NOT AUTHORIZED, including `R390` "Step 5 or M0-T029" and `R391` "M0-T032"), `R400-R409` (return items). R420 restates R390/R391/R398 at the arc level and is scoped identically. Enforcement for the M0-T033 window is not lost: the applicable `R418` ("authorized M0-T033 gates ONLY; no other gate, task, or lifecycle action") covers it, and I verified the substance independently anyway (§9).

**Exclusion is CORRECT.** One documentation observation is carried into V4.

### Evidence map = exactly the derived set

```
derived: 52   mapped: 52
in map but NOT derived (EXTRA): []
derived but NOT in map (MISSING): []
EXACT SET EQUALITY: True
```

`project-control/reports/M0-T033-evidence-map.json` contains exactly 52 keys, no extra, no missing. The CLI submit record `project-control/reports/M0-T033.json` independently carries the same 52 ids in `applicable_requirements`.

---

## 3. INTAKE REVIEW — source(s) vs. the atomic matrix

I compared the verbatim sources against `requirements.json` for the two amendments that create the M0-T033 regime (`source-010`, `source-011`), and verified registry-wide integrity mechanically for the remainder.

### source-011-amendment.md (amendment 10) → R410-R420

| Source sentence | Row(s) | Judgment |
|---|---|---|
| "Continue under the corrected frozen-base dispatch. No new owner decision is required." | R410 | faithful |
| "Preserve the original attestation stop and corrected resume honestly in the producer evidence." | R411 | faithful |
| "Do not waive or silently resolve either carried item" | R412 | faithful, split from R411 (two distinct obligations, correctly **not** combined) |
| "Prove that every test relied upon … is actually registered and executed." | R413 | faithful |
| "If the S10 body is never invoked, it cannot count as passing evidence and must be corrected within scope or returned as a blocker." | R414 | faithful, correctly split from R413 |
| "Preserve the required_gates/task_type validation asymmetry for an explicit independent-review ruling against R352 and R368." | R415 | faithful |
| "perform the contracted exact-diff containment review **and** tree-identical port" | R416, R417 | correctly split into two atoms |
| "Then proceed through the authorized M0-T033 gates only." | R418 | faithful |
| "Keep M0-T027 untouched until M0-T033 is merged and accepted." | R419 | faithful; header clause "It tightens D-004-R374" captured in the row text |
| "No Step 5, M0-T032, or unrelated work." | R420 | faithful; sentinel-scoped per convention |

**Missing: none. Weakened: none. Combined: none. Invented: none.**

### source-010-amendment.md (amendment 9) → R327-R409

Every numbered/bulleted obligation maps 1:1. Spot-critical checks: the eight "Preserve the existing default" bullets (lines 84-91) became exactly eight rows R347-R354 — **not combined**; the four new-case conditions (lines 97-100) became four rows R356-R359 plus R355 for the conjunction; the ten mandatory tests (lines 110-119) became exactly R362-R371; line 121's two sentences became R372 and R373; line 80's three clauses became R344/R345/R346. No source line lacks a row.

**One scoping observation (non-blocking):** source-010 line 123 *"Do not touch M0-T027 during the M0-T033 implementation"* → `R374`, scoped `task_ids: ["M0-T027"]` only, so it does **not** derive for M0-T033. The obligation is nonetheless enforced, because the applicable `R419` explicitly tightens R374 and is scoped to both `M0-T033` and `M0-T027`. Recorded in V4.

---

## 4. AMENDMENT INTEGRITY AND BYTE IDENTITY

### Validator

```
$ python tools/validate_directive_compliance.py --check
EXIT=0

$ python tools/validate_directive_compliance.py
directive registry OK: 5 directive(s), 5 active; source hashes, ID append-only,
and producer/verifier separation verified.
EXIT_CODE=0
```

### Append-only history (git, not the manifest's own claim)

```
$ git log --oneline --follow -- .../source-00N*.md   (count per file)
source-001: 1   source-002: 1   source-003: 1   source-004: 1
source-005: 1   source-006: 1   source-007: 1   source-008: 1
source-009: 1   source-010: 1   source-011: 1
```

Every committed source file is touched by **exactly one commit** — no committed source was ever edited.

### Digests recomputed from the checked-out bytes

```
source-001.md            declared=cb62b582374d9b8a actual=cb62b582374d9b8a MATCH=True CRLF=0 bytes=8362
source-002-amendment.md  declared=bba041d9c629cf5e actual=bba041d9c629cf5e MATCH=True CRLF=0 bytes=1199
source-003-amendment.md  declared=8f2bece86cfc9485 actual=8f2bece86cfc9485 MATCH=True CRLF=0 bytes=1473
source-004-amendment.md  declared=d15911caa921bcf8 actual=d15911caa921bcf8 MATCH=True CRLF=0 bytes=2122
source-005-amendment.md  declared=518348c3a878803a actual=518348c3a878803a MATCH=True CRLF=0 bytes=4112
source-006-amendment.md  declared=4f697eb9cfead699 actual=4f697eb9cfead699 MATCH=True CRLF=0 bytes=18818
source-007-amendment.md  declared=4d5caed0ca1ca71f actual=4d5caed0ca1ca71f MATCH=True CRLF=0 bytes=2560
source-008-amendment.md  declared=9cb73c514dfd9a22 actual=9cb73c514dfd9a22 MATCH=True CRLF=0 bytes=3141
source-009-amendment.md  declared=372842e93b0e697e actual=372842e93b0e697e MATCH=True CRLF=0 bytes=4726
source-010-amendment.md  declared=3b281586434267e8 actual=3b281586434267e8 MATCH=True CRLF=0 bytes=8043
source-011-amendment.md  declared=0d019ee1e77d091b actual=0d019ee1e77d091b MATCH=True CRLF=0 bytes=1858
ALL SOURCE DIGESTS MATCH: True

requirements_id_digest      declared 9a9d23816eec… actual 9a9d23816eec… MATCH=True
requirements_content_digest declared f4b66f9a0ada… actual f4b66f9a0ada… MATCH=True
requirements.json CRLF count: 0   bytes: 494514

locked ids: 420   requirement rows: 420   duplicates: 0
locked − present: []      present − locked: []
requirement_count field: 420 == rows: True
amendments_applied: source-002 … source-011  (10 amendments, matches manifest.amendments)
```

No row altered, renumbered, or removed; `locked_requirement_ids` intact; `manifest.version = 11`.

### CRLF / byte identity across checkout (item 3)

`.gitattributes:6` → `project-control/directives/** text eol=lf` (unchanged on this branch: `git diff --stat origin/main...HEAD -- .gitattributes` is empty). I proved the pin actually holds rather than trusting it — comparing the **git blob bytes** to the **on-disk bytes**:

```
source-001.md         blob=cb62b582374d9b8a disk=cb62b582374d9b8a IDENTICAL=True blob_crlf=0
… (all 11 sources)    IDENTICAL=True, blob_crlf=0
manifest.json         blob=df21353572e0272a disk=df21353572e0272a IDENTICAL=True blob_crlf=0
requirements.json     blob=f4b66f9a0ada03a9 disk=f4b66f9a0ada03a9 IDENTICAL=True blob_crlf=0
verification.json     blob=34143a05e8151b9f disk=34143a05e8151b9f IDENTICAL=True blob_crlf=0
```

A fresh clone on Windows will reproduce these digests. **No CRLF hazard.**

### No self-certification in verification.json

`verification.json` (`directive_verification/v2`), M0-T033 row: `state: "pending"`, all 52 requirement rows `state: "pending"`, `verified_at: null`, `verified_by: null`, `reviewed_sha: null`. The amendment-10 diff only *extends* the applicable id list from 42 to 52 and appends ten pending rows. **Nothing has been pre-marked PASS.**

---

## 5. HARNESS OUTPUTS (all four, run by me at head)

```
$ python tools/test_project_control.py
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (357 real ledger files parse; legacy records accepted; ...)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: S10 governance-orchestrator unblock semantics (4 conjunctive conditions, preserved defaults,
    fail-closed malformed data, gate() unchanged, source-level generality proofs)
    S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases
    S10 per-block case counts: 1-non-governance-orchestrator-refused=32,
      2-governance-orchestrator-unblocks=9, 3-governance-orchestrator-no-reviewers-refused=2,
      4-orchestrator-only-roster-refused=3, 5-governance-no-independent-gate-refused=6,
      6-malformed-fails-closed=31, 7-normal-producer-unchanged=12,
      8-cancel-and-message-only-ungated=12, 9-gate-unchanged=8,
      10-source-level-generality-proofs=3
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: S9 directive claim enforcement (refs required, selective citation refused, governance-path guard)
OK: S9 submit git-canonical identity (clean-required, dirty fails closed, stale on edit)
OK: S9 accept requires independent per-task verification at the git identity
OK: S9 regime-bypass closed + migration table (9 adversarial proofs)
OK: all 15 project-control test groups passed
EXIT_CODE=0

$ python tools/test_directive_compliance.py
Ran 55 tests in 49.371s
OK
EXIT_CODE=0

$ python tools/test_directive_reminder.py
Ran 12 tests in 2.247s
OK
EXIT_CODE=0

$ python tools/validate_directive_compliance.py --check
EXIT=0
```

---

## 6. INDEPENDENT BEHAVIORAL EVIDENCE (my own harness, not the producer's tests)

I did not accept the producer's test suite as proof of semantics. I loaded the **base** module (`abb89b821d3cb7beacc916784c92c9d5570122e0`) and the **head** module in one process and compared them across a full cross-product of packet shapes.

```
combinations compared: 21294
head-side exceptions: 0
base-REFUSE to head-ALLOW cases: 96
cases outside the four authorized conditions: 0

transition tally
  base=REFUSE  head=REFUSE  11370
  base=RAISED  head=REFUSE   7098
  base=ALLOW   head=REFUSE   1638
  base=ALLOW   head=ALLOW    1092
  base=REFUSE  head=ALLOW      96

base-ALLOW -> head-REFUSE grouped by reviewer_agents shape
  ['  orchestrator  ']  364
  'bob'                 364
  {'r': 1}              364
  [{'n': 'x'}]          364
  ['  alice  ']         182
```

Reading:
- **Exactly 96 shapes became permissible, and a programmatic classifier confirms all 96 satisfy all four conditions conjunctively (producer==orchestrator ∧ task_type==governance ∧ ≥1 gate in G1/G3/G4/G5/G6 ∧ ≥1 usable reviewer). Zero outside.** That is R355 proved, not asserted.
- **7,098 shapes that CRASHED at base now return an explanatory refusal**; **1,638 shapes that fail-open ALLOWed at base now refuse**; **0 head-side exceptions across 21,294 shapes.** That is R352/R367 proved.
- Every tightening traces to a malformed or whitespace-padded roster — the F-1 class.

### Function-level byte comparison (AST)

```
functions in base: 34   in head: 36
ADDED functions:   ['_orchestrator_governance_exception', '_roster_strings']
REMOVED functions: []
CHANGED functions: ['invalid_unblock_roster']

  gate        base=b30459c1d0d1 head=b30459c1d0d1 identical=True
  submit      base=238883bf69f0 head=238883bf69f0 identical=True
  accept      base=029e0d042aaf head=029e0d042aaf identical=True
  progress    base=478e3f8e487e head=478e3f8e487e identical=True
  claim       base=58b251053122 head=58b251053122 identical=True
  new_task    base=4e49978de269 head=4e49978de269 identical=True
  checkpoint  base=ffe7506cb1f5 head=ffe7506cb1f5 identical=True
```

**Exactly one function changed.** `_directive_submit_check` and every other function in the module are byte-identical. `tools/directive_registry.py` (evidence identity, resolver, verification) is not in the diff at all. R354/R359/R361 proved structurally.

### The real M0-T027 packet, run through the head guard (read-only)

```
M0-T027 task_type= 'governance'  producer_agent= 'orchestrator'
required_gates= ['G0', 'G2', 'G3', 'G5']
reviewer_agents= ['control-plane-verifier', 'directive-compliance-verifier', 'code-reviewer']
HEAD guard verdict on the REAL M0-T027 packet: None
```

Admitted **by shape alone**; refused by the base guard (case C19 in my differential). R360 proved. The producer declined to run this ("would be a control-plane write") — it is not; calling the pure function on a loaded dict writes nothing, and I did it.

### Negative control on the execution proof itself

Rather than trusting the producer's NC-1/NC-2/NC-3 (performed at an earlier base, in a worktree, which I could not re-observe), I ran my own **in-memory** control: I read `tools/test_project_control.py`, mutated the expected count for block 6 in memory only (no file written), and executed S10:

```
NEGATIVE CONTROL FIRED (AssertionError). First 320 chars:
S10 did not execute every mandatory block, in order, with every case.
  expected: [('1-non-governance-orchestrator-refused', 32), ('2-governance-orchestrator-unblocks', 9),
  ('3-governance-orchestrator-no-reviewers-refused', 2), ('4-orchestrator-only-roster-refused', 3),
  ('5-governance-no-independent-gate-refused', 6), …
```

The `executed == expected_blocks` assertion is **live and load-bearing**, not decorative.

---

## 7. PER-REQUIREMENT TABLE — all 52 ids, one row each

| ID | STATE | Primary evidence I reproduced (file / line / observed value) |
|---|---|---|
| D-004-R332 | **SATISFIED** | `source-010-amendment.md:27` authorizes Option B. Narrowness proved by AST: 1 changed function, 2 added helpers, 0 removed. Independent review contracted (4 reviewers) and under way. M0-T027 completion NOT performed (`tasks/M0-T027.json` status `blocked`). |
| D-004-R335 | **SATISFIED (documentary + first-person)** | `reports/M0-T033-producer-report.md:6-7` "Model: Opus 5 — exact model id `claude-opus-5[1m]`"; `M0-T033-G0-readiness.md:4` "orchestrator … Opus 5 under the D-004-R307 availability exception"; `M0-T033-control-plane-verification.md:7-8` "dispatched read-only on explicit Opus 5". I attest first-hand that I am `claude-opus-5[1m]`. **Limitation stated honestly: this repository holds no machine attestation of any spawn's model; the disclosure is the compliance artifact (paired with R336).** |
| D-004-R336 | **SATISFIED** | `grep -i fable` over `M0-T033-producer-report.md`, `M0-T033-evidence-map.json`, `M0-T033-G0-readiness.md` → the only hit is the evidence map's own statement "no Fable 5 claimed". No model other than Opus 5 is asserted anywhere. |
| D-004-R337 | **SATISFIED** | `git log --diff-filter=A -- project-control/tasks/M0-T033.json` → `2a56e18` (amendment-9 commit). The id was unused before. Title = "Governance-orchestrator unblock-roster semantics". |
| D-004-R338 | **SATISFIED** | `tasks/M0-T033.json` `producer_agent: "backend-engineer"`. `.claude/agents/backend-engineer.md` exists (`name: backend-engineer`, `tools: Read, Write, Edit, Bash…`, `isolation: worktree`) — real, existing, non-orchestrator (`orchestrator.md` is a separate definition), qualified for Python service/job-control implementation. Disjoint from all four reviewers. |
| D-004-R339 | **SATISFIED** | `tasks/M0-T033.json` `reviewer_agents == ["code-reviewer","security-reviewer","control-plane-verifier","directive-compliance-verifier"]` — exactly `source-010:55-58`. All four exist under `.claude/agents/`. |
| D-004-R340 | **SATISFIED** | `tasks/M0-T033.json` `required_gates == ["G0","G2","G3","G5"]` — exactly `source-010:62-65`. |
| D-004-R341 | **SATISFIED** | `reg.evaluate_task_refs(task)` → `ok=True, applicable=52, cited=52, missing=[], invalid_refs=[], unresolved=[], reasons=[]`. |
| D-004-R342 | **SATISFIED** | 12 changed files vs `origin/main`, each inside R342's set: 2 authorized tools files; M0-T033 packet; M0-T033 reports (producer report, evidence map, G0 readiness, CLI submit record); CLI lifecycle artifacts (`gates/M0-T033-G0.json`, `state.json`) mandated by R372; D-004 registry (owner amendment 10, D-001 capture authority, not producer output). `docs/GATES_AND_CHECKPOINTS.md` **byte-identical** — `git diff --exit-code` = 0, blob `b250643a` at base and head. Producer commit `6592b89` touched exactly 3 files. |
| D-004-R343 | **SATISFIED** | `git diff --stat origin/main...HEAD -- tools/ docs/` = only the 2 authorized tools files. `.claude/**`, `CLAUDE.md`, `.github/**`, `render.yaml`, `services/**`, `apps/**`, `packages/**` absent from the diff. AST: every non-guard function byte-identical; `directive_registry.py` untouched. |
| D-004-R344 | **SATISFIED** | `project_control.py:648-752`. The guard keys on packet **shape** only. My AST scan of the whole module: zero executable string literals matching `M\d+-T\d` in the guard; module-wide `M0-T027` count = 0 (base 0, head 0). |
| D-004-R345 | **SATISFIED** | `grep -n "M0-T027" tools/project_control.py` → **no match**. AST-stripped guard code contains no ledger task id (asserted at `test_project_control.py:1898`, independently reproduced by my own AST scan). *(AS-11's broader literal clause — see ruling OQ-3, §8.)* |
| D-004-R346 | **SATISFIED** | `add_argument` count base 28 → head 28 (**no new CLI option**). `getenv` 0/0; `os.environ` absent. New `environ`/`override`/`force` tokens are prose only at `:46` and `:723`. Test asserts `progress -h` exposes exactly `{--help,--task-id,--agent,--percent,--status,--message}`. |
| D-004-R347 | **SATISFIED** | Probe: no `producer_agent` key / `""` / `None` → `REFUSE` at both base and head (differential C01, C02, C20 = "same"). |
| D-004-R348 | **SATISFIED** | Probe with orchestrator producer + usable reviewer + `G3`: `engineering`, `research`, `integration`, `product`, `ops` all `REFUSE`. Sweep: no non-governance orchestrator shape moved to ALLOW. S10 block 1 = 32 cases. |
| D-004-R349 | **SATISFIED** | Probe: `reviewer_agents=[]` and `None` → `REFUSE` on both the normal and the orchestrator path. S10 block 3 = 2 cases. |
| D-004-R350 | **SATISFIED** | Probe: `['orchestrator']`, `['orchestrator','orchestrator']`, `['','orchestrator']` → `REFUSE`; `['  orchestrator  ']` now `REFUSE` (base ALLOW — tightening). S10 block 4 = 3 cases. |
| D-004-R351 | **SATISFIED** | Probe: producer `alice` + roster `['alice']` → `REFUSE`; `['  alice  ']` now `REFUSE` (base ALLOW). S10 block 7 covers it. |
| D-004-R352 | **SATISFIED** | Sweep: **0 head-side exceptions in 21,294 shapes**; 7,098 base-crash shapes now refuse; 1,638 base fail-open shapes now refuse. Probe outputs show explanatory strings for `'rev-a'`, `{'a':1}`, `7`, `[{'n':'x'}]`, `[None]`, `[['x']]`, and for malformed `producer_agent`. Scope asymmetry disclosed and ruled at OQ-1 (§8). |
| D-004-R353 | **SATISFIED** | `progress` byte-identical (AST `478e3f8e487e` both sides); call site `project_control.py:778` `if cur == "blocked" and target != "canceled":` unchanged — cancel bypasses the guard entirely. S10 block 8 = 12 cases (6 cancel shapes incl. malformed + 6 message-only). |
| D-004-R354 | **SATISFIED** | `gate` byte-identical (AST `b30459c1d0d1` both sides). S10 block 9 = 8 cases. |
| D-004-R355 | **SATISFIED** | 21,294-shape differential: **exactly 96** base-REFUSE→head-ALLOW transitions, **0** outside the four conjunctive conditions. Structural: `:748 if producer == RESERVED_ORCHESTRATOR:` is reached only after the general usable-reviewer check at `:739-747`. |
| D-004-R356 | **SATISFIED (with note)** | `:683 if not isinstance(task_type, str) or task_type.strip() != GOVERNANCE_TASK_TYPE:` and `:132 GOVERNANCE_TASK_TYPE = "governance"`. Probe: `None`, `123`, `''`, `'Governance'`, `'governance-x'` → REFUSE. **Note:** `' governance '` → ALLOW (strip-normalized, not byte-exact). Carried to V4. |
| D-004-R357 | **SATISFIED** | `:687-696`; reuses `:117 INDEPENDENT_GATES = frozenset({"G1","G3","G4","G5","G6"})`. Probe: `[]`, `None`, `['G0']`, `['G0','G2','G7']`, `['g3']` → REFUSE; `['G1']`,`['G3']`,`['G4']`,`['G5']`,`['G6']` → ALLOW. S10 block 5 = 6 cases and asserts the refusal names all five gate ids. |
| D-004-R358 | **SATISFIED** | `:739-747` computes `usable` for **every** task and refuses before `:748`. Probe on the orchestrator path: `[]`, `None`, `['orchestrator']`, `['']` → REFUSE; `['orchestrator','code-reviewer']` → ALLOW. |
| D-004-R359 | **SATISFIED** | AST: `gate`/`submit`/`accept`/`claim`/`new_task`/`checkpoint`/`progress`/`_directive_submit_check` all byte-identical; `directive_registry.py` untouched. The guard governs only the blocked-exit transition (single call site `:779`). |
| D-004-R360 | **SATISFIED** | I ran the head guard against the **real** `tasks/M0-T027.json`: verdict `None` (admitted) purely by shape (`governance`, `orchestrator`, `G0/G2/G3/G5`, three usable reviewers). Base guard refuses the same packet. No task id anywhere in the module. |
| D-004-R361 | **SATISFIED** | AST byte-identity above + 0 head-side exceptions across the sweep + all four suites green. No weakening of gate/submit/accept/directive verification/evidence identity/producer-vs-reviewer separation. |
| D-004-R362 | **SATISFIED** | `test_project_control.py:1656-1673`, block 1, **32 cases** executed (8 task types × 4 active targets), observed in run output. |
| D-004-R363 | **SATISFIED** | `:1675-1697`, block 2, **9 cases** (5 independent gate ids + 4 active targets), with `assert n == 5` forcing every gate id. |
| D-004-R364 | **SATISFIED** | `:1699-1710`, block 3, **2 cases** (`[]`, `None`). |
| D-004-R365 | **SATISFIED** | `:1712-1723`, block 4, **3 cases**. |
| D-004-R366 | **SATISFIED** | `:1725-1740`, block 5, **6 cases**; asserts the refusal names each of G1/G3/G4/G5/G6. |
| D-004-R367 | **SATISFIED** | `:1742-1778`, block 6, **31 cases**; asserts `"Traceback" not in r.stderr` and `"amend" in r.stderr` and status stays `blocked`. Corroborated by my own 0-exceptions sweep. |
| D-004-R368 | **SATISFIED** | `:1780-1811`, block 7, **12 cases**. My differential: for non-orchestrator producers every outcome is `same` except 4 malformed/padded shapes that tightened; **no non-orchestrator behavior loosened**. |
| D-004-R369 | **SATISFIED** | `:1813-1839`, block 8, **12 cases** (6 cancel shapes incl. malformed + 6 message-only). |
| D-004-R370 | **SATISFIED** | `:1841-1879`, block 9, **8 cases**: orchestrator refused for each of G1/G3/G4/G5/G6, unrostered reviewer refused, rostered reviewer succeeds with `role == "independent_review"`, producer refused on its own task ("own task"). |
| D-004-R371 | **SATISFIED** | All four harnesses run by me: `test_project_control.py` 15/15 exit 0; `test_directive_compliance.py` 55 tests OK exit 0; `test_directive_reminder.py` 12 tests OK exit 0; `validate_directive_compliance.py --check` exit 0. |
| D-004-R372 | **SATISFIED to date (residual open)** | `gates/M0-T033-G0.json` (administrative PASS), claim + two progress entries + submit record `reports/M0-T033.json` present; `tasks/M0-T033.json` status `awaiting_gate`, 85%. **Residual:** accept step not yet performed; must be re-verified at accept. |
| D-004-R373 | **SATISFIED to date (not yet due)** | `gh pr list` → no PR for `task/M0-T033-unblock-roster-semantics` (latest is #131 for amendment 9). `state.json accepted_tasks` = 52, `M0-T033 in accepted? False`. Nothing merged or accepted. |
| D-004-R387 | **SATISFIED** | Producer STOPPED twice without writing: frozen-base identity mismatch (`producer-report.md` §0(b)) and the 42-vs-52 derivation discrepancy, which it refused to resolve by adopting either number (§0(e), §7.1). Orchestrator STOPPED the port and reworked (progress_log 55% entry). No gate beyond administrative G0. |
| D-004-R389 | **SATISFIED to date** | `git worktree list` shows 10 worktrees still present, including unrelated `M0-T030-codegraph` and `M0-T031-codegraph-hardening` — **no cleanup at all has occurred**, so no over-broad cleanup. Residual: verify at closeout. |
| D-004-R410 | **SATISFIED** | `producer-report.md` §0(c) and §0(e) record `git rev-parse HEAD` = `170478e…` then `4da0d52…`; the commit graph confirms `abb89b8 → 170478e → 836daef → 4da0d52`. No new owner decision was solicited. |
| D-004-R411 | **SATISFIED** | `producer-report.md` §0(a) named-spawn write denial (`.claude/hooks/readonly_agent_guard.py` fail-closed); §0(b) the attestation STOP, including the material admission that the files were byte-identical and it stopped anyway; §0(c) corrected resume with verbatim `git rev-parse` / `git branch --show-current`. Neither omitted nor smoothed. |
| D-004-R412 | **SATISFIED** | Carried item 1 (never-executed S10 body) was **corrected, not waived**: progress_log 55% entry records the defect and the rework; `producer-report.md` §0(d); code now records all 10 blocks (`:1673…:1922`) and asserts the full sequence (`:1943-1947`). Carried item 2 (asymmetry) preserved unresolved (§2, §8A). Neither silently resolved. |
| D-004-R413 | **SATISFIED** | Registration: `ALL_TESTS` at `:1959-1975` includes `test_s10_governance_orchestrator_unblock` at `:1969`; runner iterates it at `:1979-1980`; summary computed as `len(ALL_TESTS)` at `:1981`. Execution observed in my own run: `S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases` plus the per-block line. My in-memory mutation proved the assertion fires. |
| D-004-R414 | **SATISFIED** | The S10 body **is** invoked (observed above), so the "cannot count" condition does not apply; the earlier defect was corrected **within M0-T033's authorized scope** (only `tools/test_project_control.py` changed) rather than waived or deferred to a blocker. Producer's NC-1/NC-2/NC-3 are **claims I did not reproduce** and I do not rely on them; I substituted my own in-memory negative control and the base-vs-head differential (the base guard fails S10 block 2 by construction). |
| D-004-R415 | **SATISFIED** | `producer-report.md` §2 header: "STATUS: UNRESOLVED BY DESIGN. The independent reviewers rule on this — not the producer, not the orchestrator", with both directions argued and neither adopted; §8A lists OQ-1 as open. `verification.json` rows all `pending`. **My explicit ruling is recorded in §8 below**, as R415 requires. |
| D-004-R416 | **SATISFIED** | Orchestrator's containment review recorded in the M0-T033 progress_log at 55% (commit `4da0d52`). **I re-performed it independently rather than accepting it:** producer commit `6592b89` = exactly 3 files; and in the live producer worktree `git -C .claude/worktrees/agent-af94933c3b313bae5 status --porcelain -uall` → only `tools/project_control.py`, `tools/test_project_control.py`, the producer report, and 2 of its own agent-memory files (permitted by `.claude/rules/project-control.md`). No escape. |
| D-004-R417 | **SATISFIED** | I hashed the **live producer worktree** and the primary checkout: `project_control.py` `6b7d3ac7b52ea3444682a08d818f81541102c2a6`, `test_project_control.py` `1b5fe813a00cc130be95abc4e14ca803e7838d0d`, producer report `0e022358622e65692331b60dfa21719e9ef35bc6` — **identical on both sides**. Tree-identical port confirmed from primary objects, not from the claim. |
| D-004-R418 | **SATISFIED** | `ls project-control/gates/ | grep M0-T033` → exactly `M0-T033-G0.json` (reviewer `orchestrator`, role `administrative`, result PASS, reviewed_sha `abb89b8…`). No other gate, task, or lifecycle action for M0-T033. |
| D-004-R419 | **SATISFIED** | `git diff --stat origin/main...HEAD -- project-control/tasks/M0-T027.json` → **empty**. Status `blocked`, 75%, `updated_at 2026-07-30T14:59:29` — predates M0-T033's contracting at `15:25:04`. Last commit touching it is `cabf723`, before this arc. Not merged, not accepted. |

**Not applicable (independently justified):** `D-004-R420` — the resolver excludes it because its `applicability.task_ids` is the `D-004-OPTIONB` arc sentinel, consistent with R327-R329/R333-R334/R390-R409 from the same amendment family. I nevertheless verified its substance independently: `tasks/M0-T029.json` absent (Step 5 not begun); `tasks/M0-T032.json` status `backlog`, `updated_at 2026-07-30T06:58:41` (untouched); `M0-T025.json` not in the branch diff. **No unrelated work.**

---

## 8. RULINGS ON THE FOUR OPEN QUESTIONS (none self-certified)

I confirm first that **neither the producer nor the orchestrator resolved any of them**: `producer-report.md` §8A states "I did not resolve, self-certify, or argue away any of the open items", `verification.json` carries no verdict, and no gate has been recorded beyond administrative G0. As one of the four contracted independent reviewers, I now rule.

**OQ-1 — the `required_gates`/`task_type` validation asymmetry (R415: R352 vs R368). RULING: R368 DOMINATES. LEAVE AS BUILT.**
Reproduced fact: with a non-orchestrator producer, `required_gates='G3'` (bare string) and `task_type={'x':1}` both return `None` (allow) — unchanged from base; with an orchestrator producer the same shapes return explanatory refusals. Reasoning on the evidence: (a) R352's subject is *roster* data, and both roster fields — `producer_agent` and `reviewer_agents` — now fail closed on **every** path (proved: 7,098 base crashes and 1,638 base fail-opens converted to refusals, 0 exceptions in 21,294 shapes); (b) `required_gates` is not read at all on the normal path, and a field that is never read cannot fail open — it is absence of coupling, not silent misinterpretation; (c) validating it on the normal path would flip previously-unblockable packets to refusals, which R368 forbids in terms. The asymmetry is the correct harmonization of R352 and R368, not an oversight. **No code change required.**

**OQ-2 — the whitespace-stripping tightening. RULING: ACCEPT, IN SCOPE.**
Reproduced fact: all 1,638 base-ALLOW→head-REFUSE transitions are malformed or whitespace-padded roster shapes; `['  orchestrator  ']` (364) and `['  alice  ']` (182) are exactly the shapes that defeat R350/R351 without stripping. The change is monotonically fail-closed on the roster fields and is what makes R350 and R351 actually hold. Accepted. **One narrow exception is recorded, not waived:** the same `.strip()` applied to `task_type` at `:683` makes `' governance '` admissible, which is a *loosening* relative to R356's "exactly 'governance'" (my case C16). `task_type` is **not** enum-validated at `new-task` (`project_control.py:532` falls back to a config lookup), so such a packet is writable. Impact is negligible (the packet genuinely is a governance task and all other conditions still apply) but it should be ruled on explicitly rather than absorbed — carried to V4.

**OQ-3 — the AS-11 literal-grep interpretation. RULING: R345/R346 SATISFIED; AS-11's literal clause is NOT met and must be recorded as ruled-on, not ignored.**
Reproduced fact: `M0-T027` occurs **0 times** in `tools/project_control.py` (base and head), and my AST scan finds **zero** task-id literals in the guard's executable code. R345's binding text ("Do not hard-code M0-T027 anywhere in the guard fix") is satisfied absolutely. However, the packet's AS-11 as literally worded ("grep for … any `M0-T0` task-id pattern in the changed region … returns nothing") is **not** satisfied: the changed region contains `M0-T033` at `project_control.py:46` as a prose cross-reference in the module docstring (`M0-T0` count base 18 → head 19). I rule that the directive requirement governs and that deleting prose provenance would conflict with CLAUDE.md principle 2; but the deviation from the packet's own scenario text is real and must be recorded in the gate record rather than passed over silently.

**OQ-4 — the 42-vs-52 derivation discrepancy. RULING: correctly RESOLVED, and the trail is RETAINED, not deleted.**
`producer-report.md` §7.1 retains the full trail — the 42-vs-52 table, the programmatic set difference showing the delta is exactly R410-R419, the root cause (amendment 10 captured at `836daef`, a child of base `170478e`), and the explicit re-basing assessment. §8A retains OQ-4 as a struck-through row rather than removing it. I independently confirm the root cause: `git log` shows `836daef` is a child of `170478e`, and my own derivation at head returns 52 with zero unresolved. Correct, and honestly retained.

---

## 9. HONESTY CHECK (item 5)

- **No completion or acceptance claim.** `producer-report.md:12-13`: "This report is producer evidence only. It does NOT claim the task is complete or accepted — an independent gate decides." No "all addressed" narrative anywhere. `manifest.json` carries no `complete`/`all_addressed` flag (validator check c13 passes).
- **No Fable 5 claim.** Model disclosed as Opus 5 / `claude-opus-5[1m]`; zero contrary claims.
- **The rejected earlier return is disclosed, not laundered.** `producer-report.md` §0(d): *"The orchestrator's containment review found the R413/R414 instrumentation incomplete (`_rec` wired to blocks 1-5 only, `executed` never read, no per-block counts printed) … The finding was correct about the file as it stood."* And §9 item 1a: *"Two producer errors occurred and are disclosed, not smoothed: the R413/R414 instrumentation was initially wired to blocks 1-5 only with `executed` never read (caught by the orchestrator's containment review, now corrected) … and my first execution-total assertion used an invented floor of 120 against a real count of 118, which failed until I measured it."* The report opens with "**This task did NOT complete in a single clean pass.**" There is **no clean single-pass narrative**. The orchestrator's own record of the defect is preserved verbatim in the M0-T033 progress_log (commit `4da0d52`).
- Minor imprecision, non-blocking: §0's lead sentence says "three dispatches" while §0 itself enumerates five corrections (a)–(e). Substance is complete; phrasing undercounts. Noted, not charged.

## 10. PROHIBITED-ACTION EVIDENCE

| Prohibited action | Observed state |
|---|---|
| merged | No PR exists for `task/M0-T033-unblock-roster-semantics` (`gh pr list --state all`; newest is #131). Nothing merged. |
| accepted | `state.json accepted_tasks` = **52**; `M0-T033 in accepted? False`; task status `awaiting_gate`; `failed_gates: []`. |
| dispatched (unauthorized) | Only the contracted producer and the contracted reviewers. `M0-T029.json` absent (Step 5 not begun); `M0-T032.json` `backlog`, untouched since `06:58:41`; `M0-T025.json` not in the diff. |
| deployed | `.github/**`, `render.yaml`, `services/**`, `apps/**` absent from the diff. |
| installed / purchased | No lockfile, manifest, or dependency file in the 12-file diff. All tooling is Python stdlib (`test_directive_compliance.py` stdlib-only tests pass). |
| closed | No blocker closed; `blocked_tasks: ['M0-T007','M0-T008','M0-T027']` unchanged; M0-T027 still blocked at 75%. |
| self-certified verification | `verification.json` M0-T033 row and all 52 requirement rows are `pending`, `verified_by: null`. |

---

## 11. BINDING CORRECTIONS (blocking for the next gate and for acceptance)

**V1 — (orchestrator, blocking before accept) The M0-T033 packet's path fields are internally inconsistent with the CLI and with R372.** `allowed_paths` omits `project-control/reports/M0-T033-evidence-map.json`, which `_directive_submit_check` (`project_control.py:424-440`) **mandates** for an in-regime submit, and omits the CLI submit record `project-control/reports/M0-T033.json`; `forbidden_paths` lists `project-control/state.json`, which R372's mandated lifecycle necessarily writes via `sync_state()`. As drafted, the packet's own AS-12 ("the changed-file set is exactly within allowed_paths") is unsatisfiable. This is an **orchestrator packet-drafting defect, not a producer containment breach** — producer commit `6592b89` touched exactly three files, all inside `allowed_paths`. R342/R343 as written in the directive ("M0-T033's own packet and reports") are satisfied. Correct the packet through the CLI, record the correction in the progress log, and state explicitly whether the amendment changes the packet's `material_digest` and how that is handled — do not backdate.

**V2 — (record-only, blocking) Record the OQ-3 ruling in the gate record.** R345/R346 PASS; the packet's AS-11 literal clause is not met because `M0-T033` appears as prose provenance at `project_control.py:46`. This must appear as an explicit ruling, not an omission.

**V3 — (record-only, blocking) Record the OQ-1 ruling under R415.** My ruling: **R368 dominates; leave the asymmetry as built.** R415 requires an explicit independent-review ruling; an unrecorded pass does not discharge it.

**V4 — (registry hygiene, next amendment only, append-only) Record three observations in the D-004 audit trail without editing any committed source:** (a) `R356` is implemented as exact-after-`strip()`, so `' governance '` is admissible, and `task_type` is not enum-validated at `new-task` — confirm this reading or remove the `strip()` for `task_type` in a follow-up; (b) `manifest.applicability_note` documents the `D-004-PHASE0` and `D-004-PROCESS` sentinels but **not** `D-004-OPTIONB`, introduced by amendment 9 and used again by R420 — the note should name it so the exclusion is self-documenting; (c) `R374` is scoped to `M0-T027` only and therefore never derives for `M0-T033`; the obligation survives solely because `R419` restates and tightens it. None of these blocks this gate.

**V5 — (re-verification, blocking at accept) R372, R373, R389 and the post-merge half of R419 carry residual obligations that cannot be discharged now.** They are PASS-to-date only. At accept, re-verify: the complete lifecycle ran; merge and accept occurred only after every required independent gate passed at one frozen identity; branch/worktree cleanup touched only the two authorized tasks; and M0-T027 remained untouched until M0-T033 was **both merged and accepted**.

---

## 12. WHAT I DID NOT VERIFY (stated rather than inflated)

1. **Spawn model identity for agents other than myself.** No repository artifact cryptographically attests a spawn's model. R335 rests on the disclosures in the producer report, the G0 readiness report and the preserved reviewer return, plus my first-person attestation. This is a systemic property of the harness, not a defect of M0-T033 — but I will not call it machine-verified.
2. **The producer's NC-1/NC-2/NC-3 negative controls.** Performed at an earlier base inside a worktree; I could not re-observe them and I do **not** rely on them. I substituted my own in-memory negative control and the 21,294-shape base-vs-head differential, both reproduced above.
3. **The security-reviewer G5 outcome**, which was still open at the time of this review (per the orchestrator's progress log). It is outside my scope and does not affect any verdict above.

---

## 13. FINAL

**VERDICT: PASS with binding corrections V1–V5.**

- SHA verified at start: `1e86cd74cc0f80bd1c2bd238e088b11640b1f2a0` (matched the frozen identity).
- SHA at end of review: `6dec7a5b6793d188d2627c9f9661c4a19ce8f2fd`; path-scoped content identity `cd8f93b76116c1e43b84bb0aa54f5ad621ddc16ae5e0a932cdfe86f65a8e1665` **unchanged** across the drift and reproduced independently.
- Derived applicable ids: **52**, zero unresolved; evidence map is exactly that set.
- Per-requirement outcome: **52 SATISFIED, 0 VIOLATED, 0 BLOCKED, 0 UNVERIFIABLE**; R372/R373 SATISFIED-to-date with residual obligations; R420 NOT_APPLICABLE with independent justification and its substance separately verified.
- Registry: append-only intact, all 11 source digests and both requirements digests reproduce from the checked-out bytes, LF pin holds against the git blobs, validator exit 0.
- I produced no writes, no commits, no gate record, and no `verification.json` entry. The orchestrator records this result.

Relevant absolute paths:
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\project_control.py`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\test_project_control.py`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\directive_registry.py`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\tools\validate_directive_compliance.py`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T033.json`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T027.json`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033-producer-report.md`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033-evidence-map.json`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T033.json`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\gates\M0-T033-G0.json`
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\directives\D-004-agent-teams-runtime-adoption\` (manifest.json, requirements.json, verification.json, source-001.md … source-011-amendment.md)
`C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.gitattributes`
