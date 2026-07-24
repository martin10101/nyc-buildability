# Correction + rebase capsule — M3-T001 producer (PR #100)

**You are a producer, not the controller.** Your PR #100 is red for two reasons; the controller has already
made the tiny control-file amendments you cannot make. Your job: relocate your fixtures, rebase, go green.

## What the controller already fixed on main (do NOT touch these files)
1. `tools/context_budget.json` — registered `docs/LEGAL_CORPUS_COVERAGE_MATRIX.md` in `board_allowlist`
   (it is a legitimate current legal-corpus coverage board, NOT historical).
2. `project-control/tasks/M3-T001.json` — your fixture `allowed_paths` were relocated to the conventional
   `packages/contracts/fixtures/{valid,invalid}/legal_source_manifest/` (+ `packages/contracts/fixtures/legal_source_manifest/` for your harness).

## Root cause
The CI contract validator (`.github/scripts/validate_contracts.py`) treats every `*.json` under
`packages/contracts/schemas/v1/**` as a **schema document** (requiring `$schema/$id/title/description`). Your
positive/negative fixtures live under `schemas/v1/fixtures/legal_source_manifest/` and are therefore misread as
schemas. The repo convention is that fixtures live under `packages/contracts/fixtures/{valid,invalid}/<schema>/`,
where the same validator **instance-validates** them (valid must pass; invalid must fail).

## Your correction (all within your amended allowed paths — do NOT weaken the validator or disguise fixtures)
1. **Rebase** `task/M3-T001-legal-source-authority` onto current `origin/main` (post-#99 + the amendments above).
2. **Relocate fixtures** (keep the SCHEMA at `packages/contracts/schemas/v1/legal_source_manifest.schema.json`):
   - `git mv` your `.../schemas/v1/fixtures/legal_source_manifest/positive/*` → `packages/contracts/fixtures/valid/legal_source_manifest/`
   - `git mv` your `.../negative/*` → `packages/contracts/fixtures/invalid/legal_source_manifest/`
   - `git mv` `check_m3_t001.py` → `packages/contracts/fixtures/legal_source_manifest/` and fix its internal paths.
   - Remove the now-empty `schemas/v1/fixtures/legal_source_manifest/` tree.
   Use `valid`/`invalid` dir names (validator convention), not `positive`/`negative`.
3. Update your producer report + any doc references to the new fixture paths.
4. **Do NOT** relabel `docs/LEGAL_CORPUS_COVERAGE_MATRIX.md` "historical" to pass CI — it is current; the
   controller allowlisted it. **Do NOT** edit `.github/**` or `tools/**` (control files). If you find the fix
   truly requires a control-file change, STOP and submit a short interface-change request.
5. Rerun local verification until green: `python .github/scripts/validate_contracts.py`;
   `python tools/context_budget_check.py`; your relocated `check_m3_t001.py` harness; the negative fixtures must
   still FAIL schema validation and positives PASS.
6. Commit + push; obtain **entirely green final-head CI**.

## Boundaries
- **B-011** remains an owner-controlled construction-code-scope decision. `docs/CONSTRUCTION_CODE_RELEASE_SCOPE.md`
  is a DRAFT for owner approval only — do not imply it is approved; its acceptance does not approve that scope.
- Do not merge, accept, or touch another task/worktree. Open only the one PR (#100 stays; you push a new head).

## After you go green
Reply here with your new head SHA; the controller independently reruns G3/G4/G5 + directive verification at the
rebased head and accepts M3-T001 (which then unlocks the sequential M3 chain).
