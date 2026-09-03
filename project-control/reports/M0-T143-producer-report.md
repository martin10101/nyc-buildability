# M0-T143 — Producer report / G2 self-check (orchestrator-producer)

Reviewed content: frozen corrected candidate `3f4cee8680ba5c9a167327507af387d316f5dbc3`
(supervisor subtree tree `209026fdf83b160b1d42f0009fdaccdd3148e52f`); binding + reports land in
the follow-on control-plane commit without touching the subtree. Full evidence:
`project-control/reports/M0-T143-evidence.md`.

## Acceptance-scenario self-check

| Scenario | Verdict | Evidence |
|---|---|---|
| AS-CS-1 flatten in one change | PASS | one commit `3f4cee86` removes all five keywords together; structural walk test `test_flattened_review_verdict_carries_no_banned_keyword` asserts keys ⊆ structural set |
| AS-CS-2 mutation tests | PASS | existing `ReviewVerdictContractTests` (red 2-failed at flatten, green after) + new `M0T143ControllerEnforcedBoundsTests` (24 passed); recorded mutation pair (uniqueness disabled → 2 failed → restored → 2 passed) |
| AS-CS-3 pre-spawn inspection + sweep | PASS | `test_unsupported_schema_keyword_refuses_before_any_spawn` (zero spawns, `rh.calls==[] and rh.version_calls==[]`); `test_every_provider_facing_schema_passes_its_provider_inspection` (worker_result→Draft-7 projection; review_verdict+codex_decision→strict inspection); wired in BOTH reviewers |
| AS-CS-4 observability | PASS | fixture-driven `test_provider_rejection_surfaces_parsed_error_and_tails` (`invalid_json_schema`, `'uniqueItems' is not permitted`, returncode, both tails, audit row); `missing_decision_file` retype; truncation-marker + redaction + bounded-message tests; timeout tails; no live provider call |
| AS-CS-5 model pin | PASS | no model-selection surface in the diff; `git grep` of the change introduces no `fable` alias / `claude-fable-5-1`; owner script validates the doctor `model_selection` row |
| AS-CS-6 recovery determination + reporting semantics | PASS | evidence report §6 states explicitly: NO supported review-resume (CYCLE_ENTRY_STATES + pending-prompt absence) → ONE successor full canary via `resume-after-answer` + `start`; §7 records the corrected item semantics (3 split legs, 8 PASS, 10 NOT_RUN) |
| AS-CS-7 focused + one full frozen run | PASS | focused 339 passed pre-append; per-file 47/24/81 green; full suite at `3f4cee86`: **3626 passed, 2 skipped, 0 failed** (288.69 s, raw exit 0; 2 skips = pre-existing baseline shape) |
| AS-CS-8 binding + one owner command | PASS (command deployment follows gates) | `source_binding.json` → `3f4cee86`/`04688351`/`209026fd`; exactly one owner-run PowerShell command deployed to `ctl24-activation` with recorded sha256; this session does not execute it, push, or merge |

## Constraints honored

- R700/R701: exactly one bounded task; no reopened accepted work; no re-investigation of the
  proven-healthy surfaces.
- R712: no owner-script execution, no push, no merge, no unrelated work.
- Supervisor-freeze §3: qualifying evidence cited in the task packet and the code commit message.
- Modularity: no new module; `mrl_provider_schema.py` grew within its cohesive responsibility
  (provider-facing schema safety); checker clean on touched files.

## Known limits (honest)

- The strict-subset keyword allowlist is inferred from the provider-proven profile
  (`codex_decision.schema.json` live PASS) + the captured 400; the provider's full subset is not
  published. The inspection is deliberately narrower-or-equal (fail-closed), so a false REFUSAL
  is possible for an exotic-but-supported schema; a false ACCEPT of the five proven-rejected
  keywords is not.
- Legacy `CodexReviewer` gains the same inspection + tails through the shared helpers; its
  fake-driven suites (`reviewer`/`ephemeral_review`/`codex_channel`) pass unchanged except the
  documented bounded-message interplay (tail bound sized to the existing ceiling).
