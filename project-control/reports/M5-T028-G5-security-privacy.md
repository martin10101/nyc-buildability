# G5 Security-and-Privacy Gate Report — M5-T028

> Saved VERBATIM by the orchestrator from the security-reviewer agent return (2026-09-14;
> transport entity-decoding only, per the report-preservation rule). Reviewer ≠ producer.

- Gate ID: G5
- Task ID: M5-T028
- Reviewer: security-reviewer (independent, read-only)
- Producer: backend-engineer (unnamed worktree spawn `wt-m5t028`)
- Result: **PASS**
- Clean environment/worktree used: Yes — `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a39732ba6effb3d33`, verified `git rev-parse HEAD` = `7e7cd85e8d1fb6dcf40cfde142931f720383f532` (byte-identical to the cited material commit), `git status --porcelain` clean.

Orchestrator's HEAD note confirmed: current repo HEAD on `candidate/D-024-mrl-option-b` is `839a2d3dc0e43524be9b61e470ad5f18dc9dee2f` (control-plane-only commits, including the same-branch G3 record for this task); `7e7cd85e` lives on `worktree-agent-a39732ba6effb3d33` and is not yet integrated — expected per the frozen-worktree producer pattern, verified by `git branch --contains 7e7cd85e`.

## Acceptance criteria reviewed

`project-control/tasks/M5-T028.json` S1–S4 (derived label follows the evaluated rule / four sibling surfaces corrected / provenance prose preserved / scope+schema+regression), and the packet's explicit G5-relevant instruction: verify the section-reference interpolation cannot be reached or forged by request-controlled input, and that no new response field, log statement, or I/O surface rides along.

## Surface-by-surface: in-scope vs demonstrably-untouched

| Surface | Status | Evidence |
|---|---|---|
| String interpolation / injection into API response | **In scope, reviewed** | `derive.py` new `_cap_section_reference`/`_derived_range_label`; same pattern in the other 4 modules |
| Live HTTP endpoint wiring (`scenario_analysis.py`) | Touched by consequence, not by diff — verified unchanged | `git show 7e7cd85e --stat` lists only the 5 scenario modules + 5 test files + producer report; `scenario_analysis.py` absent |
| Web rendering (XSS sinks) | Reviewed, demonstrably clean | grep below |
| Network/external calls | Demonstrably untouched | grep: no `requests`/`httpx`/`urllib`/`socket` usage added in any of the 5 modules |
| Filesystem/storage access | Demonstrably untouched | grep: no `open(`/storage calls in the 5 modules; test-side `Path(...)` use is read-only source-text introspection of the repo's own files |
| Secrets/credentials | Demonstrably untouched | grep: no `SECRET`/`API_KEY`/`SERVICE_ROLE`/`password`/`token`/`os.environ` hits |
| Logging | Demonstrably untouched — no logging in these modules at all (before or after) | grep: zero `logger`/`logging`/`print(` in any of the 5 modules |
| Auth/tenancy boundaries | N/A — no tenant/user/session code in this diff | diff touches only pure-computation label-formatting functions |
| Deserialization of untrusted input | N/A — modules consume an already-validated internal `scenario_document` dict; no `json.loads`/`pickle`/`yaml.load` added | grep clean |
| Admin/deployment behavior | N/A | no CI/config/infra files in diff |
| Dependency/lockfile/config | Demonstrably untouched | `git show 7e7cd85e --stat`: no `pyproject.toml`, `requirements*.in/txt`, or `packages/**` present |

## Directive/requirement verification (informational — full DCV is a separate pass)

| Requirement ID | Reviewed SHA | Security-relevant verdict | Reproduced evidence |
|---|---|---|---|
| D-059-R003 | 7e7cd85e | PASS (security-relevant portion: no hardcoded/incorrect section reference can be forced, and the correction introduces no new attacker-reachable surface) | `grep -n "ZR 23-21" app/scenario/{derive,breakeven,comparison,ranking,sensitivity}.py` → zero matches at pinned commit; full derivation traced to static rule JSON (see F/A below) |
| D-046-R001/R002 (scope/disjoint-lane) | 7e7cd85e | PASS | `git show 7e7cd85e --stat` matches `allowed_paths` exactly; no `forbidden_paths` file touched |

