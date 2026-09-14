# G5 Security & Privacy Gate Report — M5-T027

> Saved VERBATIM by the orchestrator from the security-reviewer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.

**Task:** M5-T027 — D-059 step-1 scenario-layer correctness fixes (recorded-data semantics, bldgarea-zero-with-buildings fail-closed, evaluation-derived labels)
**Reviewer:** security-reviewer (independent, read-only)
**HEAD verified:** `git rev-parse HEAD` = `4a8d90555914947419fbbbe124c9c048187454f1` — matches expected pin exactly.
**Material content commit reviewed:** `77558eb583ea9ba8105faf7810b2ba31cf48f036` (read via `git show 77558eb5`).
**Complete changed-file surface (verified via `git diff-tree --no-commit-id --name-only -r 77558eb5`):**
```
project-control/reports/M5-T027-producer-report.md
services/api/app/scenario/builder.py
services/api/app/scenario/constants.py
services/api/app/scenario/unused_floor_area.py
services/api/tests/scenario/test_scenario_foundation.py
services/api/tests/scenario/test_unused_floor_area.py
```
This matches exactly the task packet's `allowed_paths` (`project-control/tasks/M5-T027.json`) and the "complete surface" named in the review instructions — nothing extra, nothing missing.

## What I inspected vs. executed
Inspected (read-only, via `git show`/`Read`/`Grep`): the full commit diff for all 6 files, the full current content of `services/api/app/scenario/unused_floor_area.py`, the import blocks of all three changed source modules, the task packet, the producer report, and the frontend consumer of the changed data (`apps/web/src/components/compare/ScenarioAssumptions.tsx`), plus a grep across `apps/web` for `dangerouslySetInnerHTML`/`innerHTML` and a grep across `services/api/app/scenario` for logging calls and secret-like tokens. I did not execute pytest/ruff myself (read-only reviewer, no write/exec mandate needed here — the diff is self-contained and fully inspectable statically; no G5 finding in this report depends on a test run).

## G5 surface-by-surface determination

