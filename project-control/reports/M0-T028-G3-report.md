# M0-T028 — G3 independent code review (verbatim reviewer return)

Preservation note (report-preservation rule, `.claude/rules/project-control.md`): the reviewer
returned this report through the agent-return channel; it is saved verbatim below with transport
entity-decoding only (`&lt;` -> `<`, `&amp;` -> `&`, `&gt;` -> `>`). Reviewer: code-reviewer
(read-only, explicit Fable 5 spawn). Frozen SHA reviewed: e8a7dbfa2145b76f91b8e5272769a1447a940525.

---

# Gate Report

- Gate ID: G3 (independent code review)
- Task ID: M0-T028 (D-004 Step 3; blocker B-015 fix)
- Reviewer: code-reviewer (read-only, model claude-fable-5)
- Producer: backend-engineer (background subagent; diff ported to the task branch by the orchestrator — disclosed deviation, verified below)
- Result: **PASS** — with one required correction to record (report-count accuracy, F-1 below; per gate-verdict semantics the orchestrator records the correction, it does not require a code rework)
- Clean environment/worktree used: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard`
  - `git rev-parse HEAD` = `e8a7dbfa2145b76f91b8e5272769a1447a940525` (equals the frozen reviewed SHA)
  - `git status --porcelain` = empty (clean)
  - Branch `task/M0-T028-readonly-guard`, single commit, parent `4a4bf2d` (the stated base). Commit author/committer is the orchestrator (`martin10101`) — consistent with the disclosed harness-confined-producer/orchestrator-port division and ADR-005.

## Acceptance criteria reviewed

AS-1–AS-7, AS-9 in G3 scope; AS-3 unit-level only (live sentinel DEFERRED to the mandatory fresh-session rerun — verified as recorded, not treated as a gap); AS-8 corroborated (full pass is control-plane-verifier scope); AS-10 orchestrator-only, correctly not performed.

## Directive/requirement verification (scoped to this G3 gate)

The packet is in-regime (`directive_refs`: D-004, "ALL"). Per the packet's reviewer split, the exhaustive D-004 ALL-requirements pass belongs to the `directive-compliance-verifier` gate; below are the requirement IDs directly implicated by my G3 scope, each independently re-derived at the frozen SHA.

| Requirement ID | Reviewed SHA | Verdict | Reproduced evidence |
|---|---|---|---|
| D-004-R100 (hook path quoting) | e8a7dbf | PASS | All four `.claude/settings.json` hook entries are the canonical single-string form with `"${CLAUDE_PROJECT_DIR}/..."` double-quoted (lines 10, 19, 29, 39); no `args` lists; test section 12 (13 checks) proves shlex-split space-safety under a synthetic spaced root and real-root file existence; I ran the suite — all pass |
| D-004-R101 (settings.local.json ignored) | e8a7dbf | PASS | `.gitignore:64` `.claude/settings.local.json` (with a one-line R101 comment at line 63, Secrets section); `git check-ignore -v .claude/settings.local.json` from the worktree root returned `.gitignore:64:...`, exit 0 — attributed to the repo file, not a global excludes |
| D-004-R144 (index.json affected_tasks) | e8a7dbf | PASS | `project-control/directives/index.json` D-004 `affected_tasks` = `["M0-T027", "M0-T028"]` (verified by JSON inspection); producer report §4 states the correction was already made by PR #120 and nothing remained — AS-7's "explicit statement" branch satisfied with primary verification |
| D-004-R159 (no effort key) | e8a7dbf | PASS | Case-insensitive search for "effort" over all four changed files at HEAD: zero occurrences; `settings.json` contains only `$schema` + `hooks`. (The evidence report's mention of an observed payload field `effort={"level":"xhigh"}` is a harness observation, not a written key) |
| D-004-R132 (pilot reports immutable) | e8a7dbf | PASS | `git diff --name-status 4a4bf2d..HEAD` lists exactly 6 paths; neither `AGENT-TEAMS-PILOT-1.md` nor `AGENT-TEAMS-PILOT-2-PROBE.md` appears |
| D-004-R022/R053 (M0-T025 untouched) | e8a7dbf | PASS | M0-T025 in no form appears in the diff inventory |

## Steps independently executed (all read-only; no ledger/git-write/gh commands)

1. `git -C <worktree> rev-parse HEAD` → `e8a7dbfa2145b76f91b8e5272769a1447a940525`; `git -C <worktree> status --porcelain` → empty.
2. `git -C <worktree> diff --name-status 4a4bf2d..HEAD` → exactly: M `.claude/hooks/readonly_agent_guard.py`, M `.claude/settings.json`, M `.gitignore`, A `project-control/reports/M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md`, A `project-control/reports/M0-T028-producer-report.md`, M `tools/test_readonly_agent_guard.py`. Single commit, parent = base. Containment (AS-9) holds: CLAUDE.md, agents, rules, D-004 sources, product code all unchanged between base and HEAD by construction of the diff.
3. Full-file review of the guard and full unified diff of all four code/config paths.
4. Byte-identity proofs via `git show` piped to Python (no file writes): the command-classification region (`_MUTATING` comment block through `def _deny`) is byte-identical base↔HEAD (matching sha256 prefixes `4eabd280ff2f7493`); `READ_ONLY_AGENTS` assignment, `WRITE_TOOLS`, `_deny`, and the unparseable-payload fail-closed preamble byte-identical; test `main()` sections 1–6 byte-identical base↔HEAD (62 static `check(` sites → 89 runtime checks).
5. `cd <worktree> && python tools/test_readonly_agent_guard.py` → **ALL CHECKS PASSED**, exit 0. Programmatic count: **131 total checks, 0 failures = 89 pre-existing + 42 new**.
6. `git -C <worktree> check-ignore -v .claude/settings.local.json` → `.gitignore:64:...`, exit 0 (matches producer §6.5 verbatim).
7. D-004 `index.json` inspection → `affected_tasks: ['M0-T027', 'M0-T028']` (matches producer §6.7).
8. Hygiene scan of both committed reports (usernames, Windows/Unix absolute paths, "Downloads", session/prompt/pane IDs, long hex runtime IDs, token patterns): clean. Only hit is the producer report's own hygiene disclaimer sentence containing the word "pane" (line 384). The two full-length hex strings present are the base/reviewed commit SHAs (legitimate provenance).
9. Committed blob line-endings: `settings.json` and `.gitignore` are LF-only at HEAD (the CRLF warning in producer §6.6 was working-copy autocrlf noise, as the producer stated).
10. `python tools/validate_directive_compliance.py` in the worktree → `directive registry OK: 5 directive(s), 5 active...`, exit 0 (corroborates AS-8; full AS-8 remains control-plane-verifier scope).
11. Roster listing of `.claude/agents/` (25 `.md` stems incl. `orchestrator.md`, `frontend-engineer.md`, `backend-engineer.md`) — explains why pre-existing section-5 ALLOW expectations still hold under the new roster-gated logic.
12. Incidental live corroboration: two of my own review commands using `>` redirection were denied at runtime by `readonly_agent_guard.py` with the guard's exact denial text naming `code-reviewer` — the PreToolUse Bash layer demonstrably fires and denies reviewer shell writes in this session (this exercises the primary checkout's guard for a role-shaped identity; it is not the deferred named-teammate sentinel proof).

## Expected versus actual — scope items 1–7

1. **Guard resolution order** (`readonly_agent_guard.py:347-363`): exactly as specified — no-identity pass (lines 350-353); `READ_ONLY_AGENTS` enforce (falls through the `not in` block); known roster stem pass (355-358, only when `agent` truthy, so agent_id-only fails closed); anything else enforce. `_known_roster_agents()` (67-78) resolves `.claude/agents` relative to `__file__`, `.md` stems only, and `iterdir()` is consumed inside the `try` so missing-dir `FileNotFoundError`/`NotADirectoryError` (OSError subclasses) → empty roster → fail closed. `_identity()` (81-91) strips strings, maps `None`→`""`, coerces non-string JSON values to `str` — a former crash path (old code's `.strip()` on a non-string would have crashed the hook, which fails OPEN) now fails CLOSED; strictly stronger. Classification logic byte-untouched (proof in step 4). **No existing denial weakened**: the old enforcement set (agent ∈ READ_ONLY_AGENTS) is a strict subset of the new one; whitespace-only `agent_type` with a camelCase fallback now enforces where it previously passed. **No legitimate read-only command newly denied** for any previously-governed or lead/roster-producer identity: proven by the byte-identical classification region plus the 89 preserved checks (incl. all section-2/4/1d/1f allows) and the new allow cases in sections 7/8/9/roster-fail.
2. **Tests**: new cases cover the observed teammate shape (spawn name in `agent_type` + name-derived `agent_id`, role in no field — matching the evidence report §2.2), agent_id-only, roster producer pass-through (incl. mutating git and Write), lead no-identity pass, roster-read failure via a real subprocess against a byte-identical guard copy in a temp tree with no `../agents` (no monkeypatching), and the R100 space-safety proof. All 89 pre-existing checks preserved verbatim (byte-identity, step 4) and the full suite passes under my own execution (step 5).
3. **settings.json**: all four entries canonical single-string, double-quoted path; no other change in the diff; no new keys; no effort key.
4. **.gitignore**: the R101 entry at line 64 plus its one-line citing comment at line 63; nothing else (2-line diff).
5. **Containment**: exact (step 2).
6. **Report hygiene**: clean (step 8); the evidence report's redaction discipline (`<...>` placeholders, raw capture kept outside the repo) is verified in the committed text.
7. **Producer report vs. independent observation**: check-ignore output — matches byte-for-byte; diff inventory and per-file stat (80/20/2/183) — match; AS-7 JSON — matches; §6.1 verbatim suite output — matches my run line-for-line (131 PASS lines); validator output — matches. **One mismatch: the summary check counts (Defect F-1).**

AS-1/AS-2 (evidence): `M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md` is the orchestrator-captured primary artifact (capture division of labor recorded explicitly in its header, lines 4-7, as the task brief states); it records actual payload key sets for lead/named/unnamed spawns, the whole-payload role-string search (negative for named spawns), H1 REFUTED / H2 CONFIRMED with the exact fall-through mechanism, and the §4 reconciliation of the Step-1 tool-unavailability finding. The implemented fix matches its §5 contract verbatim. Verified as stored evidence — not re-captured, per the recorded protocol.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\.claude\hooks\readonly_agent_guard.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\tools\test_readonly_agent_guard.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\.claude\settings.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\.gitignore`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\project-control\reports\M0-T028-TEAMMATE-PAYLOAD-EVIDENCE.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\project-control\reports\M0-T028-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\project-control\tasks\M0-T028.json`

## Regression/security/provenance findings

- The fix strictly widens the deny set for spawned identities and touches no classification byte. Documented residuals are unchanged and disclosed (scripting-language writes; verb-in-variable without a tree target; producer report §7.3).
- Intended policy consequences, tested and documented (test 9b; guard docstring lines 22-25; producer report §3): (a) any NAMED spawn is fail-closed read-only regardless of underlying role; (b) harness built-in agent types (e.g. `general-purpose`) are fail-closed read-only. Operational consequence the orchestrator should internalize: writing producers must be spawned UNNAMED, and generic Task subagents can no longer write.
- Known residual, correctly recorded not silent (producer report §7.2): a spawn NAMED exactly as a roster producer stem (e.g. name `backend-engineer`) passes through — indistinguishable in the payload per the H2 evidence; naming is lead-controlled. Case-mismatch names fail closed (roster set is case-sensitive).
- AS-3 deferral verified as recorded in three places (producer report §5/§7.1; packet risk 2; owner_review_state Phase 8 condition). B-015 must not close and the task must not be accepted before the fresh-session sentinel rerun.

## Defects

- **F-1 (LOW, report accuracy — required correction, not code rework):** `project-control/reports/M0-T028-producer-report.md` line 67 ("All 90 pre-existing checks preserved verbatim and passing") and line 102 ("132 checks (90 pre-existing preserved verbatim + 42 new)") are each off by one. Reproducible reality: **131 total = 89 pre-existing + 42 new**. The report's own §6.1 "verbatim" output (lines 115-245) contains exactly 131 PASS lines and matches my independent run line-for-line — the attached evidence is correct; only the summary arithmetic is wrong. (The same "90 pre-existing" figure propagated into this gate's dispatch brief.) Reproduce: `cd <worktree> && python tools/test_readonly_agent_guard.py | python -c "import sys; l=[x for x in sys.stdin if x.startswith(('PASS','FAIL'))]; print(len(l))"` → 131; pre-existing boundary at `fail-closed: JSON non-object (array)` = check 89.

## Required rework

None to code, tests, settings, or .gitignore. For F-1: the reviewed report is committed at the frozen SHA and must not be silently rewritten — the orchestrator should record the corrected counts (89 pre-existing / 42 new / 131 total) in the gate/progress record (and in any future citation of this suite) per the gate-verdict-semantics precedent.

## Reviewer conclusion

**VERDICT: PASS** at reviewed SHA `e8a7dbfa2145b76f91b8e5272769a1447a940525`, with required correction F-1 recorded by the orchestrator. The B-015 fix implements the evidence-derived contract exactly, is fail-closed in every uncertain branch (unknown identity, agent_id-only, coerced malformed identity, unreadable roster, unparseable payload), weakens no existing denial, newly denies no legitimate read-only command for any previously-governed or pass-through identity, and leaves the load-bearing command-classification logic byte-identical. Tests reproduce the observed payload shapes and pass in full under independent execution. Containment is exact; reports are hygienic; R100/R101/R144/R159/R132 verified in scope. AS-3 live sentinel remains correctly deferred to the mandatory fresh-session rerun before B-015 closure or acceptance.

---

Orchestrator addendum (recorded at gate time, not part of the reviewer return): F-1 was recorded in
the M0-T028 progress log (60% entry) and corrected via the appended producer-report section 9 in the
C3+C4 bounded delta (d5eb642e), which received its own bounded G3/G5 delta reviews.
