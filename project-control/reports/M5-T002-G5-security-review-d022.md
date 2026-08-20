# G5 SECURITY GATE REPORT — M5-T002 (D-022 corrected identity)

> Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel
> (transport entity-decoding only). Reviewer ≠ producer. Supersedes the invalidated
> M5-T002-G5-security-review.md conclusions (prior identity 2fee786/31e652a, D-022-R016).

**Task:** M5-T002 — internal draft-scenario endpoint + client validation boundary
**Directive:** D-022 (scenario-contract-validator-correction); prior G5 PASS at 2fee786/31e652a INVALIDATED per D-022-R016 — this review stands alone.
**Frozen reviewed identity:** commit `69558cd` / tree `ee6dce0f29416e6637dd46382872a88a25578ce1`. Working HEAD `7f9231edbd04aaf33e68b986dd643af4aa2ff916` (tree `80d2cf78`) differs from `69558cd` ONLY in `project-control/**` (M5-T002.json, evidence-map.json, state.json, tasks/M5-T002.json) — verified; no source delta.
**Branch:** task/M5-T002-scenario-endpoint. Reviewer: security-reviewer (read-only; not the producer).
**Working tree:** two uncommitted files under `.claude/agent-memory/human-journey-reviewer/` only — a different agent's memory, outside the reviewed identity and outside my write scope; no bearing on the code under review.

## VERDICT: PASS

No critical/high/medium findings. Zero inputs reach `ok:true` while violating the canonical schema. Three low/informational residuals are documented below; none block. The specific weakness the owner proved exploitable on the previous identity (shallow nested validation accepting arrays-as-objects, null items, negative/zero/non-finite caps, `verified` rule_status, and an embedded property profile) is fully remediated at `69558cd`, and I reproduced every owner case plus additional adversarial shapes as REJECTED.

Blocking corrections: none.

---

## 1. Attempted-bypass list (red-team; outcome per attempt)

Every attempt below was traced against the actual `validateScenarioDocument` at `apps/web/src/lib/scenario-contract.ts@69558cd` and the `fetchScenario` HTTP path in `apps/web/src/lib/scenario.ts`.

