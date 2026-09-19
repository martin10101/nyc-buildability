# M5-T043 — directive-compliance verification (verbatim verifier return; transport entity-decoding only)

Saved by the orchestrator from the directive-compliance-verifier agent return, 2026-09-19
(seq-118 wave, frozen head 20c597c1). Nothing added or removed beyond decoding transport
HTML entities.

---

All evidence reproduced. The facade re-exports the public seam symbols (`MatchedNamedStreetOverride`, `NamedStreetOverrideStatus`, `build_named_street_override_status`); `_fully_resolved_typed_inputs` is a private helper internal to the new module (no consumer imports it). AS-5 provider fail-safe test present. I have everything needed for the verdict.

---

# DIRECTIVE-COMPLIANCE VERIFICATION — M5-T043 (D-001 regime)

**Frozen head:** `20c597c1` (candidate/D-024-mrl-option-b) · **Material:** `f6e88222` · **Verifier ≠ producer** (producer = backend-engineer; I authored none of these changes)

**Registry check (LOADED):** `DirectiveRegistry('project-control/directives').load().evaluate_task_refs(M5-T043)` → `ok:true`, `applicable_ids == cited_ids == [D-045-R008, D-045-R009, D-066-R001]`, `missing:[]`, `invalid_refs:[]`, `unresolved:[]`. **Applicable == cited confirmed.**

**File identity:** all six M5-T043 source/test allowed-path files are byte-identical between frozen head `20c597c1` and working HEAD `11bed5f7` (`git diff 20c597c1 11bed5f7 -- <file>` empty for each), so source inspection and `modularity_check` on the working tree faithfully reflect the frozen head.

## Per-requirement verdict

