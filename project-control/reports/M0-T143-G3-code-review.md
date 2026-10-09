# M0-T143 — G3 independent code review, preserved VERBATIM

Returned by the read-only `code-reviewer` agent through the agent-return channel on 2026-09-03;
saved verbatim by the orchestrator (transport entity-decoding only: `&gt;`/`&lt;`/`&amp;` decoded).

---

# GATE REPORT — M0-T143 (G3 independent code review)

**Task:** M0-T143 — D-024 Amendment 46: Codex `--output-schema` strict-subset repair, controller-side guarantee preservation, reviewer failure observability
**Reviewer:** code-reviewer (independent, read-only)
**Reviewed head:** `59f572c1410cd25df520bb9b58ffd75695fb7b2e` (confirmed via `git -C <wt> rev-parse HEAD`)
**Code commit:** `3f4cee8680ba5c9a167327507af387d316f5dbc3`; binding commit `05d0542cd0a15eeda4192745604bb48e2ab54d2b`
**Material identity:** `tools/agent_supervisor` subtree tree `209026fdf83b160b1d42f0009fdaccdd3148e52f` (committed, clean)

## VERDICT: PASS

Two MINOR findings, both non-blocking (below). No BLOCKING findings.

---

## Reproduction summary (commands + outputs)

- `git rev-parse HEAD` → `59f572c1…` (matches reviewed head).
- Working tree: `git diff HEAD -- project-control/tasks/M0-T143.json project-control/state.json` → **empty** (the porcelain "modified" flag is EOL/CRLF normalization only; no content change; code identity unaffected).
- `python -m pytest tools/test_agent_supervisor_mrl_provider_schema.py tools/test_agent_supervisor_mrl_codex_decision.py -q` → **71 passed**.
- `python -m pytest tools/test_agent_supervisor_mrl_one_shot_review.py -q` → **81 passed**.
- `python -m pytest tools/test_agent_supervisor_reviewer.py tools/test_agent_supervisor_codex_channel.py tools/test_agent_supervisor_ephemeral_review.py tools/test_agent_supervisor_cross_task.py -q` → **217 passed** (CodexReviewer consumers).
- `python tools/modularity_check.py --check` → **failures 0; warnings 12** (all pre-existing signals).
- Tree-SHA binding verify: `git rev-parse 3f4cee86^{tree}` → `04688351…` ✓; `git rev-parse 3f4cee86:tools/agent_supervisor` → `209026fd…` ✓ (both equal the binding file's `commit_tree_sha`/`subtree_tree_sha`).

Sandbox is Python 3.11.9 (repo targets 3.12); the four directly-affected suites collect and pass here (369 tests). Producer's captured full-suite run at the frozen candidate is 3626 passed / 2 skipped / 0 failed (288.69 s) — consistent with the supervisor-freeze baseline duty; I could not re-run the entire 3600+ suite in-sandbox but independently reproduced the load-bearing behavior below.

Independent behavior reproductions (scratch scripts, real modules):
- **Guarantee-preservation proof:** the flattened `review_verdict.schema.json` validated **alone** ACCEPTS overlong rationale, duplicate ids, empty rationale, empty ids, and overlong id; `ReviewVerdict.from_provider` REJECTS all five. This proves the bounds are genuinely removed from the schema and fully re-enforced at the controller boundary — no silent weakening.
- **Pre-spawn guard proof:** running `assert_codex_output_schema_strict` against the **pre-change** schema (`3f4cee86^`) raises `codex_schema_unsupported_keyword` (`…properties.rationale: keyword 'minLength' is not a structural keyword`) — i.e., the guard would have caught the exact defect class. `CODEX_STRUCTURAL_KEYWORDS` contains **none** of `uniqueItems/minLength/maxLength/minItems/maxItems`.

---

## Findings by review item

**(1) `schemas/review_verdict.schema.json` — flattened correctly. PASS.**
Only structural keywords remain (`$schema,$id,title,description,type,additionalProperties,required,properties,enum,items`). All five constraint keywords (`uniqueItems,minLength,maxLength,minItems,maxItems`) removed together in one change (`git show 3f4cee86 -- …review_verdict.schema.json` shows a single edit). `enum`/`required`/`additionalProperties:false` intact. Trust-boundary `description` is accurate and now documents the flatten + controller-side re-enforcement.

**(2) `mrl_codex_decision.py::ReviewVerdict.from_provider` — every removed guarantee preserved. PASS.**
Ordering is correct: `validate_instance(...)` runs first (enforces types/enum/shape/`additionalProperties:false`/required via the still-supported keywords), then the manual bounds. Equivalence to the removed schema keywords is exact, with correct boundary semantics (no off-by-one): `len(rationale) > 4096` (was `maxLength 4096`), `not rationale` (was `minLength 1`), `len(ids) > 64` (was `maxItems 64`), `not ids` (was `minItems 1`), per-id `not ref` / `> 128` (was item `minLength/maxLength`), `len(set(ids)) != len(ids)` (was `uniqueItems`), issued-ids-only (R502). `test_boundary_values_are_accepted` pins 4096/64/128 accepted and +1 rejected. Constants pinned to old schema values by `test_bounds_constants_are_the_old_schema_values`. No bypass; non-`Mapping` payloads rejected up front.

**(3) `mrl_provider_schema.py::assert_codex_output_schema_strict` — allowlist sound, walk complete, fail-closed. PASS.**
The allowlist is deny-by-default (`if key not in CODEX_STRUCTURAL_KEYWORDS: _refuse`), applied at every node, so it cannot false-accept a rejected keyword; the five proven keywords are all excluded (verified). Walk is complete: recurses object `properties` and array `items` (tuple-form `items` refused), requires `type` on every node, `additionalProperties is not False` refused, `properties` must be a non-empty map, `required` must equal `properties` exactly (every-property-required), `$schema`/`$id` allowed only at top, non-`Mapping` nodes refused. Typed fail-closed error `codex_schema_unsupported_keyword` (`NoReturn`). The keyword set is evidence-backed by the proven-live `codex_decision.schema.json` (run_m0t035_shadow_pilot_r6), which passes the same inspection (sweep test).

**(4) `codex_reviewer.py` + `mrl_one_shot_review.py` — wiring + observability. PASS (one MINOR).**
Pre-spawn `assert_codex_output_schema_strict` is invoked BEFORE any child in both reviewers — in `OneShotReviewer.review` it precedes even `resolve_chain`/`observe_version` (the `--version` probe), proven by `test_unsupported_schema_keyword_refuses_before_any_spawn` asserting `rh.calls == [] and rh.version_calls == []`. `bounded_stream_tail` redacts (`redact_text`) BEFORE slicing the last 600 chars, so a secret spanning the cut cannot leak; truncation marker is explicit. `no_decision_error` classifies `provider_rejected_request` vs `missing_decision_file`, each carrying returncode + both redacted bounded tails; `OneShotReviewer` now routes its `raw is None` branch through this shared helper (never the old bare `no_decision`). SUCCESS path is behavior-unchanged (the inspection is a no-op for the shipped schema; success-path tests pass). No secret/prompt leakage (seeded-token redaction test + 50k-noise truncation test pass).
- **MINOR (4a):** `CodexReviewer.review`'s timeout branch (`codex_reviewer.py:587-590`) does not append `failure_tails`, whereas `OneShotReviewer` (`mrl_one_shot_review.py:239-242`) does. This is an inter-reviewer inconsistency, not an R706 violation — R706 targets "every nonzero Codex exit," and both reviewers cover that via the shared `no_decision_error`; a timeout is a killed process, not a nonzero exit. Observability of a legacy-reviewer timeout is slightly thinner. Non-blocking.

**(5) Tests — behavior-shaped, defect named, no weakened assertions; fixture consistent. PASS (one MINOR).**
Tests assert on inputs→outcomes (error codes, rejected mutants, `rh.calls==[]`), not implementation internals. The defect is named directly: `test_provider_rejection_surfaces_parsed_error_and_tails` drives the owner fixture as stdout with exit 1/empty-stderr and asserts `provider_rejected_request` + `invalid_json_schema` + `'uniqueItems' is not permitted` + `returncode 1` + both tails. `test_provider_error_never_reduced_to_bare_no_decision`, `test_oversized_failure_stream_is_truncated_with_marker`, `test_credential_shaped_output_is_redacted_in_tails`, `test_timeout_failure_carries_tails` cover AS-CS-4. The retyped legacy test (`no_decision`→`missing_decision_file`) tightened, not weakened. Fixture `codex_schema_probe_20260902.jsonl` carries `error` + `turn.failed` events with `invalid_json_schema`/`uniqueItems`/`text.format.schema`/status 400 — consistent with the quoted provider error; parseable by `provider_failure_reason`.
- **MINOR (5a):** `CodexReviewer`'s NEW pre-spawn FAILURE branch (bad schema → refused `ReviewOutcome`, `codex_reviewer.py:557-571`) has no dedicated assertion (the equivalent exists for `OneShotReviewer`). The SUCCESS branch IS exercised by every `test_agent_supervisor_reviewer.py` case (constructed with the real `codex_decision.schema.json`), and the shared helpers are covered by the one-shot suite, so this is a coverage gap on the legacy path only. Non-blocking.

**(6) Binding + runbook + ps_test — coherently rebound to 3f4cee86. PASS.**
`source_binding.json`: `commit_sha=3f4cee86…`, `commit_tree_sha=04688351…`, `subtree_tree_sha=209026fd…` — all three independently verified equal via `git rev-parse`. `docs/CONTROLLER_UPDATE_RUNBOOK.md` §4 pin updated `f8f0f0c8…`→`3f4cee86…`; `ps_tests/test_runbook_parse.ps1` `$pinnedSha` updated identically (both in `05d0542c`).

**(7) Modularity / scope. PASS (one MINOR).**
Code commit touches exactly the 9 in-scope files (all in `allowed_paths`); binding commit is control-plane/docs only. No parallel implementation — reuses existing `provider_failure_reason`/`no_decision_error`. `modularity_check --check` → 0 failures. AS-CS-5 confirmed: the code diff introduces no model-selection surface, no `fable` alias, no `claude-fable-5-1` (all such strings appear only in `docs/SESSION_HANDOFF.md`/commit messages, describing verify-only pin behavior).
- **MINOR (7a):** `codex_reviewer.py` (854 physical lines) carries a pre-existing "above warning threshold" modularity signal and grew ~41 net lines. The growth is cohesive (reviewer-failure observability sits with the pre-existing `no_decision_error`/`provider_failure_reason` in the same module); no split warranted, but the checker warning persists. Non-blocking.

---

## Acceptance-scenario status (code-relevant)
AS-CS-1 PASS (single flatten, no constraint keywords). AS-CS-2 PASS (all enumerated mutants rejected controller-side; independently reproduced). AS-CS-3 PASS (typed refusal before any spawn; sweep over all provider-facing schemas passes). AS-CS-4 PASS (fixture-driven provider_rejected_request with parsed error/returncode/redacted bounded tails; unparseable→missing_decision_file; truncation + redaction proven). AS-CS-5 PASS (no model-selection/alias change). AS-CS-7 PARTIAL-in-sandbox: 369 affected tests pass here; full ≥1165 baseline relied on producer-captured 3626/0 at frozen candidate (recommend orchestrator confirm the CI full-suite green at `3f4cee86` before acceptance). AS-CS-8 PASS for `source_binding.json` (== frozen candidate); the single owner-run PowerShell command and its sha256, and R708/R709 canary-reporting/recovery-path wording, are documentation/DCV-scope and out of this G3 code review.

## Files reviewed (absolute)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\schemas\review_verdict.schema.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\mrl_codex_decision.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\mrl_provider_schema.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\codex_reviewer.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\mrl_one_shot_review.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\codex_schema_probe_20260902.jsonl`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_mrl_provider_schema.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_mrl_codex_decision.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_mrl_one_shot_review.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\source_binding.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\CONTROLLER_UPDATE_RUNBOOK.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\controller_update\ps_tests\test_runbook_parse.ps1`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T143-evidence.md` (cross-checked; RED/mutation/recovery-path claims consistent with independent reproduction)

## Recommendation to orchestrator
Record **G3 = PASS**. The three MINOR items (4a timeout tails on the legacy reviewer, 5a legacy-reviewer pre-spawn failure-branch coverage, 7a codex_reviewer.py size warning) are advisory follow-ups, not acceptance blockers. Before acceptance, confirm the full-suite green at `3f4cee86` from CI/orchestrator-captured evidence (AS-CS-7), since my sandbox (Python 3.11) verified only the four directly-affected suites; and note R708/R709/owner-script items fall to the qa-engineer and directive-compliance-verifier passes.

---

# GATE REPORT ADDENDUM — M0-T143 (G3), preserved VERBATIM (same reviewer, same wave)

The background full agent_supervisor suite has now completed in my own sandbox, independently reproducing the producer's baseline. This upgrades AS-CS-7 from partial to fully verified. Verdict is unchanged.

## GATE REPORT ADDENDUM — M0-T143 (G3)

**New reproducible evidence (in-sandbox, at reviewed head `59f572c1`):**

```
python -m pytest tools/ -q -k "agent_supervisor" -p no:cacheprovider
→ 3626 passed, 2 skipped, 571 deselected in 374.17s (exit 0)
```

This independently reproduces the producer's captured full-suite result (3626 passed / 2 skipped / 0 failed) at the frozen corrected candidate — run here on Python 3.11.9, zero failures. The 2 skips match the pre-existing supervisor-freeze baseline shape.

**AS-CS-7 — now PASS (was PARTIAL-in-sandbox):** the complete affected-suite run passes at the frozen candidate with 0 failures, well above the >=1165-test supervisor-freeze baseline duty. The earlier caveat (reliance on producer-captured evidence for the full run) is resolved — I have now reproduced it directly. No orchestrator-captured full-suite evidence is needed.

**Verdict unchanged: PASS.** The three MINOR advisory items stand (4a legacy-reviewer timeout tails; 5a legacy-reviewer pre-spawn failure-branch coverage; 7a `codex_reviewer.py` size warning) — none blocks acceptance. R708/R709/owner-script items remain out of G3 scope (qa-engineer + directive-compliance-verifier passes).

(Note: the completed background run was an automated task event, not any form of user approval — it changes only the evidence available to this report, nothing else.)