| # | Attack | Outcome | Rejected by |
|---|--------|---------|-------------|
| 1 | Top-level `__proto__` key (prototype-pollution shape) | REJECTED | `JSON.parse` defines `__proto__` as an **own enumerable data property** (does not invoke the setter → no pollution); `Object.keys` includes it; not in `allowed` Set → "not a documented property". `Set.has("__proto__")` has no object-footgun. |
| 2 | Top-level `constructor` / `prototype` keys | REJECTED | Same additionalProperties:false path (line 251-255). |
| 3 | `__proto__`/`constructor` nested in constraint / citation / cap_provenance / assumption | REJECTED | `checkKnownAndRequiredKeys` on each nested object flags the undocumented key. |
| 4 | Array as the whole body | REJECTED | `isRecord(body)` false → "response body is not a JSON object" (line 483). |
| 5 | Array at evaluated_input / constraint / assumption / citation / cap_provenance / integrity_check / coverage_matrix-row | REJECTED | every object site uses `isRecord` (rejects arrays), not bare `typeof`. |
| 6 | Array as `constraint.provenance` (the exact pre-correction `typeof` hole) | REJECTED | line 342 `provenance === null || isRecord(provenance)` (test: "also rejects … a provenance ARRAY"). |
| 7 | Array as `citation.provenance` | REJECTED | line 392 `isRecord(value.provenance)`. |
| 8 | `draft_zoning_floor_area_cap_sq_ft` = `NaN` / `+Infinity` / `-Infinity` | REJECTED | `isFiniteNumber` (line 525) — defends even though strict JSON can't carry these (non-JSON/laundered caller). |
| 9 | cap = `0` / `-1` | REJECTED | `> 0` guard (line 526) — owner bypasses 1 & 2, tested. |
| 10 | Non-finite `constraint.value` / `assumption.value` / `integrity_check.tolerance` | REJECTED | `isContractScalar`→`isFiniteNumber` (lines 328/362/465). |
| 11 | `evaluated_input.bbl` = `"x"` (non-canonical) | REJECTED | `BBL_PATTERN` (line 292) — owner bypass 3, tested. |
| 12 | `input_fingerprint` = `"sha256:zz…"` (bad hex/length) | REJECTED | `DIGEST_SHA256_PATTERN` (line 307). |
| 13 | top-level `coverage_status` = `"verified"` | REJECTED | not in `SCENARIO_COVERAGE_STATUSES` (checkEnum, line 499) — tested at validator and HTTP path. |
| 14 | `cap_provenance.rule_status` = `"verified"` | REJECTED | not in `CAP_PROVENANCE_RULE_STATUSES` (line 418) — owner bypass 4, tested. |
| 15 | `cap_provenance.citations` = `[null]` | REJECTED | `checkCitation(null)`→`isRecord` false (line 374) — owner bypass 5, tested. |
| 16 | `assumptions` = `[null]` | REJECTED | `checkAssumption(null)`→`isRecord` false (line 351) — owner bypass 6, tested. |
| 17 | citations = one valid + one invalid item | REJECTED | `forEach` validates each item independently; any invalid → problem → `ok:false`. |
| 18 | Unexpected top-level property | REJECTED | additionalProperties:false — owner bypass 7, tested. |
| 19 | Embedded `property_profile` (invalid fixture) | REJECTED | undocumented root key `property_profile` — owner bypass 8, tested at validator AND `fetchScenario` (→ `validation_failure`, never `scenario`). |
| 20 | Missing required key (e.g. `scenario_kind`) | REJECTED | required-presence check + value check (missing_scenario_kind fixture, tested). |
| 21 | Empty string where non-empty required (`cap_label:""`, keys) | REJECTED | `isNonEmptyString` (length>0). |
| 22 | Whitespace-only string where non-empty required (`" "`) | ACCEPTED — **schema-faithful, not a bypass** | schema `non_empty_string` is `minLength:1` (no trim); validator matches exactly. |
| 23 | Duplicate JSON keys (last-wins) | No bypass | `JSON.parse` collapses to one value; the SAME parsed object is validated and rendered (`fetchScenario` parses once, returns `body` as the document) → no TOCTOU/parse-mismatch. |
| 24 | null vs undefined vs missing at every nullable field | REJECTED where invalid | value checks + required-presence both fire; `JSON.parse` cannot produce `undefined`. |
| 25 | `contract_version` = number `1.0` / `"1.0"` | REJECTED | strict `!== "1.0.0"` (line 495). |
| 26 | Deeply nested hostile `provenance` object (unbounded depth/size) | ACCEPTED — **schema-faithful**; see L1/L3 | schema leaves provenance an OPEN object; validator correctly does not recurse. Not a schema violation. |
| 27 | Multi-MB string in a valid string field (quote, disclaimer, cap_label) | ACCEPTED — **schema-faithful**; see L1 | schema `type:string` has no `maxLength`; React escapes at render (no injection). |
| 28 | Attacker key-name reflected into a problem string via additionalProperties branch | No injection; see L2 | reflected value is bounded (`boundedText`, 600-char cap + control-strip) and React-escaped in ScenarioFailure. |

**Result: no successful bypass.** Every input that reaches `ok:true` is faithful to `packages/contracts/schemas/v1/scenario.schema.json` (verified field-by-field against the unchanged schema and the generated `packages/contracts/generated/scenario.ts`).

---

## 2. Numbered findings

**No Critical, High, or Medium findings.**

**L1 (Low / accepted residual) — success-path document strings are rendered verbatim without a length cap.** `ScenarioResult.tsx` renders `not_verified_disclaimer`, `cap_label`, `citation.section`/`quote`, `cap_provenance.{rule_id,rule_version,output_name}`, coverage-matrix strings, and the two contract-version strings verbatim. The validator does not impose `maxLength` because the schema does not (these are `type:string`/`non_empty_string`, no maxLength). This is schema-faithful and by-design (verbatim display of a trusted deterministic-backend document, matching the accepted rule-evaluation surface). React escaping prevents injection; the surface is flag-gated internal (default-off). Adding a cap here would exceed the canonical schema and fall outside the bounded correction (D-022-R004/R005/R013). Not a validation bypass. **Remediation: none required now**; if ever hardened, do it as a separate schema-level `maxLength` change, not in this validator.