(Full directive-compliance verification, including non-security requirement facets, is the `directive-compliance-verifier`'s independent pass — not duplicated here.)

## Steps independently executed

1. `git rev-parse HEAD` (repo root) and `git branch --contains 7e7cd85e` / `git merge-base --is-ancestor` to establish the material commit's location.
2. `git show 7e7cd85e -- <each of the 5 production files>` — read full diffs.
3. `git show 7e7cd85e:services/api/app/scenario/builder.py` — read `_cap_citation_section` (the reused, already-G5-reviewed M5-T027 extraction function) and `_cap_provenance(trace)` to trace the value's true origin.
4. `git show 7e7cd85e:services/api/app/rules/rulesets/r6_r12_residential_far.rule.json` — confirmed `"section": "23-22"` is a static, sha256-content-digested literal in a repo-committed file, not derived from any runtime input.
5. `git show 7e7cd85e:services/api/app/api/v1/scenario_analysis.py` (full read) — confirmed the live route's `_rebuild_scenario` builds `scenario_document` **only** from `bbl` over the trusted server-side seam (`fetcher → build_property_profile → evaluate_property → serialize_rule_evaluation → build_scenario`), and that the request body is validated by `_structural_error`/`FORBIDDEN_FACT_KEYS` and passed to the engines **only** as `assumptions`/`variable`/`values`/`objective` parameters — never merged into `scenario_document`, which is the argument `_cap_section_reference` reads.
6. Executed the pinned worktree's test suite and lint/modularity self-checks (reproducing, not trusting, the producer's numbers — see below).
7. Ran a 13-case adversarial probe of `_cap_section_reference`/`_derived_range_label` directly (malformed shapes, non-string `section`, empty string, 100 KB hostile string containing `<script>`) to confirm fail-closed behavior with no exception and no type leak.
8. `grep` sweeps across the 5 production files and their 5 test files for logging, network, filesystem, secrets, deserialization.
9. `grep` sweep of `apps/web` for `dangerouslySetInnerHTML`/`innerHTML` and for consumers of `cap_provenance`/label fields; read `ScenarioProvenance.tsx` in full to confirm citation text renders as plain JSX (auto-escaped), never as `href` or raw HTML.
10. Confirmed call-site count of `_cap_section_reference` per engine function (grep across all 5 files) to verify it is invoked at most once per top-level call, not inside per-candidate/per-set loops.

## Expected versus actual

| Check | Expected (producer claim) | Actual (independently reproduced) |
|---|---|---|
| `python -m pytest services/api/tests/scenario -q` | 443 passed | **443 passed in 1.68s** ✓ |
| `python -m pytest services/api/tests/scenario/test_scenario_contract.py -q` | 28 passed | **28 passed in 0.19s** ✓ |
| `python -m ruff check .` (services/api) | All checks passed | **All checks passed!** ✓ |
| `python tools/modularity_check.py --check` | 405 files, 0 failures, 17 warnings (pre-existing) | **selected 405 files; failures 0; warnings 17** ✓ |
| No residual `"ZR 23-21"` in the 5 modules | grep-clean | **grep returned zero matches** ✓ |
| No `pyproject.toml`/`requirements*`/`packages/**` change | none | confirmed via `git show 7e7cd85e --stat` ✓ |

## Regression/security/provenance findings

**F (blocking): none.**

**A1 (advisory, non-blocking) — origin of the interpolated value is conclusively internal, but demonstrated rather than assumed.**
`derive._cap_section_reference(scenario_document)` → `builder._cap_citation_section(cap_provenance)` reads `scenario_document["cap_provenance"]["citations"][0]["section"]`. Traced end-to-end:
- `cap_provenance` is built by `builder._cap_provenance(trace)` (builder.py:155–179), which copies `trace["citations"]` **verbatim** from the rule-evaluation trace — never recomputed, never touched by request data.
- `trace` originates from `rule_evaluation`, itself built entirely server-side in `_rebuild_scenario` (`scenario_analysis.py`): `fetcher(bbl) → build_property_profile → evaluate_property → serialize_rule_evaluation → build_scenario(profile, rule_evaluation)`. The request body is explicitly and structurally forbidden from supplying or overriding any of `profile`, `rule_evaluation`, `scenario`/`scenario_document`, or any fact-shaped key (`FORBIDDEN_FACT_KEYS`, enforced at every JSON depth by `_structural_error`) — confirmed by reading the full route file, not by trusting its docstring.
- The literal `"section"` values ("23-21", "23-22", …) are static string literals inside repo-committed `services/api/app/rules/rulesets/*.rule.json` files, each carrying its own `content_digest_sha256` — confirmed by reading `r6_r12_residential_far.rule.json:20`.
- Conclusion: **no request-controlled or upstream-dataset-controlled (PLUTO) value can reach the interpolation** — the `bbl` path parameter can only select *which* of a small, fixed, repo-defined set of section strings is shown (the correct one for that district family), which is the task's intended behavior, not an injection channel.

