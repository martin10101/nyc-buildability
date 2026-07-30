# M0-T028 — G5 bounded delta review (verbatim reviewer return)

Preservation note (report-preservation rule, `.claude/rules/project-control.md`): the reviewer
returned this report through the agent-return channel; it is saved verbatim below with transport
entity-decoding only (`&lt;` -> `<`, `&amp;` -> `&`). Reviewer: security-reviewer (read-only,
explicit Fable 5 spawn). Delta head reviewed: d5eb642e9e7221fe173c4f8016986ee0dc3d3af8.

---

# Gate Report

- Gate ID: G5 (security) — BOUNDED DELTA review
- Task ID: M0-T028 (read-only agent guard; B-015 fix) — delta commit for G5 required corrections C3+C4
- Reviewer: security-reviewer (independent; read-only)
- Producer: M0-T028 producer (not this reviewer)
- Result: **PASS** (for the delta only; base verdict and open corrections C1/C2 unchanged)
- Clean environment/worktree used: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard` at pinned HEAD **d5eb642e9e7221fe173c4f8016986ee0dc3d3af8** (parent = previously reviewed e8a7dbfa2145b76f91b8e5272769a1447a940525); `git status --porcelain` empty.

## Acceptance criteria reviewed

Bounded-delta scope only: (1) C3 fail-closed exception envelope with `_main` body otherwise unchanged; (2) C3 test coverage, full suite 136/0/exit 0; (3) C4 append-only report appendix with corrected arithmetic; (4) delta containment (3 files, no settings/classification/effort/machine-data changes); (5) C1/C2 remain open and unclaimed.

## Directive/requirement verification

No `directive_refs` (D-nnn-Rnnn IDs) were named in this delta packet; the binding requirements are the G5 required corrections, verified individually:

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| C3 (envelope) | d5eb642 | PASS | Guard diff hunks are exactly `def main()` -> `def _main()` plus appended wrapper; `_main` body byte-identical to reviewed base. All four L-1 crash shapes re-run: now `rc=0` + `permissionDecision:deny` ("read-only guard: internal error (fail-closed)"). Same payloads against the extracted e8a7dbf guard: `rc=1`, traceback, no decision (fail-open) — envelope closes exactly those shapes. Lead (no identity keys) with tool_input as string/list and command-as-int: `rc=0`, no output (returns at the identity check before tool handling). |
| C3 (tests) | d5eb642 | PASS | `python tools/test_readonly_agent_guard.py` from the worktree: **136 PASS / 0 FAIL, exit 0**. Check 89 boundary = `fail-closed: JSON non-object (array)` (matches the G3/G5-established boundary); checks 132–136 are the five section-13 C3 checks. Test diff is +23/-0, a pure insertion before the FAILURES block — every pre-existing check unchanged. |
| C4 (appendix) | d5eb642 | PASS | Report prefix byte-identity proven programmatically: old blob is 22,614 bytes and `new[:len(old)] == old` is True; the appended text begins with the `## 9.` header. Appendix arithmetic independently re-derived: 131 = 89 + 42 at the reviewed SHA (confirmed 131 = 136 - 5 inserted checks; boundary at 89 re-confirmed in live output); 136 = 89 + 47 after the delta (confirmed by execution). Section 6.1 re-counted: exactly 131 PASS lines, matching the appendix claim. |
| Containment | d5eb642 | PASS | `diff --stat` = exactly 3 files, +57/-1, single commit `d5eb642` with parent e8a7dbf. Mechanical scan of the delta: no settings.json/.gitignore change, no classification-logic change (guard delta is rename + envelope only), no `effort` key, no usernames/absolute machine paths/session IDs in added lines (the two grep hits are pre-existing context lines). |
| C1/C2 open | d5eb642 | PASS | Mechanical grep of the delta for C1/C2/fresh-session/allowlist claims: clean. Appendix addresses only C3 and C4. C1 (fresh-session all-four-hooks proof) and C2 (allowlist-inversion follow-up) remain open and correctly deferred. |

## Steps independently executed