**L2 (Low / note) — the additionalProperties branch interpolates the attacker-supplied unknown key NAME into the problem path.** `checkKnownAndRequiredKeys` builds `` `${prefix}${key}` `` where `key` is an unknown property name from `Object.keys` (attacker-influenced). The owner's premise that "paths only contain fixed names + numeric indices" is therefore slightly imprecise for this branch. It is nonetheless SAFE: the reflected problem is passed through `boundedText` (600-char cap + C0/C1 strip, `scenario.ts` line 337) and rendered as React-escaped text in `ScenarioFailure.ValidationFailure` (`<li>{problem}</li>`). No attacker VALUE is ever interpolated into a problem. **Remediation: none required** (defense-in-depth already bounds + escapes it).

**L3 (Informational) — validator does not early-exit array iteration once `MAX_REPORTED_PROBLEMS` is reached.** On a hostile oversized array (e.g. 10^6 constraints) the validator still performs a full linear pass (message strings are even built before `Problems.add` drops them past 21). There is NO super-linear amplification: work and memory are O(body size), `JSON.parse` already allocated the array (proportional attacker cost), and the problem list is hard-bounded at 21 entries. In this trusted-backend, flag-gated-internal context this is not a practical DoS. **Remediation: none required**; an optional micro-optimization (bail once the bound is hit) would reduce wasted work but is out of scope for D-022 (R013).

---

## 3. Targeted verification of the owner's six asks

1. **Bypass construction** — exhausted (Section 1). No input reaches `ok:true` in violation of the schema. Prototype-pollution shapes are rejected as undocumented keys and cannot pollute (`JSON.parse` own-property semantics). `isRecord` closes the arrays-as-objects hole at every site (only bare `typeof==="object"` is inside `isRecord` itself, with `!== null && !Array.isArray` guards). All four numeric fields use `isFiniteNumber`.
2. **DoS/complexity** — linear, single pass per array, no quadratic path (max validator nesting depth is body→cap_provenance→citation, each array iterated once). Problem list bounded at 21 (`Problems.add`). Reflected problems bounded (`boundedText`). See L3.
3. **Reflected content** — no attacker VALUE is interpolated into problems; only fixed names + numeric indices, plus the unknown-key NAME in the additionalProperties branch (L2), which is bounded + React-escaped. `fetchScenario` maps all validation problems through `boundedText`.
4. **Never-verified guarantee** — structurally excluded end-to-end and REAL:
   - `coverage_status`: generated `DraftCoverageStatus` = `CoverageStatus & (5 draft values)` (excludes `verified`); runtime `SCENARIO_COVERAGE_STATUSES` = those 5; `checkEnum` enforces membership.
   - `rule_status`: generated `CapProvenance["rule_status"]` = `"discovered"|"extracted_draft"|"needs_review"|"published"` (scenario.ts line 37 — no `verified`); runtime `CAP_PROVENANCE_RULE_STATUSES` = exactly those four with `as const satisfies readonly CapProvenance["rule_status"][]` (tsc-enforced array⊆union — the direction that excludes `verified`); `MutuallyEqual<CapProvenance["rule_status"], (typeof CAP_PROVENANCE_RULE_STATUSES)[number]>` documents bidirectional equality (same pattern as the accepted `contract.ts`/`rule-evaluation-contract.ts`). The runtime `checkEnum` against the literal array (which contains no `verified`) is the dispositive enforcement and holds regardless of the type proof. Confirmed the generated union name/members directly.
5. **Scope/policy** — correction diff `2d9eb74..69558cd` = exactly 4 files: `apps/web/src/lib/scenario-contract.ts` + `__tests__/scenario-contract.test.ts` + `__tests__/scenario.test.ts` + `project-control/reports/M5-T002-producer-report.md`. No dependencies, no canonical contracts/schema, no generated types, no backend, no CI/security-control changes. Whole-branch diff `d8b3899..HEAD` touches only `apps/web/**`, `project-control/**`, `services/api/**` (original M5-T002 backend) — no supervisor/controller/model-selection/context-pipeline/MCP paths; D-021/D-022 holds untouched. Schema unchanged → validator was aligned TO the schema (R004/R005 satisfied).
6. **CI** — `gh api …/commits/7f9231e/check-runs`: 40 total runs, 20 unique check names, **zero non-success conclusions** (all `success`), including `web (lint + typecheck + build)`, `web-e2e (vitest + Playwright)`, `contracts-typegen`/`contracts-schema-bundle` (byte-identical drift), `api (ruff + pytest)`. PR #241 OPEN, not draft, head `7f9231e`, MERGEABLE (hold D-022-R001 respected).

