# M0-T078 — Producer report (engineering-reliability standard + skill router)

**Producer:** worker agent (NOT authorized to accept, gate, commit, push, or run the control CLI).
**Status requested:** `awaiting_gate` — evidence submitted for independent G2/G3/G5.
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t078` — branch
`task/M0-T078-reliability-standard`, base HEAD `6b9ae32f7afdd30b015fc1fc706293fb358b2b32`.
**Directive regime:** D-023 (`directive_refs: ALL`); the deliverable requirement is **D-023-R015**.

Nothing here is accepted. No git, `gh`, or `tools/project_control.py` mutation was performed by this
producer; the four working-tree changes below are left uncommitted for the orchestrator.

---

## 1. What was created

| Path | State | Lines |
|---|---|---|
| `docs/ENGINEERING_RELIABILITY_STANDARD.md` | new | 284 |
| `.claude/skills/engineering-reliability/SKILL.md` | new | 38 |
| `CLAUDE.md` | modified (+2 / −1) | 116 |
| `AGENTS.md` | modified (+3 / −1) | 91 |
| `project-control/reports/M0-T078-producer-report.md` | new (this file) | — |

`git status --porcelain` at submission:

```
 M AGENTS.md
 M CLAUDE.md
?? .claude/skills/engineering-reliability/
?? docs/ENGINEERING_RELIABILITY_STANDARD.md
```

Every path is inside the packet's `allowed_paths`. No `forbidden_paths` entry was read for writing or
modified: `.claude/ORCHESTRATION_POLICY.md`, `.claude/hooks/**`, `.claude/settings.json`, `apps/**`,
`packages/**`, `services/**`, `supabase/**`, `project-control/tasks/**`,
`project-control/directives/D-001-*`, and the four protected `tools/*.py` files are untouched.

**Standard structure** — a trigger matrix, a non-duplication map (§0), and the ten vetted principle
areas as §1–§10: debugging discipline; smallest fitting change; behavior proof; async flows;
idempotency; retries; errors; verification contexts; triage; measured claims only.

**Skill** — one file, no scripts, no assets, no sub-directories. Frontmatter `description` names the
five invocation triggers explicitly (behavior change; debugging a defect/flake/incident; async /
concurrent / network / background-job flow; retry-replay-resume-idempotency surface; before claiming
completion or an improvement) so it discriminates rather than matching every task. The body is a
routing table into the standard's sections plus rules of engagement — it restates no rule.

## 2. Non-duplication comparison (the required judgment)

I read `CLAUDE.md`, `.claude/ORCHESTRATION_POLICY.md`, `docs/GATES_AND_CHECKPOINTS.md`,
`docs/ACCEPTANCE_SCENARIO_STANDARD.md`, `docs/CODE_MODULARITY_POLICY.md`,
`docs/DEPENDENCY_SECURITY_POLICY.md`, `docs/LEAN_OPERATING_PROCESS.md`,
`docs/PROJECT_CONTROL_PROTOCOL.md`, `AGENTS.md`, and the path-scoped `.claude/rules/backend-api.md`,
`.claude/rules/frontend-web.md`, and `.claude/rules/code-architecture.md` before writing.

| # | Principle area | Already covered? | What the standard does |
|---|---|---|---|
| 1 | Debugging discipline | **No.** Nothing in the repo states a debugging method. The gates govern *who* verifies, not *how* to diagnose. | Written out in full (§1). New content. |
| 2 | Smallest fitting change | **Partly.** `docs/CODE_MODULARITY_POLICY.md` §2 (responsibility ownership before growing a file), §6 (facade-preserving splits), §11 (no over-fragmentation); `docs/LEAN_OPERATING_PROCESS.md` return item 6 B3/B8 (no framework/DSL; abstraction only for real repetition); G4 forbids duplicate implementations. | §2 **references** all of the above and adds only what is absent: the fix-at-the-owning-boundary rule, the ordered escalation of change size, the no-silent-scope-widening rule, and deletion-as-behavior-change. |
| 3 | Behavior proof | **Partly.** `CLAUDE.md` principle 8 and `docs/ACCEPTANCE_SCENARIO_STANDARD.md` mandate executable acceptance examples, the universal minimum set (incl. a regression case), and the evidence standard; G2 is the producer self-check. | §3 **references** the scenario standard for coverage/shape/evidence and adds only the two missing obligations: red-observed-before-green, and mutation-or-revert proof for critical-class regressions. Also adds prove-behavior-not-implementation, the no-weakening rule, and flake-is-a-defect. |
| 4 | Async flows | **No design rules.** `docs/ACCEPTANCE_SCENARIO_STANDARD.md` requires a dependency-failure/timeout *scenario*; `.claude/rules/backend-api.md` states jobs are "cancellable"; `.claude/rules/frontend-web.md` has no async-state rule. Those state the *requirement*, never the mechanics. | §4 written out in full: four explicit states, operation identity over booleans, supersession policy decided up front, cancellation on supersession, stale-response discard, semantic deduplication. **References** `.claude/rules/backend-api.md` as the job-level requirement §4–§6 satisfy. |
| 5 | Idempotency | **Named, never designed.** G4 checks "job idempotency/retry behavior where relevant"; the scenario standard requires a retry/idempotency scenario; `.claude/rules/backend-api.md` says jobs are idempotent. No document says how. | §5 written out in full: caller/operation/payload key binding, atomic claim, same-response-and-identity replay, record-before-act, bounded key lifecycle with same-key-different-payload conflict, crash reconciliation, retry-safety as a property of the effect. **References** G4 and the scenario standard as where it is verified. |
| 6 | Retries | **No.** Retries are mentioned as something the deterministic backend controls and as a job property; no rule constrains them. | §6 written out in full: transient-only classification, bounded attempts *and* elapsed time, exponential backoff with jitter, `Retry-After` precedence, exactly one retry layer, reconcile-before-retrying-an-ambiguous-effect, and loud terminal failure. |
| 7 | Errors | **Partly.** `docs/LEAN_OPERATING_PROCESS.md` return item 6 B5 defines the typed-error *shape* (stable code + concise message + structured metadata); G5 requires sensitive-log redaction; `docs/SECRETS_POLICY.md` §3 governs secret handling; `AGENTS.md` gives the `unknown`-not-zero rule. | §7 **references** B5 for the shape, G5 + `SECRETS_POLICY.md` for redaction, and `AGENTS.md` for `unknown`. Adds only: the two-audience split, correlation IDs on both sides, no raw-upstream pass-through, cause-chaining to preserve the diagnosis, and log-once-at-the-handling-boundary. |
| 8 | Verification contexts | **Substantially covered.** G3 already requires a clean environment/isolated worktree, real-user workflow, normal/boundary/missing/failure cases, and reviewer independence; G4 covers integration, contracts, and migrations both ways; `.claude/ORCHESTRATION_POLICY.md` §D fixes the frozen reviewed SHA and invalidation on a new commit; `CLAUDE.md` principle 7 bars self-completion. | §8 is the **most reference-heavy section by design** — it cites G3, G4, §D, and `CLAUDE.md` principle 7 rather than restating them, and adds only the four contexts nothing covers: applicable platforms (Windows PC vs Render Linux vs CI), concurrency, unsafe/adversarial paths, and stale state / upgrade paths. |
| 9 | Triage | **No vocabulary exists.** G3 issues PASS/FAIL/BLOCKED and `docs/templates/GATE_REPORT.md` has an unstructured "Defects" section; G7 mentions "no open critical/high defects" without defining the scale. | §9 written out: a three-tier must-fix / important / minor table with effects, cosmetics explicitly non-blocking, severity-with-a-reason, one-finding-per-row. **References** `docs/PROJECT_CONTROL_PROTOCOL.md` and the gates to make clear severity changes no authority. |
| 10 | Measured claims only | **Partly.** D-023-R023 is the standing prohibition; `docs/LEAN_OPERATING_PROCESS.md` states line-count reduction is never an acceptance criterion; `docs/CONTEXT_PIPELINE_RUNBOOK.md` (M0-T076) is an existing frozen-baseline precedent. | §10 **references** D-023-R023, the LEAN header rule, and the M0-T076 frozen baseline as the mechanics precedent. Adds only the definition of a frozen benchmark's required contents, honest-comparison reporting, scope limitation, the failure-data rule for reliability claims, and the describe-the-change fallback. |

**Net:** four areas (1, 4, 5, 6) were genuinely uncovered and are written out; three (2, 3, 7) are
partly covered and only their gaps are added; two (8, 9) are largely or wholly reference-and-extend;
one (10) is a standing prohibition given engineering mechanics. §0 of the standard is the explicit
citation map, and both new files instruct the reader to follow a citation rather than restate a rule.

**Cited-path integrity.** Every repository path cited across the two new files resolves, and every
cited *section anchor* exists (14 paths, 11 anchors — evidence in AS-3 below).

## 3. Discovery-pointer decision (deliverable 3)

I added a pointer in **both** files, each one line, after checking whether existing discovery would
surface the standard:

- **`AGENTS.md` — genuinely required.** Codex reviewers have no skills mechanism; the file's
  "On-demand routing" prose is their only routing surface, and it did not name the standard. Without
  the pointer a Codex reviewer could not find it. Added as one clause in the existing sentence (the
  section is prose, not a table, so a clause is the concise form there).
- **`CLAUDE.md` — added for table truthfulness.** Claude Code auto-discovers the skill from its
  frontmatter, so the skill would surface without a row. But the skills table is introduced as "The
  **five** standard workflows" and enumerates them; leaving a sixth skill out makes the enumeration
  false. Added one row, and changed "The five standard workflows" to "The standard workflows" (one
  word removed, so the count never drifts again). Total CLAUDE.md diff: +2 / −1.

The context-budget check was re-run after the edit and still passes (§4, AS-2): eager total moved
from ~2,925 to ~2,956 estimated tokens against a 6,000-token budget — a 31-token increase. No removal
was necessary.

## 4. Acceptance scenarios and evidence

Per `docs/ACCEPTANCE_SCENARIO_STANDARD.md`. This is a documentation/skill task, so the universal
minimum set is mapped to the artifacts' failure modes (a routing document's "dependency failure" is a
broken citation; its "idempotency case" is repeat validator execution). All scenarios were executed in
the worktree at base HEAD `6b9ae32`; all passed. Cleanup is uniform: every scenario is read-only over
the working tree — no scenario writes, installs, or deletes anything, so no reset step is required.

### AS-1 — Primary success: both deliverables exist with the required structure

- **Requirement:** D-023-R015; packet objective.
- **Preconditions:** worktree at `6b9ae32`, both files written.
- **Input:** `wc -l docs/ENGINEERING_RELIABILITY_STANDARD.md .claude/skills/engineering-reliability/SKILL.md` and `grep -n "^## " docs/ENGINEERING_RELIABILITY_STANDARD.md`.
- **Expected:** standard < 350 lines with a trigger matrix, a §0 map, and §1–§10; skill < 60 lines.
- **Actual:** standard **284** lines; skill **38** lines; 12 `##` sections — trigger matrix, §0, and §1–§10 in order (`Debugging discipline`, `Smallest fitting change`, `Behavior proof`, `Async flows`, `Idempotency`, `Retries`, `Errors`, `Verification contexts`, `Triage`, `Measured claims only`). **PASS.**
- **Invariant:** all ten vetted areas present; no eleventh principle introduced.
- **Evidence:** this report §1 and §4 AS-1.

### AS-2 — Boundary: the eager context budget after the CLAUDE.md addition

- **Requirement:** packet acceptance method ("context-budget validator remains green"); deliverable 3.
- **Preconditions:** CLAUDE.md row + wording change applied.
- **Input:** `python tools/context_budget_check.py` (worktree root).
- **Expected:** exit 0, `PASS`, eager total below the 6,000-token budget.
- **Actual — full output:**

```
# Context-budget check

## Eager (auto-loaded) project instructions
    10147B   116L  ~ 2498 tok  CLAUDE.md
     1868B    31L  ~  458 tok  .claude/rules/expansion-agent-dispatch-hold.md
  ---- eager total: 12015B  147L  ~2956 tok  (budget 6000 tok)

## Session handoff
  ~1486 tok  docs/SESSION_HANDOFF.md  (budget 4000 tok)

## Historical markers on known stale status docs
  OK   docs/IMPLEMENTATION_STATUS.md
  OK   docs/MASTER_EXECUTION_PLAN.md
  OK   CONTINUE_FROM_CURRENT_STATE_PROMPT.md

## Retired/superseded sections in unconditional rules
  OK - none (no retired/superseded section in an unconditional rule)

## Duplicate current-status task boards
  docs/GENERATIVE_STRATEGY_INTEGRATION_PLAN.md: allowlisted
  docs/LEGAL_CORPUS_COVERAGE_MATRIX.md: allowlisted
  docs/MASTER_EXECUTION_PLAN.md: HISTORICAL-labelled

## Result
PASS - automatic context budget within limits; no stale/duplicate/retired regressions.
CONTEXT_BUDGET_EXIT=0
```

- **Boundary value:** 2,956 of 6,000 tokens (49%); the addition cost 31 tokens against the pre-change
  2,925. Margin to the budget: 3,044 tokens. **PASS** — the CLAUDE.md addition is kept.
- **Evidence:** output above.

### AS-3 — Missing/null input: every citation resolves (a routing doc's null-reference failure)

- **Requirement:** non-duplication by reference — a citation that does not resolve silently converts a reference into a missing rule.
- **Input:** extract every backticked `*.md` / `*.py` / `*.json` path from both new files, test each with `[ -e ]`; separately `grep` each cited section anchor in its target file.
- **Expected:** zero MISSING.
- **Actual:** **14/14 paths OK** — `.claude/ORCHESTRATION_POLICY.md`, `.claude/rules/backend-api.md`, `.claude/rules/code-architecture.md`, `AGENTS.md`, `CLAUDE.md`, `docs/ACCEPTANCE_SCENARIO_STANDARD.md`, `docs/CODE_MODULARITY_POLICY.md`, `docs/CONTEXT_PIPELINE_RUNBOOK.md`, `docs/DEPENDENCY_SECURITY_POLICY.md`, `docs/ENGINEERING_RELIABILITY_STANDARD.md`, `docs/GATES_AND_CHECKPOINTS.md`, `docs/LEAN_OPERATING_PROCESS.md`, `docs/PROJECT_CONTROL_PROTOCOL.md`, `docs/SECRETS_POLICY.md`. **11/11 anchors OK** — ORCHESTRATION §D and §G; GATES "Reviewer independence"; MODULARITY §2, §6, §11; LEAN "Return item 6" and "Return item 8"; SECRETS §3; CONTEXT_PIPELINE_RUNBOOK "M0-T076"; backend-api jobs line. **PASS.**

### AS-4 — Ambiguous/conflicting input: precedence when the standard conflicts with existing policy

- **Requirement:** the standard must not become a competing authority (`CLAUDE.md`; ADR-005/006).
- **Input:** `grep -n "does not override\|confers no authority\|not authority\|never accepts a task"` over both new files.
- **Expected:** an explicit subordination clause in each file; no clause granting acceptance, waiver, merge, or hold-release power.
- **Actual:** standard line 8 ("Engineering guidance only. It does not override `CLAUDE.md`, the gates…") and line 10 ("on conflict those win. It confers no authority to accept a task, waive a gate, merge, or release a hold"); skill line 26 ("The standard is engineering guidance, not authority… never accepts a task, waives a gate, authorizes a merge, or releases a hold"). No authority-granting language found. **PASS.**
- **Invariant:** on conflict, `CLAUDE.md` / gates / `PROJECT_CONTROL_PROTOCOL.md` / ADR-005/006 / an active owner hold win.

### AS-5 — Dependency failure: the skill has no runtime dependency to fail

- **Requirement:** packet — "no scripts, downloaded assets, replacement agent roster, or new framework".
- **Input:** `find .claude/skills/engineering-reliability -type f`, then the same excluding `SKILL.md`.
- **Expected:** exactly one file; zero non-`SKILL.md` files.
- **Actual:** `.claude/skills/engineering-reliability/SKILL.md` only; non-SKILL.md count = **0**. No script, asset, hook, agent definition, dependency, or network call is introduced, so the router cannot fail on an unavailable dependency. **PASS.**

### AS-6 — Retry/idempotency: repeated validation is idempotent and non-mutating

- **Requirement:** acceptance evidence must be reproducible (`docs/ACCEPTANCE_SCENARIO_STANDARD.md`, evidence standard).
- **Input:** SHA-256 the four touched files; run `context_budget_check.py` twice and `validate_mcp_policy.py` twice; re-hash.
- **Expected:** run 1 output == run 2 output for both validators; digests unchanged.
- **Actual:** `OK context_budget_check run1 == run2`; `OK validate_mcp_policy run1 == run2`; `OK no file mutated by validators`. Digests at submission:

```
4e1e2f592ec9e898f7b588a752dab353d9c0b434a3cf4e4f43a23a35bf12ffc7  CLAUDE.md
53c64fa6d29c2666cbb5a6a76bee0f56d2a08acdda8738ee3daadcda2995dd4c  .claude/skills/engineering-reliability/SKILL.md
aedf17fa9b2547fcbeb5c2868ff83e17646a5b3b89e2b681afc9d0392d2cca23  docs/ENGINEERING_RELIABILITY_STANDARD.md
d81723833633e2451ef31265bd06c3f0ef8975335f6185675acabb78dc02bfb4  AGENTS.md
```

**PASS.** A reviewer re-running either validator at these digests must observe identical output.

### AS-7 — Security/isolation: scope containment and no third-party code

- **Requirement:** D-023-R005, D-023-R006, D-023-R038 (no third-party framework, no copied executable code, no Superpowers/secondsky/wshobson); packet `forbidden_paths`; ADR-005 producer confinement.
- **Input:** `git status --porcelain`; `git diff --stat`; `grep -rniE "superpowers|secondsky|wshobson"` over the new and changed files; `find` for added executables.
- **Expected:** changes confined to `allowed_paths`; zero third-party name hits; zero added executables.
- **Actual:** four changed paths, all in `allowed_paths` (§1); `git diff --stat` = `2 files changed, 5 insertions(+), 2 deletions(-)` for the two pre-existing files; third-party name hits = **0** in both new files; added executables/assets = **0**. No forbidden path modified. No `git commit`, `git push`, `gh`, or `tools/project_control.py` command was run. **PASS.**

### AS-8 — Regression: existing discovery and validators still behave as before

- **Requirement:** the packet may not degrade existing routing or policy validation.
- **Input:** print the CLAUDE.md skills table; `git diff -U1 CLAUDE.md AGENTS.md`; `python tools/validate_mcp_policy.py`.
- **Expected:** all five pre-existing skill rows byte-identical; the AGENTS.md routing sentence otherwise unchanged; MCP policy still intact.
- **Actual:** the five prior rows (`/replan-project` + `/status-board`, `/start-controlled-task` + `/submit-checkpoint`, `/run-quality-gate` + `/human-walkthrough`, `/dependency-security`, `/orchestration`) are unchanged and the new row is appended sixth; the AGENTS.md diff touches only the tail of the routing sentence; `validate_mcp_policy.py` output:

```
MCP default-deny policy intact: claude.ai connectors disabled, empty allowlist, audited identifiers denied, .mcp.json servers rejected, auto-approval off, pre-existing settings preserved.
MCP_POLICY_EXIT=0
```

**PASS.**

### AS-9 — Prohibition regression: no unmeasured improvement claim was introduced

- **Requirement:** D-023-R023; the packet's explicit instruction that the standard must not claim it changes defect rate, speed, token use, or cost.
- **Input:** `grep -nEi "faster|cheaper|fewer token|defect rate|token use|speed|cost|improvement"` over both new files, then read each hit in context.
- **Expected:** every occurrence sits inside a trigger description, a prohibition, or a disclaimer — never an assertion.
- **Actual:** 10 occurrences. Standard lines 26 and 45 and skill line 18 are trigger/route descriptions; line 250 is the word "costly" in the §9 severity table; lines 265, 275, 281 are §10 prohibitions; lines 283–284 and skill line 38 are the explicit self-disclaimer ("This standard makes no claim about its own effect on defect rate, delivery speed, token use, or cost. It states required practice; it is not evidence of an outcome."). **No affirmative improvement claim exists in either file. PASS.**

## 5. Validator outputs at submission (required by the packet)

| Command | Exit | Result |
|---|---|---|
| `python tools/context_budget_check.py` | 0 | `PASS - automatic context budget within limits; no stale/duplicate/retired regressions.` (eager 2,956 / 6,000 tok) |
| `python tools/validate_mcp_policy.py` | 0 | `MCP default-deny policy intact: …` |

Full outputs are reproduced verbatim in AS-2 and AS-8.

## 6. Explicit confirmations

- **No third-party code was copied, vendored, downloaded, installed, or executed.** Superpowers,
  secondsky, wshobson, and every other community agent/plugin pack were not fetched, read, or
  referenced. Both files were written from scratch against the repository's own documents. Zero
  network access was used. Zero new dependencies, scripts, hooks, agent definitions, or assets were
  added, and the agent roster is unchanged (D-023-R004, R005, R006, R038).
- **No performance, reliability, cost, speed, or token claim is made** — for the standard, the skill,
  or this task. §10.8 disclaims it inside the standard itself, and AS-9 audits it mechanically
  (D-023-R023).
- **No authority was exercised or asserted.** No commit, push, PR, merge, gate record, ledger write,
  task-status change, or hold release. The standard and skill both subordinate themselves explicitly
  to `CLAUDE.md`, the gates, `docs/PROJECT_CONTROL_PROTOCOL.md`, ADR-005/006, and any active owner
  hold (AS-4).
- **No production behavior changed.** This packet is documentation and routing only; no `services/`,
  `apps/`, `packages/`, `supabase/`, or `tools/` file was modified.

## 7. Judgment calls for the reviewer to check

1. **A CLAUDE.md row was added even though skill auto-discovery would surface the router.** The
   packet said to add a pointer only if discovery would otherwise fail. Strictly, Claude Code would
   find the skill from its frontmatter. I added the row anyway because the table's own preamble
   asserted a count ("The five standard workflows") that a sixth skill falsifies. Cost: 31 eager
   tokens, budget still at 49%. If the reviewer prefers the stricter reading, deleting the row and
   restoring the word "five" is a self-contained two-line revert; the AGENTS.md pointer should stay
   regardless, since Codex has no skills mechanism.
2. **§8 is deliberately the thinnest section**, because G3/G4/§D already own most of the
   verification-context rules. It adds only platforms, concurrency, unsafe paths, and stale state.
   A reviewer wanting a fuller checklist should confirm the missing items are not already in the
   gates before asking for them.
3. **The AGENTS.md pointer is a prose clause, not a table row**, because that file's routing section
   is a sentence. The packet asked for "ONE table row each"; there is no table there to add to.
4. **The trigger matrix is duplicated between the standard and the skill.** This is intentional —
   the skill's copy is the routing surface (its whole purpose), the standard's copy orients a direct
   reader. It is the one intentional repetition; everything else is a citation.
5. **Mutation proof (§3.4) is scoped to critical-class defects only** (security, tenancy, legal-rule,
   provenance, money, data-loss) rather than all changes, to keep the obligation affordable. A
   reviewer may judge that scope too narrow or too broad.
