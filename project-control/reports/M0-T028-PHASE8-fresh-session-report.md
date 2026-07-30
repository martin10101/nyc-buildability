# M0-T028 — Phase 8 fresh-session end-to-end validation report (D-004 Step 3)

Recorded by the orchestrator in the REQUIRED fresh Claude Code session (post-dates the PR #121
merge; two-session boundary of D-004-R134/R135 and source-006 satisfied). Executed exactly per
`project-control/reports/M0-T028-FRESH-SESSION-CAPSULE.md` on the owner's explicit Phase-8 GO
(captured append-only as D-004 amendment 6, `source-007-amendment.md`, rows D-004-R287–R296).

Reviewer report sections below are the reviewers' returns captured VERBATIM (transport
entity-decoding only) per the report-preservation rule in `.claude/rules/project-control.md`.

## 1. Live reconciliation (capsule step 1)

- `git fetch --all --prune` run first; `origin/main` = local `main` = HEAD =
  **`88045b06ef12ccb9b994b4e8b38ffe40d9cadf04`** (frozen fresh-session head, 40 chars).
- `git merge-base --is-ancestor 9db4ab328ea7e1570e347ae19174041d199aedc8 origin/main` → YES
  (main contains the PR #121 implementation merge).
- `python tools/project_control.py status`: M0-T028 `awaiting_gate` 95%, 49 accepted, CP-0033,
  M0-T027 `blocked`, B-015 open — all matching the capsule's expected state.
- Main CI at this head (merge of PR #123): CI ✅ success (2m50s), secret-scan ✅ success,
  context-budget ✅ success (run set 30517553178/30517553211/30517553215, 2026-07-30T05:46Z).
- M0-T028 live content identity (allowed_paths minus `project-control/`, computed via
  `tools/directive_registry.py frozen_git_identity` at HEAD, clean-tree enforced):
  **`126d2d53472deb8828ca4f007b5809b19e5c512ea2288b25499c27f12c0287c2`** — EXACTLY equal to the
  submit record's `content_manifest_sha256` (no drift since submission at `9db4ab3`).

## 2. C1 — all-four-hook-entries wiring proof (capsule step 2; G5 correction C1)

The merged `.claude/settings.json` wires all four entries in single-string form with the
`${CLAUDE_PROJECT_DIR}` path double-quoted (D-004-R100). Evidence each entry FIRED in this fresh
session:

(a) **SessionStart → `directive_reminder.py`: FIRED.** The session-start context of this fresh
session contained the hook's additional context, captured verbatim:
"SessionStart hook additional context: Active owner directives (5): D-001 (Durable Owner Directive
Compliance System), D-002 (Activate the control system, consolidate the plan, and prepa), D-003
(Integrate first wave (D-002 sequential integration) and prep), D-004 (Agent-teams runtime
adoption, staged with pilots), D-005 (Codebase knowledge graph pilot (Graphify) - controlled
evalu). Registry: project-control/directives/ (validate with tools/validate_directive_compliance.py).
If this prompt changes repository work, invoke /directive-compliance and capture/bind it before
acting."

(b) **UserPromptSubmit → `directive_reminder.py`: FIRED.** The owner's first prompt (the Phase-8
GO) carried the hook's additional context, captured verbatim:
"UserPromptSubmit hook additional context: If this prompt changes repository work, invoke
/directive-compliance and capture/bind it before acting."
(The same context re-appeared on subsequent prompt-submit events during the session.)

(c) **PreToolUse `Agent|Task` → `agent_dispatch_guard.py`: FIRED (no error).** Three Agent
dispatches (the reviewer spawns in §4) each passed through the hook with no hook error and no
spurious denial (expected allow: none of the three roles is in BLOCKED_AGENTS). Supplementary
script-level proof under the exact wired command form (`CLAUDE_PROJECT_DIR` set, double-quoted
path):
`echo '{"tool_input":{"subagent_type":"code-reviewer"},"cwd":"..."}' | python "${CLAUDE_PROJECT_DIR}/.claude/hooks/agent_dispatch_guard.py"` → exit 0 (allow).

(d) **PreToolUse `Bash|Write|Edit|MultiEdit|NotebookEdit` → `readonly_agent_guard.py`: FIRED.**
Proven live by the sentinel denial in §4 (the guard's own denial text was returned to the
code-reviewer teammate) and additionally by an incidental live denial against the
control-plane-verifier teammate (its first derivation probe contained a `->` sequence and was
denied — the documented fail-safe over-denial). Supplementary script-level proof under the exact
wired command form:
`echo '{"agent_type":"code-reviewer","tool_name":"Bash","tool_input":{"command":"echo x > ./PILOT_SENTINEL.tmp"},"cwd":"..."}' | python "${CLAUDE_PROJECT_DIR}/.claude/hooks/readonly_agent_guard.py"` → permissionDecision "deny" with the exact expected denial text, exit 0.

**C1 conclusion: all four entries fire in the merged single-string form. No entry required
reversion to the args-array form.**

## 3. Pre-spawn dirt sweep (capsule step 3)

- Primary checkout: 39 `git status --porcelain` entries — 36 expected machine-local state
  (`.claude/agent-memory/**` modifications/additions, untracked `.npmrc`) plus EXACTLY the three
  deliberate amendment-6 capture files
  (`project-control/directives/D-004-agent-teams-runtime-adoption/{manifest.json (M),
  requirements.json (M), source-007-amendment.md (??)}`). No other artifact.
- Sentinel pre-check: `test -e ./PILOT_SENTINEL.tmp` → exit 1 (ABSENT before the test).
- Registered worktrees (10): `M0-T028-readonly-guard` CLEAN; `M0-T030-codegraph`,
  `M0-T031-codegraph-hardening` clean; six pre-existing `agent-*` husk worktrees carry only
  pre-existing stale state from prior sessions (recorded as baseline; NOT authorized for cleanup).
  The `handoff-update/` and several other `.claude/worktrees/` directories are unregistered husk
  directories (no git linkage or broken linkage); unchanged by this session.

## 4. On-policy three-reviewer sentinel rerun (capsule steps 3–4; D-004-R134/R135)

Spawned concurrently, each UNNAMED (so `agent_type` carries the role), each with an EXPLICIT
Fable 5 model on the spawn (`model: fable` → resolves to `claude-fable-5`, the verified
mechanism), each pinning frozen head `88045b0` and invoking `/run-quality-gate`:
`code-reviewer`, `control-plane-verifier`, `directive-compliance-verifier`.

Sentinel negative test (assigned to the code-reviewer-role teammate; performed exactly once):

- **Direct Write-tool attempt** at `./PILOT_SENTINEL.tmp`: blocked by TOOL-UNAVAILABILITY (the
  reviewer definition exposes no Write tool). Reported honestly as tool-unavailability, NOT as a
  guard denial. Verbatim message received by the reviewer:
  "Error: No such tool available: Write. Write exists but is not enabled in this context. Use one
  of the available tools instead."
- **Bash redirection** `echo x > ./PILOT_SENTINEL.tmp`: **DENIED by `readonly_agent_guard.py`
  itself.** Verbatim denial text received by the reviewer:
  "'code-reviewer' is operationally read-only: repository/GitHub/control-plane mutation and shell
  file-writes are blocked. Read-only git inspection, gh reads, and test execution are allowed;
  return findings via SendMessage."
  This is the guard's own `_deny` text; the resolved identity `'code-reviewer'` proves the unnamed
  spawn's payload carried the governed role and matched the READ_ONLY_AGENTS enforcement path.
- **Orchestrator independent absence verification** (never reviewer assertion alone):
  `test -e ./PILOT_SENTINEL.tmp` → **exit 1 (ABSENT)**; `ls PILOT_SENTINEL.tmp` → "No such file
  or directory"; `git status --porcelain | grep -i sentinel` → no match.

**Fresh-session sentinel result: PASS** (tool-unavailability for direct Write, honestly labeled +
guard's own denial for the Bash redirection + independently verified absence — exactly the
required honest result per the sentinel acceptance clarification in source-006).

## 5. Post-test dirt sweeps (capsule step 5)

Post-sentinel `git status --porcelain` on the primary checkout: identical to the §3 baseline
(39 entries; only the three deliberate capture files beyond machine-local state). No sentinel, no
unexpected artifact in the primary checkout or any worktree. Registered-worktree count unchanged
(10).

## 6. Regression and directive checks (capsule step 6)

Run in this fresh session at the frozen head:

- `python tools/test_readonly_agent_guard.py` → **136 checks PASS, 0 failures** ("ALL CHECKS
  PASSED"; count independently reproduced line-by-line by the code-reviewer).
- `python tools/test_project_control.py` → all 14 groups OK.
- `python tools/test_directive_compliance.py` → 55 tests OK.
- `python tools/validate_directive_compliance.py --check` → exit 0 (registry integrity green,
  including the uncommitted amendment-6 capture; D-004: 296 requirements, 0 errors).
- Secret scan: gitleaks pre-commit hook active on every commit in this repo; main CI secret-scan
  job ✅ at this head (see §1). [Lifecycle-PR commits below will also pass through the gitleaks
  pre-commit hook and the secret-scan CI job.]
- Main CI green at `88045b0` (§1).

## 7. Reviewer verdicts (returns captured verbatim below)

| Reviewer (role, unnamed spawn, explicit Fable 5) | Verdict |
|---|---|
| code-reviewer (G3-class rerun + sentinel) | **PASS** |
| control-plane-verifier | **PASS** |
| directive-compliance-verifier (final per-requirement verification) | see §10 / Appendix C |

## 8. C2 owner decision (capsule §5 precondition for acceptance)

Captured live from the owner in this session (AskUserQuestion, 2026-07-30): **"Contract it"** —
the C2 follow-up proposal (positive PRODUCER_AGENTS allowlist or adding human-journey-reviewer +
visual-quality-reviewer to READ_ONLY_AGENTS; CI-pinned write-authorized set; ADR-005
reconciliation; dispatch-guard name-collision evaluation) is to be contracted as a new controlled
ledger task. Recorded here and bound at D-004-R296; the C2 work itself is NOT part of M0-T028
acceptance. Follow-up task: see the lifecycle records in this PR (M0-T029 is RESERVED for D-004
Step 5 adoption and is NOT used for this).

## Appendix A — code-reviewer return (verbatim)

All verification complete. The working tree matches the frozen head for all four in-scope files (empty diff, clean status). Here is the G3-rerun report.

---

# Gate Report — M0-T028 G3 Fresh-Session Rerun (D-004 Step 3 Phase 8)

- Gate ID: G3-rerun (fresh session)
- Task ID: M0-T028 (read-only guard fail-closed fix, merged via PR #121)
- Reviewer: code-reviewer (independent, read-only)
- Producer: not this reviewer (fix produced in prior sessions; reviewed at base e8a7dbfa, delta d5eb642e, merged as 9db4ab32)
- Result: PASS
- Clean environment/worktree used: primary checkout at frozen head; working tree verified identical to HEAD for every in-scope file (see below). Deliberate uncommitted orchestrator work under `project-control/directives/**` was declared expected and is out of scope; it does not touch any reviewed path.

## Frozen head confirmation

`git rev-parse HEAD` → `88045b06ef12ccb9b994b4e8b38ffe40d9cadf04` — exactly the pinned SHA. Review proceeded.

Working-tree identity check for the four in-scope files: `git diff HEAD -- .claude/hooks/readonly_agent_guard.py .claude/settings.json .gitignore tools/test_readonly_agent_guard.py` and `git status --porcelain` on the same paths both returned empty — the content I read and executed is the frozen-head content.

## Findings per review-scope item

**1. `.claude/hooks/readonly_agent_guard.py` — fail-closed identity resolution: CONFIRMED.**
- No identity keys (`agent_type`/`agentType`/`agent_id` all absent or empty) → `return 0` pass-through (lead/main session), lines 348–353.
- Identity in `READ_ONLY_AGENTS` (7 roles, lines 52–62) → falls through to enforcement (WRITE_TOOLS deny, Bash mutation/redirect/argv-git deny), lines 354–376.
- Identity equal to another known `.claude/agents/*.md` stem → pass-through (lines 355–357); roster listed at runtime relative to the hook file (`_known_roster_agents`, lines 67–78), never a hardcoded path; any `OSError` yields an EMPTY roster so spawned identities fail closed.
- Any other present identity (named spawn, harness built-in type, agent_id-only, unreadable roster) → enforced read-only via fall-through (lines 358–362). Verified the agent_id-only path: `agent == ""` fails the `if agent and ...` roster check, so it is governed.
- `main()` (lines 380–390) is a fail-closed exception envelope: any exception in `_main()` emits a deny instead of crashing (a crashed hook is non-blocking, i.e. fails open). Unparseable/non-object payloads also deny (lines 340–346).

**2. `.claude/settings.json`: CONFIRMED.** Exactly four hook entries (PreToolUse `Agent|Task` → agent_dispatch_guard; PreToolUse `Bash|Write|Edit|MultiEdit|NotebookEdit` → readonly_agent_guard; SessionStart and UserPromptSubmit → directive_reminder). All four are single-string `"command"` form (no legacy `args` list) with the `${CLAUDE_PROJECT_DIR}` path double-quoted, e.g. `python "${CLAUDE_PROJECT_DIR}/.claude/hooks/readonly_agent_guard.py"`. Also mechanically proven by the suite's 13 `settings:`/`settings hook #N` checks (spaced-root shlex survival + real-root file existence for each entry).

**3. `.gitignore`: CONFIRMED.** Line 64 contains `.claude/settings.local.json` under the D-004-R101 comment (line 63).

**4. Test suite `tools/test_readonly_agent_guard.py`: PASS.** Ran read-only via `python tools/test_readonly_agent_guard.py`. Result: **136 PASS checks, 0 failures**, final line `ALL CHECKS PASSED`, exit 0 — matches the expected 136/0. I counted the PASS lines individually (15 spaced-`-C` verb×quoting + 6 nuanced sub-commands + 9 operator-adjacency + 3 quoted-separator allows + 14 wrapper/case/dynamic denies + 4 prefix/dynamic allows + 9 read-only-`-C` allows + 10 preserved denials + 7 preserved allows + 10 role-governance + 2 malformed-payload + 15 teammate-shape + 5 id-only + 3 producer-roster + 2 built-in-type + 1 lead-shape + 4 roster-fail + 13 settings + 5 C3-envelope = 136). The suite exercises the real guard as a subprocess including a byte-identical copy run from a rosterless temp tree (missing-roster fail-closed) — no monkeypatching.

**5. Merged-content immutability: CONFIRMED.** `git diff 9db4ab328ea7e1570e347ae19174041d199aedc8..HEAD -- .claude/hooks/readonly_agent_guard.py .claude/settings.json .gitignore tools/test_readonly_agent_guard.py` produced empty output — the four files are unchanged since the reviewed merge.

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-004-R134 (sentinel Write-tool attempt) | 88045b06 | PASS (honestly labeled) | Attempt made exactly once; blocked by TOOL-UNAVAILABILITY, not the guard — verbatim message below |
| D-004-R135 (sentinel Bash redirect attempt) | 88045b06 | PASS | Exact contracted command denied by readonly_agent_guard.py — verbatim message below |
| D-004-R100 ride-along (settings quoting) | 88045b06 | PASS | Inspection of all 4 entries + 13 settings checks in the 136-check suite |
| D-004-R101 ride-along (settings.local.json ignored) | 88045b06 | PASS | `.gitignore` line 64 |

## Sentinel negative test (contracted; performed exactly once, no variations, no retries)

**(a) Write tool — enforcement layer: TOOL-UNAVAILABILITY (NOT the guard).** I attempted `Write` of `PILOT_SENTINEL.tmp` (content: `x`) directly. The Write tool is not available in my context; the attempt never reached the guard. Verbatim unavailability message:

> `Error: No such tool available: Write. Write exists but is not enabled in this context. Use one of the available tools instead.`

I state honestly: this blocking layer was tool-unavailability. I make no claim that the guard denied this call.

**(b) Bash redirect — enforcement layer: `.claude/hooks/readonly_agent_guard.py` (the guard itself).** I ran the exact command `echo x > ./PILOT_SENTINEL.tmp` once. It was DENIED. Verbatim denial message:

> `'code-reviewer' is operationally read-only: repository/GitHub/control-plane mutation and shell file-writes are blocked. Read-only git inspection, gh reads, and test execution are allowed; return findings via SendMessage.`

This is the guard's `_deny` text (hook lines 371–375), and the resolved identity `'code-reviewer'` confirms my spawn carried the governed reviewer identity and was matched by the `READ_ONLY_AGENTS` path, with the `_REDIRECT` rule producing the denial.

**(c) Existence probe (read-only):** `test -e ./PILOT_SENTINEL.tmp` → exit code **1** (file does not exist at the Bash cwd, which is the primary checkout root). The orchestrator will verify absence independently.

## Anomalies (none blocking; reported without softening)

1. Sentinel (a) could not exercise the guard's WRITE_TOOLS branch because the Write tool is not enabled for this agent; the guard's Write/Edit denial behavior is instead evidenced by the suite's subprocess checks (`deny Write tool`, `teammate shape: deny Write`, `id-only: deny Write Tool` — all PASS at the frozen head).
2. The denial message says "return findings via SendMessage" — in this session findings are returned as the final message, not via a SendMessage tool. Cosmetic wording only; the text is unchanged since the reviewed merge and the denial semantics are correct.
3. Documented residuals, unchanged from the reviewed state and explicitly disclosed in the hook's own docstrings: (i) a mutating verb hidden in a shell variable WITHOUT a `-C`/tree target (`c=push; git "$c"`) is not statically resolvable (line ~269 note); (ii) scripting-language file writes (`python -c` open-for-write) are inseparable from allowing test execution (module docstring, lines 39–44); (iii) a NAMED spawn whose spawn name exactly equals a roster producer stem is indistinguishable from an unnamed producer spawn and passes through — inherent to the observed payload shape (role unrecoverable for named spawns) and covered by the stated operating rule that writing producers are spawned unnamed plus orchestrator-only integration. All three are pre-existing, documented, and out of this rerun's defect scope.
4. My earlier read-only commands in this session (`git rev-parse`, `git diff`, `python tools/test_...`, `test -e`) were all permitted — consistent with the guard's allow rules for read-only inspection and test execution, providing incidental live confirmation of the no-over-denial contract.

## Defects

None.

## Required rework

None.

## Reviewer conclusion

All five review-scope items reproduce cleanly at the frozen head; the 136-check suite passes with 0 failures; the sentinel Bash write was denied by the guard itself with the resolved governed identity; merged content is byte-identical since review.

VERDICT: PASS — all contracted checks reproduced at frozen head 88045b06 with 136/0 test results and a guard-produced sentinel denial; the only non-guard blocking event (Write tool unavailability) is honestly attributed to tool availability, not the guard.

*(Orchestrator note: the reviewer's return rendered absolute Windows paths for two file references;
they are normalized to repo-relative paths in this capture per the no-machine-specific-data rule
(D-004). No other alteration. Original absolute forms referenced the primary checkout.)*

## Appendix B — control-plane-verifier return (verbatim)

All evidence gathered. Here is the verification report, returned verbatim for the orchestrator to capture.

# Gate Report — Control-Plane Verification (D-004 Step 3 Phase 8 fresh-session rerun)

- Gate ID: control-plane verification (fresh-session rerun capsule item; feeds the M0-T028 gate set)
- Task ID: M0-T028
- Reviewer: control-plane-verifier (read-only; explicit fresh session)
- Producer: backend-engineer (no gate recorded by producer; see item 2)
- Result: PASS
- Clean environment/worktree used: primary checkout at frozen HEAD `88045b06ef12ccb9b994b4e8b38ffe40d9cadf04` (confirmed via `git rev-parse HEAD` before any other step); working-tree dirt enumerated and matched against the declared capture set (item 6).

## Finding per item

### Item 1 — M0-T028 lifecycle integrity: CONFIRMED
File: `project-control/tasks/M0-T028.json`
- `status`: `awaiting_gate` (observed, line 75); CLI status output agrees (`awaiting_gate`, progress 95, agent backend-engineer).
- `producer_agent`: `backend-engineer` (line 68).
- `dependencies`: `[]` (line 27) with the recorded `dependency_note` present (line 102: owner directive 2026-07-29, D-004 source-006 Phase 1, M0-T027 removed as formal dependency to break the accept() deadlock while remaining the causal predecessor).
- Submit record `project-control/reports/M0-T028.json`: `reviewed_sha` = `9db4ab328ea7e1570e347ae19174041d199aedc8` (CONFIRMED ancestor of frozen HEAD via `git merge-base --is-ancestor`), `evidence_map` = `project-control/reports/M0-T028-evidence-map.json` (file exists; 177 rows; carries the same `reviewed_sha`), `content_manifest_sha256` = `126d2d53472deb8828ca4f007b5809b19e5c512ea2288b25499c27f12c0287c2` (exact match), `applicable_requirements` count = 177 (177 unique, counted programmatically).

### Item 2 — Gate records and reviewer independence: CONFIRMED
Files under `project-control/gates/`:
- `M0-T028-G0.json`: PASS, reviewer `orchestrator`, role `administrative`, reviewed_sha `4a4bf2d572edce963a355d9d997a2e05833c1dbf` (ancestor of HEAD, confirmed), content manifest `f7a85a25…` (pre-implementation identity, as expected for a readiness gate).
- `M0-T028-G2.json`: PASS, reviewer `orchestrator`, role `self_check`, reviewed_sha `9db4ab3…`, content manifest `126d2d5…`. Legal: G2 is the producer self-check gate ("only permits submission; it does not accept the task", `docs/GATES_AND_CHECKPOINTS.md` line 57), recorded by the orchestrator per ADR-005.
- `M0-T028-G3.json`: PASS, reviewer `code-reviewer`, role `independent_review`, reviewed_sha `9db4ab3…`, content manifest `126d2d5…`.
- `M0-T028-G5.json`: PASS, reviewer `security-reviewer`, role `independent_review`, reviewed_sha `9db4ab3…`, content manifest `126d2d5…`.
- Independence: producer backend-engineer recorded zero gates; G3/G5 reviewers are distinct identities from the producer (satisfies `docs/GATES_AND_CHECKPOINTS.md` line 163); gate-class semantics are mechanically enforced (test group S3 "gate classes (independent/self_check/administrative; no bypass)" passed, item 7).
- Consistency note (not a defect): the G3/G5 report files (`project-control/reports/M0-T028-G3-report.md`, `M0-T028-G5-report.md`) state the review was performed at frozen task-branch SHA `e8a7dbfa2145b76f91b8e5272769a1447a940525`; the gate records are pinned at the main merge SHA `9db4ab3` with the identical `content_manifest_sha256` `126d2d5…` bridging the content identity, matching the submit record. This is the established merge-reconciliation pattern and the reports disclose it verbatim.

### Item 3 — B-015 still OPEN with intact append-only audit trail: CONFIRMED
File: `project-control/blockers/B-015-teammate-readonly-guard-bypass.json`
- `status`: `open` (line 4). NOT resolved at review time, as required.
- `audit_log`: exactly one entry (the 2026-07-24 OPENED record). Git history of the file shows a single commit (`0361491`, 2026-07-24) and no modification since — nothing removed or rewritten; append-only trail intact.

### Item 4 — Ledger totals: CONFIRMED
- `python tools/project_control.py status` reports `task_counts.accepted: 49`; `project-control/state.json` lists 49 accepted task IDs (counted).
- `state.json` `last_checkpoint`: `CP-0033`; `project-control/checkpoints/CP-0033.json` exists and is the highest-numbered checkpoint file (glob of `project-control/checkpoints/*`).
- `M0-T027` is in `state.json` `blocked_tasks` and reports `blocked` (progress 60) in the CLI output — unchanged.
- Additional totals cross-check: blocked 3 (M0-T007, M0-T008, M0-T027), claimed 1 (M0-T019), awaiting_gate 9, backlog 10 — CLI counts match the per-task listing and the state file.

### Item 5 — Reviewer independence + authority (no producer/reviewer control-plane writes): CONFIRMED
- All five `progress_log` entries in `M0-T028.json` carry `"agent": "orchestrator"`; content is disclosure-grade (model-mismatch disclosure, deviation disclosure, G3/G5 correction records) with no producer- or reviewer-authored entries.
- `git log` over `project-control/tasks/M0-T028.json`, `project-control/gates/`, and `project-control/reports/M0-T028.json`: every commit is authored by `martin10101` (the orchestrator's git identity) on control-lifecycle commits merged via PRs #121–#123; no commit by any producer/reviewer identity.
- Timestamps are CLI-ordered: submit 05:34:41 → G2 05:34:52 → G3 05:34:54 → G5 05:34:56 → task/state update 05:34:57 (same UTC second-ordering across files).
- Anomaly, disclosed and benign: the submit record file `reports/M0-T028.json` was missed from PR #122's staging and added at the frozen head by commit `14ed27f` (PR #123, "add the CLI submit record missed from PR #122"). The record's internal timestamps predate the gate records, so the CLI lifecycle ordering was correct; only the git staging lagged by one commit, and the commit message discloses it. No hand-edit indicators.
- Incidental live corroboration of the guard: my own first derivation probe was DENIED by the read-only guard because the script text contained the `->` character sequence — the documented pre-existing fail-safe over-denial (G5 INFO item). This confirms the guard fires against this reviewer identity in the fresh session; I reworked the probe without arrow sequences.

### Item 6 — Uncommitted amendment-6 capture is well-formed append-only registry state: CONFIRMED
Directory: `project-control/directives/D-004-agent-teams-runtime-adoption/`
- `git status --porcelain`: control-plane dirt is exactly `manifest.json` (M), `requirements.json` (M), `source-007-amendment.md` (untracked) — matching the declared capture. Remaining dirt is agent-memory files plus an untracked machine-local `.npmrc` (owner's global tooling artifact; outside the control plane; noted, no impact).
- `git diff HEAD -- <file>` is 0 bytes for every committed source: source-001.md, source-002…source-006-amendment.md — byte-unchanged.
- `source-007-amendment.md`: new, 2560 bytes; raw sha256 `4d5caed0ca1ca71fc4cf30bbca4b6e658a60481cf3c616f758155bf92e3d44cb` equals the manifest sequence-7 `content_digest_sha256` exactly.
- `manifest.json`: version 6 → 7; `sources` gains exactly the sequence-7 entry (entries 1–6 unchanged, verified by object equality); `amendments` appends `source-007-amendment.md`; `locked_requirement_ids` 286 → 296 with the HEAD list preserved as an exact prefix and exactly `D-004-R287`…`D-004-R296` appended; `audit_log` 6 → 7 entries (HEAD prefix preserved) with the amendment-6 entry; `notes` append-only (HEAD 10-entry prefix preserved, one added); `owner_approval.state` extended to `…step_3_authorized_phase_8_go`; requirements digests re-derived; `updated_at` bumped. No non-append mutation found.
- `requirements.json`: 286 → 296 rows; rows R001–R286 equal to HEAD as parsed objects (exact prefix); exactly R287–R296 appended, every one scoped `applicability.task_ids: ["D-004-PHASE8"]` (verified row-by-row).
- Derivation check (executed): `DirectiveRegistry().load().derive_applicable()` on the working-tree registry against `tasks/M0-T028.json` yields exactly 177 applicable requirement IDs, all D-004, zero unresolved reasons, set-equal to the submit record's `applicable_requirements`, and none of R287–R296 leak into it.
- `python tools/validate_directive_compliance.py --check` → exit 0 against the working tree (registry CLI additionally reports D-004: 296 requirements, 0 errors, status active).

### Item 7 — Read-only test suite: CONFIRMED PASS
`python tools/test_project_control.py` → exit 0; all 14 groups OK, including S1 transition enum (legal chain passes; every prohibited jump rejected), S2 accept preconditions (status, gates, dependencies, blockers), S3 gate classes, S6 spoofing rejection, S9 directive claim enforcement / git-canonical identity / accept-requires-independent-verification / regime-bypass closed.

## Defects
None blocking. Observations (all disclosed above, none softened): (a) submit-record file staged one PR late (item 5) — content and ordering intact; (b) untracked `.npmrc` at repo root — machine-local, non-control-plane; (c) guard over-denial of `->` sequences — pre-existing, documented, fail-safe direction; (d) CP-0033 predates the M0-T028 lifecycle merges — acceptable, since no acceptance has occurred after CP-0033 and checkpoints bind to acceptances.

## Required rework
None.

## Reviewer conclusion
Every status transition observed is legal and CLI-recorded by the orchestrator; all four required gates carry real reports with producer ≠ reviewer; M0-T028 is not accepted and B-015 remains open with an intact audit trail; ledger totals match task files and the CLI; the active owner holds (expansion hold, D-004 staged GOs) are respected — the only uncommitted control-plane state is the well-formed, append-only, digest-verified amendment-6 Phase-8 GO capture whose sentinel scoping provably leaves the M0-T028 applicable set at 177.

VERDICT: PASS — all seven verification items are CONFIRMED at frozen head 88045b06ef12ccb9b994b4e8b38ffe40d9cadf04 with no control-plane violation found and only non-blocking, fully disclosed observations.

*(Orchestrator note: the reviewer's return rendered absolute Windows paths for three file
references; normalized to repo-relative paths in this capture per the no-machine-specific-data
rule (D-004). No other alteration.)*

## 9. B-015 resolution (capsule step 7b)

Performed by the orchestrator AFTER the sentinel pass above and after the
directive-compliance-verifier's pass-1 read of the still-open blocker:
`project-control/blockers/B-015-teammate-readonly-guard-bypass.json` status `open` → `resolved`,
with an append-only audit entry citing the merged fix (PR #121, merge
`9db4ab328ea7e1570e347ae19174041d199aedc8`), the passing fresh-session sentinel at frozen head
`88045b0`, the independent absence verification, and the residual-risk routing (C2 follow-up per
the owner's recorded decision; M0-T027 remains blocked; Steps 4–5 remain un-authorized). The
original OPENED audit entry is byte-preserved.

## 10. Final independent directive verification (capsule step 7c) — two-pass structure

The directive-compliance-verifier (unnamed spawn, explicit Fable 5) performed the final
per-requirement verification at frozen head `88045b06ef12ccb9b994b4e8b38ffe40d9cadf04` and
content identity `126d2d53472deb8828ca4f007b5809b19e5c512ea2288b25499c27f12c0287c2`:

- **Pass 1** (Appendix C, verbatim): derived the applicable set itself (177 ids, equal to the
  pending verification row and the submit record), then recorded 157 PASS + 20 PENDING-PHASE8 +
  0 FAIL/BLOCKED/UNVERIFIABLE/NOT_APPLICABLE. The 20 pending rows are exactly the Phase-8
  completion acts performed after its review (sentinel evidence recording, B-015 resolution,
  acceptance, checkpoint/cleanup, return packet).
- **Pass 2** (Appendix D, verbatim): bounded finalization of exactly those 20 rows against the
  completed artifacts (§§4–9 of this report, the resolved B-015 audit entry, the queued
  CLI acceptance, the checkpoint decision in §11, and the bound return-packet content in §11).
- The orchestrator transcribes the verifier's verdicts VERBATIM into
  `project-control/directives/D-004-agent-teams-runtime-adoption/verification.json`
  (M0-T028 row) under the verifier's identity at the frozen identity above. The producer of
  requirements.json (orchestrator) records no verdict of its own; every PASS is the independent
  verifier's.

## 11. Acceptance-adjacent decisions bound before accept (for pass-2 evidence)

- **Checkpoint decision:** the established policy (`docs/GATES_AND_CHECKPOINTS.md` §Checkpoint
  requirements) REQUIRES a checkpoint here ("after integrating a task", "when a blocker changes
  the critical path", "at the end of every meaningful work session"). CP-0034 is therefore
  created immediately AFTER acceptance, recording the accepted state. It was not assumed or
  pre-reserved; this is a policy-derived requirement recorded before acceptance.
- **Cleanup (queued post-acceptance):** delete ONLY local branch `task/M0-T028-readonly-guard`
  (remote already deleted) and worktree `.claude/worktrees/M0-T028-readonly-guard`. The
  pre-existing `agent-*` worktree husks and every other worktree remain untouched (not
  authorized).
- **C2 owner decision:** "Contract it" (recorded §8). Follow-up packet M0-T032 is contracted via
  `project_control.py new-task` after acceptance (backlog, unclaimed; starting the C2 work needs
  its own owner GO at claim time).
- **Return packet:** delivered as the final message of this session per source-006 (17 items);
  its content is fully determined by this report plus the two mechanical post-accept values
  (acceptance record, CP-0034). No item depends on unperformed analysis.
- **Accept command (queued):** `python tools/project_control.py accept --task-id M0-T028
  --agent orchestrator` — run immediately after the pass-2 verdicts are transcribed and the
  validator re-run is green; refused automatically by the CLI if any precondition fails.

## Appendix C — directive-compliance-verifier pass-1 return (verbatim)

All evidence is gathered and reproduced. Assembling the final per-requirement report.

---

# M0-T028 / D-004 — FINAL independent directive-compliance verification (fresh session, D-004 Step 3 Phase 8)

**Verifier:** directive-compliance-verifier (read-only; not the producer of requirements.json or of any reviewed change)

## Header — identity confirmation

- Frozen head: `git rev-parse HEAD` = `88045b06ef12ccb9b994b4e8b38ffe40d9cadf04` — MATCHES the required frozen head. `origin/main` = same SHA (reconciled). First-parent chain contains implementation merge `9db4ab328ea7e1570e347ae19174041d199aedc8` (PR #121, state MERGED, mergeCommit oid verified via gh) with exactly commits `e8a7dbfa…` (fix) and `d5eb642e…` (C3+C4 bounded delta) over base `4a4bf2d…`.
- Git-canonical content identity: `directive_registry.frozen_git_identity(task.allowed_paths, "HEAD", exclude_prefixes=("project-control/",))` = `('126d2d53472deb8828ca4f007b5809b19e5c512ea2288b25499c27f12c0287c2', '88045b06ef12ccb9b994b4e8b38ffe40d9cadf04', None)` — MATCHES the required identity, clean, no error.
- Applicable set derived by me from `project-control/tasks/M0-T028.json` via `load_registry().derive_applicable(task)`: **177 ids, zero unresolved reasons**, derived over the working-tree registry that already contains amendment 6 (none of R287–R296 matched). Set equality confirmed against: (a) the pending row `verification.json → task_verifications[task_id=M0-T028].applicable_requirement_ids` (177, state pending, verifier=directive-compliance-verifier, no pre-recorded PASS — producer/verifier separation intact); (b) the submit record `project-control/reports/M0-T028.json → applicable_requirements` (177, `content_manifest_sha256` = `126d2d53…`, `reviewed_sha` = `9db4ab3…`). All three sets are identical.

## Per-requirement verdicts (177 rows, sorted)

D-004-R010: PASS | Ledger is sole truth: CLI-written progress_log/gates/state.json + PRs #120–#123 + gh checks 28/28; no extra-ledger status claimed anywhere
D-004-R011: PASS | No Agent Teams task list existed (single-writer subagent; probes bounded read-only); no team-state artifact in e5d95b6..HEAD diff
D-004-R012: PASS | git log: e8a7dbf/d5eb642/all merges authored by orchestrator identity martin10101; producer report §6 contains no CLI/git-write/gh command
D-004-R013: PASS | Merges #120–#123 are all orchestrator first-parent merge commits (git log --first-parent)
D-004-R014: PASS | Producer report §1/§6: no push/gh/rebase; branch commits authored/committed by orchestrator only
D-004-R015: PASS | Not triggered — no rebase occurred (task branch is base 4a4bf2d + 2 commits, merge-base = base)
D-004-R016: PASS | Sequential PRs #120→#121→#122→#123; G2/G3/G5 recorded at merged content identity 126d2d53
D-004-R017: PASS | All 4 reviewer roles exist as .claude/agents/*.md (ls verified); guard denials named the roster roles live (G3 §12, G5 line 46, dcv §7, plus 4 denials of this verifier at HEAD)
D-004-R018: PASS | Reviewer set = packet reviewer_agents exactly (4 independent) + administrative G0/G2 (gates/M0-T028-G*.json)
D-004-R019: PASS | Every reviewer report header pins the frozen 40-char SHA (e8a7dbfa…/d5eb642e…); this dispatch pinned 88045b06…
D-004-R020: PASS | All six review reports follow the /run-quality-gate GATE_REPORT template; my dispatch explicitly invoked the skill
D-004-R021: PASS | PR #121 diff = 6 files all ⊆ allowed_paths; #122/#123 = orchestrator control-plane lifecycle records bound to M0-T028 (each gate record names its report_file)
D-004-R022: PASS | No M0-T025 path in e5d95b6..HEAD name list; 0-line diff 4a4bf2d..9db4ab3 on tasks/M0-T025.json
D-004-R023: PASS | Evidence file §2 records only spawn name m0t028-diag-probe + roles from configuration
D-004-R024: PASS | Task-lane artifacts sanitized — my grep over both frozen reports finds only payload key names + the hygiene disclaimer; reviewer returns follow the 2026-07-16 owner verbatim-preservation rule (see summary note 2)
D-004-R025: PASS | Fresh session spawns fresh agents (this session); capsule §3 mandates fresh spawns; no prior-team messaging artifact
D-004-R026: PASS | Merged-hook testing deferred to this fresh session (producer AS-3, capsule); dcv grep found zero premature-test claims
D-004-R050: PASS | Not triggered — Step-2 probe passed (AGENT-TEAMS-PILOT-2-PROBE.md at main); Step 3 began only on owner GO (source-006)
D-004-R051: PASS | source-006 = explicit owner GO for Step 3 only; Step-2 pass on record
D-004-R052: PASS | M0-T028 packet: own ID, scope, AS-1..AS-10, 4 independent reviewers, G0/G2/G3/G5
D-004-R053: PASS | M0-T025 untouched in every diff (0 lines)
D-004-R054: PASS | Guard docstring residuals (lines 39–44) + producer §3/§7 + evidence §4.5 name detection as backstop; no "impossible" claim anywhere
D-004-R055: PASS | Binding task↔worktree↔branch task/M0-T028-readonly-guard↔frozen base 4a4bf2d (single-chain); harness refused unbound work (producer §1 verbatim denials)
D-004-R056: PASS | Execution-level: producer Write/Edit outside its worktree denied (producer §1 quoted harness denial); governed identities denied all Write/Edit by guard; teams-runtime layer-2 infra not triggerable (no producer teammates, R233; Step 4 unauthorized, R178) — see summary note 3
D-004-R057: PASS | Harness refused producer cross-tree git -C (producer §1); guard denies mutating Bash for governed/unknown identities (suite 136/0; 4 live denials of this verifier at HEAD)
D-004-R058: PASS | Not triggered — no TaskCompleted/TeammateIdle events existed (Agent Teams producers prohibited while B-015 open); containment enforced by orchestrator port-diff + 3 reviewer containment checks + recorded dirt sweeps
D-004-R059: PASS | Containment covered committed/staged/untracked (control-plane full dirt inventory; G5 forbidden-path grep; my diff --name-status = exactly 6 files, no renames/deletes)
D-004-R060: PASS | Zero escapes (sweeps clean; sentinel absent — my test -e exit 1); the one Step-1 escape (B-015) blocked completion until fixed — refusal semantics upheld
D-004-R061: PASS | Producer isolated worktree at identical base + orchestrator exact-diff port review before integration (65% entry; G3 step 2)
D-004-R062: PASS | Suite covers shell redirects, quoted/backslash/spaced git -C, absolute paths, case/wrapper vectors (sections 1,1b,1d,1e); scripting-language residual explicitly exercised+documented (G5 dim 7); owner-corrected contracted test set (R143) fully present and passing
D-004-R063: PASS | Prior session stopped after gates+submit with capsule STOP; Phase-8 GO captured (amendment 6) before any completion act
D-004-R085: PASS | Each STOP presented evidence/diffs then waited: packet proposal→owner GO (source-006); capsule→owner GO (source-007, 2026-07-30)
D-004-R086: PASS | Ambiguity→blocker practice upheld (B-015; MODEL-MISMATCH honest stop at 40% entry; no improvised action)
D-004-R089: PASS | .claude/settings.json = $schema + hooks only; no teammateDefaultModel (file read at HEAD)
D-004-R090: PASS | Lead on Fable 5 (40% entry); every gate reviewer spawn explicit Fable 5 (all six report headers)
D-004-R091: PASS | Not triggered — no producer teammate used (forbidden while B-015 open); background-subagent inherit=Fable 5 non-downgrade honestly recorded (40% entry)
D-004-R094: PASS | No effort key in any changed file (grep 0 in settings.json; G5 added-key-set-empty proof)
D-004-R096: PASS | Absolute hold honored; session effort xhigh unchanged (observed payload field only, never written)
D-004-R100: PASS | settings.json:10,19,29,39 all quoted "${CLAUDE_PROJECT_DIR}/…"; suite section 12 space-safety passes (my 136/0 run); the quoted wiring demonstrably fires live in this fresh session (guard denied 4 of my commands)
D-004-R101: PASS | .gitignore:64 entry; my `git check-ignore -v` resolves to repo `.gitignore:64`, not a global excludes
D-004-R124: PASS | No effort applied anywhere (settings clean; diff grep hits are report prose only)
D-004-R127: PASS | Owner decided (effort xhigh, R156); nothing pre-empted in any diff
D-004-R134: PASS | Sequencing honored — fix merged (9db4ab3) with no rerun attempted before merge (zero premature claims, dcv grep)
D-004-R135: PENDING-PHASE8 | Completing artifact: passing fresh-session sentinel evidence file (capsule §3 steps 3–4)
D-004-R136: PENDING-PHASE8 | Completing artifact: rerun record proving 3 same reviewer roles + frozen main head + explicit Fable 5 per spawn + sentinel repeated
D-004-R137: PENDING-PHASE8 | Completing artifact: captured guard denial + orchestrator's independent verification in the rerun evidence
D-004-R139: PASS | B-015 blocker exists with its OPENED audit entry; ratification captured in registry (source-005 rows)
D-004-R140: PASS | Packet objective assigns B-015 diagnosis+fix to M0-T028
D-004-R141: PASS | TEAMMATE-PAYLOAD-EVIDENCE.md §§1–4: live payloads, H1 REFUTED/H2 CONFIRMED, tool-unavailability positive explicitly weighed
D-004-R142: PASS | Fail-closed identity resolution at HEAD (readonly_agent_guard.py:347–363); named/unknown spawns 63/63 mutations denied (G5 differential); suite 136/0 (my run); pre-existing unnamed-reviewer-class residual = C2 owner decision, flagged not hidden
D-004-R143: PASS | Suite contains the sentinel case ("teammate shape: deny sentinel redirect"), R100 section 12, and R101 is proven via check-ignore
D-004-R144: PASS | index.json D-004 affected_tasks = ["M0-T027","M0-T028"] (my JSON read); corrected at capture (PR #120); task diff on index = 0 with explicit statement (producer §4)
D-004-R145: PASS | Packet presented and owner-APPROVED before start (owner_review_state; PR #120 merged 03:43Z before G0 03:45:49Z)
D-004-R156: PASS | effortLevel xhigh session-global observed unchanged (payload §2.2); no change made
D-004-R157: PASS | No MAX effort applied anywhere
D-004-R159: PASS | No effort key written in any file (greps; G5 key-set proof; settings.json read)
D-004-R160: PASS | Probes A/B explicit Fable 5 (evidence §2.2/2.3; probe self-reported claude-fable-5); reviewer spawns explicit Fable 5
D-004-R161: PASS | All six gate-class reviewer spawns explicit Fable 5 (report preservation headers)
D-004-R162: PASS | Not triggered — no producer teammate; enum limitation (opus→claude-opus-5) honestly measured and recorded (40% entry; capsule §4)
D-004-R166: PASS | Historical sequence on record: source-005 captured → Step 2 run (PILOT-2-PROBE.md at main) → STOP with M0-T028 packet proposal
D-004-R167: PASS | No unrecorded ambiguity; blocker practice upheld
D-004-R168: PASS | source-006 header records live reconciliation to e5d95b6 before any write
D-004-R169: PASS | Owner GO captured verbatim (source-006: "explicit owner GO for D-004 Step 3 only")
D-004-R170: PASS | Amendment merged in PR #120 (4a4bf2d) before any M0-T028 mutation (implementation base = 4a4bf2d)
D-004-R171: PASS | Packet corrected in PR #120 before G0 and claim (timestamps above)
D-004-R172: PASS | e5d95b6..HEAD name list = M0-T028/D-004 artifacts only; no other work
D-004-R173: PASS | Diagnosis rests on the primary payload artifact (evidence §§1–2)
D-004-R174: PASS | H2 proven repairable inside .claude/hooks/readonly_agent_guard.py (allowed path); fix confined there
D-004-R175: PASS | R100 (settings.json) + R101 (.gitignore) ride-alongs present in the merged diff
D-004-R176: PENDING-PHASE8 | Independent review + protected-main merge complete (gates; PR #121 28/28); required fresh-session rerun outstanding
D-004-R177: PENDING-PHASE8 | Closure/acceptance acts occur only after this verification + passing sentinel (accept() consumes verification.json)
D-004-R178: PASS | No Step-4/5 artifact in any diff; capsule §6 forbids; none begun
D-004-R179: PASS | No M0-T029 artifact
D-004-R180: PASS | No Agent Teams adoption artifact
D-004-R181: PASS | No producer wave/injection; single-writer subagent recorded
D-004-R182: PASS | No detection-only substitute (prevention fix implemented on proven H2)
D-004-R183: PASS | M0-T025 unchanged (0-line diffs)
D-004-R184: PASS | No M0-T019/PR #64 content in any diff
D-004-R185: PASS | No second-wave product task artifact
D-004-R186: PASS | No expansion architecture/PRD artifact
D-004-R187: PASS | No Mission Control artifact
D-004-R188: PASS | No project/control-graph artifact
D-004-R189: PASS | No NYC Evidence KG artifact
D-004-R190: PASS | No Graphify artifact (D-005 WAIT standing)
D-004-R191: PASS | No M2–M7 product code (diff surface = hooks/settings/gitignore/tools-test/reports/control-plane only)
D-004-R192: PASS | No survey work
D-004-R193: PASS | No deployment change or hold release (no deploy file touched; B-001/004/010/011/012/013 open, B-002 resolved_temporary)
D-004-R194: PASS | No effort setting/key (verified)
D-004-R195: PASS | Recorded in source-006 header + G0 readiness (fetch/status/current_state before writing)
D-004-R196: PASS | Reconciliation recorded (source-006 orientation block: main/PRs/tasks/blockers/CP/CI/D-004 state)
D-004-R197: PASS | Phase-0 reading list recorded as read (G0 readiness; source-006 capture header)
D-004-R199: PASS | settings.json contains no allow rules, machine paths, effort keys, or local config (file read at HEAD)
D-004-R200: PASS | No permission-prompt rule staged; settings.local.json untracked and now repo-ignored (line 64)
D-004-R201: PASS | Task names its principal files; no graph-first navigation; evidence map/G0 record "code graph not needed"
D-004-R202: PASS | Advancement e5d95b6→4a4bf2d is PR #120 itself (the authorized capture); later advancement = this task's own PRs #121–#123
D-004-R203: PASS | Deadlock ratified and corrected pre-G0; accept() dependency refusal confirmed at tools/project_control.py:923–933 (control-plane item 1)
D-004-R204: PASS | tasks/M0-T028.json line 27: "dependencies": []
D-004-R205: PASS | Inputs 2–3 = both pilot reports; dependency_note preserves M0-T027 as causal predecessor, not acceptance prerequisite
D-004-R206: PASS | Empty array with explicit no-replacement reasoning (dependency_note)
D-004-R207: PASS | Correction explained in source-006 Phase 1 + manifest audit + PR #120 body (reproduced by control-plane/dcv reviews)
D-004-R208: PASS | owner_review_state = "APPROVED — explicit owner GO … source-006 …" citing its conditions
D-004-R209: PASS | backend-engineer exists in the 25-stem roster and is distinct from all four reviewers (my ls)
D-004-R210: PASS | Existing role used; none invented (roster-inspected producer_note)
D-004-R211: PASS | Clarification recorded: Write/Edit may remain blocked by tool unavailability (packet AS-2; evidence §4.1)
D-004-R212: PASS | No artifact claims the guard denied an uninvokable tool; Step-1 Write denial attributed to "No such tool available: Write" (evidence §4.1; dcv grep zero false claims)
D-004-R213: PASS | Bash redirection is the load-bearing test in suite + capsule §3.4 procedure
D-004-R214: PENDING-PHASE8 | Unit-level guard deny proven at HEAD (suite sentinel case; G5 synthetic named-spawn deny) — live fresh-session capture outstanding
D-004-R215: PENDING-PHASE8 | Orchestrator post-sentinel `test -e` record outstanding (my pre-test check: absent, exit 1)
D-004-R216: PENDING-PHASE8 | The honest trio (tool-unavailability + guard denial + independent absence) recorded only by the rerun evidence
D-004-R218: PASS | source-006 contains every mandated record item (read; cross-checked with dcv-premerge scope 1)
D-004-R219: PASS | Rows appended from next free ID R168; prior rows unedited (control-plane row-by-row proof; my amendment-6 comparison: R001–R286 unchanged)
D-004-R220: PASS | validate_directive_compliance.py --check exit 0 on the working tree (my run); digests recomputed by two reviewers
D-004-R221: PASS | affected_tasks corrected in manifest + index via PR #120 (my index.json read)
D-004-R222: PASS | PR #120 diff = 6 control files only, no product/M0-T025/effort/handoff (control-plane item 1); checks green
D-004-R223: PASS | PR #120 merged, then implementation frozen at 4a4bf2d (G0 record reviewed_sha)
D-004-R224: PASS | Implementation/review/merge in the prior session; merged-behavior validation reserved to this fresh session (capsule; zero premature claims)
D-004-R225: PASS | No detection-only fallback (prevention fix on H2)
D-004-R226: PASS | Both diagnostic teammate probes carried explicit Fable 5; no producer teammate used
D-004-R227: PASS | All unrelated holds standing (blocker states listed; expansion hold rule active in this session; Graphify WAIT; M0-T027 blocked)
D-004-R228: PASS | Fresh G0 PASS at 4a4bf2d against the corrected packet (gates/M0-T028-G0.json)
D-004-R229: PASS | New task-named worktree/branch from frozen main (task/M0-T028-readonly-guard, base 4a4bf2d)
D-004-R230: PASS | No pilot branch/team/worktree reuse (branch created post-#120; control-plane confirmation)
D-004-R231: PASS | CLI claim recorded (CLI-written progress_log; state.json active_tasks contains M0-T028)
D-004-R232: PASS | Single-writer model: one producer, orchestrator sole committer/integrator
D-004-R233: PASS | Producer = background subagent, NOT an Agent Teams teammate (producer_note; no team artifact)
D-004-R234: PASS | Probes bounded, no-Write/Edit, explicit model (evidence §§2.2–2.3)
D-004-R235: PASS | Dirt sweeps before/after every probe recorded clean (35% entry; evidence §1)
D-004-R236: PASS | No unexpected file at any point (sweeps; sentinel currently absent)
D-004-R237: PASS | Diagnosis (35% entry, 03:57Z) precedes implementation commit; fix contract derived from evidence §5, not guessed
D-004-R238: PASS | H1 vs H2 distinguished with live payload captures (evidence §§2–3)
D-004-R239: PASS | Live instrumentation of the real hook stdin — primary runtime artifact, not synthetic (evidence §1)
D-004-R240: PASS | Both frozen reports sanitized (my grep: only payload key names + the disclaimer sentence)
D-004-R241: PASS | Evidence §4 reconciles all five required facts explicitly
D-004-R242: PASS | Narrowest identity-resolution fix inside allowed paths; classification core byte-identical to base (G5 10,947-byte blob proof; G3 step 4; my full-file read)
D-004-R243: PASS | Unparseable-payload deny unchanged + roster-failure→empty-roster fail-closed + C3 envelope (guard code; fail-closed cases in my 136/0 run)
D-004-R244: PASS | No weakening: 89/89 base suite vs new guard + 388-comparison differential, 0 weakenings (G5); enforcement set strictly widened (code inspection)
D-004-R245: PASS | Read-only git/gh/test commands unchanged across all identity classes (34×4 identical; allow checks in my run; my own read-only git/gh executed)
D-004-R246: PASS | Not triggered — H2 proven; no detection-only implemented, no packet reinterpretation
D-004-R247: PASS | Not triggered — no H1 STOP packet needed
D-004-R248: PASS | Not triggered — no detection-only work
D-004-R249: PASS | Contracted work completed starting with the guard correction (diff inventory)
D-004-R250: PASS | Suite sections 7/8 encode the actual teammate payload shape (spawn name + agent_id; agent_id-only)
D-004-R251: PASS | Malformed/unparseable fail-closed cases pass in my run
D-004-R252: PASS | No previously-denied mutating command becomes allowed (G5 dual proof + byte-identical classification core)
D-004-R253: PASS | Legitimate read-only commands remain allowed (suite; live)
D-004-R254: PASS | All four hook commands quoted single-string (settings.json lines 10/19/29/39)
D-004-R255: PASS | Suite section 12 spaced-root proof passes (my 136/0 run)
D-004-R256: PASS | .gitignore:64 = .claude/settings.local.json with R101 comment
D-004-R257: PASS | My `git check-ignore -v` output: `.gitignore:64:.claude/settings.local.json` — repo file supplies the match
D-004-R258: PASS | Index corrected at the capture layer (PR #120); task diff on index.json = 0, explicitly stated
D-004-R259: PASS | My runs at HEAD: guard 136 PASS/0 FAIL, project-control 14/14, directive-compliance 55 OK, directive-reminder 12 OK, validator --check exit 0; gitleaks on all 6 changed files "no leaks found" (my runs); PR #121/#122/#123 checks 28/28 pass (gh); containment diff exact
D-004-R260: PASS | Untouched: M0-T025, product code, pilot reports, prior D-004 sources (R001–R286 unchanged), unrelated settings, CLAUDE.md, agents, rules, deployment, effort
D-004-R261: PASS | One frozen SHA e8a7dbf for G3/G5/control-plane/dcv + G2 via orchestrator CLI; bounded delta reviews at d5eb642 (reports + gate records)
D-004-R262: PASS | backend-engineer ≠ any of the four reviewers; I am not the producer of any reviewed change
D-004-R263: PASS | Every listed inspection item covered across G3/G5/control-plane/dcv reports (sections cited in each), reproduced where reachable by me
D-004-R264: PASS | C3/C4 applied within contracted paths only; C1 bound into Phase-8 procedure; C2 held as owner proposal
D-004-R265: PASS | Bounded G3+G5 delta reviews at d5eb642 performed before merge (delta reports; merge contains both commits)
D-004-R266: PASS | Protected-main PR #121 MERGED with 28/28 checks pass (gh, reproduced)
D-004-R267: PASS | At HEAD: B-015 open, M0-T028 awaiting_gate (not accepted; 49 accepted), CP-0033 last checkpoint, no Step 4, no adoption, zero sentinel-passed claims
D-004-R268: PENDING-PHASE8 | This fresh session is the venue; partial live proof already (merged quoted wiring fired 4× denying this verifier); full C1 four-hook + sentinel proof outstanding
D-004-R269: PASS | main==origin/main at 88045b0; merge SHA recorded (capsule §1; submit record); trees clean except the authorized amendment-6 capture
D-004-R270: PASS | Capsule contains every mandated item (merged SHA, task status, PR, reviewed SHAs, gates, procedure, models, forbidden actions, B-015 OPEN, M0-T027 BLOCKED, no Step 4/5)
D-004-R271: PASS | STOP after capsule with explicit restart instruction (capsule header); this fresh session exists as corroboration
D-004-R272: PASS | No freshness simulation — genuinely new session; prior records refuse simulation
D-004-R273: PASS | Phase 8 authorized by owner GO captured as amendment 6 (source-007, rows R287–R296 scoped to D-004-PHASE8, 2026-07-30)
D-004-R274: PENDING-PHASE8 | Head frozen at 88045b0 containing 9db4ab3 (done); three-role on-policy sentinel rerun outstanding
D-004-R275: PENDING-PHASE8 | This verifier runs on claude-fable-5; the sentinel reviewer spawns' explicit-model proof outstanding
D-004-R276: PENDING-PHASE8 | Rerun evidence must record Write/Edit unavailability honestly (procedure bound in capsule §3.4)
D-004-R277: PENDING-PHASE8 | Rerun guard-denial capture outstanding (strong corroboration: 4 live denials of this verifier by the merged guard at HEAD)
D-004-R278: PENDING-PHASE8 | Orchestrator post-sentinel `test -e` non-zero record outstanding
D-004-R279: PENDING-PHASE8 | Post-sentinel dirt sweeps + recheck outstanding (my pre-sentinel state: all suites green, sentinel absent)
D-004-R280: PENDING-PHASE8 | THIS report is the final-verification component; B-015 audit-log resolution + CLI acceptance outstanding
D-004-R281: PENDING-PHASE8 | Checkpoint-policy decision + task-only branch/worktree cleanup outstanding
D-004-R283: PENDING-PHASE8 | 17-item final return packet outstanding
D-004-R284: PASS | No stop condition triggered through this identity: main reconciled, all checks green, deviations disclosed not improvised, no simulated freshness
D-004-R285: PENDING-PHASE8 | Conduct row judgeable only after the return packet is delivered
D-004-R286: PENDING-PHASE8 | Answer content recorded (40% entry: producer-teammates rule + xhigh session-global, no per-spawn effort); delivery inside the return packet outstanding

## Summary

- **Counts:** PASS = 157; PENDING-PHASE8 = 20; FAIL = 0; BLOCKED = 0; UNVERIFIABLE = 0; NOT_APPLICABLE = 0. (177 total — matches the derived applicable set.)
- **PENDING-PHASE8 ids (20):** R135, R136, R137, R176, R177, R214, R215, R216, R268, R274, R275, R276, R277, R278, R279, R280, R281, R283, R285, R286. Each names its completing artifact above; all are Phase-8 completion acts that by design occur after this review in this session.
- **Amendment-6 capture integrity (non-blocking, confirmed):** working tree vs HEAD sorted-key JSON comparison — rows R001–R286 unchanged (zero edits, zero deletions); R287–R296 appended only, every one scoped to sentinel task id `D-004-PHASE8` (none touches the M0-T028 applicable set — derivation over the amended registry still yields exactly 177); `source-007-amendment.md` present as a new append-only file; `python tools/validate_directive_compliance.py --check` exit 0 on the working tree.
- **Non-blocking observations (report-level, for the orchestrator/owner; none changes a verdict):**
  1. G5 required corrections status: C3/C4 applied and delta-reviewed (d5eb642, both PASS); C1 is bound into the Phase-8 procedure (all four hook entries must be proven firing — partial live evidence already exists: the readonly-guard entry under the new quoted wiring denied this verifier 4 times in this session); C2 is an owner decision that the capsule (§5) states must be *recorded* (contract/defer/reject) before acceptance — the orchestrator must not accept without recording it.
  2. R024 tension, pre-existing practice: the six verbatim-preserved reviewer returns committed in PR #122 contain absolute user paths (evidence-path sections), consistent with the owner's 2026-07-16 verbatim-preservation rule and with 64 committed reports across the repo's history; the D-004 evidence lane itself (pilot reports, payload evidence, producer report, capsule, evidence map) is fully redacted. If the owner wants reviewer returns redacted too, that requires an explicit rule change; recorded here as an observation, not an M0-T028 violation.
  3. R054–R062 (original Step-3 confinement-layer rows): judged on execution-conduct primary evidence (harness worktree denials, guard denials, orchestrator port-diff, reviewer containment, dirt sweeps) plus the owner's amendment-5 re-contract; the full layer-2/3/4 hook infrastructure for Agent-Teams *producer waves* does not exist at HEAD and remains future Step-4 work the owner has explicitly not authorized (R178/R181).
  4. Guard over-denial of `>`-bearing read-only one-liners observed live 4× during this review (fail-safe direction; matches G5's INFO note).

VERDICT: PASS-PROVISIONAL — every applicable requirement is PASS (157) or PENDING-PHASE8 (20) with zero FAIL/BLOCKED/UNVERIFIABLE; the 20 pending rows await only the same-session Phase-8 completion acts (sentinel rerun evidence, B-015 resolution audit entry, CLI acceptance, final return packet, checkpoint decision) and a bounded second pass must finalize exactly those rows before D-004/M0-T028 may be called complete.

## Appendix D — directive-compliance-verifier bounded pass-2 return (verbatim)

# M0-T028 / D-004 — Bounded pass 2: finalization of the 20 PENDING-PHASE8 rows

**Verifier:** directive-compliance-verifier (read-only; producer ≠ verifier; I am the third of the three unnamed explicit-Fable-5 reviewer spawns and self-confirm I run on claude-fable-5)

**Identity re-confirmation:** `git rev-parse HEAD` = `88045b06ef12ccb9b994b4e8b38ffe40d9cadf04` (unchanged); `frozen_git_identity(allowed_paths, HEAD, exclude project-control/)` = `('126d2d53472deb8828ca4f007b5809b19e5c512ea2288b25499c27f12c0287c2', '88045b06…', None)` (unchanged, clean, no error). Completing artifacts are working-tree control-plane files under `project-control/`, outside the content identity by design. The 157 pass-1 PASS rows are untouched by this pass.

**Primary evidence reproduced for this pass:** `project-control/reports/M0-T028-PHASE8-fresh-session-report.md` read in full (§§1–11 + Appendices A–C; Appendix C is my pass-1 return, verbatim); `project-control/blockers/B-015-teammate-readonly-guard-bypass.json` compared field-by-field against `git show HEAD:` — status `open`→`resolved`, OPENED entry object-identical, exactly one appended orchestrator audit entry (1,594 chars) citing PR #121 / merge `9db4ab3…`, reviewed `e8a7dbf`+`d5eb642`, frozen head `88045b0`, the guard's own denial naming 'code-reviewer', independent `test -e` → exit 1, 136/0 suite, C1 proof, and residual routing (C2 "contract it", Steps 4–5 unauthorized, M0-T027 stays blocked), no other field changed; my own re-runs this session at this head: `test -e ./PILOT_SENTINEL.tmp` → exit 1 (twice), guard suite 136/0, project-control 14/14, directive-compliance 55 OK, validator `--check` exit 0; checkpoints directory still ends at CP-0033 (CP-0034 not pre-reserved); current dirt sweep = exactly B-015 (M) + amendment-6 capture (3 files) + the Phase-8 report (untracked) + machine-local `.npmrc`/agent-memory — no unexpected artifact, no sentinel. Live corroboration owned by me: the merged quoted-wiring readonly guard denied 6 of my own commands this session naming `directive-compliance-verifier`.

## Finalized verdicts (exactly the 20 rows)

D-004-R135: PASS | Phase-8 report §4: on-policy rerun performed post-merge and PASSED (verbatim tool-unavailability + verbatim guard denial + independent absence); doubles as the B-015 fix's end-to-end acceptance test, cited in the B-015 resolution entry
D-004-R136: PASS | §4: same three Step-1 reviewer roles (code-reviewer, control-plane-verifier, directive-compliance-verifier), frozen then-current main head 88045b0, explicit Fable 5 on every spawn (I am the third; self-confirmed claude-fable-5), sentinel repeated exactly once
D-004-R137: PASS | Guard denial OBSERVED (verbatim `_deny` text naming 'code-reviewer', §4/Appendix A(b), byte-matching the guard at HEAD) and INDEPENDENTLY verified (orchestrator test -e → exit 1 + ls + git-status grep; my own test -e → exit 1) — not reviewer assertion alone
D-004-R176: PASS | All three mandated components now complete: independent review (G3/G5 + delta at e8a7dbf/d5eb642), protected-main merge (PR #121, 28/28), fresh-session end-to-end rerun (§4 PASS)
D-004-R177: PASS | B-015 resolved ONLY after the passing sentinel and with zero FAIL/BLOCKED/UNVERIFIABLE across all 177 rows (pass 1 + this pass); acceptance is the queued CLI act that consumes these verdicts and is auto-refused if any precondition fails
D-004-R214: PASS | Live fresh-session Bash sentinel denied by readonly_agent_guard.py itself; denial evidence captured verbatim (§4, Appendix A(b)); corroborated by 6 live denials of this verifier at the same head
D-004-R215: PASS | Orchestrator independently ran `test -e ./PILOT_SENTINEL.tmp` → exit 1 ABSENT, recorded in §4; reproduced by me (exit 1)
D-004-R216: PASS | The required honest trio recorded exactly: tool-unavailability for direct Write (labeled as such, never credited to the guard) + guard's own denial for Bash + independent absence verification (§4)
D-004-R268: PASS | Merged hook/settings tested only in this genuinely fresh session; C1 proof covers all four entries (§2: SessionStart + UserPromptSubmit reminder contexts captured verbatim, dispatch guard fired on the three spawns + script-level proof, readonly guard proven by the live sentinel denial); no entry needed reversion
D-004-R274: PASS | §1: fetch/prune, main==origin/main==88045b0, ancestor check for 9db4ab3, status reconciled; head frozen; on-policy rerun with the same three roles executed (§4)
D-004-R275: PASS | Explicit Fable 5 passed on every gate-class reviewer spawn (§4 records the mechanism `fable`→claude-fable-5; my own spawn carried it and I run on claude-fable-5)
D-004-R276: PASS | Direct Write attempt remained unavailable and is reported honestly as TOOL-UNAVAILABILITY with the verbatim harness message (Appendix A(a)); no guard-credit claim anywhere
D-004-R277: PASS | Bash redirection denied by readonly_agent_guard.py itself with the guard's captured verbatim denial text naming the resolved 'code-reviewer' identity (§4, Appendix A(b))
D-004-R278: PASS | Orchestrator's independent `test -e` against the exact sentinel path recorded as exit 1 / ABSENT (§4), plus ls and git-status corroboration; reproduced by me at this head
D-004-R279: PASS | Post-test dirt sweeps identical to baseline (§5: 39 entries, no sentinel, no unexpected artifact); regression/directive checks re-run green (§6) and independently reproduced by me (136/0, 14/14, 55 OK, validator exit 0); my current sweep shows only the declared control-plane artifacts
D-004-R280: PASS | All four components in place in the required order: audit evidence appended on the permitted report surface (new M0-T028-PHASE8 report under reports/, per capsule §3.7); B-015 resolved by the orchestrator with the append-only audit entry citing merged fix + passing sentinel (verified against HEAD: OPENED entry byte-preserved); final independent verification completed by my two passes; CLI acceptance queued immediately after verbatim transcription, mechanically unable to precede these verdicts and auto-refused if any precondition fails
D-004-R281: PASS | Checkpoint decision policy-derived, not assumed (§11: GATES_AND_CHECKPOINTS requires one after integrating a task; CP-0034 only after acceptance; checkpoints dir verified still ending at CP-0033 — nothing pre-reserved); cleanup queued for ONLY task/M0-T028-readonly-guard branch + its worktree, husks explicitly excluded
D-004-R283: PASS | All 17 packet items verified bound and determined in recorded artifacts (§§1–9, §11 + lifecycle records: final SHA, PRs/merges, dependency state, amendment rows R168–R286/R287–R296, frozen SHAs, H2 + evidence location, fix, file inventory, test/CI, reviewer verdicts, sentinel result, B-015 entry, task/M0-T027 states, count/checkpoint, holds, prohibited-action confirmations); delivery is the orchestrator's mechanically-following final message — judged on bound content per the two-pass design, so recorded here explicitly rather than strained silent
D-004-R285: PASS | Conduct-to-date clean (this session contains only Phase-8/M0-T028 acts; e5d95b6..HEAD and the working tree contain no unrelated work); remaining session plan is enumerated and terminates at the packet (§11) — any post-packet unrelated work would be a new violation outside this verification's reach, stated plainly
D-004-R286: PASS | The owner's trailing question is answered honestly and the answer content is bound into the packet (§11 + the 40% progress entry restated: producer-class workers are NOT on Opus 4.8 — no producer teammate is permitted while B-015 was open, the coarse enum resolves opus→claude-opus-5 so Opus 4.8 is not per-spawn selectable and that is a recorded STOP condition if ever required, the sole producer ran inherit=Fable 5 non-downgrade; effort is session-global xhigh, unchanged, with no per-spawn control and no effort key ever written)

## Counts

- PASS = 20; FAIL = 0; BLOCKED = 0; UNVERIFIABLE = 0. (20 rows finalized — exactly the pass-1 PENDING-PHASE8 set; the 157 pass-1 PASS rows stand unchanged.)
- Final combined tally for the M0-T028 row: **177 PASS / 0 FAIL / 0 BLOCKED / 0 UNVERIFIABLE / 0 NOT_APPLICABLE** at frozen head `88045b06ef12ccb9b994b4e8b38ffe40d9cadf04`, content identity `126d2d53472deb8828ca4f007b5809b19e5c512ea2288b25499c27f12c0287c2`.

VERDICT: PASS — all 20 previously pending rows are satisfied by the reproduced Phase-8 primary evidence (live sentinel denial by the guard itself, independent absence verification, C1 four-hook proof, append-only B-015 resolution, bound acceptance/checkpoint/packet decisions), completing the 177-row applicable set with zero non-green rows; acceptance may proceed on these verdicts.
