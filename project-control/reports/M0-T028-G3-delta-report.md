# M0-T028 — G3 bounded delta review (verbatim reviewer return)

Preservation note (report-preservation rule, `.claude/rules/project-control.md`): the reviewer
returned this report through the agent-return channel; it is saved verbatim below with transport
entity-decoding only (`&lt;` -> `<`, `&gt;` -> `>`). Reviewer: code-reviewer (read-only, explicit
Fable 5 spawn; same reviewer as the base G3). Delta head reviewed: d5eb642e9e7221fe173c4f8016986ee0dc3d3af8.

---

# Gate Report

- Gate ID: G3 (bounded delta review)
- Task ID: M0-T028
- Reviewer: code-reviewer (read-only; same reviewer as the base G3 review at e8a7dbfa)
- Producer: M0-T028 producer (delta commit d5eb642, applying G5 required corrections C3 + C4)
- Result: **PASS**
- Clean environment/worktree used: yes — `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard`, pinned HEAD `d5eb642e9e7221fe173c4f8016986ee0dc3d3af8` (parent `e8a7dbfa2145b76f91b8e5272769a1447a940525`), `git status --porcelain` empty. Historical trees (parent SHA, pre-task 41957bb) extracted read-only via `git archive | tar` into the session scratchpad for independent execution.

## Acceptance criteria reviewed

Bounded delta only (base already PASSed at e8a7dbfa): (1) guard fail-closed envelope C3 correct and contained; (2) test section 13 well-formed and passing, F-1 boundary intact; (3) report appendix C4 append-only with correct arithmetic; (4) delta containment — exactly 3 files, +57/-1.

## Directive/requirement verification

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| C3 (G5 L-1) fail-closed exception envelope | d5eb642 | PASS | Envelope present in `.claude/hooks/readonly_agent_guard.py` (lines 380-391); crash shape reproduced against both guards: parent guard -> `AttributeError`, rc=1, no decision emitted (fail open); HEAD guard -> `{"permissionDecision": "deny", "permissionDecisionReason": "read-only guard: internal error (fail-closed)"}`, rc=0 |
| C4 (G3 F-1 / G5 L-4) count-arithmetic correction | d5eb642 | PASS | All three figures verified by execution, not text: pre-task suite (41957bb) = 89 PASS/0 FAIL exit 0; reviewed-SHA suite (e8a7dbfa) = 131 PASS/0 FAIL exit 0; delta suite (HEAD) = 136 PASS/0 FAIL exit 0. 131 = 89 + 42; 136 = 89 + 47 |

## Steps independently executed

1. `git -C <worktree> rev-parse HEAD` -> `d5eb642e9e7221fe173c4f8016986ee0dc3d3af8`; `git status --porcelain` -> empty.
2. `git diff e8a7dbfa..HEAD` (full, `--stat`, `--numstat`, `--name-status`) -> exactly 3 modified files, +57/-1 (guard 14+/1-, report 20+/0-, test 23+/0-). No mode changes, no other files.
3. Read the guard's full decision path and envelope; statically traced each section-13 payload through the HEAD guard code.
4. Ran `python tools/test_readonly_agent_guard.py` from the worktree -> **136 PASS / 0 FAIL, exit 0**; `grep -n` positions: check 89 = `fail-closed: JSON non-object (array)`, C3 checks at positions 132-136.
5. Extracted `.claude` + `tools` at parent SHA e8a7dbfa and at pre-task 41957bb (`git archive | tar -x` into scratchpad); ran both suites: parent = **131 PASS / 0 FAIL, exit 0**; pre-task = **89 PASS / 0 FAIL, exit 0**, last check = `fail-closed: JSON non-object (array)`.
6. `diff` of first 131 output lines (parent run vs HEAD run) -> identical; `diff` of first 89 lines (pre-task run vs parent run) -> identical.
7. Fed the governed + `tool_input:"not-a-dict"` payload directly to the parent guard copy and the HEAD guard (behavior-delta proof, step C3 row above).
8. Grepped the report: body lines 67 and 102 contain the erroneous "132 / 90 pre-existing" claims the appendix corrects; `grep -c "^PASS"` on the report = 131 (section 6.1 verbatim output is correct, as the appendix asserts).

