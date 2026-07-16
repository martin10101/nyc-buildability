# Gate Report

- Gate ID: G3
- Task ID: M0-T009 (Canonical contracts v1)
- Reviewer: code-reviewer (independent; did not produce the work)
- Producer: backend-engineer
- Result: **PASS**
- Clean environment/worktree used: yes — reviewed at `.claude/worktrees/agent-ac0ceadafeac708be`, branch `task/M0-T009-contracts-v1`, head `522d3b2`. Reviewer's sandbox permitted read-only python execution, so all evidence below was independently re-run by the reviewer (stronger than verifying orchestrator-captured G2 evidence alone). Adversarial mutation tests were run in a throwaway `mktemp -d` copy; the worktree and main tree were never modified. Formed my own view from schemas/fixtures/validator/PRD/research doc first; read the producer report last.

## Acceptance criteria reviewed

`project-control/tasks/M0-T009.json` scenarios S1–S6, plus the orchestrator's nine mandatory focus items and the M0-T004 G3 carry-forward defects D1–D5.

## Steps independently executed

All commands run by the reviewer (not copied from producer evidence):

1. `python .github/scripts/validate_contracts.py` from worktree root (jsonschema 4.26.0 present) → exit 0; banner `meta-schema engines : stdlib-structural + jsonschema 4.26.0`; 6 schemas OK, 5 valid fixtures pass, 11 invalid fixtures correctly rejected, 3 broken schemas correctly rejected; `Checked 6 schema file(s); 0 failure(s).`
2. Same script with `jsonschema` import blocked via a `sys.meta_path` hook (simulating a CI runner without the package) → exit 0; banner `meta-schema engines : stdlib-structural ONLY (jsonschema not importable ...)` + explicit degraded-mode NOTE; identical 25 OK verdicts, including all three invalid_schemas rejections caught by the stdlib layer alone.
3. Adversarial tests in a temp copy of the tree (all behaved correctly):
   - TEST A malformed JSON `{ not json` planted in `fixtures/valid/source_fact/` → `FAIL ... does not parse as JSON`, exit 1.
   - TEST B valid fixture planted into `fixtures/invalid/source_fact/` → `FAIL ... fixture in 'invalid/' unexpectedly PASSED validation`, exit 1 (invalid-fixture-passes is itself a build failure, as documented).
   - TEST C BBL boundary probes against the shipped pattern: `5999999999` accept, `1000000000` accept, `0000477501` reject, `6000477501` reject, `10004775011` reject, `100047750` reject, `' 1000477501'` reject, `'1000477501\n'` **accept** (see Defect 1).
   - TEST D typo keyword `enmu` injected into `schemas/v1/coverage_status.schema.json` → `FAIL ... unknown/unsupported keyword 'enmu'`, exit 1.
4. `python project-control/reports/M0-T009-check-disclaimer.py` → `PRD bytes: 488 / TS bytes: 488 / PASS: disclaimer.ts matches PRD s29 byte-for-byte`, exit 0 (D4).
5. `git diff main...HEAD --name-only` scope audit; `git log` on `apps/web/src/lib/disclaimer.ts` (already fixed on main in `a0d8f3a`, so no change was needed by this task).
6. Grep verification of every grounding citation against `docs/research/M0-T002-geoclient-address-resolution.md` (lines 49, 83, 96, 120, 140, 163–166, 206).
7. Checked MAIN-tree `.github/workflows/ci.yml` contracts job: runs `python3 .github/scripts/validate_contracts.py` with no prior installs (lines 68–76) — matches the script's no-dependency degraded mode.

## Expected versus actual

### Scenario results