| Req ID | Verdict | Primary evidence I reproduced (file · locus · observed value) |
|---|---|---|
| **D-045-R008** (sequencing / bounded increment) | **SATISFIED** | Material union = exactly the 7 files in `git show f6e88222 --name-only`: `wide_street_wiring.py`, `named_street_override_status.py`, `tests/rules/test_wide_street_wiring.py`, `tests/spatial/test_wide_street_live_provider.py`, `CalculationEvidence.tsx`, `__tests__/report-view.test.tsx`, `reports/M5-T043-producer-report.md` — **all 7 ⊆ allowed_paths**. Bookkeeping `876ea2b8` touches only `state.json` + `tasks/M5-T043.json` (control-plane, not source). **No `*.rule.json`** in the union. **Contract files byte-untouched:** no schema, no contract-TS types, no `integration.py`, no `response.py` in the union. **No consumer SOURCE file edited** — `git show f6e88222 --name-only` carries no `integration.py`/`api/v1/rule_evaluation.py`/`spatial/wide_street_live_provider.py`; the only provider-side file is its *test* (`test_wide_street_live_provider.py`). Facade preserves public imports: `wide_street_wiring.py:94-98` re-exports `MatchedNamedStreetOverride, NamedStreetOverrideStatus, build_named_street_override_status`. 475 consumer tests green = orchestrator-captured record (`M5-T043-ci-evidence.md`), corroborating the structurally-verified no-edit fact. |
| **D-045-R009** (preservation / scope limit) | **SATISFIED** | Added-line grep across all material source (`git show f6e88222 -- *.py *.tsx | grep '^+' | grep -i 'published\|verified\|compliance\|compliant'`) → **no matches**. DRAFT display assertions **survive**: `report-view.test.tsx` diff has zero removed content lines (only `--- a/` header + additions); at `20c597c1` the display suites carry 25 (report-view) and 61 (development-limits, untouched by material) DRAFT/not-verified/review assertions. Guard change is **tighten-only**: removed the vacuous `all(())`-True path → now explicit `False` (AS-3 `test_db028d…exceptions_checked_false`); safe attestation path now *requires* `override_table_implemented=True` — a hand-built `may_touch=False/implemented=False` shape that previously wasn't refused now **never clears** (AS-2 `test_db028c…never_clears_guard`, asserts `exceptions_checked is False`). Item (h) `CalculationEvidence.tsx` swaps **only** the non-review null-FAR fallback (`?? "Not calculated"`); the `wideReview ? "withheld — professional review required"` review-state phrase is preserved. Standing holds intact: task **not accepted** (status `in_progress`/later `awaiting_gate`), nothing merged. |
| **D-066-R001** (code-graph nav wiring) | **SATISFIED** | Nav block **present in packet** (`tasks/M5-T043.json` input #5, "CODE-GRAPH NAVIGATION BLOCK (D-066-R001…)") naming consumers with anchors — `integration.py:56, :514-520`; `api/v1/rule_evaluation.py:74`; `spatial/wide_street_live_provider.py:100`; the three suites — the **G3 extraction seam** (`MatchedNamedStreetOverride + _fully_resolved_typed_inputs + build_named_street_override_status`), and the `query.py --no-regen impact` instruction. Extraction **executed that seam**: `named_street_override_status.py` (frozen head) defines all three (`:48` class, `:99` `_fully_resolved_typed_inputs`, `:127` `build_named_street_override_status`); `wide_street_wiring.py` re-exports as facade. **Modularity improved** — I ran `python tools/modularity_check.py --check` → **exit 0, 0 failures**; neither `wide_street_wiring.py` nor `named_street_override_status.py` appears in the 21 warnings (the warned `named_street_override.py` is a distinct pre-existing module outside T043's paths). |

**CI (orchestrator-captured, verified from stored record):** `M5-T043-ci-evidence.md` reports combined head `a380a956` — CI `35412920210` **success**, secret-scan `35412920196` success, context-budget `35412920224` success. I independently confirmed `git diff f6e88222..a380a956 --name-only` ∩ T043 allowed_paths = **NONE** (touches only M5-T044 `dtm_condo_soda.py`+test, M5-T044 report, control-plane files) — the combined head's disjoint M5-T044 material is provably outside T043's paths.

## VERDICT: **PASS**

All three applicable requirements SATISFIED on reproduced primary evidence; no VIOLATED/UNVERIFIABLE result. No prohibited action observed (task not accepted, nothing merged/deployed; standing holds intact).

## Conditional restamp pre-authorization (peer-tolerant; M5-T042 DCV precedent)

I pre-authorize the orchestrator to restamp this PASS verdict (`reviewed_sha`) from `20c597c1` to a later head **`<H>`** **without re-review**, iff **all five** hold, **explicitly tolerating disjoint peer-task product commits** (files provably outside M5-T043's `allowed_paths` — e.g., M5-T044's `services/api/app/connectors/**` and its tests, plus control-plane bookkeeping) landing between `20c597c1` and `<H>`:

1. **Own-file byte-identity.** For every M5-T043 `allowed_path`, `git diff 20c597c1..<H> -- <path>` is empty under LF-normalization (M5-T043's own files byte-identical at `<H>`).
2. **Material identity stable.** `f6e88222` (or an LF-verified cherry-pick with identical tree for the 7 files) remains the sole M5-T043 material; the 7-file union is unchanged; no new commit edits any M5-T043 allowed_path.
3. **Disjoint-peer tolerance (explicit).** Any commit between `20c597c1` and `<H>` that changes files outside M5-T043's allowed_paths is a disjoint peer-task product commit or control-plane bookkeeping; `git diff 20c597c1..<H> --name-only` ∩ M5-T043 allowed_paths = **NONE**.
4. **Registry still resolves.** `evaluate_task_refs(M5-T043)` at `<H>` is `ok` with applicable == cited == {D-045-R008, D-045-R009, D-066-R001} — no new applicable requirement appears; `validate_directive_compliance.py --check` clean.
5. **CI green at the pinned head.** The required workflows conclude `success` at `<H>` (or the combined head `<H>` pins), orchestrator-captured.

If any condition fails (notably any change to an M5-T043 allowed_path, or a new applicable requirement), this pre-authorization is void and re-verification is required.

## Exact read-only commands run

```
git rev-parse HEAD ; git branch --show-current ; git status --short
git log -1 --format=... 20c597c1 ; git log -1 --format=... f6e88222 ; git merge-base --is-ancestor 20c597c1 11bed5f7
python -c "DirectiveRegistry('project-control/directives').load().evaluate_task_refs(M5-T043)"   # applicable==cited
python -c "print requirement bodies D-045-R008/R009, D-066-R001 from requirements.json"
git log --oneline -12 20c597c1
git show f6e88222 --name-only            # material 7-file union
git show 876ea2b8 --name-only            # bookkeeping = control files only
git diff 20c597c1 11bed5f7 -- <each T043 file>          # byte-identity frozen head vs HEAD
git show f6e88222 -- <src/tsx> | grep '^+' | grep -i 'published|verified|compliance|compliant'
git show 20c597c1:services/api/app/rules/named_street_override_status.py | grep -nE 'class MatchedNamedStreetOverride|def _fully_resolved_typed_inputs|def build_named_street_override_status'
git show 20c597c1:services/api/app/rules/wide_street_wiring.py | grep -nE 'named_street_override_status|MatchedNamedStreetOverride|build_named_street_override_status'  # facade
python tools/modularity_check.py --check ; (grep for wide_street_wiring|named_street_override_status)
git show f6e88222 -- .../wide_street_wiring.py | grep '^-' (removed guard: vacuous all(()), may_touch/implemented)
git show f6e88222 -- .../test_wide_street_wiring.py | grep '^+' (AS-2/AS-3 regression tests)
git show f6e88222 -- .../CalculationEvidence.tsx ; .../report-view.test.tsx   (item h + removed-line check)
git diff f6e88222..a380a956 --name-only ; python (intersection with allowed_paths = NONE)
git show 20c597c1:.../report-view.test.tsx | grep -ic 'DRAFT|...' ; development-limits.test.tsx
git show 20c597c1:project-control/reports/M5-T043-evidence-map.json ; M5-T043-ci-evidence.md
git show 20c597c1:.../test_wide_street_live_provider.py | grep -nE 'def test.*load|cache_clear|raise'   # AS-5
git show 20c597c1:project-control/tasks/M5-T043.json (status: in_progress/90 — not accepted)
```

I wrote nothing (no ledger, git, gh, or `verification.json` writes). Recording the verdict and writing `verification.json` is the orchestrator's action.
