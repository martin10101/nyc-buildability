# M0-T063 Unit A1 — rework evidence (41f84a4 → c45c39e)

How each round-1 blocking/major finding was closed, for the delta re-review and
the acceptance record.

| Source | Finding | Closure at c45c39e | Proof |
|---|---|---|---|
| G3 MAJOR-1 | tracked-only fingerprint diverges from the generator's all-eligible index → stale-index collision | `compute_fingerprint` now hashes EVERY eligible file (tracked+untracked); `tracked` is metadata, not an exclusion; snapshot uniquely determines the generator output | `test_untracked_content_change_moves_the_fingerprint` (the round-1 collision now fails to collide) + `test_untracked_eligible_file_is_indexed_and_flagged` |
| G3 MINOR-2 | recover() quarantines a live writer's temp dir | recover() skips a temp generation whose encoded pid is alive (`_temp_owner_alive`); only dead-pid orphans are quarantined | `test_live_writer_temp_dir_is_not_quarantined` |
| QA F1 | committed baseline evidence stale (corpus grew 422→426 via the merge) | regenerated at the final identity | committed export_digest `3d64d3b2a7584fc011db9aa7351e91a963094c5abc97503e72002f2dcc27f758`, 8418 nodes / 3420 edges / 426 files; reproduces at HEAD (ran twice, byte-identical) |
| DCV / QA minor | evidence-map `reviewed_sha: "SET_AT_SUBMIT"` placeholder | stamped to the frozen head at submit/accept | acceptance sequence |
| QA minor | `source_fingerprint` misread as generator identity | doc clarifies it is an input-corpus content fingerprint | pipeline doc baseline section |
| DCV | R037/R079 A2 parity obligation must be carried forward | the enforced byte-identical incremental-vs-full test is built in the A2 worktree (M0-T064) and passing; A1 delivers only the reference (no false completion) | M0-T064 test_repo_index_incremental.py::ParityInvariant |

## Test state at c45c39e
- `python -m pytest tools/test_repo_fingerprint.py tools/test_repo_index_cache.py tools/test_repo_index_baseline.py -q` → 34 passed, 1 skipped (symlink test needs OS privilege; runs on CI ubuntu).
- `python tools/modularity_check.py --check` → 244 files, 0 failures (each new module < 600 SLOC).
- Delta scope `git diff 41f84a4..c45c39e`: only tools/repo_fingerprint.py, tools/repo_index_cache.py, the two test modules, docs/CONTEXT_INTELLIGENCE_PIPELINE.md, and the two baseline-evidence files. No supervisor/code_graph/forbidden-path change.

## Behavior note (MAJOR-1 fix impact)
At a clean committed tree there are no untracked eligible files, so counts are
unchanged by the fix; the fix changes behavior only when untracked eligible
files exist (the iterate-before-commit case), where they are now hashed into the
fingerprint so A2 can never key a stale index on them.