| Scenario | Case | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| S1 | normal | 6 schemas meta-validate (draft 2020-12); script enforces; CI job unchanged | Reviewer-run: all 6 OK in both engine modes, exit 0; ci.yml command path matches | PASS |
| S2 | provenance completeness (D1) | Every PRD §9 mandatory field required; fixture missing any one fails | `source_fact` `required` = all 11 PRD §9 elements + `provenance_id` (justified by PRD §19 resolvability); `missing_dataset_version`, `missing_effective_date_key`, `provenance_missing_conflict_status`, `fact_missing_provenance_ref` all correctly rejected in reviewer's run | PASS |
| S3 | real-data enums (D2) | Enums/BBL pattern match documented official values with citations; malformed BBLs rejected | Every citation verified against research doc; borough 6 / non-numeric / 9-digit fixtures all rejected by `^[1-5][0-9]{5}[0-9]{4}$`; platform-defined enums explicitly labeled, not passed off as government values | PASS |
| S4 | boundary | Exactly the 14 PRD §32.1 states; invalid state fails | Enum is 1:1 with PRD §32.1, same spelling, PRD order, no extras/omissions; `"compliance_declared"` rejected | PASS |
| S5 | invalid input | Broken fixtures → nonzero exit with per-file errors | All 11 invalid + 3 invalid_schemas rejected with clear per-file messages matching each fixture's `_expected_failure` note; reviewer's mutation tests A/B/D all exit 1 | PASS |
| S6 | regression | CI green path intact; D4 byte-match; README accuracy | Disclaimer byte-check PASS (488=488, U+2019 both); root README four-job list matches ci.yml; contracts README table matches the 6 shipped schemas exactly; ci.yml untouched (forbidden path respected) | PASS |

### Mandatory focus items

| # | Item | Finding |
| --- | --- | --- |
| 1 | source_fact ↔ PRD §9 1:1 | PASS. All 11 PRD elements required; `effective_date` nullable but key REQUIRED (absence visible, never silent — `missing_effective_date_key.json` proves it). Only addition is `provenance_id`, the reference key demanded by PRD §19 resolvability; no unjustified invented required fields. |
| 2 | analysis_state = PRD §32.1 | PASS. Exactly 14, exact spellings, PRD order. |
| 3 | BBL grounding | PASS. Pattern `^[1-5][0-9]{5}[0-9]{4}$` matches Geoclient User Guide v2.0.4 recognition rule and /v2/bbl zero-padding example (research doc lines 96, 120). All three invalid BBL fixtures fail on the pattern itself (rejection messages cite the pattern). All-zero block/lot honestly flagged OPEN, delegated to the Function BL connector — correct non-guessing behavior. |
| 4 | Fixture swap desk-check + execution | PASS. All 11 invalid fixtures traced by hand AND executed: each fails for its INTENDED reason (printed first-error matches `_expected_failure` in every case). `dangling_provenance_ref` is schema-valid and rejected ONLY by `profile_provenance_invariant()` (validate_contracts.py:343-364), proving the cross-reference check exists in code — correctly acknowledged as inexpressible in vanilla JSON Schema and documented as a backend obligation for live data. My planted-valid-fixture swap (TEST B) correctly failed the build. |
| 5 | jsonschema-absent path | PASS. Import guard at validate_contracts.py:72-77; loud banner both modes (lines 429-434); stdlib structural layer alone catches all three invalid_schemas cases (verified by actual blocked-import run, not just code reading). Notably `bad_keyword` (`requird`) is caught ONLY by the stdlib allowlist — the 2020-12 meta-schema ignores unknown keywords — so the stdlib layer is load-bearing, not decorative. Engine/mini-validator verdict disagreement fails the build (line 505). |
| 6 | Versioning | PASS. Schemas under `v1/`; `$id` must contain `/v1/` (enforced, line 394-396); additive-change policy + breaking→`v2/` documented in packages/contracts/README.md. `$id`s are absolute GitHub URIs but ALL `$ref`s are relative and resolved against a local in-memory registry (both stdlib `resolve_ref` and the jsonschema `referencing.Registry` path) — no network fetch, offline-safe; verified by the blocked-import and normal runs. |
| 7 | G3 standard cases | PASS. Normal: 5 valid fixtures. Boundary: borough 1 and 5 accepted, 0/6 rejected (TEST C); empty arrays and `effective_date: null` in valid fixtures. Missing/ambiguous: missing-key fixtures. Failure: malformed JSON fixture → loud FAIL + exit 1 (TEST A). |
| 8 | Regression/scope | PASS. Branch diff = contracts + fixtures + validator + READMEs + M0-T009 reports + producer agent-memory only. ci.yml (forbidden) untouched; MAIN ci.yml contracts job command invokes the script at its unchanged path with no installs. README statements verified accurate against ci.yml. |
| 9 | AI-boundary/provenance | PASS. coverage_status = exactly the 6 PRD §12 values; data_completeness = exactly the 3 values. Transition `actor` enum is `system|user` with deliberately no `ai` value (PRD §32.1). `normalized_value` description states normalization code, never AI, produces it. `confidence` description restates PRD §12 (confidence never substitutes for review status). |

## Evidence paths

