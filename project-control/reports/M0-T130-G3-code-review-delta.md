# M0-T130 G3 delta re-review (VERBATIM reviewer return; saved unmodified by the orchestrator per the report-preservation rule)

Same independent code-reviewer context as round 1 (read-only). Rework identity
`fa13cf8b`. Verdict: PASS (C1/C2 discharged, O1 addressed; one cosmetic nit — the G2
self-check residual summary line — synced by the orchestrator in the follow-up commit
alongside the G4 +17-SLOC precision figures). Recorded by orchestrator 2026-08-31.

---VERBATIM-BEGIN---
Both blocking corrections are discharged and O1 is addressed. Here is my delta re-review.

---

# G3 Delta Re-Review — M0-T130 (rework at fa13cf8b)

**Prior verdict:** FAIL (C1: `modularity_check --check` exit 1; C2: false modularity PASS claims). **Rework identity:** HEAD `fa13cf8b`. Reviewer read-only.

## Runtime code unchanged (my correctness findings stand)
`git diff 20bfa449..fa13cf8b --stat` touches **no runtime file** — only `project-control/**` and `tools/modularity_exceptions.json`. `tools/agent_supervisor/claude_runner.py` and `tools/test_agent_supervisor_runner.py` are byte-identical to the identity I reviewed. My Section 2 correctness assessment (deferred-injection logic, edge cases, removal-sensitivity, honest repurposed test) therefore carries forward unchanged; the runner pack (78 passed) I already reproduced applies to identical bytes.

## C1 — DISCHARGED
Re-ran unpiped at HEAD:
```
$ python tools/modularity_check.py --check ; echo REAL_EXIT=$?
selected 335 files; failures 0; warnings 11
REAL_EXIT=0
```
No failure on claude_runner.py; the 11 warnings are pre-existing report-only signals unrelated to this task. I independently validated the exception entry against the checker's own rules (modularity_check.py:385-427):
- `kind=file`, path-exact `tools/agent_supervisor/claude_runner.py`, `max_lines=1410`, `baseline_sloc=1400`.
- Not over-broad: `material_growth_limit(1400) = 1400 + max(50,140) = 1540`; ceiling `1410 < 1540` OK.
- Not exceeded: current SLOC `1400 <= 1410` OK (narrow 10-SLOC headroom — a real ceiling, not a blank check).
- Not expired: `expires 2026-11-25` vs today `2026-08-31` (~86 days, within horizon) OK.
- Cohesion justification present; `review_evidence` cites my G3 report + the fix report + the delta report.
- Scope amendment recorded: `project-control/tasks/M0-T130.json` `allowed_paths` now includes `tools/modularity_exceptions.json`, so the exception edit is in-scope.

## C2 — DISCHARGED
Both artifacts now state the original claim was FALSE and give the honest account:
- `M0-T130-G2-self-check.md` (lines 19-29) and `M0-T130-reserved-turn-fix.md` s3 (lines 66-77): original "0 failures" was false; producer error = check run behind `| tail` (masking the exit code) plus ruff's "All checks passed!" misread as the modularity verdict; correct figure = 142 SLOC over baseline 1258 (~20 from this diff); the `20bfa449` commit-message "modularity 0 failures" is corrected by this note riding the rework commit (a committed message cannot be rewritten). Accurate and matches my reproduced numbers.

## O1 — DISCHARGED
`reserved-turn-fix.md` residual #1 (lines 81-91) now explicitly names the watchdog-bounded silent-swallow sub-case: if the exhausted CLI silently swallows the injected reserved turn (no result, stream open), the unit still rides the 900 s wall watchdog into a watchdog-bounded tree-termination — "narrower and safer than the original defect... but a wall ride nonetheless." This precisely captures my O1.

## Minor non-blocking nit (not a corrections item)
The `M0-T130-G2-self-check.md` one-line residual summary (lines 33-36) still reads "worst case lands in the fast honest-failure path" and was not synced with the corrected, more precise residual #1 in the fix report. Cosmetic inconsistency in a summary line; the authoritative residual disclosure (the fix report) is fully corrected. Non-blocking.

## Conclusion
Both blocking corrections (C1, C2) are discharged with reproducible evidence, O1 is addressed, and no runtime code changed — so the design/correctness/test findings from my original PASS-quality Section 2 stand. The change now passes the wired CI modularity gate and its evidence is honest.

VERDICT: PASS
---VERBATIM-END---
