# M0-T028 — Fresh-session resume capsule (D-004 Step 3, Phase 8)

**Purpose:** D-004 forbids testing merged hook/settings behavior in the session that predates the
merge. This capsule is the complete input for the REQUIRED fresh Claude Code session that performs
Phase 8 (end-to-end sentinel validation, B-015 resolution, M0-T028 acceptance). Start a completely
new session, paste/point to this file, and follow it exactly. Reconcile everything live; trust no
SHA here blindly.

## 1. State at capsule time (verify live on resume)

| Item | Value |
|---|---|
| Implementation PR | #121, MERGED; merge commit `9db4ab328ea7e1570e347ae19174041d199aedc8` |
| Reviewed SHAs | base reviews at `e8a7dbfa2145b76f91b8e5272769a1447a940525`; C3/C4 bounded delta reviews at `d5eb642e9e7221fe173c4f8016986ee0dc3d3af8`; PR #121 merged exactly those commits (no further changes) |
| Directive capture | D-004 amendment 5 (`source-006-amendment.md`, rows R168–R286), PR #120, merge `4a4bf2d572edce963a355d9d997a2e05833c1dbf` |
| M0-T028 status | `awaiting_gate` (submitted at `9db4ab3` with evidence map `M0-T028-evidence-map.json`) |
| Gates completed | G0 PASS @ `4a4bf2d` (administrative readiness); G2 PASS @ `9db4ab3` (producer self-check); G3 PASS @ `9db4ab3` (report `M0-T028-G3-report.md`, reviewed `e8a7dbf` + delta `d5eb642e`, both PASS); G5 PASS @ `9db4ab3` (report `M0-T028-G5-report.md`, reviewed `e8a7dbf` + delta `d5eb642e`, both PASS, corrections C1–C4 recorded) |
| Supporting verifications | control-plane verification PASS (`M0-T028-control-plane-verification.md`); directive-compliance PRE-MERGE pass PASS (`M0-T028-dcv-premerge.md`); final directive verification (verification.json rows) PENDING BY DESIGN — happens in THIS fresh session |
| B-015 | **OPEN** (must stay open until the Phase-8 sentinel passes) |
| M0-T027 | **BLOCKED** (stays blocked; only its B-015 condition may be updated after the rerun; any further transition needs separate owner authorization) |
| Checkpoint / accepted count | CP-0033 / 49 accepted (M0-T028 would be 50th on acceptance) |
| G5 corrections status | C3, C4 APPLIED (delta `d5eb642e`, delta reviews PASS). C1 = fresh-session all-four-hooks proof (THIS session's job). C2 = follow-up-task proposal, OWNER DECISION pending (see §5) |

## 2. What changed on main (the merged fix)

- `.claude/hooks/readonly_agent_guard.py`: fail-closed identity resolution — no identity keys →
  lead pass-through; `READ_ONLY_AGENTS` → enforced; other known `.claude/agents/*.md` stem →
  pass-through; ANY other present identity (spawn names, agent_id-only, built-ins, unreadable
  roster) → enforced read-only; `main()` = fail-closed exception envelope around `_main()`.
- `.claude/settings.json`: all four hook entries in single-string form with the
  `${CLAUDE_PROJECT_DIR}` path double-quoted (R100). **The wiring form changed — hence C1.**
- `.gitignore`: `.claude/settings.local.json` (R101).
- `tools/test_readonly_agent_guard.py`: 136 checks = 89 pre-existing + 47 new.
- CRITICAL operational consequence: **writing producers must be spawned UNNAMED** (roster identity
  resolvable); any NAMED spawn and harness built-in agent types are fail-closed read-only.

## 3. Phase-8 procedure (in order; STOP on any non-green)

1. `git fetch --all --prune`; reconcile local main = origin/main; confirm it contains
   `9db4ab328ea7e1570e347ae19174041d199aedc8`; run `python tools/project_control.py status` and
   `python tools/current_state.py`; freeze the then-current accepted main head (40 chars).
2. **C1 hook-wiring proof (all four entries, new single-string form):**
   (a) SessionStart `directive_reminder.py` — the session-start context must show the directive
   reminder (capture it); (b) UserPromptSubmit `directive_reminder.py` — visible on the first
   prompt (capture it); (c) `agent_dispatch_guard.py` — fires on an Agent dispatch (the reviewer
   spawns below exercise it; capture evidence it ran or did not error); (d) `readonly_agent_guard.py`
   — the sentinel test below. If ANY entry does not fire: STOP, revert that entry to the
   `{"command": "python", "args": [...]}` form via a reviewed control change, re-review — do not
   proceed to acceptance.
3. **On-policy reviewer sentinel rerun (D-004-R134/R135):** spawn the same three reviewer roles as
   Step 1 — `code-reviewer`, `control-plane-verifier`, `directive-compliance-verifier` — each with
   an EXPLICIT Fable 5 model on the spawn, each instructed to pin the frozen head
   (`git rev-parse HEAD`) and invoke `/run-quality-gate`. Spawn them UNNAMED so `agent_type`
   carries the role. Pre/post dirt sweeps across the primary checkout and any worktree used.
4. Sentinel negative test (assign to the code-reviewer-role teammate):
   - Direct Write-tool attempt at `./PILOT_SENTINEL.tmp` → must remain unavailable/denied; report
     HONESTLY as tool-unavailability if that is the layer (do NOT claim the guard denied it).
   - Bash redirection `echo x > ./PILOT_SENTINEL.tmp` → must be DENIED **by
     `readonly_agent_guard.py` itself**; capture the guard's denial text verbatim (expected shape:
     `'code-reviewer' is operationally read-only: repository/GitHub/control-plane mutation and
     shell file-writes are blocked...`).
   - Orchestrator independently runs `test -e ./PILOT_SENTINEL.tmp` and records the non-zero/ABSENT
     result. Reviewer assertion alone is insufficient.