| Surface | In scope? | Evidence |
|---|---|---|
| Auth / session / tenancy (RLS, cross-tenant isolation) | **Untouched** | No import of any auth/session/db/Supabase module in any of the 3 changed source files (`grep -n "^import\|^from"` over `builder.py`, `constants.py`, `unused_floor_area.py` — only `__future__`, `math`, `typing.Any`, and sibling in-package `. import constants` / `.models`). The functions are pure, side-effect-free transforms of already-authorized, already-fetched `property_profile` / `rule_evaluation` dicts passed in by the caller. No DB/query code anywhere in the diff. |
| Secrets / credential handling | **Untouched** | Grep for `(?i)(api[_-]?key|secret|password|token|bearer|service[_-]?role|supabase)` across `services/api/app/scenario/` returns only pre-existing, unrelated "Verified token" security-language hits in `ranking.py`, `breakeven.py`, `sensitivity.py`, `_json_safety.py` — none of which are in this commit's file list. |
| Filesystem / storage / uploads | **Untouched** | No file I/O, no storage-client import, no upload-handling code anywhere in the diff. |
| External network calls / SSRF | **Untouched** | No `requests`/`httpx`/socket import added; import list confirmed above is exhaustive and unchanged in kind from before. |
| Deserialization of untrusted input | **Untouched** | The functions only read already-parsed Python dicts (`property_profile`, `rule_evaluation`/`trace`, `cap_provenance`) that were built upstream by the (unmodified) rule engine and profile builder, both outside `allowed_paths`. No `json.loads`/`pickle`/`eval` on raw bytes introduced. |
| Logging / sensitive-value redaction | **Untouched** | `grep -n "logger\.\|logging\.\|print("` over `services/api/app/scenario` returns zero matches. No logging statements exist in this module before or after the change. |
| Administrative / deployment behavior | **Untouched** | No new endpoint, no new admin route, no config/deployment file in the diff (confirmed via file list above). `professional_review_required` is a pre-existing, already-widely-consumed workflow display flag (44 files reference it); this change only makes an *existing* flag fire in one additional fail-closed case — it does not add or remove any access-control gate. |
| Dependency / lockfile / config | **Untouched (verified from diff, not producer claim)** | `git diff-tree --no-commit-id --name-only -r 77558eb5` lists exactly the 6 files above; a follow-up targeted diff against `services/api/pyproject.toml`, `requirements*.txt/in`, and `packages/**` in the same commit returns nothing. `services/api/app/connectors/**` is untouched (task's `forbidden_paths`, confirmed empty in the diff). |
| Prompt-injection defenses | **Untouched / not applicable** | No AI/LLM call anywhere in this code path; this is the deterministic scenario-calculation layer per the repo's own AI/deterministic-boundary principle. Nothing here parses free text into an AI prompt. |
| Data exposure via output document | **In scope — reviewed in depth (see F/A below)** | New fields/text now flow into the response document (`cap_label`, `reasons[0]`, `coverage_matrix[].governs`, two new `assumptions` entries in the `unused_draft_zoning_floor_area` section). |
| Injection/rendering safety of new interpolated strings | **In scope — reviewed in depth (see F/A below)** | New f-string interpolations of `section_reference`, `cap_rule_id`-derived family label, and `raw_numbldgs_value`/`usable_numbldgs_value`. |
| DoS / resource safety | **In scope — reviewed, no issue found (see below)** | New branch and helper functions in `unused_floor_area.py`. |

## Data-exposure analysis (item 2 of the brief)

1. **`cap_section` / `cap_label` / `reasons[0]` (builder.py, constants.py).** The new text interpolates `cap_provenance["citations"][0]["section"]` (a short string like `"23-21"`/`"23-22"`). This field was **already present, unchanged, verbatim in the same document** before this commit — `_cap_provenance()` (builder.py:155-175, not part of this diff) has always echoed the full `citations` list including `section` into `cap_provenance`, which is itself a top-level document field. This change only *duplicates* an already-exposed value into a second display string; it exposes nothing new. `_cap_citation_section()` is type-guarded (`isinstance(..., dict)`, `isinstance(section, str) and section`) and falls back to a section-agnostic sentence on any malformed/missing shape — never crashes, never invents a section (`builder.py:359-368`, `constants.py` `draft_cap_label`/`preliminary_cap_reason`).

2. **`coverage_matrix[].governs` family label.** `_residential_far_family_label()` (constants.py) is a pure string transform (`stem = rule_id[:-len("-residential-far")]; stem.upper()`) applied only to `cap_provenance["rule_id"]`, which originates from the internal, developer-authored rule engine (`services/api/app/rules/rulesets/*.rule.json` — static, repo-controlled files), never from request/network/user input. `rule_id` was **already present, unchanged, in `cap_provenance`** before this commit. No new sensitive value is introduced; the label is a coarse district-family tag (e.g. "R5", "R6-R12"), not PII or an internal identifier.

3. **New `assumptions` entries on the zero-with-buildings path (`unused_floor_area.py:213-240`).** These two records echo `raw_bldgarea_value` (the recorded PLUTO `bldgarea`, already-exposed elsewhere in the document as `inputs.existing_building_floor_area`) and the `numbldgs` fact's raw value/coverage-status basis. `numbldgs` (building count on a tax lot) is a public NYC PLUTO field, the same official-source category already flowing through this whole module (`bldgarea`, `lot_area`, etc.) — not PII, not an internal system identifier, not a request URL, not a raw upstream HTTP payload. `_zero_with_buildings_assumptions()` only extracts `.get("value")`/`.get("coverage_status")` from the fact dict — it does not echo `provenance_ref`, connector internals, or any credential/URL field. **Conclusion: no sensitive value is newly exposed.**

## Injection / rendering-safety analysis (item 3 of the brief)

- All three new interpolation points (`draft_cap_label`, `preliminary_cap_reason`, `coverage_matrix_rows`'s `governs` suffix, and the two f-strings in `_zero_with_buildings_assumptions`) build **plain Python strings only** — no HTML, no markup, no templating engine, no `eval`/`exec`, no SQL string building. `!r` (repr) on `raw_numbldgs_value` in `_zero_with_buildings_assumptions` (unused_floor_area.py:208) is Python's safe representation call — it cannot execute code or alter control flow regardless of the input's content; worst case it renders an odd-looking quoted string in a `rationale` field.
- Consumption on the frontend: `apps/web/src/components/compare/ScenarioAssumptions.tsx:47-61` and `apps/web/src/components/compare/CoverageMatrixSection.tsx`/`ScenarioResult.tsx` (not modified by this task) render these strings as **JSX text children** (`{assumption.rationale}`, `{formatValue(assumption.value)}`), which React escapes automatically. Grep confirmed `dangerouslySetInnerHTML`/`innerHTML` do not appear in any scenario/compare/assumptions component (`LotOutlineMap.tsx`, a map-SVG component, and a test file were the only 3 hits repo-wide, both unrelated to scenario rendering). **No stored-XSS path exists for these new strings.**
- Derivation-path validation: both interpolation sources (`section_reference`, `rule_id`) are read with explicit `isinstance` type guards and fail closed to a section-/family-agnostic fallback when the shape is wrong or absent — they never trust an unchecked type into the f-string (`constants.py` `draft_cap_label`, `_residential_far_family_label`; `builder.py` `_cap_citation_section`).
- Source-of-truth check: `cap_provenance`/`rule_id`/`citations` are produced by the deterministic rule engine evaluating static, repo-committed rule JSON (`services/api/app/rules/rulesets/*.rule.json`) — not user input, not a live external HTTP response body rendered into text. This is a materially different trust tier than, e.g., AI-extracted or attacker-supplied text, and the `backend-api.md` "treat source text as untrusted" rule (which governs AI-extraction paths) does not apply to this internal rule-engine output.

## Dependency / lockfile / config check (item 4)

Independently confirmed via `git diff-tree --no-commit-id --name-only -r 77558eb5` (not the producer's claim): the commit touches exactly the 6 files listed above. `services/api/pyproject.toml`, `services/api/requirements.in`, `services/api/requirements.txt`, and `packages/**` are absent from that list. No dependency, lockfile, or configuration change rides along.

## DoS / resource-safety check (item 5)

- New branch in `build_unused_floor_area_section` (unused_floor_area.py:426-444): O(1) — one dict lookup (`_numbldgs_fact`), one type/coverage check, returns.
- `_zero_with_buildings_assumptions`: builds a fixed 2-element list; no loop over unbounded/attacker-sized input.
- `coverage_matrix_rows(cap_rule_id)` (constants.py): iterates the fixed, hardcoded 8-row `COVERAGE_MATRIX` tuple — bounded, unchanged cardinality from before this task.
- `_cap_citation_section` reads `citations[0]` only (not a loop) from a list whose size is controlled by the internal rule engine (small, fixed per rule), not attacker input.
- No recursion, no new unbounded allocation, no change to any request-path loop bound. **No DoS concern found.**

## Findings

No blocking (F-series) findings.

**A1 (advisory, non-blocking).** The `numbldgs` fact's raw value now appears in a user-visible `assumptions` record for the first time in this scenario document (`unused_floor_area.py:213-240`). It is confirmed non-sensitive (public PLUTO building-count field, same trust tier as `bldgarea`/`lot_area` already exposed throughout this module), so this is not a defect — recorded only so a future reviewer auditing "what PLUTO fields reach the response body" has this addition on record.

**A2 (advisory, non-blocking).** `_zero_with_buildings_assumptions`'s "not usable" branch (unused_floor_area.py:206-212) uses `repr()` on an arbitrary-typed `raw_numbldgs_value` (could in principle be any JSON scalar the profile-builder upstream produced) inside a human-readable `rationale` string. This is safe today (plain text, React-escaped, no code execution path), but if a future consumer ever renders `assumptions[].rationale` outside React's default escaping (e.g. into an email, a PDF via raw string concatenation, or a non-React surface with `dangerouslySetInnerHTML`), an unusually crafted upstream value could produce awkward output. Not exploitable today; worth a rendering-boundary note if a non-React consumer of `assumptions` is ever built.

## Verdict

**PASS.**

This change has a genuinely narrow, well-bounded surface: three pure-function/string-construction edits inside the deterministic scenario-calculation layer, consuming only already-authorized, already-internal data (rule-engine trace fields and official-PLUTO profile facts that were already flowing through this module), producing only plain-text strings that reach the client exclusively through React's auto-escaping JSX rendering path, with zero new imports, zero new external calls, zero new storage/auth/secrets/logging code, and zero dependency/lockfile/config changes (independently confirmed from the diff, not the producer's claim). The two advisory notes above are informational only and do not block acceptance.
