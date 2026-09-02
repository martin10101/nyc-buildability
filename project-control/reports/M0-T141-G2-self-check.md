# M0-T141 G2 producer self-check (orchestrator, 2026-09-02)

| Check | Result | Evidence |
|---|---|---|
| Scope: only allowed paths touched | PASS | `git show --stat 2245de74` + `git show --stat 5a576837` — every path is in the packet's allowed_paths; forbidden paths (`schemas/`, `mrl_worker_result.py`) untouched (`git diff` empty there) |
| AS-DS-1 canonical unchanged | PASS | `test_canonical_in_memory_schema_is_never_mutated` + schema file byte-identical |
| AS-DS-2 Draft-7 provider copy | PASS | `test_provider_copy_declares_draft7_and_preserves_the_body` |
| AS-DS-3 no 2020-12 in serialized argv | PASS | `test_serialized_cli_argument_contains_no_2020_12_declaration` + argv assertions in `test_one_fresh_process_one_prompt_one_schema_bound_result` |
| AS-DS-4 fail-closed keyword walk | PASS | 15 parametrized refusal cases + 5 nested-position cases, all `draft7_schema_incompatible` |
| AS-DS-5 guard-removed = exact recorded error | PASS | `test_guard_removed_would_reproduce_the_exact_recorded_failure` (URI byte-equal to preserved stderr) |
| AS-DS-6 mutation proof + checks | PASS | Mutants M1–M6 all DETECTED; focused 89 passed; suite 3566 passed/2 skipped; ruff clean; modularity 0 failures; registry validator exit 0 |
| AS-DS-7 freeze rebind consistent | PASS | binding/runbook §4/ps_test `$pinnedSha` all `2245de74…`; controller_update ps harness 7/7 (includes the SHA-agreement tooth) |
| R672 failed-run evidence preserved | PASS | `M0-T141-canary-b502-schema-failure-evidence.md`; runtime dirs read-only |
| R679 no push/merge/provider call | PASS | branch local-only; no `git push`; no `start`/`doctor --live`; only read-only `status`/`recovery-status` probes |
| R674 M0-T140 still claimed; no reopen; R603–R605 untouched | PASS | ledger `M0-T140` status `claimed`; no accepted-task file modified; model_selection untouched |

Verdict: PASS — submit for independent G3/G4/DCV review (producer ≠ reviewer, R677).