**A2 (advisory, non-blocking) — type guards are solid; probed adversarially, zero exceptions, zero type leaks.**
`_cap_citation_section` requires `isinstance(cap_provenance, dict)`, `isinstance(citations, list) and citations`, `isinstance(first, dict)`, and `isinstance(section, str) and section` (truthy) at every step, else returns `None`. 13-case probe (non-dict document, `None` document, non-dict `cap_provenance`, non-list `citations`, empty `citations`, non-dict first citation, non-string `section`, empty-string `section`, and a hostile 100 KB string containing `<script>alert(1)</script>`) produced **zero exceptions** in all cases; malformed shapes fall back correctly to the generic non-committal clause (`"(see cap_provenance.citations for the exact Zoning Resolution section)"`), never defaulting to a specific section. Even in the hypothetical (currently unreachable, per A1) case where a hostile string did reach `section`, interpolation is a plain Python f-string (`f"(ZR {section_reference})"`) — not `eval`/`exec`/template rendering — so it would only ever produce inert text, and there is no `dangerouslySetInnerHTML`/`innerHTML` anywhere in `apps/web/src/components/compare/**` or `apps/web/src/lib/scenario*` (grep-confirmed) to turn that text into markup; `ScenarioProvenance.tsx` (pre-existing, unrelated to this diff) already renders `citation.section` as plain React JSX text (auto-escaped). No length cap exists at this specific derivation layer for a corrupted `section` value, but this is a pre-existing, out-of-task-scope class (rule-JSON supply-chain integrity, already covered by per-citation `content_digest_sha256` pinning and the M5-T027 G5-reviewed extraction seam) — not a new risk introduced by M5-T028.

**A3 (informational, no action needed) — data exposure is duplicative, not novel.**
None of the reworded label strings add a new field, category, or identifier to the response. The `.label` fields already existed pre-fix (with the wrong hardcoded section); only the embedded section substring now varies. The same section text was already exposed in the very same response envelope via the sibling `cap_label` field (`_finish()` in `scenario_analysis.py`, driven by the already-accepted, already-G5-PASS'd M5-T027 `builder.py` code), and via `cap_provenance.citations[].section` on the accepted `GET /properties/{bbl}/scenario` route. No rule id, internal identifier, citation object, or request URL was newly added to any of the five label strings — only the section number, matching the pre-fix `(ZR 23-21)` pattern already in place.

**A4 (informational) — DoS/resource check: confirmed non-redundant, not merely assumed.**
`_cap_section_reference(scenario_document)` is called **at most once per top-level engine invocation** in every module (grep-verified call sites: `derive.py` 2 sites, `breakeven.py` 2, `ranking.py` 3, `sensitivity.py` 3, `comparison.py` 2 — none inside a per-candidate/per-point/per-set loop). `comparison.py`'s success path computes `section_reference`/`metric_labels` once (line 626) and threads the result through the per-set loop (line 629+) rather than recomputing per iteration. The function itself does O(1) dict/list access (reads only `citations[0]`, never scans the full list). No unbounded loop, no new allocation scaling with request size, beyond what the M5-T012-accepted, already-bounded request-size caps (`MAX_ASSUMPTION_SETS`, `MAX_CANDIDATE_DOMAIN_LENGTH`, etc.) already govern.

## Defects

None.

## Required rework

None.

## Reviewer conclusion

The five modules' fix is a narrow, mechanically-verified text correction: it removes an incorrect hardcoded legal citation and replaces it with a value derived exclusively from static, repo-committed, sha256-pinned rule JSON, reached through a scenario document that is provably rebuilt server-side and structurally firewalled against request-body fact injection (independently confirmed by reading `scenario_analysis.py` in full, not by trusting its docstrings). The derivation's type guards were adversarially probed and never raise, never leak a non-string type, and never fabricate a section. No network, filesystem, secret, logging, auth/tenancy, deserialization, or dependency surface is touched, added, or regressed. The web client has no HTML-injection sink anywhere near these fields. Reproduced pytest/ruff/modularity results match the producer's report exactly at the pinned commit.

**Verdict: PASS.**
