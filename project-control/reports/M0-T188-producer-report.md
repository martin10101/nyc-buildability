# M0-T188 producer report — the ledger refuses a pattern entry in a packet's allowed_paths

Producer: backend-engineer (AI agent), isolated worktree
`/root/project/nyc-buildability/.claude/worktrees/agent-a7b7c0042eeef3329`.
Claim-seam head (contract): `b416cf0d154400ebf1dcaaabc199da4f4e25bc40`.
Backlog DB-181; owner directive D-090-R557; serves D-001-R146 / D-001-R110. Option B (refuse a
pattern; never expand it at identity time; rewrite no accepted record).

## Files changed (additive only — 419 insertions, 0 deletions)

- `tools/directive_registry.py` (+98): the shared detector `pattern_allowed_paths()` and the
  frozen `PATTERN_ALLOWED_PATHS_GRANDFATHERED` allowlist, beside `path_free_opt_in`.
- `tools/project_control.py` (+38): the shared CLI refusal helper and its wiring at claim/submit.
- `tools/validate_directive_compliance.py` (+42): the new static catch `c18`.
- `tools/test_project_control.py` (+89): lifecycle refusal test `test_s13_pattern_allowed_paths_seal`
  (the red proof + the claim/submit states), registered in `ALL_TESTS`.
- `tools/test_ledger_seal_literal_paths.py` (+152): the focused detector/allowlist/validator tests
  (was a tracked G0 placeholder; replaced).
- `project-control/reports/M0-T188-producer-report.md`, `-lookback-pattern-allowed-paths.md`
  (were tracked G0 placeholders; replaced).

No file outside the 7 `allowed_paths`. The identity algorithm (`_ls_tree_entries`,
`git_tree_manifest`, `frozen_git_identity` hashing, the empty-identity guard,
`GIT_LITERAL_PATHSPECS`) and the validator's `c17` are byte-unchanged (zero deletions in the diff).

## Where the detector sits and every place that calls it

- Detector: `tools/directive_registry.py:1353` `pattern_allowed_paths(allowed_paths) -> list`
  (magic chars at `:1350`; frozen allowlist at `:1385`). One detector, one place; both consumers
  import it so they can never diverge (the `path_free_opt_in` / D-001-R152 precedent).
- CLI: `tools/project_control.py:494` `_pattern_allowed_paths_check(t, task_id)` — called at
  **submit** (`:555`, inside `_directive_submit_check`, before `_task_git_identity`) and at
  **claim** (`:892`, right after `_directive_claim_check`).
- CI static catch: `tools/validate_directive_compliance.py:334`
  `_validate_pattern_allowed_paths(tasks_dir)` (check `c18`), wired into `validate()` at `:404`
  immediately after `c17`.

The CLI helper and `c18` are both scoped to **in-regime** tasks and both exempt the frozen
allowlist, so the refusal bites only NEW packets.

## Reproduced DB-181 numbers (read-only, at the claim head, before editing)

| pathspec (literal) | tracked files |
|---|---|
| `docs/measurement-basis/**` | 0 |
| `docs/measurement-basis` | 7 |
| `docs/measurement-basis/*` | 0 |
| `services/api/app/scenario/three_answers/result_way_bridge_*.py` | 0 |
| `apps/web/src/app/survey/review/[documentId]/page.tsx` (bracket route) | 1 |

All match the packet's VERIFIED NUMBERS. The bracket route binds literally (1 file), so it must
not be refused.

## The table of states (one test per input, with its id)