- Worktree under review: `.claude/worktrees/agent-ac0ceadafeac708be` @ `522d3b2`
- Schemas: `packages/contracts/schemas/v1/{common,source_fact,property_profile,coverage_status,analysis_state,analysis_state_transition}.schema.json`
- Validator: `.github/scripts/validate_contracts.py` (invariant lines 343-364; import guard 72-77; engine banner 427-434; disagreement check 505)
- Fixtures: `packages/contracts/fixtures/{valid,invalid,invalid_schemas}/**`
- Orchestrator G2 evidence (main tree): `project-control/reports/M0-T009-G2-evidence.md` — consistent with my independent re-runs
- Research grounding: `docs/research/M0-T002-geoclient-address-resolution.md` lines 49, 83, 96, 120, 140, 163-166, 206
- CI wiring (main tree): `.github/workflows/ci.yml` lines 68-76

## Human-style walkthrough findings

A downstream consumer reading only the schemas can determine: what is required, why (PRD citations in every description), what is officially grounded versus platform-defined (explicit `PLATFORM-DEFINED` labels), and what is deliberately open (`OPEN-WITH-FLAG` for all-zero block/lot, ZIP+4, zoning district codes, geometry CRS). Deferred contracts (rule trace, scenario, report evidence item) are explicitly NOT stubbed so nothing can bind to unreviewed shapes — the right call under PRD §34. Error messages from the validator are per-file, specific, and actionable.

## Regression/security/provenance findings

- No secrets, no network calls, no new dependencies; text-only change, low-storage compliant; no large artifacts written anywhere (temp test dir deleted).
- Provenance enforcement is strictly stronger than the M0-T004 baseline; all carry-forward defects D1/D2/D3 verified closed, D4/D5 verified closed (D4 was already fixed on main in `a0d8f3a`; this task added the byte-check proof script).
- For G5: (a) confirm the jsonschema legacy `RefResolver` fallback path (validate_contracts.py:91-99) can never trigger a remote fetch if a `$ref` misses the local store — currently all refs resolve locally and CI does not install jsonschema, so exposure is theoretical; (b) the absolute `$id` URLs point at the public GitHub repo namespace — fine, but keep them out of any future `$ref` usage.

## Defects

All low severity; none gate-blocking; none require rework before acceptance.

1. LOW — Regex anchor edge: Python `re` `$` matches before a trailing newline, so `"1000477501\n"` passes the BBL pattern (and equivalently for bin/zip/date/date_time patterns) under BOTH shipped engines. Evidence: reviewer TEST C, `'1000477501\n'` → True. JSON Schema prescribes ECMA-262 regex semantics, where non-multiline `$` does not match before a trailing newline — a future JS validator (frontend/Vercel) would reject values a Python validator accepts, a cross-engine contract divergence. Fix additively when convenient: backend normalization must strip trailing whitespace before validation, or note the divergence in packages/contracts/README.md. File: `packages/contracts/schemas/v1/common.schema.json:9` et al.
2. LOW — Date patterns accept semantically impossible dates (e.g. `2026-99-99` for `effective_date`); `format` is annotation-only and the pattern checks digits only. Calendar validity is a backend-normalization obligation; worth one line in the README's backend-obligation notes. File: `common.schema.json:38-43`, `source_fact.schema.json:52-56`.
3. INFO — `profile_provenance_invariant()` hard-codes the two current fact sections (`lot_facts`, `existing_building_facts`). If a future schema revision adds `fact_value` usage elsewhere (e.g. zoning facts), the function must be extended in the same commit; the script's "extend allowlist + mini-validator together" header note does not mention this third co-update point. File: `.github/scripts/validate_contracts.py:353`.
4. INFO — No valid boundary fixture for borough 5 / edge-digit BBL (only invalid boundary fixtures exist). Reviewer covered it by direct pattern probes (TEST C); a `valid/property_profile` Staten Island fixture would make the boundary case self-documenting in CI.

## Required rework

None. Defects 1-2 are additive follow-ups suitable for the M1 connector-normalization tasks; 3-4 are notes for the next contracts revision.

## Reviewer conclusion

PASS. All six acceptance scenarios pass on independent re-execution; all five M0-T004 carry-forward defects (D1-D5) are verifiably closed; every enum and pattern traces to the official research doc or is explicitly labeled platform-defined/open; the validator is honest in both engine modes and its expected-failure machinery resists adversarial fixture swaps, malformed JSON, and schema corruption. Recommend orchestrator acceptance, then G4 after merge and G5 with the two focus notes above.
