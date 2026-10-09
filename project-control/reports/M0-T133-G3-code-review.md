# Gate Report — G3 Independent Code Review — M0-T133 (verbatim reviewer return)

- Gate ID: M0-T133-G3
- Task: M0-T133 (D-024 Amendment 37 — controller-authoritative git-state checkpoint enrichment)
- Reviewer: code-reviewer (independent G3, read-only, opus fallback)
- Producer: orchestrator-defect-runner
- **Result: FAIL** (single blocking defect: modularity ceiling; all six logic focuses PASS)
- Frozen SHA `78f4d6756f2b7334a6541cd6a4ee3383478998c5`, branch `control/D-024-fable-codex-loop`, tree clean.

## Logic focuses — all PASS
1. `enrich_checkpoint`: fresh shallow copy, iterates only ENVELOPE_FIELDS, fills absent + records added,
   exact-normalized match for supplied (raises `checkpoint_field_mismatch`), input never mutated, only
   the four fields touched. PASS.
2. Fail-closed completeness (R464): `git_unreadable`, `ambiguous_sha`, `ambiguous_branch`,
   `unexpected_branch`, `wrong_worktree`; `EnvelopeError` in run_unit → `checkpoint_error =
   "invalid_checkpoint: …"`, checkpoint None → loop routes to `stop("no_valid_checkpoint", …,
   PAUSED_RECOVERY)`. Pre-dispatch HEAD unreadable → starting_sha "" → fails closed at resolve. PASS.
3. `extract_checkpoint` split preserves behavior (find/dedup/missing/conflicting/multiple retained;
   `extract_checkpoint = validate_checkpoint(find_checkpoint_candidate(...))`; `checkpoint_question_decided`
   unchanged). PASS.
4. No weakening (R466/R471): `models.py`/ClaudeCheckpoint NOT in the diff; four fields remain required;
   `validate()` still runs on the enriched dict; BLOCKED status/summary/blockers survive; a no-candidate
   stream stays `missing_checkpoint`. PASS.
5. Limited-auto scoping (R295 precedent) sound; shadow/supervised keep the fail-closed worker-supplied
   path. PASS.
6. Windows normalization correct on the windows-latest CI target; circular import avoided via
   TYPE_CHECKING + duck-typing. PASS (with LOW doc advisory DEFECT-2).

## DEFECT-1 (BLOCKING, reproducible) — modularity ceiling exceeded
`python tools/modularity_check.py --check` → **exit 1**:
`FAIL exception_exceeded: tools/agent_supervisor/claude_runner.py (1432) - grew past its reviewed
exception ceiling (1410); renew through review`. The M0-T130 exception pins `max_lines: 1410` ("no
growth headroom; a module split is the recorded follow-up on the NEXT substantial growth"). M0-T133's
split + run_unit wiring + 2 RunResult fields pushed claude_runner.py to 1432 (+22) without splitting or
renewing (`tools/modularity_exceptions.json` NOT in the diff / outside allowed_paths). The required
`modularity` CI job (ci.yml:560-563) fails on this SHA → blocks merge; violates CLAUDE.md rule 16.
**Evidence contradiction:** the G2 self-check claimed `modularity_check --check: exit 0` — false at the
frozen identity (actual exit 1).

## DEFECT-2 (LOW, advisory) — `normalize_worktree` docstring (checkpoint_envelope.py:78-80) overstates
cross-platform case-equivalence (case-folding is Windows-only). No functional impact on the windows-latest
CI target.

## Required rework (either)
- **(preferred, matches recorded follow-up)** extract `find_checkpoint_candidate` / `validate_checkpoint`
  / `extract_checkpoint` (+ optionally `checkpoint_question_decided`) out of `claude_runner.py` into a
  focused module, preserving public imports via a compatibility facade (existing
  `from .claude_runner import extract_checkpoint` callers unaffected) — drops claude_runner.py under 1410
  and improves cohesion; OR
- renew the path-exact `claude_runner.py` ceiling in `tools/modularity_exceptions.json` with a reviewed
  cohesion justification + new expiry (expand allowed_paths to include it).
Then re-run the required teeth at the new SHA and correct the G2 self-check's modularity claim.

## No security/provenance regressions
`checkpoint_original_digest` computed from the worker candidate BEFORE enrichment; audit records added
fields + original digest + "NOT worker-authored". 24 targeted tests pass; the journey-5 removal-sensitivity
anchor is genuine; ruff clean.

**VERDICT: FAIL** (DEFECT-1 — modularity ceiling; fix by extraction or reviewed exception renewal, then
re-run at a fresh identity).