| state | input allowed_paths | behaviour today (pre-change) | behaviour after | test id |
|---|---|---|---|---|
| literal existing file | `['tools/directive_registry.py']` | accepted | accepted (no offenders) | S2 `test_pattern_detector_one_per_state` |
| literal existing folder | `['docs/measurement-basis']` (→7) | accepted | accepted (no offenders) | S3 same |
| `**` pattern | `['docs/measurement-basis/**']` (→0) | accepted; identity covers nothing | refused, names the entry | S4 same + S1 lifecycle |
| `*` in a file name | `['…/result_way_bridge_*.py']` (→0) | accepted | refused, names the entry | S5 same |
| literal path not yet created | `['tools/a_new_file_not_yet_created.py']` | accepted | accepted (emptiness is the separate empty-identity guard) | S6 same |
| mixed literal + pattern | `['tools/project_control.py','services/api/**']` | accepted | refused, names ONLY `services/api/**` | S7 same + S13 mixed arm |
| empty list | `[]` | accepted | no-op (path-free/empty-identity guard reached unchanged) | S8 same |
| literal bracket route | `['…/[documentId]/page.tsx']` (→1) | accepted | accepted (NOT a pattern) | S9 same |
| grandfathered (pre-existing pattern task) | any pattern, id in frozen list | accepted | still accepted (exempt; packet not rewritten) | `test_grandfather_allowlist_shape`, `test_cli_refusal_helper_arms`, `test_validator_static_catch_c18` |
| all accepted tasks still validate | `validate --check` before/after | exit 0 | exit 0 | S10 `test_migration_proof_zero_new_flags_on_real_ledger` + the CLI runs below |
| look-back report | script over `tasks/*.json` | — | 88 ids listed; no record rewritten | S11 `-lookback-pattern-allowed-paths.md` |
| no weakening + mutation | git diff | — | additions only; reverting fails S1/S4/S5/S7 | S12 mutation proofs below |
| modularity + Windows-safe | `modularity_check --check`; the code | — | exit 0; posix-string, no OS call | S13 statement below |
| **claim refusal (lifecycle)** | pattern + literal report, in-regime | **claim accepts (RED)** | claim fails closed naming the entry | S1 `test_s13_pattern_allowed_paths_seal` |
| **submit refusal (lifecycle)** | pattern + literal report, in-regime | **submit accepts (RED)** | submit fails closed naming the entry | S1 same |

## The red proof (one line)

Against the untouched tools reconstructed from the claim head, the S1 lifecycle test FAILED at
its claim assertion — the pre-change CLI printed `Claimed M9-T900 by producer-x` (returncode 0)
instead of refusing (`AssertionError: ... assert (0 != 0)`), proving the test genuinely catches
the defect; after the change the same test passes.

## The grandfather list — how it was generated

The frozen allowlist was produced by the look-back script (verbatim, with its full output, in
`project-control/reports/M0-T188-lookback-pattern-allowed-paths.md`) run over
`project-control/tasks/*.json` at the claim head: **88** pattern-carrying tasks (**77 accepted +
11 in-flight**), matching the packet's risk note. The constant holds exactly those 88 ids; it
never grows by hand. Completeness and non-growth are asserted by
`test_grandfather_allowlist_is_complete_for_real_inregime_tasks` and
`test_grandfather_allowlist_shape` (len == 88).

## Migration proof — validator exit 0 before and after

- BEFORE (untouched tools): `python tools/validate_directive_compliance.py --check` → **exit 0**.
- AFTER (changed tools): same command → **exit 0**.

What acceptance and the validator recompute on old tasks: `accept` recomputes a task's FULL
content identity only at the moment that task is accepted (never re-run on an already-accepted
task); the validator recomputes only EMPTINESS (`c17`) and now PATTERN-PRESENCE (`c18`), and never
compares an accepted task's full identity (`c10` compares stored sha to stored sha). Option B
changes no identity value (the identity algorithm is byte-unchanged), so no accepted task's
recorded identity moves, and the 88-id allowlist exempts every pre-existing pattern task, so `c18`
adds zero errors.

## Mutation proofs (each in a copy OUTSIDE the repository; each must FAIL)

- **M1 — detector neutralized** (`pattern_allowed_paths` discriminator forced to never flag):
  `test_pattern_detector_one_per_state` FAILED (S4/S5/S7 expected offenders, got `[]`) and
  `test_s13_pattern_allowed_paths_seal` FAILED (claim returned 0). `M1_EXIT=1`.