5. Full dirt sweeps after the test (primary checkout + every worktree); any unexpected file outside
   the deliberately named sentinel path = STOP.
6. Re-run: `python tools/test_readonly_agent_guard.py` (136/0), `python tools/test_project_control.py`,
   `python tools/test_directive_compliance.py`, `python tools/validate_directive_compliance.py`;
   secret scan; confirm main CI green.
7. **Only if 1–6 all pass:**
   - Append the audit evidence to M0-T028's permitted report surface
     (`project-control/reports/M0-T028-producer-report.md` appendix or a new
     `M0-T028-*` report file under reports/).
   - Resolve B-015 through the orchestrator with an audit-log entry citing the merged fix
     (PR #121, `9db4ab3`) and the passing fresh-session sentinel.
   - Complete the FINAL independent directive verification: the directive-compliance-verifier
     records per-requirement verdicts in `verification.json` (M0-T028 row, 177 applicable ids) at
     the frozen fresh-session identity (producer never records PASS there).
   - Accept M0-T028 via `python tools/project_control.py accept ...`.
   - Checkpoint ONLY if the established checkpoint policy actually requires one — do not assume or
     pre-reserve CP-0034.
   - Clean ONLY this task's branches/worktrees: local branch `task/M0-T028-readonly-guard` (remote
     already deleted), worktree `.claude/worktrees/M0-T028-readonly-guard`. (The pre-existing
     orphaned `agent-*` worktree husks remain NOT authorized for cleanup.)
   - Commit the lifecycle records (B-015 resolution, acceptance, verification.json, any checkpoint)
     via a protected-main control PR.
8. Deliver the FINAL RETURN PACKET per source-006 (17 items), including the owner's trailing
   model/effort answer (already recorded in the M0-T028 progress log at 40%).

## 4. Exact model requirements (D-004)

- Every gate-class reviewer teammate spawn: EXPLICIT Fable 5. (Verified mechanism: explicit
  `fable` resolves to `claude-fable-5`.)
- No producer teammate may be used before B-015 resolves; if any producer-class teammate is ever
  used post-resolution (Step 4+, NOT authorized now): explicit Opus 4.8 — NOTE: the coarse
  per-spawn model enum resolves `opus` to `claude-opus-5`, NOT Opus 4.8 (measured 2026-07-30,
  recorded in the M0-T028 40% progress entry); if Opus 4.8 cannot be explicitly selected when it
  is required, that is a STOP condition per source-006.
- NO effort key, ever, anywhere (D-004-R159 permanent). Session effort stays xhigh, global.

## 5. Owner decision pending (C2 — do not execute without GO)

G5 finding M-2 (pre-existing at base, codified by the fix): the guard authorizes writes negatively
— any `.claude/agents/*.md` stem outside `READ_ONLY_AGENTS` passes through (18 identities today,
including `human-journey-reviewer` and `visual-quality-reviewer`, which ADR-005 classifies as
read-only reviewers). Proposed follow-up task (needs owner GO to contract): invert to a positive
`PRODUCER_AGENTS` allowlist (or add the two reviewer roles to `READ_ONLY_AGENTS`), pin the
write-authorized set in a test so a roster addition fails CI, reconcile the two definitions with
ADR-005, and evaluate extending `agent_dispatch_guard.py` to refuse spawn names colliding with
roster stems. Acceptance of M0-T028 does NOT require the C2 work itself — it requires the owner's
decision on this proposal to be recorded (contract it, defer it, or reject it explicitly).

## 6. Forbidden in the fresh session (unchanged from source-006)

No D-004 Step 4 or 5; no M0-T029; no Agent Teams adoption or producer waves; no detection-only
substitute; no M0-T025; no M0-T019/PR #64; no second-wave product tasks; no expansion surfaces
(Master Expansion Architecture, six PRDs, Mission Control map, project/control graph, NYC Evidence
KG); no Graphify; no product code under M2–M7; no survey work; no deployment or hold release; no
effort setting or effort key; no handoff recreation; do not accept M0-T027 or start its Step 4
merely because the rerun passed; do not begin unrelated work after the return packet.

## 7. Session-local state notes (primary checkout, non-ledger)

- The owner-side security-audit tool's uncommitted `.gitignore` block (dated 2026-07-27) was
  preserved in `git stash` (labeled "owner security-audit .gitignore block (2026-07-27) preserved
  pre-M0-T028") plus a scratchpad patch copy, because tracked-file dirt in an allowed path blocks
  the CLI's fail-closed content-identity checks. Owner decides whether to re-apply, commit via a
  task, or drop it (its `.env`/key patterns largely duplicate lines already tracked).
- Long-standing untracked local files (`.claude/settings.local.json`, `.npmrc`, agent-memory
  modifications) are expected machine-local state, not task dirt.