1. `git -C <worktree> rev-parse HEAD` -> d5eb642e9e7221fe173c4f8016986ee0dc3d3af8; `git -C <worktree> status --porcelain` -> empty.
2. `git -C <worktree> diff --stat e8a7dbf..HEAD` and full `diff`; `git log --oneline e8a7dbf..HEAD` -> one commit.
3. Read `.claude/hooks/readonly_agent_guard.py` at HEAD in full; confirmed the only changes versus the reviewed base are the rename and appended wrapper.
4. Ran the full suite: 136 PASS / 0 FAIL / exit 0; counted PASS/FAIL lines and located the 89/131/136 boundaries.
5. Re-ran my original L-1 reproductions (7 payloads) against the new guard via direct subprocess invocation with exit-code and stdout capture.
6. Extracted the base-SHA guard (`git show e8a7dbf:...`) to the session scratchpad and re-ran the same payloads: all four governed/named shapes crash rc=1 with no decision; lead rc=0 silent.
7. Byte-compared the report prefix against `git show e8a7dbf:project-control/reports/M0-T028-producer-report.md`; counted section 6.1 PASS lines.
8. Mechanical greps of the delta for machine data, effort keys, settings/gitignore refs, and C1/C2 claims.

Incidental live confirmation: my own first attempt to redirect suite output to the scratchpad was **denied by the guard itself** ("'security-reviewer' is operationally read-only… shell file-writes are blocked") — the deployed hook is actively governing this very review session.

## Expected versus actual

All expected values matched exactly: pinned SHA, empty status, 3 files +57/-1, 136/0/exit 0, deny-on-crash-shapes, lead pass-through, byte-identical report prefix, appendix arithmetic.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T028-readonly-guard\.claude\hooks\readonly_agent_guard.py` (envelope at lines 380–390; `_main` at 337–377)
- `...\M0-T028-readonly-guard\tools\test_readonly_agent_guard.py` (section 13 at lines 412–433)
- `...\M0-T028-readonly-guard\project-control\reports\M0-T028-producer-report.md` (appendix section 9, appended after byte 22,614)

## Regression/security/provenance findings

- **No new fail-open path.** The envelope only converts exceptions into a deny (exit 0 + `permissionDecision:deny`, the established blocking contract); return values pass through unchanged; `_deny` sits inside the `except`.
- **Residual: `_deny` throwing inside the `except` — judged ACCEPTABLE.** `_deny` is `sys.stdout.write(json.dumps(<static dict of ASCII strings>))`; `json.dumps` of that input cannot raise, so the only failure mode is a closed/broken stdout channel to the harness. In that transport-failure mode no in-process code path could deliver a deny anyway — the residual is irreducible at the hook level, not a defect of this delta.
- **Residual: `except Exception` does not catch `BaseException`** (`KeyboardInterrupt`/`SystemExit`). `_main` never raises `SystemExit`; signal interruption of a sub-second hook process is not an agent-controllable bypass. Acceptable; noted for the record.
- **Informational (LOW):** the appendix sentence "The delta received its own bounded independent review before merge (see the gate records)" was forward-looking at commit time. It is made true by protocol ordering — orchestrator: ensure this gate record is saved **before** merging, so the sentence is accurate from any merged reading. Not a defect.

## Defects

None in the delta.

## Required rework

None for the delta. C1 (orchestrator-captured fresh-session proof that all four hooks fire) and C2 (allowlist-inversion follow-up task proposal) remain open from the base G5 and must be tracked to closure separately; nothing in this delta discharges them.

## Reviewer conclusion

**Verdict: PASS.** Delta head pinned at **d5eb642e9e7221fe173c4f8016986ee0dc3d3af8**. The C3 envelope closes every fail-open crash shape I originally reproduced (proven by before/after execution against the extracted base guard), leaves the lead pass-through and all 131 pre-existing behaviors untouched, and introduces no new fail-open path; the suite is 136/0/exit 0; the C4 appendix is a byte-verified pure append with independently re-derived arithmetic and no machine data; the delta is contained to exactly the three expected files; C1/C2 remain correctly open. The orchestrator may record G5-delta PASS and proceed to merge, saving this report first.