**Cross-cutting security checks:** cross-tenant isolation — N/A at this client boundary (no auth/tenancy logic; bbl path is `encodeURIComponent`'d, host fixed by `apiBaseUrl()` → no SSRF/path-injection). Service-role secrecy — none present; the `INTERNAL_SCENARIO_UI` flag is deliberately NOT `NEXT_PUBLIC_`, so it is never inlined into the browser bundle. Private storage — N/A. Injection — no `dangerouslySetInnerHTML`/`innerHTML`/`eval` anywhere in `apps/web/src` (grep clean; all rendering via React-escaped text). Upload controls / prompt-injection — N/A (no uploads, no LLM input on this path; source text treated as untrusted DATA and only shape-checked). Least privilege — two-factor default-off gate (server env + per-request opt-in). Log redaction — validator/client do not log; reflected text bounded.

**Malformed-data containment (D-022-R011):** `ScenarioPanel` renders `ScenarioResult` ONLY for `outcome.kind === "scenario"`, which `fetchScenario` returns ONLY when `validateScenarioDocument` returns `ok:true`; all other outcomes route to `ScenarioFailure`. The guarantee is enforced at the validator boundary (the correction did not edit `ScenarioResult`), exactly as required.

---

## 4. Commands and last lines

- `git rev-parse HEAD` → `7f9231edbd04aaf33e68b986dd643af4aa2ff916`; `git rev-parse 69558cd^{tree}` → `ee6dce0f29416e6637dd46382872a88a25578ce1` (matches frozen tree).
- `git diff --name-only 69558cd HEAD` → 4 paths, all `project-control/**` (no source delta).
- `git diff --name-only 2d9eb74 69558cd` → `scenario-contract.ts`, `scenario-contract.test.ts`, `scenario.test.ts`, `M5-T002-producer-report.md` (4 files).
- `gh api …/commits/7f9231e…/check-runs --jq '.total_count'` → `40`; unique names → `20`; `select(.conclusion != "success")` → (empty).
- `gh pr view 241 …` → `{"state":"OPEN","isDraft":false,"headRefOid":"7f9231e…","mergeable":"MERGEABLE"}`.
- `cd services/api && python -m pytest tests/api -q` → **`144 passed in 3.83s`**.
- Grep `dangerouslySetInnerHTML|innerHTML|eval\(|service_role` over `apps/web/src` → only the descriptive comment in `bounded.ts` (no usage).

---

## 5. Residual risks / could-not-verify

- **Web vitest/Playwright not run locally** (thin-client policy prohibits npm/node; D-022-R014 designates the CI matrix as the clean-checkout execution). I relied on the green `web`, `web-e2e`, and `contracts-typegen` check-runs at the exact frozen head `7f9231e` as the authoritative execution evidence, and independently re-derived every adversarial case from source. This is NOT a BLOCKED condition — the required CI is green at the reviewed identity.
- **L1/L3 residuals** are accepted design/schema properties (verbatim display, open provenance objects), not defects of this correction; any future hardening belongs in the canonical schema, not this validator.
- **Prior self-under-call, addressed:** my earlier report classified the shallow nested validation as merely informational; the owner correctly proved it an exploitable validation bypass. That class is now fully closed at `69558cd` (all 8 owner cases + additional shapes reproduced as REJECTED). The residuals I report now (L1-L3) are genuinely non-exploitable given schema-faithfulness, React escaping, and the trusted-backend/flag-gated threat model — I flag them explicitly rather than omitting them.

**Recommendation to orchestrator:** record G5 = PASS at frozen identity `69558cd` / tree `ee6dce0f` (HEAD `7f9231e`, source-identical). No blocking corrections.
