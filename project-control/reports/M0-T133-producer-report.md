# M0-T133 — producer report: controller-authoritative git-state checkpoint enrichment (D-024 Amendment 37)

The smallest durable fix for the journey-5 `invalid_checkpoint` (opus omitted
`branch`/`worktree`/`starting_sha`/`current_sha`): those four are now CONTROLLER-AUTHORITATIVE
envelope fields the controller fills from the dispatch context + a fresh read-only git measurement
*before* validation, with exact-normalized match-or-fail-closed for any the worker supplied.

## Design (R461-R466)
- **NEW `tools/agent_supervisor/checkpoint_envelope.py`** (pure, injectable git):
  - `normalize_sha` (full 40-hex or fail closed `ambiguous_sha`), `normalize_worktree` (Windows-safe
    lexical canonicalization: slashes, case, trailing/duplicate separators), `normalize_branch`
    (rejects empty / detached `HEAD`).
  - `measure_git_state(git, worktree)` — read-only `rev-parse --abbrev-ref HEAD` / `--show-toplevel`
    / `HEAD`; any failure → fail closed `git_unreadable`.
  - `CheckpointEnvelope.resolve()` — measures the live state, cross-checks observed==expected
    (`unexpected_branch` / `wrong_worktree` fail closed), returns the four canonical values
    (`starting_sha` from the pre-dispatch measurement, `current_sha` from the fresh one).
  - `enrich_checkpoint(chosen, authoritative)` → `(enriched_copy, added_fields)`: fills any absent
    field (recorded as added); requires an exact normalized match for any supplied field
    (`checkpoint_field_mismatch` fail closed, NEVER overwritten). Touches ONLY the four fields; the
    input mapping is never mutated (worker's original bytes preserved).
- **`claude_runner.py`**: `extract_checkpoint` split into `find_checkpoint_candidate` (find/dedup/
  single) + `validate_checkpoint` (from_dict+validate). `run_unit(..., checkpoint_envelope=None)`
  finds the candidate, records its digest as `checkpoint_original_digest`, and when an envelope is
  present resolves it + enriches BEFORE `validate_checkpoint`; an `EnvelopeError` becomes a
  fail-closed `invalid_checkpoint`. `RunResult` gains `checkpoint_enriched_fields` +
  `checkpoint_original_digest`. `extract_checkpoint` retained as the no-envelope composition.
- **`loop.py`**: injectable read-only `git` runner (default `subprocess_git()`);
  `_build_checkpoint_envelope()` measures the pre-dispatch `starting_sha` and builds the envelope
  from `authority.branch`/`authority.worktree`; `_audit_checkpoint_enrichment()` records
  `checkpoint_envelope_enriched` (added_fields + the worker's original digest + a "NOT worker-authored"
  note, R465). **SCOPE (R295 precedent):** enrichment applies to the certified unattended run
  (`limited-auto`) only — the exact place the journey-5 defect occurred and where no human validates
  the worker's git-state fields; `shadow`/`supervised` are human-observed and keep the worker-supplied
  path unchanged (this also keeps the existing shadow/supervised end-to-end tests green).

## What was NOT changed (R466)
`models.py` / the `ClaudeCheckpoint` schema is untouched — the four fields stay required and the
controller fills them. No change to semantic completion, evidence, status, review, advancement,
worktree-isolation, effect, budget, or owner-gate requirements; enrichment reads/writes only the four
envelope fields. No prompt-only wording fix; no bare Opus retry.

## Tests (R467-R468) — all 8 named scenarios, removal-sensitive
`tools/test_agent_supervisor_checkpoint_envelope.py` (18) + `tools/test_agent_supervisor_claude_runner_checkpoint.py` (6):
all-four-missing→enriched; partially-missing; supplied-matching; each supplied field mismatching
(param, 4); unreadable/ambiguous git (git_unreadable, ambiguous_sha, ambiguous_branch,
unexpected_branch, wrong_worktree); normalized Windows worktree paths (equivalent match / genuinely
different fail); the exact journey-5 opus shape (RED without enrichment on the four missing fields →
GREEN with it — the removal-sensitivity anchor); no false completion (only the four fields change;
BLOCKED status/summary/blockers preserved; a missing checkpoint is still `missing_checkpoint`, never
fabricated). Plus loop-level: limited-auto builds the envelope, shadow/supervised skip it, unreadable
pre-dispatch git leaves starting_sha empty (→ resolve fails closed), audit records only when enriched.

## Evidence at the frozen identity
Affected packs (runner/loop/cross_task/recovery/recovery_probes/checkpoint_journey/start_reentry/
loop_turnover + the two new files): **477 passed, 0 failed**. Golden pack: **42 passed**. ruff clean on
touched files; modularity exit 0 (`checkpoint_envelope.py` not flagged); command-doc 0 failures. Whole
suite recorded in the recertification report.