## Expected versus actual

All expected values met exactly: HEAD SHA, clean tree, 3 files +57/-1, 136/0/exit 0 at HEAD, 131/0 at parent, 89/0 at pre-task, first-131 and first-89 output-line identity, check-89 boundary name, deny reason string byte-equal to the packet's expected `read-only guard: internal error (fail-closed)`.

## Human-style walkthrough findings

Not applicable (no UI). The guard's live enforcement was incidentally exercised: it denied this reviewer's own `>` file redirects (including to scratchpad) while allowing pipes, `git archive | tar` to a non-repo path, and test execution — consistent with its documented contract.

## Regression/security/provenance findings

- **Guard delta containment**: the diff contains exactly two hunks in the guard — the one-line `def main():` -> `def _main():` rename and the appended 13-line `main()` envelope. Identity resolution, roster handling, and command classification are byte-identical to the parent (nothing else appears in the diff).
- **Envelope correctness**: `except Exception` correctly excludes `SystemExit`/`KeyboardInterrupt`; `_main()` contains no `sys.exit` calls, so no control flow is swallowed. `_deny` writes a single JSON decision and returns; no double-output path exists (every `_deny` in `_main` is immediately followed by `return 0`). `__main__` still calls `main()` via `sys.exit`. Docstring is accurate: a crashed hook exits 1 -> non-blocking to the harness -> fail open; the envelope converts that to an explicit deny at exit 0. Style matches the file (deny-then-`return 0` pattern, no annotations).
- **Section 13 tests**: all five expectations verified independently against the code paths — governed + string/list `tool_input` -> `AttributeError`; governed + `{"command": 42}` -> `TypeError` in `_MUTATING.search`; named spawn (same TM literals as section 7) governed via the fail-closed non-roster path -> `AttributeError`; lead (no identity keys) returns at the pass-through branch before touching `tool_input` -> ALLOW (proves no over-deny). Helpers `bash_payload`/`check` reused idiomatically; the envelope's `json.dumps` output matches the `decision()` helper's deny detector.
- **F-1 boundary intact**: 89 pre-existing checks preserved verbatim (proven by execution and output-line diff across all three SHAs), + 47 new (42 base + 5 delta).
- **Report appendix**: single hunk appended at EOF (`@@ -383,3 +383,23 @@`, additions only); the reviewed body above is byte-identical to the parent version. Both arithmetic statements (131 = 89 + 42; 136 = 89 + 47) verified by running the suites.

## Defects

None blocking. Two cosmetic observations, no rework required:
1. Section 13 re-types the `TM_NAME`/`TM_ID` literals (`"m0t028-diag-probe"` / `"am0t028-diag-probe-0f3a"`) instead of reusing the in-scope variables from section 7. Values match exactly; maintainability nit only.
2. The appendix quotes the body claim as `"132 checks (90 pre-existing + 42 new)"` while line 102's exact phrasing is `"132 checks (90 pre-existing preserved verbatim + 42 new)"` — a paraphrase, not a misstatement; the referenced claims exist and the correction is accurate.

## Required rework

None.

## Reviewer conclusion

**PASS** for the bounded delta at `d5eb642e9e7221fe173c4f8016986ee0dc3d3af8`. C3 is implemented exactly as specified, demonstrably converts a previously fail-open crash into a fail-closed deny, and touches nothing else in the guard. C4 correctly and append-only records the F-1 arithmetic correction, and every count in it reproduces by execution. The suite stands at 136 PASS / 0 FAIL, exit 0, with the 89 pre-existing checks verbatim-preserved. Delta containment confirmed: exactly 3 files, +57/-1.

Key paths: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\.claude\hooks\readonly_agent_guard.py`, `...\tools\test_readonly_agent_guard.py`, `...\project-control\reports\M0-T028-producer-report.md`.
