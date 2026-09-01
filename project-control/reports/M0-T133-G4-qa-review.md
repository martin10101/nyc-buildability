# Gate Report — G4 QA (independent) — M0-T133 (verbatim reviewer return, condensed)

- Gate: G4 (qa-engineer, independent, opus fallback). Producer: orchestrator-defect-runner.
- Clean isolated worktree reset to frozen `78f4d675`. Windows, Python 3.11.9.
- **Result: FAIL** (single blocking defect: modularity ceiling; all QA dimensions otherwise PASS).

## Test reproduction — all four producer claims reproduced exactly
| # | Command | Claim | Reproduced |
|---|---|---|---|
| 1 | new tests (checkpoint_envelope + claude_runner_checkpoint) | 24 (18+6) | **24 passed** |
| 2 | affected 11 packs | 477/0 | **477 passed, 0 failed** |
| 3 | golden | 42 | **42 passed** |
| 4 | WHOLE suite | 3067/2/0 | **3067 passed, 2 skipped, 0 failed** |

## 8-scenario coverage — all eight genuinely covered (AS-1..AS-8 mapped to named tests). Baseline
reconciles (3043 + 24 = 3067; 2 skipped == baseline, NO skip delta; no test removed).

## Removal-sensitivity (two SCRATCH mutants via sys.modules injection, no repo edit)
- **Mutant A** (enrich_checkpoint → no-op): **9 failed / 15 passed** — RED includes the journey-5 anchor,
  all four mismatch tests, all-missing, partial, genuinely-different-worktree, touch-only-envelope.
- **Mutant B** (resolve → lax, no measurement/cross-checks): **6 failed / 12 passed** — every resolve
  fail-closed path RED (git_unreadable, ambiguous_current_sha, detached_head/ambiguous_branch,
  ambiguous_starting_sha, unexpected_branch, wrong_worktree).
Every fail-closed path the packet names is proven load-bearing + removal-sensitive.

## D1 (BLOCKING) — required modularity gate fails closed, misreported as passing
`python tools/modularity_check.py --check` → **exit 1**:
`FAIL exception_exceeded: tools/agent_supervisor/claude_runner.py (1432) - grew past its reviewed
exception ceiling (1410)`. The M0-T130 exception (`max_lines: 1410`, "no growth headroom; a module split
is the recorded follow-up on the NEXT substantial growth") was TRIGGERED by M0-T133 (+22 SLOC) but not
honored; `tools/modularity_exceptions.json` is outside the task allowed_paths, so growth past 1410 was
not admissible in-scope. **Both the producer report and the G2 self-check misreport this as exit 0.**
Violates CLAUDE.md principle 16; fails CI on merge.

## Required rework (one of)
1. Reduce `claude_runner.py` ≤ 1410 SLOC (move the run_unit enrichment orchestration / RunResult plumbing
   into checkpoint_envelope.py / a thin helper, or extract the checkpoint find/validate functions), then
   correct the reports and re-gate; OR
2. Owner/G3-reviewed renewal of the `claude_runner.py` ceiling in `tools/modularity_exceptions.json`
   (add it to allowed_paths, bump max_lines/baseline_sloc with review evidence, honor/reschedule the
   split follow-up), then correct the reports and re-gate.

**VERDICT: FAIL** (route to rework; the engineering + QA are otherwise strong).