- **M2 — CLI refusal reverted** (pre-change `project_control.py`, no helper calls):
  `test_s13_pattern_allowed_paths_seal` FAILED (`Claimed M9-T900 by producer-x`, returncode 0).
  `M2_EXIT=1`.
- **M3 — validator c18 reverted** (pre-change `validate_directive_compliance.py`):
  `test_validator_static_catch_c18` FAILED
  (`AttributeError: module 'validate_directive_compliance' has no attribute
  '_validate_pattern_allowed_paths'`). `M3_EXIT=1`.

## Residual (documented limitation)

A pattern written ONLY with a bracket character range (e.g. `dir/file[abc].py`) is NOT flagged:
the detector excludes `[` / `]` so it never false-refuses the one tracked Next.js bracket route
`apps/web/src/app/survey/review/[documentId]/page.tsx` (S9). Such a bracket-range entry still binds
literally and matches nothing, so the empty-identity guard catches it when it is the only scope;
the gap is only the bracket-range-plus-literal-report shape, which no current packet uses. This is
the stated bracket-only char-range residual.

## Windows

Path handling in the detector is posix-string comparison (`startswith(":")`, `in`) with no OS or
filesystem call, so it behaves identically on Windows. This is NOT claimed tested on Windows — no
Windows machine ran it here.

## Checks a–f with DIRECT exit codes

- **(a) ruff** `python -m ruff check tools/directive_registry.py tools/project_control.py
  tools/validate_directive_compliance.py tools/test_project_control.py
  tools/test_ledger_seal_literal_paths.py` → **RUFF_EXIT=1**, reporting 4 errors, ALL at
  pre-existing lines not touched by this task (`project_control.py:131` E401 import line;
  `test_project_control.py:1134` E402, `:2243` E702, `:2443` F841 — existing S11 code). My
  additions are clean. **Configuration that applies:** the repository does NOT lint `tools/` in
  CI — the only ruff job (`.github/workflows/ci.yml`, job `api`) runs with
  `working-directory: services/api` and `ruff check .`, and there is no root ruff config. The 4
  errors are therefore pre-existing, unenforced repo state; I left those lines untouched (out of
  scope; fixing them would be unrelated churn).
- **(b) pytest** `python -m pytest -q -p no:cacheprovider tools/test_ledger_seal_literal_paths.py
  tools/test_project_control.py` → **PYTEST_EXIT=0**, `32 passed in 104.99s` (8 seal + 24
  project-control, i.e. the 23 baseline + the new S13).
- **(c) validator before/after** `python tools/validate_directive_compliance.py --check` →
  **VALIDATOR_BEFORE_EXIT=0** and **VALIDATOR_AFTER_EXIT=0**.
- **(d) modularity** `python3 tools/modularity_check.py --check` → **MODULARITY_EXIT=0**
  (724 files; 0 failures; 29 warnings, NONE for the three edited tool files). No cohesion
  justification required — directive_registry.py grew 1790→1888, project_control.py 1430→1468,
  validate_directive_compliance.py 596→638, all small additive; the check did not flag them and
  the file was not split.
- **(e) red proof + mutation proofs** — RED: S1 lifecycle test FAILED against untouched tools
  (`assert (0 != 0)`, `exit 1`). MUTATIONS: M1_EXIT=1, M2_EXIT=1, M3_EXIT=1 (all failed as
  required). All run in copies outside the repository.
- **(f) scope** `git status --porcelain` (clean after commit) and
  `git diff --name-status b416cf0d…HEAD` → only the 7 allowed paths (5 tool files + 2 reports),
  419 insertions, 0 deletions.

## No state-changing ledger command

No `new-task/claim/progress/submit/gate/accept/checkpoint` was run in the repository or the
worktree; all lifecycle exercises run in disposable temp git projects (as the existing suite
does). `tools/test_directive_compliance.py` was NOT run.
