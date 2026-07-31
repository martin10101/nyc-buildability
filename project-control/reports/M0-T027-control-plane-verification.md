# M0-T027 — independent control-plane verification (VERBATIM reviewer return)

**Orchestrator header (NOT part of the reviewer's return).** Dispatched read-only against frozen
identity `3ed05fda6d434670e5b610e6dad7a8b224a9aa94` on branch
`task/M0-T027-closeout-phases-3-4`. Agent type `control-plane-verifier`, spawn name `m0t027-cpv`.
Model value passed at spawn: **explicit Opus 5** under the still-active temporary availability
exception (D-004-R307). The reviewer independently discloses its actual model below. No Fable 5 is
claimed for this wave. Everything from the horizontal rule to the end of this file is the
reviewer's return preserved **verbatim** (D-004-R385/R468); the orchestrator altered nothing.

---

# M0-T027 INDEPENDENT CONTROL-PLANE VERIFICATION REPORT

Reviewer identity: control-plane-verifier (spawn name `m0t027-cpv`), read-only.
Producer under review: `orchestrator`. Reviewer != producer: CONFIRMED.
Date of review: 2026-07-30.
Model actually used: Claude Opus 5 (1M context), `claude-opus-5[1m]`. I did not use Fable 5 and do not claim to have.

VERDICT: **PASS** — with five recorded observations (O-1..O-5), none of which is a control-plane integrity violation at the reviewed identity. Two are forward-looking prerequisites the orchestrator must satisfy before acceptance (O-1, O-4).

Method note: every claim below was re-derived from primary artifacts (git objects, the packet, the gate records, the CLI source). Where I relied on the producer's narrative I say so explicitly. My sandbox blocks writes; several read-only commands that combined `git show` with a pipe or `subprocess` were refused by the guard, and I re-derived the same facts by another read-only route each time; those substitutions are named in-line.

---

## CHECK 0 — FROZEN IDENTITY AND WORKING-TREE DELTA

Command:
```
git rev-parse HEAD ; git rev-parse --abbrev-ref HEAD ; git status --porcelain
```
Output (my own run):
```
3ed05fda6d434670e5b610e6dad7a8b224a9aa94
task/M0-T027-closeout-phases-3-4
```
**CONFIRMED**: my HEAD is exactly `3ed05fda6d434670e5b610e6dad7a8b224a9aa94` on `task/M0-T027-closeout-phases-3-4`, matching the frozen reviewed identity.

Tracked control-plane deltas in the working tree, exactly as disclosed:
```
?? project-control/gates/M0-T027-G2.json
 M project-control/state.json
 M project-control/tasks/M0-T027.json
```
I verified their content rather than accepting the disclosure:
```
git diff HEAD -- project-control/tasks/M0-T027.json project-control/state.json
```
The entire uncommitted tracked delta is two `updated_at` bumps:
- `project-control/state.json`: `2026-07-30T19:23:23.474515+00:00` -> `2026-07-30T19:33:47.556123+00:00`
- `project-control/tasks/M0-T027.json`: `2026-07-30T19:23:23.381489+00:00` -> `2026-07-30T19:33:47.467362+00:00`

No status, percent, roster, gate, scenario, or path field changed uncommitted. File mtimes corroborate one single CLI invocation:
```
stat -c '%y %n' project-control/state.json project-control/tasks/M0-T027.json project-control/gates/M0-T027-G2.json
2026-07-30 15:33:47.556123800 -0400 project-control/state.json
2026-07-30 15:33:47.468365300 -0400 project-control/tasks/M0-T027.json
2026-07-30 15:33:47.462361900 -0400 project-control/gates/M0-T027-G2.json
```
All three written within 94 ms of each other, in the order `gate record -> save(task) -> sync_state()` that `gate()` performs (tools/project_control.py:931, 953, 954). **CONFIRMED: CLI-written, not hand-edited.**

The disclosure is accurate as to *tracked* deltas. For completeness, the working tree also carries pre-existing untracked/agent-memory noise that is outside the ledger and predates the frozen commit (branch commits are 15:19, 15:23, 15:33 EDT):
- ` M .claude/agent-memory/backend-engineer/env-producer-sandbox-no-exec.md` — mtime 2026-07-29 22:37 EDT (agent memory, explicitly non-authoritative per `.claude/rules/project-control.md`).
- `?? .npmrc` — mtime 2026-07-28 12:38 EDT, untracked and NOT gitignored (`git check-ignore` exit 1).
- `?? ".claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4 (1).md"` — mtime 2026-07-30 13:08 EDT, untracked and NOT gitignored, sitting inside the governed `.claude/` tree.
- ~30 untracked `.claude/agent-memory/**` files and `?? .claude/agent-memory/visual-quality-reviewer/`.

None of these is in the branch diff and none changes anything at HEAD. See **O-5** (staging hazard).

---

## CHECK 1 — LIFECYCLE LEGALITY (blocked -> in_progress, 80%)

**1a. Transition is legal in the enum.** `tools/project_control.py:101-112`:
```
PROGRESS_TRANSITIONS = { ... "blocked": {"backlog", "ready", "in_progress", "awaiting_gate", "canceled"}, ... }
```
`blocked -> in_progress` is an allowed `progress` transition. **CONFIRMED.**

**1b. It was performed by the CLI, not a hand edit.** Evidence, independently derived:
- The packet's last `progress_log` entry has exactly the shape `progress()` appends at tools/project_control.py:802-804 — keys `at`, `agent`, `percent`, `status`, `message` and nothing else — with `"at": "2026-07-30T19:23:23.381489+00:00"`, `"agent": "orchestrator"`, `"percent": 80`, `"status": "in_progress"`.
- `state.json.updated_at` at HEAD is `2026-07-30T19:23:23.474515+00:00`, i.e. 93 ms after the packet write. That is the `save(p, t)` -> `sync_state()` sequence at lines 805-806. A hand edit would have had to fabricate a consistent second file.
- I recomputed every `sync_state()` roster from the task packets and compared to `state.json` (see CHECK 8): all four fields match exactly.
- `git log --name-only main..HEAD` shows the 80% transition landed in commit `3ed05fd`, which touches no tool and no other packet.

**CONFIRMED** (strong evidence, not cryptographic proof: the CLI leaves no signature, so a sufficiently careful hand edit is not formally excluded. Everything observable is consistent with the CLI and inconsistent with a casual hand edit.)

**1c. The transition was admitted by the general M0-T033 shape rule, not by a special case.** I read both functions myself.

`invalid_unblock_roster` (tools/project_control.py:700-750) requires a non-empty `producer_agent` and at least one reviewer that is non-empty, not `orchestrator`, and not the producer; when `producer == RESERVED_ORCHESTRATOR` it delegates to `_orchestrator_governance_exception`.

`_orchestrator_governance_exception` (tools/project_control.py:669-697) admits only when `task_type.strip() == GOVERNANCE_TASK_TYPE` ("governance", line 132) AND `set(required_gates) & INDEPENDENT_GATES` is non-empty (`INDEPENDENT_GATES = {G1,G3,G4,G5,G6}`, line 117).

There is **no task id, no flag, and no environment lookup** anywhere in either function. Repo-wide check:
```
grep -n "os.environ|getenv" tools/project_control.py tools/directive_registry.py
tools/directive_registry.py:652:  env={**os.environ, "GIT_LITERAL_PATHSPECS": "1"}, timeout=60)
```
The single environment use is a git-invocation hardening flag, not a control bypass. **CONFIRMED.**

I then executed the guard against the actual packets:
```
python -c "... pc.invalid_unblock_roster(t) ..."
current packet (HEAD):            None
pre-correction packet (main):     None
counterfactual reviewers=['orchestrator']:  "reviewer_agents has no usable independent reviewer ..."
counterfactual task_type='implementation':  "producer_agent is the reserved 'orchestrator' and task_type is 'implementation' ..."
counterfactual required_gates=['G0','G2']:  "... requires no independent gate (G1/G3/G4/G5/G6) ..."
```
Two findings of substance:
- The guard returned `None` on the **pre-correction** packet too (three reviewers, no `security-reviewer`). **The roster correction was therefore NOT the route to admission** — the unblock would have been admitted without it. This is the decisive evidence against a manufactured-gate reading (see CHECK 2).
- The three counterfactuals prove the exception is conditioned on packet *shape* alone and refuses in each direction.

**1d. The regime-entry guard did not apply.** Lines 791-799 fail closed only for a task that is `not _task_in_regime(t)`. M0-T027 carries `directive_regime_version: "1.0"` and `directive_refs`, so `_task_in_regime()` is True and the branch is not taken. That guard was not bypassed; it was simply not applicable. **CONFIRMED.**

**1e. The tooling under which this ran is the accepted M0-T033 code, unmodified.**
```
git diff --name-only 208c939 HEAD -- tools/ .claude/ docs/   ->  docs/SESSION_HANDOFF.md   (PR #134, already in main's ancestry)
git status --porcelain tools/                                ->  (empty)
```
No `tools/` or `.claude/` file differs from the post-PR-#133 merge point, and the working tree is clean for `tools/`. The guard that admitted the transition is byte-identical to the reviewed and accepted M0-T033 output. **CONFIRMED.**

---

## CHECK 2 — ROSTER CORRECTION

```
git diff main...HEAD -- project-control/tasks/M0-T027.json
```
Relevant hunk, in full:
```
   "reviewer_agents": [
     "control-plane-verifier",
     "directive-compliance-verifier",
-    "code-reviewer"
+    "code-reviewer",
+    "security-reviewer"
   ],
-  "status": "blocked",
-  "progress_percent": 75,
+  "status": "in_progress",
+  "progress_percent": 80,
```
- **Exactly one addition** to `reviewer_agents`: `security-reviewer`. CONFIRMED.
- **Every pre-existing reviewer identity unchanged** (`control-plane-verifier`, `directive-compliance-verifier`, `code-reviewer` appear as context lines / unchanged). CONFIRMED.
- **`producer_agent` unchanged.** It does not appear in the diff at all; pre-correction packet at `main` reads `producer: orchestrator`, HEAD reads `orchestrator`. CONFIRMED.
- **`required_gates` unchanged.** Not in the diff; both `main` and HEAD read `['G0','G2','G3','G5']`. CONFIRMED.
- **`reviewer_agents` is genuinely excluded from `MATERIAL_FIELDS`.** tools/directive_registry.py:814-816, read verbatim:
```
MATERIAL_FIELDS = ("objective", "inputs", "outputs", "dependencies",
                   "allowed_paths", "forbidden_paths", "acceptance_scenarios",
                   "required_gates", "risks", "blockers")
```
`reviewer_agents` and `producer_agent` are absent. CONFIRMED.

**Judgement: legitimately non-material, and NOT a route to a manufactured gate.** Three independent reasons:
1. The unblock guard already returned `None` before the correction (CHECK 1c), so the correction bought no lifecycle admission.
2. The correction does not *create* a gate requirement; `G5` was already in `required_gates` at contracting time (verified in the packet at its creation commit `ba7be38`). It makes an already-required gate satisfiable by the specialist the protocol names — `docs/GATES_AND_CHECKPOINTS.md:164`: "Security-sensitive work requires `security-reviewer` even if QA passed." Without it, `gate()` (tools/project_control.py:898-900) would reject a `security-reviewer` G5 record as "not in this task's reviewer_agents".
3. It is owner-authorized in specific, bounded terms: `source-012-amendment.md:139-145` authorizes adding exactly `security-reviewer` and forbids changing `producer_agent`, `required_gates`, or any other reviewer identity. What was done matches what was authorized, with nothing extra.

Adding a reviewer *widens* the pool of identities that can independently gate this task; it cannot lower the independence bar, because `gate()` still enforces `reviewer != producer` and `reviewer != orchestrator` for every independent gate. **CONFIRMED — non-material, correctly scoped, not a manufactured gate.**

---

## CHECK 3 — MATERIAL DIGEST (dc5d2979 -> d6afb9d7)

I recomputed both digests myself with the canonical function rather than trusting the producer's numbers:
```
pre-correction packet (git show main:...):  dc5d2979f844675f1f7a9422f2cbea9c7b48e1cdbcdd194fd2b3b1113af830a0
current packet (HEAD):                      d6afb9d70cdaac3778faed121beb0e39bdf90cb842c2fde54b781966013cac31
```
Both match the producer's stated values exactly. `acceptance_scenarios` IS in `MATERIAL_FIELDS` (line 815), so the digest movement is the expected consequence of the two AS clarifications. **CONFIRMED.**

**Consequence analysis — I verified the code paths rather than the narrative.** Repo-wide consumers of `material_digest`:
```
tools/project_control.py:347       reg_mod.material_digest(t) != mm.digest_for(task_id)   <- inside _legacy_grandfather_check
tools/directive_registry.py:819    def material_digest(...)
tools/validate_directive_compliance.py:224  t.get("material_digest")  <- reads the MANIFEST's own recorded digests (shape/64-hex validation of migration_manifest.json entries), never recomputes against a live packet
tools/test_project_control.py:*    tests only
```
The single production consumer is `_legacy_grandfather_check` (lines 330-355). Its two call sites:
- `submit()` line 842 — inside the `else:` branch of `if _task_in_regime(t):` (line 833).
- `accept()` line 1040 — inside the `else:` branch of `if _task_in_regime(t):` (line 1035).

`gate()` never calls it. `progress()` never calls it. M0-T027 has `directive_regime_version: "1.0"`, so `_task_in_regime()` (line 302-305) returns True and **both grandfathering branches are unreachable for this task**. Independently corroborating that there was nothing to invalidate:
```
grep -n "M0-T027" project-control/directives/migration_manifest.json  ->  No matches found
```
M0-T027 is absent from the frozen migration manifest, so it could never have been grandfathered regardless of digest.

**CONFIRMED: the producer's reasoning is correct, and I found no consequence it missed.** No blocking finding here.

---

## CHECK 4 — GATE RECORDS

**Gate inventory:**
```
ls project-control/gates/ | grep M0-T027   ->   M0-T027-G0.json, M0-T027-G2.json
```
Only two records exist. **No G3, no G5, no independent gate of any kind has been recorded.** CONFIRMED.

**G0 not overwritten, recreated, or backdated:**
```
git log --oneline --follow -- project-control/gates/M0-T027-G0.json
0361491 M0-T027: D-004 Step-1 reviewer pilot - negative test FAILED, blocker B-015
```
A single commit in its entire history. Blob identity across the whole span:
```
git show 0361491:project-control/gates/M0-T027-G0.json | git hash-object --stdin  ->  b542f03ee17ae18e947d87daea4213deb32539c5
git rev-parse HEAD:project-control/gates/M0-T027-G0.json                          ->  b542f03ee17ae18e947d87daea4213deb32539c5
git status --porcelain project-control/gates/M0-T027-G0.json                      ->  (empty, clean)
```
Identical blob hashes from the introducing commit to HEAD, with no working-tree modification. The record also carries **no `history` array**, which `gate()` would have added at line 925-930 had it ever been re-recorded. Content read in full:
```json
{ "task_id": "M0-T027", "gate_id": "G0", "reviewer": "orchestrator", "role": "administrative",
  "result": "PASS", "report_file": "project-control/reports/M0-T027-producer-report.md",
  "reviewed_at": "2026-07-24T18:35:04.645350+00:00",
  "content_manifest_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "reviewed_sha": "da0d42b6e9334e823a95aa5cd120f480dbc501c8",
  "updated_at": "2026-07-24T18:35:04.975765+00:00" }
```
**CONFIRMED: untouched, un-backdated, single-origin.**

**Was the G0 record lawful when written?** I checked this rather than assuming, because today `gate()` line 879-880 refuses an administrative gate when `producer == reviewer`, and this packet's producer is now `orchestrator`. The hardening that added that line landed 2026-07-17 (`3e5e6e5`, M0-T014), i.e. **before** the 2026-07-24 recording — so the check was live. The resolution is that `producer_agent` was not yet set:
```
git show ba7be38:project-control/tasks/M0-T027.json  ->  producer: None  status: backlog  pct: 0
```
`new_task()` creates `"producer_agent": None` (line 580) and `claim()` sets it (line 640). At 18:35:04 the task was un-claimed, `producer` was falsy, the `if producer and producer == a.reviewer` guard did not fire, and `role="administrative"` was assigned lawfully. **CONFIRMED lawful at time of writing.** See **O-2** for the structural consequence.

**G2 record — correctly formed:**
```json
{ "task_id": "M0-T027", "gate_id": "G2", "reviewer": "orchestrator", "role": "self_check",
  "result": "PASS", "report_file": "project-control/reports/M0-T027-producer-report.md",
  "reviewed_at": "2026-07-30T19:33:47.172167+00:00",
  "content_manifest_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "reviewed_sha": "3ed05fda6d434670e5b610e6dad7a8b224a9aa94",
  "updated_at": "2026-07-30T19:33:47.461360+00:00" }
```
- `role` is `self_check`, machine-assigned by `gate()` line 869-874 (G2 is in `SELF_CHECK_GATES` and the reviewer must be `orchestrator`). CONFIRMED.
- `reviewed_sha` equals my own `git rev-parse HEAD` exactly. CONFIRMED.
- Content manifest: I recomputed it with the same function the CLI uses (`pc._task_git_identity(dr, t)`) and got `e3b0c442...` with `resolved_sha 3ed05fda...` and `err: None` — byte-for-byte what the record stores. CONFIRMED.
- `report_file` exists (`project-control/reports/M0-T027-producer-report.md`). CONFIRMED.
- `accept()` line 995-1002 can never let a `self_check` record satisfy an independent gate. G2 is in the packet's `required_gates` as a self-check gate only.

**No independent gate has been recorded by the producer, and no reviewer identity equals `producer_agent`.** CONFIRMED (only two records exist; both are orchestrator-recorded non-independent classes).

See **O-3** on the empty-set content manifest.

---

## CHECK 5 — REVIEWER INDEPENDENCE

`producer_agent`: `orchestrator`.
`reviewer_agents`: `["control-plane-verifier", "directive-compliance-verifier", "code-reviewer", "security-reviewer"]`.

- Four identities, all distinct from each other (no duplicates). CONFIRMED.
- None equals `orchestrator`. CONFIRMED.
- All four exist as real agent definitions:
```
ls .claude/agents/ | grep -E "security-reviewer|code-reviewer|control-plane-verifier|directive-compliance-verifier"
code-reviewer.md
control-plane-verifier.md
directive-compliance-verifier.md
security-reviewer.md
```
- `gate()` still forbids the reserved identity from independent gates — tools/project_control.py:887-891, read verbatim:
```
if a.reviewer == RESERVED_ORCHESTRATOR:
    return fail(f"Reviewer {RESERVED_ORCHESTRATOR!r} is reserved and cannot record an "
                f"independent gate ({a.gate_id}): it records self_check (G2) and "
                f"administrative (G0/G7) gates only. ...")
```
followed by `if producer and a.reviewer == producer: return fail("Producer cannot independently gate own task.")` and the roster-membership check. That code is byte-identical to the accepted M0-T033 version (CHECK 1e). **CONFIRMED — the producer cannot satisfy G3 or G5, and no unrostered identity can either.**

Independence at acceptance is additionally enforced at `accept()` lines 995-1005 (self_check can never satisfy an independent gate; a producer-recorded independent gate is rejected). **CONFIRMED.**

---

## CHECK 6 — CONTAINMENT

Complete branch diff, produced by me:
```
git diff --name-only main...HEAD
project-control/directives/D-004-agent-teams-runtime-adoption/manifest.json
project-control/directives/D-004-agent-teams-runtime-adoption/requirements.json
project-control/directives/D-004-agent-teams-runtime-adoption/source-012-amendment.md
project-control/reports/M0-T027-evidence-map.json
project-control/reports/M0-T027-producer-report.md
project-control/state.json
project-control/tasks/M0-T027.json
```
```
git diff --numstat main...HEAD
115  5   .../manifest.json
3735 2   .../requirements.json
280  0   .../source-012-amendment.md
118  4   project-control/reports/M0-T027-evidence-map.json
236  0   project-control/reports/M0-T027-producer-report.md
3    3   project-control/state.json
21   6   project-control/tasks/M0-T027.json
```
Topology: `main = origin/main = merge-base = 11f3540c602849f4100517f35b7b93eca6742a8d`; the branch is a clean 3-commit fast-forwardable descendant; `git branch --contains 3ed05fd` lists only `task/M0-T027-closeout-phases-3-4`. Nothing was pushed to main.

Per-path judgement:

| Path | Classification | Verdict |
|---|---|---|
| `directives/.../manifest.json` | Orchestrator D-001 capture; `forbidden_paths` deliberately places `project-control/directives/**` outside producer scope, and `allowed_paths_note` says so explicitly | IN BOUNDS |
| `directives/.../requirements.json` | same | IN BOUNDS |
| `directives/.../source-012-amendment.md` | same (new verbatim amendment file) | IN BOUNDS |
| `reports/M0-T027-producer-report.md` | `allowed_paths` entry 4 | IN BOUNDS |
| `reports/M0-T027-evidence-map.json` | **NOT in `allowed_paths`** — CLI-mandated lifecycle evidence, explicitly ordered by the owner | See **O-1** |
| `state.json` | CLI-written by `sync_state()`; `forbidden_paths` names `state.json` as off-limits to the producer, and it was not producer-written | IN BOUNDS |
| `tasks/M0-T027.json` | `allowed_paths` entry 5, the declared lifecycle path | IN BOUNDS |

Per-commit containment (no touch-and-revert): `git log --name-only main..HEAD` shows
- `abef119` — the three directive files only;
- `1bb811e` — `tasks/M0-T027.json` only;
- `3ed05fd` — evidence map, producer report, state.json, packet.
No intermediate commit touched any other path. **CONFIRMED.**

Specific confirmations requested:
- **`project-control/tasks/M0-T025.json` unmodified**: absent from the branch diff; its last touching commit is `0fcdc68` (M0-T024 consolidation), long before this branch; status still `backlog`. **CONFIRMED.**
- **No `tools/**`, `.claude/hooks/**`, `.claude/agents/**`, `.claude/rules/**`, or settings change**: `git diff --name-only 208c939 HEAD -- tools/ .claude/` returns nothing; `git status --porcelain tools/` is empty. **CONFIRMED.**
- **No `effort` / `effortLevel` key anywhere**: `git diff main...HEAD | grep -i effort` returns 8 hits, and I read every one — all are prose recording the *prohibition* (e.g. `"NOT AUTHORIZED under this GO: any effort key or effort setting."`, the AS-9 scenario text, the producer report's confirmation). **No JSON/settings key named `effort` or `effortLevel` is added or changed, and no settings file is in the diff at all.** CONFIRMED.
- **No product file under `services/**`, `apps/**`, `packages/**`**: none in the diff. CONFIRMED.
- **No other task's packet or report changed**: the only task packet in the diff is M0-T027's; the only reports are M0-T027's own two. CONFIRMED.

Append-only integrity of the directive capture (I checked this because "capture path" is not a licence to rewrite history):
```
git diff main...HEAD -- .../requirements.json | grep -E "^-"
--- a/project-control/directives/D-004-agent-teams-runtime-adoption/requirements.json
-  "requirement_count": 420,
-    "source-011-amendment.md"
```
Exactly two deleted content lines, whose replacements are `"requirement_count": 516,` and `"source-011-amendment.md",` + `"source-012-amendment.md"`. **No requirement row was edited, deleted, or renumbered** — every other change in a 3735-line diff is a pure insertion. Live counts: `grep -c '"id": "D-004-R'` = 516 rows against a declared `requirement_count` of 516; new rows R421..R516 = 96. `source-012-amendment.md` is 280 insertions / 0 deletions (new file). The producer report is 236 insertions / 0 deletions — **append-only, sections 1-12 byte-preserved as claimed**, verified at the diff level rather than from the narrative.

Independent validator run:
```
python tools/validate_directive_compliance.py
directive registry OK: 5 directive(s), 5 active; source hashes, ID append-only, and producer/verifier separation verified.
VALIDATOR_EXIT=0
```

---

## CHECK 7 — OWNER HOLDS AND UNAUTHORIZED LANES

- **Expansion hold** (`.claude/rules/expansion-agent-dispatch-hold.md`): file is not in the branch diff and not modified in the working tree; `.claude/` is byte-identical to the post-#133 merge point. No expansion task, contract, or GDS proposal was created; `master_plan.json` is untouched (absent from the diff, clean in `git status`). **CONFIRMED — hold intact, not released, not violated.**
- **D-004 manifest `prohibits` list** (manifest.json lines 178-210): I read all 32 entries. The operative ones for this work:
  - "touching M0-T025 in any way" — CONFIRMED respected (unmodified, still `backlog`).
  - "writing an effort key anywhere, ever" — CONFIRMED respected.
  - "spawning any teammate without an explicit model value" — outside my observation; I can attest only that my own spawn carried an explicit model (Opus 5) and that I was instructed to run `/run-quality-gate`-class verification read-only. INDETERMINATE for other spawns.
  - "advancing M0-T027 past blocked, or accepting it, before the on-policy re-run passes" (from amendment 4) — the precondition is satisfied: the on-policy fresh-session re-run landed under M0-T028, `B-015` is `resolved`, and M0-T028 is `accepted`. The later, more specific owner GO (source-012 Phase 4 item 1) expressly directs the unblock. **CONFIRMED — no live prohibition was breached by the transition.**
  - "M0-T032, another producer wave, predicate-schema follow-ups, or product/legal-rule changes under the closeout GO" — CONFIRMED respected; M0-T032 remains `backlog` and untouched.
  - "producing any tracked file outside a contracted task's allowed_paths" — see **O-1**.
- **Step 5 / M0-T029**: `ls project-control/tasks/M0-T029.json` -> `No such file or directory`. Task-file count is 76 with no new packet on this branch. **CONFIRMED — no M0-T029 created, no Step-5 work begun.**
- **M0-T032, M0-T025**: both `backlog`, both untouched. **CONFIRMED.**
- **`accept()`, D-001, and directive-resolution behavior unchanged** (source-012 line 248): no `tools/` change at all. **CONFIRMED.**

---

## CHECK 8 — LEDGER TOTALS

`project-control/state.json` at HEAD+worktree: `last_checkpoint: "CP-0035"`, `accepted_tasks` length **53**, `blocked_tasks` = `["M0-T007","M0-T008"]`, `failed_gates` = `[]`, `current_milestone: "M4"`.

I recomputed every roster from the 76 task packets using the exact `sync_state()` rules (tools/project_control.py:250-265) and compared:
```
accepted recomputed 53   state 53   match True
active match True   ['M0-T019','M0-T021','M0-T027','M4-T001','M4-T002','M4-T003','M4-T004','M4-T005','M4-T006','M5-T001']
blocked match True  ['M0-T007','M0-T008']
failed_gates match True []
last_checkpoint CP-0035
backlog: M0-T025, M0-T026, M0-T032, M2-T014, M2-T015, M2-T016, M3-T002..M3-T005, M6-T001  (11)
```
Every field is exactly what `sync_state()` derives from the task files — **no drift, no hand-authored entry**, and M0-T027 correctly appears in `active_tasks` as a consequence of the transition. `project-control/checkpoints/CP-0035.json` exists, is well-formed, records `commit 31226481a62170477c0d6973a3d51bd215751505` on `branch main` at `2026-07-30T08:36:54Z`. **CONFIRMED (53 accepted, CP-0035, sync_state-written).**

Note: CP-0035 predates today's M0-T033 acceptance and this branch. That is not staleness in the ledger sense — `state.json` is authoritative and current, and no checkpoint has been claimed for the closeout. Nothing claims a checkpoint that does not exist. **No stale-checkpoint violation.**

Global integrity sweep (beyond the brief, per my standing mandate): for all 53 accepted tasks I checked that every `required_gates` entry has a PASS record and that independent gates are not self-approved. Result: **no accepted task lacks a required PASS record; no independent gate is recorded by its own producer.** Nine accepted tasks carry independent-gate records with `reviewer: "orchestrator"` — see **O-4**; all nine are pre-hardening legacy records.

---

## CHECK 9 — BLOCKERS AND DEPENDENCIES

I scanned all 16 blocker files with the same word-bounded matcher `accept()` uses (`_blocker_references`, line 959-971):
```
B-001 open     refs M0-T027 = False
B-002 resolved_temporary  False
B-003 closed   False
B-004 open     False
B-005..B-009 resolved      False
B-010 open     False
B-011 open     False
B-012 open     False
B-013 open     False
B-014 resolved False
B-015 resolved refs M0-T027 = True
B-016 resolved refs M0-T027 = True
```
- **No OPEN blocker references M0-T027.** The only two that reference it (`B-015`, `B-016`) are both `resolved`, so `accept()`'s blocker scan (lines 1017-1029, which treats `open` or empty status as blocking) adds no reason. **CONFIRMED.**
- **`B-015` is `resolved`.** CONFIRMED (`project-control/blockers/B-015-teammate-readonly-guard-bypass.json`).
- **Dependency `M0-T024` is `accepted`.** CONFIRMED — it is the only entry in `dependencies` and appears in `state.accepted_tasks`.

---

## ADDITIONAL VERIFICATION I PERFORMED (not requested, materially relevant)

**Evidence map, independently re-derived.** The producer claims 233 resolver-derived applicable ids. I ran the canonical resolver myself against the live packet:
```
refs ok: True   reasons: []
applicable count (resolver-derived): 233
evidence map keys: 233   non-empty covered: 233
applicable not covered: []      covered not applicable: 0
```
Exact coverage, no missing ids, no padding. The three totals are correctly kept distinct (128 historical contract-time, 516 current locked D-004 total, 233 applicable to this task). **CONFIRMED.**

**No premature verification.** `project-control/directives/.../verification.json` (schema `directive_verification/v2`) row for M0-T027: `state: pending`, `reviewed_sha: null`, `verifier: directive-compliance-verifier` (!= producer `orchestrator`). The producer has not written its own PASS. **CONFIRMED.** See **O-4** for the forward-looking prerequisite.

**No submit record yet.** `project-control/reports/M0-T027.json` does not exist, consistent with `in_progress` at 80% and with `submit` not having been run. **CONFIRMED.**

---

## OBSERVATIONS

**O-1 (advisory, forward-looking — containment/packet hygiene).** `project-control/reports/M0-T027-evidence-map.json` is modified on this branch but is **not listed in `allowed_paths`**, while D-004 `prohibits` includes "producing any tracked file outside a contracted task's allowed_paths" and AS-9 asserts the containment diff touches only `allowed_paths`. Mitigating facts, all verified: the owner explicitly ordered it (`source-012-amendment.md:199` "Regenerate the M0-T027 evidence map using the canonical resolver"); the CLI *requires* it for any in-regime submit (`_directive_submit_check`, line 437-439); it lives in this task's own report namespace and is not in `forbidden_paths`; and it first entered the repo in `cabf723` on main, so the omission predates this branch. Precedent is inconsistent repo-wide: `M0-T033` **does** list both `project-control/reports/M0-T033-evidence-map.json` and its submit record `project-control/reports/M0-T033.json` in `allowed_paths`; `M0-T028` (accepted) does not list its evidence map. I judge this **not a control-plane integrity violation**, but the acceptance record should not let AS-9 assert something literally untrue. Forward-looking: the upcoming `submit` will create `project-control/reports/M0-T027.json`, also outside `allowed_paths`. Cleanest fix, if the orchestrator judges it in scope: add those two paths to `allowed_paths` (a MATERIAL field — digest moves again, with the same nil control-plane consequence established in CHECK 3), or record the exception explicitly in the acceptance evidence rather than silently.

**O-2 (structural note — G0 is not re-recordable).** Because `producer_agent` is now `orchestrator` and `gate()` line 879-880 refuses an administrative gate where `producer == reviewer`, a *replacement* G0 could not lawfully be recorded today. It is not needed: `accept()` applies the producer-independence test only to `INDEPENDENT_GATES` (lines 995-1005) and tolerates stored records, so the existing `role: administrative` PASS satisfies the requirement. The owner anticipated exactly this at `source-012-amendment.md:149` and asked to be told if a replacement were required — **it is not**. This is the same structural asymmetry the M0-T033 exception addresses for the unblock path, and it remains unaddressed for the administrative-gate path; worth a follow-up task, not a blocker here.

**O-3 (known, owner-deferred — the content manifest carries no content-binding force here).** All five `allowed_paths` entries live under `project-control/`, which `_MANIFEST_EXCLUDE_PREFIXES` excludes (line 311). The frozen identity therefore hashes the empty set: `e3b0c442...` is literally `sha256("")` (I confirmed the equality). Consequence, stated precisely: `accept()`'s staleness test (line 487) compares the submit record's `content_manifest_sha256` to the recomputed identity, and both sides are permanently `e3b0c442...`, so **post-review edits to the producer report or the pilot reports would not be detected by that mechanism**; what remains load-bearing is the `reviewed_sha` stamp (`3ed05fda...`, which I verified against my own `rev-parse`) and the reviewers' own inspection at that SHA. This is the D-001 empty-set behavior the owner explicitly ruled out of scope for this GO ("Do not change accept(), D-001, or directive-resolution behavior under this GO"), and a D-001 empty-set verification row was already recorded at M0-T033 acceptance. Recorded, not charged against this task.

**O-4 (forward-looking prerequisite — acceptance is currently impossible, fail-closed).** The D-004 `verification.json` row for M0-T027 lists **97** applicable requirement ids and 97 requirement rows, while the resolver now derives **233**. `_directive_accept_reasons` (line 503) calls `task_unresolved_requirements` with the resolver-derived set, and that function fails closed on missing rows ("Missing, duplicate, extra, cross-task, or stale rows FAIL CLOSED"). So `accept()` will refuse M0-T027 until the **independent** directive-compliance-verifier records all 233 at the frozen identity. That is correct behavior and no one has tried to short-circuit it; I flag it so it is not discovered at the last step. (Separately, in the global sweep: nine accepted tasks — M0-T001/T002/T003 G3, M0-T009/T012 G4, M1-T002/T005/T006 G4, M2-T001 G4 — carry independent-gate records with `reviewer: "orchestrator"`. All nine have **no `role` field** and `reviewed_at` timestamps between 2026-07-14T21:34Z and 2026-07-17T07:39Z, i.e. all before the write-time hardening at 2026-07-17T16:12Z. They are the documented pre-hardening legacy records that `accept()` deliberately tolerates, not new self-approvals, and none belongs to M0-T027.)

**O-5 (hygiene risk for the next commit).** Three untracked, **non-gitignored** items sit in the working tree: `.npmrc`, `.claude/CODEX_CLAUDE_SUPERVISOR_BUILD_DIRECTIVE_v4 (1).md` (inside the governed `.claude/` tree), and ~30 `.claude/agent-memory/**` files. A broad `git add -A` while committing the G2 lifecycle deltas would sweep them into the closeout PR and breach containment. `.claude/rules/project-control.md` already forbids broad `git add`; stage the three lifecycle paths explicitly.

---

## WHAT I COULD NOT VERIFY (INDETERMINATE)

1. **Absolute proof the lifecycle files were CLI-written.** The CLI leaves no cryptographic signature. My conclusion rests on log-entry shape, sub-100 ms write clustering, and exact `sync_state()` roster agreement — strong and mutually corroborating, but not proof.
2. **Model tier of other agents in this session.** I can attest only to my own: Opus 5. Whether the G3/G5 reviewers were spawned with an explicit Opus 5 value (D-004-R307 / source-012 line 218) is not observable from the repository.
3. **Whether reviewer returns are preserved verbatim.** No G3/G5 record exists yet, so there is nothing to compare; that check belongs to the gate that records them.
4. **GitHub-side facts** (PR state, branch protection, CI at the PR head). No PR exists for this branch yet, and I did not query GitHub.
5. **Substantive correctness of the 233 evidence-map pointers.** I verified coverage and derivation, not that each cited artifact actually proves its requirement — that is the directive-compliance verifier's gate.

---

## VERDICT

**PASS.**

Every lifecycle transition in M0-T027's history is legal, machine-recorded, and correctly ordered; the `blocked -> in_progress` unblock was admitted by the general M0-T033 shape rule and would have been admitted **without** the roster correction, so no gate was manufactured; the roster correction is exactly one non-material addition with producer, gates, and every prior reviewer identity unchanged; the material-digest movement has no reachable control-plane consequence and the producer's reasoning survives independent code-path verification; the historical G0 record is byte-identical and single-origin, and the new G2 is a properly classified `self_check` stamped with the correct SHA; no independent gate has been recorded, no reviewer equals the producer, and the reserved identity remains barred from independent gates; the changed-file set is confined to this task's own artifacts plus orchestrator D-001 capture paths, with one unenumerated-but-owner-ordered evidence-map path recorded as O-1; every owner hold is intact and no unauthorized lane began; ledger totals are exactly what `sync_state()` derives (53 accepted, CP-0035); and no open blocker touches the task while its sole dependency is accepted.

No self-approval, no missing gate, no out-of-order transition, no stale checkpoint, and no held/dispatched conflict was found. O-1 and O-4 should be resolved before acceptance; O-2, O-3, and O-5 are recorded for the orchestrator's judgement.
